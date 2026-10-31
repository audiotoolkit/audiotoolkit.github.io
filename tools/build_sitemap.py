#!/usr/bin/env python3
"""Rebuild sitemap.xml from the pages that exist (skips 404 and any noindex page).
Run from the repo root:  python3 tools/build_sitemap.py [YYYY-MM-DD]   (default lastmod = today)"""
import datetime, glob, os, re, sys
BASE = "https://audiotoolkit.github.io"
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
lastmod = sys.argv[1] if len(sys.argv) > 1 else datetime.date.today().isoformat()
urls = []
for f in sorted(glob.glob("*.html")):
    s = open(f, encoding="utf-8").read()
    if f == "404.html" or re.search(r'<meta[^>]*content="noindex[^"]*"[^>]*name="robots"|<meta[^>]*name="robots"[^>]*content="noindex', s):
        continue
    urls.append(BASE + "/" if f == "index.html" else BASE + "/" + f)
urls.sort(key=lambda u: (u != BASE + "/", u))
out = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
out += ["  <url><loc>%s</loc><lastmod>%s</lastmod></url>" % (u, lastmod) for u in urls]
out.append("</urlset>")
open("sitemap.xml", "w", encoding="utf-8").write("\n".join(out) + "\n")
print("sitemap.xml: %d URLs" % len(urls))
