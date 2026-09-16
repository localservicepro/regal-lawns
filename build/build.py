#!/usr/bin/env python3
"""Static site generator for regallawnsandgardens.com.au

Run:  python3 build/build.py
Writes every page into the repo root. Shared elements (header, footer, NAP,
service areas, quote form, tracking script, schema) live here so they are
identical on every page.
"""
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --------------------------------------------------------------------------
# Business facts — every one of these comes from the SEO strategy document.
# Anything NOT in the strategy doc is a PLACEHOLDER (see TODO() below).
# --------------------------------------------------------------------------
BIZ = {
    "name": "Regal Lawns And Gardens PTY LTD",
    "short": "Regal Lawns And Gardens",
    "contact": "Ben Butler",
    "phone_display": "0426 883 076",
    "phone_e164": "+61426883076",
    "email": "info@regallawnsandgardens.com.au",
    "street": "19 Clair Ave",          # schema only — not shown on page
    "suburb": "Deception Bay",
    "state": "QLD",
    "postcode": "4508",
    "country": "AU",
    "domain": "https://regallawnsandgardens.com.au",
    # Approximate suburb-centre coordinates for Deception Bay (not the exact
    # street address) — replace with the exact pin from Google Maps.
    "lat": -27.193,
    "lng": 153.024,
}
PUBLIC_ADDRESS = "Deception Bay QLD 4508"

SUBURBS = [
    "Caboolture", "Burpengary", "Burpengary East", "Narangba", "Morayfield",
    "Dakabin", "Kallangur", "Strathpine", "Murrumba Downs", "Lawnton",
    "Brendale", "Deception Bay", "Rothwell", "Kippa-Ring", "Redcliffe",
    "Margate", "Clontarf", "Woody Point", "Newport", "Bray Park",
    "North Lakes", "Mango Hill",
]
assert len(SUBURBS) == 22

TRACKING_SCRIPT = (
    '<script src="https://link.msgsndr.com/js/external-tracking.js" '
    'data-tracking-id="tk_6ac0af015fe844119d96e63a3a0dbc4e"></script>'
)

# --------------------------------------------------------------------------
# Stock images (Pexels — free licence, no attribution required). See README.
# --------------------------------------------------------------------------
IMAGES = {
    "home-hero":    (6728919,  "Magic K",            "Close-up of a person mowing a sunlit lawn with a push mower"),
    "lawn-mowing":  (11364122, "Pascal Küffer",      "Person using a lawn mower to trim grass in a sunny garden"),
    "lawn-mowing-2":(4162011,  "Magda Ehlers",       "Lawn mower on green grass"),
    "acreage":      (173552,   "Pexels contributor", "Man riding a lawn mower vehicle"),
    "acreage-2":    (12130131, "Pexels contributor", "Man driving a blue tractor on a green grass field"),
    "garden":       (5231048,  "Pexels contributor", "Gardener cutting branches of a tree in a garden"),
    "garden-2":     (12110580, "Pexels contributor", "Person wearing gloves gardening"),
    "hedge":        (24595771, "Aleksander Dumała",  "Man cutting a hedge with a trimmer in the garden"),
    "hedge-2":      (7813043,  "Indi Van Kuijk",     "Man trimming the hedges with a power tool"),
    "treatments":   (16603972, "Pexels contributor", "Dandelion weeds growing in a lawn"),
    "treatments-2": (12887876, "Pexels contributor", "Water sprinklers on green grass"),
    "tree":         (7509492,  "Mark Stebnicki",     "Man standing on a ladder cutting a tree branch"),
    "tree-2":       (4206115,  "Pexels contributor", "Person using a chainsaw"),
    "about":        (16680733, "Pexels contributor", "Gardening tools in a wheelbarrow"),
    "house":        (7546775,  "Pexels contributor", "House backyard with a green lawn"),
    "house-2":      (5178034,  "Pexels contributor", "Aerial view of a suburban house with a green lawn"),
    "services":     (6728933,  "Magic K",            "Man mowing a lawn"),
}


def img_url(key, w):
    pid = IMAGES[key][0]
    return f"https://images.pexels.com/photos/{pid}/pexels-photo-{pid}.jpeg?auto=compress&cs=tinysrgb&w={w}"


def img(key, alt, cls="", w=1200, h=750, eager=False, sizes="(min-width: 960px) 50vw, 100vw"):
    """Responsive <img> hotlinked from Pexels with a local SVG fallback."""
    attrs = [
        f'src="{img_url(key, w)}"',
        f'srcset="{img_url(key, 640)} 640w, {img_url(key, 1200)} 1200w, {img_url(key, 1920)} 1920w"',
        f'sizes="{sizes}"',
        f'alt="{html.escape(alt)}"',
        f'width="{w}" height="{h}"',
        'decoding="async"',
        ('loading="eager" fetchpriority="high"' if eager else 'loading="lazy"'),
        "onerror=\"this.onerror=null;this.srcset='';this.src='/images/placeholder.svg'\"",
    ]
    if cls:
        attrs.append(f'class="{cls}"')
    return "<img " + " ".join(attrs) + ">"


# --------------------------------------------------------------------------
# Placeholders — anything the strategy doc does not supply is marked visibly.
# --------------------------------------------------------------------------
PLACEHOLDERS = []


def TODO(label, inline=True):
    PLACEHOLDERS.append(label)
    if inline:
        return f'<mark class="todo">[TO CONFIRM: {html.escape(label)}]</mark>'
    return f'<div class="todo-block"><strong>Placeholder — remove before launch</strong>{html.escape(label)}</div>'


# --------------------------------------------------------------------------
# SVG icons
# --------------------------------------------------------------------------
ICON = {
    "phone": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/></svg>',
    "mail": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-10 7L2 7"/></svg>',
    "pin": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0z"/><circle cx="12" cy="10" r="3"/></svg>',
    "clock": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>',
    "check": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12l5 5L20 7"/></svg>',
    "arrow": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
    "menu": '<svg class="icon-open" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg><svg class="icon-close" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>',
    "close": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>',
    "chev": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>',
    "mower": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 17h2m14 0h2M7 17h10M5 17l3-6h8l3 6"/><circle cx="7" cy="17" r="2"/><circle cx="17" cy="17" r="2"/><path d="M16 11V5h3"/></svg>',
    "leaf": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M11 20A7 7 0 0 1 4 13c0-5 4-9 16-9-1 12-5 16-9 16z"/><path d="M4 20c4-6 8-9 12-11"/></svg>',
    "shield": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/></svg>',
    "home": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m3 11 9-8 9 8v10a1 1 0 0 1-1 1h-5v-7H9v7H4a1 1 0 0 1-1-1z"/></svg>',
    "tag": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20.6 13.4 13.4 20.6a2 2 0 0 1-2.8 0L2 12V2h10l8.6 8.6a2 2 0 0 1 0 2.8z"/><circle cx="7.5" cy="7.5" r="1.5"/></svg>',
}

LOGO_SVG = (
    '<svg viewBox="0 0 48 48" aria-hidden="true"><rect width="48" height="48" rx="12" fill="#1f6a41"/>'
    '<path d="M10 30l4-12 6 8 4-14 4 14 6-8 4 12z" fill="#f0b23a"/>'
    '<rect x="10" y="32" width="28" height="5" rx="2" fill="#f0b23a"/></svg>'
)


def logo(tag=True):
    t = '<span class="logo__tag">Deception Bay · Moreton Bay</span>' if tag else ""
    return (f'<a class="logo" href="/" aria-label="{BIZ["short"]} home">{LOGO_SVG}'
            f'<span class="logo__text"><span class="logo__name">Regal Lawns &amp; Gardens</span>{t}</span></a>')


# --------------------------------------------------------------------------
# Services
# --------------------------------------------------------------------------
SERVICES = [
    {
        "slug": "lawn-mowing",
        "name": "Lawn Mowing",
        "nav": "Lawn Mowing",
        "h1": "Professional Lawn Mowing in Redcliffe &amp; the Peninsula",
        "title": "Lawn Mowing Redcliffe | Regal Lawns And Gardens",
        "desc": "Reliable lawn mowing in Redcliffe, Kippa-Ring, Margate and Clontarf. Regular or one-off mowing, edging and clean-up. Free quotes from a local crew.",
        "keyword": "lawn mowing redcliffe",
        "blurb": "Regular or one-off mowing with edging and blow-down for homes and rentals across the Redcliffe peninsula and Moreton Bay.",
        "img": "lawn-mowing",
        "img2": "lawn-mowing-2",
        "alt": "Lawn mowing in Redcliffe: push mower cutting a green residential lawn",
        "related": ["lawn-treatments-weed-control", "garden-maintenance"],
        "form_value": "Lawn mowing",
        "icon": "mower",
    },
    {
        "slug": "acreage-mowing",
        "name": "Acreage Mowing",
        "nav": "Acreage Mowing",
        "h1": "Acreage Mowing &amp; Slashing — Brisbane North &amp; Moreton Bay",
        "title": "Acreage Mowing Brisbane | Regal Lawns And Gardens",
        "desc": "Acreage mowing and slashing for lifestyle blocks in Narangba, Burpengary East, Dakabin and across Brisbane's north. Ride-on mowing, free quotes.",
        "keyword": "acreage mowing brisbane",
        "blurb": "Ride-on mowing and slashing for lifestyle blocks and larger properties in Narangba, Burpengary East and beyond.",
        "img": "acreage",
        "img2": "acreage-2",
        "alt": "Acreage mowing in Brisbane north: ride-on mower cutting a large grassed block",
        "related": ["lawn-mowing", "tree-trimming"],
        "form_value": "Acreage mowing",
        "icon": "mower",
    },
    {
        "slug": "garden-maintenance",
        "name": "Garden Maintenance",
        "nav": "Garden Maintenance",
        "h1": "Expert Garden Maintenance in North Lakes &amp; Mango Hill",
        "title": "Garden Maintenance North Lakes | Regal Lawns And Gardens",
        "desc": "Garden maintenance in North Lakes and Mango Hill: weeding, pruning, mulching and garden bed tidy-ups for homes, rentals and body corporates. Free quotes.",
        "keyword": "garden maintenance north lakes",
        "blurb": "Weeding, pruning, mulching and garden bed tidy-ups that keep North Lakes and Mango Hill gardens looking sharp year round.",
        "img": "garden",
        "img2": "garden-2",
        "alt": "Garden maintenance in North Lakes: gardener pruning shrubs in a residential garden bed",
        "related": ["hedge-trimming", "lawn-mowing"],
        "form_value": "Garden maintenance",
        "icon": "leaf",
    },
    {
        "slug": "hedge-trimming",
        "name": "Hedge Trimming",
        "nav": "Hedge Trimming",
        "h1": "Hedge Trimming &amp; Shaping Across Brisbane North",
        "title": "Hedge Trimming Brisbane | Regal Lawns And Gardens",
        "desc": "Hedge trimming and shaping across Brisbane's northside, from Strathpine to Caboolture. Clean lines, level tops, clippings removed. Free quotes.",
        "keyword": "hedge trimming brisbane",
        "blurb": "Straight lines, level tops and all the clippings removed, for hedges of every size across Brisbane's northside.",
        "img": "hedge",
        "img2": "hedge-2",
        "alt": "Hedge trimming in Brisbane: petrol hedge trimmer shaping a green garden hedge",
        "related": ["garden-maintenance", "tree-trimming"],
        "form_value": "Hedge trimming",
        "icon": "leaf",
    },
    {
        "slug": "lawn-treatments-weed-control",
        "name": "Lawn Treatments &amp; Weed Control",
        "nav": "Lawn Treatments &amp; Weed Control",
        "h1": "Lawn Treatments &amp; Weed Control — Brisbane North",
        "title": "Lawn Care Services Brisbane | Regal Lawns And Gardens",
        "desc": "Lawn care services for Brisbane's north: weed control, fertilising and treatments that fix patchy, weedy turf in Morayfield, North Lakes and beyond.",
        "keyword": "lawn care services brisbane",
        "blurb": "Weed control, fertilising and seasonal treatments that turn thin, weedy turf back into a lawn worth mowing.",
        "img": "treatments",
        "img2": "treatments-2",
        "alt": "Lawn care services in Brisbane: weeds in a lawn before weed control treatment",
        "related": ["lawn-mowing", "garden-maintenance"],
        "form_value": "Lawn treatments & weed control",
        "icon": "shield",
    },
    {
        "slug": "tree-trimming",
        "name": "Tree Trimming",
        "nav": "Tree Trimming",
        "h1": "Tree Trimming &amp; Lopping — Brisbane Northside",
        "title": "Tree Trimming Brisbane Northside | Regal Lawns",
        "desc": "Tree trimming on Brisbane's northside: overhanging branches, storm damage and small tree lopping in Kallangur, Burpengary and Redcliffe. Free quotes.",
        "keyword": "tree trimming brisbane northside",
        "blurb": "Overhanging branches, storm-damaged limbs and small trees trimmed back, with the debris taken away.",
        "img": "tree",
        "img2": "tree-2",
        "alt": "Tree trimming on Brisbane's northside: cutting an overhanging branch from a ladder",
        "related": ["hedge-trimming", "acreage-mowing"],
        "form_value": "Tree trimming",
        "icon": "leaf",
    },
]
SERVICE_BY_SLUG = {s["slug"]: s for s in SERVICES}


def service_url(s):
    return f"/services/{s['slug']}/"


# --------------------------------------------------------------------------
# Shared components
# --------------------------------------------------------------------------
def quote_form(form_id, heading="Get a free quote", inline=False):
    opts = "".join(f'<option value="{html.escape(s["form_value"])}">{s["nav"]}</option>' for s in SERVICES)
    sizes = [
        "Small (under 400 m²)", "Medium (400–800 m²)", "Large (800 m² to ¼ acre)",
        "Acreage (over ¼ acre)", "Not sure",
    ]
    size_opts = "".join(f'<option value="{html.escape(x)}">{html.escape(x)}</option>' for x in sizes)
    tag = "h2" if inline else "h3"
    return f"""
<form class="quote-form" id="{form_id}" method="post" action="/thank-you/" novalidate>
  <{tag} id="{form_id}-title">{heading}</{tag}>
  <p class="quote-sub">Tell us about the job and we'll come back to you with a price. Or call <a href="tel:{BIZ['phone_e164']}">{BIZ['phone_display']}</a>.</p>
  <div class="form-error" role="alert"></div>
  <div class="form-grid">
    <div class="field"><label for="{form_id}-name">Name</label><input id="{form_id}-name" name="full_name" type="text" autocomplete="name" required></div>
    <div class="field"><label for="{form_id}-phone">Phone</label><input id="{form_id}-phone" name="phone" type="tel" autocomplete="tel" inputmode="tel" required></div>
    <div class="field field--full"><label for="{form_id}-email">Email</label><input id="{form_id}-email" name="email" type="email" autocomplete="email" inputmode="email" required></div>
    <div class="field field--full"><label for="{form_id}-address">Property address</label><input id="{form_id}-address" name="property_address" type="text" autocomplete="street-address" placeholder="Street and suburb" required></div>
    <div class="field"><label for="{form_id}-size">Property size</label><select id="{form_id}-size" name="property_size"><option value="">Choose…</option>{size_opts}</select></div>
    <div class="field"><label for="{form_id}-service">Service needed</label><select id="{form_id}-service" name="service_needed" required><option value="">Choose…</option>{opts}<option value="Multiple services / not sure">Multiple services / not sure</option></select></div>
    <div class="field field--full"><label for="{form_id}-notes">Job notes</label><textarea id="{form_id}-notes" name="job_notes" placeholder="Anything we should know: gate access, dogs, how often you'd like it done…"></textarea></div>
    <div class="field field--hp" aria-hidden="true"><label for="{form_id}-hp">Leave this field empty</label><input id="{form_id}-hp" name="company_website" type="text" tabindex="-1" autocomplete="off"></div>
    <div class="field field--full"><button class="btn btn--primary btn--block" type="submit">Send my quote request</button></div>
  </div>
  <p class="form-note">No obligation. We reply by phone or email, usually within one business day.</p>
</form>"""


def quote_modal():
    return f"""
<dialog class="quote-modal" id="quote-modal" aria-labelledby="modal-form-title">
  <div class="quote-card">
    <button class="modal-close" type="button" data-close-quote aria-label="Close">{ICON['close']}</button>
    {quote_form('modal-form')}
  </div>
</dialog>"""


def header(current):
    def cur(path):
        return ' aria-current="page"' if current == path else ""
    sub = "".join(f'<li><a href="{service_url(s)}"{cur(service_url(s))}>{s["nav"]}</a></li>' for s in SERVICES)
    return f"""
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="container">
    {logo()}
    <nav class="site-nav" id="site-nav" aria-label="Main">
      <ul>
        <li><a href="/"{cur('/')}>Home</a></li>
        <li class="has-sub"><a href="/services/"{cur('/services/')}>Services {ICON['chev']}</a><ul>{sub}</ul></li>
        <li><a href="/about/"{cur('/about/')}>About</a></li>
        <li><a href="/contact/"{cur('/contact/')}>Contact</a></li>
        <li class="nav-cta"><a class="btn btn--primary btn--block" href="/contact/#quote" data-open-quote>Get a free quote</a></li>
      </ul>
    </nav>
    <a class="header-call" href="tel:{BIZ['phone_e164']}" aria-label="Call {BIZ['phone_display']}">{ICON['phone']}<span>{BIZ['phone_display']}</span></a>
    <a class="btn btn--primary header-quote" href="/contact/#quote" data-open-quote aria-label="Get a free quote"><span class="short">Free quote</span><span class="long">Get a free quote</span></a>
    <button class="nav-toggle" type="button" aria-controls="site-nav" aria-expanded="false" aria-label="Menu">{ICON['menu']}</button>
  </div>
</header>"""


def footer():
    services = "".join(f'<li><a href="{service_url(s)}">{s["nav"]}</a></li>' for s in SERVICES)
    areas = " · ".join(SUBURBS)
    return f"""
<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div>
        {logo()}
        <p>Lawn mowing and garden maintenance for homes, rentals, acreage and commercial sites across Deception Bay, Moreton Bay and Brisbane's northside.</p>
        <p><strong style="color:#fff">{BIZ['name']}</strong><br>{PUBLIC_ADDRESS}<br>
        <a href="tel:{BIZ['phone_e164']}">{BIZ['phone_display']}</a><br>
        <a href="mailto:{BIZ['email']}">{BIZ['email']}</a></p>
      </div>
      <div>
        <h3>Services</h3>
        <ul>{services}</ul>
      </div>
      <div>
        <h3>Company</h3>
        <ul>
          <li><a href="/">Home</a></li>
          <li><a href="/services/">All services</a></li>
          <li><a href="/about/">About</a></li>
          <li><a href="/contact/">Contact</a></li>
          <li><a href="/contact/#quote" data-open-quote>Get a free quote</a></li>
        </ul>
      </div>
      <div class="footer-areas">
        <h3>Service areas (22 suburbs)</h3>
        <p>{areas}</p>
      </div>
    </div>
    <div class="footer-bottom">
      <span>© <span id="year">2026</span> {BIZ['name']}. All rights reserved.</span>
      <span>ABN {TODO('ABN')}</span>
    </div>
  </div>
</footer>
<div class="mobile-bar">
  <a class="btn btn--outline" href="tel:{BIZ['phone_e164']}">{ICON['phone']} Call now</a>
  <a class="btn btn--primary" href="/contact/#quote" data-open-quote>Get a free quote</a>
</div>
{quote_modal()}
<script src="/js/site.js" defer></script>"""


def breadcrumb_schema(items):
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": BIZ["domain"] + u}
            for i, (n, u) in enumerate(items)
        ],
    }


def breadcrumb_html(items):
    lis = []
    for i, (n, u) in enumerate(items):
        if i == len(items) - 1:
            lis.append(f'<li aria-current="page">{n}</li>')
        else:
            lis.append(f'<li><a href="{u}">{n}</a></li>')
    return f'<nav class="breadcrumb" aria-label="Breadcrumb"><ol>{"".join(lis)}</ol></nav>'


def local_business(full=True):
    lb = {
        "@type": "LocalBusiness",
        "@id": BIZ["domain"] + "/#business",
        "name": BIZ["name"],
        "alternateName": BIZ["short"],
        "url": BIZ["domain"] + "/",
        "telephone": BIZ["phone_e164"],
        "email": BIZ["email"],
        "image": img_url("home-hero", 1200),
        "address": {
            "@type": "PostalAddress",
            "streetAddress": BIZ["street"],
            "addressLocality": BIZ["suburb"],
            "addressRegion": BIZ["state"],
            "postalCode": BIZ["postcode"],
            "addressCountry": BIZ["country"],
        },
        "geo": {"@type": "GeoCoordinates", "latitude": BIZ["lat"], "longitude": BIZ["lng"]},
        "areaServed": [{"@type": "Place", "name": f"{s}, QLD"} for s in SUBURBS],
        # "openingHoursSpecification": TODO — opening hours were not supplied.
        # "sameAs": TODO — Google Business Profile URL was not supplied.
    }
    if full:
        lb["hasOfferCatalog"] = {
            "@type": "OfferCatalog",
            "name": "Lawn and garden services",
            "itemListElement": [
                {"@type": "Offer", "itemOffered": {"@type": "Service", "name": html.unescape(s["name"]), "url": BIZ["domain"] + service_url(s)}}
                for s in SERVICES
            ],
        }
    return lb


def cta_band(title="Ready for a tidier lawn and garden?", text=None):
    text = text or f"Call {BIZ['phone_display']} or send us the job details and we'll come back with a free, no-obligation quote."
    return f"""
<section class="cta-band">
  <div class="container">
    <div><h2>{title}</h2><p>{text}</p></div>
    <div class="cta-band__actions">
      <a class="btn btn--dark" href="/contact/#quote" data-open-quote>Get a free quote</a>
      <a class="btn btn--outline" href="tel:{BIZ['phone_e164']}">{ICON['phone']} {BIZ['phone_display']}</a>
    </div>
  </div>
</section>"""


def areas_section(green=False, intro=None):
    intro = intro or ("We're based in Deception Bay and travel across 22 suburbs of Moreton Bay and Brisbane's northside, "
                      "from the Caboolture and Burpengary corridor down to Strathpine and Brendale, and east across the Redcliffe peninsula.")
    lis = "".join(f"<li>{s}</li>" for s in SUBURBS)
    cls = "section section--green" if green else "section"
    return f"""
<section class="{cls}" id="areas">
  <div class="container">
    <span class="eyebrow">Service areas</span>
    <h2>Suburbs we service</h2>
    <p class="lede">{intro}</p>
    <ul class="areas">{lis}</ul>
  </div>
</section>"""


def page(path, title, desc, body, schema, canonical=None, noindex=False, og_image="home-hero", extra_head=""):
    canonical = canonical or (BIZ["domain"] + path)
    ld = {"@context": "https://schema.org", "@graph": schema}
    robots = '<meta name="robots" content="noindex, nofollow">' if noindex else '<meta name="robots" content="index, follow, max-image-preview:large">'
    doc = f"""<!DOCTYPE html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{html.escape(desc, quote=True)}">
{robots}
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{BIZ['short']}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{html.escape(desc, quote=True)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{img_url(og_image, 1200)}">
<meta property="og:locale" content="en_AU">
<meta name="theme-color" content="#1f6a41">
<link rel="icon" href="/images/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/images/favicon.svg">
<link rel="preconnect" href="https://images.pexels.com" crossorigin>
<link rel="dns-prefetch" href="https://link.msgsndr.com">
<link rel="stylesheet" href="/css/site.css">
{TRACKING_SCRIPT}
<!-- Google Analytics 4: add the gtag.js snippet here once a GA4 property is created.
     The site pushes these events to window.dataLayer: quote_form_submit, click_to_call, quote_modal_open, thank_you_view -->
<script>window.dataLayer = window.dataLayer || [];</script>
{extra_head}
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head>
<body>
{header(path)}
<main id="main">
{body}
</main>
{footer()}
</body>
</html>
"""
    out = os.path.join(ROOT, path.strip("/"), "index.html") if path != "/" else os.path.join(ROOT, "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(doc)
    return out


# --------------------------------------------------------------------------
# FAQ (homepage) — the six questions are verbatim from the strategy doc.
# --------------------------------------------------------------------------
HOME_FAQ = [
    ("How much does lawn mowing cost in Deception Bay?",
     f"It depends on the size of the lawn, how long the grass is and whether you want edging and a blow-down included. Most standard residential lawns in Deception Bay fall between ${TODO('typical lawn mowing price range, e.g. $X–$Y')} per visit, with regular fortnightly or monthly clients paying less per cut than one-off jobs. Quotes are free and we confirm the price before we start, so there are no surprises."),
    ("Do you mow acreage properties around Narangba and Burpengary East?",
     "Yes. Acreage mowing and slashing is one of our core services. We bring ride-on equipment for lifestyle blocks and larger properties in Narangba, Burpengary East, Dakabin, Morayfield and Caboolture, and we can set up a regular schedule so the block never gets away from you."),
    ("Do you offer commercial lawn mowing contracts across Moreton Bay?",
     "We do. We mow and maintain grounds for commercial properties, rental portfolios and body corporates across our 22 service suburbs in Moreton Bay, including North Lakes, Mango Hill, Redcliffe and Caboolture. Contact us for a scheduled maintenance quote that covers mowing, edging, hedges and garden beds in one visit."),
    ("Which suburbs do you service around Redcliffe and North Lakes?",
     "On the Redcliffe peninsula we cover Redcliffe, Kippa-Ring, Margate, Clontarf, Woody Point, Newport and Rothwell. Around North Lakes we cover North Lakes, Mango Hill, Murrumba Downs, Kallangur, Dakabin and Deception Bay, where we're based. In total we service 22 suburbs across Moreton Bay and Brisbane's northside."),
    ("Can you do hedge trimming and lawn treatments on the same visit?",
     "Yes. Most of our clients book lawn mowing together with hedge trimming, garden maintenance or a lawn treatment so everything is done in one visit by the same crew. Tell us what you need on the quote form and we'll price it as a single job."),
    ("Do you take NDIS lawn mowing and garden maintenance clients in Brisbane?",
     f"{TODO('confirm whether Regal accepts NDIS participants (self- or plan-managed) and how invoicing works')} We provide regular lawn mowing and garden maintenance across 22 suburbs of Brisbane's northside and Moreton Bay. Please call {BIZ['phone_display']} to discuss your plan and how the service can be set up."),
]


def faq_html(faqs):
    items = "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in faqs)
    return f'<div class="faq">{items}</div>'


def faq_schema(faqs):
    def strip(s):
        return html.unescape(re.sub(r"<[^>]+>", "", s))
    return {
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": strip(q), "acceptedAnswer": {"@type": "Answer", "text": strip(a)}}
            for q, a in faqs
        ],
    }


# --------------------------------------------------------------------------
# HOMEPAGE
# --------------------------------------------------------------------------
def build_home():
    cards = "".join(f"""
      <article class="card">
        {img(s['img'], s['alt'], cls='card__img', w=800, h=500, sizes='(min-width: 960px) 33vw, (min-width: 640px) 50vw, 100vw')}
        <div class="card__body">
          <h3><a href="{service_url(s)}" style="text-decoration:none;color:inherit">{s['name']}</a></h3>
          <p>{s['blurb']}</p>
          <a class="card__link" href="{service_url(s)}">Learn more {ICON['arrow']}</a>
        </div>
      </article>""" for s in SERVICES)

    body = f"""
<section class="hero">
  {img('home-hero', 'Lawn mowing in Deception Bay: freshly cut green lawn with a push mower', cls='hero__bg', w=1920, h=1080, eager=True, sizes='100vw')}
  <div class="container">
    <div>
      <span class="eyebrow">Deception Bay · Moreton Bay · Brisbane North</span>
      <h1>Professional Lawn Mowing &amp; Garden Maintenance in Deception Bay</h1>
      <p>Regal Lawns And Gardens is a local, Deception Bay based crew for lawn mowing, garden maintenance, hedge trimming, lawn treatments, tree trimming and acreage work across 22 suburbs of Moreton Bay and Brisbane's northside.</p>
      <div class="hero__actions">
        <a class="btn btn--primary" href="#quote" data-open-quote>Get a free quote</a>
        <a class="btn btn--light" href="tel:{BIZ['phone_e164']}">{ICON['phone']} Call {BIZ['phone_display']}</a>
      </div>
      <ul class="hero__trust">
        <li>{ICON['check']} Free, no-obligation quotes</li>
        <li>{ICON['check']} Locally based in Deception Bay</li>
        <li>{ICON['check']} Residential, acreage &amp; commercial</li>
      </ul>
    </div>
    <div class="quote-card" id="quote">
      {quote_form('home-form', heading='Get a free quote', inline=True)}
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <span class="eyebrow">What we do</span>
    <h2>Lawn and garden services, one local crew</h2>
    <p class="lede">Whether it's a fortnightly mow for a rental in Redcliffe, a slashing job on a Narangba block or a full garden tidy-up in North Lakes, we handle it with our own equipment and take the green waste with us.</p>
    <div class="grid grid--3" style="margin-top:28px">{cards}</div>
  </div>
</section>

<section class="section section--alt">
  <div class="container">
    <div class="two-col">
      <div>
        <span class="eyebrow">Why Regal</span>
        <h2>Lawn mowing in Deception Bay from a crew that actually lives here</h2>
        <p>We're based in Deception Bay, so for anyone on the Redcliffe peninsula, around North Lakes or up the Burpengary and Caboolture corridor we're a short drive away, not a franchise call centre. You deal with one local business from the first quote to the last blow-down.</p>
        <ul class="checks">
          <li><strong>One crew for the whole yard.</strong> Mowing, edging, hedges, garden beds, weed control and tree trimming can all be done on the same visit.</li>
          <li><strong>Quoted up front.</strong> Send the job details or call us and you'll have a clear price before any work starts.</li>
          <li><strong>Residential, acreage and commercial.</strong> From a small courtyard in Margate to a lifestyle block in Burpengary East or a body corporate in Mango Hill.</li>
          <li><strong>Regular or one-off.</strong> Set up a fortnightly or monthly schedule, or book a single clean-up before an inspection or sale.</li>
        </ul>
        <div class="stat-row">
          <div class="stat"><b>22</b><span>suburbs serviced</span></div>
          <div class="stat"><b>6</b><span>lawn &amp; garden services</span></div>
          <div class="stat"><b>Free</b><span>quotes, no obligation</span></div>
        </div>
      </div>
      <div>{img('house', 'Well-kept green lawn at a suburban home in Moreton Bay after regular lawn mowing', w=1200, h=900)}</div>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <span class="eyebrow">How it works</span>
    <h2>Three steps to a tidy yard</h2>
    <ol class="steps">
      <li><h3>Tell us about the job</h3><p>Use the quote form or call {BIZ['phone_display']}. Let us know the suburb, roughly how big the property is and what you need done.</p></li>
      <li><h3>Get your price</h3><p>We come back to you with a clear quote. For regular mowing we'll suggest a schedule that suits the season and your grass type.</p></li>
      <li><h3>We turn up and do it properly</h3><p>Mowed, edged, trimmed and blown down, with the clippings and green waste taken away.</p></li>
    </ol>
  </div>
</section>

<section class="section section--alt">
  <div class="container">
    <span class="eyebrow">Reviews</span>
    <h2>What customers say</h2>
    {TODO('Customer review text and Google Business Profile review link. No reviews were supplied, so nothing is shown here yet. Replace this block with real reviews once the Google Business Profile is live.', inline=False)}
  </div>
</section>

{areas_section(green=True)}

<section class="section" id="faq">
  <div class="container">
    <span class="eyebrow">FAQ</span>
    <h2>Questions people ask us</h2>
    {faq_html(HOME_FAQ)}
  </div>
</section>

{cta_band()}
"""
    schema = [
        local_business(),
        {"@type": "WebSite", "@id": BIZ["domain"] + "/#website", "url": BIZ["domain"] + "/", "name": BIZ["short"], "publisher": {"@id": BIZ["domain"] + "/#business"}},
        {"@type": "WebPage", "@id": BIZ["domain"] + "/#webpage", "url": BIZ["domain"] + "/", "name": "Lawn Mowing Deception Bay | Regal Lawns And Gardens", "isPartOf": {"@id": BIZ["domain"] + "/#website"}, "about": {"@id": BIZ["domain"] + "/#business"}},
        faq_schema(HOME_FAQ),
    ]
    return page(
        "/",
        "Lawn Mowing Deception Bay | Regal Lawns And Gardens",
        "Expert lawn mowing in Deception Bay. Regal Lawns And Gardens offers mowing, garden care, hedging and acreage work across Moreton Bay. Get a free quote.",
        body, schema,
    )


# --------------------------------------------------------------------------
# SERVICES INDEX
# --------------------------------------------------------------------------
def build_services_index():
    cards = "".join(f"""
      <article class="card">
        {img(s['img'], s['alt'], cls='card__img', w=800, h=500, sizes='(min-width: 960px) 33vw, (min-width: 640px) 50vw, 100vw')}
        <div class="card__body">
          <h2 style="font-size:1.2rem;margin:0"><a href="{service_url(s)}" style="text-decoration:none;color:inherit">{s['name']}</a></h2>
          <p>{s['blurb']}</p>
          <a class="card__link" href="{service_url(s)}">View service {ICON['arrow']}</a>
        </div>
      </article>""" for s in SERVICES)
    crumbs = [("Home", "/"), ("Services", "/services/")]
    body = f"""
<section class="hero hero--inner">
  {img('services', 'Lawn mowing and garden maintenance services across Moreton Bay', cls='hero__bg', w=1920, h=1080, eager=True, sizes='100vw')}
  <div class="container">
    <div>
      {breadcrumb_html(crumbs)}
      <h1>Lawn Mowing &amp; Garden Services in Moreton Bay</h1>
      <p>Six services, one local crew. Everything below is available across Deception Bay, the Redcliffe peninsula, North Lakes and the Caboolture to Strathpine corridor.</p>
      <div class="hero__actions">
        <a class="btn btn--primary" href="/contact/#quote" data-open-quote>Get a free quote</a>
        <a class="btn btn--light" href="tel:{BIZ['phone_e164']}">{ICON['phone']} {BIZ['phone_display']}</a>
      </div>
    </div>
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="grid grid--3">{cards}</div>
  </div>
</section>
<section class="section section--alt">
  <div class="container">
    <div class="prose">
      <h2>Bundle services into one visit</h2>
      <p>Most of the properties we look after need more than a mow. A typical regular visit in North Lakes or Redcliffe covers the lawn, the edges, the hedges and a quick tidy of the garden beds, and a seasonal lawn treatment or a bit of tree trimming can be added when it's needed. Booking it all with one crew means one quote, one invoice and no waiting on three different tradies.</p>
      <p>Not sure which service you need? Send us a photo or a quick description on the <a href="/contact/">contact page</a> and we'll tell you what we'd recommend.</p>
    </div>
  </div>
</section>
{areas_section()}
{cta_band()}
"""
    schema = [
        breadcrumb_schema(crumbs),
        {"@type": "ItemList", "name": "Services", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": html.unescape(s["name"]), "url": BIZ["domain"] + service_url(s)} for i, s in enumerate(SERVICES)]},
    ]
    return page("/services/", "Lawn & Garden Services Moreton Bay | Regal Lawns",
                "All six Regal Lawns And Gardens services: lawn mowing, acreage mowing, garden maintenance, hedges, lawn treatments and tree trimming across Moreton Bay.",
                body, schema, og_image="services")


# --------------------------------------------------------------------------
# SERVICE PAGES — copy
# --------------------------------------------------------------------------
SERVICE_COPY = {}

SERVICE_COPY["lawn-mowing"] = dict(
    intro="Looking for reliable lawn mowing in Redcliffe? Regal Lawns And Gardens is based just across the bridge in Deception Bay and mows lawns every week across the peninsula, from Clontarf and Woody Point through Margate and Redcliffe to Kippa-Ring, Rothwell and Newport. Regular or one-off, small courtyard or full quarter-acre, we turn up with our own gear and leave the yard finished.",
    sections=[
        ("What's included in a standard mow",
         """<p>Every mow is a full service, not a quick pass with the mower. On a standard visit we:</p>
<ul class="checks">
<li>Mow the front and back lawn at the right height for the grass type and the season</li>
<li>Whipper-snip along fences, garden beds, paths and around trees</li>
<li>Edge the driveway, footpath and kerb for a clean line</li>
<li>Blow down paths, patios and the driveway so nothing is left behind</li>
<li>Take the clippings away, or leave them if you prefer to compost</li>
</ul>
<p>If the lawn has been left for a while we can do a first cut to get it back under control, then move onto a regular schedule at the normal rate.</p>"""),
        ("Regular lawn mowing for homes and rentals",
         """<p>Most of our Redcliffe clients are on a fortnightly schedule through the warmer months and monthly through winter, which keeps the lawn looking cared for without paying for cuts it doesn't need. We adjust the timing to suit your grass: buffalo and couch lawns on the peninsula grow fast from October to April, and we'll tell you when it's worth stretching the gap.</p>
<p>We also mow for property managers and landlords who need rentals kept tidy between tenancies, and for owners who want the lawn done before an inspection or open home. Give us the address and the dates and we'll fit it in.</p>"""),
        ("Where we mow",
         "<p>This page is about the Redcliffe peninsula, but the same service runs across all 22 of our suburbs: Deception Bay, Rothwell, Kippa-Ring, Margate, Clontarf, Woody Point, Newport, North Lakes, Mango Hill, Murrumba Downs, Kallangur, Dakabin, Narangba, Burpengary, Burpengary East, Morayfield, Caboolture, Strathpine, Lawnton, Bray Park and Brendale. Larger blocks are handled on our <a href=\"/services/acreage-mowing/\">acreage mowing</a> page, and if the grass is more weed than lawn, have a look at <a href=\"/services/lawn-treatments-weed-control/\">lawn treatments and weed control</a>.</p>"),
    ],
    faq=[
        ("How often should a lawn in Redcliffe be mowed?",
         "In summer most couch and buffalo lawns on the peninsula need mowing every 2 weeks. From about May to August, growth slows and every 3 to 4 weeks is usually enough. We'll set the schedule with you and adjust it as the seasons change."),
        ("Do you mow rental properties and vacant homes?",
         "Yes. We work with landlords and property managers across Redcliffe, Kippa-Ring, Margate and Clontarf to keep rentals mowed between tenants and before inspections. We can invoice the agency or the owner directly."),
        ("Do I need to be home when you mow?",
         "No. As long as we can get to the lawn, we can mow while you're at work. Let us know about gate codes, locked side gates or dogs in the job notes when you request a quote."),
    ],
)

SERVICE_COPY["acreage-mowing"] = dict(
    intro="Acreage mowing in Brisbane's north is a different job from a suburban lawn. Lifestyle blocks in Narangba, Burpengary East, Dakabin and out towards Caboolture and Morayfield need ride-on equipment, slashing for the rough paddock areas and someone who will actually keep coming back before the grass gets away. Regal Lawns And Gardens is based in Deception Bay and services acreage properties across Moreton Bay.",
    sections=[
        ("Ride-on mowing and slashing",
         """<p>We match the equipment to the block. The areas around the house, sheds and driveway are mowed with a ride-on for a neat finish, and the larger open sections or paddocks are slashed to keep them under control. On a typical visit we:</p>
<ul class="checks">
<li>Ride-on mow the house yard, entertaining areas and along the driveway</li>
<li>Slash paddocks, verges and rough grass on the rest of the block</li>
<li>Whipper-snip around fences, posts, tanks, sheds and trees</li>
<li>Clear long grass from fire-risk areas and fence lines</li>
<li>Trim overhanging branches along tracks and driveways on request</li>
</ul>"""),
        ("Regular schedules for lifestyle blocks",
         """<p>Acreage in the Narangba and Burpengary East area grows quickly after summer rain, and a block that's been left for two months takes far longer to cut than one on a schedule. We set up regular visits, usually every 3 to 6 weeks through the growing season and less often through winter, so the property stays presentable and the mowing stays quick and affordable.</p>
<p>We also do one-off jobs: clearing an overgrown block before a sale, tidying up for a settlement or getting on top of a property that's been vacant. Send us the address and rough size, and a photo if you have one, and we'll quote it.</p>"""),
        ("Acreage areas we cover",
         "<p>We service acreage and semi-rural properties in Narangba, Burpengary, Burpengary East, Dakabin, Morayfield and Caboolture, plus the larger blocks scattered through Kallangur, Murrumba Downs, Deception Bay, Rothwell and the rest of our 22 suburbs across Moreton Bay and Brisbane's northside. For standard residential lawns see our <a href=\"/services/lawn-mowing/\">lawn mowing</a> page, and for branches over tracks and fence lines see <a href=\"/services/tree-trimming/\">tree trimming</a>.</p>"),
    ],
    faq=[
        ("How big a property can you mow?",
         "We regularly handle blocks from a quarter acre up to several acres across Narangba, Burpengary East and Dakabin. For anything larger, or with steep or heavily treed ground, send us the address and we'll confirm what we can do before quoting."),
        ("How often does acreage need mowing in Brisbane's north?",
         "Through the wet season, roughly November to April, every 3 to 4 weeks keeps a lifestyle block tidy. Over winter that usually stretches to every 6 to 8 weeks. We'll recommend a schedule after we've seen the block."),
        ("Do you slash overgrown blocks before a sale or settlement?",
         "Yes. One-off clean-ups of overgrown acreage in Caboolture, Morayfield and Burpengary are common for us. Long grass takes longer to cut, so the first visit is quoted separately from any ongoing schedule."),
    ],
)

SERVICE_COPY["garden-maintenance"] = dict(
    intro="Garden maintenance in North Lakes and Mango Hill is mostly about keeping newer estate gardens looking the way they did when they were planted: beds weeded, shrubs shaped, mulch topped up and the edges clean. Regal Lawns And Gardens looks after gardens for homeowners, rentals and body corporates across North Lakes, Mango Hill, Murrumba Downs and the rest of Moreton Bay, on a regular schedule or as a one-off tidy-up.",
    sections=[
        ("What our garden maintenance covers",
         """<p>Every garden is different, so we quote to what yours needs. A typical maintenance visit can include:</p>
<ul class="checks">
<li>Weeding garden beds, pathways and paved areas</li>
<li>Pruning and shaping shrubs, natives and ornamentals</li>
<li>Topping up mulch and redefining garden bed edges</li>
<li>Deadheading, cutting back and tidying seasonal plants</li>
<li>Small hedge trims (larger hedges are covered under <a href="/services/hedge-trimming/">hedge trimming</a>)</li>
<li>Removing green waste so the garden is clean when we leave</li>
</ul>
<p>Combined with <a href="/services/lawn-mowing/">lawn mowing</a>, that's the whole yard done in one visit.</p>"""),
        ("Regular garden care for homes, rentals and body corporates",
         """<p>For homeowners in North Lakes and Mango Hill we usually visit every 4 to 8 weeks, which is enough to stop weeds establishing and keep shrubs in shape without it turning into a big job. Property managers use us to keep rental gardens presentable between tenancies, and body corporates and strata managers use us for common-area gardens and entrance beds where a consistent, tidy appearance matters.</p>
<p>One-off garden clean-ups are welcome too: an overgrown garden after a long summer, a tidy before you list the house, or a reset after a tenant moves out.</p>"""),
        ("Garden maintenance areas",
         "<p>As well as North Lakes and Mango Hill we maintain gardens in Murrumba Downs, Kallangur, Dakabin, Deception Bay, Rothwell, Kippa-Ring, Redcliffe, Margate, Clontarf, Woody Point, Newport, Narangba, Burpengary, Burpengary East, Morayfield, Caboolture, Strathpine, Lawnton, Bray Park and Brendale.</p>"),
    ],
    faq=[
        ("How often should a North Lakes garden be maintained?",
         "For most estate gardens in North Lakes and Mango Hill a visit every 4 to 8 weeks keeps weeds down and shrubs tidy. Gardens with lots of fast-growing natives or hedging may need a visit every 4 weeks in summer."),
        ("Do you do one-off garden clean-ups?",
         "Yes. We do single tidy-ups across all 22 of our suburbs, including overgrown rentals and pre-sale clean-ups. The first visit is quoted on what's there, and any ongoing schedule is quoted separately."),
        ("Do you take the green waste away?",
         "Yes. Prunings, weeds and clippings are removed as part of the job unless you'd rather keep them for your own compost or green bin."),
    ],
)

SERVICE_COPY["hedge-trimming"] = dict(
    intro="Hedge trimming in Brisbane's north is about two things: a straight, level result and taking every last clipping away. Regal Lawns And Gardens trims and shapes hedges of all sizes across Brisbane's northside and Moreton Bay, from small lilly pilly borders in Strathpine to long boundary hedges on acreage in Narangba and Caboolture, and we're based in Deception Bay so we're close to all of it.",
    sections=[
        ("Hedge trimming and shaping",
         """<p>We use petrol and battery hedge trimmers and, for tall hedges, pole trimmers and platforms so the top is as level as the sides. A typical hedge trimming job includes:</p>
<ul class="checks">
<li>Trimming the sides straight and the top level</li>
<li>Shaping formal hedges, topiary and feature shrubs</li>
<li>Reducing height on hedges that have grown past the fence line</li>
<li>Cutting back overgrown hedges in stages so they recover well</li>
<li>Raking, blowing down and removing every clipping</li>
</ul>
<p>Common hedges around Brisbane's northside include lilly pilly, murraya, viburnum, photinia, duranta and box. Each responds differently to hard pruning, and we'll tell you if a hedge needs to be brought back over two or three visits rather than one.</p>"""),
        ("Regular hedge maintenance",
         """<p>Hedges look best when they're trimmed little and often. In the growing season, roughly September to April, most hedges in Moreton Bay need a trim every 6 to 8 weeks to hold their shape; through winter that stretches out. We can add hedge trimming to a regular <a href="/services/lawn-mowing/">lawn mowing</a> or <a href="/services/garden-maintenance/">garden maintenance</a> schedule so it's done on the same visit, or book it as a stand-alone job.</p>
<p>For commercial grounds, body corporates and rental properties we keep boundary and entrance hedges tidy on a schedule that suits the site.</p>"""),
        ("Where we trim hedges",
         "<p>We trim hedges across all 22 suburbs we service: Deception Bay, Rothwell, Kippa-Ring, Redcliffe, Margate, Clontarf, Woody Point, Newport, North Lakes, Mango Hill, Murrumba Downs, Kallangur, Dakabin, Narangba, Burpengary, Burpengary East, Morayfield, Caboolture, Strathpine, Lawnton, Bray Park and Brendale. For branches and small trees rather than hedges, see <a href=\"/services/tree-trimming/\">tree trimming</a>.</p>"),
    ],
    faq=[
        ("How often should hedges in Brisbane be trimmed?",
         "Most hedges in Brisbane's north need trimming every 6 to 8 weeks through the growing season and 2 or 3 times over winter. Fast growers like murraya and duranta sit at the shorter end of that range."),
        ("Can you reduce the height of an overgrown hedge?",
         "Usually, yes. Many hedges can be brought down by a third in one visit. Cutting harder than that risks bare patches, so for badly overgrown hedges we'll suggest staging the reduction over 2 or 3 visits."),
        ("Do you remove the hedge clippings?",
         "Yes. All clippings are raked, blown down and taken away as part of the job, whether it's a small border hedge in Strathpine or a long boundary hedge in Caboolture."),
    ],
)

SERVICE_COPY["lawn-treatments-weed-control"] = dict(
    intro="Mowing keeps a lawn tidy, but it won't fix a lawn that's thin, patchy or full of weeds. Regal Lawns And Gardens provides lawn care services across Brisbane's north, including weed control, fertilising and seasonal treatments, for homes in Morayfield, North Lakes, Deception Bay, Redcliffe and the rest of Moreton Bay. New-estate lawns that never established properly and older lawns that have been taken over by weeds are both regular jobs for us.",
    sections=[
        ("Weed control",
         """<p>The most common lawn weeds in Brisbane's north are broadleaf weeds like bindii, clover, cudweed and creeping oxalis, plus grassy weeds such as nutgrass, winter grass and crowsfoot. Treating them properly means using the right product for the weed and the right product for your grass, because what's safe on couch can damage buffalo. We identify the weed, treat it with a selective herbicide where one exists and, for stubborn grassy weeds, work through a programme rather than a single spray.</p>"""),
        ("Fertilising and seasonal lawn treatments",
         """<p>A lawn that's fed properly crowds out weeds on its own. Our lawn treatments include:</p>
<ul class="checks">
<li>Fertilising with a programme matched to couch, buffalo, kikuyu or zoysia</li>
<li>Broadleaf and grassy weed control</li>
<li>Bindii treatment in late winter, before the prickles form</li>
<li>Lawn grub and pest treatment when there's active damage</li>
<li>Advice on watering, mowing height and where the lawn is struggling</li>
</ul>
<p>Treatments are timed to the season. Spring feeds get the lawn growing, summer is about pest pressure, and autumn and late-winter treatments stop weeds from taking hold while the grass is slow.</p>"""),
        ("Lawn care with your regular mow",
         "<p>Most clients add treatments to a regular <a href=\"/services/lawn-mowing/\">lawn mowing</a> schedule so the same crew that cuts the grass is also watching how it's going. That's the easiest way to keep a lawn healthy in Moreton Bay's climate. We provide lawn care services across all 22 of our suburbs, from Caboolture, Morayfield and Burpengary through North Lakes, Mango Hill and Kallangur to Deception Bay, Redcliffe and the peninsula. Garden beds are covered under <a href=\"/services/garden-maintenance/\">garden maintenance</a>.</p>"),
    ],
    faq=[
        ("When is the best time to treat bindii in Brisbane?",
         "Late winter, usually July to August, before the plant sets its prickly seed heads. By the time you feel bindii underfoot in spring it has already seeded, so an early treatment in Morayfield, North Lakes or Deception Bay saves a summer of prickles."),
        ("Will weed control damage my buffalo lawn?",
         "Not if the right product is used. Many common broadleaf herbicides are unsafe on buffalo, so we identify your grass type before treating. Buffalo lawns are very common across North Lakes, Mango Hill and the Redcliffe peninsula."),
        ("How many treatments does a weedy lawn need?",
         "A single treatment handles most broadleaf weeds. Grassy weeds like nutgrass and winter grass usually take 2 or 3 treatments over a season, combined with feeding so the lawn thickens up and stops new weeds getting in."),
    ],
)

SERVICE_COPY["tree-trimming"] = dict(
    intro="Tree trimming on Brisbane's northside is usually about a branch that's grown too far: over the roof, over the fence, across the driveway or into the powerline clearance zone. Regal Lawns And Gardens trims and lops small to medium trees across Moreton Bay and Brisbane's northside, from Kallangur and Strathpine through Burpengary and Caboolture to Deception Bay and the Redcliffe peninsula, and takes the branches away when we're done.",
    sections=[
        ("Tree trimming and lopping services",
         """<p>Our tree work covers the jobs that come up around an ordinary home or acreage property:</p>
<ul class="checks">
<li>Cutting back branches overhanging roofs, gutters, sheds and fences</li>
<li>Lifting low canopies over driveways, paths and lawns</li>
<li>Trimming small and medium trees to shape or reduce size</li>
<li>Clearing storm-damaged and hanging limbs</li>
<li>Removing small trees and unwanted saplings</li>
<li>Chipping or removing all branches and debris</li>
</ul>
<p>We work from the ground, from ladders and with pole saws. Large trees, trees close to powerlines and anything that needs climbing or a cherry picker are the job of a qualified arborist, and we'll tell you honestly if that's what your tree needs.</p>"""),
        ("Storm season and council rules",
         """<p>Brisbane's northside gets its worst storms between November and March. Overhanging limbs and dead wood are the branches most likely to come down, so trimming them back in winter and spring is cheaper than dealing with damage in summer. We can combine tree trimming with <a href="/services/hedge-trimming/">hedge trimming</a> and a general clean-up so the whole property is storm-ready in one visit.</p>
<p>Moreton Bay Regional Council protects some trees under its planning scheme. Minor pruning of branches on your own property is generally fine, but if you're unsure whether a tree is protected, check with council before booking removal. We're happy to trim while you confirm.</p>"""),
        ("Tree trimming areas",
         "<p>We trim trees across all 22 suburbs we service: Kallangur, Murrumba Downs, Dakabin, North Lakes, Mango Hill, Deception Bay, Rothwell, Kippa-Ring, Redcliffe, Margate, Clontarf, Woody Point, Newport, Narangba, Burpengary, Burpengary East, Morayfield, Caboolture, Strathpine, Lawnton, Bray Park and Brendale. For paddocks and tracks on larger properties, see <a href=\"/services/acreage-mowing/\">acreage mowing</a>.</p>"),
    ],
    faq=[
        ("What size trees can you trim?",
         "We handle small to medium trees that can be reached safely from the ground, a ladder or a pole saw, typically up to around 6 to 8 metres. Larger trees, removals near powerlines and anything requiring climbing should go to a qualified arborist."),
        ("Can you trim my neighbour's branches that overhang my yard?",
         "In Queensland you can generally trim branches that overhang your boundary back to the fence line, as long as the tree isn't protected. We regularly do this for homes in Kallangur, Strathpine and Redcliffe. Talking to the neighbour first always helps."),
        ("Do you take the branches away?",
         "Yes. Branches, offcuts and leaf litter are removed as part of the job. If you'd like the wood cut into lengths and left for firewood or mulch, just let us know when you book."),
    ],
)


def build_service(s):
    copy = SERVICE_COPY[s["slug"]]
    crumbs = [("Home", "/"), ("Services", "/services/"), (html.unescape(s["name"]), service_url(s))]
    sections_html = "".join(f"<h2>{h}</h2>{body}" for h, body in copy["sections"])
    related = "".join(f'<li><a href="{service_url(SERVICE_BY_SLUG[r])}">{SERVICE_BY_SLUG[r]["nav"]}</a></li>' for r in s["related"])
    CUR = ' aria-current="page"'
    all_services = "".join(
        f'<li><a href="{service_url(x)}"{CUR if x is s else ""}>{x["nav"]}</a></li>' for x in SERVICES)
    body = f"""
<section class="hero hero--inner">
  {img(s['img'], s['alt'], cls='hero__bg', w=1920, h=1080, eager=True, sizes='100vw')}
  <div class="container">
    <div>
      {breadcrumb_html(crumbs)}
      <h1>{s['h1']}</h1>
      <p>{copy['intro']}</p>
      <div class="hero__actions">
        <a class="btn btn--primary" href="/contact/#quote" data-open-quote data-service="{html.escape(s['form_value'])}">Get a free quote</a>
        <a class="btn btn--light" href="tel:{BIZ['phone_e164']}">{ICON['phone']} {BIZ['phone_display']}</a>
      </div>
    </div>
  </div>
</section>
<section class="section">
  <div class="container content-grid">
    <div class="prose">
      <div class="figure">{img(s['img2'], s['alt'], w=1200, h=675, sizes='(min-width: 960px) 760px, 100vw')}</div>
      {sections_html}
      <h2>Frequently asked questions</h2>
      {faq_html(copy['faq'])}
    </div>
    <aside class="sidebar">
      <div class="cta-card">
        <h3>Get a free quote</h3>
        <p>Tell us the suburb, the size of the property and what you need done.</p>
        <a class="phone" href="tel:{BIZ['phone_e164']}">{BIZ['phone_display']}</a>
        <p><a href="mailto:{BIZ['email']}" style="color:#fff">{BIZ['email']}</a></p>
        <a class="btn btn--primary" href="/contact/#quote" data-open-quote data-service="{html.escape(s['form_value'])}">Request a quote</a>
      </div>
      <div class="side-list">
        <h3>All services</h3>
        <ul>{all_services}</ul>
      </div>
      <div class="side-list">
        <h3>Often booked with this</h3>
        <ul>{related}</ul>
      </div>
    </aside>
  </div>
</section>
{areas_section(green=True)}
{cta_band()}
"""
    schema = [
        breadcrumb_schema(crumbs),
        {
            "@type": "Service",
            "@id": BIZ["domain"] + service_url(s) + "#service",
            "name": html.unescape(s["name"]),
            "serviceType": html.unescape(s["name"]),
            "description": s["desc"],
            "url": BIZ["domain"] + service_url(s),
            "image": img_url(s["img"], 1200),
            "provider": local_business(full=False),
            "areaServed": [{"@type": "Place", "name": f"{x}, QLD"} for x in SUBURBS],
        },
        faq_schema(copy["faq"]),
    ]
    return page(service_url(s), s["title"], s["desc"], body, schema, og_image=s["img"])


# --------------------------------------------------------------------------
# ABOUT
# --------------------------------------------------------------------------
def build_about():
    crumbs = [("Home", "/"), ("About", "/about/")]
    body = f"""
<section class="hero hero--inner">
  {img('about', 'Regal Lawns And Gardens: lawn and garden maintenance tools ready for a job in Deception Bay', cls='hero__bg', w=1920, h=1080, eager=True, sizes='100vw')}
  <div class="container">
    <div>
      {breadcrumb_html(crumbs)}
      <h1>About Regal Lawns And Gardens</h1>
      <p>A local lawn mowing and garden maintenance business based in Deception Bay, servicing 22 suburbs across Moreton Bay and Brisbane's northside.</p>
    </div>
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="two-col">
      <div class="prose">
        <h2>Local, and based where we work</h2>
        <p>Regal Lawns And Gardens PTY LTD is run by Ben Butler from Deception Bay. Being based here rather than across town means we're a short drive from every suburb we service, whether that's the Redcliffe peninsula to the east, North Lakes and Kallangur to the south or the Burpengary and Caboolture corridor to the north.</p>
        <p>We do lawn mowing, acreage mowing and slashing, garden maintenance, hedge trimming, lawn treatments and weed control, and tree trimming, for homeowners, landlords and property managers, body corporates and commercial sites. Most clients use us for more than one of those, on a regular schedule, so their whole yard is handled by one crew on one visit.</p>
        <h2>How we work</h2>
        <ul class="checks">
          <li><strong>Quoted before we start.</strong> You'll know the price up front, whether it's a one-off clean-up or an ongoing schedule.</li>
          <li><strong>Our own equipment.</strong> Mowers, ride-ons, trimmers and pole saws, with the green waste taken away afterwards.</li>
          <li><strong>Straight answers.</strong> If a tree needs an arborist or a lawn needs a treatment programme rather than a quick spray, we'll say so.</li>
        </ul>
        <p>{TODO('years in business, background of Ben Butler, team size, insurance / licences. None of these were supplied; do not publish claims until confirmed.')}</p>
      </div>
      <div>
        {img('house-2', 'Neatly mowed lawn and tidy garden at a Moreton Bay home', w=1200, h=900)}
      </div>
    </div>
  </div>
</section>
<section class="section section--alt">
  <div class="container">
    <div class="grid grid--3">
      <div class="card card--plain"><div class="icon">{ICON['pin']}</div><h3>Based in Deception Bay</h3><p>{PUBLIC_ADDRESS}. We service 22 suburbs from Caboolture to Brendale and across the Redcliffe peninsula.</p></div>
      <div class="card card--plain"><div class="icon">{ICON['home']}</div><h3>Residential, acreage &amp; commercial</h3><p>Small suburban yards, lifestyle blocks, rental portfolios and body corporate grounds.</p></div>
      <div class="card card--plain"><div class="icon">{ICON['tag']}</div><h3>Free quotes</h3><p>Call {BIZ['phone_display']} or use the quote form and we'll come back to you with a price.</p></div>
    </div>
  </div>
</section>
{areas_section()}
{cta_band()}
"""
    schema = [
        breadcrumb_schema(crumbs),
        {"@type": "AboutPage", "url": BIZ["domain"] + "/about/", "name": "About Regal Lawns And Gardens", "about": {"@id": BIZ["domain"] + "/#business"}},
        local_business(full=False),
    ]
    return page("/about/", "About Us | Regal Lawns And Gardens, Deception Bay",
                "Regal Lawns And Gardens is a Deception Bay lawn mowing and garden maintenance business run by Ben Butler, servicing 22 suburbs across Moreton Bay.",
                body, schema, og_image="about")


# --------------------------------------------------------------------------
# CONTACT
# --------------------------------------------------------------------------
def build_contact():
    crumbs = [("Home", "/"), ("Contact", "/contact/")]
    body = f"""
<section class="hero hero--inner">
  {img('house', 'Contact Regal Lawns And Gardens for lawn mowing and garden maintenance in Deception Bay', cls='hero__bg', w=1920, h=1080, eager=True, sizes='100vw')}
  <div class="container">
    <div>
      {breadcrumb_html(crumbs)}
      <h1>Contact Regal Lawns And Gardens</h1>
      <p>Call, email or send the job details below for a free quote on lawn mowing and garden maintenance anywhere in our 22 service suburbs.</p>
    </div>
  </div>
</section>
<section class="section">
  <div class="container content-grid" style="grid-template-columns:minmax(0,1fr)">
    <div class="two-col" style="align-items:start">
      <div>
        <h2>Get in touch</h2>
        <ul class="contact-list">
          <li>{ICON['phone']}<div><a href="tel:{BIZ['phone_e164']}">{BIZ['phone_display']}</a><small>Call or text. If we're on a mower we'll call you back.</small></div></li>
          <li>{ICON['mail']}<div><a href="mailto:{BIZ['email']}">{BIZ['email']}</a><small>Email the job details and a photo if you have one.</small></div></li>
          <li>{ICON['pin']}<div><strong>{PUBLIC_ADDRESS}</strong><small>Servicing Moreton Bay and Brisbane's northside.</small></div></li>
          <li>{ICON['clock']}<div><strong>Opening hours</strong><small>{TODO('opening hours (e.g. Mon–Fri 7am–5pm, Sat 7am–1pm)')}</small></div></li>
        </ul>
        <div class="notice"><strong>Google Business Profile:</strong> {TODO('Google Business Profile link and review link once the profile is verified')}</div>
        <h3 style="margin-top:28px">What to include in your quote request</h3>
        <ul>
          <li>The property address or suburb</li>
          <li>Roughly how big the lawn or block is</li>
          <li>Which services you need, and whether it's one-off or regular</li>
          <li>Access details: side gates, locks, dogs</li>
        </ul>
      </div>
      <div class="quote-card" id="quote">
        {quote_form('contact-form', heading='Request a free quote', inline=True)}
      </div>
    </div>
  </div>
</section>
{areas_section(green=True)}
"""
    schema = [
        breadcrumb_schema(crumbs),
        {"@type": "ContactPage", "url": BIZ["domain"] + "/contact/", "name": "Contact Regal Lawns And Gardens", "about": {"@id": BIZ["domain"] + "/#business"}},
        local_business(full=False),
    ]
    return page("/contact/", "Contact Us | Free Quotes | Regal Lawns And Gardens",
                f"Contact Regal Lawns And Gardens in Deception Bay on {BIZ['phone_display']} for a free lawn mowing or garden maintenance quote anywhere in Moreton Bay.",
                body, schema, og_image="house")


# --------------------------------------------------------------------------
# THANK YOU
# --------------------------------------------------------------------------
def build_thanks():
    body = f"""
<section class="section">
  <div class="container">
    <div class="thanks">
      <div class="tick">{ICON['check']}</div>
      <h1>Thanks, we've got your request</h1>
      <p class="lede" style="margin:0 auto 20px">We'll look over the details and come back to you with a quote, usually within one business day. If it's urgent, call us on <a href="tel:{BIZ['phone_e164']}"><strong>{BIZ['phone_display']}</strong></a>.</p>
      <div class="hero__actions" style="justify-content:center">
        <a class="btn btn--dark" href="/">Back to the homepage</a>
        <a class="btn btn--outline" href="/services/">Browse our services</a>
      </div>
    </div>
  </div>
</section>
"""
    extra = "<script>window.dataLayer.push({event:'thank_you_view'});</script>"
    schema = [{"@type": "WebPage", "url": BIZ["domain"] + "/thank-you/", "name": "Thank you"}]
    return page("/thank-you/", "Thanks | Regal Lawns And Gardens", "Your quote request has been received.", body, schema,
                noindex=True, extra_head=extra)


# --------------------------------------------------------------------------
# 404, sitemap, robots
# --------------------------------------------------------------------------
def build_404():
    body = f"""
<section class="section">
  <div class="container">
    <div class="thanks">
      <h1>Page not found</h1>
      <p class="lede" style="margin:0 auto 20px">That page doesn't exist. Try one of the links below or call {BIZ['phone_display']}.</p>
      <div class="hero__actions" style="justify-content:center">
        <a class="btn btn--dark" href="/">Homepage</a>
        <a class="btn btn--outline" href="/services/">Services</a>
        <a class="btn btn--outline" href="/contact/">Contact</a>
      </div>
    </div>
  </div>
</section>
"""
    doc_path = page("/404/", "Page not found | Regal Lawns And Gardens", "Page not found.", body, [], noindex=True)
    # move to /404.html for static hosts
    with open(doc_path, encoding="utf-8") as f:
        content = f.read()
    os.remove(doc_path)
    os.rmdir(os.path.dirname(doc_path))
    with open(os.path.join(ROOT, "404.html"), "w", encoding="utf-8") as f:
        f.write(content)


def build_sitemap(paths):
    urls = "".join(f"  <url><loc>{BIZ['domain']}{p}</loc><changefreq>monthly</changefreq><priority>{'1.0' if p == '/' else '0.8'}</priority></url>\n" for p in paths)
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "</urlset>\n")
    with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(f"User-agent: *\nAllow: /\nDisallow: /thank-you/\n\nSitemap: {BIZ['domain']}/sitemap.xml\n")


def build_assets():
    with open(os.path.join(ROOT, "images", "favicon.svg"), "w", encoding="utf-8") as f:
        f.write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48"><rect width="48" height="48" rx="10" fill="#1f6a41"/>'
                '<path d="M10 30l4-12 6 8 4-14 4 14 6-8 4 12z" fill="#f0b23a"/><rect x="10" y="32" width="28" height="5" rx="2" fill="#f0b23a"/></svg>\n')
    with open(os.path.join(ROOT, "images", "placeholder.svg"), "w", encoding="utf-8") as f:
        f.write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 1000"><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">'
                '<stop offset="0" stop-color="#2a8a55"/><stop offset="1" stop-color="#164a2e"/></linearGradient></defs>'
                '<rect width="1600" height="1000" fill="url(#g)"/>'
                '<path d="M0 1000 L0 760 Q400 640 800 760 T1600 760 L1600 1000Z" fill="#1f6a41" opacity=".8"/>'
                '<path d="M0 1000 L0 860 Q400 780 800 860 T1600 860 L1600 1000Z" fill="#164a2e" opacity=".8"/></svg>\n')


def main():
    build_assets()
    paths = ["/", "/services/"] + [service_url(s) for s in SERVICES] + ["/about/", "/contact/"]
    build_home()
    build_services_index()
    for s in SERVICES:
        build_service(s)
    build_about()
    build_contact()
    build_thanks()
    build_404()
    build_sitemap(paths)
    print("Built", len(paths) + 2, "pages")
    print("\nPlaceholders to replace before launch:")
    for p in dict.fromkeys(PLACEHOLDERS):
        print(" -", p)


if __name__ == "__main__":
    main()
