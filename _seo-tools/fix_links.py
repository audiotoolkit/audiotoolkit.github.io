#!/usr/bin/env python3
"""Batch 4: add relevant internal links to pages with fewer than 3. Idempotent (skips links already present)."""
import re
idx=open("index.html",encoding="utf-8").read()
info={}
for m in re.finditer(r'<a [^>]*class="tool-card"[^>]*>(.*?)</a>',idx,re.S):
    h=re.search(r'href="([^"]+\.html)"',m.group(0)); t=re.search(r"<h3>(.*?)</h3>",m.group(1),re.S); d=re.search(r"<p>(.*?)</p>",m.group(1),re.S)
    if h and t and d: info[h.group(1)]=(re.sub(r"<[^>]+>","",t.group(1)).strip(),re.sub(r"<[^>]+>","",d.group(1)).strip())
tools={"audio-compressor":["audio-trimmer","mp3-tag-editor","audio-converter"],"audio-equalizer":["volume-booster","audio-compressor","audio-trimmer"],
"audio-merger":["audio-trimmer","fade-in-out","audio-converter"],"audio-reverser":["audio-trimmer","loop-maker","speed-changer"],
"bpm-detector":["metronome","loop-maker","audio-trimmer"],"guitar-tuner":["metronome","voice-recorder","bpm-detector"],
"loop-maker":["audio-trimmer","bpm-detector","fade-in-out"],"metronome":["bpm-detector","guitar-tuner","loop-maker"],
"mp3-tag-editor":["audio-converter","audio-compressor","audio-trimmer"],"ringtone-maker":["audio-trimmer","fade-in-out","volume-booster"],
"sample-rate-converter":["audio-converter","audio-compressor","stereo-to-mono"],"silence-remover":["audio-trimmer","audio-splitter","volume-booster"],
"speed-changer":["audio-trimmer","loop-maker","audio-reverser"],"stereo-to-mono":["audio-compressor","audio-converter","volume-booster"],
"text-to-speech":["voice-recorder","audio-converter","voice-to-text"],"vocal-remover":["audio-trimmer","audio-equalizer","bpm-detector"],
"voice-recorder":["audio-trimmer","volume-booster","voice-to-text"],"voice-to-text":["voice-recorder","text-to-speech","audio-trimmer"],
"volume-booster":["audio-compressor","audio-trimmer","audio-equalizer"],"waveform-image":["audio-trimmer","audio-converter","audio-merger"]}
blogs={"blog-audio-too-quiet":["volume-booster","audio-compressor"],"blog-free-ringtone-from-song":["ringtone-maker","audio-trimmer","fade-in-out"],
"blog-iphone-voice-memos-to-mp3":["m4a-to-mp3","audio-trimmer","audio-compressor"],"blog-is-online-audio-conversion-safe":["audio-converter","audio-trimmer"],
"blog-lossless-vs-lossy":["audio-converter","wav-to-mp3"],"blog-m4a-vs-mp3":["m4a-to-mp3","audio-trimmer","wav-to-mp3"],
"blog-mp3-bitrate-guide":["audio-compressor","wav-to-mp3","audio-converter"],"blog-remove-silence-podcast":["silence-remover","audio-trimmer","audio-merger"]}
n=0
for page,cands in tools.items():
    f=page+".html"; s=open(f,encoding="utf-8").read()
    body=s[s.find("</nav>"):s.find("<footer")]
    have={h for h in re.findall(r'href="([a-z0-9-]+)\.html',body)}|{page}
    m=re.search(r'(<div class="related-grid">)(.*?)(</div>\s*(?:</section>|</div>|</main>))',s,re.S)
    if not m: print("no related-grid",f); continue
    add=""
    cnt=len({h for h in re.findall(r'href="([a-z0-9-]+)\.html',m.group(2))})
    for c in cands:
        if cnt>=3: break
        if c in have: continue
        nm,ds=info[c+".html"]; add+=f'\n<a href="{c}.html" class="related-card"><h3>{nm}</h3><p>{ds}</p></a>'; have.add(c); cnt+=1
    if add: s=s[:m.end(2)]+add+"\n"+s[m.end(2):]; open(f,"w",encoding="utf-8").write(s); n+=1
for page,cands in blogs.items():
    f=page+".html"; s=open(f,encoding="utf-8").read()
    if "Related tools:" in s: continue
    have=set(re.findall(r'href="([a-z0-9-]+)\.html',s[s.find("</nav>"):s.find("<footer")]))
    links=[f'<a href="{c}.html">{info[c+".html"][0]}</a>' for c in cands if c not in have]
    if not links: continue
    s=s.replace("</article>",f'<p><strong>Related tools:</strong> {" · ".join(links[:3])}</p>\n</article>',1); open(f,"w",encoding="utf-8").write(s); n+=1
print("pages updated:",n)
