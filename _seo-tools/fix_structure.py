#!/usr/bin/env python3
"""Batch 6: category breadcrumbs, music-tools additions, 404 page, long titles, contact guidance. Idempotent."""
import re, json, glob, os
BASE="https://audiotoolkit.github.io"
CATS={"audio-converters":("Audio Converters",["audio-converter","m4a-to-mp3","aac-to-mp3","wav-to-mp3","mp3-to-wav","flac-to-mp3","ogg-to-mp3","mp3-to-ogg","m4a-to-wav","mp4-to-wav","video-to-mp3"]),
 "audio-editing":("Audio Editing Tools",["audio-trimmer","audio-splitter","audio-merger","fade-in-out","audio-reverser","speed-changer","silence-remover","volume-booster","audio-compressor","audio-equalizer","sample-rate-converter","stereo-to-mono"]),
 "music-tools":("Music Tools",["ringtone-maker","bpm-detector","guitar-tuner","loop-maker","mp3-tag-editor","vocal-remover","waveform-image","metronome","white-noise-generator"]),
 "voice-audio-tools":("Voice &amp; Speech Tools",["voice-recorder","voice-to-text","text-to-speech"])}
def rd(f): return open(f,encoding="utf-8").read()
def wr(f,s): open(f,"w",encoding="utf-8").write(s)

# 1 add metronome + white noise cards to music-tools
s=rd("music-tools.html")
for t in ("metronome","white-noise-generator"):
    if f'href="{t}.html"' in s: continue
    p=rd(t+".html")
    title=re.search(r"<title>(.*?)</title>",p,re.S).group(1).replace(" | Audio Toolkit","").strip()
    d=re.search(r'<meta[^>]*name="description"[^>]*>',p).group(0); d=re.search(r'content="([^"]*)"',d).group(1)
    card=f'<a class="card" href="{t}.html"><h2>{title}</h2><p>{d}</p></a>'
    anchor=re.search(r'<a class="card" href="guitar-tuner.html">.*?</a>',s,re.S)
    s=s[:anchor.end()]+card+s[anchor.end():]
wr("music-tools.html",s)

# 2 breadcrumbs through category pages
n=0
for cat,(cname,tools) in CATS.items():
    for t in tools:
        f=t+".html"; s=rd(f)
        m=re.search(r'<div class="breadcrumb">(.*?)</div>',s,re.S)
        if not m or "audio-tools.html" in m.group(1): continue
        last=re.sub(r"<[^>]+>","",m.group(1).split("›")[-1]).strip()
        new=f'<div class="breadcrumb"><a href="/">Home</a> › <a href="audio-tools.html">Audio Tools</a> › <a href="{cat}.html">{cname}</a> › {last}</div>'
        s=s.replace(m.group(0),new,1)
        cu=re.search(r'<link[^>]*rel="canonical"[^>]*href="([^"]+)"',s) or re.search(r'<link[^>]*href="([^"]+)"[^>]*rel="canonical"',s)
        cu=cu.group(1)
        def fix(mm):
            try: j=json.loads(mm.group(2))
            except Exception: return mm.group(0)
            if isinstance(j,dict) and j.get("@type")=="BreadcrumbList":
                lastname=j["itemListElement"][-1]["name"]
                items=[("Home",BASE+"/"),("Audio Tools",BASE+"/audio-tools.html"),(re.sub("&amp;","&",cname),f"{BASE}/{cat}.html"),(lastname,cu)]
                j["itemListElement"]=[{"@type":"ListItem","position":i+1,"name":a,"item":b} for i,(a,b) in enumerate(items)]
                return mm.group(1)+"\n"+json.dumps(j,indent=2,ensure_ascii=False)+"\n</script>"
            return mm.group(0)
        s=re.sub(r'(<script type="application/ld\+json">)(.*?)</script>',fix,s,flags=re.S)
        wr(f,s); n+=1
print("breadcrumbs rewritten:",n)

# 3 long titles
for f,(old_re,new) in {"blog-is-online-audio-conversion-safe.html":(r"Is Online Audio Conversion Safe\? Privacy &amp; Browser Tools \| Audio Toolkit","Is Online Audio Conversion Safe? Privacy Explained | Audio Toolkit"),
                       "white-noise-generator.html":(r"White Noise Generator Online – Free Background Sound \| Audio Toolkit","White Noise Generator – Free Background Sound | Audio Toolkit")}.items():
    s=rd(f); s2=re.sub(old_re,new.replace("&","&amp;"),s); wr(f,s2); print(f,"changed" if s!=s2 else "UNCHANGED")

# 4 404 page
s=rd("404.html")
s=re.sub(r'\s*<link[^>]*rel="canonical"[^>]*>',"",s)
tools=[("Audio Trimmer","audio-trimmer"),("Audio Converter","audio-converter"),("M4A to MP3","m4a-to-mp3"),("Audio Merger","audio-merger"),("Volume Booster","volume-booster"),("Video to MP3","video-to-mp3")]
cats=[("Audio Converters","audio-converters"),("Audio Editing","audio-editing"),("Music Tools","music-tools"),("Voice &amp; Speech","voice-audio-tools"),("All Tools","audio-tools"),("Guides","blog")]
s=re.sub(r"<body>.*</body>",lambda m:'''<body>
<nav><a class="logo" href="/">Audio <span>Toolkit</span></a><a href="/audio-tools.html">Categories</a></nav>
<main>
<section class="hero">
<div class="hero-badge">404 Error</div>
<h1>4<span>0</span>4</h1>
<h2>This page wandered off.</h2>
<p>The page you're looking for doesn't exist or may have moved.</p>
<a class="btn-home" href="/">Back to Homepage</a>
</section>
<section>
<h2>Popular tools</h2>
<div class="tools-grid">
'''+"\n".join(f'<a class="tool-card" href="/{h}.html"><h3>{t}</h3></a>' for t,h in tools)+'''
</div>
<p class="cat-links">'''+" · ".join(f'<a href="/{h}.html">{t}</a>' for t,h in cats)+'''</p>
</section>
</main>
<footer><div class="footer-logo">Audio <span>Toolkit</span></div><a href="/audio-tools.html">Audio Tools</a></footer>
</body>''',s,flags=re.S)
s=s.replace("</style>",".tools-grid{max-width:760px}.cat-links{margin-top:22px;font-size:.92rem}.cat-links a{color:#7C3AED;font-weight:600;text-decoration:none}\n</style>",1) if ".cat-links" not in s else s
wr("404.html",s)

# 5 contact: bug-report guidance
s=rd("contact.html")
if "What to include" not in s:
    add='<p style="margin-top:24px;font-size:.9rem"><strong>What to include in a bug report:</strong> the tool name and page address, your browser and device (for example Chrome on Android), the file format and approximate size, and what you expected versus what happened. Please do not share private recordings; a short description of the file is enough.</p>\n'
    s=re.sub(r'(<p style="margin-top:24px;font-size:\.88rem)',lambda m:add+m.group(1),s,1); 
    print("contact guidance added" if "What to include" in s else "contact: anchor missing")
    wr("contact.html",s)
