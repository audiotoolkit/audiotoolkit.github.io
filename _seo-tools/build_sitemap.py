#!/usr/bin/env python3
"""Regenerate sitemap.xml from local HTML files: canonical URLs only, skips noindex and 404.
Usage: python3 tools/build_sitemap.py [repo_dir] [base_url]
lastmod comes from the last git commit date of each file (omitted if git unavailable)."""
import sys, os, re, glob, subprocess
ROOT=sys.argv[1] if len(sys.argv)>1 else "."
BASE=(sys.argv[2] if len(sys.argv)>2 else "https://audiotoolkit.github.io").rstrip("/")
out=[]
for f in sorted(glob.glob(os.path.join(ROOT,"*.html"))):
    n=os.path.basename(f); s=open(f,encoding="utf-8",errors="replace").read()
    if n=="404.html" or re.search(r'<meta[^>]+robots[^>]+noindex',s,re.I): continue
    m=re.search(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)',s) or re.search(r'<link[^>]+href=["\']([^"\']+)["\'][^>]+rel=["\']canonical',s)
    url=m.group(1) if m else (BASE+"/" if n=="index.html" else f"{BASE}/{n}")
    try: d=subprocess.check_output(["git","log","-1","--format=%cs","--",n],cwd=ROOT,stderr=subprocess.DEVNULL,text=True).strip()
    except Exception: d=""
    out.append((url,d))
seen=set(); lines=['<?xml version="1.0" encoding="UTF-8"?>','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for u,d in out:
    if u in seen: continue
    seen.add(u); lines.append(f"  <url><loc>{u}</loc>"+(f"<lastmod>{d}</lastmod>" if d else "")+"</url>")
lines.append("</urlset>")
open(os.path.join(ROOT,"sitemap.xml"),"w").write("\n".join(lines)+"\n")
print(len(seen),"URLs written to sitemap.xml")
