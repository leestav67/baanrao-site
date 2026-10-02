#!/usr/bin/env bash
# Change the site's public address in every place it's used (canonical, og:url, og:image,
# twitter:image, JSON-LD in index.html). Run from the site folder:
#   tools/set-site-url.sh https://baanraomookata.netlify.app/
set -euo pipefail
NEW="${1:?usage: tools/set-site-url.sh https://new-address/}"
case "$NEW" in */) ;; *) NEW="$NEW/";; esac
cd "$(dirname "$0")/.."
OLD=$(grep -o '<link rel="canonical" href="[^"]*"' index.html | sed 's/.*href="//;s/"$//')
[ -n "$OLD" ] || { echo "canonical not found in index.html"; exit 1; }
python3 - "$OLD" "$NEW" <<'PY'
import sys; old,new=sys.argv[1],sys.argv[2]
for f in ["index.html"]:
    s=open(f,encoding="utf-8").read(); n=s.count(old)
    open(f,"w",encoding="utf-8").write(s.replace(old,new)); print(f"{f}: {n} replaced ({old} -> {new})")
PY
