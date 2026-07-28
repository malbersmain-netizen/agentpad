# Agent Pad — complete build manual

Takes you from loose parts to a working, mounted device. Read section 4 before you touch
the iron; everything else follows in order.

**Scope:** 1 LCD + 4 LEDs + 7 buttons on two kit perfboards, screwed to a wooden backing

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
12mm tactile switches. The LCD is already safe: it is **never soldered** — 4 F-M jumpers,
female onto its own header, so it unplugs and moves.

**2. Solder nothing you haven't already proven on the breadboard.** Everything here is
validated. Don't add features and solder them the same day.

---

## 1. Parts and tools

### From the Freenove kit
ESP32 · I²C LCD1602 · 4 LEDs (R/G/B/Y) · 4× 220Ω · 4 capped push buttons · 3 plain push
buttons · **3× PY-5CM\*7CM perfboards** (two used, one for practice) · **40-pin stacking
header** (cut into two 15-socket strips).

> **The kit's perfboards are SINGLE-SIDED** — copper on one face only. Every solder joint
> goes on that face; components sit on the other. This is normal and fine, but it's why
> the ESP32 needs its own board (§3).

### Buy — tools
| Item | Notes |
|---|---|
| Temperature-controlled soldering iron | ~340°C for leaded solder |
| Solder, 60/40 **leaded**, 0.6–0.8mm | Far more forgiving than lead-free for a first build |
| Flux pen | The difference between clean joints and blobs |
| **Multimeter with continuity beep** | **Non-negotiable.** Nearly every failure is a cold joint or invisible bridge |
| Wire strippers · flush cutters | |
| Helping hands / small vise | You need both hands for iron and solder |
| Desoldering braid | For when — not if — you bridge two pads |

### Buy — materials
| Item | Notes |
|---|---|
| 22AWG solid-core hookup wire | The 15 board-to-board wires and the buses |
| 24–26AWG stranded wire | LCD leads — it moves, so solid core would fatigue and snap |
| Heat-shrink, assorted | |
| Wood backing plate | ~150 × 200mm, any offcut |
| M3 screws + nylon washers/standoffs | Mounting both boards and the LCD |

### Nice to have
Isopropyl + brush (clean flux so you can see joints) · Kapton tape (holds parts while you
tack the first pin) · a second ESP32 if you ever see one in stock.

---

## 2. The case — deferred

**The demo does not depend on a case.** The deliverable is the two soldered boards plus the
LCD, screwed to a wooden plate. That is a solid object you can hand to someone, and it
needs no printer.

and are measured, regenerate the case *from* them rather than building to it.

---

## 3. The board

One **30 × 42 hole double-sided board** (~79 × 109mm), oriented **42 columns across,
30 rows down**. Grid reference: col 1, row 1 = top-left.

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

> **The LCD is still never soldered.** Four F-M jumpers clip onto its own header at one end
> and onto the ESP32's pins at the other, so it stays a reusable part — and no 5V ever runs
> across the control surface.

<!-- GEN:rowplan -->
| Row | What |
|---:|---|
| **2** | **LED anodes (+)** — each also takes that LED's wire to the socket · cols 4, 11, 18, 25 |
| **3** | **LED cathodes (−)** — lead bends over on the copper face to the row-4 pad |
| **4** | 220Ω top lead (the only thing in this hole) |
| **8** | 220Ω bottom lead — lands on the bus · **GND bus** — bare wire, cols 1 → 28 |
| **11** | **Colored button signal legs** · cols 3, 10, 17, 24 |
| **16** | **GND bus** — bare wire, cols 1 → 28 · **Colored button ground legs** · cols 5, 12, 19, 26 |
| **19** | **AA / no / yes signal legs** · cols 4, 13, 22 |
| **21** | **GND bus** — bare wire, cols 1 → 28 · **AA / no / yes ground legs** · cols 6, 15, 24 |

The 3 GND buses join together down **column 28**.

Genuinely free rows (no lead *and* no component body above them): **1, 9, 10, 17, 18, 22, 23, 24, 25, 26, 27, 28, 29, 30**.
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

The USB connector overhangs the board edge, so the cable can reach it.

### The wires

<!-- GEN:wiretable -->
**12 wires**, each from a component pad to the pad of the ESP32 socket pin it serves. All on the same board — short runs, no inter-board loom.

| # | Signal | From — hole | To — ESP32 pin | Socket side | Position |
|---:|---|---|---|---|---:|
| 1 | LED 1 red | col 4, row 2 | **D13** | LEFT | 3 |
| 2 | LED 2 green | col 11, row 2 | **D14** | LEFT | 5 |
| 3 | LED 3 blue | col 18, row 2 | **D27** | LEFT | 6 |
| 4 | LED 4 yellow | col 25, row 2 | **D26** | LEFT | 7 |
| 5 | button 1 red | col 3, row 11 | **D32** | LEFT | 10 |
| 6 | button 2 green | col 10, row 11 | **D33** | LEFT | 9 |
| 7 | button 3 blue | col 17, row 11 | **D25** | LEFT | 8 |
| 8 | button 4 yellow | col 24, row 11 | **D4** | RIGHT | 5 |
| 9 | AA (always allow) | col 4, row 19 | **D23** | RIGHT | 15 |
| 10 | no (deny) | col 13, row 19 | **D18** | RIGHT | 9 |
| 11 | yes (approve) | col 22, row 19 | **D19** | RIGHT | 10 |
| 12 | ground | any GND bus (rows 8, 16, 21) | **GND** | LEFT | 2 |

Plus the LCD's **4** F-M jumpers, which clip straight onto the ESP32's pins and are never soldered:

| Signal | From | To — ESP32 pin |
|---|---|---|
| LCD GND | F-M jumper onto the LCD's own header | **GND** |
| LCD VCC | F-M jumper onto the LCD's own header | **VIN** |
| LCD SDA | F-M jumper onto the LCD's own header | **21** |
| LCD SCL | F-M jumper onto the LCD's own header | **22** |

That is **8 on the left column, 4 on the right**, plus 4 LCD jumpers — **16 landing on the socket** in total.

> **Never wire to RX0 or TX0** (right column, positions 12–13). Those carry the USB serial link; touching them breaks uploads *and* the daemon, and looks like a dead board.
<!-- /GEN:wiretable -->

**Label both ends before soldering the second end.** Identical wires get confusing fast.

### How much soldering this is

<!-- GEN:joints -->
| Board | Joints | What |
|---|---:|---|
| control surface | ~86 | 30 bus + 44 component legs + 12 wire ends |
| ESP32 socket | 22 | two 15-socket strips; 16 of those pads also take a wire |
| **total** | **~108** | at 1–2 min each including inspection, that is **3–5 hours** |
<!-- /GEN:joints -->

### Mounting to wood

Every solder joint is on the underside, so **nothing sits flat on the wood** — each piece
stands off on spacers.

| Item | Hole | Fixing | Spacer |
|---|---|---|---|
| The board | drill 2 diagonal corners to **3.5mm** | #4 × ½″ pan-head wood screw + nylon washer | **6mm** |
| The ESP32 socket | same | same | **6mm** |
| LCD | its own 4 × M3 holes — no drilling | M3 × 16mm | **12–15mm** (its I²C backpack sticks ~10mm off the back) |
| ESP32 | — | none, it plugs into the ESP32 socket | — |

- **Pilot-drill the wood at 2mm** or it splits.
- **Nylon washer under every screw head** — perfboard cracks if you overtighten onto bare
  FR4.
- Perfboard drills easily: back it with scrap wood, go slow, let the bit cut.
- Two diagonal corners per board is plenty and halves the drilling.

Lay it out the way it reads: **LCD at the top, the board below it, the ESP32 socket off to one side**
with its USB facing an edge so the cable exits cleanly and can be strain-relieved to the
wood with a cable clip.

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

**Rule of thumb:** solder the **lowest-profile parts first** so the board still lies flat.
Header → buses → resistors → LEDs → buttons.

---

## 5. Build, in order

Each step ends with a test. **Do not proceed past a failing test** — one new joint is
easy to debug, thirty is an all-nighter.

Before every power-up: **beep the new joints, and check each GND bus does NOT beep against
any signal row.** (There is no 5V on the board, so the old GND↔5V check does not apply here —
do that one on the ESP32 socket, between the VIN and GND pads.)

### Step 0 — drill the mounting holes FIRST

Drill both boards' mounting holes **before any solder goes on**. Drilling a populated
board cracks joints and rains conductive swarf onto the copper face.

Put them in the **5.8mm left/right margins**, not the corners — the top and bottom margins
are only 3.4mm, too narrow for a 3.5mm hole.

### Step 1 — the ESP32 socket, the ESP32 carrier

Do this first: it's the one step that proves the ESP32 and cable still work before
anything else can be blamed.

Solder the two 15-socket strips as described above (ESP32 holding them, soldered from the
underside, pins trimmed).

**Test:** plug the ESP32 in, connect USB.
```bash
ls /dev/cu.*                     # a new usbserial port appears
cd ~/projects/agentpad
arduino-cli compile -u -p /dev/cu.usbserial-0001 --fqbn esp32:esp32:esp32 firmware/blink
```
✅ Onboard LED blinks.

> **Blink does not actually test the ESP32 socket.** The ESP32's own USB carries power and serial,
> so every socket joint could be cold and this would still pass. Test the sockets properly:
> with the ESP32 seated, **beep from each socket's underside pad to the matching ESP32 pin**,
> and beep neighbouring pads against each other to catch bridges — *before* the first
> insertion.

### Steps 2–6 — the board, in order

> **Read [`CONNECTIONS.md`](CONNECTIONS.md) first.** Every action below is one of its five
> moves. If "bend the cathode leg onto the next pad" doesn't mean anything to you yet, that
> document is where it's explained.

<!-- GEN:steps -->
#### Step A — the three GND buses  ·  *Move 2*

Only row **8** is empty enough to bus now. Rows **16, 21** also carry button legs — those buses go on *after* their buttons (steps C and D).

1. Lay bare 24AWG along row **8**, cols 1 → 28, **beside the pads, not over the holes**.
2. Tack one end, check straight, solder every 2nd–3rd pad.
3. Leave a tail at column 28 — the other two buses will join it there.

✅ **Test:** every pad in row 8 beeps to every other. No other row beeps to it.

#### Step B — LEDs and resistors  ·  *Moves 1 and 3*

Do one LED completely, test the idea, then repeat. Per LED:

| LED | long leg (+) | short leg (−) | 220Ω top | 220Ω bottom |
|---|---|---|---|---|
| 1 red | col 4, row 2 | col 4, row 3 | col 4, row 4 | col 4, row 8 |
| 2 green | col 11, row 2 | col 11, row 3 | col 11, row 4 | col 11, row 8 |
| 3 blue | col 18, row 2 | col 18, row 3 | col 18, row 4 | col 18, row 8 |
| 4 yellow | col 25, row 2 | col 25, row 3 | col 25, row 4 | col 25, row 8 |

1. LED in — long leg row 2, short leg row 3. Solder the **anode only**; leave the cathode leg long.
2. Resistor in rows 4 and 8, same column. Bend its leads so the body sits centred. Solder both.
3. **Move 3:** bend the LED's cathode leg flat onto the row-4 pad and solder it there too. Now snip both.
4. The resistor's bottom lead is in row 8 — already the GND bus. Nothing more to do.

✅ **Test:** beep col 3 row 3 to col 3 row 4 — must beep (the bent leg). Beep row 2 to the bus — must **not** beep.

#### Step C — the four colored buttons  ·  *Moves 1 and 2*

| Button | signal leg | ground leg |
|---|---|---|
| 1 red | col 3, row 11 | col 5, row 16 |
| 2 green | col 10, row 11 | col 12, row 16 |
| 3 blue | col 17, row 11 | col 19, row 16 |
| 4 yellow | col 24, row 11 | col 26, row 16 |

1. Seat all four buttons — legs span rows 11→16 and 2 columns.
2. **Solder all four legs of each** (the pairs are internally joined, so it costs nothing and doubles the anchoring).
3. On the **row-16 legs, leave them long**, bend flat along the row.
4. Now lay the row-16 bus **on top of those bent legs** and solder through. Link it to row 8 down column 28.

✅ **Test:** every row-16 leg beeps to row 8. No row-11 leg beeps to any bus.

#### Step D — AA / no / yes  ·  *same as step C*

| Button | signal leg | ground leg |
|---|---|---|
| AA (always allow) | col 4, row 19 | col 6, row 21 |
| no (deny) | col 13, row 19 | col 15, row 21 |
| yes (approve) | col 22, row 19 | col 24, row 21 |

Same sequence: seat, solder all legs, leave the row-21 legs long and bent, then bus over them and link to column 28.

✅ **Test:** all three ground legs beep to row 8. No signal leg beeps to a bus.

#### Step E — the 12 wires to the ESP32 socket  ·  *Moves 4 and 5*

Strip 4mm, tin both ends, label both ends, then solder. Full destinations in the wire table above. All runs stay on this board.

✅ **Test:** beep each wire end-to-end, then beep it against the nearest GND bus — must not beep.
<!-- /GEN:steps -->

### Step 6 — the LCD

Four **F-M jumpers** — female end onto the LCD's own 4-pin header, male end soldered to
**the ESP32 socket**, at the pads for GND, VIN, D21 (SDA) and D22 (SCL). The LCD is never soldered
to and never touches the board, so it stays a reusable part.

**Test:** `firmware/lcdtest`
✅ Serial prints `found device at 0x27` and text appears. Backlit but blank = turn the
contrast pot on its back.

> **The 3.3V vs 5V question — settled, don't relitigate.**
>
> The LCD1602 is a 5V part and the ESP32's GPIOs are not 5V tolerant. That sounds like a
> problem but isn't, because **I²C is open-drain**: devices only pull the line *down*,
> never drive it up. The only 5V path into the ESP32 is through the backpack's pull-ups,
> leaking **~0.36mA** (4.7kΩ) or **~0.17mA** (10kΩ) into the clamp diodes — far below
> anything harmful, and how most ESP32 + LCD1602 projects are wired. The breadboard
> prototype ran exactly this for hours with a stable display.
>
> **Optional free upgrade:** try LCD VCC on **3V3** instead of VIN. If it's readable, keep
> it and the out-of-spec condition disappears at no cost. 1602 modules often dim at 3.3V —
> adjust the contrast pot; if it washes out, move back to VIN, no worse off. A level
> shifter is the textbook fix but adds a part you don't have and another failure mode.

### Step 7 — real firmware, then mount it

```bash
arduino-cli compile -u -p /dev/cu.usbserial-0001 --fqbn esp32:esp32:esp32 firmware/agentpad
```

**Test from a serial monitor at 115200, line ending = Newline:**
- `L 0 working` → red LED solid
- `L 1 blocked` → green LED blinks fast
- `D0 hello` → top LCD row changes
- press buttons → `B 0` … `B 6`

✅ All of that, and **the hardware is finished.**

Only then screw everything to the wood. Re-run the tests once mounted — assembly is when
wires get pinched and joints get stressed.

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
| One LED never lights | It's backwards — flip it |
| **Several buttons dead at once** | **GND bus break — not the switches** |
| One button always pressed | Both wires on the same internal pair; rotate 90° |
| Everything dead after adding a part | Solder bridge — beep each GND bus against the neighbouring signal rows |
| LCD flashes `not blocked` | Interlock refused: no live prompt, or you're not on an agent window. Check `daemon.log` |
| `pane` empty in events.jsonl | Claude Code isn't running inside tmux |
| Port name changed | Update `PORT` in `daemon.py` |

---

## 9. If it goes wrong

- **The breadboard prototype still works.** That's why you built on the spare ESP32.
- **Record a backup video** of the working device before you start. Ten minutes of
  insurance against a demo-table failure.
- A half-finished case with working guts still demos fine. A perfect case around a dead
  board does not — so keep the electronics passing tests at every step.
