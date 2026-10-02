# บ้านเราหมูกระทะ · Baan Rao Moo Krata — website

Static, mobile-first restaurant site (HTML + CSS + vanilla JS) with a real online
booking system (Google Sheets + Google Apps Script). Thai is the page at `/`. English is a real page at `/en/`, generated at build time from the Thai page.

```
index.html          the website (all sections)
owner.html          owner's phone page: see bookings, cancel, block nights/slots (password protected)
js/config.js        ← THE ONLY FILE YOU NORMALLY EDIT (booking URL, opening hours, capacity)
js/main.js          language toggle, menu, floating buttons
js/booking.js       booking widget (demo mode + live mode)
js/videos.js        lazy TikTok clips (load on demand, one plays at a time, sound toggle)
videos/             8 web-ready TikTok clips (H.264 MP4) + posters/
css/                styles + self-hosted Thai fonts (Kanit, Noto Sans Thai)
images/             optimised photos, logo, favicon, social share image
backend/Code.gs     Google Apps Script booking backend (paste into Google Sheets)
```

---

## 1. Preview on your computer

```bash
cd baanrao-site    # the unzipped folder that contains index.html
python3 -m http.server 8000
```
Open <http://localhost:8000>. English page: build it first with `python3 tools/build_en.py .`, then open <http://localhost:8000/en/>. Owner page: <http://localhost:8000/owner.html>
(demo password: `demo`).

Until a booking URL is set, the booking form runs in **DEMO MODE**: it works end to end, but bookings
are only stored in that browser (a yellow "โหมดสาธิต" notice is shown). Nothing is sent anywhere.

## 2. Put it online for free (pick one)

### Netlify, the easiest option (one drag and drop)

1. Sign up for free at <https://www.netlify.com> (email, Google or GitHub).
2. Open <https://app.netlify.com/drop>, or go to **Sites** on your Netlify dashboard and find the drag-and-drop box.
3. Drag the site folder onto it. That's the folder with `index.html` directly inside, i.e. the inner
   `baanrao-site` folder if you unzipped the zip. Don't drag the zip itself, or the folder above it.
4. Done. Netlify gives you a live address like `random-name.netlify.app`. Rename it under
   **Site configuration → Change site name**, e.g. `baanraomookata.netlify.app`.

The folder already has Netlify's settings, so there's nothing to configure:
- `netlify.toml`: publishes this folder and runs `python3 tools/build_en.py .` to generate `/en/`.
- `_headers`: sensible caching (pages always fresh, images and videos cached for a week, fonts for a year) plus basic security headers.
- `_redirects`: hides the `backend/` folder and this README from the public site.

To update the site later, drag the updated folder onto **Deploys** for the same site. Netlify keeps old versions, so you can roll back with one click.

### Other free hosts

- **Cloudflare Pages** — Workers & Pages → Create → Pages → *Upload assets* → upload the `baanrao-site` folder.
- **GitHub Pages** — push the folder to a repo → Settings → Pages → deploy from branch `main` / root.

Then connect a domain if you buy one (e.g. baanraomookata.com). Change the one line in
`tools/site-base-url.txt` and run `python3 tools/build_en.py .` so the canonical, share image,
sitemap and English page all use the new address.

## 3. Switch on online booking (about 15 minutes, free)

1. Sign in to the restaurant's Google account. Create a new Google Sheet named **"Baan Rao Bookings"**.
2. In the Sheet: **Extensions → Apps Script**. Delete the sample code and paste all of `backend/Code.gs`.
3. At the top of the code, edit `CONFIG`:
   - `OWNER_EMAIL` → the owner's Gmail (gets an email for every booking).
   - `OPEN_TIME` / `CLOSE_TIME`, `MAX_GUESTS_PER_SLOT` (seats per 30-min slot), `MAX_PARTY_SIZE`, `CLOSED_WEEKDAYS`.
     Keep these the same as in `js/config.js`.
4. **Project Settings (⚙) → Script properties → Add**: `OWNER_PASSWORD` = a password for owner.html.
5. Back in the editor choose the function **`setup`** → **Run** → allow the permissions (Google warns
   "unverified app" because it's your own script: *Advanced → Go to project*). This creates the
   **Bookings** and **Blocked** tabs.
6. Optional: run **`testNotify`** to check the owner email (and LINE) arrive.
7. **Deploy → New deployment → type: Web app**. *Execute as*: **Me**. *Who has access*: **Anyone**. Deploy and copy the URL
   (`https://script.google.com/macros/s/…/exec`).
8. Paste that URL into `js/config.js`:
   ```js
   BOOKING_API_URL: "https://script.google.com/macros/s/XXXX/exec",
   ```
   Re-upload the site. The demo notice disappears and bookings now go to the Sheet.
9. If you change `Code.gs` later: **Deploy → Manage deployments → Edit → Version: New version** (the URL stays the same).

**How it prevents double-booking:** every booking request takes a `LockService` script lock, re-checks the
remaining seats for that slot, and only then writes the row. Full slots show as "เต็ม" (Full) and can't be picked.

## 4. How the owner gets notified and manages bookings on his phone

- **Instant notification — email:** every booking emails `OWNER_EMAIL` (subject e.g. "จองโต๊ะใหม่ 2026-10-03 19:00 · 6 ท่าน · คุณสมชาย").
  With the Gmail app installed, this pops up as a phone notification.
- **Optional — LINE message to the owner** (LINE Notify was shut down in 2025; this uses the LINE Messaging API instead):
  1. In the restaurant's **LINE Official Account** (LINE OA Manager) → Settings → Messaging API → *Enable*; this creates a channel in the LINE Developers console.
  2. In <https://developers.line.biz> → that channel → *Messaging API* tab → issue a **Channel access token (long-lived)**.
  3. The owner adds the OA as a friend. His **userId** (starts with `U…`) is shown on the channel's *Basic settings* tab as "Your user ID" (if he is the channel admin).
  4. Add Script properties `LINE_CHANNEL_TOKEN` and `LINE_OWNER_USER_ID`. Every booking is now pushed to his LINE.
     (Push messages count against the free OA message quota.)
- **Guest confirmation:** instant on screen with a booking reference (e.g. `BR-82PNY`), plus an email if the guest enters one.
  SMS confirmations are possible as a paid add-on (e.g. Twilio or a Thai SMS gateway such as ThaiBulkSMS) — not included.
- **See bookings:** open the **Google Sheets app** → "Baan Rao Bookings" → **Bookings** tab (sort/filter by date), or open
  **`yoursite/owner.html`** on the phone (add to home screen): pick a day, see guests and phone numbers, tap to call.
- **Cancel:** in owner.html tap **ยกเลิก**, or in the Sheet change **Status** to `cancelled` (the seats free up immediately).
  Other statuses: `arrived`, `no-show`.
- **Close a night or a slot** (private party, holiday, full by walk-ins): owner.html → *ปิดรับจอง*, or add a row to the
  **Blocked** tab — `Date` = 2026-10-31, leave `Time` empty for the whole night, or `Time` = 19:00 for one slot.

## 5. Everyday edits

- Opening hours / capacity: `js/config.js` (and the same values in `Code.gs` CONFIG). Also update the hours in the JSON-LD
  block at the top of `index.html` for Google.
- Texts: in `index.html` — Thai text is the element content, English is in the `data-en="…"` attribute next to it.
- Photos: replace files in `images/` with the same names (keep them under ~200 KB).
- Videos: clips live in `videos/` (posters in `videos/posters/`). Each card in `index.html` has `data-src` (the clip),
  `poster` and a TikTok link. Nothing downloads until a clip is visible or tapped; only one plays at a time, muted.
  Clips 01, 03, 04, 05, 07 have a sound button; 02, 06, 08 have no audio (commercial music removed).
  If the site is ever hosted somewhere with tight bandwidth, the videos can be swapped for TikTok links only.

## 6. Details the owner must confirm before going live

**Confirmed by the owner:**
- **Opening hours**: 17:00–22:00 every day. Booking slots run 17:00–21:00 (last seating 1 h before close).

**Double-check (taken from the shop's own recent signage / videos):**
1. **Address** — shown as *168 ซอยอุดมทรัพย์ หมู่ 7 บ้านเก่าน้อย ต.บ้านเลื่อม อ.เมืองอุดรธานี 41000*. Is the map pin (17.440569, 102.794069) on the entrance?
2. **Directions & landmarks** — Rangsina underpass → หมวดทางหลวงเก่าน้อย → keep left into ซอยอุดมทรัพย์ → ~150 m, turn left → shop on the right; roadside sign “หมูกระทะเตาถ่าน 100 ม.”; opposite Wang Badan.

**Please confirm:**
3. **Set prices** — ชุดเล็ก ฿199 / ชุดใหญ่ ฿299 (Dec 2025 banner). **Add-ons** — เพิ่มหมูหมัก ฿100, เพิ่มหมูสามชั้น ฿100: correct?
4. **“5 แถม เนื้อออส 1” promo** — exact terms (5 sets? which days?) and is it still running?
5. **60/40 co-payment scheme via G-Wallet / เป๋าตัง** (posted 1 July 2026) — still running? The shop sign calls it “ไทยช่วยไทย พลัส 60/40”; the site says “คนละครึ่งพลัส 60/40” — which name is right?
6. **Permission to use the TikTok videos** on the website (8 clips from @boom_berler).
7. **LINE ID** — `@BaanRaoMookata` (button: https://line.me/R/ti/p/@BaanRaoMookata). Please test it opens the right account.
8. **Parking** — site says "parking for cars and motorbikes at the restaurant". How many cars?
9. **Menu** — category cards (meats, seafood, salads, noodles/sides, veg, drinks) are examples; send a fuller menu to add.
10. **Live music** — which nights? **GrabFood** — direct link to add? **Rao Cafe** — address/link?
11. **Booking capacity** — guests per 30-minute slot (default 40) and largest online group (default 20).
12. **Owner email + Google account** for the booking sheet, and whether he wants LINE notifications.

Photos: the owner is happy for the photos to be used and edited. The hero and About photos are retouched versions
(promo sign / old banner and sparkles removed); food photos are the small originals.
