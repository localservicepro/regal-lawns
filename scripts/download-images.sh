#!/usr/bin/env bash
# Downloads the Pexels stock images used on the site into /images so they can be
# self-hosted instead of hotlinked. Run from the repo root, then swap the
# images.pexels.com URLs in build/build.py (img_url) for /images/<key>-<w>.jpg.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 - <<'PY'
import sys, urllib.request, os
sys.path.insert(0, 'build')
import build
for key, (pid, credit, desc) in build.IMAGES.items():
    for w in (640, 1200, 1920):
        url = build.img_url(key, w)
        out = f"images/{key}-{w}.jpg"
        print("->", out, "from", url)
        urllib.request.urlretrieve(url, out)
PY
