/**
 * บ้านเราหมูกระทะ — Booking backend (Google Apps Script + Google Sheets)
 * ------------------------------------------------------------------------
 * Free, no server. Bookings land in a Google Sheet the owner can open in the
 * Google Sheets app on his phone. See README.md → "Switch on online booking".
 *
 * Endpoints (deploy as Web app → "Anyone"):
 *   GET  ?action=availability&date=YYYY-MM-DD        → slots + remaining seats
 *   POST {action:"create", date, time, party, name, phone, email?, note?, lang?}
 *   GET  ?action=list&date=YYYY-MM-DD&pw=...          → owner: bookings for a day
 *   POST {action:"cancel", ref, pw}                  → owner: cancel a booking
 *   POST {action:"block", date, time?, reason?, pw}  → owner: block a night/slot
 *   POST {action:"unblock", date, time?, pw}         → owner: remove a block
 *
 * Sheets (created by running setup() once):
 *   Bookings: Ref | Created | Date | Time | Party | Name | Phone | Email | Note | Status | Lang
 *             → owner cancels by changing Status to "cancelled" (frees the seats)
 *   Blocked:  Date | Time | Reason
 *             → leave Time empty to close the whole night; fill Time (e.g. 19:00) to close one slot
 */

// ======================= SETTINGS (edit these) =======================
var CONFIG = {
  OWNER_EMAIL: 'owner@example.com',      // ← owner's Gmail: gets an email for every booking
  RESTAURANT_NAME: 'บ้านเราหมูกระทะ',
  TIMEZONE: 'Asia/Bangkok',
  OPEN_TIME: '17:00',                    // ← keep in sync with js/config.js (17:00–22:00 daily, confirmed by the owner)
  CLOSE_TIME: '22:00',
  CLOSED_WEEKDAYS: [],                   // 0=Sun … 6=Sat
  SLOT_MINUTES: 30,
  LAST_SEATING_BEFORE_CLOSE: 60,         // minutes before closing
  MAX_GUESTS_PER_SLOT: 40,               // capacity per time slot (guests)
  MAX_PARTY_SIZE: 20,
  DAYS_AHEAD: 60,
  MIN_LEAD_MINUTES: 30,                  // can't book a slot starting in < 30 min
  LINE_ID: '@BaanRaoMookata',
  PHONE_DISPLAY: '093 269 1542',
  MAPS_URL: 'https://goo.gl/maps/uLo6NqVWW7SKCHQf8'
};
// Secrets live in Project Settings → Script properties (never in the website code):
//   OWNER_PASSWORD          password for owner.html (list / cancel / block)
//   LINE_CHANNEL_TOKEN      (optional) LINE Messaging API channel access token
//   LINE_OWNER_USER_ID      (optional) owner's LINE userId (starts with "U…") to receive pushes
// =====================================================================

var BOOKING_HEADERS = ['Ref', 'Created', 'Date', 'Time', 'Party', 'Name', 'Phone', 'Email', 'Note', 'Status', 'Lang'];
var BLOCK_HEADERS = ['Date', 'Time', 'Reason'];

/** Run once from the editor: creates the two sheets with headers and text formatting. */
function setup() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var b = ss.getSheetByName('Bookings') || ss.insertSheet('Bookings');
  b.getRange(1, 1, 1, BOOKING_HEADERS.length).setValues([BOOKING_HEADERS]).setFontWeight('bold').setBackground('#f6d77e');
  b.setFrozenRows(1);
  b.getRange('A:A').setNumberFormat('@'); b.getRange('C:D').setNumberFormat('@'); b.getRange('G:G').setNumberFormat('@');
  var statusRule = SpreadsheetApp.newDataValidation().requireValueInList(['confirmed', 'cancelled', 'arrived', 'no-show'], true).build();
  b.getRange('J2:J').setDataValidation(statusRule);
  var k = ss.getSheetByName('Blocked') || ss.insertSheet('Blocked');
  k.getRange(1, 1, 1, BLOCK_HEADERS.length).setValues([BLOCK_HEADERS]).setFontWeight('bold').setBackground('#f6d77e');
  k.setFrozenRows(1); k.getRange('A:B').setNumberFormat('@');
  var s1 = ss.getSheetByName('Sheet1') || ss.getSheetByName('ชีต1');
  if (s1 && s1.getLastRow() === 0 && ss.getSheets().length > 2) ss.deleteSheet(s1);
  ss.setSpreadsheetTimeZone(CONFIG.TIMEZONE);
}

// ----------------------------- routing -----------------------------
function doGet(e) {
  var p = (e && e.parameter) || {};
  try {
    if (p.action === 'availability') return json(availability(p.date));
    if (p.action === 'list') { requireOwner(p.pw); return json(listDay(p.date)); }
    if (p.action === 'blocks') { requireOwner(p.pw); return json({ ok: true, blocks: readBlocks() }); }
    return json({ ok: true, service: 'baanrao-booking', time: now_().iso });
  } catch (err) { return json({ ok: false, error: err.code || 'ERROR', message: String(err.message || err) }); }
}

function doPost(e) {
  var body = {};
  try { body = JSON.parse(e.postData.contents || '{}'); } catch (x) { return json({ ok: false, error: 'BAD_JSON' }); }
  try {
    switch (body.action) {
      case 'create': return json(createBooking(body));
      case 'cancel': requireOwner(body.pw); return json(cancelBooking(body.ref));
      case 'block': requireOwner(body.pw); return json(addBlock(body.date, body.time, body.reason));
      case 'unblock': requireOwner(body.pw); return json(removeBlock(body.date, body.time));
      default: return json({ ok: false, error: 'UNKNOWN_ACTION' });
    }
  } catch (err) { return json({ ok: false, error: err.code || 'ERROR', message: String(err.message || err) }); }
}

// ----------------------------- core -----------------------------
function availability(date) {
  checkDate(date);
  var blocks = readBlocks().filter(function (b) { return b.date === date; });
  var dayBlocked = blocks.some(function (b) { return !b.time; });
  var used = usedByTime(date);
  var nowB = now_();
  var slots = slotTimes().map(function (t) {
    var blocked = dayBlocked || blocks.some(function (b) { return b.time === t; });
    var past = date === nowB.date && toMin(t) < nowB.minutes + CONFIG.MIN_LEAD_MINUTES;
    var rem = (blocked || past) ? 0 : Math.max(0, CONFIG.MAX_GUESTS_PER_SLOT - (used[t] || 0));
    return { time: t, capacity: CONFIG.MAX_GUESTS_PER_SLOT, remaining: rem, available: rem > 0 };
  });
  return { ok: true, date: date, blocked: dayBlocked, slots: slots };
}

function createBooking(b) {
  var date = String(b.date || ''), time = String(b.time || ''), party = parseInt(b.party, 10);
  var name = clean(b.name, 60), phone = normPhone(b.phone), email = clean(b.email, 80), note = clean(b.note, 300);
  checkDate(date);
  if (slotTimes().indexOf(time) < 0) throw err_('BAD_TIME', 'Invalid time');
  if (!(party >= 1 && party <= CONFIG.MAX_PARTY_SIZE)) throw err_('BAD_PARTY', 'Invalid party size');
  if (name.length < 2) throw err_('BAD_NAME', 'Name required');
  if (!/^0[689]\d{8}$/.test(phone) && !/^0[2-7]\d{7}$/.test(phone)) throw err_('BAD_PHONE', 'Invalid Thai phone number');
  if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) email = '';

  // LockService: only one booking is written at a time → no double-booking / over-capacity.
  var lock = LockService.getScriptLock();
  if (!lock.tryLock(15000)) throw err_('BUSY', 'Please try again');
  var ref;
  try {
    var a = availability(date);
    var slot = a.slots.filter(function (s) { return s.time === time; })[0];
    if (!slot || slot.remaining < party) return { ok: false, error: 'FULL', remaining: slot ? slot.remaining : 0 };
    ref = uniqueRef();
    sheet_('Bookings').appendRow([ref, now_().stamp, date, time, party, name, phone, email, note, 'confirmed', b.lang === 'en' ? 'en' : 'th']);
    SpreadsheetApp.flush();
  } finally { lock.releaseLock(); }

  var booking = { ref: ref, date: date, time: time, party: party, name: name, phone: phone, email: email, note: note };
  notifyOwner(booking);
  if (email) notifyGuest(booking, b.lang === 'en');
  return { ok: true, ref: ref };
}

function cancelBooking(ref) {
  var sh = sheet_('Bookings'), v = sh.getDataRange().getValues();
  for (var i = 1; i < v.length; i++) if (String(v[i][0]) === String(ref)) { sh.getRange(i + 1, 10).setValue('cancelled'); return { ok: true }; }
  return { ok: false, error: 'NOT_FOUND' };
}

function listDay(date) {
  checkDate(date, true);
  var rows = sheet_('Bookings').getDataRange().getValues().slice(1).map(rowToBooking).filter(function (r) { return r.date === date; });
  rows.sort(function (a, b) { return a.time < b.time ? -1 : a.time > b.time ? 1 : 0; });
  var blocks = readBlocks().filter(function (b) { return b.date === date; });
  return { ok: true, date: date, bookings: rows, blocks: blocks, slots: availability(date).slots };
}

function addBlock(date, time, reason) {
  checkDate(date, true);
  if (time && slotTimes().indexOf(time) < 0) throw err_('BAD_TIME', 'Invalid time');
  sheet_('Blocked').appendRow([date, time || '', clean(reason, 100)]);
  return { ok: true };
}
function removeBlock(date, time) {
  var sh = sheet_('Blocked'), v = sh.getDataRange().getValues();
  for (var i = v.length - 1; i >= 1; i--) if (fmtDate(v[i][0]) === date && fmtTime(v[i][1]) === (time || '')) sh.deleteRow(i + 1);
  return { ok: true };
}

// ----------------------------- notifications -----------------------------
function notifyOwner(b) {
  var lines = [
    '🔥 จองโต๊ะใหม่ / New booking — ' + CONFIG.RESTAURANT_NAME,
    'รหัส (Ref): ' + b.ref,
    'วันที่: ' + b.date + '  เวลา: ' + b.time,
    'จำนวน: ' + b.party + ' ท่าน',
    'ชื่อ: ' + b.name,
    'โทร: ' + b.phone,
    b.note ? 'หมายเหตุ: ' + b.note : ''
  ].filter(String);
  var text = lines.join('\n');
  try {
    if (CONFIG.OWNER_EMAIL && CONFIG.OWNER_EMAIL.indexOf('example.com') < 0) {
      MailApp.sendEmail({ to: CONFIG.OWNER_EMAIL, subject: 'จองโต๊ะใหม่ ' + b.date + ' ' + b.time + ' · ' + b.party + ' ท่าน · ' + b.name, body: text + '\n\nเปิดชีต: ' + SpreadsheetApp.getActiveSpreadsheet().getUrl() });
    }
  } catch (e) { console.error('Owner email failed', e); }
  try { linePush(text); } catch (e) { console.error('LINE push failed', e); }
}

function notifyGuest(b, en) {
  try {
    var subject = en ? 'Booking confirmed — Baan Rao Moo Krata (' + b.ref + ')' : 'ยืนยันการจองโต๊ะ — บ้านเราหมูกระทะ (' + b.ref + ')';
    var body = en
      ? 'Hi ' + b.name + ',\n\nYour table is booked!\nRef: ' + b.ref + '\nDate: ' + b.date + '\nTime: ' + b.time + '\nGuests: ' + b.party + '\n\nNeed to change or cancel? Message us on LINE ' + CONFIG.LINE_ID + ' or call ' + CONFIG.PHONE_DISPLAY + '.\nDirections: ' + CONFIG.MAPS_URL + '\n\nSee you soon!\nBaan Rao Moo Krata'
      : 'สวัสดีคุณ ' + b.name + '\n\nจองโต๊ะสำเร็จแล้ว!\nรหัสการจอง: ' + b.ref + '\nวันที่: ' + b.date + '\nเวลา: ' + b.time + '\nจำนวน: ' + b.party + ' ท่าน\n\nต้องการเปลี่ยนแปลงหรือยกเลิก แจ้งทาง LINE ' + CONFIG.LINE_ID + ' หรือโทร ' + CONFIG.PHONE_DISPLAY + '\nนำทาง: ' + CONFIG.MAPS_URL + '\n\nแล้วพบกันที่บ้านเรา 🙏\nบ้านเราหมูกระทะ';
    MailApp.sendEmail({ to: b.email, subject: subject, body: body, name: CONFIG.RESTAURANT_NAME, replyTo: CONFIG.OWNER_EMAIL.indexOf('example.com') < 0 ? CONFIG.OWNER_EMAIL : undefined });
  } catch (e) { console.error('Guest email failed', e); }
}

/** Optional: LINE Messaging API push (LINE Notify was shut down in 2025 — this is its replacement). */
function linePush(text) {
  var props = PropertiesService.getScriptProperties();
  var token = props.getProperty('LINE_CHANNEL_TOKEN'), to = props.getProperty('LINE_OWNER_USER_ID');
  if (!token || !to) return;
  UrlFetchApp.fetch('https://api.line.me/v2/bot/message/push', {
    method: 'post', contentType: 'application/json', headers: { Authorization: 'Bearer ' + token },
    payload: JSON.stringify({ to: to, messages: [{ type: 'text', text: text.slice(0, 4900) }] }), muteHttpExceptions: true
  });
}

/** Run from the editor to test notifications without making a real booking. */
function testNotify() { notifyOwner({ ref: 'BR-TEST1', date: now_().date, time: '19:00', party: 4, name: 'ทดสอบ', phone: '0812345678', note: 'test' }); }

// ----------------------------- helpers -----------------------------
function slotTimes() {
  var open = toMin(CONFIG.OPEN_TIME), close = toMin(CONFIG.CLOSE_TIME); if (close <= open) close += 1440;
  var last = close - CONFIG.LAST_SEATING_BEFORE_CLOSE, out = [];
  for (var m = open; m <= last; m += CONFIG.SLOT_MINUTES) out.push(toHHMM(m % 1440));
  return out;
}
function usedByTime(date) {
  var used = {};
  sheet_('Bookings').getDataRange().getValues().slice(1).forEach(function (r) {
    var b = rowToBooking(r);
    if (b.date === date && b.status !== 'cancelled' && b.status !== 'no-show') used[b.time] = (used[b.time] || 0) + b.party;
  });
  return used;
}
function rowToBooking(r) {
  return { ref: String(r[0]), created: String(r[1]), date: fmtDate(r[2]), time: fmtTime(r[3]), party: Number(r[4]) || 0, name: String(r[5]),
           phone: String(r[6]), email: String(r[7]), note: String(r[8]), status: String(r[9] || 'confirmed').toLowerCase().trim(), lang: String(r[10]) };
}
function readBlocks() {
  return sheet_('Blocked').getDataRange().getValues().slice(1).filter(function (r) { return r[0]; })
    .map(function (r) { return { date: fmtDate(r[0]), time: fmtTime(r[1]), reason: String(r[2] || '') }; });
}
function checkDate(date, ownerMode) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(date || '')) throw err_('BAD_DATE', 'Invalid date');
  if (ownerMode) return;
  var today = now_().date, max = addDays(today, CONFIG.DAYS_AHEAD);
  if (date < today || date > max) throw err_('BAD_DATE', 'Date out of range');
  var wd = new Date(date + 'T12:00:00Z').getUTCDay();
  if (CONFIG.CLOSED_WEEKDAYS.indexOf(wd) > -1) throw err_('CLOSED', 'Closed on this day');
}
function requireOwner(pw) {
  var real = PropertiesService.getScriptProperties().getProperty('OWNER_PASSWORD');
  if (!real || String(pw || '') !== real) { Utilities.sleep(800); throw err_('UNAUTHORIZED', 'Wrong password'); }
}
function uniqueRef() {
  var c = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789', existing = {};
  sheet_('Bookings').getRange('A:A').getValues().forEach(function (r) { existing[r[0]] = 1; });
  for (var n = 0; n < 50; n++) { var s = 'BR-'; for (var i = 0; i < 5; i++) s += c.charAt(Math.floor(Math.random() * c.length)); if (!existing[s]) return s; }
  throw err_('REF', 'Could not create reference');
}
function now_() {
  var d = new Date();
  return { date: Utilities.formatDate(d, CONFIG.TIMEZONE, 'yyyy-MM-dd'), minutes: +Utilities.formatDate(d, CONFIG.TIMEZONE, 'H') * 60 + +Utilities.formatDate(d, CONFIG.TIMEZONE, 'm'),
           stamp: Utilities.formatDate(d, CONFIG.TIMEZONE, 'yyyy-MM-dd HH:mm'), iso: d.toISOString() };
}
function addDays(iso, n) { var d = new Date(iso + 'T12:00:00Z'); d.setUTCDate(d.getUTCDate() + n); return Utilities.formatDate(d, 'UTC', 'yyyy-MM-dd'); }
function fmtDate(v) { return v instanceof Date ? Utilities.formatDate(v, CONFIG.TIMEZONE, 'yyyy-MM-dd') : String(v || '').trim(); }
function fmtTime(v) { if (v instanceof Date) return Utilities.formatDate(v, CONFIG.TIMEZONE, 'HH:mm'); var s = String(v || '').trim(); return /^\d:\d\d$/.test(s) ? '0' + s : s; }
function toMin(t) { var a = String(t).split(':'); return +a[0] * 60 + +a[1]; }
function toHHMM(m) { return ('0' + Math.floor(m / 60)).slice(-2) + ':' + ('0' + (m % 60)).slice(-2); }
function normPhone(v) { var d = String(v || '').replace(/[^\d+]/g, ''); if (d.indexOf('+66') === 0) d = '0' + d.slice(3); else if (/^66\d{8,9}$/.test(d)) d = '0' + d.slice(2); return d; }
function clean(v, max) { return String(v || '').replace(/[\u0000-\u001f]/g, ' ').replace(/^[=+\-@]+/, '').trim().slice(0, max); } // strip formula-injection prefixes
function sheet_(n) { var s = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(n); if (!s) throw err_('SETUP', 'Run setup() first'); return s; }
function err_(code, msg) { var e = new Error(msg); e.code = code; return e; }
function json(o) { return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON); }
