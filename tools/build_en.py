#!/usr/bin/env python3
"""Generate /en/index.html from index.html and keep absolute URLs in sync.

index.html is the source of truth for copy: Thai is the element text, English is
in data-en / data-en-ph / data-en-alt / data-en-aria / data-en-title.

The public origin lives in tools/site-base-url.txt (one line, no trailing slash).
Run:  python3 tools/build_en.py [site_dir]
"""
import os
import re
import sys
from html.parser import HTMLParser

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


class Spans(HTMLParser):
    """(inner_start, inner_end, english) for every element that has data-en."""

    def __init__(self, src):
        super().__init__(convert_charrefs=False)
        self.src = src
        self.lines = [0]
        for match in re.finditer("\n", src):
            self.lines.append(match.end())
        self.stack = []
        self.spans = []

    def off(self):
        line, col = self.getpos()
        return self.lines[line - 1] + col

    def handle_starttag(self, tag, attrs):
        if tag in VOID:
            return
        start = self.off()
        end = start + len(self.get_starttag_text())
        english = dict(attrs).get("data-en")
        self.stack.append((tag, end, english))

    def handle_endtag(self, tag):
        while self.stack:
            open_tag, inner_start, english = self.stack.pop()
            if open_tag == tag:
                if english is not None:
                    self.spans.append((inner_start, self.off(), english))
                break


def site_base(site):
    path = os.path.join(site, "tools", "site-base-url.txt")
    lines = [ln.strip() for ln in open(path, encoding="utf-8") if ln.strip() and not ln.strip().startswith("#")]
    if len(lines) != 1 or not lines[0].startswith("https://"):
        raise SystemExit("tools/site-base-url.txt must contain one https origin, with no trailing slash")
    base = lines[0].rstrip("/")
    if "example" + ".com" in base:
        raise SystemExit("site base URL still uses the placeholder host")
    return base


def sync_origin(site, base):
    """Copy the origin from tools/site-base-url.txt into the files that publish it."""
    index_path = os.path.join(site, "index.html")
    html = open(index_path, encoding="utf-8").read()
    found = re.search(r'<meta name="site-base-url" content="([^"]+)">', html)
    if not found:
        raise SystemExit('index.html is missing <meta name="site-base-url">')
    old = found.group(1).rstrip("/")
    if old != base:
        html = html.replace(old, base)
        open(index_path, "w", encoding="utf-8").write(html)
        print(f"index.html: {old} -> {base}")
    for name in ("robots.txt", "sitemap.xml", "llms.txt"):
        path = os.path.join(site, name)
        if not os.path.exists(path):
            continue
        text = open(path, encoding="utf-8").read()
        if old != base and old in text:
            open(path, "w", encoding="utf-8").write(text.replace(old, base))
            print(f"{name}: {old} -> {base}")
    return html if old == base else open(index_path, encoding="utf-8").read()


def write_sitemap(site, base):
    today = "2026-10-04"
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xhtml="http://www.w3.org/1999/xhtml">
  <url>
    <loc>{base}/</loc>
    <lastmod>{today}</lastmod>
    <xhtml:link rel="alternate" hreflang="th" href="{base}/"/>
    <xhtml:link rel="alternate" hreflang="en" href="{base}/en/"/>
    <xhtml:link rel="alternate" hreflang="x-default" href="{base}/"/>
  </url>
  <url>
    <loc>{base}/en/</loc>
    <lastmod>{today}</lastmod>
    <xhtml:link rel="alternate" hreflang="th" href="{base}/"/>
    <xhtml:link rel="alternate" hreflang="en" href="{base}/en/"/>
    <xhtml:link rel="alternate" hreflang="x-default" href="{base}/"/>
  </url>
</urlset>
"""
    open(os.path.join(site, "sitemap.xml"), "w", encoding="utf-8").write(xml)


def write_robots(site, base):
    text = f"""# robots.txt for บ้านเราหมูกระทะ · Baan Rao Moo Krata
# owner.html is kept out of search with <meta name="robots" content="noindex"> plus an
# X-Robots-Tag header (see _headers). It is NOT disallowed here, because a Disallow would
# stop Google from ever seeing that noindex.
User-agent: *
Allow: /

Sitemap: {base}/sitemap.xml
"""
    open(os.path.join(site, "robots.txt"), "w", encoding="utf-8").write(text)


def stamp_llms(site, base):
    path = os.path.join(site, "llms.txt")
    text = open(path, encoding="utf-8").read()
    text = text.replace("{{SITE_URL}}", base)
    open(path, "w", encoding="utf-8").write(text)


def swap_attr(html, attr, data_attr):
    """Replace attr=\"...\" with the value of a sibling data_attr, any order."""
    pattern = re.compile(
        r"(<[a-zA-Z][^>]*?\s" + attr + r'=")([^"]*)(")([^>]*?\s' + data_attr + r'=")([^"]*)(")'
        r"|"
        r"(<[a-zA-Z][^>]*?\s" + data_attr + r'=")([^"]*)(")([^>]*?\s' + attr + r'=")([^"]*)(")'
    )

    def repl(match):
        if match.group(1) is not None:
            return match.group(1) + match.group(5) + match.group(3) + match.group(4) + match.group(5) + match.group(6)
        return match.group(7) + match.group(8) + match.group(9) + match.group(10) + match.group(8) + match.group(12)

    return pattern.sub(repl, html)


def up_one_level(html):
    """en/index.html lives one folder down: point local assets at ../ (relative, so the page works both
    on the web server and when opened from the unzipped folder via file://). Absolute https URLs
    (canonical, hreflang, og, JSON-LD) are untouched."""
    html = re.sub(r'((?:src|href|poster|data-src)=")(?=(?:images|css|js|fonts|videos)/)', r"\1../", html)

    def fix_srcset(match):
        return re.sub(r'(^|,\s*|")(?=(?:images|videos)/)', r"\1../", match.group(0))

    out = re.sub(r'(?:srcset|imagesrcset)="[^"]*"', fix_srcset, html)
    left = re.findall(r'(?:src|href|poster|data-src|srcset)="/(?!/)[^"]*"', out)
    if left:
        raise SystemExit("en/index.html still has root-relative paths: " + ", ".join(left[:5]))
    return out


def check_markup(html):
    """Fail the build on the kind of damage a bad regex replacement leaves behind (e.g. a literal \\1
    where a <symbol …> tag used to be), and on icons used with <use href="#…"> but never defined."""
    stray = re.search(r"(?m)^\s*\\[0-9g]", html) or re.search(r"\\[1-9](?= viewBox=)", html)
    if stray:
        raise SystemExit("index.html has a literal regex back-reference: " + html[stray.start():stray.start() + 60])
    defined = set(re.findall(r'<symbol id="([^"]+)"', html))
    missing = sorted(set(re.findall(r'<use href="#([^"]+)"', html)) - defined)
    if missing:
        raise SystemExit("index.html uses undefined SVG icons: " + ", ".join(missing))


def build(site):
    base = site_base(site)
    # Photo blocks, JSON-LD image arrays and og:image come from tools/photos.py (one config list).
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    sys.dont_write_bytecode = True
    import photos
    photos.apply(site, base)
    src = sync_origin(site, base)
    check_markup(src)
    placeholder_host = "example" + ".com"
    if placeholder_host in src:
        raise SystemExit("index.html still contains the placeholder host")
    parser = Spans(src)
    parser.feed(src)
    spans = sorted(parser.spans, key=lambda item: (item[0], -item[1]))
    keep = []
    last_end = -1
    for span in spans:
        if span[0] >= last_end:
            keep.append(span)
            last_end = span[1]
    out = src
    for start, end, english in reversed(keep):
        # Attribute values are decoded, so a bare "&" must be escaped again. Tags stay.
        english = re.sub(r"&(?!(?:[a-zA-Z]+|#[0-9]+|#x[0-9a-fA-F]+);)", "&amp;", english)
        out = out[:start] + english + out[end:]
    out = swap_attr(out, "placeholder", "data-en-ph")
    out = swap_attr(out, "alt", "data-en-alt")
    out = swap_attr(out, "aria-label", "data-en-aria")
    out = swap_attr(out, "title", "data-en-title")
    head_path = os.path.join(site, "tools", "head-en.html")
    en_head = open(head_path, encoding="utf-8").read().replace("{{SITE_URL}}", base).strip()
    swapped = re.sub(r"<!-- SEO:BEGIN -->.*?<!-- SEO:END -->", lambda _m: en_head, out, count=1, flags=re.S)
    if swapped == out:
        raise SystemExit("index.html is missing the <!-- SEO:BEGIN --> / <!-- SEO:END --> markers")
    out = swapped
    if '<html lang="th"' not in out:
        raise SystemExit('index.html has no <html lang="th" ...> tag')
    out = out.replace('<html lang="th"', '<html lang="en"', 1)   # keeps class="no-line"
    th_toggle = '<a href="./" hreflang="th" lang="th" class="on" aria-current="page">TH</a><a href="en/" hreflang="en" lang="en">EN</a>'
    if th_toggle not in out:
        raise SystemExit("index.html language toggle not found (expected the relative ./ and en/ links)")
    out = out.replace(th_toggle,
        '<a href="../" hreflang="th" lang="th">TH</a><a href="./" hreflang="en" lang="en" class="on" aria-current="page">EN</a>')
    out = up_one_level(out)
    if placeholder_host in out or "{{SITE_URL}}" in out:
        raise SystemExit("generated English page still has a placeholder URL")
    en_dir = os.path.join(site, "en")
    os.makedirs(en_dir, exist_ok=True)
    open(os.path.join(en_dir, "index.html"), "w", encoding="utf-8").write(out)
    write_sitemap(site, base)
    write_robots(site, base)
    stamp_llms(site, base)
    print(f"en/index.html written: {len(keep)} text blocks translated ({base})")


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else ".")
