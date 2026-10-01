#!/usr/bin/env python3
"""Batch 3: make encodeMp3 yield to the browser and report progress, so long files don't freeze the tab. Idempotent."""
import re, glob
done=[]
for f in sorted(glob.glob("*.html")):
    s=open(f,encoding="utf-8").read()
    if "function encodeMp3(" not in s or "async function encodeMp3" in s: continue
    assert s.count("encodeMp3(")==2 and "statusMsg" in s, f
    ci=s.index("= encodeMp3(")
    st=s.rfind("setTimeout(() => {",0,ci); assert st>0, f
    s=s[:st]+"setTimeout(async () => {"+s[st+len("setTimeout(() => {"):]
    s=s.replace("= encodeMp3(","= await encodeMp3(",1)
    s=s.replace("function encodeMp3(buffer, kbps) {","async function encodeMp3(buffer, kbps) {",1)
    pat=re.compile(r"(if \(mp3buf\.length > 0\) mp3Data\.push\(mp3buf\);)(\s*\}\s*const end = mp3encoder\.flush\(\);)")
    assert pat.search(s), f
    ins=("\nif ((i / sampleBlockSize) % 300 === 299) {\n"
         "statusMsg.textContent = 'Converting\u2026 ' + Math.min(99, Math.round(i / left16.length * 100)) + '%';\n"
         "await new Promise(function (r) { setTimeout(r, 0); });\n}")
    s=pat.sub(lambda m:m.group(1)+ins+m.group(2),s,1)
    open(f,"w",encoding="utf-8").write(s); done.append(f)
print(len(done),done)
