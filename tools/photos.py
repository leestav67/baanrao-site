#!/usr/bin/env python3
"""Photo blocks for index.html (and the /en/ head) — the ONE place to change which photos the site shows.

tools/build_en.py calls apply() first, so the Netlify build (and `python3 tools/build_en.py .`) always
regenerates these blocks in index.html:
  <!-- PHOTOS:<name> BEGIN ... -->  …generated…  <!-- PHOTOS:<name> END -->
plus the Restaurant JSON-LD "image" arrays, og:image / twitter:image (index.html and tools/head-en.html).
Don't hand-edit inside the markers: edit this file and rebuild.

QUICK SWITCHES (see PHOTO-SOURCES.md):
  HERO = "customer-food-01"   ->  "food-pan-owner" for the owner-safe hero (owner's own photo, no credit needed)
  SHOW_CUSTOMER_PHOTOS = True ->  False removes EVERY customer photo (hero falls back to the owner photo,
                                   the menu photo row disappears, gallery/JSON-LD keep owner photos only)
  To drop one customer photo: delete its id from MENU_PHOTOS / GALLERY (or set its "enabled": False).
  SHOW_PLACEHOLDERS = True    ->  False turns the PLACEHOLDER menu cards (gold line drawings, kind="placeholder")
                                   back into plain icon cards. To swap in a real photo: see MENU_CARDS below / README.
"""
import json, os, re

# ------------------------------------------------------------------ switches
HERO = "customer-food-01"           # one-line switch: "food-pan-owner" = owner-safe fallback hero
SHOW_CUSTOMER_PHOTOS = True         # False = owner photos only, everywhere
ABOUT = "clean-night"               # the real night shot (courtyard-night.jpg is daylight)
SETS = "set-moo-krata"              # falls back to SETS_OWNER when customer photos are off
SETS_OWNER = "food-pan-owner"
MENU_PHOTOS = ["peaceii-topdown-pan", "hellosammy-dish-03", "customer-food-02", "apisit-seafood-salad"]
GALLERY = ["hellosammy-pan", "food-pan-owner", "customer-food-03"]  # big food tile, food, venue (no repeats of About/menu photos)
STOREFRONT = "owner-courtyard-day"
SHOW_PLACEHOLDERS = True            # False = placeholder cards fall back to their icon
# Menu category cards (index.html <!-- PHOTOS:menu-card-<card> -->): card -> (photo id, fallback icon, sizes).
# The photo falls back to the icon when it's switched off (customer photo with SHOW_CUSTOMER_PHOTOS = False,
# placeholder with SHOW_PLACEHOLDERS = False, or "enabled": False). Card texts stay in index.html.
# To replace a placeholder with a real photo: make square 480/800 files with tools/make_photos.py (see
# menu_cards()), add an entry to P (kind "owner" or "customer" + by=…), and put its id here.
_CARD = "(min-width: 960px) 200px, (min-width: 640px) 33vw, 50vw"
MENU_CARDS = {
    "meat":    ("fb-beef-platter", None, "(min-width: 960px) 200px, 100vw"),          # full width below 960 px
    "seafood": ("hellosammy-dish-02", "i-fish", _CARD),
    "salads":  ("peaceii-papaya", "i-chili", _CARD),
    "noodles": ("placeholder-noodles", "i-bowl", _CARD),
    "veg":     ("surachat-tray", "i-leaf", "(min-width: 960px) 200px, 50vw"),   # half width at 640–959
    "drinks":  ("placeholder-drinks", "i-drink", "(min-width: 960px) 200px, (min-width: 640px) 50vw, 100vw"),  # full width < 640
}
# JSON-LD image array (absolute URLs, every file ≥1200 px wide), in this order. Thumbnails never go here.
JSONLD_IMAGES = [
    ("customer-food-01", "baanrao-moo-krata-pan-night-1200.jpg"),     # best dish-on-pan shot (= hero)
    ("fb-beef-platter", "baanrao-australian-beef-platter-1200.jpg"),  # platter
    ("owner-courtyard-day", "baanrao-storefront-courtyard-day-1200.jpg"),  # storefront (no sign photo exists)
    ("courtyard-night", "baanrao-courtyard-dusk-1200.jpg"),                # courtyard, early evening before dark
    ("clean-night", "baanrao-dining-area-night-4x3-1200.jpg"),             # real night shot of the covered courtyard (= About)
    ("food-pan-owner", "baanrao-moo-krata-pan-pork-belly-1200.jpg"),
    ("set-moo-krata", "baanrao-moo-krata-set-table-1200.jpg"),
    ("peaceii-topdown-pan", "baanrao-moo-krata-spread-topdown-1200.jpg"),
]

# ------------------------------------------------------------------ the photos
# kind: "owner" (the shop's own upload) or "customer" (belongs to the uploader: credit shown on the page)
#       or "placeholder" (NOT a photo of the restaurant: a "ภาพตัวอย่าง / Sample photo" badge is shown on the page,
#       and it may never go into JSON-LD / og).
# files: stem + list of (width, height) that exist as .avif/.webp/.jpg in images/
P = {
    "customer-food-01": dict(kind="customer", by="Sariya Wattanapong", stem="baanrao-moo-krata-pan-night", files=[(800, 600), (1200, 900)],
        alt_th="หมูกระทะ บ้านเราหมูกระทะ หมูย่างบนโดมกระทะร้อน มาม่าและผักในน้ำซุปรอบขอบ ควันกรุ่น ไฟประดับยามค่ำ",
        alt_en="Moo krata at Baan Rao: pork grilling on the hot dome pan, instant noodles and greens in the steaming broth around the rim, fairy lights behind",
        cap_th="หมูกระทะเตาถ่าน ร้อนๆ หอมๆ ทุกโต๊ะ", cap_en="Charcoal-grilled moo krata, sizzling at every table",
        blur="baanrao-moo-krata-pan-night-blur-480", og="baanrao-moo-krata-pan-night-og-1200.jpg"),
    "food-pan-owner": dict(kind="owner", stem="baanrao-moo-krata-pan-pork-belly-4x5", files=[(480, 600), (800, 1000)],
        hero_stem="baanrao-moo-krata-pan-pork-belly-4x3", hero_files=[(800, 600), (1200, 900)],
        alt_th="หมูกระทะ บ้านเราหมูกระทะ หมูสามชั้นย่างบนโดมกระทะ น้ำซุปรอบขอบกับผักกาดขาวและผักบุ้ง",
        alt_en="Moo krata at Baan Rao: pork belly grilling on the dome pan, broth with Chinese cabbage and morning glory around the rim",
        cap_th='หมูหมัก น้ำซุปสูตรบ้านเรา <span class="nw">ทำเองทุกขั้นตอน</span>', cap_en="Our own marinated pork and broth, made from scratch",
        blur="baanrao-moo-krata-pan-pork-belly-4x3-blur-480", og="baanrao-moo-krata-pan-pork-belly-og-1200.jpg"),
    # Owner photo, but it's DAYLIGHT (EXIF 2022-08-08 18:22, before sunset), not night: caption/alt say so.
    "courtyard-night": dict(kind="owner", stem="baanrao-courtyard-dusk", files=[(480, 360), (800, 600)], venue=True,
        alt_th="ลานนั่งทานบ้านเราหมูกระทะ ไฟประดับ โต๊ะไม้ ต้นไม้ และเคาน์เตอร์ป้ายไฟโลโก้ร้าน ช่วงเย็นก่อนฟ้ามืด",
        alt_en="The Baan Rao Moo Krata courtyard in the early evening before dark: string lights, wooden tables, trees and the logo-sign counter",
        cap_th="ลานกว้าง ร่มรื่น ไฟประดับรอบร้าน", cap_en="A leafy courtyard strung with lights. Open daily 17:00–22:00."),
    "set-moo-krata": dict(kind="customer", by="Sasithonk", stem="baanrao-moo-krata-set-table", files=[(480, 480), (800, 800)],
        alt_th="ชุดหมูกระทะจัดเต็มโต๊ะยาว น้ำจิ้ม ผักสด ข้าวโพด และจานหมูกับทะเล ร้านบ้านเราหมูกระทะ อุดรธานี",
        alt_en="A long table set for moo krata at Baan Rao, Udon Thani: dipping sauces, fresh veg, corn and a pork and seafood plate",
        cap_th="ชุดเริ่มต้น ฿199 อิ่มคุ้มทั้งโต๊ะ", cap_en="Sets from ฿199. Great value for the whole table."),
    "peaceii-topdown-pan": dict(kind="customer", by="Peaceii Keeratika", stem="baanrao-moo-krata-spread-topdown", files=[(480, 600), (800, 1000)],
        alt_th="หมูกระทะมุมสูง กระทะน้ำซุป หมูสไลซ์ ข้าวโพด ผัก และน้ำจิ้ม ล้อมวงบนโต๊ะ บ้านเราหมูกระทะ",
        alt_en="Moo krata from above at Baan Rao: the pan with broth, sliced pork, corn, vegetables and dipping sauces around it",
        cap_th="ล้อมวงปิ้ง ล้อมวงคุย อบอุ่นทั้งโต๊ะ", cap_en="Grill, chat, share: the whole table together."),
    "hellosammy-dish-03": dict(kind="customer", by="hellosammy0601", stem="baanrao-charcoal-stove-dipping-sauce", files=[(480, 600), (800, 1000)],
        alt_th="เตาถ่านหมูกระทะไฟแดงร้อน ถ้วยน้ำจิ้มสูตรบ้านเรา และชามหมูหมัก บนโต๊ะไม้ บ้านเราหมูกระทะ",
        alt_en="A glowing charcoal stove under the pan, a bowl of our dipping sauce and marinated pork on a wooden table at Baan Rao",
        cap_th='น้ำจิ้มสูตรบ้านเรา <span class="nw">จิ้มคำแรกก็ติดใจ</span>', cap_en="Our family’s own dipping sauce. One dip and you’re hooked."),
    "customer-food-02": dict(kind="customer", by="จีรศักดิ์ แหล้ยัง", stem="baanrao-somtam-papaya-salad", files=[(480, 600), (800, 1000)],
        alt_th="ส้มตำมะละกอใส่กุ้งแห้ง ถั่วแระ มะเขือเทศ และมะนาว ร้านบ้านเราหมูกระทะ อุดรธานี",
        alt_en="Som tam (green papaya salad) with dried shrimp, soybeans, tomato and lime at Baan Rao Moo Krata, Udon Thani",
        cap_th="ส้มตำแซ่บๆ คู่หมูกระทะ", cap_en="Spicy papaya salad, the perfect side"),
    "apisit-seafood-salad": dict(kind="customer", by="อภิสิทธิ์ นวลปักษี", stem="baanrao-yam-talay-seafood-salad", files=[(480, 600), (800, 1000)],
        alt_th="ยำทะเลวุ้นเส้น กุ้ง หอยแมลงภู่ ไส้กรอก และขึ้นฉ่าย ร้านบ้านเราหมูกระทะ อุดรธานี",
        alt_en="Spicy seafood glass-noodle salad with shrimp, mussels, Thai sausage and Chinese celery at Baan Rao Moo Krata, Udon Thani",
        cap_th="ยำรสจัดจ้าน สั่งเพิ่มได้", cap_en="Zingy Thai salads to share"),
    "hellosammy-pan": dict(kind="customer", by="hellosammy0601", stem="baanrao-moo-krata-pan-charcoal-stove", files=[(480, 352), (800, 586)],
        alt_th="กระทะหมูกระทะบนเตาถ่าน หมูย่างบนโดม ผักกาด ผักบุ้ง และเห็ดเข็มทองในน้ำซุป ชามหมูหมัก และน้ำจิ้ม",
        alt_en="Moo krata on a charcoal stove: pork on the dome, cabbage, morning glory and enoki mushrooms in the broth, marinated pork and chilli sauce",
        cap_th="ปิ้งไป ต้มไป อร่อยครบในกระทะเดียว", cap_en="Grill on top, simmer below: it all happens in one pan"),
    "customer-food-03": dict(kind="customer", by="จีรศักดิ์ แหล้ยัง", stem="baanrao-covered-seating-day", files=[(480, 360), (800, 600)], venue=True,
        alt_th="โซนนั่งทานมีหลังคาของร้านบ้านเราหมูกระทะ ไฟประดับ ต้นไม้ และโต๊ะ ตอนกลางวัน",
        alt_en="The covered seating area at Baan Rao Moo Krata by day, with string lights, plants and tables",
        cap_th="มีหลังคา นั่งสบาย ทั้งครอบครัว", cap_en="Covered seating for the whole family"),
    "fb-beef-platter": dict(kind="owner", stem="baanrao-australian-beef-platter", files=[(480, 320), (960, 640)],
        alt_th="เนื้ออสเตรเลียสไลซ์พร้อมปีกไก่ ส้มตำ และยำ สำหรับหมูกระทะ บ้านเราหมูกระทะ อุดรธานี",
        alt_en="Sliced Australian beef with chicken wings, som tam and a spicy Thai salad for moo krata at Baan Rao Moo Krata, Udon Thani",
        cap_th="เนื้ออสเตรเลียสไลซ์ ปิ้งบนกระทะร้อน", cap_en="Sliced Australian beef, ready for the hot pan"),
    "owner-courtyard-day": dict(kind="owner", stem="baanrao-storefront-courtyard-day", files=[(480, 360)], venue=True,
        alt_th="หน้าร้านบ้านเราหมูกระทะ อุดรธานี เคาน์เตอร์ ป้ายโลโก้ร้าน และโต๊ะไม้ ตอนกลางวัน",
        alt_en="The front of Baan Rao Moo Krata in Udon Thani by day: the counter, the logo sign and wooden tables",
        cap_th="มาถึงแล้ว! สังเกตเคาน์เตอร์และป้ายโลโก้ร้าน", cap_en="You’re here! Look for our counter and logo sign"),
    # Owner's Facebook night photo of the covered courtyard (promo sign removed, sky cleaned by the retouch bot).
    "clean-night": dict(kind="owner", stem="baanrao-dining-area-night-4x3", files=[(480, 360), (800, 600)], venue=True,
        alt_th="ลานนั่งทานของร้านบ้านเราหมูกระทะยามค่ำ ใต้หลังคาและไฟประดับ เคาน์เตอร์ ป้ายไฟโลโก้ และโต๊ะไม้",
        alt_en="The covered dining courtyard at Baan Rao Moo Krata at night, with string lights, the counter, the lit logo sign and wooden tables",
        cap_th="ไฟระยิบระยับยามค่ำ นั่งชิลได้ทั้งคืน", cap_en="Fairy lights and warm evenings. Open daily 17:00–22:00."),
    # ---- menu category cards (r5) ----
    "hellosammy-dish-02": dict(kind="customer", by="hellosammy0601", stem="baanrao-prawn-salad-seafood", files=[(480, 480), (800, 800)],
        alt_th="เมนูแซ่บใส่กุ้งตัวโต ข้าวโพด มะเขือเทศ หอมใหญ่ และต้นหอม ร้านบ้านเราหมูกระทะ อุดรธานี",
        alt_en="A spicy Thai dish with big prawns, corn, tomato, onion and spring onion at Baan Rao Moo Krata, Udon Thani",
        cap_th="กุ้งตัวโต แซ่บๆ", cap_en="Big prawns, nice and spicy"),
    "peaceii-papaya": dict(kind="customer", by="Peaceii Keeratika", stem="baanrao-somtam-plate", files=[(480, 480), (800, 800)],
        alt_th="ส้มตำมะละกอจานใหญ่ ใส่มะเขือเทศ ถั่วฝักยาว และถั่วลิสง ร้านบ้านเราหมูกระทะ อุดรธานี",
        alt_en="A big plate of som tam (green papaya salad) with tomato, long beans and peanuts at Baan Rao Moo Krata, Udon Thani",
        cap_th="ส้มตำจานใหญ่", cap_en="A big plate of som tam"),
    # r7: real vegetable tray from Google Maps (customer สุรชาติ ยั่งยืน), replaces placeholder-vegetables on the veg card.
    # r8: files made from the retouched version (light/colour/crop, crumbs removed, no food added); same contents, same alt.
    "surachat-tray": dict(kind="customer", by="สุรชาติ ยั่งยืน", stem="baanrao-vegetable-tray", files=[(480, 480), (800, 800)],
        alt_th="ถาดผักสดสำหรับหมูกระทะ เห็ดเข็มทอง ฟักทอง แครอท ผักกาด วุ้นเส้น ผักบุ้ง และข้าวโพดถ้วยเล็ก ร้านบ้านเราหมูกระทะ อุดรธานี",
        alt_en="A tray of fresh vegetables for moo krata at Baan Rao Moo Krata, Udon Thani: enoki mushrooms, pumpkin, carrot, cabbage, glass noodles, morning glory and a small bowl of corn",
        cap_th="ผักสดจัดเต็มถาด", cap_en="A full tray of fresh vegetables"),
    # PLACEHOLDERS: gold line drawings from tools/placeholders/*.svg (tools/make_photos.py placeholders). Not photos.
    "placeholder-noodles": dict(kind="placeholder", stem="baanrao-menu-placeholder-noodles", files=[(480, 480), (800, 800)],
        alt_th="ภาพตัวอย่าง ไม่ใช่ภาพจริงจากร้าน: ภาพลายเส้นสีทอง ชามเส้นควันกรุ่นกับตะเกียบ ไข่ต้ม และจานเล็ก",
        alt_en="Sample image, not a real photo from the restaurant: gold line drawing of a steaming noodle bowl with chopsticks, a boiled egg and a small side dish",
        cap_th="ภาพตัวอย่าง", cap_en="Sample photo"),
    "placeholder-vegetables": dict(kind="placeholder", stem="baanrao-menu-placeholder-vegetables", files=[(480, 480), (800, 800)],
        alt_th="ภาพตัวอย่าง ไม่ใช่ภาพจริงจากร้าน: ภาพลายเส้นสีทอง จานผักสด กะหล่ำปลี ผักบุ้ง เห็ด และข้าวโพด",
        alt_en="Sample image, not a real photo from the restaurant: gold line drawing of a plate of fresh vegetables with cabbage, morning glory, mushrooms and corn",
        cap_th="ภาพตัวอย่าง", cap_en="Sample photo"),
    "placeholder-drinks": dict(kind="placeholder", stem="baanrao-menu-placeholder-drinks", files=[(480, 480), (800, 800)],
        alt_th="ภาพตัวอย่าง ไม่ใช่ภาพจริงจากร้าน: ภาพลายเส้นสีทอง เครื่องดื่มเย็นใส่น้ำแข็งและหลอดสองแก้ว กับขวดน้ำเปล่า",
        alt_en="Sample image, not a real photo from the restaurant: gold line drawing of two iced drinks with straws and a bottle of water",
        cap_th="ภาพตัวอย่าง", cap_en="Sample photo"),
}


# ------------------------------------------------------------------ helpers
def on(pid):
    p = P[pid]
    if p["kind"] == "placeholder":
        return p.get("enabled", True) and SHOW_PLACEHOLDERS
    return p.get("enabled", True) and (SHOW_CUSTOMER_PHOTOS or p["kind"] == "owner")

def esc(s):
    return s.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")

def srcset(stem, files, ext):
    return ", ".join(f"images/{stem}-{w}.{ext} {w}w" for w, _ in files)

def picture(pid, sizes, cls="", eager=False, stem=None, files=None, pcls=""):
    p = P[pid]; stem = stem or p["stem"]; files = files or p["files"]
    w, h = files[-1] if eager else files[0]
    load = 'fetchpriority="high" decoding="async"' if eager else 'loading="lazy" decoding="async"'
    c = f' class="{cls}"' if cls else ""
    pc = f' class="{pcls}"' if pcls else ""
    return (f'<picture{pc}>'
            f'<source type="image/avif" srcset="{srcset(stem, files, "avif")}" sizes="{sizes}">'
            f'<source type="image/webp" srcset="{srcset(stem, files, "webp")}" sizes="{sizes}">'
            f'<img{c} src="images/{stem}-{files[0][0]}.jpg" srcset="{srcset(stem, files, "jpg")}" sizes="{sizes}" '
            f'alt="{esc(p["alt_th"])}" data-en-alt="{esc(p["alt_en"])}" width="{w}" height="{h}" {load}>'
            f'</picture>')

def credit(pid):
    p = P[pid]
    if p["kind"] != "customer":
        return ""
    name = p.get("by_en", p["by"])
    en = f'<span lang="th">{name}</span>' if is_thai(name) else name   # screen readers switch voice on /en/
    return f'<small class="pcredit" data-en="Photo: {esc(en)}">ภาพโดย {esc(p["by"])}</small>'

def is_thai(text):
    return bool(re.search("[\u0e00-\u0e7f]", text))

def cap(pid):
    p = P[pid]
    return f'<span data-en="{esc(p["cap_en"])}">{p["cap_th"]}</span>'  # cap_th may hold <span class="nw">

def hero_id():
    return HERO if on(HERO) else "food-pan-owner"


# ------------------------------------------------------------------ blocks
def block_hero_preload():
    pid = hero_id(); p = P[pid]
    stem, files = (p.get("hero_stem", p["stem"]), p.get("hero_files", p["files"]))
    return (f'<link rel="preload" as="image" type="image/avif" imagesrcset="{srcset(stem, files, "avif")}" '
            f'imagesizes="(min-width: 960px) 75vw, 100vw" fetchpriority="high">')

def block_hero():
    pid = hero_id(); p = P[pid]
    stem, files = (p.get("hero_stem", p["stem"]), p.get("hero_files", p["files"]))
    return "\n".join([
        '<picture class="hero-blur-pic">'
        f'<source media="(min-width: 960px)" type="image/avif" srcset="images/{p["blur"]}.avif">'
        f'<source media="(min-width: 960px)" srcset="images/{p["blur"]}.jpg">'
        '<img class="hero-blur" src="data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==" alt="" aria-hidden="true" width="480" height="360">'
        '</picture>',
        picture(pid, "(min-width: 960px) 75vw, 100vw", cls="hero-bg", eager=True, stem=stem, files=files, pcls="hero-pic"),
        f'<p class="hero-cap">{cap(pid)}{credit(pid)}</p>',
    ])

def block_about():
    return (picture(ABOUT, "(min-width: 960px) 480px, 100vw", cls="about-photo") +
            f'\n<p class="about-cap">{cap(ABOUT)}{credit(ABOUT)}</p>')

def block_sets():
    pid = SETS if on(SETS) else SETS_OWNER
    return (f'<figure class="sets-photo">{picture(pid, "(min-width: 960px) 300px, 100vw", cls="sets-img")}'
            f'<figcaption>{cap(pid)}</figcaption>{credit(pid)}</figure>')

def block_menu_photos():
    items = [i for i in MENU_PHOTOS if on(i)]
    if not items:
        return ""
    tiles = "\n".join(
        f'  <figure class="mp">{picture(i, "(min-width: 960px) 260px, 50vw")}{credit(i)}<figcaption>{cap(i)}</figcaption></figure>'
        for i in items)
    return f'<div class="menu-photos">\n{tiles}\n</div>'

def block_gallery():
    items = [i for i in GALLERY if on(i) and not (i == hero_id())]
    if not items:
        return ""
    tiles = []
    for n, i in enumerate(items):
        big = n == 0
        tiles.append(f'    <figure class="g{" g-big" if big else ""}{" g-venue" if P[i].get("venue") else ""}">'
                     f'{picture(i, "(min-width: 960px) 830px, (min-width: 700px) 66vw, 100vw" if big else "(min-width: 960px) 420px, (min-width: 700px) 33vw, 50vw")}'
                     f'<figcaption>{cap(i)}{credit(i)}</figcaption></figure>')
    return ('<section class="section gallery" id="gallery" aria-labelledby="galleryTitle">\n  <div class="wrap">\n'
            '    <div class="section-head">\n'
            '      <span class="kicker" data-en="Food &amp; atmosphere">อาหารและบรรยากาศ</span>\n'
            '      <h2 id="galleryTitle" data-en="A taste of Baan Rao">ภาพจริงจากบ้านเรา</h2>\n'
            '      <p data-en="Real photos from our tables and our courtyard, many shared by guests on Google Maps.">ภาพจริงจากโต๊ะอาหารและลานร้าน ส่วนหนึ่งจากลูกค้าที่แชร์บน Google Maps</p>\n'
            '    </div>\n'
            f'    <div class="gal gal-{len(items)}">\n' + "\n".join(tiles) + '\n    </div>\n  </div>\n</section>')

def block_storefront():
    if not on(STOREFRONT):
        return ""
    return f'<figure class="storefront">{picture(STOREFRONT, "(min-width: 960px) 240px, 40vw")}<figcaption>{cap(STOREFRONT)}</figcaption></figure>'

def sample_badge(pid):
    return '<small class="mc-sample" data-en="Sample photo">ภาพตัวอย่าง</small>' if P[pid]["kind"] == "placeholder" else ""

def block_menu_card(card):
    pid, icon, sizes = MENU_CARDS[card]
    if not on(pid):
        if not icon:
            raise SystemExit(f"menu card {card!r}: photo {pid!r} is off and there is no fallback icon")
        return f'<span class="mc-ico"><svg class="i"><use href="#{icon}"/></svg></span>'
    return f'<div class="mc-pic">{picture(pid, sizes)}{sample_badge(pid)}{credit(pid)}</div>'

BLOCKS = {"hero-preload": block_hero_preload, "hero": block_hero, "about": block_about, "sets": block_sets,
          "menu-photos": block_menu_photos, "gallery": block_gallery, "storefront": block_storefront}
BLOCKS.update({f"menu-card-{c}": (lambda c=c: block_menu_card(c)) for c in MENU_CARDS})


# ------------------------------------------------------------------ apply
def _swap_block(html, name, body):
    pat = re.compile(r"(<!-- PHOTOS:" + re.escape(name) + r" BEGIN[^>]*-->)(.*?)(<!-- PHOTOS:" + re.escape(name) + r" END -->)", re.S)
    if not pat.search(html):
        raise SystemExit(f"index.html is missing the PHOTOS:{name} markers")
    return pat.sub(lambda m: m.group(1) + "\n" + body + "\n" + m.group(3), html, count=1)

def _images_json(base, indent="    "):
    items = []
    for pid, f in JSONLD_IMAGES:
        if P[pid]["kind"] == "placeholder":
            raise SystemExit(f"JSONLD_IMAGES: {pid} is a placeholder, not a real photo; keep it out of JSON-LD")
        if not on(pid):
            continue
        url = f"{base}/images/{f}"
        p = P[pid]
        if p["kind"] == "customer":   # image-licence metadata: credit the uploader
            items.append(json.dumps({"@type": "ImageObject", "contentUrl": url, "url": url,
                                     "creditText": p["by"], "creator": {"@type": "Person", "name": p["by"]}},
                                    ensure_ascii=False))
        else:
            items.append(json.dumps(url))
    return "[\n" + ",\n".join(indent + i for i in items) + "\n  ]"

def _og(html, base, lang):
    p = P[hero_id()]
    if p["kind"] == "placeholder":
        raise SystemExit("og:image can't be a placeholder")
    url = f"{base}/images/{p['og']}"
    alt = p["alt_th"] if lang == "th" else p["alt_en"]
    html = re.sub(r'(<meta property="og:image" content=")[^"]*(")', lambda m: m.group(1) + url + m.group(2), html, count=1)
    html = re.sub(r'(<meta name="twitter:image" content=")[^"]*(")', lambda m: m.group(1) + url + m.group(2), html, count=1)
    html = re.sub(r'(<meta property="og:image:alt" content=")[^"]*(")', lambda m: m.group(1) + esc(alt) + m.group(2), html, count=1)
    return html

def _restaurant_images(html, base):
    # first "image": [ … ] inside the Restaurant JSON-LD
    return re.sub(r'"image": \[[^\]]*\]', lambda m: '"image": ' + _images_json(base), html, count=1)

def apply(site, base):
    idx = os.path.join(site, "index.html")
    html = open(idx, encoding="utf-8").read()
    for name, fn in BLOCKS.items():
        html = _swap_block(html, name, fn())
    html = _restaurant_images(html, base)
    html = _og(html, base, "th")
    open(idx, "w", encoding="utf-8").write(html)
    head = os.path.join(site, "tools", "head-en.html")
    h = open(head, encoding="utf-8").read()
    h = _restaurant_images(h, "{{SITE_URL}}")
    h = _og(h, "{{SITE_URL}}", "en")
    open(head, "w", encoding="utf-8").write(h)
    cards = [v[0] for v in MENU_CARDS.values()]
    n = sum(1 for i in set(MENU_PHOTOS + GALLERY + [HERO, SETS] + cards) if on(i) and P[i]["kind"] == "customer")
    ph = sum(1 for i in cards if on(i) and P[i]["kind"] == "placeholder")
    print(f"photos: hero={hero_id()} customer photos {'on' if SHOW_CUSTOMER_PHOTOS else 'OFF'} ({n} in use), "
          f"menu-card placeholders {ph}")
