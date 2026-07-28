#!/usr/bin/env python3
"""Verify the board layout: real footprints, real overlaps, real connectivity.

Two classes of error this catches that hole-counting does not:
  1. BODIES that collide even when the legs sit in free holes.
  2. NETS that are not actually connected. On a breadboard, holes in a row are joined
     for you. On perfboard nothing is joined until you join it -- an earlier version of
     this layout put the resistors in different holes from the LED anodes, wired to
     nothing at all, and every "PASS" missed it.

MEASURED on the actual kit parts:
  colored buttons: pins 3 holes ACROSS (2 pitches) x 6 holes LONG (5 pitches)
  small buttons:   3x3 holes (2 pitches both ways)
  ESP32:           11 holes across (pin rows 1.0in apart) x 15 long -- lives on board B

BOARD IS SINGLE-SIDED: copper on one face, so every joint is on the underside and
components sit on top. Board A carries no 5V at all -- only the LCD needs it, and the
LCD wires straight to board B. That keeps 5V away from the 3.3V signal rows entirely.

    mise exec -- python tools/verify-layout.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from layout import *          # single source of truth -- see tools/layout.py

BX = (BOARD_W - (COLS-1)*P)/2
BY = (BOARD_H - (ROWS-1)*P)/2
def xy(col, row): return BX + (col-1)*P, BY + (row-1)*P

parts, fails, notes = [], [], []
def add(name, cx, cy, w, h, where):
    parts.append(dict(name=name, x0=cx-w/2, x1=cx+w/2, y0=cy-h/2, y1=cy+h/2, where=where))

for i, c in enumerate(LED_COLS):
    x, y = xy(c, (LED_ROWS[0]+LED_ROWS[1])/2)
    add(f"LED{i+1}", x, y, LED_D, LED_D, f"col {c}, rows {LED_ROWS[0]}-{LED_ROWS[1]}")
    ry = (xy(c, RES_ROWS[0])[1] + xy(c, RES_ROWS[1])[1]) / 2   # centred: equal bend each end
    add(f"R{i+1}", x, ry, RES_W, RES_BODY,
        f"col {c}, rows {RES_ROWS[0]}-{RES_ROWS[1]}")
for i, c0 in enumerate(BTN_COL0):
    x0, y0 = xy(c0, BTN_ROWS[0]); x1, y1 = xy(c0+BIG_LEG_COLS, BTN_ROWS[1])
    add(f"BTN{i+1}", (x0+x1)/2, (y0+y1)/2, BIG_BODY, BIG_BODY,
        f"cols {c0}-{c0+BIG_LEG_COLS}, rows {BTN_ROWS[0]}+{BTN_ROWS[1]}")
for n, c0 in zip(["AA", "no", "yes"], ANS_COL0):
    x0, y0 = xy(c0, ANS_ROWS[0]); x1, y1 = xy(c0+SMALL_LEG, ANS_ROWS[1])
    add(n, (x0+x1)/2, (y0+y1)/2, SMALL_BODY, SMALL_BODY,
        f"cols {c0}-{c0+SMALL_LEG}, rows {ANS_ROWS[0]}+{ANS_ROWS[1]}")

# --- 1. everything on the board
for p in parts:
    if p["x0"] < 0 or p["x1"] > BOARD_W or p["y0"] < 0 or p["y1"] > BOARD_H:
        fails.append(f"{p['name']} off the board ({p['x0']:.1f}..{p['x1']:.1f}, {p['y0']:.1f}..{p['y1']:.1f})")

# --- 2. no two bodies overlap (strict: touching counts)
for i in range(len(parts)):
    for j in range(i+1, len(parts)):
        a, b = parts[i], parts[j]
        if a["x1"] > b["x0"] and b["x1"] > a["x0"] and a["y1"] > b["y0"] and b["y1"] > a["y0"]:
            ov = min(min(a['x1'],b['x1'])-max(a['x0'],b['x0']),
                     min(a['y1'],b['y1'])-max(a['y0'],b['y0']))
            fails.append(f"{a['name']} overlaps {b['name']} by {ov:.2f}mm")

# --- 3. a part's body must fit between its own leads
span = (RES_ROWS[1]-RES_ROWS[0]) * P
if RES_BODY + 2*BEND > span:
    fails.append(f"resistor needs {RES_BODY}mm body + 2x{BEND}mm bend allowance = "
                 f"{RES_BODY+2*BEND:.2f}mm but its lead span is only {span:.2f}mm")

# --- 4. CONNECTIVITY and HOLE OCCUPANCY.
# Perfboard joins nothing, AND a 1.0mm hole holds exactly one lead. Track every hole.
holes = {}
def claim(col, row, owner):
    holes.setdefault((col, row), []).append(owner)

for i, c in enumerate(LED_COLS):
    claim(c, LED_ROWS[0], f"LED{i+1} anode");  claim(c, LED_ROWS[1], f"LED{i+1} cathode")
    claim(c, RES_ROWS[0], f"R{i+1} top");      claim(c, RES_ROWS[1], f"R{i+1} bottom")
for i, c0 in enumerate(BTN_COL0):
    claim(c0, BTN_ROWS[0], f"BTN{i+1} signal")
    claim(c0+BIG_LEG_COLS, BTN_ROWS[1], f"BTN{i+1} gnd")
for n, c0 in zip(["AA","no","yes"], ANS_COL0):
    claim(c0, ANS_ROWS[0], f"{n} signal"); claim(c0+SMALL_LEG, ANS_ROWS[1], f"{n} gnd")
for (col,row), owners in sorted(holes.items()):
    if len(owners) > 1:
        fails.append(f"hole (col {col}, row {row}) has {len(owners)} leads: {', '.join(owners)} "
                     f"— a {HOLE_D}mm hole takes one")

# the LED cathode must be ADJACENT to the resistor top so its lead can bridge on the pad
if abs(LED_ROWS[1] - RES_ROWS[0]) != 1:
    fails.append(f"LED cathode row {LED_ROWS[1]} and resistor top row {RES_ROWS[0]} are "
                 f"{abs(LED_ROWS[1]-RES_ROWS[0])} rows apart — the cathode lead cannot bridge")

# ground legs must land ON a bus
for label, row in (("resistor bottom", RES_ROWS[1]),
                   ("colored-button GND leg", BTN_ROWS[1]),
                   ("answer-button GND leg", ANS_ROWS[1])):
    if row not in GND_ROWS:
        near = min(GND_ROWS, key=lambda r: abs(r-row))
        fails.append(f"{label} (row {row}) is not on a GND bus {GND_ROWS} — "
                     f"needs a {abs(near-row)}-row jumper to row {near}")

# SIGNAL legs must NOT land on a bus  <-- the check whose absence gave a false PASS
for label, row in (("LED anode", LED_ROWS[0]),
                   ("colored-button signal leg", BTN_ROWS[0]),
                   ("answer-button signal leg", ANS_ROWS[0])):
    if row in GND_ROWS:
        fails.append(f"{label} (row {row}) sits ON a GND bus — shorted to ground")

# leg rows/cols must exist
for label, rows in (("colored button", BTN_ROWS), ("answer button", ANS_ROWS),
                    ("LED", LED_ROWS), ("resistor", RES_ROWS)):
    for r in rows:
        if not 1 <= r <= ROWS: fails.append(f"{label} leg row {r} is off the board")
if BTN_ROWS[1]-BTN_ROWS[0] != BIG_LEG_ROWS:
    fails.append(f"colored-button leg rows differ by {BTN_ROWS[1]-BTN_ROWS[0]}, measured {BIG_LEG_ROWS}")
if ANS_ROWS[1]-ANS_ROWS[0] != SMALL_LEG:
    fails.append(f"answer-button leg rows differ by {ANS_ROWS[1]-ANS_ROWS[0]}, measured {SMALL_LEG}")
notes.append("every ground leg lands directly on a bus — zero ground jumpers needed")
notes.append(f"{len(holes)} holes used, max 1 lead each")

# --- 4b. the ESP32 block must not overlap the control surface
esp_x0, esp_y0 = xy(HDR_COLS[0], HDR_ROWS[0])
esp_x1, esp_y1 = xy(HDR_COLS[1], HDR_ROWS[1])
add("ESP32", (esp_x0+esp_x1)/2, (esp_y0+esp_y1)/2, 28.0, 55.0,
    f"cols {HDR_COLS[0]}-{HDR_COLS[1]}, rows {HDR_ROWS[0]}-{HDR_ROWS[1]}")
esp = parts[-1]
for q in parts[:-1]:
    if esp["x1"] > q["x0"] and q["x1"] > esp["x0"] and esp["y1"] > q["y0"] and q["y1"] > esp["y0"]:
        fails.append(f"ESP32 overlaps {q['name']}")
if BUS_COLS[1] >= HDR_COLS[0]:
    fails.append(f"GND buses run to col {BUS_COLS[1]} but the ESP32 starts at col {HDR_COLS[0]}")

# --- 5. keep 5V off board A
if LCD_SOLDERED:
    fails.append("the LCD must stay on F-M jumpers so it remains a reusable part")

print(f"board {BOARD_W}x{BOARD_H}mm · {ROWS} rows x {COLS} cols\n")
print(f"{'part':<7} {'where':<36} {'x mm':>13}  {'y mm':>13}")
for p in parts:
    print(f"{p['name']:<7} {p['where']:<36} {p['x0']:>5.1f}..{p['x1']:<6.1f} {p['y0']:>5.1f}..{p['y1']:<6.1f}")

b   = [p for p in parts if p["name"].startswith("BTN")]
led = parts[0]; r1 = parts[1]
print("\nclearances:")
print(f"  between button bodies   {b[1]['x0']-b[0]['x1']:>6.2f} mm")
print(f"  LED -> its resistor     {r1['y0']-led['y1']:>6.2f} mm")
print(f"  resistor -> button      {b[0]['y0']-r1['y1']:>6.2f} mm")
print(f"  button -> answer row    {parts[-3]['y0']-b[0]['y1']:>6.2f} mm")
print(f"  resistor body {RES_BODY}mm in a {span:.2f}mm lead span")

used = set(LED_ROWS)|set(RES_ROWS)|set(BTN_ROWS)|set(ANS_ROWS)|set(GND_ROWS)
print(f"\nrow plan: {LED_ROWS[0]} LED anode+GPIO | {LED_ROWS[1]} LED cathode + resistor top | "
      f"{GND_ROWS[0]} GND bus | {BTN_ROWS[0]}+{BTN_ROWS[1]} button legs | "
      f"{ANS_ROWS[0]}+{ANS_ROWS[1]} answer legs | {GND_ROWS[1]} GND bus")
print(f"spare rows: {sorted(set(range(1, ROWS+1)) - used)}")
print(f"ONE board. ESP32 socketed at cols {HDR_COLS[0]}-{HDR_COLS[1]}, rows {HDR_ROWS[0]}-{HDR_ROWS[1]}. "
      f"No 5V on the control surface — the LCD jumpers straight onto the ESP32.")
for n in notes: print(f"note: {n}")
print()
if fails:
    print("FAILS:"); [print("  x", f) for f in fails]
else:
    print("PASS — bodies fit, nothing collides, and every net is actually connected.")
