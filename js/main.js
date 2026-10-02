/* บ้านเราหมูกระทะ — language toggle, nav, hours */
(function () {
  var C = window.SITE_CONFIG || {};
  var KEY = 'brm_lang';
  var titles = {
    th: document.title,
    en: 'Baan Rao Moo Krata, Udon Thani | Moo krata that feels like home · Book online'
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
// hide the floating mobile bar while the booking form is on screen (so it never covers inputs)
(function () {
  var bar = document.getElementById('fabBar'), bk = document.getElementById('booker');
  if (!bar || !bk || !('IntersectionObserver' in window)) return;
  new IntersectionObserver(function (es) { es.forEach(function (e) { bar.classList.toggle('away', e.isIntersecting && innerWidth < 960); }); }, { threshold: 0.15 }).observe(bk);
})();
// desktop: floating LINE button appears once the visitor scrolls past the hero
(function () {
  var f = function () { document.body.classList.toggle('scrolled', scrollY > 500); };
  addEventListener('scroll', f, { passive: true }); f();
})();
