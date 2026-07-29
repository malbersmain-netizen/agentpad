#!/usr/bin/env python3
"""Render every build document into one navigable HTML page and open it.

The markdown files stay the single source of truth -- this only presents them, in
reading order, with a sidebar and working cross-links. Figures live in schematics.html
(tools/schematic.py); this page links out to them.

    mise exec -- python tools/view-docs.py
"""
import os, re, subprocess, sys
import markdown

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT  = os.path.join(ROOT, "docs.html")

# reading order, not alphabetical
ORDER = [
    ("START-HERE.md",   "Start here",        "how the whole thing fits together"),
    ("WIRING.md",       "Wiring reference",  "every wire, every leg, every socket slot"),
    ("CONNECTIONS.md",  "Connections",       "the five moves the build is made of"),
    ("MULTIMETER.md",   "Multimeter",        "from zero, incl. the checks you repeat"),
    ("SOLDERING.md",    "Soldering",         "practice course, do this before the real board"),
    ("BUILD.md",        "Build manual",      "parts, board, pre-flight, then steps 1-7"),
    ("BREADBOARD.md",   "Breadboard",        "rebuild the working prototype (fallback)"),
    ("CLAUDE.md",       "Architecture",      "software side: hooks, daemon, protocol"),
]

CSS = """
:root{color-scheme:light dark;--fg:#22252a;--bg:#faf9f6;--mut:#666;--line:#e6e3da;--acc:#2f7d4f}
*{box-sizing:border-box}
body{margin:0;font:16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;
     background:var(--bg);color:var(--fg);display:flex}
nav{position:sticky;top:0;height:100vh;overflow-y:auto;flex:0 0 15rem;padding:1.5rem 1rem;
    border-right:1px solid var(--line);background:#fff}
nav h2{font-size:.72rem;letter-spacing:.09em;text-transform:uppercase;color:var(--mut);margin:1.4rem 0 .5rem}
nav a{display:block;padding:.32rem .5rem;border-radius:6px;color:var(--fg);text-decoration:none;font-size:.9rem}
nav a:hover{background:#eef6f0}
nav a.doc{font-weight:650}
nav a small{display:block;color:var(--mut);font-weight:400;font-size:.76rem;line-height:1.3}
main{flex:1;min-width:0;padding:2.5rem 3rem 6rem;max-width:60rem}
h1{font-size:1.9rem;margin:0 0 .3em;scroll-margin-top:1rem}
h2{font-size:1.35rem;margin:2.2em 0 .5em;padding-top:.4em;border-top:1px solid var(--line);scroll-margin-top:1rem}
h3{font-size:1.1rem;margin:1.8em 0 .4em}
h4{font-size:1rem;margin:1.5em 0 .3em;color:#333}
table{border-collapse:collapse;margin:1.1em 0;font-size:.9rem;display:block;overflow-x:auto;max-width:100%}
th,td{border:1px solid var(--line);padding:.42em .7em;text-align:left;vertical-align:top}
th{background:#f3f1ea;font-weight:650;white-space:nowrap}
code{background:#f0eee7;padding:.12em .35em;border-radius:4px;font-size:.87em}
pre{background:#20232a;color:#e6e6e6;padding:1em 1.1em;border-radius:8px;overflow-x:auto;line-height:1.45}
pre code{background:none;color:inherit;padding:0;font-size:.84rem}
blockquote{margin:1.2em 0;padding:.8em 1.1em;background:#eef6f0;border-left:4px solid var(--acc);border-radius:0 8px 8px 0}
blockquote p:first-child{margin-top:0}blockquote p:last-child{margin-bottom:0}
hr{border:0;border-top:1px solid var(--line);margin:2.5em 0}
.docwrap{padding-bottom:2rem}
.top{position:fixed;right:1.5rem;bottom:1.5rem;background:var(--acc);color:#fff;padding:.55em .9em;
     border-radius:999px;text-decoration:none;font-size:.85rem;box-shadow:0 2px 10px rgba(0,0,0,.18)}
.figlink{display:inline-block;margin:.4rem .5rem .4rem 0;padding:.45em .8em;background:var(--acc);
         color:#fff;border-radius:6px;text-decoration:none;font-size:.88rem;font-weight:600}
@media (prefers-color-scheme:dark){
  :root{--fg:#d8dae0;--bg:#16181c;--mut:#98a0ab;--line:#2b2f36}
  nav{background:#1b1e23}nav a{color:var(--fg)}nav a:hover{background:#22303a}
  th{background:#22262d}code{background:#252931}
  blockquote{background:#16241c}h4{color:#c4c8d0}
}
"""

def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

sections, navdoc = [], []
md = markdown.Markdown(extensions=["tables", "fenced_code", "sane_lists", "attr_list"])

for fname, title, blurb in ORDER:
    path = os.path.join(ROOT, fname)
    if not os.path.exists(path):
        continue
    md.reset()
    body = md.convert(open(path).read())
    # rewrite cross-links between the docs into in-page anchors
    for other, _, _ in ORDER:
        body = body.replace(f'href="{other}"', f'href="#{slug(other)}"')
    did = slug(fname)
    heads = re.findall(r'<h2[^>]*>(.*?)</h2>', body)
    def anchor(m):
        txt = re.sub("<[^>]+>", "", m.group(2))
        return f'<{m.group(1)} id="{did}--{slug(txt)}">{m.group(2)}</{m.group(1)}>'
    body = re.sub(r"<(h2|h3)[^>]*>(.*?)</\1>", anchor, body)
    subs = "".join(f'<a href="#{did}--{slug(re.sub("<[^>]+>","",h))}">'
                   f'{re.sub("<[^>]+>","",h)}</a>' for h in heads)
    navdoc.append(f'<a class="doc" href="#{did}">{title}<small>{blurb}</small></a>{subs}')
    sections.append(f'<section class="docwrap" id="{did}">{body}</section>')

page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Agent Pad — all build documentation</title><style>{CSS}</style></head><body>
<nav><h2>Read in this order</h2>{''.join(navdoc)}
<h2>Figures</h2>
<a href="schematics.html">Schematics &amp; board layout</a>
</nav>
<main>
<h1>Agent Pad — build documentation</h1>
<p style="color:var(--mut);margin-top:-.2em">Everything in reading order. Figures open separately:</p>
<p><a class="figlink" href="schematics.html">Schematics &amp; board layout</a></p>
{''.join(sections)}
</main>
<a class="top" href="#">↑ top</a>
</body></html>"""

open(OUT, "w").write(page)
print(OUT)
if "--no-open" not in sys.argv:
    subprocess.run(["open", "-a", "Google Chrome", OUT], check=False)
