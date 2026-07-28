#!/usr/bin/env python3
"""Regenerate BUILD.md's volatile tables from tools/layout.py.

Everything between a <!-- GEN:name --> / <!-- /GEN:name --> pair is replaced. Those
sections are the ones that kept drifting out of sync with the layout -- four times,
and the last time the wire table would have sent seven signal wires onto ground buses.
They are now derived, so they cannot disagree with the verifier.

    mise exec -- python tools/gen-tables.py
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from layout import *

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOC  = os.path.join(ROOT, "BUILD.md")

def rowplan():
    rows = {}
    def put(r, s): rows.setdefault(r, []).append(s)
    put(LED_ROWS[0], f"**LED anodes (+)** — each also takes that LED's wire to board B · cols {', '.join(map(str, LED_COLS))}")
    put(LED_ROWS[1], f"**LED cathodes (−)** — lead bends over on the copper face to the row-{RES_ROWS[0]} pad")
    put(RES_ROWS[0], f"220Ω top lead (the only thing in this hole)")
    put(RES_ROWS[1], f"220Ω bottom lead — lands on the bus")
    for r in GND_ROWS: put(r, f"**GND bus** — bare wire, cols 1 → {COLS}")
    put(BTN_ROWS[0], f"**Colored button signal legs** · cols {', '.join(str(c) for c in BTN_COL0)}")
    put(BTN_ROWS[1], f"**Colored button ground legs** · cols {', '.join(str(c+BIG_LEG_COLS) for c in BTN_COL0)}")
    put(ANS_ROWS[0], f"**AA / no / yes signal legs** · cols {', '.join(map(str, ANS_COL0))}")
    put(ANS_ROWS[1], f"**AA / no / yes ground legs** · cols {', '.join(str(c+SMALL_LEG) for c in ANS_COL0)}")
    out = ["| Row | What |", "|---:|---|"]
    for r in sorted(rows):
        out.append(f"| **{r}** | " + " · ".join(rows[r]) + " |")
    out.append("")
    out.append(f"The {len(GND_ROWS)} GND buses join together down **column {GND_LINK_COL}**.")
    out.append("")
    used = set(LED_ROWS)|set(RES_ROWS)|set(BTN_ROWS)|set(ANS_ROWS)|set(GND_ROWS)
    body = set(range(RES_ROWS[0], RES_ROWS[1]+1)) | set(range(BTN_ROWS[0], BTN_ROWS[1]+1)) \
         | set(range(ANS_ROWS[0], ANS_ROWS[1]+1)) | set(range(LED_ROWS[0], LED_ROWS[1]+1))
    truly = sorted(set(range(1, ROWS+1)) - used - body)
    out.append(f"Genuinely free rows (no lead *and* no component body above them): "
               f"**{', '.join(map(str, truly)) or 'none'}**.")
    return "\n".join(out)

def wiretable():
    h = harness()
    out = [f"**{len(h)} wires from board A to board B.** Each one's far end solders to the pad of "
           f"the header pin it serves.", "",
           "| # | Signal | From — board A hole | To — ESP32 pin | Header side | Position |",
           "|---:|---|---|---|---|---:|"]
    for i, (lbl, src, pin, side, pos) in enumerate(h, 1):
        out.append(f"| {i} | {lbl} | {src} | **{pin}** | {side} | {pos} |")
    out += ["", f"Plus the LCD's **{len(LCD_PINS)}** wires, which go to board B directly and never "
                f"touch board A:", "",
            "| Signal | From | To — ESP32 pin |", "|---|---|---|"]
    for a, b in LCD_PINS:
        out.append(f"| LCD {a} | F-M jumper onto the LCD's own header | **{b}** |")
    left  = sum(1 for *_ , s, p in h if s == "LEFT")
    right = len(h) - left
    out += ["", f"That is **{left} on the left column, {right} on the right**, plus "
                f"{len(LCD_PINS)} LCD wires — **{len(h)+len(LCD_PINS)} arriving at board B** in total.",
            "", "> **Never wire to RX0 or TX0** (right column, positions 12–13). Those carry the USB "
                "serial link; touching them breaks uploads *and* the daemon, and looks like a dead board."]
    return "\n".join(out)

def joints():
    hdr = 2 * (HDR_COLS[1]-HDR_COLS[0]+1)
    bus = len(GND_ROWS)*8 + 6
    comp = len(LED_COLS)*2 + len(LED_COLS)*2 + len(BTN_COL0)*4 + len(ANS_COL0)*4
    a = bus + comp + len(harness())
    return "\n".join([
        "| Board | Joints | What |", "|---|---:|---|",
        f"| A | ~{a} | {bus} bus + {comp} component legs + {len(harness())} wire ends |",
        f"| B | {hdr} | two {HDR_COLS[1]-HDR_COLS[0]+1}-socket strips; {len(harness())+len(LCD_PINS)} of those pads also take a wire |",
        f"| **total** | **~{a+hdr}** | at 1–2 min each including inspection, that is **3–5 hours** |",
    ])

SECTIONS = {"rowplan": rowplan, "wiretable": wiretable, "joints": joints}

doc = open(DOC).read()
changed = []
for name, fn in SECTIONS.items():
    pat = re.compile(rf"<!-- GEN:{name} -->.*?<!-- /GEN:{name} -->", re.S)
    if not pat.search(doc):
        print(f"  ! no <!-- GEN:{name} --> markers in BUILD.md — skipped")
        continue
    doc = pat.sub(f"<!-- GEN:{name} -->\n" + fn().replace("\\", "\\\\") + f"\n<!-- /GEN:{name} -->", doc)
    changed.append(name)
open(DOC, "w").write(doc)
print("regenerated:", ", ".join(changed) if changed else "nothing")
