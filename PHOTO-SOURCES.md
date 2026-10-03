# Photo sources

Every photo on the site, who took it, and where it's used. **Customer photos belong to the person who uploaded them to Google Maps.**
Lee has approved using them; each one shows a small credit on the page (TH "ภาพโดย …" on `/`, EN "Photo: …" on `/en/`, Thai names wrapped in `<span lang="th">`), and in the JSON-LD `image` array customer photos are `ImageObject`s with `creditText` and `creator`.

## Switches (all in `tools/photos.py`, then run `python3 tools/build_en.py .`)

| What | Change |
|---|---|
| Owner-safe hero (no customer photo in the hero) | `HERO = "customer-food-01"` → `HERO = "food-pan-owner"` (caption becomes "หมูหมัก น้ำซุปสูตรบ้านเรา ทำเองทุกขั้นตอน" / "Our own marinated pork and broth, made from scratch"; og:image switches too) |
| Remove **all** customer photos | `SHOW_CUSTOMER_PHOTOS = False` (hero → owner pan, sets photo → owner pan, menu photo row disappears, gallery and JSON-LD keep owner photos only) |
| Remove one photo | delete its id from `MENU_PHOTOS` / `GALLERY`, or add `enabled=False` to its entry in `P` |

The page blocks between `<!-- PHOTOS:… BEGIN -->` and `<!-- PHOTOS:… END -->` in `index.html`, the Restaurant JSON-LD `image` arrays and `og:image`/`twitter:image` (in `index.html` and `tools/head-en.html`) are rewritten by that script on every build. Don't hand-edit them.
Derivatives are made by `tools/make_photos.py` from the originals in `/workspace/baanrao/photos/google/` (not in the repo): sRGB, EXIF/GPS stripped.

## Google Maps listing photos

| Original | Site files (`images/`) | Uploader | Owner / customer | Where | Source |
|---|---|---|---|---|---|
| `customer-food-01.jpg` | `baanrao-moo-krata-pan-night-*.{avif,webp,jpg}`<br>`baanrao-moo-krata-pan-night-1200.jpg (JSON-LD)`<br>`baanrao-moo-krata-pan-night-og-1200.jpg (og)`<br>`baanrao-moo-krata-pan-night-blur-480.*` | Sariya Wattanapong | customer | Hero (index + /en/), og:image, twitter:image, JSON-LD image #1 | [Google photo](https://lh3.googleusercontent.com/gps-cs-s/ANWiy9QRyN6Bu1UccHLea5F33DciE8S-G2DymFleoQK_m-Xv_F9RvmdDgx89uURrrC1Aonv9Q8I6bQ5z1I1fJTuzGGXxHArlELKv4sdv8Xj100fWEkqILgg2zQf_ePeV97zyZYPWK7UJuoNHJbqC=s2000) |
| `food-pan-owner.jpg` | `baanrao-moo-krata-pan-pork-belly-4x5-*.{avif,webp,jpg}`<br>`baanrao-moo-krata-pan-pork-belly-4x3-*.{avif,webp,jpg}`<br>`baanrao-moo-krata-pan-pork-belly-og-1200.jpg`<br>`baanrao-moo-krata-pan-pork-belly-4x3-blur-480.*`<br>`baanrao-moo-krata-pan-pork-belly-1200.jpg (JSON-LD, from SEO)` | บ้านเราหมูกระทะ (owner) | owner | Gallery tile 2; owner-safe fallback hero (`HERO = "food-pan-owner"`); sets photo if customer photos are switched off; JSON-LD (`baanrao-moo-krata-pan-pork-belly-1200.jpg`) | [Google photo](https://lh3.googleusercontent.com/gps-cs-s/ANWiy9TuF0dlIrfijr5uAFT0hrX_iPctfl1esTPLOQ5DIc2tPVkFFW6CEJqhlYHKaeexIGTbacOVQTSRCaCv9jcH6dWaDGmbJhMdWyVjj40_OdCXuYaT-vy0xOpPhsgfp1PNiSOyydA=s2000) |
| `courtyard-night.jpg` | `baanrao-courtyard-dusk-*.{avif,webp,jpg}`<br>`baanrao-courtyard-dusk-1200.jpg (JSON-LD, from SEO)` | บ้านเราหมูกระทะ (owner) | owner | JSON-LD only (`baanrao-courtyard-dusk-1200.jpg`). **Not a night photo** despite the file name: EXIF says 8 Aug 2022, 18:22 (before sunset) and it reads as daylight, so it's no longer the About photo and its caption/alt say "ลานกว้าง ร่มรื่น ไฟประดับรอบร้าน" / early evening before dark. It is from 2022 (no roof over the tables yet), so it may show an older layout. | [Google photo](https://lh3.googleusercontent.com/gps-cs-s/ANWiy9SsTvtorH6L_y5C7k3eGsv406umWzG9rYc3XakrWfMw2_inkhZwAOku1UPfvJOiO15PLTnwrN_WMTTbUmN33vKq7bFwnhKeIXt5bdhj9QuUvICQrpGoWB9CoTAlX68M4hfuNJd7=s2000) |
| `set-moo-krata.jpg` | `baanrao-moo-krata-set-table-*.{avif,webp,jpg}`<br>`baanrao-moo-krata-set-table-1200.jpg (JSON-LD)` | Sasithonk | customer | Menu: sets card photo; JSON-LD | [Google photo](https://lh3.googleusercontent.com/gps-cs-s/ANWiy9SYNJ4y-wluFI-D3BqZlnjVt-fVmmKEvTjXviA0zo4prQXrgP9pcttjgomJl3l9mGgHF1S4SGevBRunSyhyIr9s-_hhFcOjtyXDLzePFHuLsh404ivyrpJQyURZyjdKOh6qE9Xgch8x55xq=s2000) |
| `peaceii-topdown-pan.jpg` | `baanrao-moo-krata-spread-topdown-*.{avif,webp,jpg}`<br>`baanrao-moo-krata-spread-topdown-1200.jpg (JSON-LD)` | Peaceii Keeratika | customer | Menu photo row #1; JSON-LD | [Google photo](https://lh3.googleusercontent.com/grass-cs/AABkmLc7-s_lOn9KnflHcCbRI2eyD16iGYLlfhLlzoRl7OzEprpV0hqsRLxoZRsDjFF7eE7yTxspm1YrG8jmW2th0VoMHcqb_LpNRKb-KwrT3vD9Dyq5USDh2fAksITJ5BkPyMCf0Xx_5SAWlKI=s2000) |
| `hellosammy-dish-03.jpg` | `baanrao-charcoal-stove-dipping-sauce-*.{avif,webp,jpg}` | hellosammy0601 | customer | Menu photo row #2 (sauce) | [Google photo](https://lh3.googleusercontent.com/grass-cs/AABkmLera49QoS9SCAustASRG5FDwj09QjTYhhffY6NdnsdnE05sw_4PqLDRNd2c4qyDXHeTKkdBoRrS5EWgyQW-YJSTIySuhVi8KtBouDAshDZr7vM20Do6Jb5lxWpc4B6ZWsnArfscdel6e9I=s2000) |
| `customer-food-02.jpg` | `baanrao-somtam-papaya-salad-*.{avif,webp,jpg}` | จีรศักดิ์ แหล้ยัง — **uploader to verify** | customer | Menu photo row #3 (som tam). The photo collector's working list (`work/candidates.tsv`) gives **Baster Nutnaree** for this same Google URL, while its final `sources.txt` says จีรศักดิ์ แหล้ยัง. The URL itself doesn't carry the uploader. Check the photo on the Google listing and fix `by=` in `tools/photos.py` if needed. | [Google photo](https://lh3.googleusercontent.com/gps-cs-s/ANWiy9Q11bQw5UZ1alned1DYXGsK37TQx4QWAb8JbsFI02cgZRvvmZ98reu5BbMflUzegxu49xxhSjHKZUxunOlMS9Zb1Taoyvhq_c0REVn7LYTJ1FhJwDAJwMA9L7On-6KXmw-0v5o5wzDECl_k=s2000) |
| `apisit-seafood-salad.jpg` | `baanrao-yam-talay-seafood-salad-*.{avif,webp,jpg}` | อภิสิทธิ์ นวลปักษี | customer | Menu photo row #4 (yam talay) | [Google photo](https://lh3.googleusercontent.com/grass-cs/AABkmLchuSFuFHcniKX-yvOP4YaQ_D7qWrPLZX38-gvOywDlO8xXYgpWIToFHlxpQGnLtvwVKVeTjsBjTWQkym0vfvNe2aIinPKFp7m-a2Tr0pZKzqotvAcb9FaR2jRlpWmJZRrWvJHg5AbRV7Li=s2000) |
| `hellosammy-pan.jpg` | `baanrao-moo-krata-pan-charcoal-stove-*.{avif,webp,jpg}` | hellosammy0601 | customer | Gallery tile 1 (big) | [Google photo](https://lh3.googleusercontent.com/grass-cs/AABkmLc1FFf9i_n5Kj9pgKQ8cMM_kzyh1wTIj_-hb2XFqYBZM6ef1j29_zQiQ3dsu9SOHC6zyAbQUxZMgBzyqUFjK6VzmmgBAfK1mvoonm0logb6K1YpTENOLyVwiY8YEq-FUD0ZjgQMP26AxvZ9=s2000) |
| `customer-food-03.jpg` | `baanrao-covered-seating-day-*.{avif,webp,jpg}` | จีรศักดิ์ แหล้ยัง | customer | Gallery tile 3 (venue; daytime photo) **Venue confirmed by the owner via Lee (3 Oct 2026).** | [Google photo](https://lh3.googleusercontent.com/gps-cs-s/ANWiy9SnBJFZFWoI9bVbJi_9W9Tqts0Hq5RiHqvi8VhbngkaL3YftpqCkwOQHVlLyaxowCVLvrJBgFDpAXyFgYkfDGxto8czUpVnaUkw-p6uHxm-1Jvny2kfyUtmZftHLe9BKDc3UB6axn2ilLI=s2000) |
| `owner-courtyard-day.jpg` | `baanrao-storefront-courtyard-day-*.{avif,webp,jpg}`<br>`baanrao-storefront-courtyard-day-1200.jpg (JSON-LD, from SEO)` | บ้านเราหมูกระทะ (owner) | owner | Find us: small storefront photo under the directions; JSON-LD (`baanrao-storefront-courtyard-day-1200.jpg`) | [Google photo](https://lh3.googleusercontent.com/gps-cs-s/ANWiy9SJya_PcR8G5OFdEIc6FL6Xe6MNAy906y9IrdNxCyWJ9h6JdV-quCxM2HXzsJoWNaqjlWOjhH7xmgMp1hO-xv266AJPyo_vVOXSQ2kfkkEl-ucxNinGlgNgdxOrkSkuoLE1fWWULA=s2000) |

## Other photos (owner's own Facebook / signage, already on the site)

| Site files | Source | Where |
|---|---|---|
| `baanrao-australian-beef-platter-480/960.*`, `baanrao-australian-beef-platter-1200.jpg` | Owner's Facebook (`fb/menu-dish-thaiplus.jpg`). Confirmed as sliced Australian beef | Menu: meats card; JSON-LD image #2; **`hasMenu.image` (PLACEHOLDER until there's a menu-board photo: save it as `images/baanrao-menu-board.jpg` ≥1200 px and point `hasMenu.image` at it in both `index.html` and `tools/head-en.html`)** |
| `baanrao-dining-area-night-4x3-480/800.{avif,webp,jpg}`, `baanrao-dining-area-night-4x3-1200.jpg` | Owner's Facebook night photo (`hero-new.jpg`, the previous hero); promo sign removed and sky cleaned up by the retouch bot. **The only real night shot we have** | About section photo, caption "ไฟระยิบระยับยามค่ำ นั่งชิลได้ทั้งคืน" / "Fairy lights and warm evenings. Open daily 5–10 pm." JSON-LD: `baanrao-dining-area-night-4x3-1200.jpg` (the old 16x9/4x3/1x1 crops were dropped on SEO review) |
| `logo.jpg`, video posters | Owner | logo badge / videos |
| `og-image.jpg` | Owner (old night photo) | no longer referenced; kept so old share links still show a picture |

## Not used (and why)

| Original | Uploader | Why |
|---|---|---|
| `peaceii-papaya.jpg` | Peaceii Keeratika (customer) | Duplicate of the som tam shot (Marketing) |
| `hellosammy-dish-02.jpg` | hellosammy0601 (customer) | Duplicate angle of the stove/sauce shot (Marketing) |
| `apisit-pan.jpg` | อภิสิทธิ์ นวลปักษี (customer) | Pale raw pork, not appetising (Marketing) |
| `apisit-platter.jpg` | อภิสิทธิ์ นวลปักษี (customer) | SEO skips it; the owner's Australian beef platter is used instead |
