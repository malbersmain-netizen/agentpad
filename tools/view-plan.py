#!/usr/bin/env python3
"""Render BUILD.md into a styled, bench-friendly HTML page and open it.

BUILD.md stays the single source of truth -- this only presents it. Table rows in the
"Solder order" and shopping tables get clickable checkboxes so you can tick through the
build; ticks persist in localStorage, so closing the tab doesn't lose your place.

    mise exec -- python tools/view-plan.py
"""
import os, re, subprocess, webbrowser
import markdown

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC  = os.path.join(ROOT, "BUILD.md")
OUT  = os.path.join(ROOT, "build-plan.html")

html = markdown.markdown(
    open(SRC).read(),
    extensions=["tables", "fenced_code", "toc", "sane_lists"],
)

# Give every table row in a checklist-ish table a checkbox cell.
def add_checkboxes(m):
    body = m.group(0)
    n = [0]
    def row(mm):
        n[0] += 1
        return mm.group(0).replace("<tr>", f'<tr><td class="ck"><input type="checkbox" data-k="{n[0]}"></td>', 1)
    return re.sub(r"<tr>", lambda mm: row(mm), body)

CSS = """
:root { color-scheme: light dark; }
* { box-sizing: border-box; }
body {
  margin: 0; padding: 2rem 1.25rem 6rem;
  font: 16px/1.65 -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
  background: #faf9f6; color: #22252a;
  max-width: 62rem; margin-inline: auto;
}
h1 { font-size: 2rem; letter-spacing: -.02em; margin: 0 0 .3em; }
h2 { font-size: 1.35rem; margin: 2.4em 0 .6em; padding-bottom: .3em; border-bottom: 2px solid #e6e3da; }
h3 { font-size: 1.05rem; margin: 1.8em 0 .5em; color: #444; }
p, li { color: #33373d; }
code { background: #efece4; padding: .12em .38em; border-radius: 4px; font-size: .88em; }
pre { background: #22252a; color: #e8e6e1; padding: 1rem 1.1rem; border-radius: 10px; overflow-x: auto; }
pre code { background: none; color: inherit; padding: 0; }
blockquote {
  margin: 1.2em 0; padding: .85em 1.1em; border-left: 4px solid #d99a2b;
  background: #fdf6e7; border-radius: 0 8px 8px 0;
}
blockquote p { margin: 0; }
table { border-collapse: collapse; width: 100%; margin: 1.1em 0; font-size: .93rem; }
th, td { text-align: left; padding: .55em .7em; border-bottom: 1px solid #e6e3da; vertical-align: top; }
th { background: #f2efe7; font-weight: 700; }
tbody tr:hover { background: #f7f4ec; }
td.ck { width: 2.2rem; padding-right: 0; }
input[type=checkbox] { width: 1.05rem; height: 1.05rem; cursor: pointer; accent-color: #2f7d4f; }
tr.done td:not(.ck) { opacity: .42; text-decoration: line-through; }
strong { color: #14171b; }
hr { border: 0; border-top: 1px solid #e6e3da; margin: 2.4em 0; }
.bar {
  position: fixed; left: 0; right: 0; bottom: 0; background: #22252a; color: #e8e6e1;
  padding: .6rem 1rem; font-size: .85rem; display: flex; gap: 1rem; align-items: center;
  justify-content: center;
}
.bar button {
  background: #3a3f47; color: #e8e6e1; border: 0; padding: .35rem .8rem;
  border-radius: 6px; cursor: pointer; font: inherit;
}
.bar button:hover { background: #4a505a; }
@media (prefers-color-scheme: dark) {
  body { background: #16181c; color: #d8dae0; }
  h2 { border-color: #2c3038; } h3 { color: #aab; }
  p, li { color: #c7cad1; }
  code { background: #262a31; }
  th { background: #22262d; } th, td { border-color: #2c3038; }
  tbody tr:hover { background: #1d2127; }
  blockquote { background: #2a2418; border-color: #d99a2b; }
  strong { color: #f0f2f5; }
  hr { border-color: #2c3038; }
}
@media print { .bar { display: none; } body { padding: 0; } }
"""

JS = """
const KEY = 'agentpad-build-v1';
const saved = JSON.parse(localStorage.getItem(KEY) || '{}');
document.querySelectorAll('input[type=checkbox]').forEach((b, i) => {
  const id = b.closest('table').dataset.t + ':' + b.dataset.k;
  b.checked = !!saved[id];
  b.closest('tr').classList.toggle('done', b.checked);
  b.addEventListener('change', () => {
    saved[id] = b.checked;
    localStorage.setItem(KEY, JSON.stringify(saved));
    b.closest('tr').classList.toggle('done', b.checked);
  });
});
document.getElementById('reset').addEventListener('click', () => {
  localStorage.removeItem(KEY); location.reload();
});
"""

# tag tables so checkbox ids are stable per-table
idx = [0]
def tag(m):
    idx[0] += 1
    return f'<table data-t="{idx[0]}">'
html = re.sub(r"<table>", tag, html)
html = re.sub(r"<table[^>]*>.*?</table>", add_checkboxes, html, flags=re.S)

page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Agent Pad — build plan</title><style>{CSS}</style></head>
<body>{html}
<div class="bar"><span>Ticks save automatically in this browser</span>
<button id="reset">Reset checklist</button></div>
<script>{JS}</script></body></html>"""

open(OUT, "w").write(page)
print(OUT)
subprocess.run(["open", OUT], check=False)
