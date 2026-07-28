#!/usr/bin/env python3
"""Verify the board layout: real footprints, real overlaps, real connectivity.

Classes of error this catches that hole-counting does not:
  1. BODIES that collide even when the legs sit in free holes.
  2. NETS that are not actually connected. On a breadboard, holes in a row are joined
     for you. On perfboard nothing is joined until you join it -- an earlier version of
     this layout put the resistors in different holes from the LED anodes, wired to
     nothing at all, and every "PASS" missed it.
  3. CONNECTORS with nowhere to land. The LCD was documented for months as "4 jumpers
     onto the ESP32's own pins" -- which are inside the socket the moment the module is
     seated, and therefore unreachable. Hence the on-board LCD port.
  4. MOUNTING that does not fit. The grid leaves ~2.5mm of margin all round, so the
     3.5mm corner holes an earlier draft called for could not be drilled at all.

MEASURED on the actual kit parts:
  colored buttons: pins 3 holes ACROSS (2 pitches) x 6 holes LONG (5 pitches)
  small buttons:   3x3 holes (2 pitches both ways)
  ESP32:           11 holes across (pin rows 1.0in apart) x 15 long -- socketed on the
                   same board at cols 30-40

ONE DOUBLE-SIDED BOARD. All soldering is done on a single face regardless, so the design
does not depend on the holes being plated through. The control surface carries no 5V at
all -- the only 5V is the LCD port, over at the ESP32 columns.

    mise exec -- python tools/verify-layout.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from layout import *          # single source of truth -- see tools/layout.py

fails, notes = [], []
parts = bodies()
ESP_GROUP = {"ESP32", f"socket c{HDR_COLS[0]}", f"socket c{HDR_COLS[1]}"}

# --- 1. everything on the board
for p in parts:
    if p["x0"] < 0 or p["x1"] > BOARD_W or p["y0"] < 0 or p["y1"] > BOARD_H:
        # the ESP32 module is allowed to hang over an edge; nothing else is
        if p["name"] != "ESP32":
            fails.append(f"{p['name']} off the board "
                         f"({p['x0']:.1f}..{p['x1']:.1f}, {p['y0']:.1f}..{p['y1']:.1f})")

# --- 2. no two bodies overlap (strict: touching counts)
for i in range(len(parts)):
    for j in range(i+1, len(parts)):
        a, b = parts[i], parts[j]
        if a["name"] in ESP_GROUP and b["name"] in ESP_GROUP:
            continue                       # the module legitimately sits over its sockets
        if a["x1"] > b["x0"] and b["x1"] > a["x0"] and a["y1"] > b["y0"] and b["y1"] > a["y0"]:
            ov = min(min(a['x1'],b['x1'])-max(a['x0'],b['x0']),
                     min(a['y1'],b['y1'])-max(a['y0'],b['y0']))
            fails.append(f"{a['name']} overlaps {b['name']} by {ov:.2f}mm")

# --- 3. a part's body must fit between its own leads
span = (RES_ROWS[1]-RES_ROWS[0]) * P
if RES_BODY + 2*BEND > span:
    fails.append(f"resistor needs {RES_BODY}mm body + 2x{BEND}mm bend allowance = "
                 f"{RES_BODY+2*BEND:.2f}mm but its lead span is only {span:.2f}mm")

# --- 4. HOLE OCCUPANCY. A 1.0mm hole holds exactly one lead.
holes = occupied_holes()
for (col, row), owners in sorted(holes.items()):
    if len(owners) > 1:
        fails.append(f"hole (col {col}, row {row}) has {len(owners)} leads: "
                     f"{', '.join(owners)} — a {HOLE_D}mm hole takes one")

# --- 5. CONNECTIVITY
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

# A tactile switch is two internally-joined pairs, and WHICH pair is which depends on the
# part. The kit's switches join the LONG way (down the columns); the first draft of this
# layout assumed the short way. Rather than depend on the measurement, the build clips one
# leg -- and this check PROVES that choice is safe under BOTH pairings by simulating each.
for label, cols, span, rows in (("colored button", BTN_COL0, BIG_LEG_COLS, BTN_ROWS),
                                ("answer button",  ANS_COL0, SMALL_LEG,    ANS_ROWS)):
    for c0 in cols:
        legs     = switch_legs(c0, span, rows)
        soldered = {h for h, role in legs if role != "clip"}
        wire_at  = next(h for h, role in legs if role == "signal")
        for hyp, key in (("row-wise", lambda L: L[1]), ("column-wise", lambda L: L[0])):
            sig = {h for h, _ in legs if key(h) == key(wire_at)} & soldered
            gnd = {h for h, _ in legs if key(h) != key(wire_at)} & soldered
            short = [h for h in sig if h[1] in GND_ROWS]
            if short:
                fails.append(f"{label} at col {c0}: if the joined pairs run {hyp}, the signal "
                             f"node reaches the GND bus at {short} — dead short")
            if not any(h[1] in GND_ROWS for h in gnd):
                fails.append(f"{label} at col {c0}: if the joined pairs run {hyp}, no soldered "
                             f"ground leg lands on a bus — the switch cannot pull the pin down")
            if wire_at not in sig:
                fails.append(f"{label} at col {c0}: the signal wire does not land on the "
                             f"switch's signal node under {hyp} pairing")
    if rows[1] not in GND_ROWS:
        fails.append(f"{label} ground row {rows[1]} is not a bus row")
notes.append("every switch has ONE leg clipped, which makes the board work whichever way "
             "that switch's internal pairs run — proven above for both cases")

# the GND link is BARE wire running between the buses. Every signal wire runs along its
# own row from its part out to the riser lane, so any signal row that passes over the
# link column is one nicked insulator away from a dead short to ground.
SPINE = HDR_COLS[0] - 1
crossings = [lbl for lbl, src, pin, *_ in harness()
             if pin != "GND" and src.startswith("col")
             and GND_ROWS[0] <= int(src.split("row ")[1]) <= GND_ROWS[-1]
             and int(src.split()[1].rstrip(",")) < GND_LINK_COL <= SPINE]
if crossings:
    fails.append(f"{len(crossings)} signal wires run straight over the bare GND link at col "
                 f"{GND_LINK_COL}: {', '.join(crossings)}")

# leg rows/cols must exist
for label, rows in (("colored button", BTN_ROWS), ("answer button", ANS_ROWS),
                    ("LED", LED_ROWS), ("resistor", RES_ROWS)):
    for r in rows:
        if not 1 <= r <= ROWS: fails.append(f"{label} leg row {r} is off the board")
if BTN_ROWS[1]-BTN_ROWS[0] != BIG_LEG_ROWS:
    fails.append(f"colored-button leg rows differ by {BTN_ROWS[1]-BTN_ROWS[0]}, measured {BIG_LEG_ROWS}")
if ANS_ROWS[1]-ANS_ROWS[0] != SMALL_LEG:
    fails.append(f"answer-button leg rows differ by {ANS_ROWS[1]-ANS_ROWS[0]}, measured {SMALL_LEG}")

# --- 6. the ESP32 block must not overlap the control surface
if BUS_COLS[1] >= HDR_COLS[0]:
    fails.append(f"GND buses run to col {BUS_COLS[1]} but the ESP32 starts at col {HDR_COLS[0]}")
esp = next(p for p in parts if p["name"] == "ESP32")
if HDR_ROWS[1]-HDR_ROWS[0] != 14:
    fails.append(f"socket is {HDR_ROWS[1]-HDR_ROWS[0]+1} holes long, the ESP32 has 15 pins a side")
if HDR_COLS[1]-HDR_COLS[0] != 10:
    fails.append(f"socket columns are {HDR_COLS[1]-HDR_COLS[0]} apart, the ESP32 measures 10")

# --- 7. the LCD must have somewhere to plug in
if LCD_SOLDERED:
    fails.append("the LCD must stay on jumpers so it remains a reusable part")
port = lcd_port()
if len(port) != len(LCD_PINS):
    fails.append("the LCD port does not carry every LCD pin")
pbody = next(p for p in parts if p["name"] == "LCD port")
if pbody["y1"] > esp["y0"] and esp["y1"] > pbody["y0"] and \
   pbody["x1"] > esp["x0"] and esp["x1"] > pbody["x0"]:
    fails.append("the LCD port is underneath the ESP32 module — a jumper cannot reach it")
for name, hole, pin, sock in port:
    if len(holes.get(hole, [])) != 1:
        fails.append(f"LCD port pin {name} at {hole} is not a clean single-lead hole")
notes.append(f"LCD port: 4 male pins at cols {LCD_PORT_COL0}-{LCD_PORT_COL0+3}, row "
             f"{LCD_PORT_ROW}, {esp['y0']-pbody['y1']:.1f}mm clear of the module")

# --- 8. mounting has to be physically possible
mounts = mount_holes()
if len(mounts) < 4:
    fails.append(f"only {len(mounts)} usable mounting positions found — need 4")
for col, row in mounts:
    if (col, row) in holes:
        fails.append(f"mount hole (col {col}, row {row}) already has a lead in it")
    x, y = xy(col, row)
    edge = min(x, BOARD_W-x, y, BOARD_H-y) - MOUNT_DRILL/2
    if edge < EDGE_MIN:
        fails.append(f"mount hole (col {col}, row {row}) leaves only {edge:.1f}mm to the edge")
if MOUNT_DRILL/2 >= P/2:
    fails.append(f"a {MOUNT_DRILL}mm mount hole eats into the neighbouring pads "
                 f"({P/2:.2f}mm away)")

# --- 9. where the USB cable actually comes out
usb_gap = BOARD_H - esp["y1"]
if usb_gap > 0:
    notes.append(f"the USB connector stops {usb_gap:.1f}mm SHORT of the bottom edge — it does "
                 f"not overhang. The module sits ~8mm up on the socket, so the cable clears "
                 f"the board, but rows {int((esp['y1']-BY)/P)+2}-{ROWS} at cols "
                 f"{HDR_COLS[0]}-{HDR_COLS[1]} must stay free of tall parts")
    for p in parts:
        if p["name"] in ESP_GROUP: continue
        if p["y0"] > esp["y1"] and p["x1"] > esp["x0"] and esp["x1"] > p["x0"]:
            fails.append(f"{p['name']} sits in the USB cable's exit path")

notes.append("every ground leg lands directly on a bus — zero ground jumpers needed")
notes.append(f"{len(holes)} holes used, max 1 lead each")

# ---------------------------------------------------------------- report
print(f"board {BOARD_W}x{BOARD_H}mm · {ROWS} rows x {COLS} cols · "
      f"margins {BX:.2f}mm side, {BY:.2f}mm top/bottom\n")
print(f"{'part':<12} {'where':<38} {'x mm':>13}  {'y mm':>13}")
for p in parts:
    print(f"{p['name']:<12} {p['where']:<38} {p['x0']:>5.1f}..{p['x1']:<6.1f} {p['y0']:>5.1f}..{p['y1']:<6.1f}")

b   = [p for p in parts if p["name"].startswith("BTN")]
led = parts[0]; r1 = parts[1]
ans = next(p for p in parts if p["name"] == "AA")
print("\nclearances:")
print(f"  between button bodies   {b[1]['x0']-b[0]['x1']:>6.2f} mm")
print(f"  LED -> its resistor     {r1['y0']-led['y1']:>6.2f} mm")
print(f"  resistor -> button      {b[0]['y0']-r1['y1']:>6.2f} mm")
print(f"  button -> answer row    {ans['y0']-b[0]['y1']:>6.2f} mm")
print(f"  controls -> ESP32 body  {esp['x0']-b[-1]['x1']:>6.2f} mm")
print(f"  resistor body {RES_BODY}mm in a {span:.2f}mm lead span")

used = set(LED_ROWS)|set(RES_ROWS)|set(BTN_ROWS)|set(ANS_ROWS)|set(GND_ROWS)
print(f"\nrow plan: {LED_ROWS[0]} LED anode+GPIO | {LED_ROWS[1]} LED cathode (leg bends to row {RES_ROWS[0]}) | {RES_ROWS[0]} resistor top | "
      f"{GND_ROWS[0]} GND bus | {BTN_ROWS[0]}+{BTN_ROWS[1]} button legs | "
      f"{ANS_ROWS[0]}+{ANS_ROWS[1]} answer legs | {GND_ROWS[1]} GND bus")
print(f"spare rows on the control surface: {sorted(set(range(1, ROWS+1)) - used)}")
print(f"mount holes (M{int(MOUNT_DRILL*10//10)} / {MOUNT_DRILL}mm drill): "
      + ", ".join(f"col {c} row {r}" for c, r in mounts))
print(f"ONE board. ESP32 socketed at cols {HDR_COLS[0]}-{HDR_COLS[1]}, rows {HDR_ROWS[0]}-{HDR_ROWS[1]}. "
      f"No 5V on the control surface.")
for n in notes: print(f"note: {n}")

print()
if fails:
    print("FAILS:"); [print("  x", f) for f in fails]; sys.exit(1)
print("PASS — bodies fit, nothing collides, every net is connected, "
      "and both connectors have somewhere to land.")
