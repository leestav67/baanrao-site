/* ============================================================
   บ้านเราหมูกระทะ — Site configuration (edit this file only)
   ============================================================ */
window.SITE_CONFIG = {
  // ---- BOOKING BACKEND ----
  // Leave empty "" to run in DEMO MODE (bookings stored only in this browser).
  // Paste your Google Apps Script Web App URL here to go LIVE, e.g.
  // "https://script.google.com/macros/s/AKfycb.../exec"
  BOOKING_API_URL: "",

  // ---- OPENING HOURS ----
  // 17:00–22:00 daily, confirmed by the owner (Oct 2026).
  OPEN_TIME: "17:00",
  CLOSE_TIME: "22:00",
  CLOSED_WEEKDAYS: [],          // 0=Sun ... 6=Sat, e.g. [1] if closed Mondays

  // ---- BOOKING RULES (demo mode uses these; live mode uses the values in Code.gs) ----
  SLOT_MINUTES: 30,             // a new time slot every 30 min
  LAST_SEATING_BEFORE_CLOSE: 60,// last booking 60 min before closing -> slots 17:00 … 21:00
  MAX_GUESTS_PER_SLOT: 40,      // capacity per time slot (guests)
  MAX_PARTY_SIZE: 20,           // bigger groups -> contact on LINE
  DAYS_AHEAD: 60,               // how far ahead guests can book

  // ---- CONTACT ----
  LINE_URL: "https://line.me/R/ti/p/@BaanRaoMookata",
  LINE_ID: "@BaanRaoMookata",
  PHONE: "+66932691542",
  PHONE_DISPLAY: "093 269 1542"
};
