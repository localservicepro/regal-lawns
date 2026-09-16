# Regal Lawns And Gardens — website

Static, mobile-first site for **Regal Lawns And Gardens PTY LTD** (Deception Bay QLD 4508), built from the
SEO strategy document dated 10 September 2026. No framework, no build dependencies beyond Python 3.

## Pages

| URL | Target keyword | Notes |
|---|---|---|
| `/` | lawn mowing deception bay | Exact H1, title and description from the strategy doc. LocalBusiness + FAQPage (12 Q&As) schema, speakable summary, recent-work gallery, at-a-glance facts, service-match table, lawn care guide. |
| `/services/` | — | Hub page linking the six service pages |
| `/services/lawn-mowing/` | lawn mowing redcliffe | Service + FAQPage + Breadcrumb schema |
| `/services/acreage-mowing/` | acreage mowing brisbane | " |
| `/services/garden-maintenance/` | garden maintenance north lakes | " |
| `/services/hedge-trimming/` | hedge trimming brisbane | " |
| `/services/lawn-treatments-weed-control/` | lawn care services brisbane | " |
| `/services/tree-trimming/` | tree trimming brisbane northside | " |
| `/about/` | — | |
| `/contact/` | — | Inline quote form |
| `/thank-you/` | — | `noindex`, form redirect target |
| `/404.html` | — | |

Plus `sitemap.xml`, `robots.txt`, `images/favicon.svg`, `images/placeholder.svg`.

All 22 service suburbs appear as visible text in the footer of every page and in a "Suburbs we service" block on
every page, and in `areaServed` in the schema. The street address (19 Clair Ave) is in the schema only; the page
shows "Deception Bay QLD 4508".

## Editing

Everything is generated from **`build/build.py`** (content, NAP, suburbs, schema, header/footer). Edit that file, then:

```
python3 build/build.py
```

The script prints the list of placeholders still in the copy. `css/site.css` and `js/site.js` are hand-written and
served as-is. Do not edit the generated `index.html` files directly.

## Quote form and CRM

* The header "Get a free quote" button (and every other quote CTA) opens a `<dialog>` with the form.
  The homepage hero and the contact page also carry the same form inline.
* Field `name` attributes map 1:1 to the CRM contact fields:

  | Field | `name` | CRM merge field |
  |---|---|---|
  | Name | `full_name` | `{{contact.full_name}}` |
  | Email | `email` | `{{contact.email}}` |
  | Phone | `phone` | `{{contact.phone}}` |
  | Property Address | `property_address` | `{{contact.property_address}}` |
  | Property Size | `property_size` | `{{contact.property_size}}` |
  | Service Needed | `service_needed` | `{{contact.service_needed}}` |
  | Job Notes | `job_notes` | `{{contact.job_notes}}` |

* The LeadConnector tracking script (`tk_6ac0af015fe844119d96e63a3a0dbc4e`) is in the `<head>` of every page and
  observes the native `submit` event. On submit the JS validates, waits 600 ms for the tracker, then redirects to
  `/thank-you/`.
* `FORM_ENDPOINT` in `js/site.js` is empty. If you later want the submission POSTed somewhere as JSON as well, set it
  there; the redirect then happens after the POST completes.
* Events pushed to `window.dataLayer` for GA4/GTM: `quote_modal_open`, `quote_form_submit`, `click_to_call`,
  `thank_you_view`. There is a commented slot in the `<head>` for the GA4 snippet.
* A honeypot field (`company_website`) is included for spam.

## Stock images (Pexels, free licence, no attribution required)

Images are hotlinked from `images.pexels.com` with responsive `srcset` and a local SVG fallback if the CDN fails.
To self-host instead, run `scripts/download-images.sh` and point `img_url()` in the build script at `/images/`.

| Key | Pexels photo | Used on |
|---|---|---|
| home-hero | [6728919](https://www.pexels.com/photo/6728919/) — person mowing a sunlit lawn (Magic K) | Homepage hero |
| services | [6728933](https://www.pexels.com/photo/6728933/) — man mowing lawn | Services hub hero |
| lawn-mowing | [11364122](https://www.pexels.com/photo/11364122/) — person using a lawn mower (Pascal Küffer) | Lawn mowing hero + cards |
| lawn-mowing-2 | [4162011](https://www.pexels.com/photo/4162011/) — lawn mower on grass (Magda Ehlers) | Lawn mowing body |
| acreage | [173552](https://www.pexels.com/photo/173552/) — man riding a lawn mower | Acreage hero + cards |
| acreage-2 | [12130131](https://www.pexels.com/photo/12130131/) — tractor on green field | Acreage body |
| garden | [5231048](https://www.pexels.com/photo/5231048/) — gardener cutting branches | Garden maintenance hero + cards |
| garden-2 | [12110580](https://www.pexels.com/photo/12110580/) — gloved hands gardening | Garden maintenance body |
| hedge | [24595771](https://www.pexels.com/photo/24595771/) — man cutting hedge with trimmer (Aleksander Dumała) | Hedge trimming hero + cards |
| hedge-2 | [7813043](https://www.pexels.com/photo/7813043/) — man trimming hedges (Indi Van Kuijk) | Hedge trimming body |
| treatments | [16603972](https://www.pexels.com/photo/16603972/) — dandelion in grass | Lawn treatments hero + cards |
| treatments-2 | [12887876](https://www.pexels.com/photo/12887876/) — sprinklers on green grass | Lawn treatments body |
| tree | [7509492](https://www.pexels.com/photo/7509492/) — man on ladder cutting a branch (Mark Stebnicki) | Tree trimming hero + cards |
| tree-2 | [4206115](https://www.pexels.com/photo/4206115/) — person using chainsaw | Tree trimming body |
| about | [16680733](https://www.pexels.com/photo/16680733/) — gardening tools in a wheelbarrow | About hero |
| house | [7546775](https://www.pexels.com/photo/7546775/) — house backyard with green lawn | Homepage, contact hero |
| house-2 | [5178034](https://www.pexels.com/photo/5178034/) — aerial view of house with lawn | About body |

## Placeholders to replace before launch

Search the built HTML for `class="todo"` / `todo-block`. Each one is a fact the strategy doc did not supply:

1. **ABN** (footer, every page)
2. **Opening hours** (contact page; also add `openingHoursSpecification` to the LocalBusiness schema in `build.py`)
3. **Google Business Profile link / review link** (contact page; also add `sameAs` in the schema)
4. **Customer review text** (homepage "What customers say" block)
4a. **Recent work photos**: the homepage gallery uses six stock photos with service-type captions; swap in real job photos and suburbs
5. **Typical lawn mowing price range** (homepage FAQ answer 1)
6. **NDIS**: whether Regal accepts NDIS participants (homepage FAQ answer 6)
7. **About page facts**: years in business, Ben Butler's background, team size, insurance and licences

Also: the schema `geo` coordinates are the approximate Deception Bay suburb centre, not the exact street address.

## Hosting

Any static host (Netlify, Cloudflare Pages, Vercel, S3, cPanel). The site uses root-relative URLs (`/css/site.css`,
`/services/lawn-mowing/`) so it must be served from the domain root. Serve `404.html` for missing pages.
