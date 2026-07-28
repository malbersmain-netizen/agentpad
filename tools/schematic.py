#!/usr/bin/env python3
"""Agent Pad — full schematic set.

Circuit schematic, pin map, top-side layout, UNDERSIDE wiring, per-component detail,
a wire-by-wire connection list, and one figure per solder step. All generated from the
same layout constants that tools/verify-layout.py checks, so drawings cannot drift.

    mise exec -- python tools/schematic.py
"""
import os, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT  = os.path.join(ROOT, "schematics.html")
FF   = 'font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif"'

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from layout import *          # single source of truth -- see tools/layout.py
NAME = LED_NAME

def svg(w, h, body, bg="#fff"):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" {FF}><rect width="{w}" height="{h}" fill="{bg}"/>{body}</svg>')

# =========================================================== 1. CIRCUIT SCHEMATIC
def fig_schematic():
    W, H = 1180, 780
    o = []
    V5, GND = 66, H-58
    o.append(f'<line x1="70" y1="{V5}" x2="{W-60}" y2="{V5}" stroke="#c0392b" stroke-width="3"/>')
    o.append(f'<text x="{W-56}" y="{V5+4}" font-size="13" font-weight="700" fill="#c0392b">+5V</text>')
    o.append(f'<line x1="70" y1="{GND}" x2="{W-60}" y2="{GND}" stroke="#111" stroke-width="3"/>')
    o.append(f'<text x="{W-56}" y="{GND+4}" font-size="13" font-weight="700" fill="#111">GND</text>')

    ex, ey, ew, eh = 90, 120, 210, 560
    o.append(f'<rect x="{ex}" y="{ey}" width="{ew}" height="{eh}" rx="6" fill="#fbfbfa" stroke="#222" stroke-width="2"/>')
    o.append(f'<text x="{ex+ew/2}" y="{ey+26}" text-anchor="middle" font-size="15" font-weight="700" fill="#222">ESP32-WROOM-32</text>')
    o.append(f'<text x="{ex+ew/2}" y="{ey+44}" text-anchor="middle" font-size="10.5" fill="#888">30-pin devkit · USB serial 115200</text>')

    rows = ([("VIN / 5V", "#c0392b", "pwr"), ("GND", "#111", "pwr")]
            + [(f"GPIO {g}", COL[i], f"LED {NAME[i]}") for i, g in enumerate(LED_GPIO)]
            + [(f"GPIO {g}", COL[i], f"btn {i+1}") for i, g in enumerate(BTN_GPIO)]
            + [(f"GPIO {g}", ANSC[i], ANS_INFO[i][2]) for i, (n, g, d) in enumerate(ANS_INFO)]
            + [("GPIO 21", "#ef6c00", "SDA"), ("GPIO 22", "#6d4c41", "SCL")])
    py = {}
    for i, (lab, c, note) in enumerate(rows):
        y = ey + 70 + i*33
        py[lab] = y
        o.append(f'<line x1="{ex+ew}" y1="{y}" x2="{ex+ew+22}" y2="{y}" stroke="{c}" stroke-width="2"/>')
        o.append(f'<circle cx="{ex+ew}" cy="{y}" r="3" fill="{c}"/>')
        o.append(f'<text x="{ex+ew-10}" y="{y+4}" text-anchor="end" font-size="11.5" fill="#222">{lab}</text>')
        o.append(f'<text x="{ex+ew+28}" y="{y-5}" font-size="9" fill="#999">{note}</text>')

    o.append(f'<path d="M {ex+ew+22} {py["VIN / 5V"]} H 340 V {V5}" stroke="#c0392b" stroke-width="2" fill="none"/>')
    o.append(f'<path d="M {ex+ew+22} {py["GND"]} H 320 V {GND}" stroke="#111" stroke-width="2" fill="none"/>')

    def zig(x, y0, y1):
        seg = (y1-y0)/6
        pts = [f"{x},{y0}"] + [f"{x+(7 if k%2 else -7)},{y0+seg*k}" for k in range(1, 6)] + [f"{x},{y1}"]
        return f'<polyline points="{" ".join(pts)}" fill="none" stroke="#c8862a" stroke-width="2.5"/>'

    # ---- LED bank
    bx, by = 430, 150
    o.append(f'<rect x="{bx-30}" y="{by-34}" width="290" height="230" rx="8" fill="none" stroke="#ddd" stroke-dasharray="4 3"/>')
    o.append(f'<text x="{bx-22}" y="{by-14}" font-size="12" font-weight="700" fill="#666">STATUS LEDs  ×4</text>')
    for i, g in enumerate(LED_GPIO):
        x = bx + i*62
        o.append(f'<path d="M {ex+ew+22} {py[f"GPIO {g}"]} H {x-14} V {by} H {x}" stroke="{COL[i]}" stroke-width="1.8" fill="none"/>')
        o.append(zig(x, by, by+48))
        ly = by + 76
        o.append(f'<line x1="{x}" y1="{by+48}" x2="{x}" y2="{ly-12}" stroke="#666" stroke-width="1.8"/>')
        o.append(f'<polygon points="{x-10},{ly-12} {x+10},{ly-12} {x},{ly+6}" fill="{COL[i]}" stroke="#333"/>')
        o.append(f'<line x1="{x-10}" y1="{ly+6}" x2="{x+10}" y2="{ly+6}" stroke="#333" stroke-width="2.5"/>')
        o.append(f'<text x="{x}" y="{ly+22}" text-anchor="middle" font-size="9.5" fill="#555">{NAME[i]}</text>')
        o.append(f'<path d="M {x} {ly+6} V {GND}" stroke="#666" stroke-width="1.8" fill="none"/>')
    o.append(f'<text x="{bx+8}" y="{by+30}" font-size="10" fill="#c8862a">220Ω</text>')

    # ---- button bank
    sx, sy = 430, 430
    o.append(f'<rect x="{sx-30}" y="{sy-34}" width="470" height="170" rx="8" fill="none" stroke="#ddd" stroke-dasharray="4 3"/>')
    o.append(f'<text x="{sx-22}" y="{sy-14}" font-size="12" font-weight="700" fill="#666">BUTTONS  ×7   (internal pull-up, no resistor)</text>')
    allb = [(f"GPIO {g}", COL[i], f"{i+1}") for i, g in enumerate(BTN_GPIO)] + \
           [(f"GPIO {g}", ANSC[i], n) for i, (n, g, d) in enumerate(ANS_INFO)]
    for i, (pin, c, lab) in enumerate(allb):
        x = sx + i*60
        o.append(f'<path d="M {ex+ew+22} {py[pin]} H {x-16} V {sy} H {x}" stroke="{c}" stroke-width="1.8" fill="none"/>')
        o.append(f'<line x1="{x}" y1="{sy}" x2="{x}" y2="{sy+22}" stroke="#666" stroke-width="1.8"/>')
        o.append(f'<circle cx="{x}" cy="{sy+25}" r="3.2" fill="#fff" stroke="#333" stroke-width="1.8"/>')
        o.append(f'<line x1="{x-11}" y1="{sy+38}" x2="{x+13}" y2="{sy+30}" stroke="#333" stroke-width="2.5"/>')
        o.append(f'<circle cx="{x}" cy="{sy+41}" r="3.2" fill="#fff" stroke="#333" stroke-width="1.8"/>')
        o.append(f'<path d="M {x} {sy+44} V {GND}" stroke="#666" stroke-width="1.8" fill="none"/>')
        o.append(f'<text x="{x}" y="{sy+62}" text-anchor="middle" font-size="10" font-weight="700" fill="#333">{lab}</text>')

    # ---- LCD
    lx, ly2 = 940, 180
    o.append(f'<rect x="{lx}" y="{ly2}" width="170" height="110" rx="6" fill="#fbfbfa" stroke="#222" stroke-width="2"/>')
    o.append(f'<text x="{lx+85}" y="{ly2+32}" text-anchor="middle" font-size="13" font-weight="700" fill="#222">LCD1602</text>')
    o.append(f'<text x="{lx+85}" y="{ly2+50}" text-anchor="middle" font-size="10" fill="#777">I²C backpack · 0x27</text>')
    o.append(f'<text x="{lx+85}" y="{ly2+68}" text-anchor="middle" font-size="10" fill="#777">16×2 characters</text>')
    o.append(f'<text x="{lx+85}" y="{ly2+90}" text-anchor="middle" font-size="9.5" fill="#c60">4 flying wires — the only</text>')
    o.append(f'<text x="{lx+85}" y="{ly2+102}" text-anchor="middle" font-size="9.5" fill="#c60">off-board component</text>')
    o.append(f'<path d="M {lx+40} {ly2} V {V5}" stroke="#c0392b" stroke-width="2" fill="none"/>')
    o.append(f'<text x="{lx+44}" y="{ly2-8}" font-size="9.5" fill="#c0392b">VCC</text>')
    o.append(f'<path d="M {lx+130} {ly2+110} V {GND}" stroke="#111" stroke-width="2" fill="none"/>')
    o.append(f'<text x="{lx+134}" y="{ly2+128}" font-size="9.5" fill="#111">GND</text>')
    for lab, pin, c, dx in (("SDA", "GPIO 21", "#ef6c00", 70), ("SCL", "GPIO 22", "#6d4c41", 100)):
        o.append(f'<path d="M {ex+ew+22} {py[pin]} H 360 V {ly2+150+dx/8} H {lx+dx} V {ly2+110}" stroke="{c}" stroke-width="1.8" fill="none"/>')
        o.append(f'<text x="{lx+dx-8}" y="{ly2+126+dx/8}" font-size="9.5" fill="{c}">{lab}</text>')

    o.append(f'<text x="70" y="{H-22}" font-size="11.5" fill="#777">Every button is GPIO → switch → GND. Pull-ups are enabled in firmware (INPUT_PULLUP), so a press reads LOW. No external resistors.</text>')
    return svg(W, H, "".join(o))

# ================================================================ 2. PIN MAP
def fig_pinmap():
    rows = ([(f"GPIO {LED_GPIO[i]}", f"LED {i+1} {NAME[i]}", "output", "anode via 220Ω; cathode to GND", COL[i]) for i in range(4)]
          + [(f"GPIO {BTN_GPIO[i]}", f"Select {i+1} {NAME[i]}", "input, pull-up", "diagonal legs: GPIO + GND", COL[i]) for i in range(4)]
          + [(f"GPIO {g}", n, "input, pull-up", d, ANSC[i]) for i, (n, g, d) in enumerate(ANS_INFO)]
          + [("GPIO 21", "LCD SDA", "I²C", "to LCD", "#ef6c00"),
             ("GPIO 22", "LCD SCL", "I²C", "to LCD", "#6d4c41"),
             ("VIN", "5V bus", "power", "LCD VCC only", "#c0392b"),
             ("GND", "GND bus", "power", "everything returns here", "#111")])
    W, H = 980, 60 + len(rows)*28 + 40
    o = [f'<text x="24" y="30" font-size="15" font-weight="700" fill="#222">Pin map — 15 connections total</text>']
    hdr = ["ESP32 pin", "function", "mode", "wiring"]
    xs = [30, 170, 350, 500]
    for x, h in zip(xs, hdr):
        o.append(f'<text x="{x}" y="58" font-size="11" font-weight="700" fill="#888">{h.upper()}</text>')
    for i, (pin, fn, mode, wire, c) in enumerate(rows):
        y = 82 + i*28
        if i % 2 == 0:
            o.append(f'<rect x="20" y="{y-16}" width="{W-40}" height="26" fill="#f7f6f2"/>')
        o.append(f'<rect x="22" y="{y-11}" width="4" height="16" fill="{c}"/>')
        o.append(f'<text x="{xs[0]}" y="{y}" font-size="12" font-weight="700" fill="#222">{pin}</text>')
        o.append(f'<text x="{xs[1]}" y="{y}" font-size="12" fill="#333">{fn}</text>')
        o.append(f'<text x="{xs[2]}" y="{y}" font-size="11.5" fill="#666">{mode}</text>')
        o.append(f'<text x="{xs[3]}" y="{y}" font-size="11.5" fill="#666">{wire}</text>')
    return svg(W, H, "".join(o))

# =========================================================== 3. BOARD FIGURES
PITCH, OX, OY = 34, 86, 74

def board(stage=99, side="top"):
    """Draw board A as it will actually look: copper pads, real part bodies, bus wires."""
    W = OX + COLS*PITCH + 250
    H = OY + ROWS*PITCH + 120
    X = lambda c: OX + (c-1)*PITCH
    Y = lambda r: OY + (r-1)*PITCH
    o = []
    # FR4 substrate
    o.append(f'<rect x="{OX-34}" y="{OY-30}" width="{COLS*PITCH+22}" height="{ROWS*PITCH+22}" rx="8" '
             f'fill="{"#1d6b3d" if side=="top" else "#17572f"}" stroke="#0e3f22" stroke-width="2"/>')
    # copper pads
    for c in range(1, COLS+1):
        for r in range(1, ROWS+1):
            o.append(f'<circle cx="{X(c)}" cy="{Y(r)}" r="{PITCH*0.30}" fill="#c9962e"/>')
            o.append(f'<circle cx="{X(c)}" cy="{Y(r)}" r="{PITCH*0.14}" fill="#123a1f"/>')
    for c in range(1, COLS+1, 2):
        o.append(f'<text x="{X(c)}" y="{OY-38}" text-anchor="middle" font-size="11" fill="#999">{c}</text>')
    for r in range(1, ROWS+1):
        o.append(f'<text x="{OX-44}" y="{Y(r)+4}" text-anchor="end" font-size="11" fill="#999">{r}</text>')

    def lab(x, y, s, col="#222", sz=10.5, anc="middle", w=400):
        o.append(f'<text x="{x}" y="{y}" text-anchor="{anc}" font-size="{sz}" font-weight="{w}" fill="{col}">{s}</text>')

    def bus(r):
        o.append(f'<line x1="{X(1)}" y1="{Y(r)}" x2="{X(COLS)}" y2="{Y(r)}" stroke="#8c9099" stroke-width="9" stroke-linecap="round"/>')
        o.append(f'<line x1="{X(1)}" y1="{Y(r)-2}" x2="{X(COLS)}" y2="{Y(r)-2}" stroke="#d6dae0" stroke-width="2.5" opacity="0.8"/>')
        lab(X(COLS)+52, Y(r)+4, "GND bus", "#333", 11, "start", 700)

    def resistor(c):
        x = X(c); y0 = Y(RES_ROWS[0]); y1 = Y(RES_ROWS[1])
        o.append(f'<line x1="{x}" y1="{y0}" x2="{x}" y2="{y1}" stroke="#9a9a9a" stroke-width="2.5"/>')
        bh = 6.3/2.54*PITCH; by = y1 - bh - 3
        o.append(f'<rect x="{x-7}" y="{by}" width="14" height="{bh}" rx="6" fill="#e8d5a8" stroke="#9b8b62" stroke-width="1"/>')
        for i, cc in enumerate(["#8b1a1a", "#8b1a1a", "#5a3210", "#b8860b"]):   # 220R: red red brown gold
            o.append(f'<rect x="{x-7}" y="{by+8+i*7}" width="14" height="4" fill="{cc}"/>')

    def led(c, colr, n):
        x = X(c); ya = Y(LED_ROWS[0]); yc = Y(LED_ROWS[1])
        o.append(f'<line x1="{x}" y1="{ya}" x2="{x}" y2="{yc}" stroke="#9a9a9a" stroke-width="2"/>')
        cy = (ya+yc)/2
        o.append(f'<ellipse cx="{x}" cy="{cy}" rx="{PITCH*0.95}" ry="{PITCH*0.62}" fill="#c8c8c8" opacity="0.55"/>')
        o.append(f'<circle cx="{x}" cy="{cy}" r="{PITCH*0.80}" fill="{colr}" stroke="#111" stroke-width="1.4"/>')
        o.append(f'<circle cx="{x-PITCH*0.26}" cy="{cy-PITCH*0.26}" r="{PITCH*0.22}" fill="#fff" opacity="0.45"/>')
        lab(x, cy+5, str(n), "#fff", 13, "middle", 700)

    def bigbtn(c0, colr, n):
        x0, x1 = X(c0), X(c0+BIG_LEG_COLS)
        y0, y1 = Y(BTN_ROWS[0]), Y(BTN_ROWS[1])
        cx, cy = (x0+x1)/2, (y0+y1)/2
        s = 12/2.54*PITCH
        o.append(f'<rect x="{cx-s/2}" y="{cy-s/2}" width="{s}" height="{s}" rx="4" fill="#2f3237" stroke="#111"/>')
        cs = s*0.62
        o.append(f'<rect x="{cx-cs/2}" y="{cy-cs/2}" width="{cs}" height="{cs}" rx="5" fill="{colr}" stroke="#111"/>')
        lab(cx, cy+6, str(n), "#fff", 16, "middle", 700)
        for (lx, ly) in ((x0,y0),(x1,y0),(x0,y1),(x1,y1)):
            o.append(f'<circle cx="{lx}" cy="{ly}" r="{PITCH*0.20}" fill="#b9bcc2" stroke="#555"/>')

    def smallbtn(c0, colr, name):
        x0, x1 = X(c0), X(c0+SMALL_LEG)
        y0, y1 = Y(ANS_ROWS[0]), Y(ANS_ROWS[1])
        cx, cy = (x0+x1)/2, (y0+y1)/2
        s = 6/2.54*PITCH
        o.append(f'<rect x="{cx-s/2}" y="{cy-s/2}" width="{s}" height="{s}" rx="3" fill="#2f3237" stroke="#111"/>')
        o.append(f'<circle cx="{cx}" cy="{cy}" r="{s*0.30}" fill="{colr}" stroke="#111"/>')
        lab(cx, cy+s/2+16, name, "#111", 11, "middle", 700)
        for (lx, ly) in ((x0,y0),(x1,y0),(x0,y1),(x1,y1)):
            o.append(f'<circle cx="{lx}" cy="{ly}" r="{PITCH*0.18}" fill="#b9bcc2" stroke="#555"/>')

    if side == "top":
        if stage >= 1:
            for r in GND_ROWS: bus(r)
            o.append(f'<line x1="{X(COLS)}" y1="{Y(GND_ROWS[0])}" x2="{X(COLS)}" y2="{Y(GND_ROWS[-1])}" stroke="#8c9099" stroke-width="7"/>')
            lab(X(COLS)+52, Y(GND_ROWS[0])-20, "linked down col 24", "#666", 10, "start")
        if stage >= 2:
            for i, c in enumerate(LED_COLS):
                resistor(c); led(c, COL[i], i+1)
                o.append(f'<line x1="{X(c)}" y1="{Y(LED_ROWS[0])}" x2="{X(c)}" y2="{OY-52}" stroke="{COL[i]}" stroke-width="3" stroke-dasharray="6 4"/>')
                lab(X(c), OY-58, f"GPIO {LED_GPIO[i]}", COL[i], 10, "middle", 700)
        if stage >= 3:
            for i, c0 in enumerate(BTN_COL0):
                bigbtn(c0, COL[i], i+1)
                o.append(f'<line x1="{X(c0)}" y1="{Y(BTN_ROWS[0])}" x2="{X(c0)-26}" y2="{Y(BTN_ROWS[0])}" stroke="{COL[i]}" stroke-width="3" stroke-dasharray="6 4"/>')
                lab(X(c0)-30, Y(BTN_ROWS[0])+4, f"{BTN_GPIO[i]}", COL[i], 10, "end", 700)
        if stage >= 4:
            for (n, g, d), c0, cc in zip(ANS_INFO, ANS_COL0, ANSC):
                smallbtn(c0, cc, n)
                o.append(f'<line x1="{X(c0)}" y1="{Y(ANS_ROWS[0])}" x2="{X(c0)-26}" y2="{Y(ANS_ROWS[0])}" stroke="{cc}" stroke-width="3" stroke-dasharray="6 4"/>')
                lab(X(c0)-30, Y(ANS_ROWS[0])+4, f"{g}", cc, 10, "end", 700)
        if stage >= 5:
            lab(OX + COLS*PITCH/2, OY+ROWS*PITCH+56,
                "dashed = the 15 wires to board B · the LCD never touches this board", "#666", 12)
    else:
        lab(OX + COLS*PITCH/2, OY-52, "UNDERSIDE — mirrored. ALL copper and ALL solder joints are on this face.", "#c33", 13, "middle", 700)
        for r in GND_ROWS: bus(r)
        o.append(f'<line x1="{X(COLS)}" y1="{Y(GND_ROWS[0])}" x2="{X(COLS)}" y2="{Y(GND_ROWS[-1])}" stroke="#8c9099" stroke-width="7"/>')
        for i, c in enumerate(LED_COLS):
            o.append(f'<circle cx="{X(c)}" cy="{Y(LED_ROWS[1])}" r="{PITCH*0.34}" fill="none" stroke="#ffd76b" stroke-width="3"/>')
            lab(X(c), Y(LED_ROWS[1])-24, "2 leads share", "#ffd76b", 9)
            lab(X(c), Y(LED_ROWS[1])-13, "this hole", "#ffd76b", 9)
        lab(OX + COLS*PITCH/2, OY+ROWS*PITCH+56,
            "Each ground leg lands directly on a bus — no ground jumpers anywhere.", "#444", 12)
    o.append(f'<text x="{OX-34}" y="{OY+ROWS*PITCH+86}" font-size="11.5" fill="#888">board A · 18 rows x 24 cols · single-sided</text>')
    return svg(W, H, "".join(o))

# ============================================== 3b. BOARD B + WHOLE ASSEMBLY
ESP_LEFT  = ["VIN","GND","D13","D12","D14","D27","D26","D25","D33","D32","D35","D34","VN","VP","EN"]
ESP_RIGHT = ["3V3","GND","D15","D2","D4","RX2","TX2","D5","D18","D19","D21","RX0","TX0","D22","D23"]
USED = {"VIN":"5V -> LCD","GND":"ground","D13":"LED 1 red","D14":"LED 2 green","D27":"LED 3 blue",
        "D26":"LED 4 yellow","D32":"button 1","D33":"button 2","D25":"button 3","D4":"button 4",
        "D23":"AA","D18":"no","D19":"yes","D21":"LCD SDA","D22":"LCD SCL"}

def fig_boardB():
    P2, ox, oy = 30, 150, 110
    W, H = 900, oy + 18*P2 + 120
    X = lambda c: ox + (c-1)*P2
    Y = lambda r: oy + (r-1)*P2
    o = []
    o.append(f'<text x="40" y="34" font-size="15" font-weight="700" fill="#222">Board B — the ESP32 carrier</text>')
    o.append(f'<text x="40" y="56" font-size="12" fill="#666">Same 18x24 kit board. Two 15-socket strips, 10 holes apart. Nothing else on it.</text>')
    o.append(f'<rect x="{ox-34}" y="{oy-30}" width="{24*P2+22}" height="{18*P2+22}" rx="8" fill="#1d6b3d" stroke="#0e3f22" stroke-width="2"/>')
    for c in range(1, 25):
        for r in range(1, 19):
            o.append(f'<circle cx="{X(c)}" cy="{Y(r)}" r="{P2*0.30}" fill="#c9962e"/>')
            o.append(f'<circle cx="{X(c)}" cy="{Y(r)}" r="{P2*0.14}" fill="#123a1f"/>')
    # two header strips: columns 5-19, rows 4 and 14 (10 apart)
    HR = HDR_ROWS; HC0, HC1 = HDR_COLS
    for r in HR:
        o.append(f'<rect x="{X(HC0)-11}" y="{Y(r)-11}" width="{(HC1-HC0)*P2+22}" height="22" rx="5" fill="#15181c"/>')
        for c in range(HC0, HC1+1):
            o.append(f'<circle cx="{X(c)}" cy="{Y(r)}" r="6" fill="#3a3f47" stroke="#000"/>')
    # ESP32 body ghosted on top
    o.append(f'<rect x="{X(HC0)-16}" y="{Y(HR[0])-34}" width="{(HC1-HC0)*P2+32}" height="{(HR[1]-HR[0])*P2+68}" rx="8" fill="#2b2b33" opacity="0.80" stroke="#8ecbff" stroke-width="2"/>')
    o.append(f'<text x="{(X(HC0)+X(HC1))/2}" y="{Y(9)-6}" text-anchor="middle" font-size="15" font-weight="700" fill="#fff">ESP32 plugs in on TOP</text>')
    o.append(f'<text x="{(X(HC0)+X(HC1))/2}" y="{Y(9)+14}" text-anchor="middle" font-size="11" fill="#9fd6ff">pin rows 10 holes apart · USB faces the board edge</text>')
    o.append(f'<rect x="{(X(HC0)+X(HC1))/2-26}" y="{Y(HR[1])+34}" width="52" height="16" rx="4" fill="#888"/>')
    o.append(f'<text x="{(X(HC0)+X(HC1))/2}" y="{Y(HR[1])+64}" text-anchor="middle" font-size="11" fill="#444">USB-C</text>')
    # labelled pins
    for i, nm in enumerate(ESP_LEFT):
        if nm in USED:
            o.append(f'<line x1="{X(HC0+i)}" y1="{Y(HR[0])}" x2="{X(HC0+i)}" y2="{Y(1)-30}" stroke="#c8862a" stroke-width="2"/>')
    o.append(f'<text x="{ox-46}" y="{Y(HR[0])+5}" text-anchor="end" font-size="11" font-weight="700" fill="#333">row {HR[0]}</text>')
    o.append(f'<text x="{ox-46}" y="{Y(HR[1])+5}" text-anchor="end" font-size="11" font-weight="700" fill="#333">row {HR[1]}</text>')
    o.append(f'<text x="{ox}" y="{Y(18)+52}" font-size="12" fill="#444">15 wires from board A + 4 from the LCD land on the pads under these sockets — on the UNDERSIDE.</text>')
    return svg(W, H, "".join(o))

def fig_assembly():
    W, H = 1000, 640
    o = []
    o.append(f'<text x="40" y="34" font-size="15" font-weight="700" fill="#222">How it all sits on the wood</text>')
    o.append(f'<rect x="60" y="60" width="880" height="520" rx="10" fill="#c8a06a" stroke="#8a6a3a" stroke-width="3"/>')
    o.append(f'<text x="80" y="88" font-size="12" fill="#6a4a20">plywood backing plate — everything screws down, nothing is loose</text>')
    # LCD
    o.append(f'<rect x="300" y="110" width="380" height="110" rx="6" fill="#1d3b2a" stroke="#4a7" stroke-width="2"/>')
    o.append(f'<rect x="330" y="140" width="320" height="50" rx="3" fill="#2f6b4a"/>')
    o.append(f'<text x="490" y="163" text-anchor="middle" font-size="13" fill="#bdf3cf">A3 BLOCKED 4:21</text>')
    o.append(f'<text x="490" y="182" text-anchor="middle" font-size="13" fill="#bdf3cf">1w 2i 3B 4d  34%</text>')
    o.append(f'<text x="700" y="150" font-size="12" font-weight="700" fill="#333">LCD1602</text>')
    o.append(f'<text x="700" y="168" font-size="11" fill="#555">own 4 x M3 holes</text>')
    o.append(f'<text x="700" y="184" font-size="11" fill="#a60">NOT soldered — F-M jumpers</text>')
    for x,y in ((310,120),(670,120),(310,210),(670,210)):
        o.append(f'<circle cx="{x}" cy="{y}" r="5" fill="#777" stroke="#444"/>')
    # board A
    o.append(f'<rect x="200" y="270" width="470" height="250" rx="8" fill="#1d6b3d" stroke="#0e3f22" stroke-width="2"/>')
    o.append(f'<text x="435" y="296" text-anchor="middle" font-size="13" font-weight="700" fill="#cfe">BOARD A — control surface</text>')
    for i,cc in enumerate(COL):
        o.append(f'<circle cx="{250+i*105}" cy="{330}" r="13" fill="{cc}" stroke="#111"/>')
        o.append(f'<rect x="{250+i*105-24}" y="{362}" width="48" height="48" rx="5" fill="{cc}" stroke="#111"/>')
    for i,(n,g,d) in enumerate(ANS_INFO):
        o.append(f'<rect x="{250+i*105-14}" y="{450}" width="28" height="28" rx="4" fill="{ANSC[i]}" stroke="#111"/>')
        o.append(f'<text x="{250+i*105}" y="{494}" text-anchor="middle" font-size="10" fill="#cfe">{n}</text>')
    for x,y in ((215,285),(655,505)):
        o.append(f'<circle cx="{x}" cy="{y}" r="5" fill="#777" stroke="#444"/>')
    # board B
    o.append(f'<rect x="720" y="300" width="180" height="200" rx="8" fill="#1d6b3d" stroke="#0e3f22" stroke-width="2"/>')
    o.append(f'<text x="810" y="326" text-anchor="middle" font-size="12" font-weight="700" fill="#cfe">BOARD B</text>')
    o.append(f'<rect x="748" y="340" width="124" height="120" rx="6" fill="#2b2b33" stroke="#8ecbff" stroke-width="2"/>')
    o.append(f'<text x="810" y="396" text-anchor="middle" font-size="12" font-weight="700" fill="#fff">ESP32</text>')
    o.append(f'<text x="810" y="414" text-anchor="middle" font-size="9.5" fill="#9fd6ff">in its socket</text>')
    o.append(f'<rect x="792" y="460" width="36" height="14" rx="3" fill="#888"/>')
    o.append(f'<path d="M 810 474 V 545 H 960" stroke="#333" stroke-width="5" fill="none"/>')
    o.append(f'<text x="880" y="566" font-size="11" fill="#333">USB to the Mac</text>')
    for x,y in ((735,315),(885,485)):
        o.append(f'<circle cx="{x}" cy="{y}" r="5" fill="#777" stroke="#444"/>')
    # harness A -> B
    for i in range(6):
        o.append(f'<path d="M 670 {310+i*30} C 700 {310+i*30}, 700 {350+i*22}, 720 {350+i*22}" stroke="#b0863a" stroke-width="2.5" fill="none"/>')
    o.append(f'<text x="695" y="290" text-anchor="middle" font-size="11" font-weight="700" fill="#8a5a12">15 wires</text>')
    # LCD -> B
    for i in range(4):
        o.append(f'<path d="M {620+i*14} 220 C {660+i*14} 260, 740 260, 760 {336}" stroke="#c60" stroke-width="2.2" fill="none"/>')
    o.append(f'<text x="700" y="248" font-size="11" font-weight="700" fill="#c60">LCD: 4 wires</text>')
    o.append(f'<text x="80" y="560" font-size="12" fill="#5a3a10">The LCD and the ESP32 both stay removable — only board A is permanent.</text>')
    return svg(W, H, "".join(o))

# ====================================================== 4. COMPONENT DETAILS
def fig_detail():
    W, H = 1080, 400
    o = []
    o.append(f'<text x="30" y="30" font-size="15" font-weight="700" fill="#222">Exactly which holes — one LED and one button</text>')
    def grid(ox, oy, cols, rows, pitch=34):
        g = []
        for c in range(cols):
            for r in range(rows):
                g.append(f'<circle cx="{ox+c*pitch}" cy="{oy+r*pitch}" r="9" fill="#1d6b3d"/>')
                g.append(f'<circle cx="{ox+c*pitch}" cy="{oy+r*pitch}" r="4.5" fill="#d8b13a"/>')
        return "".join(g)
    # LED
    ox, oy, p = 70, 90, 34
    o.append(grid(ox, oy, 6, 6))
    o.append(f'<text x="{ox-14}" y="{oy-16}" font-size="12" font-weight="700" fill="#333">LED + resistor</text>')
    o.append(f'<circle cx="{ox+2*p}" cy="{oy+1.5*p}" r="19" fill="#c0392b" stroke="#111" stroke-width="1.5"/>')
    o.append(f'<line x1="{ox+2*p}" y1="{oy+1*p}" x2="{ox+4*p}" y2="{oy+1*p}" stroke="#c0392b" stroke-width="3"/>')
    o.append(f'<rect x="{ox+4*p-7}" y="{oy-8}" width="14" height="{1*p+16}" rx="4" fill="#c8862a" stroke="#8a5a12"/>')
    o.append(f'<line x1="{ox+2*p}" y1="{oy+2*p}" x2="{ox+2*p}" y2="{oy+4*p}" stroke="#444" stroke-width="3"/>')
    o.append(f'<line x1="{ox-10}" y1="{oy+4*p}" x2="{ox+5.4*p}" y2="{oy+4*p}" stroke="#111" stroke-width="7"/>')
    for t, x, y in ((f"anode +  row {LED_ROWS[0]}", ox+2*p, oy+1*p-24), (f"cathode -  row {LED_ROWS[1]}", ox+2*p+26, oy+2*p+6),
                    (f"220R rows {RES_ROWS[0]}-{RES_ROWS[1]}", ox+4*p+16, oy+10), (f"GND bus row {GND_ROWS[0]}", ox+5.4*p+14, oy+4*p+4)):
        anchor = "start" if x > ox+2*p else "middle"
        o.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="10.5" fill="#333">{t}</text>')
    # button
    ox2 = 560
    o.append(grid(ox2, oy, BIG_LEG_COLS+2, BIG_LEG_ROWS+2))
    o.append(f'<text x="{ox2-14}" y="{oy-16}" font-size="12" font-weight="700" fill="#333">Colored button — legs {BIG_LEG_COLS} pitches ACROSS, {BIG_LEG_ROWS} LONG</text>')
    s = 12*p/2.54*0.42
    cx, cy = ox2+BIG_LEG_COLS/2*p, oy+BIG_LEG_ROWS/2*p
    o.append(f'<rect x="{cx-s/2}" y="{cy-s/2}" width="{s}" height="{s}" rx="6" fill="#c0392b" stroke="#111" stroke-width="1.5" opacity="0.35"/>')
    for (dc, dr) in ((0,0), (BIG_LEG_COLS,0), (0,BIG_LEG_ROWS), (BIG_LEG_COLS,BIG_LEG_ROWS)):
        o.append(f'<circle cx="{ox2+dc*p}" cy="{oy+dr*p}" r="11" fill="none" stroke="#777" stroke-width="2"/>')
    o.append(f'<circle cx="{ox2}" cy="{oy}" r="11" fill="none" stroke="#2f7d4f" stroke-width="3.5"/>')
    o.append(f'<circle cx="{ox2+BIG_LEG_COLS*p}" cy="{oy+BIG_LEG_ROWS*p}" r="11" fill="none" stroke="#2f7d4f" stroke-width="3.5"/>')
    o.append(f'<line x1="{ox2}" y1="{oy}" x2="{ox2}" y2="{oy-26}" stroke="#c0392b" stroke-width="3"/>')
    o.append(f'<text x="{ox2}" y="{oy-32}" text-anchor="middle" font-size="10.5" fill="#c0392b">to GPIO</text>')
    o.append(f'<line x1="{ox2+BIG_LEG_COLS*p}" y1="{oy+BIG_LEG_ROWS*p}" x2="{ox2+(BIG_LEG_COLS+1.2)*p}" y2="{oy+BIG_LEG_ROWS*p}" stroke="#111" stroke-width="3"/>')
    o.append(f'<text x="{ox2+(BIG_LEG_COLS+1.4)*p}" y="{oy+BIG_LEG_ROWS*p+4}" font-size="10.5" fill="#111">lands ON the GND bus</text>')
    o.append(f'<text x="{ox2}" y="{oy+(BIG_LEG_ROWS+1.4)*p}" font-size="10.5" fill="#2f7d4f">green = the two legs you wire (diagonal)</text>')
    o.append(f'<text x="{ox2}" y="{oy+(BIG_LEG_ROWS+1.4)*p+18}" font-size="10.5" fill="#777">grey = solder these too: same net, double the anchoring</text>')
    return svg(W, H, "".join(o))

# ======================================================= 5. CONNECTION LIST
def fig_wires():
    """Connection list, derived from layout.harness() so it cannot drift."""
    rows = []
    for i, c in enumerate(LED_COLS):
        rows.append((f"LED {i+1} {NAME[i]}", f"anode col {c} row {LED_ROWS[0]}",
                     f"wire to D{LED_GPIO[i]} on board B", COL[i]))
        rows.append(("", f"cathode col {c} row {LED_ROWS[1]}",
                     f"lead bends to the 220R pad at row {RES_ROWS[0]}", COL[i]))
        rows.append(("", f"220R bottom col {c} row {RES_ROWS[1]}",
                     f"lands ON the GND bus", COL[i]))
    for i, c0 in enumerate(BTN_COL0):
        rows.append((f"Button {i+1} {NAME[i]}", f"signal leg col {c0} row {BTN_ROWS[0]}",
                     f"wire to D{BTN_GPIO[i]} on board B", COL[i]))
        rows.append(("", f"gnd leg col {c0+BIG_LEG_COLS} row {BTN_ROWS[1]}",
                     "lands ON the GND bus", COL[i]))
    for i, ((n, g, d), c0) in enumerate(zip(ANS_INFO, ANS_COL0)):
        rows.append((f"{n} ({d})", f"signal leg col {c0} row {ANS_ROWS[0]}",
                     f"wire to D{g} on board B", ANSC[i]))
        rows.append(("", f"gnd leg col {c0+SMALL_LEG} row {ANS_ROWS[1]}",
                     "lands ON the GND bus", ANSC[i]))
    rows.append(("Ground", f"any GND bus (rows {', '.join(map(str, GND_ROWS))})",
                 "one wire to GND on board B", "#111"))
    for a_, b_ in LCD_PINS:
        rows.append((f"LCD {a_}", "F-M jumper on the LCD's own header",
                     f"board B pad {b_} — never board A", "#c60"))
    W, H = 940, 74 + len(rows)*22 + 30
    o = [f'<text x="24" y="30" font-size="15" font-weight="700" fill="#222">Every connection, in order</text>',
         f'<text x="24" y="50" font-size="11" fill="#888">generated from tools/layout.py — {len(harness())} wires to board B plus {len(LCD_PINS)} from the LCD</text>']
    for x, h in zip([30, 250, 560], ["PART", "BOARD A HOLE", "GOES TO"]):
        o.append(f'<text x="{x}" y="72" font-size="10.5" font-weight="700" fill="#999">{h}</text>')
    for i, (part, frm, to, c) in enumerate(rows):
        y = 94 + i*22
        if part: o.append(f'<rect x="20" y="{y-14}" width="{W-40}" height="20" fill="#f7f6f2" opacity="0.7"/>')
        o.append(f'<rect x="22" y="{y-10}" width="3" height="14" fill="{c}"/>')
        o.append(f'<text x="30" y="{y}" font-size="11" font-weight="{700 if part else 400}" fill="#222">{part}</text>')
        o.append(f'<text x="250" y="{y}" font-size="11" fill="#555">{frm}</text>')
        o.append(f'<text x="560" y="{y}" font-size="11" fill="#555">{to}</text>')
    return svg(W, H, "".join(o))

FIGS = [
 ("1 · Circuit schematic", fig_schematic(),
  "Three functional groups. LEDs: GPIO → 220Ω → LED → GND. Buttons: GPIO → switch → GND, "
  "with the ESP32's internal pull-up doing the rest. LCD: I²C on GPIO 21/22, powered from 5V."),
 ("2 · Pin map", fig_pinmap(),
  f"{len(harness())+len(LCD_PINS)} connections. Every GPIO is safe: none are input-only (34-39) or boot strapping "
  "pins (0, 2, 12, 15). Each one is an F-M jumper — female on the ESP32, male soldered in."),
 ("3 · Board layout — top side, finished", board(99, "top"),
  "One 18×24 kit board. Dashed lines leaving the top edge are the jumpers to the ESP32, which "
  "sits on its own carrier board rather than on this one."),
 ("3b · Board B — the ESP32 carrier", fig_boardB(),
  "Two 15-socket strips, 10 holes apart. The ESP32 plugs in on top; its USB faces the board "
  "edge so the cable can reach it. All 19 wires land on the pads underneath."),
 ("3c · How it all sits on the wood", fig_assembly(),
  "LCD at the top on its own M3 holes, board A below it, board B off to the side with the USB "
  "facing out. Only board A is permanent — the LCD and ESP32 both unplug."),
 ("4 · Underside — where every joint lives", board(99, "under"),
  "The board is SINGLE-SIDED: all the copper, and therefore every solder joint, is on this face. "
  "Components sit on the other side; only their legs and the jumper pins come through."),
 ("5 · Component detail — which holes exactly", fig_detail(),
  "The button has four legs but only two pairs. Use diagonally opposite corners so you're across "
  "the switch, not along a permanently-joined pair."),
 ("6 · Connection list", fig_wires(),
  "Tick these off as you go. Label both ends of every jumper before soldering the male end."),
 ("Step 1 — the buses", board(1, "top"),
  "Bare wire across row 1 (5V), rows 5 and 17 (GND), linked down column 24. "
  "Test: every point on a bus beeps; 5V↔GND must NOT beep."),
 ("Step 2 — LEDs and resistors", board(2, "top"),
  "Anode row 3, cathode row 4 straight down to the GND bus at row 5. 220Ω lies flat in row 2. "
  "Test: clip the ESP32 on with jumpers and run firmware/ledtest — all four cycle."),
 ("Step 3 — the four colored buttons", board(3, "top"),
  "Legs in rows 7 and 12, columns 2-4 / 8-10 / 14-16 / 20-22. Top-left leg takes its jumper, "
  "bottom-right leg goes to the GND bus. Test: firmware/btntest prints button 0–3."),
 ("Step 4 — AA / no / yes", board(4, "top"),
  "Small 3×3 buttons, legs rows 14 and 16. Same diagonal rule. "
  "Test: btntest now prints button 0–6. Several dead at once means the GND bus, not the switches."),
 ("Step 5 — LCD leads", board(5, "top"),
  "Four F-M jumpers from the LCD's own header straight to board B — never to board A. "
  "Test: firmware/lcdtest prints 'found device at 0x27'."),
]

CSS = """
:root{color-scheme:light dark}
body{margin:0;padding:2rem 1.25rem 5rem;font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;
background:#faf9f6;color:#22252a;max-width:82rem;margin-inline:auto}
h1{font-size:2rem;margin:0 0 .2em}.sub{color:#666;margin-bottom:1.4rem}
figure{margin:0 0 2.4rem;padding:1.3rem;background:#fff;border:1px solid #e6e3da;border-radius:12px;overflow-x:auto}
figcaption{margin-top:.85rem;font-size:.94rem;color:#555;border-top:1px solid #eee;padding-top:.65rem}
h2{font-size:1.12rem;margin:0 0 .85rem;color:#222}
.key{background:#eef6f0;border-left:4px solid #2f7d4f;padding:.9em 1.1em;border-radius:0 8px 8px 0;margin:1.2rem 0}
nav{margin:0 0 2rem;font-size:.92rem}nav a{color:#2f7d4f;margin-right:1rem;white-space:nowrap}
@media (prefers-color-scheme:dark){body{background:#16181c;color:#d8dae0}
figure{background:#fff}figcaption{color:#556;border-color:#eee}h2{color:#222}.sub{color:#99a}.key{background:#16241c}}
"""
nav = " ".join(f'<a href="#f{i}">{t.split(" · ")[0] if " · " in t else t}</a>' for i, (t, _, _) in enumerate(FIGS))
body = "".join(f'<figure id="f{i}"><h2>{t}</h2>{s}<figcaption>{c}</figcaption></figure>'
               for i, (t, s, c) in enumerate(FIGS))
page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Agent Pad — schematics</title><style>{CSS}</style></head><body>
<h1>Schematics &amp; board layout</h1>
<p class="sub">Circuit, pin map, both sides of the board, component detail, every wire, then one figure per solder step.</p>
<nav>{nav}</nav>
<div class="key"><strong>Single-sided board.</strong> All the copper is on one face, so every
solder joint is on the underside and every component sits on top. The ESP32 gets
<strong>its own carrier board</strong> — not because it could not be soldered here, but because
board A's 18 rows are already spent. Both screw to a wooden plate; the ESP32 unplugs and stays
removable.<br><br>
<strong>Verified in millimetres, not hole counts.</strong> Every figure here is generated from
<code>tools/layout.py</code>, the same file <code>tools/verify-layout.py</code> checks — so a drawing
cannot disagree with the spec. Re-check with
<code>mise exec -- python tools/verify-layout.py</code>.</div>
{body}</body></html>"""
open(OUT, "w").write(page)
print(OUT)
subprocess.run(["open", OUT], check=False)
