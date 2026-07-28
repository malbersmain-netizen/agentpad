# Agent Pad — soldered build

Moving the working breadboard prototype into a soldered, cased device.

**Scope: 1 LCD + 4 LEDs + 7 buttons.** No bar graph — context usage shows as a number
on the LCD instead, which needs no hardware at all. The firmware still understands the
`G` gauge command and reserves GPIO 5/16/17 for it, so a bar graph can be added later
without touching anything else.

---

## Two rules

**1. Build on the SPARE ESP32.** You bought two. Leave the breadboard prototype fully
assembled and working while you build the permanent one. Never be in a state where you
have zero working devices — especially the night before a demo.

**2. Never solder anything you haven't already proven on the breadboard.** Every part of
this list is already validated. Don't add a new feature and solder it in the same day.

---

## Mounting: how the kit's parts attach

The Freenove parts are breadboard components, not panel-mount ones. That decides the
approach for us:

| Part | How it mounts | Why |
|---|---|---|
| **LCD** | **Panel** — M3 screws to the case face, flying leads to the board | It has 4 mounting holes |
| **Buttons** | **Board** — caps poke through holes in the face | 12mm tactile switches; no collar or nut to bolt with |
| **LEDs** | **Board** — poke through 5mm holes | No bezels or holders in the kit |
| **ESP32** | **Board** — female header, plugs in | Never soldered directly; must stay swappable |

Board-mounted parts normally risk misalignment, but we're designing the case, so:

> **Design the case around the perfboard's 0.1" (2.54mm) grid.** Place buttons and LEDs
> on chosen grid holes, then derive the face hole positions from that same grid.
> Alignment becomes guaranteed rather than hoped for.

**Heights that constrain the design** (measure your own parts, these are typical):

- Tactile switch + cap: **~12–13mm** above the board → sets the face-to-board gap
- 5mm LED body: **~9mm** → shorter than the buttons, so **leave the LED legs long** and
  push each LED up until it meets the face before soldering
- ESP32 + female header: **~15mm** → the deepest thing on the board; set case depth by this
- LCD + its I²C daughterboard: the board on the back is thicker than the display —
  leave clearance behind it

---

## Shopping list

### Must have — tools
| Item | Notes |
|---|---|
| Temperature-controlled soldering iron | Set ~340°C for leaded. A fixed-temp cheapie will cook the LCD header |
| Solder, 60/40 leaded, 0.6–0.8mm | Leaded is far more forgiving for a first build |
| Flux pen | The difference between clean joints and blobs |
| **Multimeter with continuity beep** | **Non-negotiable** — nearly every failure is a cold joint or an invisible bridge |
| Wire strippers | |
| Flush cutters | For trimming leads flush to the board |
| Helping hands or small vise | You need both hands for iron + solder |
| Desoldering braid | For when — not if — you bridge two pads |

### Must have — materials
| Item | Notes |
|---|---|
| Perfboard, plated through-holes, 0.1" | Get **at least 2** — one will be sacrificed to a mistake. ~70×90mm or larger |
| Female header strip, 0.1" | ESP32 is 30-pin = **15 per side**. Buy breakaway strips |
| 22AWG solid-core hookup wire | Board-internal runs; holds its shape |
| 24–26AWG stranded wire | Anything that moves: the LCD's flying leads |
| Heat-shrink tubing, assorted | |
| M3 screws, nuts, standoffs | LCD to face; perfboard to case bosses |

### Nice to have
| Item | Why |
|---|---|
| Solder wick + isopropyl + brush | Cleaning flux residue so you can actually see joints |
| Kapton tape | Holding parts while you solder the first pin |
| Dupont crimps or JST connectors | Makes the LCD detachable instead of hard-wired — worth it |
| Third ESP32 | You're down to zero spares after this build |

### Already have (Freenove kit)
ESP32 (the spare), I²C LCD1602, 4 LEDs (R/G/B/Y), 4× 220Ω resistors, 4 big push buttons
with colored caps, 3 plain push buttons.

---

## Wiring harness map

**Two buses first.** Run bare solid wire across the board for these, then tie everything
to them. This is the perfboard version of the breadboard's power rails — and a floating
rail section caused most of the debugging pain during prototyping.

| Bus | Fed from | Feeds |
|---|---|---|
| **GND bus** | ESP32 `GND` | every button's return leg, every LED resistor, LCD GND |
| **5V bus** | ESP32 `VIN` | LCD VCC only |

### Signal wires

Suggested colors keep 11 near-identical wires straight. **Label every wire with a tape
flag before soldering its far end.**

| # | From (ESP32) | To | Color | Label |
|---|---|---|---|---|
| 1 | GPIO 13 | Red LED anode | red | `LED1` |
| 2 | GPIO 14 | Green LED anode | green | `LED2` |
| 3 | GPIO 27 | Blue LED anode | blue | `LED3` |
| 4 | GPIO 26 | Yellow LED anode | yellow | `LED4` |
| 5 | GPIO 32 | Red button leg | red | `BTN1` |
| 6 | GPIO 33 | Green button leg | green | `BTN2` |
| 7 | GPIO 25 | Blue button leg | blue | `BTN3` |
| 8 | GPIO 4 | Yellow button leg | yellow | `BTN4` |
| 9 | GPIO 19 | Approve button leg | white | `OK` |
| 10 | GPIO 18 | Deny button leg | grey | `NO` |
| 11 | GPIO 23 | Always button leg | purple | `ALW` |
| 12 | GPIO 21 | LCD SDA | orange | `SDA` |
| 13 | GPIO 22 | LCD SCL | brown | `SCL` |
| 14 | VIN | LCD VCC (via 5V bus) | red | `5V` |
| 15 | GND | GND bus | black | `GND` |

### Per-part returns

| Part | Connection |
|---|---|
| Each LED | cathode (short leg) → its own **220Ω** → GND bus |
| Each button | **diagonally opposite** leg → GND bus. **No resistor** — internal pull-ups |
| LCD | GND → GND bus |

> Buttons have 4 legs but only 2 pairs. Use **diagonal** corners so you're across the
> switch, not along a permanently-connected pair. Clip the two unused legs flush.

---

## Solder order

Solder and **test one subsystem at a time**, exactly like the breadboard milestones.
Debugging one new joint is easy; debugging thirty is an all-nighter.

**Before each power-up: continuity-check the new joints, and check GND↔5V for a short.**

| # | Step | Test | Pass condition |
|---|---|---|---|
| 1 | Female header strip only | `ls /dev/cu.*`, upload `firmware/blink` | New port appears; onboard LED blinks |
| 2 | GND + 5V buses | Multimeter continuity along each bus; GND↔5V | Every point on a bus beeps; **no** beep between buses |
| 3 | LCD (4 wires) | Upload `firmware/lcdtest` | Serial prints `found device at 0x27`; text on screen |
| 4 | 4 LEDs + resistors | Upload `firmware/ledtest` | All four cycle in order R→G→B→Y |
| 5 | 7 buttons | Upload `firmware/btntest` | Serial prints `button 0` … `button 6`, one per press, no repeats |
| 6 | Real firmware | Upload `firmware/agentpad`, run daemon | Full flow: button → tmux window → LED → approve |
| 7 | Close the case | Re-run steps 3–6 assembled | Nothing broke during assembly |

**Step 5 is the one to be patient with.** During prototyping, three buttons failed at
once because they shared a broken ground — if several fail together, suspect the bus,
not the switches. If a button reads pressed constantly, its two wires are on the same
internal pair: rotate it 90°.

---

## Running it

```bash
cd ~/projects/agentpad
cp hooks/agentpad.sh ~/.claude/agentpad.sh && chmod +x ~/.claude/agentpad.sh
cp hooks/agentpad-status.sh ~/.claude/agentpad-status.sh && chmod +x ~/.claude/agentpad-status.sh
mise exec -- python daemon.py
```

Then `tmux attach -t agentpad` in another terminal and press a color button.

**Stop the daemon before uploading firmware** — only one process can hold the serial
port, and the failure message ("Serial data stream stopped: possible serial noise or
corruption") looks like a hardware fault but isn't.

If the port name changes after re-plugging, update `PORT` in `daemon.py`.

---

## Case checklist

- Button holes sized to the **cap**, not the switch body — measure the caps
- Face sits **~12–13mm** above the board (button cap height); LED legs left long to reach
- **Clearance behind the LCD** for its I²C daughterboard
- USB cutout clears the **connector housing**, not just the plug
- **Strain-relieve the USB cable** at the case wall — it's what gets yanked
- Case depth ≥ ESP32 + header (~15mm) plus wire-bend room underneath
- Approve/deny/always physically separated from the four agent buttons, and labelled.
  Mixing them up mid-demo means denying what you meant to approve
- Screw bosses positioned on the perfboard's 0.1" grid
