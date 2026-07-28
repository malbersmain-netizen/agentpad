#!/usr/bin/env python3
"""Verify the single-board layout physically fits: real footprints, real overlaps.

Hole counting is not enough -- parts collide even when their legs sit in free holes.
This works in millimetres and checks bounding boxes.

MEASURED on the actual kit parts:
  colored buttons: pins 3 holes ACROSS (2 pitches, 5.08mm) and 6 holes LONG
                   (5 pitches, 12.7mm) -- e.g. legs in rows 6 and 11.
  small buttons:   3x3 holes (2 pitches both ways).

    mise exec -- python tools/verify-layout.py
"""
P = 2.54
ROWS, COLS = 18, 24
BOARD_W, BOARD_H = 70.0, 50.0
FIELD_W, FIELD_H = (COLS-1)*P, (ROWS-1)*P
BX, BY = (BOARD_W-FIELD_W)/2, (BOARD_H-FIELD_H)/2

def xy(col, row):
    return BX + (col-1)*P, BY + (row-1)*P

# ---- footprints -----------------------------------------------------------
# MEASURED: colored button pins are 3 holes across (2 pitches) and 6 holes long
# (5 pitches). Small buttons are 3x3 (2 pitches both ways).
BIG_LEG_COLS = 2         # pitches between the two leg COLUMNS
BIG_LEG_ROWS = 5         # pitches between the two leg ROWS
SMALL_LEG = 2
BIG_BODY   = 12.0
SMALL_BODY = 6.0
LED_D, RES = 5.0, (2.5, 7.0)

# 6-column pitch keeps 3.24mm between the 12mm bodies
LED_COLS  = [3, 9, 15, 21]              # LEDs and buttons share these centre columns
RES_COLS  = [6, 12, 18, 24]             # resistors stand in the gaps between buttons
BTN_COL0  = [c-1 for c in LED_COLS]     # legs at c-1 and c+1
BTN_ROWS  = (6, 11)                     # MEASURED
ANS_COL0  = [3, 11, 19]
ANS_ROWS  = (14, 14+SMALL_LEG)
HEADER    = (4, 13)                     # 9 apart, both rows clear of every body
GND_ROWS  = (5, 17)
V5_ROW    = 18
LED_ROWS  = (2, 3)                      # anode row 2, cathode row 3
RES_ROWS  = (1, 3)

parts, fails = [], []
def add(name, cx, cy, w, h, col=None, row=None):
    parts.append(dict(name=name, x0=cx-w/2, x1=cx+w/2, y0=cy-h/2, y1=cy+h/2,
                      col=col, row=row))

# LEDs + resistors
for i, c in enumerate(LED_COLS):
    x, y = xy(c, 2.5); add(f"LED{i+1}", x, y, LED_D, LED_D, c, "2-3")
    x, y = xy(RES_COLS[i], 2.0); add(f"R{i+1}", x, y, RES[0], RES[1], RES_COLS[i], "1-3")
# select buttons: body centred between the leg holes
for i, c0 in enumerate(BTN_COL0):
    x0, y0 = xy(c0, BTN_ROWS[0]); x1, y1 = xy(c0+BIG_LEG_COLS, BTN_ROWS[1])
    add(f"BTN{i+1}", (x0+x1)/2, (y0+y1)/2, BIG_BODY, BIG_BODY, f"{c0}-{c0+BIG_LEG_COLS}",
        f"{BTN_ROWS[0]}-{BTN_ROWS[1]}")
# answer buttons
for (n, c0) in zip(["AA", "no", "yes"], ANS_COL0):
    x0, y0 = xy(c0, ANS_ROWS[0]); x1, y1 = xy(c0+SMALL_LEG, ANS_ROWS[1])
    add(n, (x0+x1)/2, (y0+y1)/2, SMALL_BODY, SMALL_BODY, f"{c0}-{c0+SMALL_LEG}",
        f"{ANS_ROWS[0]}-{ANS_ROWS[1]}")

# 1. on the board?
for p in parts:
    if p["x0"] < 0 or p["x1"] > BOARD_W or p["y0"] < 0 or p["y1"] > BOARD_H:
        fails.append(f"{p['name']} off the board: x {p['x0']:.1f}..{p['x1']:.1f} y {p['y0']:.1f}..{p['y1']:.1f}")
# 2. overlaps
for i in range(len(parts)):
    for j in range(i+1, len(parts)):
        a, b = parts[i], parts[j]
        if not (a["x1"] <= b["x0"] or b["x1"] <= a["x0"] or a["y1"] <= b["y0"] or b["y1"] <= a["y0"]):
            fails.append(f"{a['name']} overlaps {b['name']}")
# 3. header rows clear of every top-side lead, AND not under a button body
used = set(LED_ROWS) | set(RES_ROWS) | set(BTN_ROWS) | set(ANS_ROWS) | set(GND_ROWS) | {V5_ROW}
under_btn = set(range(BTN_ROWS[0], BTN_ROWS[1]+1))
for r in HEADER:
    if r in used:      fails.append(f"header row {r} already carries leads")
    if r in under_btn: fails.append(f"header row {r} sits under a button body")
if HEADER[1]-HEADER[0] not in (9, 10):
    fails.append(f"header rows {HEADER} not 9 or 10 apart")

# 4. ESP32 underneath
ESP_L, ESP_W = 55.0, 28.0
x0, _ = xy(5, 1); x1, _ = xy(19, 1)
_, y0 = xy(1, HEADER[0]); _, y1 = xy(1, HEADER[1])
ecx, ecy = (x0+x1)/2, (y0+y1)/2
if ecx-ESP_L/2 < -8 or ecx+ESP_L/2 > BOARD_W+8: fails.append("ESP32 too long for the board")

print(f"board {BOARD_W}x{BOARD_H}mm  {ROWS} rows x {COLS} cols  field {FIELD_W:.1f}x{FIELD_H:.1f}\n")
print(f"{'part':<7} {'cols':>8} {'rows':>7}   {'x mm':>14}  {'y mm':>14}")
for p in parts:
    print(f"{p['name']:<7} {str(p['col']):>8} {str(p['row']):>7}   "
          f"{p['x0']:>6.1f}..{p['x1']:<6.1f} {p['y0']:>6.1f}..{p['y1']:<6.1f}")

b = [p for p in parts if p["name"].startswith("BTN")]
print(f"\nselect buttons: legs 3 across x 6 long -> leg columns "
      f"{[f'{c}-{c+BIG_LEG_COLS}' for c in BTN_COL0]}")
print(f"  gap between button bodies : {b[1]['x0']-b[0]['x1']:.2f}mm")
led = next(p for p in parts if p["name"] == "LED1")
print(f"  LED -> button vertical gap: {b[0]['y0']-led['y1']:.2f}mm")
aa = next(p for p in parts if p["name"] == "AA")
print(f"  button -> answer row gap  : {aa['y0']-b[0]['y1']:.2f}mm")
print(f"  ESP32 (under): {ESP_L}x{ESP_W} centred {ecx:.1f},{ecy:.1f}")
print(f"\nrow plan: {RES_ROWS[0]}-{RES_ROWS[1]} resistors | {LED_ROWS[0]}-{LED_ROWS[1]} LEDs | "
      f"{HEADER[0]} HEADER | {GND_ROWS[0]} GND | {BTN_ROWS[0]}+{BTN_ROWS[1]} button legs | "
      f"{HEADER[1]} HEADER | {ANS_ROWS[0]}+{ANS_ROWS[1]} answer legs | {GND_ROWS[1]} GND | {V5_ROW} 5V+LCD")
print()
if fails:
    print("FAILS:"); [print("  x", f) for f in fails]
else:
    print("PASS — 7 buttons, 4 LEDs, 4 resistors and the ESP32 fit one kit board.")
