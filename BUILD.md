# Agent Pad — complete build manual

Takes you from loose parts to a working device in a case. Read section 4 before you
touch the iron; everything else you can follow in order.

**Scope:** 1 LCD + 4 LEDs + 7 buttons. No bar graph (context usage shows as a number on
the LCD). Firmware still reserves GPIO 5/16/17 for a gauge if you ever add one.

**Done means:** press a color button → a tinted `claude` window opens and focuses; its
LED heartbeats; ask it something needing permission → LED blinks fast → press `yes` →
the command runs. All from the case, with one USB cable to the Mac.

---

## Two rules

**1. Build on the SPARE ESP32.** You have two. Leave the breadboard prototype assembled
and working until the new one passes every test. Never be at zero working devices.

**2. Solder nothing you haven't already proven on the breadboard.** Everything here is
validated. Don't add features and solder them the same day.

---

## 1. Parts and tools

### From the Freenove kit
ESP32 (the spare) · I²C LCD1602 · 4 LEDs (R/G/B/Y) · 4× 220Ω · 4 capped push buttons ·
3 plain push buttons.

### Buy — tools
| Item | Notes |
|---|---|
| Temperature-controlled soldering iron | ~340°C for leaded solder. A fixed-temp cheapie will cook the LCD header |
| Solder, 60/40 **leaded**, 0.6–0.8mm | Far more forgiving than lead-free for a first build |
| Flux pen | The difference between clean joints and blobs |
| **Multimeter with continuity beep** | **Non-negotiable.** Nearly every failure is a cold joint or invisible bridge |
| Wire strippers | |
| Flush cutters | Trimming leads flush |
| Helping hands / small vise | You need both hands for iron and solder |
| Desoldering braid | For when — not if — you bridge two pads |

### Buy — materials
| Item | Notes |
|---|---|
| Perfboard, **plated through-holes**, 0.1" | **Buy 2.** See the warning below — the kit does **not** include one. Need ≥86 × 127mm (9×15cm ideal, 8×12cm minimum) |
| Female header strip, 0.1" | ESP32 is 30-pin = **15 per side** |
| 22AWG solid-core wire | Board runs; holds its shape |
| 24–26AWG stranded wire | LCD flying leads (it moves — solid core would fatigue and snap) |
| Heat-shrink, assorted | |
| M3 screws, nuts, standoffs | LCD to face, board to case bosses |

> ### The kit's perfboards are 3mm too narrow
>
> The kit **does** include three `PY-5CM*7CM` perfboards (real perfboard — copper ring
> around every hole; not to be confused with the white solderless breadboard, which
> also ships with the kit and cannot be soldered).
>
> They are just too small for this layout, and it isn't a packing problem:
>
> | Row | Outer-edge span | Widest kit board | |
> |---|---|---|---|
> | 4 select buttons | 73.0mm | 70mm | short by 3mm |
> | AA / no / yes | 75.5mm | 70mm | short by 5.5mm |
>
> The button positions are fixed by the case face, so the row is simply wider than the
> board. Three ways out:
>
> 1. **Buy one 9×15cm perfboard (~$3).** Single board, this layout unchanged. Recommended.
> 2. **Narrow the pitch** to 7 holes (17.78mm) instead of 8, and re-render the case —
>    free while nothing is printed, and the cluster then fits a kit board.
> 3. **Split across 2–3 kit boards** joined by wire looms. Free, but every extra loom is
>    more joints and more places for a cold joint to hide.

### Nice to have
Isopropyl + brush (clean flux so you can see joints) · Kapton tape (holds parts while you
tack the first pin) · Dupont/JST connectors (makes the LCD detachable) · **a third ESP32**
(this build spends your spare).

---

## 2. The case — deferred

**The demo does not depend on the case.** Assume it won't be printed in time: the
deliverable is the three soldered boards plus the LCD on flying leads, mounted to a flat
backing plate.

The model in `case/agentpad-case.scad` is parametric and stays in the repo. Once the
boards are actually built and measured, regenerate it *from* them rather than building to
it. Everything below is reference for that later pass.

<details>
<summary>Case reference (for later)</summary>



Case **95 × 140 × 28mm**, USB-C exits the bottom edge.

### Depth — this decides the whole layout

| ESP32 placement | Needs | Verdict |
|---|---|---|
| Stacked under the perfboard | 32.7mm | **Won't close** |
| **Coplanar** (beside components) | 24.2mm | ✅ |

So the ESP32 lies **on the same board plane** as everything else, vertically in the
bottom-centre with its USB pointing at the bottom edge. `AA` sits to its left, `no`/`yes`
to its right — which is how you already drew them.

Stack-up: face 2.5 + tallest part 13.6 (ESP32 on header) + board 1.6 + wire room 4 +
back 2.5 = **24.2mm**.

### LCD cutout — the expensive mistake

The "80 × 36mm" figure is the **module outline**, not the glass. Cut that and the module
drops straight through.

| Feature | Size |
|---|---|
| Cut this — viewing window | **64.5 × 16mm** |
| Module PCB behind it | 80 × 36mm |
| M3 mounting holes | ~75 × 31mm centres |

At 80mm wide the module spans **84% of the 95mm case** — margins are only 7.5mm. Measure
your own module before finalising; these vary a little by supplier.

### Face hole positions

Measured from the **top-left inside corner**. Pitch is a whole number of 0.1" holes so the
board grid and the case agree by construction.

| Feature | X (mm) | Y (mm) | Hole |
|---|---|---|---|
| LCD window (centred) | 15.3 – 79.8 | 30 – 46 | 64.5 × 16 rectangle |
| LED 1 red | 24.64 | 54.8 | ⌀5.2 |
| LED 2 green | 39.88 | 54.8 | ⌀5.2 |
| LED 3 blue | 55.12 | 54.8 | ⌀5.2 |
| LED 4 yellow | 70.36 | 54.8 | ⌀5.2 |
| Button 1 red | 24.64 | 72.5 | square, cap size +0.4 |
| Button 2 green | 39.88 | 72.5 | " |
| Button 3 blue | 55.12 | 72.5 | " |
| Button 4 yellow | 70.36 | 72.5 | " |
| AA | 24.64 | 108.1 | " (under column 1) |
| no | 55.12 | 108.1 | " (under column 3) |
| yes | 70.36 | 108.1 | " (under column 4) |

**Pitch is 15.24mm — exactly 6 perfboard holes**, chosen so the row fits the kit's
18 × 24 hole boards (58.4mm of hole field). Gap between caps is 3.6mm. All seven
buttons and all four LEDs share the same four columns, so the board grid and the face
agree by construction. Change `PITCH_HOLES` in the .scad to move everything at once.
| USB-C slot | centred, ~12 wide | bottom edge | clears the **housing**, not just the plug |

**Button holes are sized to the CAP, not the switch body.** Measure a cap with calipers
and add ~0.4mm clearance. LED holes ⌀5.2 for a 5mm LED.

Face-to-board gap: **12.5mm** (button cap height). Leave LED legs long so the LEDs can be
pushed up to meet the face before you solder them.

---

## 3. The board — everything on ONE kit board

A kit board is **18 rows × 24 columns** (43.2 × 58.4mm of hole field). It all fits,
because the **ESP32 hangs underneath on its socket** and only consumes two rows of holes
instead of a block of top-side space.

Orient the board **24 columns across, 18 rows down**. Grid reference: col 1, row 1 =
top-left. All four LEDs and the four select buttons share columns **3, 9, 15, 21**
(6-hole pitch).

**Measured footprints** (confirmed on the real parts):

| Part | Pins across | Pins long |
|---|---|---|
| Colored button | **3 holes** (1 hole between) | **6 holes** (4 holes between) |
| Small button | **3 holes** | **3 holes** |

So a colored button's legs sit in columns `c−1` and `c+1`, rows **6 and 11**. Its 12mm
body is wider than its legs and overhangs them.

**The ESP32 measures 11 holes across × 15 long**, so its pin rows are **10 apart (1.0 inch)**
and each row is 15 pins. That spacing drives the whole row plan — a solver found only two
valid arrangements; this is the better one.

| Row | What | Columns |
|---|---|---|
| **1** | **5V bus** — bare wire across | 1 → 24 |
| 2 | 220Ω lying **flat**, one per LED | 4-6, 10-12, 16-18, 22-24 |
| 3 | LED anodes (+) | 3, 9, 15, 21 |
| 4 | LED cathodes (−), straight down to the bus | 3, 9, 15, 21 |
| **5** | **GND bus** — bare wire across | 1 → 24 |
| **6** | **ESP32 header, row A** (ESP32 plugs in from BELOW) | 15 pins |
| **7 and 12** | **Colored button legs** | 2-4, 8-10, 14-16, 20-22 |
| **13 and 15** | **AA / no / yes legs** | 3-5, 11-13, 19-21 |
| **16** | **ESP32 header, row B** (10 holes from row A) | 15 pins |
| **17** | **GND bus** (linked to row 5 down column 24) | 1 → 24 |
| 18 | LCD 4-pin connector | 1 → 4 |

Verified clearances: **3.2mm** between button bodies, **6.7mm** LED→button, 2.4mm between
the two button banks. Re-check any time with
`mise exec -- python tools/verify-layout.py`.

> Both header rows sit clear of every component body — that matters because the header's
> solder joints protrude on the top side, and a button sitting on top of them wouldn't lie
> flat. If you move anything, re-run the verifier.

### Why this works

- **The ESP32 is on the underside.** You solder two 15-pin female strips at rows 2 and
  11; the ESP32 plugs in from beneath. Its body is 55mm long, so it lies along the 24-col
  axis and its **USB overhangs the board edge** — which makes the cable easy to reach.
- **No collision underneath.** Button legs protrude ~3mm below the board; the ESP32 sits
  8.5mm below on its header, so they clear each other.
- **Rows 2 and 11 are otherwise empty**, which is exactly why the clusters are placed
  where they are. If you move a button bank, re-check that both header rows stay free.
- If your ESP32 measures **1.0 inch** between pin rows rather than 0.9, use rows **1 and
  11** and move the GND bus to row 3.

### The only off-board wiring

Four **stranded** wires to the LCD: GND → GND bus, VCC → 5V bus, SDA → GPIO 21,
SCL → GPIO 22. Leave them long enough to set the LCD down beside the board while you
work. That is the entire loom.

> Mount the board and the LCD to a flat backing plate (plywood, acrylic, even stiff foam
> board) with standoffs. That turns two loose pieces into one object you can hand to
> someone, and needs no 3D printer.

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

Before every power-up: **beep the new joints, and check GND↔5V does NOT beep.**

### Step 1 — ESP32 header

The kit's **40-pin header is a stacking type** — sockets on one face, long pins on the
other. Cut two **15-socket** lengths (count 15, cut through the 16th; you lose that one).

> **Orientation matters and is hard to undo.** Insert the strips from **UNDERNEATH** the
> board so the pins push **up through** the holes and the **sockets hang below**. Solder
> on the **top** side, then trim the pins flush.
>
> Sockets facing *down* is what lets the ESP32 plug in from below — which is the only
> reason everything fits on one board. Fitted the intuitive way (pins down, sockets up),
> the ESP32 would have to sit on top, where there is no room beside 7 buttons and 4 LEDs.

**The trick that guarantees alignment:**

1. Plug **both strips onto the ESP32's pins** first — the ESP32 now holds them at exactly
   the right spacing and squareness
2. Push that whole assembly up into the board from below
3. Confirm the pins land in **rows 6 and 16**
4. Solder **one pin per strip**, check it sits flat, then do the rest
5. Trim the pins flush and pull the ESP32 out

Soldering the strips separately and *then* trying to seat the ESP32 is how people end up
desoldering a 15-pin strip, which is genuinely miserable.

**Test:** plug in the ESP32 and the USB cable.
```bash
ls /dev/cu.*                      # a new usbserial port appears
cd ~/projects/agentpad
arduino-cli upload -p /dev/cu.usbserial-0001 --fqbn esp32:esp32:esp32 firmware/blink
```
✅ Onboard LED blinks. If no port appears, it's the cable or the header — nothing else is
connected yet.

### Step 2 — the two buses
Bare solid wire across row 32 (GND) and row 33 (5V). Solder to every 3rd or 4th hole.
Then one wire from an ESP32 `GND` pin to the GND bus, one from `VIN` to the 5V bus.

**Test:** continuity along each bus end to end; GND↔5V must **not** beep.
✅ Every point on a bus beeps; the two buses are isolated.

> The buses are the perfboard version of the breadboard's power rails. A broken rail
> section caused most of the prototype's bugs — twice.

### Step 3 — LCD
Four **stranded** flying leads, long enough to reach the face and let it hinge open:

| LCD | To |
|---|---|
| GND | GND bus |
| VCC | 5V bus |
| SDA | GPIO 21 |
| SCL | GPIO 22 |

**Test:** `arduino-cli upload ... firmware/lcdtest`
✅ Serial prints `found device at 0x27` and the screen shows text. Blank but backlit =
turn the contrast pot on its back.

### Step 4 — LEDs and resistors
Per LED: **long leg (+)** to its GPIO, **short leg (−)** through its own 220Ω to the GND
bus. Leave legs long so the LED reaches the face.

| LED | GPIO |
|---|---|
| Red | 13 |
| Green | 14 |
| Blue | 27 |
| Yellow | 26 |

**Test:** `arduino-cli upload ... firmware/ledtest`
✅ All four cycle in order red → green → blue → yellow. One dark = it's backwards; flip it.

### Step 5 — the seven buttons
Each button straddles nothing here — it just sits in 4 holes. Use **diagonally opposite**
legs: one to its GPIO, the other to the GND bus. **No resistors** (internal pull-ups).
Clip the two unused legs flush.

| Button | GPIO |
|---|---|
| 1 red | 32 |
| 2 green | 33 |
| 3 blue | 25 |
| 4 yellow | 4 |
| yes (approve) | 19 |
| no (deny) | 18 |
| AA (always allow) | 23 |

**Test:** `arduino-cli upload ... firmware/btntest`, open a serial monitor, press each.
✅ `button 0` … `button 6`, one line per press, no repeats.

> **If several buttons fail at once, suspect the GND bus — not the switches.** That exact
> failure happened twice during prototyping and wasted an hour each time.
> A button that reads *permanently pressed* has both wires on the same internal pair:
> rotate it 90°.

### Step 6 — real firmware
```bash
arduino-cli upload -p /dev/cu.usbserial-0001 --fqbn esp32:esp32:esp32 firmware/agentpad
```
**Test from a serial monitor at 115200, line ending = Newline:**
- `L 0 working` → red LED solid
- `L 1 blocked` → green LED blinks fast
- `D0 hello` → top LCD row changes
- press buttons → `B 0` … `B 6`

✅ All of the above. **Hardware is now finished.**

### Step 7 — into the case
1. Mount the LCD to the face with M3 screws
2. Push each LED up to the face, then solder its legs at final height
3. Seat the board on its standoffs; check every cap protrudes and springs back
4. Route and strain-relieve the USB cable at the wall
5. Close it up, then **re-run steps 3–6 assembled** — assembly is when wires get pinched

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
| Everything dead after adding a part | Solder bridge — check GND↔5V continuity |
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
