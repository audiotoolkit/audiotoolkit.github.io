# Changes applied on top of your zip (2026-10-01)

Static checks only (HTML/JSON-LD/JS syntax, links, duplicates). Tools were NOT run in a real browser.

1. Mobile nav: links no longer hidden under 640px (49 pages).
2. Social tags: og:image (new assets/og-default.png, 1200x630), twitter:image, summary_large_image on all indexable pages. Meta keywords removed (44 pages).
3. Breadcrumbs: tool pages now Home > Audio Tools > Category > Tool (visible + BreadcrumbList schema, 35 pages). metronome and white-noise-generator added to music-tools.html.
4. Privacy wording made accurate per tool: index, about, privacy-policy (new microphone/speech section, jsDelivr/lamejs disclosed), text-to-speech (online voices labelled in the voice list).
5. Accessibility: FAQ questions are real <button aria-expanded> (35 pages); aria-labels on 76 unlabeled inputs; visible focus outline.
6. MP3 encoding (10 pages) now yields to the browser and shows "Converting... N%" so long files do not freeze the tab. Logic tested with a stub encoder only, not with real lamejs.
7. Internal links: 28 tool/blog pages got extra relevant related links (min 3); audio-tools.html got a "Common tasks" section.
8. Sitemap regenerated (54 URLs, noindex pages excluded, lastmod 2026-10-01). 404.html: no canonical, absolute links, popular tools + categories. contact.html: bug-report guidance. 2 long titles shortened. Home links use "/" instead of index.html.

Not done: real-browser tool testing, self-hosting lamejs (add SRI/own copy), h3-before-h2 in upload boxes (30 pages), cleanup of vocal-reducer.html redirect stub.
