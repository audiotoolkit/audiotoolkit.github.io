#!/usr/bin/env python3
"""One header + one footer on every page, plus small head/markup fixes.
Run from the repo root:  python3 tools/apply_shell.py     (safe to re-run)
To change the menu or footer links edit NAV / FOOTER below and run it again."""
import glob, os, re

SKIP = {"vocal-reducer.html"}          # meta-refresh redirect stub, no layout
NAV = [("All Tools", "/#tools"), ("Categories", "audio-tools.html"), ("Blog", "blog.html"), ("About", "about.html"), ("Contact", "contact.html")]
FOOTER = [("Home", "/"), ("Audio Tools", "audio-tools.html"), ("Blog", "blog.html"), ("About", "about.html"),
          ("Privacy Policy", "privacy-policy.html"), ("Terms of Service", "terms-of-service.html"), ("Contact", "contact.html")]

def nav_html(page):
    li = "".join('<li><a href="%s"%s>%s</a></li>' % (h, ' aria-current="page"' if h == page else "", l) for l, h in NAV)
    return ('<nav class="site-nav" aria-label="Main">\n<a class="logo" href="/">Audio <span>Toolkit</span></a>\n'
            '<ul class="nav-links">%s</ul>\n</nav>' % li)

def footer_html():
    links = "\n".join('<a href="%s">%s</a>' % (h, l) for l, h in FOOTER)
    return ('<footer class="site-footer">\n<div class="footer-logo">Audio <span>Toolkit</span></div>\n'
            '<div class="footer-links">\n%s\n</div>\n<p>&copy; 2026 Audio Toolkit. All rights reserved.</p>\n</footer>' % links)

def main():
    os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    ref = open("aac-to-mp3.html", encoding="utf-8").read()
    favicon = re.search(r'<link[^>]*rel="icon"[^>]*>', ref).group(0)
    changed = 0
    for f in sorted(glob.glob("*.html")):
        if f in SKIP:
            continue
        s = o = open(f, encoding="utf-8").read()
        s = re.sub(r"<nav\b.*?</nav>", lambda m: nav_html(f), s, count=1, flags=re.S)
        s = re.sub(r"<footer\b.*?</footer>", lambda m: footer_html(), s, count=1, flags=re.S)
        if "/assets/shell.css" not in s:
            s = s.replace("</head>", '<link rel="stylesheet" href="/assets/shell.css">\n</head>', 1)
        if not re.search(r'rel="(shortcut )?icon"', s):
            s = s.replace("</head>", favicon + "\n</head>", 1)
        if "<main" not in s:                       # landmark around everything between nav and footer
            s = s.replace("</nav>", '</nav>\n<main id="main">', 1)
            s = s.replace("<footer class=\"site-footer\">", '</main>\n<footer class="site-footer">', 1)
        # heading order: the drop-zone / contact-card titles sit before any h2, make them h2 instead of h3
        s = re.sub(r'(<div class="upload-zone"[^>]*>(?:(?!</div>\s*</div>).)*?)<h3>(.*?)</h3>', lambda m: m.group(1) + "<h2>" + m.group(2) + "</h2>", s, count=1, flags=re.S)
        s = s.replace(".upload-zone h3{", ".upload-zone h2{")
        s = re.sub(r'(<a class="contact-card"[^>]*>(?:(?!</a>).)*?)<h3>(.*?)</h3>', lambda m: m.group(1) + "<h2>" + m.group(2) + "</h2>", s, flags=re.S) if f == "contact.html" else s
        if f == "contact.html":
            s = s.replace(".contact-card h3{", ".contact-card h2{")
        # wide tables scroll inside a box (avoid sideways page scroll on phones)
        if "<table" in s and 'class="table-scroll"' not in s:
            s = re.sub(r"(<table\b.*?</table>)", r'<div class="table-scroll">\1</div>', s, flags=re.S)
        if s != o:
            open(f, "w", encoding="utf-8").write(s); changed += 1
    print("updated %d page(s)" % changed)

main()
