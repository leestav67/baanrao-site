/* บ้านเราหมูกระทะ — booking widget
   LIVE MODE (SITE_CONFIG.BOOKING_API_URL set): talks to the Google Apps Script web app in backend/Code.gs.
   No URL: the form stays hidden and the page shows the "book on LINE / phone" card instead.
   TEST MODE (no URL + ?booking=test in the address): the form runs against this browser's localStorage only,
   clearly labelled "not sent to the restaurant" — for previewing the form. No fake "full" slots, ever.   */
(function () {
  var C = window.SITE_CONFIG || {};
  var API = (C.BOOKING_API_URL || '').trim();
  var DEMO = !API;
  var TEST = DEMO && /[?&]booking=test\b/.test(location.search);
  if (DEMO && !TEST) { window.BRM = { demo: true, off: true }; return; }   // LINE card is shown instead
  var TZ = 'Asia/Bangkok';
  var $ = function (id) { return document.getElementById(id); };
  var T = {
    th: { months: ['มกราคม','กุมภาพันธ์','มีนาคม','เมษายน','พฤษภาคม','มิถุนายน','กรกฎาคม','สิงหาคม','กันยายน','ตุลาคม','พฤศจิกายน','ธันวาคม'],
          dow: ['อา','จ','อ','พ','พฤ','ศ','ส'], left: 'ว่าง {n} ที่', few: 'เหลือ {n} ที่', full: 'เต็ม', loading: 'กำลังโหลดเวลาว่าง…',
          none: 'ขออภัย วันนี้ไม่มีรอบว่างแล้ว กรุณาเลือกวันอื่น หรือแชท LINE', closed: 'วันนี้ร้านปิดรับจอง กรุณาเลือกวันอื่น',
          guests: 'ท่าน', maxHint: 'รอบนี้รับได้อีกสูงสุด {n} ท่าน', date: 'วันที่', time: 'เวลา', party: 'จำนวน', name: 'ชื่อ', phone: 'โทร',
          err: 'เกิดข้อผิดพลาด กรุณาลองใหม่ หรือแชท LINE', fullErr: 'ขออภัย รอบนี้เพิ่งเต็ม กรุณาเลือกเวลาอื่น', sending: 'กำลังจอง…', yearOff: 543,
          testTitle: 'โหมดทดสอบ — ยังไม่ได้จองจริง', testText: 'การจองนี้ไม่ได้ส่งถึงร้าน กรุณาจองทาง LINE หรือโทร 065 615 4656' },
    en: { months: ['January','February','March','April','May','June','July','August','September','October','November','December'],
          dow: ['Su','Mo','Tu','We','Th','Fr','Sa'], left: '{n} seats', few: '{n} left', full: 'Full', loading: 'Loading available times…',
          none: 'Sorry, no times left on this day. Please pick another date or chat with us on LINE.', closed: 'We are not taking bookings on this day.',
          guests: 'guests', maxHint: 'Up to {n} guests available at this time', date: 'Date', time: 'Time', party: 'Guests', name: 'Name', phone: 'Phone',
          err: 'Something went wrong. Please try again or chat with us on LINE.', fullErr: 'Sorry, that time just filled up. Please choose another time.', sending: 'Booking…', yearOff: 0,
          testTitle: 'Test mode — not a real booking', testText: 'This booking was NOT sent to the restaurant. Please book on LINE or call 065 615 4656.' }
  };
  var L = function () { return T[window.SITE_LANG === 'en' ? 'en' : 'th']; };
  var fmt = function (s, n) { return s.replace('{n}', n); };

  // ---------- date helpers (restaurant time = Bangkok) ----------
  function bkkNow() {
    var p = new Intl.DateTimeFormat('en-CA', { timeZone: TZ, year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', hour12: false }).formatToParts(new Date());
    var o = {}; p.forEach(function (x) { o[x.type] = x.value; });
    return { date: o.year + '-' + o.month + '-' + o.day, minutes: (+o.hour % 24) * 60 + (+o.minute) };
  }
  function iso(d) { return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0'); }
  function parse(s) { var a = s.split('-'); return new Date(+a[0], +a[1] - 1, +a[2]); }
  function toMin(t) { var a = t.split(':'); return +a[0] * 60 + +a[1]; }
  function toHHMM(m) { return String(Math.floor(m / 60)).padStart(2, '0') + ':' + String(m % 60).padStart(2, '0'); }
  function niceDate(s) {
    var d = parse(s), lang = window.SITE_LANG === 'en' ? 'en-GB' : 'th-TH';
    return d.toLocaleDateString(lang, { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });
  }
  function slotTimes() {
    var open = toMin(C.OPEN_TIME || '17:00'), close = toMin(C.CLOSE_TIME || '22:00');
    if (close <= open) close += 1440;
    var last = close - (C.LAST_SEATING_BEFORE_CLOSE || 60), out = [];
    for (var m = open; m <= last; m += (C.SLOT_MINUTES || 30)) out.push(toHHMM(m % 1440));
    return out;
  }

  // ---------- DEMO backend (localStorage) ----------
  var DKEY = 'brm_demo_bookings';
  function demoAll() { try { return JSON.parse(localStorage.getItem(DKEY) || '[]'); } catch (e) { return []; } }
  function hash(s) { var h = 2166136261; for (var i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); } return h >>> 0; }
  var demo = {
    availability: function (date) {
      var cap = C.MAX_GUESTS_PER_SLOT || 40, all = demoAll().filter(function (b) { return b.date === date && b.status !== 'cancelled'; });
      var blocked = JSON.parse(localStorage.getItem('brm_demo_blocked') || '[]');
      var dayBlocked = blocked.some(function (b) { return b.date === date && !b.time; });
      return Promise.resolve({ ok: true, date: date, blocked: dayBlocked, slots: slotTimes().map(function (t) {
        var used = all.filter(function (b) { return b.time === t; }).reduce(function (s, b) { return s + b.party; }, 0);
        var isBlocked = dayBlocked || blocked.some(function (b) { return b.date === date && b.time === t; });
        var rem = isBlocked ? 0 : Math.max(0, cap - used);
        return { time: t, capacity: cap, remaining: rem, available: rem > 0 };
      }) });
    },
    create: function (b) {
      return demo.availability(b.date).then(function (a) {
        var s = a.slots.filter(function (x) { return x.time === b.time; })[0];
        if (!s || s.remaining < b.party) return { ok: false, error: 'FULL' };
        var ref = makeRef(), all = demoAll();
        all.push(Object.assign({ ref: ref, status: 'confirmed', created: new Date().toISOString() }, b));
        localStorage.setItem(DKEY, JSON.stringify(all));
        return new Promise(function (r) { setTimeout(function () { r({ ok: true, ref: ref }); }, 600); });
      });
    }
  };
  function makeRef() { var c = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789', s = ''; for (var i = 0; i < 5; i++) s += c[Math.floor(Math.random() * c.length)]; return 'BR-' + s; }

  // ---------- LIVE backend (Google Apps Script) ----------
  var live = {
    availability: function (date) {
      return fetch(API + '?action=availability&date=' + encodeURIComponent(date)).then(function (r) { return r.json(); });
    },
    create: function (b) {
      return fetch(API, { method: 'POST', headers: { 'Content-Type': 'text/plain;charset=utf-8' }, body: JSON.stringify(Object.assign({ action: 'create' }, b)) })
        .then(function (r) { return r.json(); });
    }
  };
  var api = DEMO ? demo : live;

  // ---------- UI state ----------
  var st = { step: 1, date: null, time: null, remaining: 0, party: 2, view: null };
  var today = bkkNow();
  var minD = parse(today.date), maxD = parse(today.date); maxD.setDate(maxD.getDate() + (C.DAYS_AHEAD || 60));
  st.view = new Date(minD.getFullYear(), minD.getMonth(), 1);
  if (DEMO) $('demoFlag').hidden = false;

  function go(n) {
    st.step = n;
    document.querySelectorAll('.step-pane').forEach(function (p) { p.hidden = +p.dataset.pane !== n; });
    document.querySelectorAll('.steps li').forEach(function (li) {
      var s = +li.dataset.step; li.classList.toggle('active', s === n); li.classList.toggle('done', s < n);
    });
    if (n === 2) loadSlots();
    if (n === 3) renderParty();
  }

  function renderCal() {
    var l = L(), y = st.view.getFullYear(), m = st.view.getMonth();
    $('calTitle').textContent = l.months[m] + ' ' + (y + l.yearOff);
    $('calDow').innerHTML = l.dow.map(function (d) { return '<span>' + d + '</span>'; }).join('');
    var first = new Date(y, m, 1).getDay(), days = new Date(y, m + 1, 0).getDate(), html = '';
    for (var i = 0; i < first; i++) html += '<span></span>';
    var closed = C.CLOSED_WEEKDAYS || [];
    for (var d = 1; d <= days; d++) {
      var dt = new Date(y, m, d), s = iso(dt);
      var dis = dt < minD || dt > maxD || closed.indexOf(dt.getDay()) > -1;
      html += '<button type="button" data-date="' + s + '"' + (dis ? ' disabled' : '') + ' class="' + (s === today.date ? 'today ' : '') + (s === st.date ? 'sel' : '') + '">' + d + '</button>';
    }
    $('calGrid').innerHTML = html;
    $('calPrev').disabled = y === minD.getFullYear() && m === minD.getMonth();
    $('calNext').disabled = new Date(y, m + 1, 1) > maxD;
  }
  $('calGrid').addEventListener('click', function (e) {
    var b = e.target.closest('button[data-date]'); if (!b || b.disabled) return;
    st.date = b.dataset.date; st.time = null; renderCal(); go(2);
  });
  $('calPrev').onclick = function () { st.view.setMonth(st.view.getMonth() - 1); renderCal(); };
  $('calNext').onclick = function () { st.view.setMonth(st.view.getMonth() + 1); renderCal(); };

  var lastSlots = null;
  function loadSlots() {
    $('chosenDateLabel').textContent = niceDate(st.date);
    $('slots').innerHTML = '<div class="loading">' + L().loading + '</div>';
    api.availability(st.date).then(function (a) { lastSlots = a; renderSlots(); })
      .catch(function () { $('slots').innerHTML = '<div class="loading">' + L().err + '</div>'; });
  }
  function renderSlots() {
    var a = lastSlots, l = L(); if (!a) return;
    if (a.blocked) { $('slots').innerHTML = '<div class="loading">' + l.closed + '</div>'; return; }
    var now = bkkNow(), html = '', any = false;
    a.slots.forEach(function (s) {
      var past = st.date === now.date && toMin(s.time) <= now.minutes + 30;
      var rem = past ? 0 : s.remaining, cls = rem <= 0 ? 'full' : (rem <= 10 ? 'low' : '');
      if (rem > 0) any = true;
      html += '<button type="button" class="slot ' + cls + (s.time === st.time ? ' sel' : '') + '" data-time="' + s.time + '" data-rem="' + rem + '"' + (rem <= 0 ? ' disabled' : '') + '><strong>' + s.time + '</strong><small>' +
        (rem <= 0 ? l.full : fmt(rem <= 10 ? l.few : l.left, rem)) + '</small></button>';
    });
    $('slots').innerHTML = any ? html : '<div class="loading">' + l.none + '</div>' + html;
  }
  $('slots').addEventListener('click', function (e) {
    var b = e.target.closest('button[data-time]'); if (!b || b.disabled) return;
    st.time = b.dataset.time; st.remaining = +b.dataset.rem; go(3);
  });

  function maxParty() { return Math.max(1, Math.min(C.MAX_PARTY_SIZE || 20, st.remaining || 1)); }
  function renderParty() {
    var l = L(), mx = maxParty();
    if (st.party > mx) st.party = mx;
    $('chosenSummary').textContent = niceDate(st.date) + ' · ' + st.time;
    $('partyOut').textContent = st.party;
    $('partyMinus').disabled = st.party <= 1; $('partyPlus').disabled = st.party >= mx;
    $('partyQuick').innerHTML = [2, 4, 6, 8, 10, 15].filter(function (n) { return n <= mx; }).map(function (n) {
      return '<button type="button" data-n="' + n + '" class="' + (n === st.party ? 'sel' : '') + '">' + n + ' ' + l.guests + '</button>';
    }).join('');
    $('partyHint').textContent = fmt(l.maxHint, mx);
  }
  $('partyMinus').onclick = function () { st.party = Math.max(1, st.party - 1); renderParty(); };
  $('partyPlus').onclick = function () { st.party = Math.min(maxParty(), st.party + 1); renderParty(); };
  $('partyQuick').addEventListener('click', function (e) { var b = e.target.closest('button[data-n]'); if (b) { st.party = +b.dataset.n; renderParty(); } });
  document.querySelectorAll('[data-back]').forEach(function (b) { b.onclick = function () { go(+b.dataset.back); }; });

  function normPhone(v) {
    var d = (v || '').replace(/[^\d+]/g, '');
    if (d.indexOf('+66') === 0) d = '0' + d.slice(3); else if (/^66\d{8,9}$/.test(d)) d = '0' + d.slice(2);
    return d;
  }
  function validPhone(d) { return /^0[689]\d{8}$/.test(d) || /^0[2-7]\d{7}$/.test(d); }
  function setInvalid(id, bad) { $(id).closest('.field').classList.toggle('invalid', bad); return bad; }

  $('bookForm').addEventListener('submit', function (e) {
    e.preventDefault();
    var name = $('fName').value.trim(), phone = normPhone($('fPhone').value), email = $('fEmail').value.trim(), note = $('fNote').value.trim();
    var bad = setInvalid('fName', name.length < 2);
    bad = setInvalid('fPhone', !validPhone(phone)) || bad;
    bad = setInvalid('fEmail', email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) || bad;
    if (bad) return;
    var btn = $('submitBtn'), label = btn.innerHTML; btn.disabled = true; btn.textContent = L().sending; $('formError').hidden = true;
    var payload = { date: st.date, time: st.time, party: st.party, name: name, phone: phone, email: email, note: note, lang: window.SITE_LANG };
    api.create(payload).then(function (r) {
      btn.disabled = false; btn.innerHTML = label;
      if (r && r.ok) { showConfirm(r.ref, payload); return; }
      var msg = r && r.error === 'FULL' ? L().fullErr : (r && r.message) || L().err;
      $('formError').textContent = msg; $('formError').hidden = false;
    }).catch(function () { btn.disabled = false; btn.innerHTML = label; $('formError').textContent = L().err; $('formError').hidden = false; });
  });

  var lastConf = null;
  function showConfirm(ref, p) {
    lastConf = { ref: ref, p: p }; renderConfirm(); go(4);
    $('booker').scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
  function renderConfirm() {
    if (!lastConf) return; var l = L(), p = lastConf.p;
    $('confRef').textContent = lastConf.ref;
    if (DEMO) { $('confTitle').textContent = l.testTitle; $('confText').textContent = l.testText; $('confRef').textContent = 'TEST'; var ic = document.querySelector('.confirm-ico'); if (ic) { ic.textContent = '!'; ic.style.background = 'var(--gold-d)'; } }
    var ph = p.phone.length === 10 ? p.phone.replace(/(\d{3})(\d{3})(\d{4})/, '$1-$2-$3') : p.phone;
    $('confList').innerHTML = '<dt>' + l.date + '</dt><dd>' + niceDate(p.date) + '</dd><dt>' + l.time + '</dt><dd>' + p.time + '</dd><dt>' + l.party + '</dt><dd>' + p.party + ' ' + l.guests + '</dd><dt>' + l.name + '</dt><dd>' + esc(p.name) + '</dd><dt>' + l.phone + '</dt><dd>' + ph + '</dd>';
  }
  function esc(s) { return s.replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  $('newBooking').onclick = function () { st.date = null; st.time = null; lastConf = null; $('bookForm').reset(); renderCal(); go(1); };

  document.addEventListener('langchange', function () {
    renderCal();
    if (st.step === 2) { $('chosenDateLabel').textContent = niceDate(st.date); renderSlots(); }
    if (st.step === 3) renderParty();
    if (st.step === 4) renderConfirm();
  });
  renderCal();
  // expose for owner page / testing
  window.BRM = { api: api, demo: DEMO, slotTimes: slotTimes, today: today.date };
})();
