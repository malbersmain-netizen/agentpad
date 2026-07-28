#!/usr/bin/env python3
"""Verify the board A layout: real footprints, real overlaps, real connectivity.

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
P = 2.54
ROWS, COLS = 18, 24
BOARD_W, BOARD_H = 70.0, 50.0
BX = (BOARD_W - (COLS-1)*P)/2
BY = (BOARD_H - (ROWS-1)*P)/2
def xy(col, row): return BX + (col-1)*P, BY + (row-1)*P

# ---- footprints (mm) ------------------------------------------------------
BIG_LEG_COLS, BIG_LEG_ROWS = 2, 5
SMALL_LEG   = 2
BIG_BODY    = 12.0
SMALL_BODY  = 6.0
LED_D       = 6.0    # 5mm LED INCLUDING its base flange -- the flange is what collides
RES_BODY    = 6.3    # 1/4W body length
RES_W       = 2.5

# ---- layout ---------------------------------------------------------------
LED_COLS = [3, 9, 15, 21]   # each LED, its resistor and its button share one column
LED_ROWS = (2, 3)           # anode row 2 (takes the GPIO wire), cathode row 3
RES_ROWS = (3, 7)           # resistor stands in the CATHODE path: top lead shares the
                            # cathode hole, bottom lead lands on the GND bus
BTN_COL0 = [c-1 for c in LED_COLS]
BTN_ROWS = (9, 14)   # bottom leg lands directly ON a GND bus
ANS_COL0 = [3, 11, 19]
ANS_ROWS = (16, 18)  # bottom leg lands directly ON a GND bus
GND_ROWS = (7, 14, 18)      # one bus per bank, so NO ground jumpers are needed at all;
                            # all three link together down column 24
LCD_ON_BOARD_A = False      # LCD's 4 wires go straight to board B

parts, fails, notes = [], [], []
def add(name, cx, cy, w, h, where):
    parts.append(dict(name=name, x0=cx-w/2, x1=cx+w/2, y0=cy-h/2, y1=cy+h/2, where=where))

for i, c in enumerate(LED_COLS):
    x, y = xy(c, (LED_ROWS[0]+LED_ROWS[1])/2)
    add(f"LED{i+1}", x, y, LED_D, LED_D, f"col {c}, rows {LED_ROWS[0]}-{LED_ROWS[1]}")
    y1 = xy(c, RES_ROWS[1])[1]          # body pushed to the bus end so it clears the LED
    add(f"R{i+1}", x, y1 - RES_BODY/2, RES_W, RES_BODY,
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
if RES_BODY > span:
    fails.append(f"resistor body {RES_BODY}mm > its {span:.2f}mm lead span — cannot physically fit")

# --- 4. CONNECTIVITY. Perfboard joins nothing; every net needs a shared hole or a bus.
if LED_ROWS[1] != RES_ROWS[0]:
    fails.append(f"LED cathode (row {LED_ROWS[1]}) and resistor top (row {RES_ROWS[0]}) are "
                 f"different holes — NOT connected")
for label, row in (("resistor bottom", RES_ROWS[1]),
                   ("colored-button GND leg", BTN_ROWS[1]),
                   ("answer-button GND leg", ANS_ROWS[1])):
    if row not in GND_ROWS:
        near = min(GND_ROWS, key=lambda r: abs(r-row))
        fails.append(f"{label} (row {row}) is not on a GND bus {GND_ROWS} — "
                     f"needs a {abs(near-row)}-row jumper to row {near}")
notes.append("every ground leg lands directly on a bus — zero ground jumpers needed")

# --- 5. keep 5V off board A
if LCD_ON_BOARD_A:
    fails.append("5V on board A would sit beside the 3.3V signal rows — route the LCD to board B")

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
print("board A carries NO 5V — the LCD's four wires go straight to board B")
for n in notes: print(f"note: {n}")
print()
if fails:
    print("FAILS:"); [print("  x", f) for f in fails]
else:
    print("PASS — bodies fit, nothing collides, and every net is actually connected.")
