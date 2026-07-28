#!/usr/bin/env python3
"""Verify the single-board layout physically fits: real body sizes, real overlaps.

Hole counting is not enough -- a 12mm button body is 4.7 holes wide, so parts can
collide even when their legs are in free holes. This checks bounding boxes in mm.

    mise exec -- python tools/verify-layout.py
"""
P = 2.54                      # hole pitch
ROWS, COLS = 18, 24           # kit board PY-5CM*7CM
BOARD_W, BOARD_H = 70.0, 50.0 # physical board
FIELD_W, FIELD_H = (COLS-1)*P, (ROWS-1)*P
BORDER_X = (BOARD_W - FIELD_W)/2
BORDER_Y = (BOARD_H - FIELD_H)/2

def xy(col, row):
    """mm position of a hole, measured from the board's top-left corner."""
    return BORDER_X + (col-1)*P, BORDER_Y + (row-1)*P

# ---- component body sizes (mm) -------------------------------------------
BIG_BTN   = (12.0, 12.0)   # 12x12 tactile, colored cap
SMALL_BTN = (6.0, 6.0)     # 6x6 tactile
LED       = (5.0, 5.0)     # 5mm round
RES       = (2.5, 7.0)     # 1/4W standing vertically

COLS_MAIN = [3, 9, 15, 21]          # 6-hole pitch
COLS_RES  = [5, 11, 17, 23]         # 2 columns right of each LED, clear of its body
COLS_ANS  = [4, 12, 20]

parts = []
def add(name, col, row, size, kind="top"):
    w, h = size
    cx, cy = xy(col, row)
    parts.append(dict(name=name, kind=kind, cx=cx, cy=cy, w=w, h=h,
                      x0=cx-w/2, x1=cx+w/2, y0=cy-h/2, y1=cy+h/2, col=col, row=row))

# LEDs: anode row 3, cathode row 4 -> body centred between them
for i, c in enumerate(COLS_MAIN):
    add(f"LED{i+1}", c, 3.5, LED)
    add(f"R{i+1}", COLS_RES[i], 2.0, RES)   # 220R standing, rows 1-3
# select buttons centred on row 8 (legs land rows 7 and 9)
for i, c in enumerate(COLS_MAIN):
    add(f"BTN{i+1}", c, 8, BIG_BTN)
# answer buttons centred on row 14 (legs rows 13 and 15)
for i, (c, n) in enumerate(zip(COLS_ANS, ["AA", "no", "yes"])):
    add(n, c, 14, SMALL_BTN)

# ---- checks ---------------------------------------------------------------
fails = []

# 1. everything on the physical board
for p in parts:
    if p["x0"] < 0 or p["x1"] > BOARD_W or p["y0"] < 0 or p["y1"] > BOARD_H:
        fails.append(f"{p['name']} hangs off the board: "
                     f"x {p['x0']:.1f}..{p['x1']:.1f} y {p['y0']:.1f}..{p['y1']:.1f}")

# 2. no two bodies overlap
def overlap(a, b):
    return not (a["x1"] <= b["x0"] or b["x1"] <= a["x0"] or
                a["y1"] <= b["y0"] or b["y1"] <= a["y0"])
for i in range(len(parts)):
    for j in range(i+1, len(parts)):
        if overlap(parts[i], parts[j]):
            fails.append(f"{parts[i]['name']} overlaps {parts[j]['name']}")

# 3. ESP32 header rows must be free of top-side legs
LEG_ROWS = set()
for c in COLS_MAIN: LEG_ROWS |= {1, 3, 4, 7, 9}      # resistor, LED, button legs
for c in COLS_ANS:  LEG_ROWS |= {13, 15}
BUS_ROWS = {5, 16, 18}
HEADER = (2, 12)
for r in HEADER:
    if r in LEG_ROWS or r in BUS_ROWS:
        fails.append(f"header row {r} is already used")
if HEADER[1] - HEADER[0] not in (9, 10):
    fails.append(f"header rows {HEADER} are not 9 or 10 apart")

# 4. ESP32 underneath: does its body fit within the board outline?
ESP_W, ESP_L = 28.0, 55.0
hx0, _ = xy(5, HEADER[0]); hx1, _ = xy(19, HEADER[0])
esp_cx = (hx0 + hx1)/2
_, hy0 = xy(5, HEADER[0]); _, hy1 = xy(5, HEADER[1])
esp_cy = (hy0 + hy1)/2
if esp_cx - ESP_L/2 < -6 or esp_cx + ESP_L/2 > BOARD_W + 6:
    fails.append("ESP32 length does not fit along the board")
esp_overhang = max(0, (esp_cy + ESP_W/2) - BOARD_H)

# ---- report ---------------------------------------------------------------
print(f"board  {BOARD_W} x {BOARD_H} mm, {ROWS} rows x {COLS} cols, "
      f"hole field {FIELD_W:.1f} x {FIELD_H:.1f}, border {BORDER_X:.1f}/{BORDER_Y:.1f}\n")
print(f"{'part':<7} {'col':>4} {'row':>5}   {'x range':>14}  {'y range':>14}")
for p in parts:
    print(f"{p['name']:<7} {p['col']:>4} {str(p['row']):>5}   "
          f"{p['x0']:>6.1f}..{p['x1']:<6.1f} {p['y0']:>6.1f}..{p['y1']:<6.1f}")

print(f"\nESP32 (underside): centred {esp_cx:.1f},{esp_cy:.1f}  "
      f"body {ESP_L}x{ESP_W}  overhangs bottom edge by {esp_overhang:.1f}mm "
      f"({'USB reachable' if esp_overhang > 0 else 'flush'})")

gaps = []
for i, c in enumerate(COLS_MAIN[:-1]):
    a = next(p for p in parts if p["name"] == f"BTN{i+1}")
    b = next(p for p in parts if p["name"] == f"BTN{i+2}")
    gaps.append(b["x0"] - a["x1"])
print(f"gap between select-button bodies: {min(gaps):.2f}mm")
led = next(p for p in parts if p["name"] == "LED1")
btn = next(p for p in parts if p["name"] == "BTN1")
print(f"vertical gap LED -> select button: {btn['y0'] - led['y1']:.2f}mm")
b1 = next(p for p in parts if p["name"] == "BTN1")
a1 = next(p for p in parts if p["name"] == "AA")
print(f"vertical gap select -> answer row : {a1['y0'] - b1['y1']:.2f}mm")

print()
if fails:
    print("FAILS:")
    for f in fails: print("  x", f)
else:
    print("PASS — all 7 buttons, 4 LEDs, 4 resistors and the ESP32 fit on one kit board.")
