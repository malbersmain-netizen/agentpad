#!/usr/bin/env python3
"""Regenerate BUILD.md's volatile tables from tools/layout.py.

Everything between a <!-- GEN:name --> / <!-- /GEN:name --> pair is replaced. Those
sections are the ones that kept drifting out of sync with the layout -- four times,
and the last time the wire table would have sent seven signal wires onto ground buses.
They are now derived, so they cannot disagree with the verifier.

    mise exec -- python tools/gen-tables.py
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from layout import *

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOC  = os.path.join(ROOT, "BUILD.md")

def rowplan():
    rows = {}
    def put(r, s): rows.setdefault(r, []).append(s)
    put(LED_ROWS[0], f"**LED anodes (+)** — each also takes that LED's wire to the socket · cols {', '.join(map(str, LED_COLS))}")
    put(LED_ROWS[1], f"**LED cathodes (−)** — lead bends over on the copper face to the row-{RES_ROWS[0]} pad")
    put(RES_ROWS[0], f"220Ω top lead (the only thing in this hole)")
    put(RES_ROWS[1], f"220Ω bottom lead — lands on the bus")
    for r in GND_ROWS: put(r, f"**GND bus** — bare wire, cols {BUS_COLS[0]} → {BUS_COLS[1]}")
    put(BTN_ROWS[0], f"**Colored button signal legs** · cols {', '.join(str(c) for c in BTN_COL0)}")
    put(BTN_ROWS[1], f"**Colored button ground legs** · cols {', '.join(str(c+BIG_LEG_COLS) for c in BTN_COL0)}")
    put(ANS_ROWS[0], f"**AA / no / yes signal legs** · cols {', '.join(map(str, ANS_COL0))}")
    put(ANS_ROWS[1], f"**AA / no / yes ground legs** · cols {', '.join(str(c+SMALL_LEG) for c in ANS_COL0)}")
    out = ["| Row | What |", "|---:|---|"]
    for r in sorted(rows):
        out.append(f"| **{r}** | " + " · ".join(rows[r]) + " |")
    out.append("")
    out.append(f"The {len(GND_ROWS)} GND buses join together down **column {GND_LINK_COL}**.")
    out.append("")
    used = set(LED_ROWS)|set(RES_ROWS)|set(BTN_ROWS)|set(ANS_ROWS)|set(GND_ROWS)
    body = set(range(RES_ROWS[0], RES_ROWS[1]+1)) | set(range(BTN_ROWS[0], BTN_ROWS[1]+1)) \
         | set(range(ANS_ROWS[0], ANS_ROWS[1]+1)) | set(range(LED_ROWS[0], LED_ROWS[1]+1))
    truly = sorted(set(range(1, ROWS+1)) - used - body)
    out.append(f"Genuinely free rows (no lead *and* no component body above them): "
               f"**{', '.join(map(str, truly)) or 'none'}**.")
    return "\n".join(out)

def wiretable():
    h = harness()
    out = [f"**{len(h)} wires**, each from a component pad to the pad of the ESP32 socket pin it "
           f"serves. All on the same board — short runs, no inter-board loom.", "",
           "| # | Signal | From — hole | To — ESP32 pin | Socket side | Position |",
           "|---:|---|---|---|---|---:|"]
    for i, (lbl, src, pin, side, pos) in enumerate(h, 1):
        out.append(f"| {i} | {lbl} | {src} | **{pin}** | {side} | {pos} |")
    out += ["", f"Plus the LCD's **{len(LCD_PINS)}** F-M jumpers, which clip straight onto the ESP32's pins "
                f"and are never soldered:", "",
            "| Signal | From | To — ESP32 pin |", "|---|---|---|"]
    for a, b in LCD_PINS:
        out.append(f"| LCD {a} | F-M jumper onto the LCD's own header | **{b}** |")
    left  = sum(1 for *_ , s, p in h if s == "LEFT")
    right = len(h) - left
    out += ["", f"That is **{left} on the left column, {right} on the right**, plus "
                f"{len(LCD_PINS)} LCD jumpers — **{len(h)+len(LCD_PINS)} landing on the socket** in total.",
            "", "> **Never wire to RX0 or TX0** (right column, positions 12–13). Those carry the USB "
                "serial link; touching them breaks uploads *and* the daemon, and looks like a dead board."]
    return "\n".join(out)

def joints():
    hdr = 2 * (HDR_COLS[1]-HDR_COLS[0]+1)
    bus = len(GND_ROWS)*8 + 6
    comp = len(LED_COLS)*2 + len(LED_COLS)*2 + len(BTN_COL0)*4 + len(ANS_COL0)*4
    a = bus + comp + len(harness())
    return "\n".join([
        "| Board | Joints | What |", "|---|---:|---|",
        f"| control surface | ~{a} | {bus} bus + {comp} component legs + {len(harness())} wire ends |",
        f"| ESP32 socket | {hdr} | two 15-socket strips; {len(harness())+len(LCD_PINS)} of those pads also take a wire |",
        f"| **total** | **~{a+hdr}** | at 1–2 min each including inspection, that is **3–5 hours** |",
    ])

def steps():
    """Every physical action, in order, with its coordinates. Moves refer to CONNECTIONS.md."""
    o = []
    o.append(f"#### Step A — the three GND buses  ·  *Move 2*")
    o.append("")
    o.append(f"Only row **{GND_ROWS[0]}** is empty enough to bus now. Rows "
             f"**{', '.join(str(r) for r in GND_ROWS[1:])}** also carry button legs — those buses go on "
             f"*after* their buttons (steps C and D).")
    o.append("")
    o.append(f"1. Lay bare 24AWG along row **{GND_ROWS[0]}**, cols {BUS_COLS[0]} → {BUS_COLS[1]}, **beside the pads, not over the holes**.")
    o.append(f"2. Tack one end, check straight, solder every 2nd–3rd pad.")
    o.append(f"3. Leave a tail at column {GND_LINK_COL} — the other two buses will join it there.")
    o.append("")
    o.append(f"✅ **Test:** every pad in row {GND_ROWS[0]} beeps to every other. No other row beeps to it.")
    o.append("")
    o.append(f"#### Step B — LEDs and resistors  ·  *Moves 1 and 3*")
    o.append("")
    o.append("Do one LED completely, test the idea, then repeat. Per LED:")
    o.append("")
    o.append("| LED | long leg (+) | short leg (−) | 220Ω top | 220Ω bottom |")
    o.append("|---|---|---|---|---|")
    for i, c in enumerate(LED_COLS):
        o.append(f"| {i+1} {LED_NAME[i]} | col {c}, row {LED_ROWS[0]} | col {c}, row {LED_ROWS[1]} | "
                 f"col {c}, row {RES_ROWS[0]} | col {c}, row {RES_ROWS[1]} |")
    o.append("")
    o.append(f"1. LED in — long leg row {LED_ROWS[0]}, short leg row {LED_ROWS[1]}. Solder the **anode only**; leave the cathode leg long.")
    o.append(f"2. Resistor in rows {RES_ROWS[0]} and {RES_ROWS[1]}, same column. Bend its leads so the body sits centred. Solder both.")
    o.append(f"3. **Move 3:** bend the LED's cathode leg flat onto the row-{RES_ROWS[0]} pad and solder it there too. Now snip both.")
    o.append(f"4. The resistor's bottom lead is in row {RES_ROWS[1]} — already the GND bus. Nothing more to do.")
    o.append("")
    o.append(f"✅ **Test:** beep col 3 row {LED_ROWS[1]} to col 3 row {RES_ROWS[0]} — must beep (the bent leg). "
             f"Beep row {LED_ROWS[0]} to the bus — must **not** beep.")
    o.append("")
    o.append(f"#### Step C — the four colored buttons  ·  *Moves 1 and 2*")
    o.append("")
    o.append("| Button | signal leg | ground leg |")
    o.append("|---|---|---|")
    for i, c0 in enumerate(BTN_COL0):
        o.append(f"| {i+1} {LED_NAME[i]} | col {c0}, row {BTN_ROWS[0]} | col {c0+BIG_LEG_COLS}, row {BTN_ROWS[1]} |")
    o.append("")
    o.append(f"1. Seat all four buttons — legs span rows {BTN_ROWS[0]}→{BTN_ROWS[1]} and 2 columns.")
    o.append(f"2. **Solder all four legs of each** (the pairs are internally joined, so it costs nothing and doubles the anchoring).")
    o.append(f"3. On the **row-{BTN_ROWS[1]} legs, leave them long**, bend flat along the row.")
    o.append(f"4. Now lay the row-{BTN_ROWS[1]} bus **on top of those bent legs** and solder through. Link it to row {GND_ROWS[0]} down column {GND_LINK_COL}.")
    o.append("")
    o.append(f"✅ **Test:** every row-{BTN_ROWS[1]} leg beeps to row {GND_ROWS[0]}. No row-{BTN_ROWS[0]} leg beeps to any bus.")
    o.append("")
    o.append(f"#### Step D — AA / no / yes  ·  *same as step C*")
    o.append("")
    o.append("| Button | signal leg | ground leg |")
    o.append("|---|---|---|")
    for (n, g, d), c0 in zip(ANS_INFO, ANS_COL0):
        o.append(f"| {n} ({d}) | col {c0}, row {ANS_ROWS[0]} | col {c0+SMALL_LEG}, row {ANS_ROWS[1]} |")
    o.append("")
    o.append(f"Same sequence: seat, solder all legs, leave the row-{ANS_ROWS[1]} legs long and bent, then bus over them and link to column {GND_LINK_COL}.")
    o.append("")
    o.append(f"✅ **Test:** all three ground legs beep to row {GND_ROWS[0]}. No signal leg beeps to a bus.")
    o.append("")
    o.append(f"#### Step E — the {len(harness())} wires to the ESP32 socket  ·  *Moves 4 and 5*")
    o.append("")
    o.append("Strip 4mm, tin both ends, label both ends, then solder. Full destinations in the wire table above. All runs stay on this board.")
    o.append("")
    o.append(f"✅ **Test:** beep each wire end-to-end, then beep it against the nearest GND bus — must not beep.")
    return "\n".join(o)

SECTIONS = {"rowplan": rowplan, "wiretable": wiretable, "joints": joints, "steps": steps}

doc = open(DOC).read()
changed = []
for name, fn in SECTIONS.items():
    pat = re.compile(rf"<!-- GEN:{name} -->.*?<!-- /GEN:{name} -->", re.S)
    if not pat.search(doc):
        print(f"  ! no <!-- GEN:{name} --> markers in BUILD.md — skipped")
        continue
    doc = pat.sub(f"<!-- GEN:{name} -->\n" + fn().replace("\\", "\\\\") + f"\n<!-- /GEN:{name} -->", doc)
    changed.append(name)
open(DOC, "w").write(doc)
print("regenerated:", ", ".join(changed) if changed else "nothing")
