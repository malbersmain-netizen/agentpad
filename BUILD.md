# Agent Pad — complete build manual

Takes you from loose parts to a working, mounted device. Read section 4 before you touch
the iron; everything else follows in order.

**Scope:** 1 LCD + 4 LEDs + 7 buttons on two kit perfboards, screwed to a wooden backing
plate. No 3D-printed case — it isn't needed and won't be ready.

**Done means:** press a color button → a tinted `claude` window opens and focuses; its LED
heartbeats; ask it something needing permission → LED blinks fast → press `yes` → the
command runs. One USB cable to the Mac.

---

## Two rules

**1. You have ONE ESP32 — it must stay removable.** That's why it goes in a socket rather
than being soldered down. If the build stalls, unplug it and rebuild the breadboard from
`BREADBOARD.md` in twenty minutes; that is always your fallback demo.

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

`case/agentpad-case.scad` stays in the repo, parametric and unused. Once the boards exist
and are measured, regenerate the case *from* them rather than building to it.

---

## 3. The two boards

Each kit board is **18 rows × 24 columns** (43.2 × 58.4mm of hole field). Orient them
**24 columns across, 18 rows down**; grid reference col 1, row 1 = top-left.

| Board | Holds |
|---|---|
| **A — control surface** | 4 LEDs + resistors, 7 buttons, buses, LCD connector |
| **B — ESP32 carrier** | Two 15-socket header strips, and nothing else |

**Measured footprints** (confirmed on the real parts with calipers):

| Part | Pins across | Pins long |
|---|---|---|
| Colored button | **3 holes** (1 between) | **6 holes** (4 between) |
| Small button | **3 holes** | **3 holes** |
| ESP32 | **11 holes** (pin rows 10 apart) | **15 holes** |

A colored button's legs sit in columns `c−1` and `c+1`, rows **7 and 12**. Its 12mm body is
wider than its legs and overhangs them.

### The board is SINGLE-SIDED — this shapes everything

Copper is on **one face only**, so **every solder joint is on the underside** and every
component sits on top. That is completely normal for LEDs, buttons, resistors and buses.

What it *does* rule out is socketing the ESP32 here: its socket body would have to sit on
the copper face, pressed flat against the very pads you need to solder. And it can't go on
top either — it spans 11 of the 18 rows, leaving 7 where 14 are needed.

> **So the ESP32 gets its own small board**, and both boards screw down to a wooden
> backing plate along with the LCD — one solid object you can hand to someone.

**Board B (ESP32 carrier)** is easy, and single-sided handles it the *normal* way round:
header body on **top**, pins down through the holes, soldered on the **bottom** copper
face. Sockets face up, the ESP32 plugs in from above. No orientation trickery.

This uses 2 of your 3 kit boards — the third is for the practice exercises in
`SOLDERING.md`.

The two boards are joined by **15 wires**. The ESP32 still unplugs from its socket, so
`BREADBOARD.md` stays a live fallback.

| Row | What | Columns |
|---|---|---|
| **1** | **5V bus** — bare wire across | 1 → 24 |
| 2 | 220Ω lying **flat**, one per LED | 4-6, 10-12, 16-18, 22-24 |
| 3 | LED anodes (+) | 3, 9, 15, 21 |
| 4 | LED cathodes (−), straight down to the bus | 3, 9, 15, 21 |
| **5** | **GND bus** — bare wire across | 1 → 24 |
| **7 and 12** | **Colored button legs** | 2-4, 8-10, 14-16, 20-22 |
| **14 and 16** | **AA / no / yes legs** | 3-5, 11-13, 19-21 |
| **17** | **GND bus** (linked to row 5 down column 24) | 1 → 24 |
| 18 | LCD 4-pin connector | 1 → 4 |

Rows **6, 8-11, 13, 15 are spare** — room to shift things if a part doesn't sit where you
expect.

Verified clearances: **3.2mm** between button bodies, **6.7mm** LED→button, **5.0mm**
between the two banks. Re-check any time with
`mise exec -- python tools/verify-layout.py`.

### Board B — the ESP32 carrier

Cut two **15-socket** lengths from the kit's 40-pin stacking header (count 15, cut through
the 16th). Then:

1. Plug **both strips onto the ESP32's pins** — the ESP32 now holds them at exactly the
   right spacing and squareness
2. Lower that assembly onto board B **from the top**, pins through the holes
3. Confirm the pin rows land **10 holes apart** (your ESP32 measures 11 holes across)
4. Solder **one pin per strip** on the underside, check it sits flat, then do the rest
5. Trim the pins flush and pull the ESP32 out

Soldering the strips separately and *then* trying to seat the ESP32 is how people end up
desoldering a 15-pin strip. Let the ESP32 hold them.

Leave a clear edge on board B for the 15 wires and room for two mounting screws.

### The 15 wires between the boards

Each solders to the pad under the corresponding header pin on board B.

| Wire | Board A | ESP32 pin |
|---|---|---|
| LED 1 red | resistor end, col 6 row 2 | GPIO 13 |
| LED 2 green | resistor end, col 12 row 2 | GPIO 14 |
| LED 3 blue | resistor end, col 18 row 2 | GPIO 27 |
| LED 4 yellow | resistor end, col 24 row 2 | GPIO 26 |
| Button 1 red | leg col 2 row 7 | GPIO 32 |
| Button 2 green | leg col 8 row 7 | GPIO 33 |
| Button 3 blue | leg col 14 row 7 | GPIO 25 |
| Button 4 yellow | leg col 20 row 7 | GPIO 4 |
| AA | leg col 3 row 14 | GPIO 23 |
| no | leg col 11 row 14 | GPIO 18 |
| yes | leg col 19 row 14 | GPIO 19 |
| 5V | 5V bus (row 1) | VIN |
| GND | GND bus (row 5 or 17) | GND |
| SDA | LCD connector, row 18 | GPIO 21 |
| SCL | LCD connector, row 18 | GPIO 22 |

**Label both ends before soldering the second end.** Fifteen identical wires get confusing
fast. Leave them long enough that the two boards can lie side by side while you work —
you can always dress them shorter once it's mounted.

### Mounting to wood

| Item | How |
|---|---|
| Board A, board B | Drill the **corner holes out to 3mm** (perfboard drills easily), then wood screws with a nylon washer or standoff so the underside joints don't touch the wood |
| LCD | Its own 4 corner holes, M3 |
| ESP32 | Nothing — it just plugs into board B |

**Leave a few mm of standoff under each board.** All your solder joints are on the
underside; pressing them flat against wood risks shorts and stresses the joints.

Lay it out the way it reads: LCD at the top, board A below it, board B off to one side
with its USB facing an edge so the cable exits cleanly.

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

### Step 1 — board B, the ESP32 carrier

Do this first: it's the one step that proves the ESP32 and cable still work before
anything else can be blamed.

Solder the two 15-socket strips as described above (ESP32 holding them, soldered from the
underside, pins trimmed).

**Test:** plug the ESP32 in, connect USB.
```bash
ls /dev/cu.*                     # a new usbserial port appears
cd ~/projects/agentpad
arduino-cli upload -p /dev/cu.usbserial-0001 --fqbn esp32:esp32:esp32 firmware/blink
```
✅ Onboard LED blinks. Nothing else is connected, so a failure here is the cable, the
socket, or a cold joint.

### Step 2 — board A, the buses

Bare solid wire straight across: **row 1** (5V), **rows 5 and 17** (GND). Link the two GND
rows with a wire down **column 24**. Tack each at one end, check it's straight, then solder
every second or third pad.

> The board has no traces. A bus is what turns 24 isolated holes into one shared node — it
> is the single most important thing on the board.

**Test:** multimeter continuity.
✅ Every point on a bus beeps · **5V ↔ GND does NOT beep**

Repeat that second check after *every* stage from here. If the buses ever beep together
you've bridged something — find it before adding another part.

### Step 3 — LEDs and resistors

Per LED: **anode (long leg)** in row 3, **cathode (short leg)** in row 4, cathode leg bent
straight down into the **GND bus at row 5**. The **220Ω lies flat in row 2**, one end level
with the anode column, the other end taking that LED's wire to the ESP32.

| LED | Column | ESP32 |
|---|---|---|
| Red | 3 | GPIO 13 |
| Green | 9 | GPIO 14 |
| Blue | 15 | GPIO 27 |
| Yellow | 21 | GPIO 26 |

**Test:** temporarily wire the four LED lines plus GND to the ESP32 and upload
`firmware/ledtest`.
✅ All four cycle red → green → blue → yellow. One dark = it's backwards; flip it.

### Step 4 — the four colored buttons

Legs in **rows 7 and 12**, columns **2-4, 8-10, 14-16, 20-22**. Use **diagonally opposite**
legs: the top-left one takes its wire to the ESP32, the bottom-right one goes to the GND
bus. **No resistors** — the firmware enables internal pull-ups. Clip the unused legs flush.

| Button | Left leg column | ESP32 |
|---|---|---|
| 1 red | 2 | GPIO 32 |
| 2 green | 8 | GPIO 33 |
| 3 blue | 14 | GPIO 25 |
| 4 yellow | 20 | GPIO 4 |

**Test:** `firmware/btntest`, serial monitor at 115200.
✅ `button 0` … `button 3`, one line per press, no repeats.

### Step 5 — AA / no / yes

Small 3×3 buttons, legs in **rows 14 and 16**, columns **3-5, 11-13, 19-21**. Same diagonal
rule.

| Button | Left leg column | ESP32 |
|---|---|---|
| AA (always allow) | 3 | GPIO 23 |
| no (deny) | 11 | GPIO 18 |
| yes (approve) | 19 | GPIO 19 |

**Test:** `firmware/btntest` again.
✅ `button 0` … `button 6`.

> **Several buttons dead at once means the GND bus, not the switches.** That exact failure
> happened twice on the breadboard and cost an hour each time.
> A button reading *permanently pressed* has both wires on the same internal pair — rotate
> it 90°.

### Step 6 — the LCD

Four **stranded** wires from the row-18 connector: GND → GND bus, VCC → 5V bus, SDA and SCL
out to the ESP32 (GPIO 21 and 22). Long enough to set the LCD down beside the board.

**Test:** `firmware/lcdtest`
✅ Serial prints `found device at 0x27` and text appears. Backlit but blank = turn the
contrast pot on its back.

### Step 7 — real firmware, then mount it

```bash
arduino-cli upload -p /dev/cu.usbserial-0001 --fqbn esp32:esp32:esp32 firmware/agentpad
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
