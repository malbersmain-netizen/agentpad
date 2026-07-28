# Agent Pad — complete build manual

Takes you from loose parts to a working, mounted device. Read section 4 before you touch
the iron; everything else follows in order.

**Scope:** 1 LCD + 4 LEDs + 7 buttons on **one 30 × 42 double-sided PCB**, screwed to a wooden
backing. ~149 solder joints, 4–6 hours.

**Done means:** press a color button → a tinted `claude` window opens and focuses; its LED
heartbeats; ask it something needing permission → LED blinks fast → press `yes` → the
command runs. One USB cable to the Mac.

---

## Two rules

**1. You have ONE ESP32 — it must stay removable.** That's why it goes in a socket rather
than being soldered down.

**Be clear-eyed about the fallback.** Once the board is soldered you will have **zero
colored buttons and zero LCDs left** (the kit has exactly 4 and 1; LEDs, resistors and
small buttons do have spares). `BREADBOARD.md` is only a true fallback if you buy 4 spare
12mm tactile switches. The LCD is already safe: it is **never soldered** — 4 F-F jumpers,
female onto its own header and female onto the board's 4-pin LCD port, so it unplugs and moves.

**2. Solder nothing you haven't already proven on the breadboard.** Everything here is
validated. Don't add features and solder them the same day.

---

## 1. Parts and tools

### From the Freenove kit
ESP32 · I²C LCD1602 · 4 LEDs (R/G/B/Y) · 4× 220Ω · 4 capped push buttons · 3 plain push
buttons · **40-pin stacking header** (cut into two 15-socket strips) · a **4-pin male
header** for the LCD port · **3× PY-5CM\*7CM perfboards** — *not* the build surface any
more, but sacrifice one for the soldering practice in `SOLDERING.md`.

### Bought separately
**One 30 × 42 hole double-sided PCB, 120 × 80mm** — silkscreen reads `12*8CM 2.54MM`.
This is what everything is built on. It arrives with **four factory corner mounting holes**,
so no drilling is needed.

### Buy — tools
| Item | Notes |
|---|---|
| Temperature-controlled soldering iron | ~340°C for leaded solder |
| Solder, 60/40 **leaded**, 0.6–0.8mm | Far more forgiving than lead-free for a first build |
| Flux pen | The difference between clean joints and blobs |
| **Multimeter with continuity beep** | **Non-negotiable.** Nearly every failure is a cold joint or invisible bridge. Never used one? [`MULTIMETER.md`](MULTIMETER.md) |
| Wire strippers · flush cutters | |
| Helping hands / small vise | You need both hands for iron and solder |
| Desoldering braid | For when — not if — you bridge two pads |

### Buy — materials
| Item | Notes |
|---|---|
| 22AWG solid-core hookup wire | The 12 signal wires and the 4 LCD-port wires |
| Bare or tinned 24AWG | The three GND buses and the link — thinner is far easier to heat |
| Heat-shrink, assorted | |
| Wood backing plate | ~150 × 200mm, any offcut |
| **M3 × 12mm screws** + nylon washers + 6mm standoffs | Mounting the board through its factory corner holes — measure one first |
| M3 × 16mm screws + 12–15mm standoffs | Mounting the LCD by its own 4 holes |
| 4 × F-F jumper wires | LCD to the board's LCD port — never soldered |

### Nice to have
Isopropyl + brush (clean flux so you can see joints) · Kapton tape (holds parts while you
tack the first pin) · a second ESP32 if you ever see one in stock.

---

## 2. The case — deferred

**The demo does not depend on a case.** The deliverable is the soldered board plus the LCD,
screwed to a wooden plate. That is a solid object you can hand to someone, and it needs no
printer. If a case ever happens, generate it *from* `tools/layout.py` — the part positions
there are already measured — rather than building the board to fit a case.

---

## 3. The board

One **30 × 42 hole double-sided board, 120 × 80mm**, oriented **42 columns across, 30 rows
down**. Grid reference: col 1, row 1 = top-left. The silkscreen letters along the bottom
edge run A–Z then A–P — that is your 42 columns — and there are four factory-drilled
mounting holes at the corners.

Everything lives on it — the control surface in **columns 1–28**, the ESP32's socket in
**columns 30–40**. There is no second board and no inter-board loom.

**Measured footprints** (calipers, on the real parts):

| Part | Pins across | Pins long |
|---|---|---|
| Colored button | **3 holes** (1 between) | **6 holes** (4 between) |
| Small button | **3 holes** | **3 holes** |
| ESP32 | **11 holes** (pin rows 1.0″ apart) | **15 holes** |

### Why this board changed the design

The previous plan used two of the kit's small single-sided boards, because a single-sided
board cannot socket the ESP32 underneath and there was no room for it on top. At 30 × 42
the question disappears: the ESP32 simply sits **beside** the controls in its own socket,
mounted the ordinary way — body on top, pins down, soldered underneath.

That drops the second board, the 12-wire inter-board loom and ~30 joints, **and** roughly
doubles every clearance:

| | old 18×24 | this board |
|---|---|---|
| Between button bodies | 3.24mm | **5.78mm** |
| Resistor → button | 5.43mm | **9.90mm** |
| Button → answer row | 4.97mm | **7.51mm** |
| Spare rows | 10 | **22** |

Because every joint stays on one face, the design does **not** depend on whether your
holes are plated through. If they are, that's a bonus (sturdier pads); if not, nothing
changes.

> **The LCD is still never soldered** — but it cannot clip onto the ESP32's pins either,
> because those are *inside the socket* the moment the module is seated. So the board
> carries a **4-pin male LCD port** of its own (cols 30–33, row 2), wired to the socket
> pads, and the LCD reaches it with 4 F-F jumpers. The LCD stays a reusable part, and the
> only 5V on the board is that one port — nowhere near the control surface.

<!-- GEN:rowplan -->
| Row | What |
|---:|---|
| **2** | **LED anodes (+)** — each also takes that LED's wire to the socket · cols 4, 11, 18, 25 · **LCD port** — 4 male pins · cols 30–33 |
| **3** | **LED cathodes (−)** — lead bends over on the copper face to the row-4 pad |
| **4** | 220Ω top lead (the only lead *in* this hole; the cathode lands on its pad) |
| **8** | 220Ω bottom lead — lands straight on the bus · **GND bus** — bare wire, cols 1 → 28 |
| **11** | **Colored button legs — signal node** · cols 3+5, 10+12, 17+19, 24+26 |
| **16** | **GND bus** — bare wire, cols 1 → 28 · **Colored button legs — ground node** · cols 3+5, 10+12, 17+19, 24+26 |
| **19** | **AA / no / yes legs — signal node** · cols 4+6, 13+15, 22+24 |
| **21** | **GND bus** — bare wire, cols 1 → 28 · **AA / no / yes legs — ground node** · cols 4+6, 13+15, 22+24 |

The 3 GND buses join together down **column 1** — the far left. Every signal wire leaves its part at column 3 or higher and runs *right*, so nothing ever crosses that bare link.

Genuinely free rows on the control surface, cols 1–28 (no lead *and* no component body above them): **1, 9, 10, 17, 18, 22, 23, 24, 25, 26, 27, 28, 29, 30**.
<!-- /GEN:rowplan -->

Verified clearances and spare rows come straight from `tools/verify-layout.py`; re-run it
after any change.

### The ESP32 socket

Cut two **15-socket** lengths from the kit's 40-pin stacking header (count 15, cut through
the 16th). They go at **columns 30 and 40, rows 8 → 22**.

1. Plug **both strips onto the ESP32's pins** — the ESP32 now holds them at exactly the
   right spacing and squareness
2. Lower that assembly onto the board **from the top**, pins through the holes
3. Confirm the strips land in columns 30 and 40 (10 apart — your ESP32 measures 11 holes
   across)
4. Solder **one pin per strip** on the underside, check it sits flat, then do the rest
5. Trim the pins flush and pull the ESP32 out

Soldering the strips separately and *then* trying to seat the ESP32 is how people end up
desoldering a 15-pin strip. Let the ESP32 hold them.

**Where the USB ends up.** The module's 55mm body overhangs its 15-pin rows by about 4
rows at each end, so with the socket at rows 8–22 the USB connector stops **13mm short of
the bottom edge** — it does *not* overhang. That is fine: the module rides ~8mm up on the
socket pins, so the plug and cable pass clear over the board. What it does mean is that
**rows 26–30 at columns 30–40 must stay empty** — that strip is the cable's exit path.
`verify-layout.py` checks it.

### The wires

<!-- GEN:wiretable -->
**12 soldered wires**, each from a component pad to the pad of the ESP32 socket pin it serves. All on the same board — short runs, no inter-board loom.

| # | Signal | From — component hole | To — socket hole | ESP32 pin | Fitted in |
|---:|---|---|---|---|---|
| 1 | LED 1 red | col 4, row 2 | **col 40, row 20** | D13 (VIN 3) | step 3 |
| 2 | LED 2 green | col 11, row 2 | **col 40, row 18** | D14 (VIN 5) | step 3 |
| 3 | LED 3 blue | col 18, row 2 | **col 40, row 17** | D27 (VIN 6) | step 3 |
| 4 | LED 4 yellow | col 25, row 2 | **col 40, row 16** | D26 (VIN 7) | step 3 |
| 5 | button 1 red | col 3, row 11 | **col 40, row 13** | D32 (VIN 10) | step 4 |
| 6 | button 2 green | col 10, row 11 | **col 40, row 14** | D33 (VIN 9) | step 4 |
| 7 | button 3 blue | col 17, row 11 | **col 40, row 15** | D25 (VIN 8) | step 4 |
| 8 | button 4 yellow | col 24, row 11 | **col 30, row 18** | D4 (3V3 5) | step 4 |
| 9 | AA (always allow) | col 4, row 19 | **col 30, row 8** | D23 (3V3 15) | step 5 |
| 10 | no (deny) | col 13, row 19 | **col 30, row 14** | D18 (3V3 9) | step 5 |
| 11 | yes (approve) | col 22, row 19 | **col 30, row 13** | D19 (3V3 10) | step 5 |
| 12 | ground | col 28, row 8 | **col 30, row 21** | GND (3V3 2) | step 2 |

Plus the **LCD port** — 4 male header pins soldered into the board in step 6, each wired to a socket pad. The LCD itself reaches them with 4 F-F jumpers and is **never soldered**:

| LCD pin | Board hole (male pin) | Wires to socket hole | ESP32 pin |
|---|---|---|---|
| GND | col 30, row 2 | col 40, row 21 | **GND** |
| VCC | col 31, row 2 | col 40, row 22 | **VIN** |
| SDA | col 32, row 2 | col 30, row 12 | **D21** |
| SCL | col 33, row 2 | col 30, row 9 | **D22** |

That is **7 wires onto the 3V3 column (col 30, the near one) and 9 onto the VIN column (col 40)** — 16 of the socket's 30 pads take a wire.

> **Never wire to RX0 or TX0** (3V3 column, positions 12–13 from the USB end). Those carry the USB serial link; touching them breaks uploads *and* the daemon, and looks like a dead board.

> **The LCD port carries 5V** (VIN). It is the only 5V on the board and it lives at columns 30–33, well away from the control surface. Keep it that way.
<!-- /GEN:wiretable -->

**Label both ends before soldering the second end.** Identical wires get confusing fast.

### How much soldering this is

<!-- GEN:joints -->
| Group | Joints | What |
|---|---:|---|
| GND buses + link | 46 | 3 bare wires soldered every 2nd pad, plus the column-1 link |
| Component legs | 37 | 4 LEDs + 4 resistors (2 each), 7 switches (**3 legs each** — the fourth is clipped) |
| ESP32 socket | 30 | two 15-way strips |
| Signal wires | 24 | 12 wires, both ends |
| LCD port | 12 | 4 male pins + 4 wires |
| **total** | **~149** | at 1–2 min each including inspection, that is **4–6 hours** |
<!-- /GEN:joints -->

### Mounting to wood

<!-- GEN:mounts -->
**Your board already has four mounting holes**, drilled at the factory in the corners, outside the pad grid. Use them. **Do not drill anything.**

| | |
|---|---|
| Board | 120 × 80 mm — silkscreen reads `12*8CM 2.54MM` |
| Grid | 30 rows × 42 columns, 2.54mm pitch |
| Margin outside the grid | 7.9 mm at the sides, 3.2 mm top and bottom |
| Corner holes | factory-drilled, typically 3.0–3.2mm → **M3** |

> Measure one corner hole before buying screws. 3.0–3.2mm takes M3; if yours are smaller, M2.5 or M2 with a washer will still hold a board this light.
<!-- /GEN:mounts -->

Every solder joint is on the underside, so **nothing sits flat on the wood** — each piece
stands off on spacers.

| Item | Fixing | Spacer |
|---|---|---|
| The board | M3 × 12mm + nylon washer, through the four factory corner holes | **6mm** |
| LCD | its own 4 × M3 holes — no drilling | **12–15mm** (its I²C backpack sticks ~10mm off the back) |
| ESP32 | none — it plugs into the socket | — |

- **Pilot-drill the wood at 2mm** for M3, or it splits.
- **Nylon washer under every screw head** — perfboard cracks if you overtighten onto bare FR4.
- Leave the bottom-right of the board clear of clips and cable ties: that is where the USB
  cable comes out, 8mm above the surface.

Lay it out the way it reads: **LCD at the top, the board below it**, with the ESP32's USB
end facing you so the cable exits toward the front and can be strain-relieved to the wood.

---

## 4. Soldering, if you've never done it

**→ Full beginner course with practice exercises: [`SOLDERING.md`](SOLDERING.md).** Do the
six exercises there on a spare kit board *before* touching the real one — about an hour,
and it's the highest-return hour in the project.

The condensed version follows.

> **The thing that surprises everyone:** perfboard has **no wires in it**. Every hole is
> isolated. Nothing is connected until you connect it — with a bent lead, a solder bridge,
> or a jumper. That's why the layout has *buses*: a bare wire soldered across a row, which
> turns 20 isolated holes into one shared node.

**Setup.** Damp sponge or brass wool. Iron at ~340°C. Ventilate — flux fumes are the
irritant, not the metal. Wash hands after handling leaded solder.

**Tin the tip** the moment it's hot: melt a little solder on it, wipe on brass wool. A
dull grey tip transfers almost no heat; a shiny silver one is ready.

**The actual motion** — this is the part people get wrong:

1. Touch the iron so it heats **both** the pad and the lead at once (~2 seconds)
2. Feed solder **into the joint**, not onto the iron
3. It should flow and wet flat almost instantly
4. Remove solder, then iron
5. Don't move the joint while it cools (~2s)

**Total contact: 2–4 seconds.** Longer lifts pads and cooks parts. If it isn't flowing,
stop, add flux, retry — don't just hold the iron there.

| Joint | Looks like | Meaning |
|---|---|---|
| Good | Shiny, concave, volcano-shaped | Solid |
| Cold | Dull, rounded, blobby | Reheat with flux |
| Bridge | Solder across two pads | Wick it off with braid |
| Starved | Pad barely covered | Add solder |

**First-timer order:** practise on 5–10 spare holes with scrap wire before touching the
real board. Ten minutes here saves hours.

**Wire prep:** strip 4–5mm, twist stranded ends, tin them before fitting. Tinned wire goes
into a joint far more predictably.

**Rule of thumb:** solder the **lowest-profile parts first** so the board still lies flat —
with one exception: on a row that carries both a bus *and* component legs, the components go
in first and the bus wire lies on top of their bent legs. §5 gives the order that respects both.

---

## 5. Build, in order

Each step ends with a test that **exercises the thing you just built**, not just a beep.
**Do not proceed past a failing test** — one new joint is easy to debug, thirty is an
all-nighter.

Two habits for the whole build:

- **Beep every new joint** before moving on, and after each stage beep each GND bus
  against the neighbouring signal rows. They must never beep. (There is no 5V on the
  control surface, so the classic GND↔5V check belongs at the LCD port and the socket's
  VIN/GND pads.)
- **Label both ends of every wire before you solder the second end.** Sixteen identical
  wires become indistinguishable the moment they are in a bundle.

> **Read [`CONNECTIONS.md`](CONNECTIONS.md) first.** Every action below is one of its five
> moves. If "bend the cathode leg onto the next pad" doesn't mean anything to you yet,
> that document is where it's explained.

### Pre-flight — before any solder

> **Never used a multimeter?** [`MULTIMETER.md`](MULTIMETER.md) walks through the jacks,
> the dial, and each of these tests. Twenty minutes and you will use it all build.

<!-- GEN:preflight -->
Twenty minutes here. Every one of these has bitten someone building this exact board.

#### P1 — confirm your switches behave like a switch

A 4-leg tactile switch is two pairs of two. The legs within a pair are joined permanently; pressing connects one pair to the other. **On this kit's switches the joined pairs run the long way, down the columns** — measured with a meter, not assumed.

You do not have to match that. The build **clips one leg off every switch**, which makes the board work whichever way the pairs run — `verify-layout.py` proves it for both cases. This check is just to confirm the parts are alive and behave normally.

1. Multimeter to continuity. Take one spare colored switch and one spare small switch.
2. Beep all six leg pairings without pressing. **Exactly two pairings beep.**
3. Press and hold: all four legs beep together. Release: back to two.

✅ **Pass:** two pairs unpressed, everything joined when pressed.

❌ **If only one pair beeps,** or nothing changes when you press, that switch is faulty — try another. **If three or more pairs beep unpressed,** it is shorted; discard it.

> Full meter walkthrough: [`MULTIMETER.md`](MULTIMETER.md).

#### P2 — confirm the resistors are 220Ω

Bands **red · red · brown · gold**. Meter across one: 209–231Ω.
Brown-black-brown is 100Ω and will look fine but run the LEDs bright; red-red-red is 2.2kΩ and they will look dim.

#### P3 — LED polarity and brightness

Long leg is the anode (+) and goes in row 2. Also look *into* the LED: the small flag inside is the cathode. Test each LED with a 220Ω resistor on a breadboard before it is soldered in — a dead LED found now costs nothing.

#### P4 — check the board itself

Before anything is soldered to it, confirm the board is what the layout thinks it is.

1. **Calipers across it.** Should be 120 × 80 mm.
2. **Count the grid.** 42 columns (the silkscreen letters run A–Z then A–P) × 30 rows.
3. **Beep adjacent pads.** Take any two neighbouring holes and check continuity. **They must NOT beep.** Do this in four or five places across the board, including along the edges. *Positive control first:* both probes on the same pad ring **must** beep — otherwise you are measuring oxide, not isolation, and every silent reading is meaningless.
4. **Beep the elongated edge pads to each other.** If they beep, your board has power rails down the edges — tell me before soldering, because the layout puts a GND bus in column 1 and a rail there changes things.
5. **Beep top pad to bottom pad of the same hole.** Beeping means the holes are plated through (sturdier pads, and a joint on one face reaches the other). Silent means they are not — which is fine, the design solders one face only either way.

✅ **Test:** neighbours silent, dimensions match, grid counts match. *(Confirmed on the real board: adjacent pads isolated, edge pads individual.)*

❌ **If neighbouring pads beep:** stop. That is stripboard, not perfboard, and every row is pre-connected. The entire layout would have to change.

#### P5 — cut the socket strips

Count **15 sockets**, cut through the 16th. You need two. Cutting a stacking header sacrifices the socket you cut through — that is normal and the 40-pin strip has enough.

✅ **Test:** both strips push fully onto the ESP32's pin rows with no gap.
<!-- /GEN:preflight -->

### The build

<!-- GEN:steps -->
#### Step 1 — the ESP32 socket  ·  *Move 1*

Two 15-way strips at **columns 30 and 40, rows 8 → 22**. This goes first because it proves the ESP32 and the cable still work before anything else can be blamed.

1. Push **both strips onto the ESP32's pins** first. The module now holds them at exactly the right spacing and squareness — soldering them separately is how people end up desoldering a 15-pin strip.
2. Lower the whole assembly onto the board from the top, pins through the holes.
3. Check the strips landed in columns 30 and 40 — 10 apart — and that the module's USB end points at the **bottom** edge.
4. Solder **one pin on each strip**. Turn it over, check it sits flat and square. Only then do the other 28.
5. Trim the pins flush and pull the ESP32 out.

✅ **Test:** beep from each socket pad on the underside to the matching ESP32 pin (module seated), then beep each pad to its neighbour — no neighbour may beep. Then plug in USB: `ls /dev/cu.*` shows a new port, and `firmware/blink` uploads and blinks.

❌ **If it fails:** A blink that works proves nothing about the socket — the ESP32's own USB carries power and serial, so every socket joint could be cold. Trust the beep test, not the blink.

#### Step 2 — the first GND bus and the ground wire  ·  *Moves 2 and 4*

Row **8** is the only bus row with nothing else in it, so it can go on now. Rows 16, 21 carry button legs and must wait until those buttons are seated (steps 4 and 5).

1. Cut bare 24AWG a little longer than 28 holes.
2. Lay it on the copper face along row **8**, columns 1 → 28, **beside the pad centres, never across them**. A wire lying over a hole blocks the lead you push in later, and the joint still looks perfect from underneath.
3. Tack one end. Check it is straight and clear of every hole. Then solder every 2nd–3rd pad.
4. Leave ~10mm of tail at column 1 — the other two buses join it there.
5. Run wire **12**: from **col 28, row 8** to the socket's **GND** pad at **col 30, row 21**. This is the board's only ground wire.

✅ **Test:** every pad in row 8 beeps to every other, and to the socket's GND pad. No other row beeps to it. Push a spare lead down through a row-8 hole from the top — it must reach the copper, not stop on the bus wire.

#### Step 3 — LEDs, resistors and their four wires  ·  *Moves 1, 3 and 4*

Do **LED 1 completely, including its wire and the test**, before starting LED 2. The first one teaches you the bent-leg move; the other three are then quick.

| LED | long leg (+) | short leg (−) | 220Ω top | 220Ω bottom | wire # → socket |
|---|---|---|---|---|---|
| 1 red | col 4, row 2 | col 4, row 3 | col 4, row 4 | col 4, row 8 | **1** → col 40, row 20 (D13) |
| 2 green | col 11, row 2 | col 11, row 3 | col 11, row 4 | col 11, row 8 | **2** → col 40, row 18 (D14) |
| 3 blue | col 18, row 2 | col 18, row 3 | col 18, row 4 | col 18, row 8 | **3** → col 40, row 17 (D27) |
| 4 yellow | col 25, row 2 | col 25, row 3 | col 25, row 4 | col 25, row 8 | **4** → col 40, row 16 (D26) |

1. **Resistor first** — it is the lower part. Legs into rows 4 and 8 of the same column; bend them so the 6.3mm body sits centred in the 10.2mm span. Solder both, trim.
2. **LED next** — long leg into row 2, short leg into row 3. Solder the **anode only**. Leave the cathode leg full length.
3. **Move 3 — the bent leg.** On the copper face, bend the cathode's leftover length flat until it lies on the **row-4 pad**, where the resistor's top lead already is. Solder it into that same joint. *Now* trim both.
4. The resistor's bottom lead is already in row 8 — the bus. It is grounded; there is nothing else to do.
5. Run that LED's wire from **its own column, row 2** to its socket pad. **Both ends are lap joints** (*Move 5*) — the anode hole holds the LED's own leg and the socket hole holds a header pin, so you are soldering onto existing blobs, not into free holes.

✅ **Test:** beep col 4, row 3 to col 4, row 4 — **must beep** (that is the bent leg doing its job). Beep row 2 to the bus — must **not**. With all four done, seat the ESP32 and run `firmware/ledtest`: all four cycle in order red, green, blue, yellow.

❌ **If it fails:** One LED dark and backwards → its legs are swapped; desolder the anode, rotate, redo. All four dark → the ground wire or the row-8 bus. Wrong LED lighting → two wires swapped at the socket end, which is why you label both ends.

#### Step 4 — the four colored buttons, the second bus, the link  ·  *Moves 1, 2 and 4*

| Button | signal leg (takes the wire) | anchor leg | **CLIP this one** | ground leg (on the bus) | wire # |
|---|---|---|---|---|---|
| 1 red | col 3, row 11 | col 5, row 11 | ~~col 3, row 16~~ | col 5, row 16 | **5** → col 40, row 13 (D32) |
| 2 green | col 10, row 11 | col 12, row 11 | ~~col 10, row 16~~ | col 12, row 16 | **6** → col 40, row 14 (D33) |
| 3 blue | col 17, row 11 | col 19, row 11 | ~~col 17, row 16~~ | col 19, row 16 | **7** → col 40, row 15 (D25) |
| 4 yellow | col 24, row 11 | col 26, row 11 | ~~col 24, row 16~~ | col 26, row 16 | **8** → col 30, row 18 (D4) |

> **Clip one leg off every switch before you seat it** — the one at **column c, row 16**, directly below the signal leg. Snip it flush with the body so it cannot reach the board. Solder the other three.

> **Why.** A tactile switch's two internally-joined pairs may run along the rows or down the columns depending on the part — this kit's run down the columns. If they do, that row-16 leg is on the *signal* node, and soldering it onto the GND bus shorts the button closed forever. Clipping it is safe **either way**, so the board does not depend on which switch you bought. Do not solder all four to 'anchor it better' — `verify-layout.py` fails if the design ever assumes that.

1. **Clip the row-16 leg in the signal column** off all four switches first, while they are still loose and easy to hold.
2. Seat all four. The remaining three legs span rows 11→16 and columns c → c+2. Tack one leg, sight along the row to check the cap is square, then finish.
3. Solder both **row-11** legs and trim them.
4. Solder the remaining **row-16** leg but **leave it long**; bend it flat along the row.
5. Lay the row-16 bus **on top of those bent legs**, cols 1 → 28, and solder through both at once. (Bus-first does not work on this row — the wire would block the holes.)
6. **Link the buses:** bare wire down column 1 from row 8 to row 16. Column 1 is chosen because no signal wire ever runs left of column 3, so nothing crosses this bare wire.
7. Run the four button wires from the row-11 leg in the signal column.


✅ **Test:** every row-16 leg beeps to row 8 and to the socket GND. **No** row-11 leg beeps to any bus while the button is released — and every one does while it is pressed. Then `firmware/btntest` prints `button 0`…`button 3`.

❌ **If it fails:** Several buttons dead at once is the bus or the link, not the switches — that failed twice on the breadboard. **One button permanently pressed almost certainly means you soldered the leg you were told to clip** — desolder it and snip it off. A button that never registers means its signal wire or its row-11 joint.

#### Step 5 — AA / no / yes, the third bus  ·  *same moves*

| Button | signal leg | anchor leg | **CLIP this one** | ground leg | wire # |
|---|---|---|---|---|---|
| AA (always allow) | col 4, row 19 | col 6, row 19 | ~~col 4, row 21~~ | col 6, row 21 | **9** → col 30, row 8 (D23) |
| no (deny) | col 13, row 19 | col 15, row 19 | ~~col 13, row 21~~ | col 15, row 21 | **10** → col 30, row 14 (D18) |
| yes (approve) | col 22, row 19 | col 24, row 19 | ~~col 22, row 21~~ | col 24, row 21 | **11** → col 30, row 13 (D19) |

Identical sequence to step 4 — **including clipping one leg off each switch first**. These are square, and because one leg is clipped **it does not matter which way round they go** — the wire and the clip are defined by position, not by the switch's internals. Solder the row-19 legs, leave the row-21 leg long and bent, bus over it, extend the column-1 link from row 16 to row 21, and run the three wires.

✅ **Test:** all three ground legs beep to row 8. No signal leg beeps to a bus when released. `firmware/btntest` now prints `button 0` … `button 6` — **all seven**.

❌ **If it fails:** btntest reading only some buttons has been a real failure here: an old copy of that sketch scanned 4 pins instead of 7 and made three good switches look dead. Check the sketch declares all 7 GPIOs before you unsolder anything.

#### Step 6 — the LCD port  ·  *Moves 1 and 4*

The LCD is never soldered, so it needs somewhere to plug into. Once the ESP32 is seated its pins are **inside the socket** and nothing can clip onto them — so the board carries its own 4-pin male header at **cols 30–33, row 2**, wired to the socket pads.

| LCD pin | Male pin at | Wire to socket hole | ESP32 pin |
|---|---|---|---|
| GND | col 30, row 2 | col 40, row 21 | **GND** |
| VCC | col 31, row 2 | col 40, row 22 | **VIN** |
| SDA | col 32, row 2 | col 30, row 12 | **D21** |
| SCL | col 33, row 2 | col 30, row 9 | **D22** |

1. Cut a **4-pin male** strip. Seat it at cols 30–33, row 2, short side down through the board.
2. Tack one pin, check it stands square, solder the rest.
3. Run the four wires to the socket pads in the table. **Mark the VCC wire** — it is the only 5V on the board.
4. Connect the LCD with **4 F-F jumpers**, female onto the LCD's own male header, female onto this port. Match the labels, not the colours.

✅ **Test:** beep each port pin to its socket pad, and beep **VCC to GND** — that one must **not**. Then `firmware/lcdtest`: serial prints `found device at 0x27` and text appears.

❌ **If it fails:** Backlit but blank is the contrast pot on the back. Completely dead: try address `0x3F`, and check SDA/SCL are not swapped — the two middle wires are the easy pair to cross.

#### Step 7 — real firmware, then mount it

```bash
arduino-cli compile -u -p /dev/cu.usbserial-0001 --fqbn esp32:esp32:esp32 firmware/agentpad
```

From a serial monitor at 115200, line ending **Newline**:

| Send | Expect |
|---|---|
| `L 0 working` | red LED solid |
| `L 1 blocked` | green LED blinks fast |
| `L 2 working` | blue LED solid |
| `L 3 blocked` | yellow LED blinks fast |
| `D0 hello` | top LCD row changes |
| press each button | `B 0` … `B 6` |

Only once all of that passes, screw the board and the LCD to the wood — then **run the whole test again**. Assembly is when wires get pinched and joints get stressed.

✅ **Test:** every line above, before and after mounting.
<!-- /GEN:steps -->

> **The 3.3V vs 5V question — settled, don't relitigate.**
>
> The LCD1602 is a 5V part and the ESP32's GPIOs are not 5V tolerant. That sounds like a
> problem but isn't, because **I²C is open-drain**: devices only pull the line *down*,
> never drive it up. The only 5V path into the ESP32 is through the backpack's pull-ups,
> leaking **~0.36mA** (4.7kΩ) or **~0.17mA** (10kΩ) into the clamp diodes — far below
> anything harmful, and how most ESP32 + LCD1602 projects are wired. The breadboard
> prototype ran exactly this for hours with a stable display.
>
> **Optional free upgrade:** move the LCD port's VCC wire from the VIN pad to the **3V3**
> pad (**col 40, row 8**) — one wire, one end. If it's readable, keep
> it and the out-of-spec condition disappears at no cost. 1602 modules often dim at 3.3V —
> adjust the contrast pot; if it washes out, move back to VIN, no worse off. A level
> shifter is the textbook fix but adds a part you don't have and another failure mode.

---

## 6. Software

Only needed if this is a fresh Mac; your current one is already set up.

```bash
cd ~/projects/agentpad
cp hooks/agentpad.sh        ~/.claude/agentpad.sh        && chmod +x ~/.claude/agentpad.sh
cp hooks/agentpad-status.sh ~/.claude/agentpad-status.sh && chmod +x ~/.claude/agentpad-status.sh
mise install                      # Python 3.13 + venv
mise exec -- pip install pyserial
```

`~/.claude/settings.json` needs five hooks, each running `~/.claude/agentpad.sh <state>`:

| Hook | State |
|---|---|
| `SessionStart` | `idle` |
| `UserPromptSubmit` | `working` |
| `PermissionRequest` | `blocked` |
| `Stop` | `done` |
| `SessionEnd` | `none` |

plus `statusLine` → `~/.claude/agentpad-status.sh` for the context percentage.

> **Use `PermissionRequest`, never `Notification`.** Measured on this hardware,
> `Notification` fires **6.00 seconds** after the prompt appears — it exists to chase a
> user who walked away. `PermissionRequest` fires at +0.00s.

**Run it:**
```bash
cd ~/projects/agentpad && mise exec -- python daemon.py
tmux attach -t agentpad        # in another terminal
```

**Stop the daemon before uploading firmware.** Only one process can hold the serial port;
uploading while it runs fails with *"Serial data stream stopped: possible serial noise or
corruption"*, which reads like a hardware fault but isn't.

---

## 7. Final acceptance test

1. Press each color button → its window opens, tinted, and focuses
2. Each LED heartbeats when its agent is idle
3. In one agent: `run: curl -sI https://example.com` → **LED blinks fast**
4. Press `yes` → command runs, LED returns to working
5. Repeat, press `no` → declined
6. Type `/model` in an agent → LED blinks (proves non-permission menus work); press Esc
7. LCD bottom row shows the four states plus context %
8. Unplug USB, replug → daemon reconnects on its own
9. Pull the ESP32 out of its socket and push it back → everything still works. That is the
   one part you cannot replace, and the socket is what protects it.

> **Demo tip:** only sandbox-escaping commands prompt. `curl` prompts reliably; `date` and
> `df -h` do **not**. Use curl.

---

## 8. Troubleshooting

| Symptom | Cause |
|---|---|
| No `/dev/cu.*` port | Charge-only cable, or a header pin not soldered through |
| Upload: "Failed to connect" | Hold BOOT during "Connecting…" |
| Upload: "serial noise or corruption" | The daemon is holding the port — stop it |
| LCD backlit, blank | Contrast pot on its back |
| LCD dead | Change `0x27` → `0x3F` in the firmware; check SDA/SCL aren't swapped |
| LCD dead, port beeps fine | The two middle port wires are crossed — SDA and SCL |
| LCD backlight flickers | VCC wire is on 3V3, not VIN — fine electrically, but some backpacks need 5V |
| Board shorted the moment the last bus went on | A signal wire crossing the bare GND link. It runs down **column 1** for exactly this reason — check nothing routes left of column 3 |
| One LED never lights | It's backwards — flip it |
| **Several buttons dead at once** | **GND bus break — not the switches** |
| One button always pressed | Both wires on the same internal pair; rotate 90° |
| Everything dead after adding a part | Solder bridge — beep each GND bus against the neighbouring signal rows |
| LCD flashes `not blocked` | Interlock refused: no live prompt, or you're not on an agent window. Check `daemon.log` |
| `pane` empty in events.jsonl | Claude Code isn't running inside tmux |
| Port name changed | Update `PORT` in `daemon.py` |

---

## 9. If it goes wrong

- **The breadboard prototype is the fallback**, but rebuilding it means pulling the ESP32
  back out of the socket — which is exactly why it is socketed. Budget 20 minutes and follow
  `BREADBOARD.md`; you will also need 4 spare 12mm switches, since the kit's four are now
  soldered down.
- **Record a backup video** of the working device before you start. Ten minutes of
  insurance against a demo-table failure.
- A half-finished case with working guts still demos fine. A perfect case around a dead
  board does not — so keep the electronics passing tests at every step.
