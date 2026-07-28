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

## Bill of materials

### Already have (from the Freenove kit)
| Part | Qty | Notes |
|---|---|---|
| ESP32 (ESP-WROOM-32, 30-pin) | 1 | the **spare** one |
| I²C LCD1602 | 1 | address 0x27 |
| LEDs — red, green, blue, yellow | 4 | agent identity |
| 220Ω resistors | 4 | one per LED |
| Big push buttons + colored caps | 4 | agent select |
| Plain push buttons | 3 | approve / deny / always-allow |

### Need to buy
| Item | Why |
|---|---|
| Perfboard / protoboard (plated holes) | Get more than you think you need |
| **Female header strip** | ESP32 plugs in — never solder the ESP32 directly |
| 22AWG solid-core wire | Board-internal runs |
| 24–26AWG stranded wire | Anything that moves: panel buttons, LEDs |
| Heat-shrink tubing | |
| M2/M3 standoffs + screws | Mounting the board in the case |

### Tools
| Tool | Why |
|---|---|
| Temperature-controlled soldering iron | A fixed-temp cheapie will cook the LCD header |
| Solder — 60/40 leaded, thin | Leaded is far more forgiving for a first build |
| Flux pen | The difference between clean joints and blobs |
| **Multimeter with continuity beep** | **Non-negotiable.** Most failures are cold joints or invisible bridges |
| Wire strippers | |
| Flush cutters | |
| Helping hands or small vise | |
| Desoldering braid | For when — not if — you bridge two pads |

---

## Pin map (unchanged from the prototype)

| Function | GPIO |
|---|---|
| LEDs — red, green, blue, yellow | 13, 14, 27, 26 |
| Agent buttons — red, green, blue, yellow | 32, 33, 25, 4 |
| Approve | 19 |
| Deny | 18 |
| Always-allow ("yes, don't ask again") | 23 |
| LCD I²C — SDA / SCL | 21, 22 |
| LCD power | VIN (5V) + GND |
| *reserved, unused* — bar graph if ever added | 5, 16, 17 |

Every button: one leg to its GPIO, the diagonal leg to ground. **No resistors** —
internal pull-ups do the job. Every LED: long leg to its GPIO, short leg through a
220Ω resistor to ground.

---

## Build order

Solder and **test one subsystem at a time**, exactly like the breadboard milestones.
Debugging one new joint is easy; debugging thirty is an all-nighter.

1. **Header strip for the ESP32.** Plug it in, confirm it still enumerates
   (`ls /dev/cu.*`) and that a sketch uploads. Nothing else attached.
2. **Ground and 3V3/5V distribution.** Run the power buses first. Beep out every
   node with the multimeter *before* anything is connected to them.
3. **LCD** (4 wires: GND, VIN, SDA→21, SCL→22). Upload `firmware/lcdtest` — it
   scans I²C and prints the address it finds.
4. **4 LEDs + resistors.** Upload `firmware/ledtest`, watch them cycle in order.
5. **7 buttons.** Upload `firmware/btntest`, confirm `button 0` … `button 6` on serial.
6. **Real firmware** (`firmware/agentpad`), then the daemon.

After each step: continuity-check the new joints, and look for solder bridges on
neighbouring pads with a bright light.

---

## Case notes

Check these before committing to a print:

- **Button holes are sized to the CAP, not the switch body.** Measure the colored
  caps, not the button underneath.
- **LCD needs a window plus clearance behind it** for the I²C daughterboard soldered
  to its back — that board is thicker than the display.
- **USB port cutout** must clear the *connector housing*, not just the plug.
- **Strain-relieve the USB cable** at the case wall. It's the one thing that will get
  yanked repeatedly.
- Leave depth for the ESP32 *plus* its header strip — that's ~15mm, more than the
  bare board.
- Physically separate approve/deny/always from the four agent buttons, and label them.
  Mixing them up mid-demo means denying something you meant to approve.

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
