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

# ---- layout (mirrors verify-layout.py) ------------------------------------
ROWS, COLS = 18, 24
BIG_LEG_COLS, BIG_LEG_ROWS, SMALL_LEG = 2, 5, 2
LED_COLS = [3, 9, 15, 21]
BTN_COL0 = [c-1 for c in LED_COLS]
BTN_ROWS = (7, 12)
RES_COLS = [6, 12, 18, 24]   # flat, row 2
ANS_COL0 = [3, 11, 19]
ANS_ROWS = (14, 16)
ANS_ROWS_NOTE = 'off-board ESP32'
GND_ROWS = (5, 17)
V5_ROW   = 1
LCD_ROW  = 18
LED_GPIO = [13, 14, 27, 26]
BTN_GPIO = [32, 33, 25, 4]
ANS_INFO = [("AA", 23, "always allow"), ("no", 18, "deny"), ("yes", 19, "approve")]
COL  = ["#c0392b", "#2e7d32", "#1565c0", "#b8860b"]
NAME = ["red", "green", "blue", "yellow"]
ANSC = ["#8a5a12", "#37474f", "#0f6b52"]

def svg(w, h, body, bg="#fff"):
    return f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" {FF}><rect width="{w}" height="{h}" fill="{bg}"/>{body}</svg>'

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
PITCH, OX, OY = 30, 74, 62
def board(stage=99, side="top"):
    W = OX + COLS*PITCH + 210
    H = OY + ROWS*PITCH + 80
    X = lambda c: OX + (c-1)*PITCH
    Y = lambda r: OY + (r-1)*PITCH
    o = []
    o.append(f'<rect x="{OX-30}" y="{OY-26}" width="{COLS*PITCH+18}" height="{ROWS*PITCH+14}" rx="7" fill="#1d6b3d" stroke="#12built" stroke-width="0"/>'.replace("#12built", "#124d2b"))
    for c in range(1, COLS+1):
        for r in range(1, ROWS+1):
            o.append(f'<circle cx="{X(c)}" cy="{Y(r)}" r="4" fill="#0f3d22"/>')
            o.append(f'<circle cx="{X(c)}" cy="{Y(r)}" r="2.1" fill="#d8b13a"/>')
    for c in range(1, COLS+1):
        if c % 2 == 1:
            o.append(f'<text x="{X(c)}" y="{OY-34}" text-anchor="middle" font-size="10" fill="#999">{c}</text>')
    for r in range(1, ROWS+1):
        o.append(f'<text x="{OX-42}" y="{Y(r)+4}" text-anchor="end" font-size="10" fill="#999">{r}</text>')

    def label(x, y, t, c="#333", size=10, anchor="middle"):
        o.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" fill="{c}">{t}</text>')

    if side == "top":
        if stage >= 1:
            for r in GND_ROWS:
                o.append(f'<line x1="{X(1)}" y1="{Y(r)}" x2="{X(COLS)}" y2="{Y(r)}" stroke="#111" stroke-width="7"/>')
                label(X(COLS)+40, Y(r)+4, "GND bus", "#111", 11, "start")
            o.append(f'<line x1="{X(COLS)}" y1="{Y(GND_ROWS[0])}" x2="{X(COLS)}" y2="{Y(GND_ROWS[1])}" stroke="#111" stroke-width="6"/>')
            o.append(f'<line x1="{X(1)}" y1="{Y(V5_ROW)}" x2="{X(COLS)}" y2="{Y(V5_ROW)}" stroke="#c0392b" stroke-width="7"/>')
            label(X(COLS)+40, Y(V5_ROW)+4, "5V bus", "#c0392b", 11, "start")
        if stage >= 2:
            for i, c in enumerate(LED_COLS):
                o.append(f'<circle cx="{X(c)}" cy="{Y(3.5)}" r="{5/2*PITCH/2.54}" fill="{COL[i]}" stroke="#111" stroke-width="1.5"/>')
                label(X(c), Y(3.5)+4, str(i+1), "#fff", 12)
                rc = RES_COLS[i]
                o.append(f'<rect x="{X(rc)-2*PITCH-6}" y="{Y(2)-6}" width="{2*PITCH+12}" height="12" rx="4" fill="#c8862a" stroke="#8a5a12"/>')
                o.append(f'<line x1="{X(c)}" y1="{Y(2)}" x2="{X(rc)}" y2="{Y(2)}" stroke="{COL[i]}" stroke-width="2.5"/>')
                o.append(f'<line x1="{X(c)}" y1="{Y(3)}" x2="{X(c)}" y2="{Y(GND_ROWS[0])}" stroke="#444" stroke-width="2.5"/>')
                o.append(f'<line x1="{X(rc)}" y1="{Y(2)}" x2="{X(rc)}" y2="{Y(1)-38}" stroke="{COL[i]}" stroke-width="2.5" stroke-dasharray="5 3"/>')
                label(X(rc)+22, Y(4), f"GPIO {LED_GPIO[i]}", COL[i], 9)
            label(X(2), Y(3.5)-26, "220Ω", "#c8862a", 9.5)
        if stage >= 3:
            for i, c0 in enumerate(BTN_COL0):
                x0, x1 = X(c0), X(c0+BIG_LEG_COLS)
                y0, y1 = Y(BTN_ROWS[0]), Y(BTN_ROWS[1])
                cx, cy = (x0+x1)/2, (y0+y1)/2
                s = 12*PITCH/2.54
                o.append(f'<rect x="{cx-s/2}" y="{cy-s/2}" width="{s}" height="{s}" rx="5" fill="{COL[i]}" stroke="#111" stroke-width="1.5" opacity="0.92"/>')
                label(cx, cy+6, str(i+1), "#fff", 16)
                for (lx, ly) in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
                    o.append(f'<circle cx="{lx}" cy="{ly}" r="6" fill="none" stroke="#fff" stroke-width="2"/>')
                o.append(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{Y(1)-38}" stroke="{COL[i]}" stroke-width="2.5" stroke-dasharray="5 3" opacity="0.75"/>')
                label(cx, cy-s/2-8, f"GPIO {BTN_GPIO[i]}", "#222", 9.5)
                o.append(f'<line x1="{x1}" y1="{y1}" x2="{x1}" y2="{Y(GND_ROWS[1])}" stroke="#111" stroke-width="2.5" opacity="0.55"/>')
        if stage >= 4:
            for i, c0 in enumerate(ANS_COL0):
                x0, x1 = X(c0), X(c0+SMALL_LEG)
                y0, y1 = Y(ANS_ROWS[0]), Y(ANS_ROWS[1])
                cx, cy = (x0+x1)/2, (y0+y1)/2
                s = 6*PITCH/2.54
                o.append(f'<rect x="{cx-s/2}" y="{cy-s/2}" width="{s}" height="{s}" rx="4" fill="{ANSC[i]}" stroke="#111" stroke-width="1.5"/>')
                label(cx, cy+s/2+16, ANS_INFO[i][0], "#111", 11)
                label(cx, cy-s/2-8, f"GPIO {ANS_INFO[i][1]}", "#222", 9.5)
        if stage >= 5:
            o.append(f'<rect x="{X(1)-10}" y="{Y(LCD_ROW)-10}" width="{3*PITCH+20}" height="20" rx="4" fill="#e07b00"/>')
            label(X(6)+40, Y(LCD_ROW)+4, "LCD: GND · 5V · SDA(21) · SCL(22)", "#e07b00", 11, "start")
    else:  # underside
        o.append(f'<text x="{OX-30}" y="{OY-48}" font-size="12" fill="#c33">MIRRORED — this is the view with the board flipped left-to-right</text>')
        o.append(f'<rect x="{X(4)}" y="{Y(8)-30}" width="{16*PITCH}" height="{4*PITCH}" rx="8" fill="#20242b" stroke="#8ecbff" stroke-width="2" stroke-dasharray="7 5"/>')
        label(X(12), Y(9)-16, "ESP32 lives on BOARD B", "#8ecbff", 14)
        label(X(12), Y(10)-14, "15 wires join board A to board B;", "#8ecbff", 11)
        label(X(12), Y(11)-16, "it plugs into a socket there and stays removable", "#8ecbff", 11)
        for i in range(4):
            o.append(f'<path d="M {X(RES_COLS[i])} {Y(2)} V {Y(1)-34}" stroke="{COL[i]}" stroke-width="2.5" fill="none"/>')
            o.append(f'<path d="M {X(BTN_COL0[i])} {Y(BTN_ROWS[0])} V {Y(1)-34}" stroke="{COL[i]}" stroke-width="2.5" fill="none" opacity="0.75"/>')
        for i, c0 in enumerate(ANS_COL0):
            o.append(f'<path d="M {X(c0)} {Y(ANS_ROWS[0])} V {Y(ROWS)+30}" stroke="{ANSC[i]}" stroke-width="2.5" fill="none" opacity="0.75"/>')
        label(X(12), Y(ROWS)+56, "Every joint is on THIS side — the board is single-sided, so all copper is here.", "#c33", 12.5)
        label(X(12), Y(ROWS)+76, "Each jumper's male pin solders into the same pad as the leg it serves.", "#444", 12)
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
    for t, x, y in (("anode +  row 3", ox+2*p, oy+1*p-24), ("cathode −  row 4", ox+2*p+26, oy+2*p+6),
                    ("220Ω  rows 1-3", ox+4*p+16, oy+10), ("GND bus  row 5", ox+5.4*p+14, oy+4*p+4)):
        anchor = "start" if x > ox+2*p else "middle"
        o.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="10.5" fill="#333">{t}</text>')
    # button
    ox2 = 560
    o.append(grid(ox2, oy, 7, 7))
    o.append(f'<text x="{ox2-14}" y="{oy-16}" font-size="12" font-weight="700" fill="#333">Colored button — legs 5 holes apart BOTH ways</text>')
    s = 12*p/2.54*0.42
    cx, cy = ox2+2.5*p, oy+2.5*p
    o.append(f'<rect x="{cx-s/2}" y="{cy-s/2}" width="{s}" height="{s}" rx="6" fill="#c0392b" stroke="#111" stroke-width="1.5" opacity="0.35"/>')
    for (dc, dr) in ((0, 0), (5, 0), (0, 5), (5, 5)):
        o.append(f'<circle cx="{ox2+dc*p}" cy="{oy+dr*p}" r="11" fill="none" stroke="#777" stroke-width="2"/>')
    o.append(f'<circle cx="{ox2}" cy="{oy}" r="11" fill="none" stroke="#2f7d4f" stroke-width="3.5"/>')
    o.append(f'<circle cx="{ox2+5*p}" cy="{oy+5*p}" r="11" fill="none" stroke="#2f7d4f" stroke-width="3.5"/>')
    o.append(f'<line x1="{ox2}" y1="{oy}" x2="{ox2}" y2="{oy-26}" stroke="#c0392b" stroke-width="3"/>')
    o.append(f'<text x="{ox2}" y="{oy-32}" text-anchor="middle" font-size="10.5" fill="#c0392b">to GPIO</text>')
    o.append(f'<line x1="{ox2+5*p}" y1="{oy+5*p}" x2="{ox2+6.2*p}" y2="{oy+5*p}" stroke="#111" stroke-width="3"/>')
    o.append(f'<text x="{ox2+6.4*p}" y="{oy+5*p+4}" font-size="10.5" fill="#111">to GND bus</text>')
    o.append(f'<text x="{ox2}" y="{oy+6.4*p}" font-size="10.5" fill="#2f7d4f">green = the two legs you actually wire (diagonal)</text>')
    o.append(f'<text x="{ox2}" y="{oy+6.4*p+18}" font-size="10.5" fill="#777">grey = the other two; leave them, or clip flush</text>')
    return svg(W, H, "".join(o))

# ======================================================= 5. CONNECTION LIST
def fig_wires():
    rows = []
    for i in range(4):
        rows.append((f"LED {i+1} {NAME[i]}", f"anode, col {LED_COLS[i]} row 3", f"220Ω (col {RES_COLS[i]}) → GPIO {LED_GPIO[i]}", COL[i]))
        rows.append(("", f"cathode, col {LED_COLS[i]} row 4", f"GND bus (row {GND_ROWS[0]})", COL[i]))
    for i in range(4):
        rows.append((f"Button {i+1} {NAME[i]}", f"leg col {BTN_COL0[i]} row {BTN_ROWS[0]}", f"GPIO {BTN_GPIO[i]}", COL[i]))
        rows.append(("", f"leg col {BTN_COL0[i]+BIG_LEG_COLS} row {BTN_ROWS[1]}", f"GND bus (row {GND_ROWS[1]})", COL[i]))
    for i, (n, g, d) in enumerate(ANS_INFO):
        rows.append((f"{n} ({d})", f"leg col {ANS_COL0[i]} row {ANS_ROWS[0]}", f"GPIO {g}", ANSC[i]))
        rows.append(("", f"leg col {ANS_COL0[i]+SMALL_LEG} row {ANS_ROWS[1]}", f"GND bus (row {GND_ROWS[1]})", ANSC[i]))
    for lab, dest, c in (("LCD GND", f"GND bus", "#111"), ("LCD VCC", f"5V bus (row {V5_ROW})", "#c0392b"),
                         ("LCD SDA", "GPIO 21", "#ef6c00"), ("LCD SCL", "GPIO 22", "#6d4c41")):
        rows.append((lab, "flying lead", dest, c))
    rows.append(("ESP32 GND", "header pin", f"GND bus", "#111"))
    rows.append(("ESP32 VIN", "header pin", f"5V bus", "#c0392b"))
    W, H = 900, 70 + len(rows)*22 + 30
    o = [f'<text x="24" y="30" font-size="15" font-weight="700" fill="#222">Every connection, in order</text>']
    for x, h in zip([30, 210, 470], ["PART", "FROM", "TO"]):
        o.append(f'<text x="{x}" y="56" font-size="10.5" font-weight="700" fill="#999">{h}</text>')
    for i, (part, frm, to, c) in enumerate(rows):
        y = 78 + i*22
        if part:
            o.append(f'<rect x="20" y="{y-14}" width="{W-40}" height="{44 if not part else 22}" fill="#f7f6f2" opacity="0.6"/>')
        o.append(f'<rect x="22" y="{y-10}" width="3" height="14" fill="{c}"/>')
        o.append(f'<text x="30" y="{y}" font-size="11" font-weight="{700 if part else 400}" fill="#222">{part}</text>')
        o.append(f'<text x="210" y="{y}" font-size="11" fill="#555">{frm}</text>')
        o.append(f'<text x="470" y="{y}" font-size="11" fill="#555">→ {to}</text>')
    return svg(W, H, "".join(o))

FIGS = [
 ("1 · Circuit schematic", fig_schematic(),
  "Three functional groups. LEDs: GPIO → 220Ω → LED → GND. Buttons: GPIO → switch → GND, "
  "with the ESP32's internal pull-up doing the rest. LCD: I²C on GPIO 21/22, powered from 5V."),
 ("2 · Pin map", fig_pinmap(),
  "Fifteen connections. Every GPIO is safe: none are input-only (34-39) or boot strapping "
  "pins (0, 2, 12, 15). Each one is an F-M jumper — female on the ESP32, male soldered in."),
 ("3 · Board layout — top side, finished", board(99, "top"),
  "One 18×24 kit board. Dashed lines leaving the top edge are the jumpers to the ESP32, which "
  "sits on its own carrier board rather than on this one."),
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
  "Four stranded wires off row 18. Test: firmware/lcdtest prints 'found device at 0x27'."),
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
solder joint is on the underside and every component sits on top. The ESP32 cannot be socketed
here — its socket body would cover the pads — so it gets <strong>its own carrier board</strong>,
joined by 15 wires. Both screw to a wooden plate; the ESP32 unplugs and stays removable.<br><br>
<strong>Verified in millimetres, not hole counts:</strong> 7 buttons, 4 LEDs and 4 resistors fit
with 3.2mm between button bodies, 6.7mm LED→button and 5.0mm between banks — and 7 spare rows.
Re-check with <code>mise exec -- python tools/verify-layout.py</code>.</div>
{body}</body></html>"""
open(OUT, "w").write(page)
print(OUT)
subprocess.run(["open", OUT], check=False)
