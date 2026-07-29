# Rebuilding the breadboard prototype

This is the **working demo** — the version that was verified end-to-end. If the soldered
build isn't finished, this is what you present. Rebuild takes about 20 minutes.

**Unplug USB before wiring anything. Plug it in only at the end.**

---

## The rules that make it all work

1. **The ESP32 does NOT go on the breadboard.** It's ~1 inch wide and would cover the
   centre channel. It sits *beside* the board; female-to-male jumpers reach across.
2. **The blue `–` rail is ground.** Nothing grounds to the ESP32 directly except one
   wire. Everything else grounds to the rail.
3. **Buttons straddle the centre trench** and use **diagonally opposite** legs.
4. **If your rail has a gap halfway along**, the two halves are separate. Either keep
   everything on one half, or bridge the gap with a short jumper. *This caused two
   separate multi-button failures during the original build.*

Jumper types: **F-M** = female end on an ESP32 pin, male end in the breadboard.
**M-M** = both ends in the breadboard. **F-F** = both ends on pins (LCD only).

---

## Step 1 — ground (do this first)

| From | To | Jumper |
|---|---|---|
| ESP32 **GND** (the one near 3V3) | breadboard **blue `–` rail** | F-M |

Nothing works without this and it is the easiest thing to forget.

---

## Step 2 — LCD (4 wires, straight to the ESP32)

The LCD never touches the breadboard. Use **F-F** jumpers pin-to-pin:

| LCD pin | ESP32 pin |
|---|---|
| GND | **GND** (the one next to VIN) |
| VCC | **VIN** |
| SDA | **D21** |
| SCL | **D22** |

Address is **0x27**. If it's backlit but blank, turn the contrast pot on its back.

---

## Step 3 — the four LEDs

Left to right, in this order. For each one:

1. Long leg (+) and short leg (−) in **two different rows**
2. **220Ω** resistor from the short-leg row → **blue `–` rail**
3. **F-M** jumper from the long-leg row → the ESP32 pin below

| # | LED | ESP32 pin |
|---|---|---|
| 1 | Red | **GPIO 13** |
| 2 | Green | **GPIO 14** |
| 3 | Blue | **GPIO 27** |
| 4 | Yellow | **GPIO 26** |

A dark LED is simply backwards — flip it, no harm done.

---

## Step 4 — the seven buttons

Straddle the trench. **One leg → its GPIO (F-M). The diagonally opposite leg → blue rail
(M-M).** No resistors — the firmware turns on the ESP32's internal pull-ups.

| Button | Cap | ESP32 pin |
|---|---|---|
| Agent 1 | Red | **GPIO 32** |
| Agent 2 | Green | **GPIO 33** |
| Agent 3 | Blue | **GPIO 25** |
| Agent 4 | Yellow | **GPIO 4** |
| **Approve** | plain | **GPIO 19** |
| **Deny** | plain | **GPIO 18** |
| **Always allow** | plain | **GPIO 23** |

> A button that fires constantly has its second leg not reaching the rail.
> A button that does nothing while others work is usually the same thing.
> **Several buttons dead at once = the ground rail, not the switches.**

---

## Complete pin list

Everything on the ESP32, in one place:

| ESP32 pin | Goes to |
|---|---|
| GND (near 3V3) | blue `–` rail |
| GND (near VIN) | LCD GND |
| VIN | LCD VCC |
| D21 | LCD SDA |
| D22 | LCD SCL |
| GPIO 13 | red LED (+) |
| GPIO 14 | green LED (+) |
| GPIO 27 | blue LED (+) |
| GPIO 26 | yellow LED (+) |
| GPIO 32 | red button |
| GPIO 33 | green button |
| GPIO 25 | blue button |
| GPIO 4 | yellow button |
| GPIO 19 | approve button |
| GPIO 18 | deny button |
| GPIO 23 | always-allow button |

Plus, on the breadboard only: 4 × 220Ω from each LED's cathode row to the blue rail, and
7 × M-M from each button's diagonal leg to the blue rail.

**Jumper budget:** 11 F-M (4 LED + 7 button) + 1 F-M for ground = 12, plus 4 F-F for the
LCD and 7 M-M for button grounds. The kit only has 10 F-M, so you'll need the extra pack.

---

## Step 5 — bring it up

```bash
ls /dev/cu.*                     # expect /dev/cu.usbserial-0001
cd ~/github/agentpad
arduino-cli compile -u -p /dev/cu.usbserial-0001 --fqbn esp32:esp32:esp32 firmware/agentpad
mise exec -- python daemon.py
```

Then in another terminal: `tmux attach -t agentpad`

**Stop the daemon before uploading firmware** — only one process can hold the serial port.

### Test in this order
1. LCD shows `A1 --` / `1- 2- 3- 4-`, all LEDs dark
2. Press each color button → a tinted `claude` window spawns and focuses
3. In one agent: `run: curl -sI https://example.com` → its LED blinks fast
4. Press **yes** → the command runs
5. Type `/model` in an agent → LED still blinks (non-permission menus work too); Esc

> Only sandbox-escaping commands prompt. **`curl` prompts; `date` and `df -h` do not.**
> Use curl when demoing.

---

## If something misbehaves

| Symptom | Cause |
|---|---|
| No `/dev/cu.*` | Charge-only cable, or the board came unplugged |
| LCD backlit but blank | Contrast pot on the back |
| LCD completely dead | Try address `0x3F`; check SDA/SCL aren't swapped |
| One LED never lights | It's backwards — flip it |
| **Several buttons dead** | **Ground rail** — check the split-rail gap |
| One button always pressed | Both wires on the same internal pair — rotate it 90° |
| Everything dead | Missing GND jumper (Step 1) |
| LCD flashes `not blocked` | The interlock refused: no live prompt, or you're not on an agent window |

Full detail in `BUILD.md`; live state in `daemon.log`.
