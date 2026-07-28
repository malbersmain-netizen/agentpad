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
| Perfboard, **plated through-holes**, 0.1" | **Buy 2.** Unplated phenolic lifts pads the moment you rework. Need ≥86 × 127mm |
| Female header strip, 0.1" | ESP32 is 30-pin = **15 per side** |
| 22AWG solid-core wire | Board runs; holds its shape |
| 24–26AWG stranded wire | LCD flying leads (it moves — solid core would fatigue and snap) |
| Heat-shrink, assorted | |
| M3 screws, nuts, standoffs | LCD to face, board to case bosses |

### Nice to have
Isopropyl + brush (clean flux so you can see joints) · Kapton tape (holds parts while you
tack the first pin) · Dupont/JST connectors (makes the LCD detachable) · **a third ESP32**
(this build spends your spare).

---

## 2. The case

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
| LED 1 red | 17.0 | 54.8 | ⌀5.2 |
| LED 2 green | 37.3 | 54.8 | ⌀5.2 |
| LED 3 blue | 57.6 | 54.8 | ⌀5.2 |
| LED 4 yellow | 78.0 | 54.8 | ⌀5.2 |
| Button 1 red | 17.0 | 72.5 | square, cap size +0.4 |
| Button 2 green | 37.3 | 72.5 | " |
| Button 3 blue | 57.6 | 72.5 | " |
| Button 4 yellow | 78.0 | 72.5 | " |
| AA | 17.0 | 108.1 | " |
| no | 65.3 | 108.1 | " |
| yes | 80.5 | 108.1 | " |
| USB-C slot | centred, ~12 wide | bottom edge | clears the **housing**, not just the plug |

**Button holes are sized to the CAP, not the switch body.** Measure a cap with calipers
and add ~0.4mm clearance. LED holes ⌀5.2 for a 5mm LED.

Face-to-board gap: **12.5mm** (button cap height). Leave LED legs long so the LEDs can be
pushed up to meet the face before you solder them.

---

## 3. The perfboard

Cut/snap to **34 × 50 holes** (86.4 × 127mm). Score with a knife along a hole row and
snap over a table edge; file the cut smooth.

Grid reference: **col 1, row 1 = top-left**. Case position = `4.3 + (col−1)×2.54` across,
`6.5 + (row−1)×2.54` down.

| What | Columns | Rows |
|---|---|---|
| LCD 4-pin connector | 2–5 | 2 |
| LEDs 1–4 | **6, 14, 22, 30** | 20 |
| LED resistors | same cols | 21–23 (down to GND bus) |
| Select buttons 1–4 | centred on **6, 14, 22, 30** | 25–29 |
| AA button | centred on 6 | 39–43 |
| no button | centred on 25 | 39–43 |
| yes button | centred on 31 | 39–43 |
| **ESP32 header** | **12 and 21** (0.9" apart) | **35–49** |
| GND bus | 1 → 34 | 32 |
| 5V bus | 1 → 34 | 33 |

**Keep rows 1–16 clear of anything tall** — the LCD hangs down into that space from the
face.

> Sanity-check before soldering: dry-fit the ESP32 into loose header strips at cols 12/21
> and confirm it drops in. If the fit is tight, your board's grid isn't true 0.1" — better
> to find that now.

---

## 4. Soldering, if you've never done it

Read this once. It's the difference between an evening and a weekend.

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
Solder two 15-pin female strips at cols 12 and 21, rows 35–49. Tack **one pin each**
first, check the strips are square and the ESP32 still seats, then do the rest.

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
