/* บ้านเราหมูกระทะ — lazy TikTok clips
   - nothing is downloaded until a clip is needed (preload="none", src set on demand)
   - one clip plays at a time: the most visible one autoplays muted; tap to play/pause
   - sound button only on clips that have audio; unmuting one mutes the others
   - Save-Data / reduced-motion visitors: no autoplay, tap to play                     */
(function () {
  var cards = [].slice.call(document.querySelectorAll('.vcard'));
  if (!cards.length) return;
  var conn = navigator.connection || {};
  var autoOK = !conn.saveData && !(window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches);
  var current = null, ratios = new Map();

  function vid(card) { return card.querySelector('video'); }
  function load(v) { if (!v.getAttribute('src') && v.dataset.src) { v.src = v.dataset.src; v.load(); } }
  function play(card, byUser) {
    if (current && current !== card) pause(current);
    var v = vid(card); load(v);
    current = card; card.classList.add('loading');
    var pr = v.play();
    if (pr && pr.then) pr.then(function () { card.classList.add('playing'); card.classList.remove('loading'); })
      .catch(function () { card.classList.remove('loading', 'playing'); if (current === card) current = null; });
    if (byUser) delete card.dataset.userPaused;
  }
  function pause(card, byUser) {
    var v = vid(card); v.pause(); card.classList.remove('playing', 'loading');
    if (byUser) card.dataset.userPaused = '1';
    if (current === card) current = null;
  }
  function pickAuto() {
    if (!autoOK) return;
    if (current && (ratios.get(current) || 0) >= 0.6) return;
    var best = null, bestR = 0;
    cards.forEach(function (c) { var r = ratios.get(c) || 0; if (r >= 0.6 && r > bestR && !c.dataset.userPaused) { best = c; bestR = r; } });
    if (best) play(best); else if (current && (ratios.get(current) || 0) < 0.25) pause(current);
  }

  cards.forEach(function (card) {
    var v = vid(card);
    v.muted = true; v.setAttribute('muted', '');
    card.querySelector('.vplay').addEventListener('click', function () { play(card, true); });
    v.addEventListener('click', function () { if (v.paused) play(card, true); else pause(card, true); });
    v.addEventListener('waiting', function () { card.classList.add('loading'); });
    v.addEventListener('playing', function () { card.classList.remove('loading'); card.classList.add('playing'); });
    var snd = card.querySelector('.vsound');
    if (snd) snd.addEventListener('click', function (e) {
      e.stopPropagation();
      var on = v.muted;                       // currently muted -> turn sound on
      cards.forEach(function (c) { var o = vid(c); if (o !== v) { o.muted = true; var b = c.querySelector('.vsound'); if (b) { b.setAttribute('aria-pressed', 'false'); c.classList.remove('sound-on'); } } });
      v.muted = !on; snd.setAttribute('aria-pressed', String(on)); card.classList.toggle('sound-on', on);
      if (on && v.paused) play(card, true);
    });
  });

  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { var c = e.target.closest('.vcard'); ratios.set(c, e.intersectionRatio); if (e.intersectionRatio < 0.25 && current === c) pause(c); });
      pickAuto();
    }, { threshold: [0, 0.25, 0.6, 0.9] });
    cards.forEach(function (c) { io.observe(c.querySelector('.vwrap')); ratios.set(c, 0); });
  }
  document.addEventListener('visibilitychange', function () { if (document.hidden && current) pause(current); });

  // carousel arrows (desktop)
  var row = document.getElementById('vrow');
  if (row) document.querySelectorAll('.vnav').forEach(function (b) {
    b.addEventListener('click', function () { row.scrollBy({ left: (b.classList.contains('next') ? 1 : -1) * row.clientWidth * 0.8, behavior: 'smooth' }); });
  });
})();
