#!/usr/bin/env python3
"""Batch 1: site-wide safe fixes. Idempotent. Usage: python3 tools/fix_common.py [repo_dir]"""
import re, glob, os, json, sys
ROOT = sys.argv[1] if len(sys.argv)>1 else "."
BASE = "https://audiotoolkit.github.io"
OG = BASE + "/assets/og-default.png"
stats = {}
def bump(k): stats[k]=stats.get(k,0)+1

TITLES = {
 "sample-rate-converter.html":("Sample Rate Converter – Change Audio Sample Rate Free | Audio Toolkit","Sample Rate Converter – Change Audio Sample Rate | Audio Toolkit"),
 "blog-is-online-audio-conversion-safe.html":("Is It Safe to Convert Audio Online? A Privacy Explainer | Audio Toolkit Blog","Is Online Audio Conversion Safe? Privacy Explained | Audio Toolkit"),
 "blog-mp3-bitrate-guide.html":("Best MP3 Bitrate for Music, Podcasts & Voice Memos | Audio Toolkit Blog","Best MP3 Bitrate for Music, Podcasts & Voice | Audio Toolkit"),
 "voice-to-text.html":("Voice to Text – Free Live Speech-to-Text Dictation | Audio Toolkit","Voice to Text – Free Live Speech-to-Text | Audio Toolkit"),
 "video-to-mp3.html":("Video to MP3 Converter – Extract Audio Free Online | Audio Toolkit","Video to MP3 Converter – Extract Audio Online | Audio Toolkit"),
 "silence-remover.html":("Silence Remover – Trim Silent Parts from Audio Free | Audio Toolkit","Silence Remover – Trim Silent Parts from Audio | Audio Toolkit"),
 "blog-audio-too-quiet.html":("Why Does My Audio Sound Quiet? Volume Boosting Explained | Audio Toolkit Blog","Why Is My Audio Quiet? How to Boost Volume | Audio Toolkit"),
 "volume-booster.html":("Volume Booster – Increase Audio Volume Online Free | Audio Toolkit","Volume Booster – Increase Audio Volume Online | Audio Toolkit"),
 "audio-trimmer.html":("Audio Trimmer & MP3 Cutter – Cut Audio Online Free | Audio Toolkit","Audio Trimmer & MP3 Cutter – Cut Audio Online | Audio Toolkit"),
 "blog-lossless-vs-lossy.html":("Lossless vs Lossy Audio: FLAC, WAV & MP3 Compared | Audio Toolkit Blog","Lossless vs Lossy Audio: FLAC, WAV & MP3 | Audio Toolkit"),
 "blog-remove-silence-podcast.html":("How to Remove Silence from a Podcast Automatically | Audio Toolkit Blog","How to Remove Silence from a Podcast | Audio Toolkit"),
 "mp3-tag-editor.html":("MP3 Tag Editor – Edit Song Title, Artist, Album Free | Audio Toolkit","MP3 Tag Editor – Edit Title, Artist & Album | Audio Toolkit"),
}
LABELS = {"bitrateSelect":"MP3 bitrate","startHandle":"Trim start position","endHandle":"Trim end position",
 "waveStyle":"Waveform style","waveSize":"Image size","waveColor":"Waveform color","volSlider":"Volume","voiceSelect":"Voice",
 "trebleSlider":"Treble","transcript":"Transcript","timerSelect":"Timer","timeSignature":"Time signature","textInput":"Text to speak",
 "targetLength":"Target length","strengthSlider":"Vocal reduction strength","startTime":"Start time","endTime":"End time",
 "splitPoints":"Split points","speedSlider":"Playback speed","sensSlider":"Sensitivity","repeatCount":"Number of repeats",
 "rateSlider":"Speech rate","pitchSlider":"Speech pitch","partCount":"Number of parts","midSlider":"Mid frequencies",
 "fieldYear":"Year","fieldTitle":"Title","fieldGenre":"Genre","fieldComment":"Comment","fieldArtist":"Artist","fieldAlbum":"Album",
 "fadeOutSlider":"Fade out duration","fadeInSlider":"Fade in duration","bpmSlider":"Beats per minute","boostSlider":"Volume boost",
 "bitrateSlider":"Bitrate","bgColor":"Background color","bassSlider":"Bass"}

def crumbs(s):
    m = re.search(r'<(?:nav|div|ol|p)[^>]*class="breadcrumb"[^>]*>(.*?)</(?:nav|div|ol|p)>', s, re.S)
    if not m: return None
    out=[]; inner=m.group(1)
    for a in re.finditer(r'<a href="([^"]*)"[^>]*>(.*?)</a>', inner, re.S):
        href=a.group(1); href = BASE+"/" if href in("/","index.html") else BASE+"/"+href.lstrip("/")
        out.append((re.sub(r"<[^>]+>","",a.group(2)).strip(), href))
    tail = re.sub(r"<[^>]+>"," ", re.sub(r'<a .*?</a>',"",inner,flags=re.S)).replace("&rsaquo;"," ").strip()
    return out, re.sub(r"\s+"," ",tail)

for f in sorted(glob.glob(os.path.join(ROOT,"*.html"))):
    n=os.path.basename(f); s=open(f,encoding="utf-8").read(); o=s
    if n=="vocal-reducer.html": continue  # redirect stub, left as is
    # 1 mobile nav: keep links visible
    s,c = re.subn(r"@media\s*\(max-width:\s*640px\)\s*\{\s*\.nav-links\s*\{\s*display:\s*none;?\s*\}\s*\}",
        "@media(max-width:640px){.nav-links{gap:14px}.nav-links a{font-size:.82rem}.logo{font-size:1.05rem}}", s)
    if c: bump("mobile-nav")
    # 2 meta keywords
    s,c = re.subn(r'<meta[^>]*name="keywords"[^>]*/?>\s*\n?', "", s)
    if c: bump("keywords-removed")
    # 3 home link variants
    s = s.replace('href="index.html#','href="/#').replace('href="index.html"','href="/"')
    # 4 titles
    if n in TITLES and TITLES[n][0] in s: s=s.replace(TITLES[n][0],TITLES[n][1]); bump("titles")
    # 5 social tags (not for 404)
    if n!="404.html":
        t=re.search(r"<title>(.*?)</title>",s,re.S).group(1).strip()
        d=re.search(r'<meta name="description" content="(.*?)"',s)
        d=d.group(1) if d else ""
        cm=re.search(r'<link[^>]*rel="canonical"[^>]*href="(.*?)"',s) or re.search(r'<link[^>]*href="([^"]*)"[^>]*rel="canonical"',s)
        if not cm: print("no canonical, skipped social/schema:",n); s=s if s!=o else s; open(f,"w",encoding="utf-8").write(s) if s!=o else None; continue
        cu=cm.group(1)
        add=[]
        has=lambda k: re.search(r'<meta[^>]*(?:property|name)="%s"'%re.escape(k),s)
        if not has("og:type"): add.append('<meta property="og:type" content="website" />')
        if not has("og:site_name"): add.append('<meta property="og:site_name" content="Audio Toolkit" />')
        if not has("og:title"): add.append(f'<meta property="og:title" content="{t}" />')
        if not has("og:description") and d: add.append(f'<meta property="og:description" content="{d}" />')
        if not has("og:url"): add.append(f'<meta property="og:url" content="{cu}" />')
        if not has("og:image"): add += [f'<meta property="og:image" content="{OG}" />','<meta property="og:image:width" content="1200" />','<meta property="og:image:height" content="630" />',f'<meta property="og:image:alt" content="Audio Toolkit – free online audio tools" />']
        if has("twitter:card"): s=re.sub(r'(<meta[^>]*content=")summary("[^>]*name="twitter:card")',r'\1summary_large_image\2',s)
        else: add.append('<meta name="twitter:card" content="summary_large_image" />')
        if not has("twitter:title"): add.append(f'<meta name="twitter:title" content="{t}" />')
        if not has("twitter:description") and d: add.append(f'<meta name="twitter:description" content="{d}" />')
        if not has("twitter:image"): add.append(f'<meta name="twitter:image" content="{OG}" />')
        if add:
            s=s.replace("</head>","\n".join(add)+"\n</head>",1) if False else re.sub(r'(<link[^>]*rel="canonical"[^>]*>)',lambda m:m.group(1)+"\n"+"\n".join(add),s,1); bump("social-tags")
        # 6 schema url/breadcrumb consistency
        def fix(m):
            try: j=json.loads(m.group(2))
            except Exception: return m.group(0)
            ch=False
            if isinstance(j,dict):
                if j.get("@type") in("SoftwareApplication","WebApplication") and j.get("url")!=cu: j["url"]=cu; ch=True
                if j.get("@type")=="BreadcrumbList":
                    items=j["itemListElement"]
                    if items[-1].get("item")!=cu:
                        cb=crumbs(s)
                        if cb and cb[0]:
                            links,last=cb; new=[{"@type":"ListItem","position":i+1,"name":nm,"item":u} for i,(nm,u) in enumerate(links)]
                            new.append({"@type":"ListItem","position":len(new)+1,"name":items[-1]["name"],"item":cu})
                            j["itemListElement"]=new
                        else: items[-1]["item"]=cu
                        ch=True
            if not ch: return m.group(0)
            bump("schema-fixed")
            return m.group(1)+"\n"+json.dumps(j,indent=2,ensure_ascii=False)+"\n"+"</script>"
        s=re.sub(r'(<script type="application/ld\+json">)(.*?)</script>',fix,s,flags=re.S)
    # 7 FAQ divs -> buttons
    s,c = re.subn(r'<div class="faq-q" onclick="this\.parentElement\.classList\.toggle\(\'open\'\)">(.*?)</div>',
        r'<button type="button" class="faq-q" aria-expanded="false" onclick="var p=this.parentElement;p.classList.toggle(\'open\');this.setAttribute(\'aria-expanded\',p.classList.contains(\'open\'))">\1</button>', s, flags=re.S)
    if c:
        bump("faq-buttons")
        s=s.replace("</style>","button.faq-q{width:100%;background:none;border:0;padding:0;text-align:left;font-family:inherit;color:inherit}\n.faq-q:focus-visible,.nav-links a:focus-visible,a:focus-visible{outline:2px solid var(--accent);outline-offset:2px}\n</style>",1)
    # 8 labels
    def lab(m):
        tag=m.group(0)
        if "aria-label" in tag or "aria-labelledby" in tag: return tag
        i=re.search(r'\bid="([^"]+)"',tag)
        if not i or re.search(r'<label[^>]+for="%s"'%re.escape(i.group(1)),s): return tag
        i=i.group(1)
        if i=="fileInput":
            text="Choose video file" if "video" in tag else "Choose audio file"
        elif i in LABELS: text=LABELS[i]
        else: return tag
        bump("aria-labels")
        return tag[:-1].rstrip("/ ").rstrip()+f' aria-label="{text}">' if not tag.endswith("/>") else tag[:-2].rstrip()+f' aria-label="{text}" />'
    s=re.sub(r"<(?:input|select|textarea)\b[^>]*>",lab,s)
    if s!=o: open(f,"w",encoding="utf-8").write(s)
print(stats)
