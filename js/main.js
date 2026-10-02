/* บ้านเราหมูกระทะ — language toggle, nav, hours */
(function () {
  var C = window.SITE_CONFIG || {};
  var KEY = 'brm_lang';

  // ---- values from js/config.js (one place to edit) ----
  // <a data-cfg-href="LINE_URL">  -> href from config (static href is only a no-JS fallback)
  // <a data-cfg-href="A|B">       -> first non-empty of A, B
  // <span class="js-line-id">     -> LINE ID text
  document.querySelectorAll('[data-cfg-href]').forEach(function (a) {
    var keys = a.getAttribute('data-cfg-href').split('|');
    for (var i = 0; i < keys.length; i++) { var v = (C[keys[i]] || '').trim(); if (v) { a.href = v; break; } }
  });
  if (C.LINE_ID) document.querySelectorAll('.js-line-id').forEach(function (el) { el.textContent = C.LINE_ID; });

  // ---- booking mode: LINE card while BOOKING_API_URL is empty; real form once it is set ----
  // (?booking=test previews the form in test mode: nothing is sent, clearly labelled)
  var live = !!(C.BOOKING_API_URL || '').trim(), test = !live && /[?&]booking=test\b/.test(location.search);
  document.documentElement.classList.toggle('booking-live', live || test);
  document.documentElement.classList.toggle('booking-test', test);

  var titles = {
    th: document.title,
    en: 'Baan Rao Moo Krata, Udon Thani | Charcoal moo krata, open daily 5–10pm'
  };
  var els = document.querySelectorAll('[data-en]');
  els.forEach(function (el) { el.dataset.th = el.innerHTML; });
  var phs = document.querySelectorAll('[data-en-ph]');
  phs.forEach(function (el) { el.dataset.thPh = el.getAttribute('placeholder') || ''; });

  function getLang() {
    var q = new URLSearchParams(location.search).get('lang');
    if (q === 'en' || q === 'th') return q;
    try { return localStorage.getItem(KEY) || 'th'; } catch (e) { return 'th'; }
  }
  function apply(lang) {
    els.forEach(function (el) { el.innerHTML = lang === 'en' ? el.dataset.en : el.dataset.th; });
    phs.forEach(function (el) { el.setAttribute('placeholder', lang === 'en' ? el.dataset.enPh : el.dataset.thPh); });
    document.documentElement.lang = lang;
    document.title = titles[lang];
    var t = document.getElementById('langToggle');
    if (t) { t.children[0].classList.toggle('on', lang === 'th'); t.children[1].classList.toggle('on', lang === 'en'); }
    window.SITE_LANG = lang;
    document.dispatchEvent(new CustomEvent('langchange', { detail: lang }));
  }
  window.SITE_LANG = getLang();
  document.getElementById('langToggle').addEventListener('click', function () {
    var next = window.SITE_LANG === 'th' ? 'en' : 'th';
    try { localStorage.setItem(KEY, next); } catch (e) {}
    apply(next);
  });

  // hours from config (one place to edit)
  var hrs = (C.OPEN_TIME || '17:00') + '–' + (C.CLOSE_TIME || '22:00');
  document.querySelectorAll('.js-hours').forEach(function (el) { el.textContent = hrs; });
  els.forEach(function (el) { if (el.dataset.th.indexOf('js-hours') > -1) { el.dataset.th = el.dataset.th.replace(/\d\d:\d\d–\d\d:\d\d/g, hrs); } });

  // mobile nav
  var btn = document.getElementById('menuBtn'), nav = document.getElementById('nav');
  btn.addEventListener('click', function () {
    var open = nav.classList.toggle('open'); btn.setAttribute('aria-expanded', open);
  });
  nav.addEventListener('click', function (e) { if (e.target.tagName === 'A') { nav.classList.remove('open'); btn.setAttribute('aria-expanded', 'false'); } });

  document.getElementById('year').textContent = new Date().getFullYear();
  if (window.SITE_LANG !== 'th') apply(window.SITE_LANG); else window.SITE_LANG = 'th';
})();
// hide the floating mobile bar while the booking form / LINE booking card is on screen (it never covers inputs or buttons)
(function () {
  var bar = document.getElementById('fabBar');
  var targets = [document.getElementById('booker'), document.querySelector('.line-book')].filter(Boolean);
  if (!bar || !targets.length || !('IntersectionObserver' in window)) return;
  var vis = new Map();
  var io = new IntersectionObserver(function (es) {
    es.forEach(function (e) { vis.set(e.target, e.isIntersecting && e.target.offsetParent !== null); });
    var any = false; vis.forEach(function (v) { any = any || v; });
    bar.classList.toggle('away', any && innerWidth < 960);
  }, { threshold: 0.15 });
  targets.forEach(function (t) { io.observe(t); });
})();
// Netlify's "Powered by Netlify" badge (injected by Netlify on free-plan sites, bottom-right) must never cover
// the mobile bar: when it's on the page, lift the bar above it. Turn the badge off in Netlify:
// Project configuration → General → Powered by Netlify badge.
(function () {
  var root = document.documentElement;
  function check() {
    var f = document.getElementById('nl-badge-frame') || document.getElementById('nl-hud-frame');
    root.classList.toggle('has-nl-badge', !!(f && f.isConnected && getComputedStyle(f).display !== 'none'));
  }
  check();
  if ('MutationObserver' in window) new MutationObserver(check).observe(document.body, { childList: true });
})();
// desktop: floating LINE button appears once the visitor scrolls past the hero
(function () {
  var f = function () { document.body.classList.toggle('scrolled', scrollY > 500); };
  addEventListener('scroll', f, { passive: true }); f();
})();
