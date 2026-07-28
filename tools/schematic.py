#!/usr/bin/env python3
"""Agent Pad — full schematic set.

Circuit schematic, pin map, top-side layout, UNDERSIDE wiring, per-component detail,
a wire-by-wire connection list, and one figure per solder step. All generated from the
same layout constants that tools/verify-layout.py checks, so drawings cannot drift.

    mise exec -- python tools/schematic.py
"""
import os, re, subprocess

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
PITCH, OX, OY = 22, 74, 62

def board(stage=99, side="top"):
    """Draw the board as it will actually look: copper pads, real part bodies, buses, wires."""
    W = OX + COLS*PITCH + 250
    H = OY + ROWS*PITCH + 130
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
        o.append(f'<line x1="{X(BUS_COLS[0])}" y1="{Y(r)}" x2="{X(BUS_COLS[1])}" y2="{Y(r)}" stroke="#8c9099" stroke-width="9" stroke-linecap="round"/>')
        o.append(f'<line x1="{X(BUS_COLS[0])}" y1="{Y(r)-2}" x2="{X(BUS_COLS[1])}" y2="{Y(r)-2}" stroke="#d6dae0" stroke-width="2.5" opacity="0.8"/>')
        lab(X(BUS_COLS[1])+14, Y(r)+4, "GND", "#333", 11, "start", 700)

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
        for (hc, hr), role in switch_legs(c0, BIG_LEG_COLS, BTN_ROWS):
            lx, ly = X(hc), Y(hr)
            if role == "clip":
                o.append(f'<circle cx="{lx}" cy="{ly}" r="{PITCH*0.26}" fill="none" stroke="#ff5b5b" stroke-width="2.4"/>')
                o.append(f'<path d="M {lx-5} {ly-5} L {lx+5} {ly+5} M {lx+5} {ly-5} L {lx-5} {ly+5}" stroke="#ff5b5b" stroke-width="2.4"/>')
            else:
                o.append(f'<circle cx="{lx}" cy="{ly}" r="{PITCH*0.20}" fill="#b9bcc2" stroke="#555"/>')

    def smallbtn(c0, colr, name):
        x0, x1 = X(c0), X(c0+SMALL_LEG)
        y0, y1 = Y(ANS_ROWS[0]), Y(ANS_ROWS[1])
        cx, cy = (x0+x1)/2, (y0+y1)/2
        s = 6/2.54*PITCH
        o.append(f'<rect x="{cx-s/2}" y="{cy-s/2}" width="{s}" height="{s}" rx="3" fill="#2f3237" stroke="#111"/>')
        o.append(f'<circle cx="{cx}" cy="{cy}" r="{s*0.30}" fill="{colr}" stroke="#111"/>')
        lab(cx, cy+s/2+16, name, "#111", 11, "middle", 700)
        for (hc, hr), role in switch_legs(c0, SMALL_LEG, ANS_ROWS):
            lx, ly = X(hc), Y(hr)
            if role == "clip":
                o.append(f'<circle cx="{lx}" cy="{ly}" r="{PITCH*0.24}" fill="none" stroke="#ff5b5b" stroke-width="2.2"/>')
                o.append(f'<path d="M {lx-4.5} {ly-4.5} L {lx+4.5} {ly+4.5} M {lx+4.5} {ly-4.5} L {lx-4.5} {ly+4.5}" stroke="#ff5b5b" stroke-width="2.2"/>')
            else:
                o.append(f'<circle cx="{lx}" cy="{ly}" r="{PITCH*0.18}" fill="#b9bcc2" stroke="#555"/>')

    if side == "top":
        if stage >= 1:
            for r in GND_ROWS: bus(r)
            o.append(f'<line x1="{X(GND_LINK_COL)}" y1="{Y(GND_ROWS[0])}" x2="{X(GND_LINK_COL)}" y2="{Y(GND_ROWS[-1])}" stroke="#8c9099" stroke-width="7"/>')
            lab(X(GND_LINK_COL)+9, Y((GND_ROWS[0]+GND_ROWS[-1])/2)-6, "all 3 buses linked", "#d6dae0", 9.5, "start", 700)
            lab(X(GND_LINK_COL)+9, Y((GND_ROWS[0]+GND_ROWS[-1])/2)+6, f"down col {GND_LINK_COL} \u2014 no signal crosses it", "#d6dae0", 9.5, "start", 700)
            # ESP32 socket, same board
            ex0, ey0 = X(HDR_COLS[0]), Y(HDR_ROWS[0])
            ex1, ey1 = X(HDR_COLS[1]), Y(HDR_ROWS[1])
            o.append(f'<rect x="{ex0-20}" y="{ey0-30}" width="{ex1-ex0+40}" height="{ey1-ey0+60}" rx="8" '
                     f'fill="#2b2b33" opacity="0.30" stroke="#8ecbff" stroke-width="2" stroke-dasharray="7 5"/>')
            o.append(f'<rect x="{ex0-20}" y="{ey0-56}" width="{ex1-ex0+40}" height="22" rx="4" fill="#0e3f22"/>')
            lab((ex0+ex1)/2, ey0-40, "ESP32 module sits ON TOP \u2014 outline only", "#bfe4ff", 11.5, "middle", 700)
            for c in HDR_COLS:
                o.append(f'<rect x="{X(c)-11}" y="{ey0-11}" width="22" height="{ey1-ey0+22}" rx="5" fill="#15181c"/>')
            used = {p for _, _, p, _, _, _, _ in harness()}
            for sd, names in (("3V3", ESP_3V3_SIDE), ("VIN", ESP_VIN_SIDE)):
                for i, nm in enumerate(names):
                    c, r = socket_hole(sd, i+1)
                    hot = nm in used
                    o.append(f'<circle cx="{X(c)}" cy="{Y(r)}" r="{PITCH*0.26}" '
                             f'fill="{"#f0c419" if hot else "#5a6068"}"/>')
                    lab(X(c) + (13 if sd == "3V3" else 14), Y(r)+3.5, nm,
                        "#fff" if hot else "#7d848d", 8.5,
                        "start", 700 if hot else 400)
            # mounting. The real board has factory holes in the margin at each corner;
            # the computed on-pad positions are only the fallback.
            if FACTORY_CORNER_HOLES:
                mx0, my0 = OX-34+13, OY-30+13
                mx1, my1 = OX-34+COLS*PITCH+22-13, OY-30+ROWS*PITCH+22-13
                for mx, my in ((mx0,my0),(mx1,my0),(mx0,my1),(mx1,my1)):
                    o.append(f'<circle cx="{mx}" cy="{my}" r="7" fill="#0b2b16" stroke="#e8e8e8" stroke-width="2"/>')
                lab(mx0+16, my0-6, "factory corner holes \u2014 M3, no drilling", "#e8e8e8", 9.5, "start", 700)
            else:
                for c, r in mount_holes():
                    o.append(f'<circle cx="{X(c)}" cy="{Y(r)}" r="{MOUNT_DRILL/2/2.54*PITCH}" '
                             f'fill="#0b2b16" stroke="#e8e8e8" stroke-width="2"/>')
                lab(X(mount_holes()[0][0])+14, Y(mount_holes()[0][1])-14,
                    f"drill {MOUNT_DRILL}mm here", "#e8e8e8", 9.5, "start", 700)
            # the LCD port -- 4 male pins
            p0 = LCD_PORT_COL0; pr = LCD_PORT_ROW
            o.append(f'<rect x="{X(p0)-11}" y="{Y(pr)-11}" width="{(len(LCD_PINS)-1)*PITCH+22}" '
                     f'height="22" rx="4" fill="#15181c" stroke="#c60" stroke-width="1.5"/>')
            for i, (nm, _) in enumerate(LCD_PINS):
                o.append(f'<circle cx="{X(p0+i)}" cy="{Y(pr)}" r="{PITCH*0.26}" fill="#e8a33d"/>')
                lab(X(p0+i), Y(pr)-16, nm, "#e8a33d", 8.5, "middle", 700)
            lab(X(p0)-2, Y(pr)+30, "LCD port \u2014 4 male pins, F-F jumpers, never soldered", "#e8a33d", 10, "start", 700)
            o.append(f'<rect x="{(ex0+ex1)/2-150}" y="{ey1+40}" width="300" height="34" rx="4" fill="#0e3f22"/>')
            lab((ex0+ex1)/2, ey1+54, "USB faces this way, 13mm short of the edge", "#bfe4ff", 10.5, "middle", 700)
            lab((ex0+ex1)/2, ey1+68, "keep rows 26-30 clear: the cable exits over them", "#8fbcd8", 9.5)
        if stage >= 2:
            for i, c in enumerate(LED_COLS):
                resistor(c); led(c, COL[i], i+1)
                pass
        if stage >= 3:
            for i, c0 in enumerate(BTN_COL0):
                bigbtn(c0, COL[i], i+1)
                pass
                pass
        if stage >= 4:
            for (n, g, d), c0, cc in zip(ANS_INFO, ANS_COL0, ANSC):
                smallbtn(c0, cc, n)
                pass
                pass
        if stage >= 5:
            # Every signal wire on its real route: right along its own row to the riser
            # lane at col 29 (clear of the buses, which stop at col 28), along the lane,
            # then into its socket hole. Wires to the RIGHT column pass UNDER the ESP32
            # module on the copper face — drawn dashed where they do.
            SPINE = HDR_COLS[0] - 1
            wires = [w for w in harness() if w[2] != "GND"]
            groups = {LED_ROWS[0]: (LED_COLS, COL),
                      BTN_ROWS[0]: (BTN_COL0, COL),
                      ANS_ROWS[0]: (ANS_COL0, ANSC)}
            for n, (lbl, src, pin, sd, pos, col, row) in enumerate(wires, 1):
                m = re.match(r"col (\d+), row (\d+)", src)
                if not m: continue
                sc, sr = int(m.group(1)), int(m.group(2))
                cols_, pal = groups.get(sr, ([], COL))
                cc2 = pal[cols_.index(sc)] if sc in cols_ else "#555"
                # fan the risers out so 11 strands read as 11, not as one line
                dx = (n - len(wires)/2) * 1.7
                dy = (n - len(wires)/2) * 1.9
                xs, ys, xl = X(sc), Y(sr), X(SPINE) + dx
                o.append(f'<path d="M {xs} {ys} V {ys+dy} H {xl} V {Y(row)} H {X(HDR_COLS[0])}" '
                         f'stroke="{cc2}" stroke-width="2.2" fill="none" opacity="0.9" '
                         f'stroke-linejoin="round"/>')
                if sd == "VIN":     # continues underneath the module to the far column
                    o.append(f'<path d="M {X(HDR_COLS[0])} {Y(row)} H {X(col)}" stroke="{cc2}" '
                             f'stroke-width="2.2" fill="none" stroke-dasharray="5 4" opacity="0.9"/>')
                o.append(f'<circle cx="{X(col)}" cy="{Y(row)}" r="4.5" fill="{cc2}" stroke="#fff" stroke-width="1.2"/>')
                o.append(f'<circle cx="{xs}" cy="{ys}" r="4.5" fill="{cc2}" stroke="#fff" stroke-width="1.2"/>')
                o.append(f'<circle cx="{xs}" cy="{ys-15}" r="7.5" fill="#fff" stroke="{cc2}" stroke-width="1.6"/>')
                lab(xs, ys-11.5, str(n), cc2, 9, "middle", 700)
            # the four LCD-port wires. Short runs straight down; the two I2C lines carry
            # on underneath the module (dashed) to reach the right-hand column.
            for i, (nm, hole, esp, sock) in enumerate(lcd_port()):
                hx, hy = X(hole[0]), Y(hole[1])
                sx, sy = X(sock[0]), Y(sock[1])
                o.append(f'<path d="M {hx} {hy} V {sy}" stroke="#e8a33d" stroke-width="2.2" fill="none"/>')
                if hx != sx:
                    o.append(f'<path d="M {hx} {sy} H {sx}" stroke="#e8a33d" stroke-width="2.2" '
                             f'fill="none" stroke-dasharray="5 4"/>')
                o.append(f'<circle cx="{sx}" cy="{sy}" r="4" fill="#e8a33d" stroke="#fff" stroke-width="1.1"/>')

            # the single ground wire: bus at col 28 -> the socket's GND pad
            gc, gr = socket_hole(*esp_position("GND"))
            o.append(f'<path d="M {X(BUS_COLS[1])} {Y(GND_ROWS[1])} H {X(SPINE)+14} V {Y(gr)} H {X(gc)}" '
                     f'stroke="#111" stroke-width="3" fill="none" stroke-linejoin="round"/>')
            o.append(f'<circle cx="{X(gc)}" cy="{Y(gr)}" r="4.5" fill="#111" stroke="#fff" stroke-width="1.2"/>')
            lab(OX-34, OY+ROWS*PITCH+34, "wire 12: GND bus (col 28) \u2192 the ESP32's GND pad \u2014 the only ground wire on the board", "#111", 11, "start", 700)

            lab(OX + COLS*PITCH/2, OY+ROWS*PITCH+56,
                "\u2715 red = the leg you CLIP OFF before seating each switch \u2014 three legs go in, not four",
                "#ff5b5b", 11.5, "middle", 700)
            lab(OX + COLS*PITCH/2, OY+ROWS*PITCH+76,
                f"{len(wires)} signal wires + 1 ground (numbered as in BUILD.md) + {len(LCD_PINS)} orange LCD-port wires \u00b7 "
                f"dashed = runs under the ESP32 on the copper face \u00b7 the LCD itself is never "
                f"soldered \u2014 it plugs into the orange port with 4 F-F jumpers", "#666", 11.5)
    else:
        lab(OX + COLS*PITCH/2, OY-52, "UNDERSIDE — mirrored. ALL copper and ALL solder joints are on this face.", "#c33", 13, "middle", 700)
        for r in GND_ROWS: bus(r)
        o.append(f'<line x1="{X(COLS)}" y1="{Y(GND_ROWS[0])}" x2="{X(COLS)}" y2="{Y(GND_ROWS[-1])}" stroke="#8c9099" stroke-width="7"/>')
        for i, c in enumerate(LED_COLS):
            o.append(f'<path d="M {X(c)} {Y(LED_ROWS[1])} L {X(c)} {Y(RES_ROWS[0])}" stroke="#ffd76b" stroke-width="4" fill="none"/>')
            o.append(f'<circle cx="{X(c)}" cy="{Y(LED_ROWS[1])}" r="{PITCH*0.30}" fill="none" stroke="#ffd76b" stroke-width="2.5"/>')
            o.append(f'<circle cx="{X(c)}" cy="{Y(RES_ROWS[0])}" r="{PITCH*0.30}" fill="none" stroke="#ffd76b" stroke-width="2.5"/>')
            lab(X(c), Y(LED_ROWS[1])-26, "cathode leg bent", "#ffd76b", 9)
            lab(X(c), Y(LED_ROWS[1])-15, "flat onto row 4", "#ffd76b", 9)
        lab(OX + COLS*PITCH/2, OY+ROWS*PITCH+56,
            "Each ground leg lands directly on a bus — no ground jumpers anywhere.", "#444", 12)
    o.append(f'<text x="{OX-34}" y="{OY+ROWS*PITCH+100}" font-size="11.5" fill="#888">ONE board · {ROWS} rows x {COLS} cols · double-sided · ESP32 socketed at cols {HDR_COLS[0]}-{HDR_COLS[1]}</text>')
    return svg(W, H, "".join(o))

# ============================================== 3b. BOARD B + WHOLE ASSEMBLY
USED = {"VIN":"5V -> LCD","GND":"ground","D13":"LED 1 red","D14":"LED 2 green","D27":"LED 3 blue",
        "D26":"LED 4 yellow","D32":"button 1","D33":"button 2","D25":"button 3","D4":"button 4",
        "D23":"AA","D18":"no","D19":"yes","D21":"LCD SDA","D22":"LCD SCL"}

def fig_assembly():
    """One board + the LCD, screwed to the wooden plate."""
    W, H = 1020, 620
    o = []
    o.append(f'<text x="40" y="34" font-size="15" font-weight="700" fill="#222">How it sits on the wood</text>')
    o.append(f'<rect x="55" y="58" width="910" height="510" rx="10" fill="#c8a06a" stroke="#8a6a3a" stroke-width="3"/>')
    o.append(f'<text x="76" y="86" font-size="12" fill="#6a4a20">plywood plate — two pieces screw down: the board, and the LCD</text>')
    # LCD
    o.append(f'<rect x="300" y="108" width="380" height="108" rx="6" fill="#1d3b2a" stroke="#4a7" stroke-width="2"/>')
    o.append(f'<rect x="330" y="136" width="320" height="50" rx="3" fill="#2f6b4a"/>')
    o.append(f'<text x="490" y="159" text-anchor="middle" font-size="13" fill="#bdf3cf">A3 BLOCKED 4:21</text>')
    o.append(f'<text x="490" y="178" text-anchor="middle" font-size="13" fill="#bdf3cf">1w 2i 3B 4d  34%</text>')
    for x, y in ((312,118),(668,118),(312,206),(668,206)):
        o.append(f'<circle cx="{x}" cy="{y}" r="5" fill="#777" stroke="#444"/>')
    o.append(f'<text x="700" y="140" font-size="12" font-weight="700" fill="#333">LCD1602</text>')
    o.append(f'<text x="700" y="158" font-size="11" fill="#555">its own 4 × M3 holes</text>')
    o.append(f'<text x="700" y="176" font-size="11" fill="#a60">NEVER soldered — 4 F-F jumpers</text>')
    o.append(f'<text x="700" y="192" font-size="11" fill="#555">into the board\u2019s 4-pin LCD port</text>')
    # the one board
    bx, by, bw, bh = 150, 268, 690, 262
    o.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="8" fill="#1d6b3d" stroke="#0e3f22" stroke-width="2"/>')
    o.append(f'<text x="{bx+16}" y="{by+26}" font-size="12.5" font-weight="700" fill="#cfe">ONE BOARD — 30 × 42 holes, double-sided</text>')
    for i, cc in enumerate(COL):
        o.append(f'<circle cx="{bx+70+i*105}" cy="{by+62}" r="12" fill="{cc}" stroke="#111"/>')
        o.append(f'<rect x="{bx+70+i*105-24}" y="{by+92}" width="48" height="48" rx="5" fill="{cc}" stroke="#111"/>')
    for i, (n, g, d) in enumerate(ANS_INFO):
        o.append(f'<rect x="{bx+70+i*105-14}" y="{by+178}" width="28" height="28" rx="4" fill="{ANSC[i]}" stroke="#111"/>')
        o.append(f'<text x="{bx+70+i*105}" y="{by+222}" text-anchor="middle" font-size="10" fill="#cfe">{n}</text>')
    o.append(f'<text x="{bx+30}" y="{by+250}" font-size="10.5" fill="#9c9">control surface — cols 1–28</text>')
    # ESP32 on the same board
    ex = bx + 470
    o.append(f'<rect x="{ex}" y="{by+50}" width="150" height="170" rx="7" fill="#2b2b33" stroke="#8ecbff" stroke-width="2"/>')
    o.append(f'<text x="{ex+75}" y="{by+128}" text-anchor="middle" font-size="13" font-weight="700" fill="#fff">ESP32</text>')
    o.append(f'<text x="{ex+75}" y="{by+148}" text-anchor="middle" font-size="10" fill="#9fd6ff">socketed, cols 30–40</text>')
    o.append(f'<text x="{ex+75}" y="{by+164}" text-anchor="middle" font-size="10" fill="#9fd6ff">unplugs any time</text>')
    o.append(f'<rect x="{ex+56}" y="{by+220}" width="38" height="14" rx="3" fill="#888"/>')
    o.append(f'<path d="M {ex+75} {by+234} V {by+272} H {W-70}" stroke="#333" stroke-width="5" fill="none"/>')
    o.append(f'<text x="{W-160}" y="{by+292}" font-size="11" fill="#333">USB to the Mac</text>')
    for x, y in ((bx+16, by+bh-16), (bx+bw-16, by+bh-16), (bx+bw-16, by+16)):
        o.append(f'<circle cx="{x}" cy="{y}" r="5" fill="#777" stroke="#444"/>')
    # LCD jumpers
    for i in range(4):
        o.append(f'<path d="M {600+i*16} 216 C {640+i*16} 250, {ex+40} 250, {ex+40+i*12} {by+50}" '
                 f'stroke="#c60" stroke-width="2.2" fill="none"/>')
    o.append(f'<text x="700" y="212" font-size="11" font-weight="700" fill="#c60">4 F-F jumpers down to the LCD port</text>')
    o.append(f'<text x="76" y="556" font-size="12" fill="#5a3a10">Only the board is permanent. The LCD and the ESP32 both unplug.</text>')
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
                     f"wire to the D{LED_GPIO[i]} socket pad", COL[i]))
        rows.append(("", f"cathode col {c} row {LED_ROWS[1]}",
                     f"lead bends to the 220R pad at row {RES_ROWS[0]}", COL[i]))
        rows.append(("", f"220R bottom col {c} row {RES_ROWS[1]}",
                     f"lands ON the GND bus", COL[i]))
    for i, c0 in enumerate(BTN_COL0):
        L = dict((r, h) for h, r in switch_legs(c0, BIG_LEG_COLS, BTN_ROWS))
        rows.append((f"Button {i+1} {NAME[i]}", f"signal leg col {L['signal'][0]} row {L['signal'][1]}",
                     f"wire to the D{BTN_GPIO[i]} socket pad", COL[i]))
        rows.append(("", f"anchor leg col {L['anchor'][0]} row {L['anchor'][1]}", "solder, no connection", COL[i]))
        rows.append(("", f"col {L['clip'][0]} row {L['clip'][1]}", "CLIP THIS LEG OFF", "#c00"))
        rows.append(("", f"gnd leg col {L['ground'][0]} row {L['ground'][1]}", "lands ON the GND bus", COL[i]))
    for i, ((n, g, d), c0) in enumerate(zip(ANS_INFO, ANS_COL0)):
        L = dict((r, h) for h, r in switch_legs(c0, SMALL_LEG, ANS_ROWS))
        rows.append((f"{n} ({d})", f"signal leg col {L['signal'][0]} row {L['signal'][1]}",
                     f"wire to the D{g} socket pad", ANSC[i]))
        rows.append(("", f"anchor leg col {L['anchor'][0]} row {L['anchor'][1]}", "solder, no connection", ANSC[i]))
        rows.append(("", f"col {L['clip'][0]} row {L['clip'][1]}", "CLIP THIS LEG OFF", "#c00"))
        rows.append(("", f"gnd leg col {L['ground'][0]} row {L['ground'][1]}", "lands ON the GND bus", ANSC[i]))
    rows.append(("Ground", f"col {GND_WIRE_FROM[0]} row {GND_WIRE_FROM[1]} (GND bus)",
                 "one wire to the GND socket pad", "#111"))
    for name, hole, esp, sock in lcd_port():
        rows.append((f"LCD {name}", f"port pin col {hole[0]} row {hole[1]} (F-F jumper)",
                     f"wire to the {esp} socket pad, col {sock[0]} row {sock[1]}", "#c60"))
    W, H = 940, 74 + len(rows)*22 + 30
    o = [f'<text x="24" y="30" font-size="15" font-weight="700" fill="#222">Every connection, in order</text>',
         f'<text x="24" y="50" font-size="11" fill="#888">generated from tools/layout.py — {len(harness())} soldered wires plus {len(LCD_PINS)} LCD jumpers</text>']
    for x, h in zip([30, 250, 560], ["PART", "BOARD HOLE", "GOES TO"]):
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
  "pins (0, 2, 12, 15). The 12 signal wires and the ground wire are soldered to socket pads; the "
  "LCD's 4 reach the board's LCD port on F-F jumpers."),
 ("3 · Board layout — top side, finished", board(99, "top"),
  f"One {ROWS}\u00d7{COLS} double-sided board. The ESP32 is socketed at columns {HDR_COLS[0]}-{HDR_COLS[1]} on this "
  f"same board; every wire is drawn on its real route. Red \u2715 marks the switch leg you clip off."),
 ("3b · How it sits on the wood", fig_assembly(),
  "Two pieces screw to the plate: the board, and the LCD. The ESP32 is socketed on the board "
  "itself, USB facing an edge. Only the board is permanent."),
 ("4 · Underside — where every joint lives", board(99, "under"),
  "The board is double-sided, but every joint is made on THIS face, so the design works whether or "
  "not the holes are plated through. Components sit on the other side; only their legs come through."),
 ("5 · Component detail — which holes exactly", fig_detail(),
  "Each switch has four legs but only two internally-joined pairs \u2014 and on this kit they join "
  "down the LONG axis. One leg is CLIPPED OFF before seating so the board works either way."),
 ("6 · Connection list", fig_wires(),
  "Tick these off as you go. Label both ends of every wire before you solder the second end."),
 ("Step 1 — the buses and the ESP32 socket", board(1, "top"),
  f"Bare wire along rows {', '.join(map(str, GND_ROWS))} (all GND), spanning columns "
  f"{BUS_COLS[0]}-{BUS_COLS[1]} and linked down column {GND_LINK_COL}. Then the two 15-way "
  f"socket strips at columns {HDR_COLS[0]} and {HDR_COLS[1]}, rows {HDR_ROWS[0]}-{HDR_ROWS[1]}. "
  f"Test: every point on a bus beeps to every other; no bus beeps to a signal row."),
 (f"Step 2 — LEDs and resistors", board(2, "top"),
  f"Anode row {LED_ROWS[0]}, cathode row {LED_ROWS[1]}; the cathode lead bends flat on the copper "
  f"face onto the row-{RES_ROWS[0]} pad, where the 220R starts. The resistor's other lead sits in "
  f"row {RES_ROWS[1]} — a GND bus — so it grounds itself. Columns {', '.join(map(str, LED_COLS))}. "
  f"Test: plug the ESP32 in, run firmware/ledtest — all four cycle."),
 ("Step 3 — the four colored buttons", board(3, "top"),
  f"Legs in rows {BTN_ROWS[0]} and {BTN_ROWS[1]}, left columns {', '.join(map(str, BTN_COL0))} "
  f"(each spans {BIG_LEG_COLS} columns). CLIP the leg at the signal column on row {BTN_ROWS[1]} before "
  f"seating \u2014 three legs go in. The row-{BTN_ROWS[0]} signal leg takes the wire; the diagonally "
  f"opposite leg lands on the row-{BTN_ROWS[1]} bus. Test: firmware/btntest prints button 0-3."),
 ("Step 4 — AA / no / yes", board(4, "top"),
  f"Small 3x3 buttons, legs in rows {ANS_ROWS[0]} and {ANS_ROWS[1]}, left columns "
  f"{', '.join(map(str, ANS_COL0))}. Same clip-one-leg rule. These are square, so orientation does "
  f"not matter. Test: btntest prints button 0-6. Several dead at once means the GND bus, not the switches."),
 ("Step 5 — the 12 wires, then the LCD", board(5, "top"),
  f"Every signal wire runs along its own row to the riser lane at column {HDR_COLS[0]-1}, then into "
  f"its socket pad; the four that serve right-hand pins carry on underneath the module. Last, the "
  f"4-pin LCD port at cols {LCD_PORT_COL0}-{LCD_PORT_COL0+3} row {LCD_PORT_ROW} and its four wires \u2014 "
  f"the LCD plugs into it on F-F jumpers and is never soldered. Test: firmware/lcdtest prints 'found device at 0x27'."),

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
<div class="key"><strong>One double-sided board, 30 × 42 holes.</strong> Everything lives on it:
the control surface in columns 1–28, the ESP32 in a socket at columns 30–40 with its USB
overhanging the edge. All soldering is done on <em>one</em> face, so the design works whether or
not the holes are plated through. The ESP32 and the LCD both unplug — only the board is
permanent.<br><br>
<strong>Verified in millimetres, not hole counts.</strong> Every figure here is generated from
<code>tools/layout.py</code>, the same file <code>tools/verify-layout.py</code> checks — so a drawing
cannot disagree with the spec. Re-check with
<code>mise exec -- python tools/verify-layout.py</code>.</div>
{body}</body></html>"""
open(OUT, "w").write(page)
print(OUT)
subprocess.run(["open", OUT], check=False)
