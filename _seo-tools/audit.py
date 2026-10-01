#!/usr/bin/env python3
"""Read-only static SEO/HTML audit for a flat GitHub Pages site.
Usage: python3 tools/audit.py [repo_dir] [base_url]
Writes AUDIT_REPORT.md and audit.csv into repo_dir. Never edits site files.
Static checks only: it does NOT run tools or test audio processing."""
import sys, re, json, csv, os, glob
from html.parser import HTMLParser
from urllib.parse import urlparse, urljoin
from collections import defaultdict

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
BASE = (sys.argv[2] if len(sys.argv) > 2 else "https://audiotoolkit.github.io").rstrip("/")

class P(HTMLParser):
    def __init__(s):
        super().__init__(convert_charrefs=True)
        s.title=""; s.in_title=False; s.meta={}; s.links=[]; s.canon=None; s.lang=None
        s.h=[]; s.cur=None; s.a=[]; s.scripts=[]; s.imgs=[]; s.ld=[]; s.in_ld=False
        s.skip=0; s.text=[]; s.div_onclick=0; s.inputs=[]; s.labels_for=set(); s.ids=set()
    def handle_starttag(s,t,a):
        d=dict(a)
        if "id" in d: s.ids.add(d["id"])
        if t=="html": s.lang=d.get("lang")
        elif t=="title": s.in_title=True
        elif t=="meta":
            k=d.get("name") or d.get("property")
            if k: s.meta[k.lower()]=d.get("content","")
        elif t=="link" and d.get("rel")=="canonical": s.canon=d.get("href")
        elif t=="a" and d.get("href") is not None: s.a.append(d["href"])
        elif t=="script":
            if d.get("type")=="application/ld+json": s.in_ld=True; s.ld.append("")
            elif d.get("src"): s.scripts.append(d)
            s.skip+=1
        elif t=="style": s.skip+=1
        elif t=="img": s.imgs.append(d)
        elif t in("h1","h2","h3","h4","h5","h6"): s.cur=[int(t[1]),""]
        elif t=="div" and "onclick" in d: s.div_onclick+=1
        elif t=="label" and d.get("for"): s.labels_for.add(d["for"])
        elif t in("input","select","textarea") and d.get("type") not in("hidden","submit","button"):
            s.inputs.append(d)
    def handle_endtag(s,t):
        if t=="title": s.in_title=False
        elif t=="script": s.in_ld=False; s.skip=max(0,s.skip-1)
        elif t=="style": s.skip=max(0,s.skip-1)
        elif s.cur and t==f"h{s.cur[0]}": s.h.append(tuple(s.cur)); s.cur=None
    def handle_data(s,x):
        if s.in_title: s.title+=x
        if s.in_ld and s.ld: s.ld[-1]+=x
        if s.cur is not None: s.cur[1]+=x
        if not s.skip: s.text.append(x)

files = sorted(glob.glob(os.path.join(ROOT,"**","*.html"), recursive=True))
files = [f for f in files if ".git"+os.sep not in f]
pages = {}
for f in files:
    p=P(); p.feed(open(f,encoding="utf-8",errors="replace").read()); pages[os.path.relpath(f,ROOT)]=p

def clean(u): return u.split("#")[0].split("?")[0]
issues=defaultdict(list); rows=[]
titles=defaultdict(list); descs=defaultdict(list)
for name,p in pages.items():
    I=issues[name]; title=p.title.strip(); desc=p.meta.get("description","").strip()
    titles[title].append(name); descs[desc].append(name)
    if not title: I.append("missing <title>")
    elif len(title)>65: I.append(f"title long ({len(title)} chars)")
    if not desc: I.append("missing meta description")
    elif len(desc)>165: I.append(f"description long ({len(desc)} chars)")
    if not p.canon: I.append("missing canonical")
    elif p.canon.rstrip("/")!=(BASE+"/"+name).rstrip("/") and not (name=="index.html" and p.canon.rstrip("/")==BASE):
        I.append(f"canonical differs from file URL: {p.canon}")
    if "noindex" in p.meta.get("robots",""): I.append("NOINDEX (excluded from sitemap)")
    if "viewport" not in p.meta: I.append("missing viewport")
    if not p.lang: I.append("missing html lang")
    h1=[x for x in p.h if x[0]==1]
    if len(h1)!=1: I.append(f"H1 count = {len(h1)}")
    prev=0
    for lvl,_ in p.h:
        if prev and lvl>prev+1: I.append(f"heading jump h{prev}->h{lvl}"); break
        prev=lvl
    for k in("og:title","og:description","og:url","og:image","twitter:card"):
        if k not in p.meta: I.append(f"missing {k}")
    if "keywords" in p.meta: I.append("meta keywords present (ignored by Google; safe to remove)")
    if "icon" not in "".join(p.meta) and False: pass
    # structured data
    for raw in p.ld:
        try: j=json.loads(raw)
        except Exception as e: I.append(f"JSON-LD invalid: {e}"); continue
        for o in (j if isinstance(j,list) else [j]):
            t=o.get("@type"); 
            if t in("SoftwareApplication","WebApplication") and o.get("url") and clean(o["url"]).rstrip("/")!=(p.canon or "").rstrip("/"):
                I.append(f"{t} schema url ({o['url']}) != canonical")
            if t=="BreadcrumbList":
                items=o.get("itemListElement",[])
                if items and clean(items[-1].get("item","")).rstrip("/")!=(p.canon or "").rstrip("/"):
                    I.append("Breadcrumb last item URL != this page's canonical")
    # links
    for h in p.a:
        if re.match(r"(https?:|mailto:|tel:|javascript:|#)",h) or not h: 
            if h.startswith(BASE): pass
            else: continue
        tgt=clean(urlparse(h).path if h.startswith("http") else h)
        if h.startswith("http"): tgt=tgt.lstrip("/")
        elif tgt.startswith("/"): tgt=tgt.lstrip("/")
        else: tgt=os.path.normpath(os.path.join(os.path.dirname(name),tgt))
        if tgt in("","."): continue
        if not os.path.exists(os.path.join(ROOT,tgt)): I.append(f"broken internal link: {h}")
    idx=[h for h in p.a if h.endswith("index.html") and "#" not in h or h=="index.html"]
    if idx: I.append("links to index.html (duplicate of '/'); prefer '/'")
    for s in p.scripts:
        src=s["src"]
        if src.startswith("http"):
            host=urlparse(src).netloc
            note=[]
            if "integrity" not in s: note.append("no SRI")
            if not re.search(r"@\d+\.\d+\.\d+",src): note.append("version not pinned")
            I.append(f"external script {host} ({', '.join(note) or 'ok'}) {src}")
    for im in p.imgs:
        if "alt" not in im: I.append(f"img missing alt: {im.get('src','?')[:40]}")
        if "width" not in im or "height" not in im: I.append(f"img missing width/height: {im.get('src','?')[:40]}")
    if p.div_onclick: I.append(f"{p.div_onclick} <div onclick> (not keyboard accessible; use <button>)")
    for d in p.inputs:
        if d.get("id") not in p.labels_for and "aria-label" not in d and "aria-labelledby" not in d:
            I.append(f"form control without label: {d.get('id') or d.get('type') or 'input'}")
    words=len(re.findall(r"\w+"," ".join(p.text)))
    if words<300 and name not in("404.html",): I.append(f"thin visible text (~{words} words)")
    rows.append([name,title,(h1[0][1].strip() if h1 else ""),desc,p.canon or "",words,len(I)])
for t,ns in titles.items():
    if t and len(ns)>1: [issues[n].append(f"duplicate title with {', '.join(x for x in ns if x!=n)}") for n in ns]
for t,ns in descs.items():
    if t and len(ns)>1: [issues[n].append(f"duplicate description with {', '.join(x for x in ns if x!=n)}") for n in ns]
# orphan check
linked=set()
for n,p in pages.items():
    for h in p.a:
        linked.add(os.path.basename(clean(h)))
for n in pages:
    if n!="index.html" and n not in linked: issues[n].append("orphan: no page links to it")
for extra in("robots.txt","sitemap.xml"):
    if not os.path.exists(os.path.join(ROOT,extra)): issues["(site)"].append(f"missing {extra}")
sm=os.path.join(ROOT,"sitemap.xml")
if os.path.exists(sm):
    urls=set(re.findall(r"<loc>(.*?)</loc>",open(sm).read()))
    for n,p in pages.items():
        u=(p.canon or "").strip()
        if "noindex" in p.meta.get("robots","") and u in urls: issues["(site)"].append(f"sitemap lists noindex page {n}")
        elif "noindex" not in p.meta.get("robots","") and n!="404.html" and u and u not in urls: issues["(site)"].append(f"sitemap missing {n}")
    for u in urls:
        if os.path.basename(urlparse(u).path) and not os.path.exists(os.path.join(ROOT,os.path.basename(urlparse(u).path))): issues["(site)"].append(f"sitemap lists nonexistent file {u}")
with open(os.path.join(ROOT,"audit.csv"),"w",newline="",encoding="utf-8") as fh:
    w=csv.writer(fh); w.writerow(["file","title","h1","description","canonical","words","issue_count"]); w.writerows(rows)
with open(os.path.join(ROOT,"AUDIT_REPORT.md"),"w",encoding="utf-8") as fh:
    fh.write(f"# Static audit ({len(pages)} pages)\n\nStatic HTML checks only. Tool functionality is NOT tested by this script.\n\n")
    for n in sorted(issues):
        if issues[n]: fh.write(f"## {n}\n"+"".join(f"- {i}\n" for i in issues[n])+"\n")
print(f"{len(pages)} pages, {sum(len(v) for v in issues.values())} findings -> AUDIT_REPORT.md, audit.csv")
