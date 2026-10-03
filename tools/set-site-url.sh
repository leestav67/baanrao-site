#!/usr/bin/env bash
# Change the site's public address everywhere it is published:
# index.html (canonical, og:url, og:image, twitter:image, JSON-LD),
# tools/site-base-url.txt (what the Netlify build reads), robots.txt, sitemap.xml, llms.txt.
# Then regenerates /en/. Run from anywhere:
#   tools/set-site-url.sh https://baanraomookata.netlify.app/
set -euo pipefail
NEW="${1:?usage: tools/set-site-url.sh https://new-address/}"
NEW="${NEW%/}"
case "$NEW" in
  https://*) ;;
  *) echo "address must start with https://"; exit 1 ;;
esac
cd "$(dirname "$0")/.."
OLD=$(grep -o '<link rel="canonical" href="[^"]*"' index.html | head -1 | sed 's/.*href="//;s/"$//;s:/$::')
[ -n "$OLD" ] || { echo "canonical not found in index.html"; exit 1; }
if [ "$OLD" = "$NEW" ]; then
  echo "already $NEW"
else
  python3 - "$OLD" "$NEW" <<'PY'
import sys
old, new = sys.argv[1], sys.argv[2]
for f in ("index.html", "robots.txt", "sitemap.xml", "llms.txt"):
    try:
        s = open(f, encoding="utf-8").read()
    except FileNotFoundError:
        print(f"{f}: skipped")
        continue
    n = s.count(old)
    open(f, "w", encoding="utf-8").write(s.replace(old, new))
    print(f"{f}: {n} replaced ({old} -> {new})")
path = "tools/site-base-url.txt"
lines = open(path, encoding="utf-8").read().splitlines(keepends=True)
out, replaced = [], False
for ln in lines:
    stripped = ln.strip()
    if stripped and not stripped.startswith("#") and not replaced:
        out.append(new + ("\n" if ln.endswith("\n") else ""))
        replaced = True
    else:
        out.append(ln)
if not replaced:
    if out and not out[-1].endswith("\n"):
        out[-1] += "\n"
    out.append(new + "\n")
open(path, "w", encoding="utf-8").write("".join(out))
print(f"{path}: origin set to {new}")
PY
fi
python3 tools/build_en.py .
