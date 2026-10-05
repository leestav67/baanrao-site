/* ============================================================
   บ้านเราหมูกระทะ — Site configuration (edit this file only)
   ============================================================ */
window.SITE_CONFIG = {
  // ---- BOOKING BACKEND ----
  // Leave empty "" while there is no backend: the booking section then shows the
  // "จองโต๊ะง่ายๆ ทาง LINE" card (book on LINE / by phone) and the online form is hidden.
  // Paste your Google Apps Script Web App URL here to switch the real online booking form on, e.g.
  // "https://script.google.com/macros/s/AKfycb.../exec"
  BOOKING_API_URL: "",

  // ---- OPENING HOURS ----
  // 17:00–22:00 daily, confirmed by the owner (Oct 2026).
  OPEN_TIME: "17:00",
  CLOSE_TIME: "22:00",
  CLOSED_WEEKDAYS: [],          // 0=Sun ... 6=Sat, e.g. [1] if closed Mondays

  // ---- BOOKING RULES (used by the form; live mode also enforces the values in Code.gs) ----
  SLOT_MINUTES: 30,             // a new time slot every 30 min
  LAST_SEATING_BEFORE_CLOSE: 60,// last booking 60 min before closing -> slots 17:00 … 21:00
  MAX_GUESTS_PER_SLOT: 40,      // capacity per time slot (guests)
  MAX_PARTY_SIZE: 20,           // bigger groups -> contact on LINE
  DAYS_AHEAD: 60,               // how far ahead guests can book

  // ---- LINE (the ONE place for the LINE link: every LINE button on the site reads it) ----
  // Lee (6 Oct 2026): LINE is the same number as the shop phone, 065 615 4656.
  // Click-to-chat URL uses the same R/ti/p/ pattern the site used before (with ~ for a phone ID).
  // Phone stays the primary booking channel; LINE is an extra chat option.
  // While LINE_URL is empty every LINE button is hidden (html.no-line).
  LINE_URL: "https://line.me/R/ti/p/~0656154656",
  LINE_ID: "065 615 4656",

  // ---- PHONE ----
  PHONE: "0656154656",
  PHONE_DISPLAY: "065 615 4656",

  // ---- GOOGLE REVIEWS ----
  // "Read all reviews" opens the shop's Google Maps place.
  GOOGLE_REVIEWS_URL: "https://maps.google.com/?cid=10793292857098184680",
  // Owner: Google Business Profile → "Ask for reviews" → copy the link and paste it here.
  // While empty, the "please review us" link opens the Google Maps place instead.
  GOOGLE_WRITE_REVIEW_URL: ""
};
