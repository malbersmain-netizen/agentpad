#!/usr/bin/env python3
"""Regenerate BUILD.md's volatile tables and step list from tools/layout.py.

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

H = harness()
WIRE_NO = {lbl: i for i, (lbl, *_) in enumerate(H, 1)}

def wires_for(prefix):
    return [(WIRE_NO[l], l, s, p, c, r) for l, s, p, _, _, c, r in H if l.startswith(prefix)]


def rowplan():
    rows = {}
    def put(r, s): rows.setdefault(r, []).append(s)
    put(LED_ROWS[0], f"**LED anodes (+)** — each also takes that LED's wire to the socket · cols {', '.join(map(str, LED_COLS))}")
    put(LED_ROWS[1], f"**LED cathodes (−)** — lead bends over on the copper face to the row-{RES_ROWS[0]} pad")
    put(RES_ROWS[0], f"220Ω top lead (the only lead *in* this hole; the cathode lands on its pad)")
    put(RES_ROWS[1], f"220Ω bottom lead — lands straight on the bus")
    for r in GND_ROWS: put(r, f"**GND bus** — bare wire, cols {BUS_COLS[0]} → {BUS_COLS[1]}")
    put(BTN_ROWS[0], f"**Colored button legs — signal node** · cols {', '.join(f'{c}+{c+BIG_LEG_COLS}' for c in BTN_COL0)}")
    put(BTN_ROWS[1], f"**Colored button legs — ground node** · cols {', '.join(f'{c}+{c+BIG_LEG_COLS}' for c in BTN_COL0)}")
    put(ANS_ROWS[0], f"**AA / no / yes legs — signal node** · cols {', '.join(f'{c}+{c+SMALL_LEG}' for c in ANS_COL0)}")
    put(ANS_ROWS[1], f"**AA / no / yes legs — ground node** · cols {', '.join(f'{c}+{c+SMALL_LEG}' for c in ANS_COL0)}")
    put(LCD_PORT_ROW, f"**LCD port** — 4 male pins · cols {LCD_PORT_COL0}–{LCD_PORT_COL0+len(LCD_PINS)-1}")
    out = ["| Row | What |", "|---:|---|"]
    for r in sorted(rows):
        out.append(f"| **{r}** | " + " · ".join(rows[r]) + " |")
    out.append("")
    out.append(f"The {len(GND_ROWS)} GND buses join together down **column {GND_LINK_COL}** — the far "
               f"left. Every signal wire leaves its part at column {min(int(s.split()[1].rstrip(',')) for _,s,p,*_ in H if p!='GND')} "
               f"or higher and runs *right*, so nothing ever crosses that bare link.")
    out.append("")
    used = set(LED_ROWS)|set(RES_ROWS)|set(BTN_ROWS)|set(ANS_ROWS)|set(GND_ROWS)
    body = set(range(RES_ROWS[0], RES_ROWS[1]+1)) | set(range(BTN_ROWS[0], BTN_ROWS[1]+1)) \
         | set(range(ANS_ROWS[0], ANS_ROWS[1]+1)) | set(range(LED_ROWS[0], LED_ROWS[1]+1))
    truly = sorted(set(range(1, ROWS+1)) - used - body)
    out.append(f"Genuinely free rows on the control surface, cols {BUS_COLS[0]}–{BUS_COLS[1]} "
               f"(no lead *and* no component body above them): **{', '.join(map(str, truly)) or 'none'}**.")
    return "\n".join(out)


def wiretable():
    out = [f"**{len(H)} soldered wires**, each from a component pad to the pad of the ESP32 socket "
           f"pin it serves. All on the same board — short runs, no inter-board loom.", "",
           "| # | Signal | From — component hole | To — socket hole | ESP32 pin | Fitted in |",
           "|---:|---|---|---|---|---|"]
    when = {"LED": "step 3", "button": "step 4", "AA": "step 5", "no": "step 5",
            "yes": "step 5", "ground": "step 2"}
    for i, (lbl, src, pin, side, pos, col, row) in enumerate(H, 1):
        st = next(v for k, v in when.items() if lbl.startswith(k))
        out.append(f"| {i} | {lbl} | {src} | **col {col}, row {row}** | {pin} ({side} {pos}) | {st} |")
    out += ["", f"Plus the **LCD port** — 4 male header pins soldered into the board in step 6, each "
                f"wired to a socket pad. The LCD itself reaches them with 4 F-F jumpers and is "
                f"**never soldered**:", "",
            "| LCD pin | Board hole (male pin) | Wires to socket hole | ESP32 pin |", "|---|---|---|---|"]
    for name, hole, esp, sock in lcd_port():
        out.append(f"| {name} | col {hole[0]}, row {hole[1]} | col {sock[0]}, row {sock[1]} | **{esp}** |")
    left  = sum(1 for r in H if r[3] == "LEFT")
    right = len(H) - left
    lp_left = sum(1 for _, _, _, s in lcd_port() if s[0] == HDR_COLS[0])
    out += ["", f"That is **{left+lp_left} wires onto the left socket column and "
                f"{right+len(lcd_port())-lp_left} onto the right** — "
                f"{len(H)+len(lcd_port())} of the socket's 30 pads take a wire.",
            "", "> **Never wire to RX0 or TX0** (right column, positions 12–13). Those carry the USB "
                "serial link; touching them breaks uploads *and* the daemon, and looks like a dead board.",
            "", f"> **The LCD port carries 5V** (VIN). It is the only 5V on the board and it lives at "
                f"columns {LCD_PORT_COL0}–{LCD_PORT_COL0+3}, well away from the control surface. "
                f"Keep it that way."]
    return "\n".join(out)


def mounts():
    m = mount_holes()
    out = [f"Four **{MOUNT_DRILL}mm** holes (M2 clearance), drilled **on existing pads** in free "
           f"positions — computed and clearance-checked by `verify-layout.py`:", "",
           "| # | Hole | From left edge | From top edge |", "|---:|---|---|---|"]
    for i, (c, r) in enumerate(m, 1):
        x, y = xy(c, r)
        out.append(f"| {i} | **col {c}, row {r}** | {x:.1f} mm | {y:.1f} mm |")
    out += ["", f"> **Why not the corners?** The hole grid spans {(COLS-1)*P:.1f} × {(ROWS-1)*P:.1f} mm "
                f"on a {BOARD_W:.0f} × {BOARD_H:.0f} mm board, leaving only **{BX:.1f} mm** at the "
                f"sides and **{BY:.1f} mm** top and bottom. Nothing bigger than about 2mm fits in "
                f"that margin, so the screws go on pads instead. A {MOUNT_DRILL}mm bit cuts "
                f"{MOUNT_DRILL/2:.2f}mm of radius — less than the {P/2:.2f}mm half-pitch — so it "
                f"cannot reach past the midpoint toward the next pad, {P:.2f}mm away. Only the pad "
                f"you drill is lost, and all four of these are unused."]
    return "\n".join(out)


def joints():
    bus_len   = BUS_COLS[1] - BUS_COLS[0] + 1
    bus       = len(GND_ROWS) * (bus_len // 2) + 4          # every 2nd pad, + the link
    legs      = len(LED_COLS)*2 + len(LED_COLS)*2 + len(BTN_COL0)*4 + len(ANS_COL0)*4
    sockets   = 2 * (HDR_ROWS[1] - HDR_ROWS[0] + 1)         # 15 pins per strip, both strips
    sig_wires = len(H) * 2
    port      = len(LCD_PINS) + len(LCD_PINS)*2             # 4 male pins + 4 wires, 2 ends each
    total     = bus + legs + sockets + sig_wires + port
    return "\n".join([
        "| Group | Joints | What |", "|---|---:|---|",
        f"| GND buses + link | {bus} | 3 bare wires soldered every 2nd pad, plus the column-{GND_LINK_COL} link |",
        f"| Component legs | {legs} | 4 LEDs + 4 resistors (2 each), 7 switches (**4 legs each**) |",
        f"| ESP32 socket | {sockets} | two 15-way strips |",
        f"| Signal wires | {sig_wires} | {len(H)} wires, both ends |",
        f"| LCD port | {port} | {len(LCD_PINS)} male pins + {len(LCD_PINS)} wires |",
        f"| **total** | **~{total}** | at 1–2 min each including inspection, that is **4–6 hours** |",
    ])


def preflight():
    b, s = BTN_ROWS, ANS_ROWS
    return "\n".join([
        "Twenty minutes here. Every one of these has bitten someone building this exact board.",
        "",
        "#### P1 — find each switch's internally-joined leg pair  ·  **do not skip**",
        "",
        f"A 4-leg tactile switch is two pairs of two. The legs within a pair are joined "
        f"permanently; pressing connects one pair to the other. This layout puts **one whole "
        f"pair on the signal row and the other whole pair on the ground row** — so the joined "
        f"pair must run *across a row*, along the columns. Get that backwards and every signal "
        f"leg is welded to the ground bus.",
        "",
        "1. Multimeter to continuity. Take one **spare** colored switch and one spare small switch.",
        "2. Beep all six leg pairings without pressing. Exactly two pairings beep — those are "
        "your pairs.",
        "3. **Mark the joined pair with a marker across the top of the body.** That line must end "
        "up running left-to-right (along a row) when the switch is seated.",
        "4. Press and hold: now all four legs beep together. Release: back to two pairs.",
        "",
        f"✅ **Pass:** you know which way each switch has to face, and every switch of that type "
        f"goes in the same way. The colored switches are {BIG_LEG_COLS*P:.1f}mm across × "
        f"{BIG_LEG_ROWS*P:.1f}mm long so they only physically fit one way — check that the joined "
        f"pair is the {BIG_LEG_COLS*P:.1f}mm one. The small ones are square "
        f"({SMALL_LEG*P:.1f}mm both ways) so they fit either way and **you must use the mark**.",
        "",
        f"❌ **If a colored switch's joined pair runs the long way** ({BIG_LEG_ROWS*P:.1f}mm, rows "
        f"{BTN_ROWS[0]}↔{BTN_ROWS[1]}), stop. It cannot be rotated — it would not fit. Change "
        f"`BTN_ROWS` in `tools/layout.py` so signal and ground are on different *columns* instead, "
        f"re-run `verify-layout.py` and `gen-tables.py`, and rebuild the figures.",
        "",
        "#### P2 — confirm the resistors are 220Ω",
        "",
        "Bands **red · red · brown · gold**. Meter across one: 209–231Ω.",
        "Brown-black-brown is 100Ω and will look fine but run the LEDs bright; "
        "red-red-red is 2.2kΩ and they will look dim.",
        "",
        "#### P3 — LED polarity and brightness",
        "",
        f"Long leg is the anode (+) and goes in row {LED_ROWS[0]}. Also look *into* the LED: the "
        f"small flag inside is the cathode. Test each LED with a 220Ω resistor on a breadboard "
        f"before it is soldered in — a dead LED found now costs nothing.",
        "",
        "#### P4 — drill the mounting holes",
        "",
        "Drill **before any solder goes on**. Drilling a populated board cracks joints and rains "
        "conductive swarf across the copper. Positions are in §3.",
        "",
        "1. Mark all four holes from the top, counting columns and rows twice.",
        "2. Back the board with scrap wood, clamp it, drill slowly at the marked pads.",
        "3. Deburr both faces with a craft knife twisted by hand.",
        "4. Vacuum, then wipe with isopropyl. Swarf between pads is a short.",
        "",
        "✅ **Test:** a screw passes without force, and no neighbouring pad has lifted.",
        "",
        "#### P5 — cut the socket strips",
        "",
        f"Count **{HDR_ROWS[1]-HDR_ROWS[0]+1} sockets**, cut through the {HDR_ROWS[1]-HDR_ROWS[0]+2}th. "
        f"You need two. Cutting a stacking header sacrifices the socket you cut through — that is "
        f"normal and the 40-pin strip has enough.",
        "",
        "✅ **Test:** both strips push fully onto the ESP32's pin rows with no gap.",
    ])


def steps():
    o = []
    def head(t):      o.extend([f"#### {t}", ""])
    def test(t, fail=None):
        o.extend(["", f"✅ **Test:** {t}"])
        if fail: o.extend(["", f"❌ **If it fails:** {fail}"])
        o.append("")

    # ---------------------------------------------------------------- 1
    head("Step 1 — the ESP32 socket  ·  *Move 1*")
    o.append(f"Two {HDR_ROWS[1]-HDR_ROWS[0]+1}-way strips at **columns {HDR_COLS[0]} and "
             f"{HDR_COLS[1]}, rows {HDR_ROWS[0]} → {HDR_ROWS[1]}**. This goes first because it "
             f"proves the ESP32 and the cable still work before anything else can be blamed.")
    o.append("")
    o.extend([
        "1. Push **both strips onto the ESP32's pins** first. The module now holds them at exactly "
        "the right spacing and squareness — soldering them separately is how people end up "
        "desoldering a 15-pin strip.",
        "2. Lower the whole assembly onto the board from the top, pins through the holes.",
        f"3. Check the strips landed in columns {HDR_COLS[0]} and {HDR_COLS[1]} — {HDR_COLS[1]-HDR_COLS[0]} "
        f"apart — and that the module's USB end points at the **bottom** edge.",
        "4. Solder **one pin on each strip**. Turn it over, check it sits flat and square. Only then "
        "do the other 28.",
        "5. Trim the pins flush and pull the ESP32 out.",
    ])
    test(f"beep from each socket pad on the underside to the matching ESP32 pin (module seated), "
         f"then beep each pad to its neighbour — no neighbour may beep. Then plug in USB: "
         f"`ls /dev/cu.*` shows a new port, and `firmware/blink` uploads and blinks.",
         "A blink that works proves nothing about the socket — the ESP32's own USB carries power "
         "and serial, so every socket joint could be cold. Trust the beep test, not the blink.")

    # ---------------------------------------------------------------- 2
    head(f"Step 2 — the first GND bus and the ground wire  ·  *Moves 2 and 4*")
    o.append(f"Row **{GND_ROWS[0]}** is the only bus row with nothing else in it, so it can go on "
             f"now. Rows {', '.join(str(r) for r in GND_ROWS[1:])} carry button legs and must wait "
             f"until those buttons are seated (steps 4 and 5).")
    o.append("")
    o.extend([
        f"1. Cut bare 24AWG a little longer than {BUS_COLS[1]-BUS_COLS[0]+1} holes.",
        f"2. Lay it on the copper face along row **{GND_ROWS[0]}**, columns {BUS_COLS[0]} → "
        f"{BUS_COLS[1]}, **beside the pad centres, never across them**. A wire lying over a hole "
        f"blocks the lead you push in later, and the joint still looks perfect from underneath.",
        "3. Tack one end. Check it is straight and clear of every hole. Then solder every 2nd–3rd pad.",
        f"4. Leave ~10mm of tail at column {GND_LINK_COL} — the other two buses join it there.",
        f"5. Run wire **{WIRE_NO['ground']}**: from **col {GND_WIRE_FROM[0]}, row {GND_WIRE_FROM[1]}** "
        f"to the socket's **GND** pad at **col {socket_hole(*esp_position('GND'))[0]}, row "
        f"{socket_hole(*esp_position('GND'))[1]}**. This is the board's only ground wire.",
    ])
    test(f"every pad in row {GND_ROWS[0]} beeps to every other, and to the socket's GND pad. "
         f"No other row beeps to it. Push a spare lead down through a row-{GND_ROWS[0]} hole from "
         f"the top — it must reach the copper, not stop on the bus wire.")

    # ---------------------------------------------------------------- 3
    head("Step 3 — LEDs, resistors and their four wires  ·  *Moves 1, 3 and 4*")
    o.append("Do **LED 1 completely, including its wire and the test**, before starting LED 2. "
             "The first one teaches you the bent-leg move; the other three are then quick.")
    o.append("")
    o.append("| LED | long leg (+) | short leg (−) | 220Ω top | 220Ω bottom | wire # → socket |")
    o.append("|---|---|---|---|---|---|")
    for i, c in enumerate(LED_COLS):
        n, l, s, p, col, row = wires_for(f"LED {i+1}")[0]
        o.append(f"| {i+1} {LED_NAME[i]} | col {c}, row {LED_ROWS[0]} | col {c}, row {LED_ROWS[1]} | "
                 f"col {c}, row {RES_ROWS[0]} | col {c}, row {RES_ROWS[1]} | "
                 f"**{n}** → col {col}, row {row} ({p}) |")
    o.append("")
    o.extend([
        f"1. **Resistor first** — it is the lower part. Legs into rows {RES_ROWS[0]} and "
        f"{RES_ROWS[1]} of the same column; bend them so the {RES_BODY}mm body sits centred in the "
        f"{(RES_ROWS[1]-RES_ROWS[0])*P:.1f}mm span. Solder both, trim.",
        f"2. **LED next** — long leg into row {LED_ROWS[0]}, short leg into row {LED_ROWS[1]}. "
        f"Solder the **anode only**. Leave the cathode leg full length.",
        f"3. **Move 3 — the bent leg.** On the copper face, bend the cathode's leftover length flat "
        f"until it lies on the **row-{RES_ROWS[0]} pad**, where the resistor's top lead already is. "
        f"Solder it into that same joint. *Now* trim both.",
        f"4. The resistor's bottom lead is already in row {RES_ROWS[1]} — the bus. It is grounded; "
        f"there is nothing else to do.",
        f"5. Run that LED's wire from **its own column, row {LED_ROWS[0]}** to its socket pad. **Both ends "
        f"are lap joints** (*Move 5*) — the anode hole holds the LED's own leg and the socket hole "
        f"holds a header pin, so you are soldering onto existing blobs, not into free holes.",
    ])
    test(f"beep col {LED_COLS[0]}, row {LED_ROWS[1]} to col {LED_COLS[0]}, row {RES_ROWS[0]} — "
         f"**must beep** (that is the bent leg doing its job). Beep row {LED_ROWS[0]} to the bus — "
         f"must **not**. With all four done, seat the ESP32 and run `firmware/ledtest`: all four "
         f"cycle in order red, green, blue, yellow.",
         "One LED dark and backwards → its legs are swapped; desolder the anode, rotate, redo. All "
         "four dark → the ground wire or the row-8 bus. Wrong LED lighting → two wires swapped at "
         "the socket end, which is why you label both ends.")

    # ---------------------------------------------------------------- 4
    head("Step 4 — the four colored buttons, the second bus, the link  ·  *Moves 1, 2 and 4*")
    o.append("| Button | legs — signal node (row " + str(BTN_ROWS[0]) + ") | legs — ground node (row "
             + str(BTN_ROWS[1]) + ") | wire # → socket |")
    o.append("|---|---|---|---|")
    for i, c0 in enumerate(BTN_COL0):
        n, l, s, p, col, row = wires_for(f"button {i+1}")[0]
        o.append(f"| {i+1} {LED_NAME[i]} | cols {c0} **and** {c0+BIG_LEG_COLS} | "
                 f"cols {c0} **and** {c0+BIG_LEG_COLS} | **{n}** from col {c0} → col {col}, row {row} ({p}) |")
    o.append("")
    o.append(f"> All four legs get soldered. The two legs in row {BTN_ROWS[0]} are one internal "
             f"node (the signal), the two in row {BTN_ROWS[1]} are the other (ground) — that is "
             f"what P1 confirmed. Soldering all four costs nothing and doubles the anchoring on a "
             f"part you will press thousands of times.")
    o.append("")
    o.extend([
        f"1. Seat all four switches. Legs span rows {BTN_ROWS[0]}→{BTN_ROWS[1]} and columns "
        f"c → c+{BIG_LEG_COLS}. Check each cap is square before soldering — tack one leg, sight "
        f"along the row, then finish.",
        f"2. Solder the two **row-{BTN_ROWS[0]}** legs of each and trim them.",
        f"3. Solder the two **row-{BTN_ROWS[1]}** legs but **leave them long**; bend them flat "
        f"along row {BTN_ROWS[1]}.",
        f"4. Lay the row-{BTN_ROWS[1]} bus **on top of those bent legs**, cols {BUS_COLS[0]} → "
        f"{BUS_COLS[1]}, and solder through both at once. (Bus-first does not work on this row — "
        f"the wire would block the holes.)",
        f"5. **Link the buses:** bare wire down column {GND_LINK_COL} from row {GND_ROWS[0]} to row "
        f"{GND_ROWS[1]}. Column {GND_LINK_COL} is chosen because no signal wire ever runs left of "
        f"column {min(int(s.split()[1].rstrip(',')) for _,s,p,*_ in H if p!='GND')}, so nothing crosses this bare wire.",
        "6. Run the four button wires from the row-" + str(BTN_ROWS[0]) + " leg listed above.",
    ])
    test(f"every row-{BTN_ROWS[1]} leg beeps to row {GND_ROWS[0]} and to the socket GND. **No** "
         f"row-{BTN_ROWS[0]} leg beeps to any bus while the button is released — and every one does "
         f"while it is pressed. Then `firmware/btntest` prints `button 0`…`button 3`.",
         "Several buttons dead at once is the bus or the link, not the switches — that failed twice "
         "on the breadboard. One button permanently pressed means its signal and ground legs are on "
         "the same internal node: recheck P1.")

    # ---------------------------------------------------------------- 5
    head("Step 5 — AA / no / yes, the third bus  ·  *same moves*")
    o.append("| Button | signal legs (row " + str(ANS_ROWS[0]) + ") | ground legs (row "
             + str(ANS_ROWS[1]) + ") | wire # → socket |")
    o.append("|---|---|---|---|")
    for (n_, g, d), c0 in zip(ANS_INFO, ANS_COL0):
        n, l, s, p, col, row = wires_for(n_)[0]
        o.append(f"| {n_} ({d}) | cols {c0} **and** {c0+SMALL_LEG} | cols {c0} **and** {c0+SMALL_LEG} | "
                 f"**{n}** from col {c0} → col {col}, row {row} ({p}) |")
    o.append("")
    o.append(f"Identical sequence to step 4: seat, solder the row-{ANS_ROWS[0]} legs, leave the "
             f"row-{ANS_ROWS[1]} legs long and bent, bus over them, then extend the column-"
             f"{GND_LINK_COL} link down from row {GND_ROWS[1]} to row {GND_ROWS[2]}. Then the three wires.")
    test(f"all three ground legs beep to row {GND_ROWS[0]}. No signal leg beeps to a bus when "
         f"released. `firmware/btntest` now prints `button 0` … `button 6` — **all seven**.",
         f"btntest reading only some buttons has been a real failure here: an old copy of that "
         f"sketch scanned 4 pins instead of 7 and made three good switches look dead. Check the "
         f"sketch declares all 7 GPIOs before you unsolder anything.")

    # ---------------------------------------------------------------- 6
    head("Step 6 — the LCD port  ·  *Moves 1 and 4*")
    o.append(f"The LCD is never soldered, so it needs somewhere to plug into. Once the ESP32 is "
             f"seated its pins are **inside the socket** and nothing can clip onto them — so the "
             f"board carries its own 4-pin male header at **cols {LCD_PORT_COL0}–"
             f"{LCD_PORT_COL0+len(LCD_PINS)-1}, row {LCD_PORT_ROW}**, wired to the socket pads.")
    o.append("")
    o.append("| LCD pin | Male pin at | Wire to socket hole | ESP32 pin |")
    o.append("|---|---|---|---|")
    for name, hole, esp, sock in lcd_port():
        o.append(f"| {name} | col {hole[0]}, row {hole[1]} | col {sock[0]}, row {sock[1]} | **{esp}** |")
    o.append("")
    o.extend([
        f"1. Cut a **4-pin male** strip. Seat it at cols {LCD_PORT_COL0}–"
        f"{LCD_PORT_COL0+len(LCD_PINS)-1}, row {LCD_PORT_ROW}, short side down through the board.",
        "2. Tack one pin, check it stands square, solder the rest.",
        "3. Run the four wires to the socket pads in the table. **Mark the VCC wire** — it is the "
        "only 5V on the board.",
        "4. Connect the LCD with **4 F-F jumpers**, female onto the LCD's own male header, female "
        "onto this port. Match the labels, not the colours.",
    ])
    test("beep each port pin to its socket pad, and beep **VCC to GND** — that one must **not**. "
         "Then `firmware/lcdtest`: serial prints `found device at 0x27` and text appears.",
         "Backlit but blank is the contrast pot on the back. Completely dead: try address `0x3F`, "
         "and check SDA/SCL are not swapped — the two middle wires are the easy pair to cross.")

    # ---------------------------------------------------------------- 7
    head("Step 7 — real firmware, then mount it")
    o.append("```bash")
    o.append("arduino-cli compile -u -p /dev/cu.usbserial-0001 --fqbn esp32:esp32:esp32 firmware/agentpad")
    o.append("```")
    o.append("")
    o.append("From a serial monitor at 115200, line ending **Newline**:")
    o.append("")
    o.append("| Send | Expect |")
    o.append("|---|---|")
    for i, nm in enumerate(LED_NAME):
        o.append(f"| `L {i} {'working' if i % 2 == 0 else 'blocked'}` | {nm} LED "
                 f"{'solid' if i % 2 == 0 else 'blinks fast'} |")
    o.append("| `D0 hello` | top LCD row changes |")
    o.append(f"| press each button | `B 0` … `B {len(LED_NAME)+len(ANS_INFO)-1}` |")
    o.append("")
    o.append("Only once all of that passes, screw the board and the LCD to the wood — then "
             "**run the whole test again**. Assembly is when wires get pinched and joints get stressed.")
    test("every line above, before and after mounting.")
    return "\n".join(o).rstrip()


SECTIONS = {"rowplan": rowplan, "wiretable": wiretable, "mounts": mounts,
            "joints": joints, "preflight": preflight, "steps": steps}

doc = open(DOC).read()
changed, missing = [], []
for name, fn in SECTIONS.items():
    pat = re.compile(rf"<!-- GEN:{name} -->.*?<!-- /GEN:{name} -->", re.S)
    if not pat.search(doc):
        missing.append(name); continue
    doc = pat.sub(lambda _m, f=fn, n=name: f"<!-- GEN:{n} -->\n" + f() + f"\n<!-- /GEN:{n} -->", doc)
    changed.append(name)
open(DOC, "w").write(doc)
print("regenerated:", ", ".join(changed) if changed else "nothing")
if missing:
    print("  ! no markers in BUILD.md for:", ", ".join(missing))
