#!/usr/bin/env python3
"""Full schematic + board layout + step-by-step solder figures, generated from the
same layout data that tools/verify-layout.py checks.

    mise exec -- python tools/schematic.py
"""
import os, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT  = os.path.join(ROOT, "schematics.html")
FF = 'font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif"'

P = 2.54
ROWS, COLS = 18, 24
COLS_MAIN = [3, 9, 15, 21]
COLS_RES  = [5, 11, 17, 23]
COLS_ANS  = [4, 12, 20]
LEDC  = ["#c0392b", "#27823b", "#1f6fb4", "#b8860b"]
LEDN  = ["red", "green", "blue", "yellow"]
LED_GPIO = [13, 14, 27, 26]
BTN_GPIO = [32, 33, 25, 4]
ANS   = [("AA", 23, "#8a5a12"), ("no", 18, "#333"), ("yes", 19, "#0f6b52")]
HEADER_ROWS = (2, 12)
GND_ROWS = (5, 16)
BUS5V_ROW = 18

# =====================================================================  SCHEMATIC
def schematic():
    W, H = 1120, 720
    o = [f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" {FF}>']
    o.append(f'<rect width="{W}" height="{H}" fill="#fff"/>')
    # ESP32 block
    ex, ey, ew, eh = 60, 90, 190, 520
    o.append(f'<rect x="{ex}" y="{ey}" width="{ew}" height="{eh}" rx="6" fill="none" stroke="#222" stroke-width="2"/>')
    o.append(f'<text x="{ex+ew/2}" y="{ey-14}" text-anchor="middle" font-size="15" font-weight="700" fill="#222">ESP32-WROOM-32</text>')

    pins = ([("VIN", "#c0392b")] + [(f"GPIO {g}", LEDC[i]) for i, g in enumerate(LED_GPIO)]
            + [(f"GPIO {g}", LEDC[i]) for i, g in enumerate(BTN_GPIO)]
            + [(f"GPIO {g}", c) for _, g, c in ANS]
            + [("GPIO 21", "#e08000"), ("GPIO 22", "#7a4a10"), ("GND", "#111")])
    py = {}
    for i, (lab, col) in enumerate(pins):
        y = ey + 26 + i*33
        py[lab] = y
        o.append(f'<line x1="{ex+ew}" y1="{y}" x2="{ex+ew+26}" y2="{y}" stroke="{col}" stroke-width="2"/>')
        o.append(f'<text x="{ex+ew-8}" y="{y+4}" text-anchor="end" font-size="12" fill="#222">{lab}</text>')

    # rails
    gnd_y, v5_y = H-52, 62
    o.append(f'<line x1="300" y1="{gnd_y}" x2="{W-40}" y2="{gnd_y}" stroke="#111" stroke-width="3"/>')
    o.append(f'<text x="{W-36}" y="{gnd_y+4}" font-size="13" font-weight="700" fill="#111">GND</text>')
    o.append(f'<line x1="300" y1="{v5_y}" x2="{W-40}" y2="{v5_y}" stroke="#c0392b" stroke-width="3"/>')
    o.append(f'<text x="{W-36}" y="{v5_y+4}" font-size="13" font-weight="700" fill="#c0392b">5V</text>')
    o.append(f'<path d="M {ex+ew+26} {py["GND"]} H 300 V {gnd_y}" stroke="#111" stroke-width="2" fill="none"/>')
    o.append(f'<path d="M {ex+ew+26} {py["VIN"]} H 330 V {v5_y}" stroke="#c0392b" stroke-width="2" fill="none"/>')

    def zig(x, y0, y1, col="#c8862a"):
        n, seg = 6, (y1-y0)/6
        pts = [f"{x},{y0}"]
        for k in range(1, n):
            pts.append(f"{x + (7 if k % 2 else -7)},{y0+seg*k}")
        pts.append(f"{x},{y1}")
        return f'<polyline points="{" ".join(pts)}" fill="none" stroke="{col}" stroke-width="2.5"/>'

    # LEDs
    for i, g in enumerate(LED_GPIO):
        x = 400 + i*72
        y = py[f"GPIO {g}"]
        o.append(f'<path d="M {ex+ew+26} {y} H {x}" stroke="{LEDC[i]}" stroke-width="2" fill="none"/>')
        o.append(zig(x, y, y+52))
        o.append(f'<text x="{x+12}" y="{y+30}" font-size="10.5" fill="#c8862a">220Ω</text>')
        ly = y + 78
        o.append(f'<line x1="{x}" y1="{y+52}" x2="{x}" y2="{ly-13}" stroke="#555" stroke-width="2"/>')
        o.append(f'<polygon points="{x-11},{ly-13} {x+11},{ly-13} {x},{ly+7}" fill="{LEDC[i]}" stroke="#333"/>')
        o.append(f'<line x1="{x-11}" y1="{ly+7}" x2="{x+11}" y2="{ly+7}" stroke="#333" stroke-width="2.5"/>')
        o.append(f'<text x="{x}" y="{ly-22}" text-anchor="middle" font-size="10.5" fill="#333">{LEDN[i]}</text>')
        o.append(f'<path d="M {x} {ly+7} V {gnd_y}" stroke="#555" stroke-width="2" fill="none"/>')

    # buttons (select + answer share the same topology)
    allb = [(f"GPIO {g}", LEDC[i], f"btn {i+1}") for i, g in enumerate(BTN_GPIO)] + \
           [(f"GPIO {g}", c, n) for n, g, c in ANS]
    for i, (pin, col, lab) in enumerate(allb):
        x = 700 + i*56
        y = py[pin]
        o.append(f'<path d="M {ex+ew+26} {y} H {x}" stroke="{col}" stroke-width="2" fill="none"/>')
        o.append(f'<line x1="{x}" y1="{y}" x2="{x}" y2="{y+26}" stroke="#555" stroke-width="2"/>')
        o.append(f'<circle cx="{x}" cy="{y+28}" r="3" fill="none" stroke="#333" stroke-width="2"/>')
        o.append(f'<line x1="{x-12}" y1="{y+40}" x2="{x+14}" y2="{y+33}" stroke="#333" stroke-width="2.5"/>')
        o.append(f'<circle cx="{x}" cy="{y+44}" r="3" fill="none" stroke="#333" stroke-width="2"/>')
        o.append(f'<path d="M {x} {y+47} V {gnd_y}" stroke="#555" stroke-width="2" fill="none"/>')
        o.append(f'<text x="{x+8}" y="{y+18}" font-size="10" fill="#444">{lab}</text>')

    # LCD
    lx, ly2 = 880, 250
    o.append(f'<rect x="{lx}" y="{ly2}" width="150" height="90" rx="4" fill="none" stroke="#222" stroke-width="2"/>')
    o.append(f'<text x="{lx+75}" y="{ly2+34}" text-anchor="middle" font-size="13" font-weight="700" fill="#222">LCD1602</text>')
    o.append(f'<text x="{lx+75}" y="{ly2+52}" text-anchor="middle" font-size="10.5" fill="#666">I²C, addr 0x27</text>')
    o.append(f'<text x="{lx+75}" y="{ly2+70}" text-anchor="middle" font-size="10" fill="#999">4 flying wires</text>')
    for lab, dy, col in (("SDA", 0, "#e08000"), ("SCL", 18, "#7a4a10")):
        pin = "GPIO 21" if lab == "SDA" else "GPIO 22"
        o.append(f'<path d="M {ex+ew+26} {py[pin]} H 350 V {ly2+120+dy} H {lx+40+dy} V {ly2+90}" stroke="{col}" stroke-width="2" fill="none"/>')
        o.append(f'<text x="{lx+44+dy}" y="{ly2+116+dy}" font-size="10" fill="{col}">{lab}</text>')
    o.append(f'<path d="M {lx+110} {ly2+90} V {gnd_y}" stroke="#111" stroke-width="2" fill="none"/>')
    o.append(f'<text x="{lx+114}" y="{ly2+110}" font-size="10" fill="#111">GND</text>')
    o.append(f'<path d="M {lx+135} {ly2} V {v5_y}" stroke="#c0392b" stroke-width="2" fill="none"/>')
    o.append(f'<text x="{lx+139}" y="{ly2-8}" font-size="10" fill="#c0392b">VCC</text>')

    o.append(f'<text x="400" y="{H-16}" font-size="12" fill="#666">Every button: GPIO → switch → GND. No pull-up resistor — the ESP32\'s internal pull-ups are enabled in firmware.</text>')
    o.append('</svg>')
    return "".join(o)

# ================================================================  BOARD LAYOUT
def board(stage=99, note=""):
    pitch = 26
    ox, oy = 60, 50
    W = ox + COLS*pitch + 260
    H = oy + ROWS*pitch + 90
    o = [f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" {FF}>']
    o.append(f'<rect width="{W}" height="{H}" fill="#fff"/>')
    o.append(f'<rect x="{ox-26}" y="{oy-22}" width="{COLS*pitch+16}" height="{ROWS*pitch+10}" rx="6" fill="#1f6b3f" stroke="#14512e"/>')
    X = lambda c: ox + (c-1)*pitch
    Y = lambda r: oy + (r-1)*pitch
    for c in range(1, COLS+1):
        for r in range(1, ROWS+1):
            o.append(f'<circle cx="{X(c)}" cy="{Y(r)}" r="3.4" fill="#c9a227" opacity="0.55"/>')
    for c in range(1, COLS+1, 2):
        o.append(f'<text x="{X(c)}" y="{oy-30}" text-anchor="middle" font-size="10" fill="#888">{c}</text>')
    for r in range(1, ROWS+1):
        o.append(f'<text x="{ox-36}" y="{Y(r)+4}" text-anchor="end" font-size="10" fill="#888">{r}</text>')

    # stage 1: ESP32 header (underside)
    if stage >= 1:
        for r in HEADER_ROWS:
            o.append(f'<rect x="{X(5)-9}" y="{Y(r)-9}" width="{14*pitch+18}" height="18" rx="4" fill="#111" opacity="0.85"/>')
            o.append(f'<text x="{X(12)}" y="{Y(r)+4}" text-anchor="middle" font-size="10" fill="#9fd6ff">female header (ESP32 plugs in UNDERNEATH)</text>')
    # stage 2: buses
    if stage >= 2:
        for r in GND_ROWS:
            o.append(f'<line x1="{X(1)}" y1="{Y(r)}" x2="{X(COLS)}" y2="{Y(r)}" stroke="#111" stroke-width="6"/>')
            o.append(f'<text x="{X(COLS)+14}" y="{Y(r)+4}" font-size="11" font-weight="700" fill="#111">GND</text>')
        o.append(f'<line x1="{X(COLS)}" y1="{Y(GND_ROWS[0])}" x2="{X(COLS)}" y2="{Y(GND_ROWS[1])}" stroke="#111" stroke-width="5"/>')
        o.append(f'<line x1="{X(1)}" y1="{Y(BUS5V_ROW)}" x2="{X(COLS)}" y2="{Y(BUS5V_ROW)}" stroke="#c0392b" stroke-width="6"/>')
        o.append(f'<text x="{X(COLS)+14}" y="{Y(BUS5V_ROW)+4}" font-size="11" font-weight="700" fill="#c0392b">5V</text>')
    # stage 3: LEDs + resistors
    if stage >= 3:
        for i, c in enumerate(COLS_MAIN):
            o.append(f'<circle cx="{X(c)}" cy="{Y(3.5)}" r="{2.5*pitch/2.54/2}" fill="{LEDC[i]}" stroke="#111"/>')
            o.append(f'<text x="{X(c)}" y="{Y(3.5)+4}" text-anchor="middle" font-size="9" fill="#fff">{i+1}</text>')
            rc = COLS_RES[i]
            o.append(f'<rect x="{X(rc)-5}" y="{Y(1)}" width="10" height="{2*pitch}" rx="3" fill="#c8862a" stroke="#8a5a12"/>')
            o.append(f'<line x1="{X(c)}" y1="{Y(3)}" x2="{X(rc)}" y2="{Y(3)}" stroke="{LEDC[i]}" stroke-width="2"/>')
            o.append(f'<line x1="{X(c)}" y1="{Y(4)}" x2="{X(c)}" y2="{Y(GND_ROWS[0])}" stroke="#555" stroke-width="2"/>')
            o.append(f'<line x1="{X(rc)}" y1="{Y(1)}" x2="{X(rc)}" y2="{Y(1)-16}" stroke="{LEDC[i]}" stroke-width="2"/>')
            o.append(f'<text x="{X(rc)+8}" y="{Y(1)-18}" font-size="9" fill="{LEDC[i]}">GPIO {LED_GPIO[i]}</text>')
    # stage 4: select buttons
    if stage >= 4:
        for i, c in enumerate(COLS_MAIN):
            s = 12*pitch/2.54
            o.append(f'<rect x="{X(c)-s/2}" y="{Y(8)-s/2}" width="{s}" height="{s}" rx="4" fill="{LEDC[i]}" stroke="#111" opacity="0.9"/>')
            o.append(f'<text x="{X(c)}" y="{Y(8)+5}" text-anchor="middle" font-size="13" font-weight="700" fill="#fff">{i+1}</text>')
            o.append(f'<text x="{X(c)}" y="{Y(8)-s/2-6}" text-anchor="middle" font-size="9" fill="#333">GPIO {BTN_GPIO[i]}</text>')
    # stage 5: answer buttons
    if stage >= 5:
        for (n, g, col), c in zip(ANS, COLS_ANS):
            s = 6*pitch/2.54
            o.append(f'<rect x="{X(c)-s/2}" y="{Y(14)-s/2}" width="{s}" height="{s}" rx="3" fill="{col}" stroke="#111"/>')
            o.append(f'<text x="{X(c)}" y="{Y(14)+s/2+13}" text-anchor="middle" font-size="10" font-weight="700" fill="#222">{n}</text>')
            o.append(f'<text x="{X(c)}" y="{Y(14)-s/2-6}" text-anchor="middle" font-size="9" fill="#333">GPIO {g}</text>')
    # stage 6: LCD connector
    if stage >= 6:
        o.append(f'<rect x="{X(1)-8}" y="{Y(BUS5V_ROW)-8}" width="{3*pitch+16}" height="16" rx="3" fill="#c60"/>')
        o.append(f'<text x="{X(6)+10}" y="{Y(BUS5V_ROW)+4}" font-size="10" fill="#c60">LCD: GND · 5V · SDA(21) · SCL(22)</text>')
    if note:
        o.append(f'<text x="{ox-26}" y="{oy+ROWS*pitch+44}" font-size="12.5" fill="#444">{note}</text>')
    o.append('</svg>')
    return "".join(o)

FIGS = [
 ("Schematic — the whole circuit", schematic(),
  "Read it as three groups: LEDs (GPIO → 220Ω → LED → GND), buttons (GPIO → switch → GND, "
  "no resistor), and the LCD on I²C. Everything returns to one GND."),
 ("Board layout — finished", board(99,
  "All 7 buttons, 4 LEDs, 4 resistors and the ESP32 on one 18×24 kit board. Verified for real "
  "body clearances: 3.2mm between button caps, 2.9mm LED→button."),
  "Columns 3/9/15/21 carry both the LEDs and the select buttons. Resistors stand vertically two "
  "columns right of each LED so they clear the LED body."),
 ("Step 1 — female header only", board(1,
  "Two 15-pin strips at rows 2 and 12, columns 5→19. Solder ONE pin on each, check square, then the rest."),
  "The ESP32 plugs in from underneath, so these two rows are the only board space it costs. Test: upload firmware/blink."),
 ("Step 2 — the buses", board(2,
  "Bare wire across rows 5 and 16 (GND) and row 18 (5V). Link the two GND rows down column 24."),
  "Test with the multimeter: every point on a bus beeps; GND↔5V must NOT beep."),
 ("Step 3 — LEDs and resistors", board(3,
  "LED anode row 3, cathode row 4 → straight down to the GND bus at row 5. Resistor stands in rows 1–3."),
  "Test: upload firmware/ledtest — all four cycle red→green→blue→yellow. A dark one is backwards; flip it."),
 ("Step 4 — the four select buttons", board(4,
  "Centred on row 8, columns 3/9/15/21. Diagonal legs: one to its GPIO, the opposite to the GND bus."),
  "Test: firmware/btntest prints button 0–3."),
 ("Step 5 — AA / no / yes", board(5,
  "Small 6mm buttons centred on row 14, columns 4/12/20. Same diagonal rule."),
  "Test: firmware/btntest now prints button 0–6. If several fail at once, suspect the GND bus."),
 ("Step 6 — LCD connector", board(6,
  "Four stranded wires from row 18: GND, 5V, SDA→GPIO 21, SCL→GPIO 22."),
  "Test: firmware/lcdtest prints 'found device at 0x27' and shows text."),
]

CSS = """
:root{color-scheme:light dark}
body{margin:0;padding:2rem 1.25rem 4rem;font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;
background:#faf9f6;color:#22252a;max-width:78rem;margin-inline:auto}
h1{font-size:2rem;margin:0 0 .2em}.sub{color:#666;margin-bottom:2rem}
figure{margin:0 0 2.6rem;padding:1.25rem;background:#fff;border:1px solid #e6e3da;border-radius:12px;overflow-x:auto}
figcaption{margin-top:.8rem;font-size:.95rem;color:#555;border-top:1px solid #eee;padding-top:.6rem}
h2{font-size:1.15rem;margin:0 0 .8rem}
.key{background:#eef6f0;border-left:4px solid #2f7d4f;padding:.9em 1.1em;border-radius:0 8px 8px 0;margin:1.2rem 0}
@media (prefers-color-scheme:dark){body{background:#16181c;color:#d8dae0}
figure{background:#fff}figcaption{color:#556;border-color:#eee}.sub{color:#99a}.key{background:#16241c}}
"""
body = "".join(f'<figure><h2>{t}</h2>{s}<figcaption>{c}</figcaption></figure>' for t, s, c in FIGS)
page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Agent Pad — schematics</title><style>{CSS}</style></head><body>
<h1>Schematics &amp; board layout</h1>
<p class="sub">Circuit schematic, the finished board, then one figure per solder step.</p>
<div class="key"><strong>Verified:</strong> all 7 buttons, 4 LEDs, 4 resistors and the ESP32
fit a single 18×24 kit board. Checked for real component bodies, not just hole counts —
3.2mm between button caps, 2.9mm LED→button, 6.2mm between the two button banks.</div>
{body}</body></html>"""
open(OUT, "w").write(page)
print(OUT)
subprocess.run(["open", OUT], check=False)
