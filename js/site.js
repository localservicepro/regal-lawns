/* Regal Lawns And Gardens — site behaviour
 * - Mobile nav toggle
 * - "Get a free quote" modal (native <dialog>)
 * - Quote form validation, optional POST to an endpoint, then redirect to /thank-you/
 *
 * CRM: the LeadConnector external-tracking.js script (loaded in <head>) listens for
 * form submissions on the page and forwards the field values to the CRM. Field names
 * match the CRM contact fields exactly:
 *   full_name, email, phone, property_address, property_size, service_needed, job_notes
 */
(function () {
  'use strict';

  // Optional: set a form endpoint here (e.g. a CRM webhook / form-handler URL).
  // Leave empty to rely on the tracking script alone.
  var FORM_ENDPOINT = '';
  var THANK_YOU_URL = '/thank-you/';
  var TRACKING_GRACE_MS = 600; // give the tracking script time to capture the submit

  /* ---------- Mobile nav ---------- */
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('site-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && nav.classList.contains('is-open')) {
        nav.classList.remove('is-open');
        toggle.setAttribute('aria-expanded', 'false');
        toggle.focus();
      }
    });
  }

  /* ---------- Quote modal ---------- */
  var modal = document.getElementById('quote-modal');
  var lastFocus = null;

  function openModal(service) {
    if (!modal) return;
    lastFocus = document.activeElement;
    if (service) {
      var sel = modal.querySelector('select[name="service_needed"]');
      if (sel) {
        for (var i = 0; i < sel.options.length; i++) {
          if (sel.options[i].value === service) { sel.selectedIndex = i; break; }
        }
      }
    }
    if (typeof modal.showModal === 'function') {
      modal.showModal();
    } else {
      modal.setAttribute('open', '');
    }
    document.body.style.overflow = 'hidden';
    var first = modal.querySelector('input:not([type="hidden"]):not([tabindex="-1"])');
    if (first) setTimeout(function () { first.focus(); }, 30);
    if (window.dataLayer) window.dataLayer.push({ event: 'quote_modal_open' });
  }

  function closeModal() {
    if (!modal) return;
    if (typeof modal.close === 'function' && modal.open) modal.close();
    else modal.removeAttribute('open');
    document.body.style.overflow = '';
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }

  document.addEventListener('click', function (e) {
    var trigger = e.target.closest('[data-open-quote]');
    if (trigger) {
      e.preventDefault();
      openModal(trigger.getAttribute('data-service') || '');
      return;
    }
    if (e.target.closest('[data-close-quote]')) {
      e.preventDefault();
      closeModal();
    }
  });

  if (modal) {
    // click on the backdrop closes
    modal.addEventListener('click', function (e) {
      if (e.target === modal) closeModal();
    });
    modal.addEventListener('close', function () {
      document.body.style.overflow = '';
    });
  }

  /* ---------- Quote forms (modal + inline) ---------- */
  function showError(form, msg) {
    var box = form.querySelector('.form-error');
    if (!box) return;
    box.textContent = msg;
    box.classList.add('is-visible');
  }

  function clearError(form) {
    var box = form.querySelector('.form-error');
    if (box) { box.textContent = ''; box.classList.remove('is-visible'); }
  }

  function validPhone(v) {
    var digits = v.replace(/[^\d+]/g, '');
    return digits.length >= 8;
  }

  function handleSubmit(e) {
    var form = e.target;
    if (!form.classList.contains('quote-form')) return;
    e.preventDefault(); // static site: no server to post to
    clearError(form);

    if (form.dataset.submitting === '1') return;

    // Honeypot: bots fill this, humans never see it
    var hp = form.querySelector('input[name="company_website"]');
    if (hp && hp.value) { window.location.href = THANK_YOU_URL; return; }

    var name = form.querySelector('[name="full_name"]');
    var email = form.querySelector('[name="email"]');
    var phone = form.querySelector('[name="phone"]');
    var address = form.querySelector('[name="property_address"]');
    var service = form.querySelector('[name="service_needed"]');

    if (!name.value.trim()) { showError(form, 'Please enter your name.'); name.focus(); return; }
    if (!validPhone(phone.value)) { showError(form, 'Please enter a phone number we can call you back on.'); phone.focus(); return; }
    if (!email.value.trim() || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)) { showError(form, 'Please enter a valid email address.'); email.focus(); return; }
    if (!address.value.trim()) { showError(form, 'Please enter the property address or suburb.'); address.focus(); return; }
    if (service && !service.value) { showError(form, 'Please choose the service you need.'); service.focus(); return; }

    form.dataset.submitting = '1';
    var btn = form.querySelector('button[type="submit"]');
    if (btn) { btn.disabled = true; btn.textContent = 'Sending…'; }

    var payload = {};
    new FormData(form).forEach(function (v, k) { if (k !== 'company_website') payload[k] = v; });
    payload.page = window.location.href;

    if (window.dataLayer) window.dataLayer.push({ event: 'quote_form_submit', service: payload.service_needed || '' });

    function go() { window.location.href = THANK_YOU_URL; }

    if (FORM_ENDPOINT) {
      var done = false;
      var finish = function () { if (!done) { done = true; go(); } };
      try {
        fetch(FORM_ENDPOINT, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
          keepalive: true
        }).then(finish, finish);
      } catch (err) { finish(); }
      setTimeout(finish, 4000);
    } else {
      // Let the external tracking script observe the submit before we leave the page.
      setTimeout(go, TRACKING_GRACE_MS);
    }
  }

  document.addEventListener('submit', handleSubmit);

  /* ---------- Click-to-call tracking ---------- */
  document.addEventListener('click', function (e) {
    var a = e.target.closest('a[href^="tel:"]');
    if (a && window.dataLayer) window.dataLayer.push({ event: 'click_to_call' });
  });

  /* ---------- Footer year ---------- */
  var y = document.getElementById('year');
  if (y) y.textContent = String(new Date().getFullYear());
})();
