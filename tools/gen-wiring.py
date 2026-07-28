#!/usr/bin/env python3
"""Generate WIRING.md -- the flat point-to-point reference.

Three views of the same data, all derived from tools/layout.py:
  A. every wire, hardware end -> socket end
  B. the ESP32 socket slot by slot, all 30, including the unused ones
  C. every component, every leg, and where it goes

    mise exec -- python tools/gen-wiring.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from layout import *

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT  = os.path.join(ROOT, "WIRING.md")

H = harness()
PORT = lcd_port()

# what each socket slot is connected to
conn = {}
for i, (lbl, src, pin, sd, pos, c, r) in enumerate(H, 1):
    conn[(c, r)] = (i, lbl, src)
for n, hole, esp, sk in PORT:
    conn[sk] = (None, f"LCD {n}", f"LCD port, col {hole[0]} row {hole[1]}")

o = []
w = o.append

w("# Wiring reference")
w("")
w("**Generated from `tools/layout.py` — do not edit.** Re-run "
  "`mise exec -- python tools/gen-wiring.py` after any layout change.")
w("")
w(f"Board: {ROWS} rows × {COLS} columns, {BOARD_W:.0f} × {BOARD_H:.0f} mm. "
  f"Grid reference col 1, row 1 = top-left, viewed from the **component side**.")
w("")
w(f"ESP32 seated with **USB pointing at the bottom edge**. Pin positions are counted "
  f"**from the USB end**, so position 1 is the bottom socket (row {HDR_ROWS[1]}) and "
  f"position 15 is the top (row {HDR_ROWS[0]}). The **3V3 column is board col "
  f"{HDR_SIDE_COL['3V3']}** (nearest the controls); the **VIN column is col "
  f"{HDR_SIDE_COL['VIN']}**.")
w("")
w("---")
w("")

# ---------------------------------------------------------------- A
w("## A. Every wire")
w("")
w(f"**{len(H)} soldered signal/ground wires + {len(PORT)} LCD-port wires = {len(H)+len(PORT)} total.**")
w("")
w("| # | Wire | From — hardware | From — hole | To — socket hole | ESP32 pin | Slot |")
w("|---:|---|---|---|---|---|---|")
hw = {}
for i, c in enumerate(LED_COLS):   hw[f"LED {i+1} {LED_NAME[i]}"] = f"LED {i+1} ({LED_NAME[i]}) anode, long leg"
for i, c in enumerate(BTN_COL0):   hw[f"button {i+1} {LED_NAME[i]}"] = f"Button {i+1} ({LED_NAME[i]}) signal leg"
for (n, g, d), c0 in zip(ANS_INFO, ANS_COL0): hw[f"{n} ({d})"] = f"'{n}' switch signal leg"
hw["ground"] = f"GND bus (row {GND_WIRE_FROM[1]})"
for i, (lbl, src, pin, sd, pos, c, r) in enumerate(H, 1):
    w(f"| {i} | {lbl} | {hw.get(lbl, lbl)} | {src} | **col {c}, row {r}** | `{pin}` | "
      f"{sd} side, pos {pos} |")
for n, hole, esp, sk in PORT:
    sd, pos = esp_position(esp, gnd_for="lcd")
    w(f"| — | LCD {n} | LCD port male pin | col {hole[0]}, row {hole[1]} | "
      f"**col {sk[0]}, row {sk[1]}** | `{esp}` | {sd} side, pos {pos} |")
w("")
w("> The LCD itself is **not** on this list — it reaches the port with 4 F-F jumpers and "
  "is never soldered.")
w("")

# ---------------------------------------------------------------- B
w("---")
w("")
w("## B. The ESP32 socket, slot by slot")
w("")
w(f"All 30 sockets. **{len(conn)} carry a wire**, the rest are soldered but unused. "
  f"Leave a 2mm stub on the ones marked ●; trim the others flush.")
w("")
for side, names in (("3V3", ESP_3V3_SIDE), ("VIN", ESP_VIN_SIDE)):
    col = HDR_SIDE_COL[side]
    w(f"### {side} side — board column {col}")
    w("")
    w("| Pos | Pin | Board hole | | Connected to |")
    w("|---:|---|---|:-:|---|")
    for i, nm in enumerate(names, 1):
        c, r = socket_hole(side, i)
        if (c, r) in conn:
            num, lbl, src = conn[(c, r)]
            tag = f"wire {num} — {lbl}" if num else lbl
            w(f"| {i} | **{nm}** | col {c}, row {r} | ● | {tag}, from {src} |")
        else:
            w(f"| {i} | {nm} | col {c}, row {r} | | *unused — trim flush* |")
    w("")

# ---------------------------------------------------------------- C
w("---")
w("")
w("## C. Every component, every leg")
w("")
w("Legs that are **not** on this list do not exist — they were clipped off.")
w("")
w("| Part | Leg | Hole | What it connects to |")
w("|---|---|---|---|")
for i, c in enumerate(LED_COLS):
    n = WIRE = next(j for j, (l, *_) in enumerate(H, 1) if l == f"LED {i+1} {LED_NAME[i]}")
    w(f"| **LED {i+1} ({LED_NAME[i]})** | anode, long leg (+) | col {c}, row {LED_ROWS[0]} | "
      f"wire {n} → `D{LED_GPIO[i]}` |")
    w(f"| | cathode, short leg (−) | col {c}, row {LED_ROWS[1]} | bent flat on the underside "
      f"onto the row-{RES_ROWS[0]} pad |")
    w(f"| **220Ω R{i+1}** | top lead | col {c}, row {RES_ROWS[0]} | joins that bent cathode leg |")
    w(f"| | bottom lead | col {c}, row {RES_ROWS[1]} | lands **on the GND bus** |")
for i, c0 in enumerate(BTN_COL0):
    n = next(j for j, (l, *_) in enumerate(H, 1) if l == f"button {i+1} {LED_NAME[i]}")
    legs = dict((role, h) for h, role in switch_legs(c0, BIG_LEG_COLS, BTN_ROWS))
    w(f"| **Button {i+1} ({LED_NAME[i]})** | signal | col {legs['signal'][0]}, row {legs['signal'][1]} | "
      f"wire {n} → `D{BTN_GPIO[i]}` |")
    w(f"| | anchor | col {legs['anchor'][0]}, row {legs['anchor'][1]} | soldered, no connection |")
    w(f"| | ~~clipped~~ | ~~col {legs['clip'][0]}, row {legs['clip'][1]}~~ | **cut this leg off** |")
    w(f"| | ground | col {legs['ground'][0]}, row {legs['ground'][1]} | lands **on the GND bus** |")
for (nm, g, d), c0 in zip(ANS_INFO, ANS_COL0):
    n = next(j for j, (l, *_) in enumerate(H, 1) if l == f"{nm} ({d})")
    legs = dict((role, h) for h, role in switch_legs(c0, SMALL_LEG, ANS_ROWS))
    w(f"| **'{nm}' ({d})** | signal | col {legs['signal'][0]}, row {legs['signal'][1]} | "
      f"wire {n} → `D{g}` |")
    w(f"| | anchor | col {legs['anchor'][0]}, row {legs['anchor'][1]} | soldered, no connection |")
    w(f"| | ~~clipped~~ | ~~col {legs['clip'][0]}, row {legs['clip'][1]}~~ | **cut this leg off** |")
    w(f"| | ground | col {legs['ground'][0]}, row {legs['ground'][1]} | lands **on the GND bus** |")
for i, (nm, hole, esp, sk) in enumerate(PORT):
    w(f"| **LCD port** | pin {i+1} — {nm} | col {hole[0]}, row {hole[1]} | "
      f"wire to `{esp}` at col {sk[0]}, row {sk[1]} |")
w("")
w("---")
w("")
w("## D. The buses")
w("")
w("| Bus | Row | Spans | Carries |")
w("|---|---:|---|---|")
carry = {GND_ROWS[0]: "the four 220Ω bottom leads",
         GND_ROWS[1]: "the four colour-button ground legs",
         GND_ROWS[2]: "the three answer-button ground legs"}
for r in GND_ROWS:
    w(f"| GND | **{r}** | cols {BUS_COLS[0]} → {BUS_COLS[1]} | {carry[r]} |")
w("")
w(f"All three are joined by a bare wire down **column {GND_LINK_COL}**, rows "
  f"{GND_ROWS[0]}–{GND_ROWS[-1]}. One wire (#{next(j for j,(l,*_) in enumerate(H,1) if l=='ground')}) "
  f"carries ground from col {GND_WIRE_FROM[0]}, row {GND_WIRE_FROM[1]} to the ESP32's "
  f"`GND` at col {socket_hole(*esp_position('GND'))[0]}, row "
  f"{socket_hole(*esp_position('GND'))[1]}. There are **no other ground connections** — "
  f"every ground leg sits directly on a bus.")
w("")

open(OUT, "w").write("\n".join(o) + "\n")
print(OUT)
