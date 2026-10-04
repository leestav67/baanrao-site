#!/usr/bin/env python3
"""Make the web derivatives of the Google Maps listing photos (run once; output is committed).

Needs Pillow >= 11.3 (AVIF). Sources live outside the repo:
  /workspace/baanrao/photos/google/*.jpg   (see PHOTO-SOURCES.md for uploaders and URLs)
Output: images/baanrao-<subject>-<detail>-<width>.{avif,webp,jpg}
  - converted to sRGB (most sources are Display P3), EXIF/GPS stripped (nothing copied over)
  - AVIF q≈50, WebP q≈75, JPEG q≈78 progressive; quality steps down only if a file is over budget
Budgets: hero 1200 (source is only 1200 px wide, so no 1600): AVIF ≤120 KB, WebP ≤160 KB, JPEG ≤220 KB.
         cards/gallery 800: WebP ≤60 KB, JPEG ≤90 KB.
"""
import io, os, sys
from PIL import Image, ImageCms, ImageOps, ImageFilter

G = '/workspace/baanrao/photos/google/'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'images')
SRGB = ImageCms.createProfile('sRGB')
KB = 1024

def load(name):
    im = Image.open(G + name)
    icc = im.info.get('icc_profile')
    im = ImageOps.exif_transpose(im).convert('RGB')
    if icc:
        src = ImageCms.ImageCmsProfile(io.BytesIO(icc))
        im = ImageCms.profileToProfile(im, src, SRGB, outputMode='RGB')
    return im

def crop(im, box):            # box in fractions (l, t, r, b)
    w, h = im.size
    return im.crop((round(box[0]*w), round(box[1]*h), round(box[2]*w), round(box[3]*h)))

def to_ratio(im, rw, rh, xb=0.5, yb=0.5):
    w, h = im.size
    if w / h > rw / rh:
        nw = round(h * rw / rh); x = round((w - nw) * xb); return im.crop((x, 0, x + nw, h))
    nh = round(w * rh / rw); y = round((h - nh) * yb); return im.crop((0, y, w, y + nh))

def fit(im, w):
    return im if im.width <= w else im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)

def save(im, path, fmt, q, limit, qmin):
    while True:
        buf = io.BytesIO()
        if fmt == 'avif': im.save(buf, 'AVIF', quality=q)
        elif fmt == 'webp': im.save(buf, 'WEBP', quality=q, method=6)
        else: im.save(buf, 'JPEG', quality=q, optimize=True, progressive=True)
        if not limit or buf.tell() <= limit or q <= qmin:
            open(path, 'wb').write(buf.getvalue())
            return q, buf.tell()
        q -= 3

def three(im, stem, w, budget):
    im = fit(im, w)
    res = []
    for fmt, q, qmin in (('avif', 50, 35), ('webp', 75, 50), ('jpg', 78, 55)):
        src, note = im, ''
        q2, n = save(src, f'{OUT}/{stem}-{w}.{fmt}', fmt, q, budget.get(fmt), qmin)
        lim = budget.get(fmt)
        # Busy textures (gravel, foliage, phone sharpening noise) blow the budget: soften the noise a
        # touch instead of dropping JPEG/WebP quality into visible blocking.
        for r in (0.5, 0.8, 1.1):
            if not lim or n <= lim: break
            src, note = im.filter(ImageFilter.GaussianBlur(r)), f' blur{r}'
            q2, n = save(src, f'{OUT}/{stem}-{w}.{fmt}', fmt, q, lim, qmin)
        res.append(f'{fmt} {n/KB:.0f}KB q{q2}{note}')
    print(f'{stem}-{w}  {im.size[0]}x{im.size[1]}  ' + ' · '.join(res))
    return im

HERO = {'avif': 120*KB, 'webp': 160*KB, 'jpg': 220*KB}
CARD = {'webp': 60*KB, 'jpg': 90*KB}
CARD480 = {'webp': 30*KB, 'jpg': 45*KB}

def card(im, stem):
    three(im, stem, 480, CARD480); three(im, stem, 800, CARD)

def jsonld(im, stem, w=1200):
    """Large JPEG for JSON-LD / og (≥1200 px wide), ≤250 KB."""
    im = fit(im, w)
    q, n = save(im, f'{OUT}/{stem}-{w}.jpg', 'jpg', 80, 250*KB, 60)
    print(f'{stem}-{w}.jpg  {im.size[0]}x{im.size[1]}  {n/KB:.0f}KB q{q} (JSON-LD)')

def blur(im, stem):
    b = fit(im, 480)
    b.save(f'{OUT}/{stem}-blur-480.avif', 'AVIF', quality=40)
    b.save(f'{OUT}/{stem}-blur-480.jpg', 'JPEG', quality=60, optimize=True)

CREDIT_FONT = '/usr/share/fonts/truetype/sand-box/google/Noto Sans/NotoSans-VariableFont_wdth,wght.ttf'

def burn_credit(im, text):
    """Small credit pill, bottom-right, for customer photos used as share images (LINE/Facebook previews
    don't show the on-page credit). Latin text so one file works for TH and EN."""
    from PIL import ImageDraw, ImageFont
    im = im.copy()
    f = ImageFont.truetype(CREDIT_FONT, 22)
    try: f.set_variation_by_name('SemiBold')
    except Exception: pass
    d = ImageDraw.Draw(im, 'RGBA')
    l, t, r, b = d.textbbox((0, 0), text, font=f)
    w, h = r - l, b - t
    x1, y1 = im.width - 18, im.height - 16
    x0, y0 = x1 - w - 28, y1 - h - 18
    d.rounded_rectangle((x0, y0, x1, y1), radius=(y1 - y0) // 2, fill=(15, 12, 8, 170))
    d.text((x0 + 14 - l, y0 + 9 - t), text, font=f, fill=(255, 255, 255, 255))
    return im

def og_night():
    """Share image (og:image / twitter:image): the hero pan photo, 1200x630, with the uploader's credit burnt in."""
    pan = load('customer-food-01.jpg')
    og = to_ratio(pan, 1200, 630, yb=0.62).resize((1200, 630), Image.LANCZOS)
    og = burn_credit(og, 'Photo: Sariya Wattanapong')
    save(og, f'{OUT}/baanrao-moo-krata-pan-night-og-1200.jpg', 'jpg', 82, 200*KB, 60)
    print('baanrao-moo-krata-pan-night-og-1200.jpg  1200x630  (credit burnt in)')

def menu_cards():
    """Menu category cards (r5, r7, r8, r9): square 480/800 crops of real customer photos."""
    # SEAFOOD card (customer, hellosammy0601): prawn salad; crop away the pork plate and sauce bowl at the top
    card(load('hellosammy-dish-02.jpg').crop((100, 400, 1500, 1800)), 'baanrao-prawn-salad-seafood')
    # SALADS & SOM TAM card (customer, Peaceii Keeratika): som tam on a plate; crop away the hand and the plants
    card(load('peaceii-papaya.jpg').crop((500, 100, 1900, 1500)), 'baanrao-somtam-plate')
    # VEGETABLES card (customer, สุรชาติ ยั่งยืน). r8: Photo Retouch's version of surachat-tray.jpg, already a
    # 1200x1200 square of the vegetable tray (light/colour corrected, crumbs removed, no food added; no ICC/EXIF).
    # r7 used the original instead: card(load('surachat-tray.jpg').crop((232, 225, 1080, 1073)), ...)
    card(load('surachat-tray-retouched.jpg'), 'baanrao-vegetable-tray')
    # NOODLES & SIDES card (r9, customer, อภิสิทธิ์ นวลปักษี): yam woon sen talay; square on the plate, the neighbouring
    # plate (right) and the orange bowl (top) cropped out
    card(load('apisit-seafood-salad.jpg').crop((30, 560, 1200, 1730)), 'baanrao-yam-woon-sen-talay-square')

FB = '/workspace/baanrao/photos/fb/r10/'

def load_fb(name):
    """Owner's Facebook photos (r10). FB serves sRGB JPEGs without EXIF; same conversion path as load()."""
    im = Image.open(FB + name)
    icc = im.info.get('icc_profile')
    im = ImageOps.exif_transpose(im).convert('RGB')
    if icc:
        im = ImageCms.profileToProfile(im, ImageCms.ImageCmsProfile(io.BytesIO(icc)), SRGB, outputMode='RGB')
    return im

def upto(im, w):
    """Scale a crop up to w px wide when it's a little smaller (LANCZOS + a light unsharp mask); see each call."""
    if im.width >= w:
        return im
    return im.resize((w, round(im.height * w / im.width)), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.0, 30, 2))

def fb_r10():
    """r10: owner's own Facebook photos replace 4 customer photos (seafood card, sets, menu row #3, salads card).
    Crop boxes are in pixels of the downloaded originals (see PHOTO-SOURCES.md for post dates and URLs)."""
    # SEAFOOD card: 22 Mar 2026 post, photo 2 of 5 (2048x1365): the whole orange seafood/suki bowl, veg tray cropped out
    card(load_fb('fb-15-0322-2-seafood-platter.jpg').crop((0, 170, 1070, 1240)), 'baanrao-seafood-suki-bowl')
    # SETS: 22 Mar 2026 post, photo 3 of 5 (1366x2048): the full set. Square starts right of the diner's arm/shirt
    # (x < ~300) and below the hand reaching in at the top left (y < ~520), so it's 1056 px: scaled to 1200 for JSON-LD
    st = upto(load_fb('fb-14-0322-3-hotpot-table.jpg').crop((310, 530, 1366, 1586)), 1200)
    card(st, 'baanrao-moo-krata-set-charcoal')
    jsonld(st, 'baanrao-moo-krata-set-charcoal')
    # MENU photo row #3: 17 Apr 2026 post (1536x2048): plate of sliced beef, fairy-light bokeh. 4:5 for the row below
    # 960 px, 4:3 from 960 px (the row is 4:3 there; served with <source media>), plate kept whole in both
    bp = load_fb('fb-11-pork-sides-0417.jpg')
    card(bp.crop((0, 40, 1536, 1960)), 'baanrao-sliced-beef-plate-night-4x5')
    card(bp.crop((0, 700, 1536, 1852)), 'baanrao-sliced-beef-plate-night-4x3')
    # SALADS card: 18 Mar 2026 post (2048x1367): the som tam on its oval plate. The yam plate (left), the veg tray (top),
    # the chicken wings (bottom) and the sauce bowl / table sign (right) all touch it, so the clean square is 623 px:
    # scaled to 800
    card(upto(load_fb('fb-18-two-salads-0318.jpg').crop((955, 362, 1578, 985)), 800), 'baanrao-somtam-oval-plate')

OD = '/workspace/baanrao/photos/owner-drinks/'

def owner_drinks():
    """r10: drinks card. Owner photo supplied by Lee on 4 Oct 2026 (master outside the repo, Display P3 -> sRGB).
    Square on the iced red soda (Rao Cafe cup; the number printed on it is 065 615 4656, the current one, so it stays);
    the plant and figurine are partly in. The cup stays whole inside the 3:2 and 4:3 bands the card uses at some widths."""
    im = Image.open(OD + 'iced-red-soda-rao-cafe.png')
    icc = im.info.get('icc_profile')
    im = ImageOps.exif_transpose(im).convert('RGB')
    if icc:
        im = ImageCms.profileToProfile(im, ImageCms.ImageCmsProfile(io.BytesIO(icc)), SRGB, outputMode='RGB')
    card(im.crop((0, 530, 930, 1460)), 'baanrao-iced-red-soda')

ON = '/workspace/baanrao/photos/owner-noodles/'

def owner_noodles():
    """r10: noodles card. Owner photo of the beef noodle soup (lunch menu), supplied by Lee on 4 Oct 2026; master outside
    the repo (1108x1477 PNG, sRGB). Square over the whole bowl. (Lee sent 3 more; not used: one has an AI-generated
    watermark and two have AI-looking wood backgrounds.)"""
    im = ImageOps.exif_transpose(Image.open(ON + 'beef-noodle-soup.png')).convert('RGB')
    card(im.crop((0, 268, 1108, 1376)), 'baanrao-beef-noodle-soup')

def placeholders():
    """Menu-card PLACEHOLDERS: gold line drawings (tools/placeholders/*.svg), NOT photos. Rendered with
    headless Chrome (Playwright), then saved like any other card. Replace them with real photos: see README."""
    import tempfile
    from playwright.sync_api import sync_playwright
    here = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'placeholders')
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=os.environ.get('CHROME', '/usr/bin/google-chrome'), args=['--headless=new'])
        pg = b.new_page(viewport={'width': 800, 'height': 800})
        for name in ('noodles', 'vegetables', 'drinks'):
            pg.goto('file://' + os.path.join(here, f'placeholder-{name}.svg'))
            png = os.path.join(tempfile.gettempdir(), f'placeholder-{name}.png')
            pg.screenshot(path=png)
            card(Image.open(png).convert('RGB'), f'baanrao-menu-placeholder-{name}')
        b.close()

if __name__ == '__main__' and len(sys.argv) > 1:
    # python3 tools/make_photos.py menu-cards placeholders og fb-r10 owner-drinks owner-noodles   (only those sets; no args = everything)
    for what in sys.argv[1:]:
        {'menu-cards': menu_cards, 'placeholders': placeholders, 'og': og_night, 'fb-r10': fb_r10, 'owner-drinks': owner_drinks, 'owner-noodles': owner_noodles}[what]()
    sys.exit(0)

if __name__ == '__main__':
    # HERO (customer, Sariya Wattanapong): smoking pan, fairy-light bokeh. 1200x900 source.
    pan = load('customer-food-01.jpg')
    for w in (800, 1200): three(pan, 'baanrao-moo-krata-pan-night', w, HERO)
    blur(pan, 'baanrao-moo-krata-pan-night')
    jsonld(pan, 'baanrao-moo-krata-pan-night')      # same pixels as hero-1200, for JSON-LD
    og_night()                                       # 1200x630 share image, credit burnt in
    # HERO fallback (owner): pork belly on the pan, 4:3 crop of a portrait photo
    own = load('food-pan-owner.jpg')
    own43 = to_ratio(own, 4, 3, yb=0.48)
    for w in (800, 1200): three(own43, 'baanrao-moo-krata-pan-pork-belly-4x3', w, HERO)
    blur(own43, 'baanrao-moo-krata-pan-pork-belly-4x3')
    og = to_ratio(own, 1200, 630, yb=0.45).resize((1200, 630), Image.LANCZOS)
    save(og, f'{OUT}/baanrao-moo-krata-pan-pork-belly-og-1200.jpg', 'jpg', 82, 200*KB, 60)
    # gallery / sets fallback (owner): 4:5 portrait
    card(to_ratio(own, 4, 5, yb=0.42), 'baanrao-moo-krata-pan-pork-belly-4x5')
    # ABOUT + gallery (owner): courtyard at dusk, string lights, lit logo sign
    card(load('courtyard-night.jpg'), 'baanrao-courtyard-dusk')
    # MENU sets (customer, Sasithonk): group table; crop away the street/people at the top
    st = crop(load('set-moo-krata.jpg'), (0, 0.225, 1, 0.98))
    st = to_ratio(st, 1, 1, yb=0.6)
    card(st, 'baanrao-moo-krata-set-table')
    jsonld(st, 'baanrao-moo-krata-set-table')
    # MENU (customer, Peaceii Keeratika): top-down spread; trim hands at the edges
    td = crop(load('peaceii-topdown-pan.jpg'), (0.06, 0.04, 0.94, 0.90))
    td = to_ratio(td, 4, 5)
    card(td, 'baanrao-moo-krata-spread-topdown')
    jsonld(td, 'baanrao-moo-krata-spread-topdown')
    # MENU (customer, hellosammy0601): charcoal stove + dipping sauce; crop out arms, legs and bottles
    sd = crop(load('hellosammy-dish-03.jpg'), (0.03, 0.205, 0.78, 1.0))
    sd = to_ratio(sd, 4, 5, yb=0.1)
    card(sd, 'baanrao-charcoal-stove-dipping-sauce')
    # MENU (customer, จีรศักดิ์ แหล้ยัง): som tam
    card(to_ratio(load('customer-food-02.jpg'), 4, 5, yb=0.45), 'baanrao-somtam-papaya-salad')
    # MENU (customer, อภิสิทธิ์ นวลปักษี): yam talay
    card(to_ratio(load('apisit-seafood-salad.jpg'), 4, 5, yb=0.62), 'baanrao-yam-talay-seafood-salad')
    # GALLERY (customer, hellosammy0601): pan on the charcoal stove; crop away diners' torsos
    card(crop(load('hellosammy-pan.jpg'), (0, 0.16, 0.86, 1.0)), 'baanrao-moo-krata-pan-charcoal-stove')
    # GALLERY venue (customer, จีรศักดิ์ แหล้ยัง): covered seating by day, venue confirmed by the owner via Lee
    card(load('customer-food-03.jpg'), 'baanrao-covered-seating-day')
    # ABOUT (owner, Facebook): the real night shot of the covered courtyard; promo sign removed and sky
    # cleaned up by the retouch bot. courtyard-night.jpg is actually daylight (EXIF 18:22, before sunset).
    night = Image.open('/workspace/baanrao/photos-clean/hero-new.jpg').convert('RGB')   # 1448x1086
    card(night, 'baanrao-dining-area-night-4x3')
    jsonld(night, 'baanrao-dining-area-night-4x3')   # 1200x900 for JSON-LD
    menu_cards()
    fb_r10()
    owner_drinks()
    owner_noodles()
    placeholders()
