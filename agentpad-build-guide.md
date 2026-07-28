# Agent Pad — Complete Build Guide (macOS)

A physical control surface for Claude Code. Four LEDs show what four agents are doing, an LCD shows detail, four buttons pick an agent, and an N64 controller approves or denies permission prompts.

Assumes zero electronics experience. Nothing is soldered.

---

## 1. Shopping list

### RadioShack of Bozeman — 2855 N 19th Ave, opens 9am, (406) 587-1613

| Item | Price | Notes |
|---|---|---|
| [Freenove Ultimate Starter Kit](https://radioshack-of-bozeman-640025.shoplightspeed.com/pi-4-acckit-freenove-ultimate-starter-kit-for-rasp.html) | $79.95 | **Being held for you. Only 1 in stock.** Contains LCD, LEDs, buttons, resistors, breadboard |
| [ESP32 dev board](https://radioshack-of-bozeman-640025.shoplightspeed.com/wifi-board-hiletgo-esp-wroom-32-esp32-esp-32s-deve.html) × 2 | $9.95 ea | **Only 2 in stock — buy both.** Headers confirmed pre-soldered |
| [N64 USB controller](https://radioshack-of-bozeman-640025.shoplightspeed.com/n64-saffun-classic-n64-controller-saffun-n64-wired.html) | $22.99 | Backup: [NES controller](https://radioshack-of-bozeman-640025.shoplightspeed.com/suily-usb-controller-for-nes-games-suily-pc-usb-co.html), $11.99 |
| [Edgelec 30cm male-to-female jumpers](https://radioshack-of-bozeman-640025.shoplightspeed.com/electronics-parts/lights/led-strips/jumpers/) | ~$10 | **Essential** — the ESP32 doesn't fit on a breadboard. See §6 |
| [Hiearcool 7-in-1 USB-C hub](https://radioshack-of-bozeman-640025.shoplightspeed.com/cables-and-adapters/usb-cable-types/hubs/) | ~$40 | 100W PD passthrough lets you charge while building. Count the USB-A ports — you need 2 |
| [USB-**A** to USB-**C** data cable](https://radioshack-of-bozeman-640025.shoplightspeed.com/cables-and-adapters/usb-cable-types/usb-type-c/usb-type-c-cables/) | ~$12 | **A-to-C, not C-to-C.** Hub USB-C ports are often power-only with no data lines. Also: not a charge-only cable |
| [Breadboard, Chanzon 400-point](https://radioshack-of-bozeman-640025.shoplightspeed.com/electronics-parts/diy/breadboards/) | ~$8 | Optional — the kit includes one |

**No soldering required.** The ESP32 ships with headers pre-attached and the LCD has its own. Skip the iron, solder, flux, and wick entirely.

### What the Freenove kit supplies

Confirmed from the contents sheet — you need nothing else for the core build:

| Part | Qty | Used for |
|---|---|---|
| LCD Module | 1 | The display |
| Red / Green / Blue / Yellow LEDs | 10 / 4 / 4 / 4 | One per agent |
| Resistor-220 | 20 | Four, one per LED |
| Big Push Button + Red/Green/Blue/Yellow caps | 4 + 4 | Agent keys, color-matched to the LEDs |
| Push Button | 6 | Spares |
| Project Board (breadboard) | 1 | Everything else |
| 65 Jump Wire M-M | 65 | Breadboard-internal connections |
| 10 Jump Wire F-F | 10 | LCD directly to ESP32 |
| 10 Jump Wire F-M | 10 | ESP32 to breadboard — **the tight one, see §6** |

Bonus parts you now have for stretch goals: **servo** (a physical flag), **joystick**, **potentiometers ×3**, **active and passive buzzers**.

**Leave in the box:** GPIO Extension Board, 40 Pin GPIO Cable, ADC Module, 40 Pin Headers. All Raspberry Pi-specific or already handled by the ESP32.

### Using the Freenove tutorial

The full tutorial is at https://docs.freenove.com/projects/fnk0020/en/latest/ — Chapter 20 covers the I²C LCD1602, Chapter 2 the buttons, Chapter 1 the LEDs. It's genuinely useful for understanding the components, with two rules:

**Read the diagrams, ignore the code.** Their code is `RPi.GPIO` / WiringPi and won't run on an ESP32. The circuits translate perfectly — an LED with a resistor to ground is the same on any board.

**Mentally delete the GPIO Extension Board.** Every diagram shows a white T-shaped adapter bringing the Pi's 40 pins to the breadboard. You don't have one. Read from the breadboard outward and treat your ESP32 jumper as replacing that whole left-hand side.

**Ignore their pin numbers.** Diagrams reference Pi numbering like GPIO17 or BCM27. Meaningless on ESP32 — use the pin tables in this guide.

Store home: [radioshack-of-bozeman.shoplightspeed.com](https://radioshack-of-bozeman-640025.shoplightspeed.com/)

### Best Buy — 2155 Cattail St, opens 10am, (406) 602-6059

| Item | Price | Notes |
|---|---|---|
| Wiz or Govee smart bulb | ~$18 | Backup plan. Buy it |

[Best Buy Bozeman store page](https://stores.bestbuy.com/mt/bozeman/2155-cattail-st-1264.html)

**Total: ~$185**

### Ask at the counter

1. "Does the Freenove kit have the LCD1602 in it?" — look in the box
2. "How many USB-A ports does the Hiearcool hub have?" — you need 2
3. "How many pushbuttons are in the kit?" — you want 6; 5 is common
4. "Does the kit include a breadboard, and how big?" — tells you if you need the Chanzon

### Do NOT buy

Servos, LED strips, RC light kits, tactile buttons, resistors. The Freenove kit covers all of it.

**Confirmed absent from this store — don't waste time looking:** WS2812/addressable LED strips, Raspberry Pi Pico, OLED screens, loose pushbuttons, discrete resistors. The RC light kits are Traxxas closed systems and won't work.

---

## 2. What you're building, in plain English

You run four Claude Code sessions at once. The problem: you can't tell which one is waiting for you without checking each terminal.

This device tells you.

```
        ┌──────────────────────────────┐
        │   A2 BLOCKED 4:21            │   ← LCD, 2 rows of 16 characters
        │   1w 2B 3i 4d                │
        └──────────────────────────────┘
          🔴     🟢     🔵     🟡         ← 4 LEDs, one per agent
         [red] [grn]  [blu]  [ylw]        ← 4 buttons, matching caps

        [N64 controller]  A = approve, B = deny
```

### Reading the device

**Color = which agent. Blink = what state.**

The kit's LEDs are single-color, so a red LED is always red. Color is permanent identity, not status. Status is carried by the blink pattern, and every LED speaks the same language:

| LED behavior | State |
|---|---|
| Off | No session |
| Slow heartbeat | Idle |
| Solid on | Working |
| **Fast blink** | **Blocked — needs you** |
| Solid ~2s then heartbeat | Just finished |

So a **blinking green LED means agent 3 is blocked** — not "green is good."

**The LCD's two rows:**

```
A2 BLOCKED 4:21     ← the agent you have focused, and how long it's been in that state
1w 2B 3i 4d         ← all four at a glance
```

Bottom-row letters: `-` none · `i` idle · `w` working · **`B` blocked** · `d` done.
Uppercase B is deliberate — it's the only tall character, so it catches your eye without being read.

---

## 3. How the pieces connect

Three things are running, all on your Mac:

1. **Claude Code sessions** — four of them, inside tmux
2. **The ESP32** — a $10 chip that drives the LEDs and LCD and reads the buttons
3. **A Python program** — the brain connecting everything

```
  ┌─────────────────────────────────────────┐
  │  macOS                                  │
  │                                         │
  │  tmux                  Python daemon    │
  │   ├─ agent 1  ──hooks──►  reads         │
  │   ├─ agent 2            events.jsonl    │
  │   ├─ agent 3                            │
  │   └─ agent 4  ◄─send-keys─┤             │
  │                           ├─ USB ↔ ESP32│
  │                           └─ USB ← N64  │
  └─────────────────────────────────────────┘
```

**Hooks** are Claude Code's way of running a command when something happens — a session starts, a prompt is submitted, Claude needs permission. You'll write one tiny script and point five hooks at it.

Each hook appends a line to the events file. The daemon watches that file, updates the lights, and when you press a button it uses `tmux send-keys` to type into the right session.

**None of this needs a network.** Only Claude Code itself needs internet to reach the API — a phone hotspot is plenty.

---

## 4. Before you go to the store

Do this tonight. It's the slowest part and it wants decent wifi.

### Homebrew and tmux

macOS doesn't ship tmux. Install [Homebrew](https://brew.sh) if you don't have it, then:

```
brew install tmux
```

Verify: `tmux new -d -s test && tmux ls && tmux kill-session -t test`

### Arduino IDE

Download from https://www.arduino.cc/en/software

On first launch macOS may block it — System Settings → Privacy & Security → "Open Anyway".

Then add ESP32 support:

1. Arduino IDE → Settings → **Additional Boards Manager URLs**, paste:
   `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`
2. Tools → Board → Boards Manager → search "esp32" → install **esp32 by Espressif**
3. Tools → Manage Libraries → search "LiquidCrystal I2C" → install the one by **Frank de Brabander**

The board package is a few hundred MB. Do it on home wifi.

### Python

```
pip3 install pyserial pygame
```

If `pip3` isn't found, install Python from https://www.python.org/downloads/

### USB driver — wait, don't install it yet

macOS often already handles the CP2102 chip. **Try without a driver first** (see §5). Only if the port doesn't appear, download the **Mac OSX** CP210x VCP driver from https://www.silabs.com/software-and-tools/usb-to-uart-bridge-vcp-drivers — pick Apple Silicon or Intel to match your Mac, mount the `.dmg`, run "Install CP210x VCP Driver.app", then approve it in **System Settings → Privacy & Security**. That approval step is mandatory and easy to miss.

---

## 5. Milestone 1 — Make the ESP32 blink

Do this before wiring anything. It proves the board, cable, and port all work.

**1. Check what serial ports exist before plugging anything in:**

```
ls /dev/cu.*
```

**2. Plug in the ESP32** with the USB-C data cable, wait a few seconds, run it again:

```
ls /dev/cu.*
```

A new entry should appear — `/dev/cu.usbserial-0001`, `/dev/cu.SLAB_USBtoUART`, or similar.

**Write that name down.** It goes in `PORT = "..."` in both Python scripts later.

> **Always use `/dev/cu.*`, never `/dev/tty.*`.** Both appear for the same device. Python hangs forever on `tty.` waiting for a carrier signal the ESP32 never sends. This wastes an hour if you hit it blind.

**3. Upload a blink sketch:**

- Arduino IDE → Tools → Board → esp32 → **ESP32 Dev Module**
- Tools → Port → your `/dev/cu.` port
- File → Examples → 01.Basics → Blink
- Click the arrow (Upload)

The small blue LED on the board should blink.

**If no new port appears:** try a different cable first — charge-only USB-C cables are extremely common and look identical to data cables. If a known-good cable also fails, install the Mac VCP driver from §4.

**If upload fails with "Failed to connect":** hold the BOOT button on the board while it says "Connecting...", release when it starts uploading.

---

## 6. Milestone 2 — Wire the LCD

**Unplug the ESP32 from USB before wiring anything.**

### The ESP32 does not go on the breadboard

This 30-pin board is about an inch wide. Pushed into a breadboard it covers the center channel and leaves no usable holes on either side. **A bigger breadboard does not fix this** — every breadboard ever made has the same 0.3" channel and 5 holes per row. Bigger ones only add more columns.

So: **the ESP32 sits beside the breadboard, not in it.**

```
   ┌──────────┐        ┌─────────────────────┐
   │  ESP32   │════════│   breadboard        │
   │          │ F-M    │  LEDs, resistors,   │
   │          │ jumpers│  buttons            │
   └──────────┘        └─────────────────────┘
```

Female-to-male jumper wires do the work: the **female** end pushes onto an ESP32 pin, the **male** end goes into a breadboard hole. Every "connect GPIO X to Y" instruction below means one of these wires.

Use the 30cm jumpers, not the 10cm ones — the slack lets you pick the ESP32 up and look at it while debugging instead of fighting a taut bundle.

### Wiring the LCD

The Freenove tutorial confirms this is the **I²C** version (their Chapter 20 is "Project I2C LCD1602"), so the module on the back should have exactly **4 pins: GND, VCC, SDA, SCL**. Glance at it to confirm — if you somehow see a bare row of ~16 pins instead, stop, because that variant needs 6+ wires and a contrast potentiometer.

The 4 pins are male, and the ESP32's pins are male too, so use the kit's **F-F jumpers** to connect them directly. The LCD never touches the breadboard.

| LCD pin | ESP32 pin |
|---|---|
| GND | GND |
| VCC | VIN (also labeled 5V) |
| SDA | GPIO 21 |
| SCL | GPIO 22 |

The ESP32 has tiny labels printed next to each pin. Look for `21`, `22`, `GND`, `VIN`.

> **Watch your F-M budget.** The kit has only 10 female-to-male jumpers and they're the only ones that reach the ESP32. Allocation: 4 for LED signals, 4 for button signals, 1 for GND to the negative rail — 9 of 10, with one spare. Going LCD-to-ESP32 with F-F is what makes this fit. The 30cm Edgelec pack is your insurance.

Plug in USB, then upload this:

```cpp
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);

void setup() {
  Wire.begin(21, 22);
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("agentpad ready");
}

void loop() {}
```

**If the backlight is on but there's no text:** turn the small blue screw on the back of the LCD board (that's the contrast dial) with a small screwdriver until text appears. Half the "broken" LCDs are just contrast.

**If nothing happens at all:** change `0x27` to `0x3F` and re-upload. Those are the two common addresses.

---

## 7. Milestone 3 — Wire the LEDs

**Unplug USB first.** Get four LEDs and four 220Ω resistors from the kit (red-red-brown-gold stripes).

An LED has one long leg (+, called the anode) and one short leg (−, cathode). **Backwards LEDs simply don't light — they aren't damaged, so don't panic.**

For each of the four:

1. Long leg → a row on the breadboard
2. Short leg → a different row
3. Resistor from the short leg's row → the breadboard's negative rail (the line marked `−`)
4. Jumper from the long leg's row → the ESP32 GPIO pin below

| Agent | LED color | ESP32 pin |
|---|---|---|
| 1 | Red | GPIO 13 |
| 2 | Green | GPIO 14 |
| 3 | Blue | GPIO 27 |
| 4 | Yellow | GPIO 26 |

Lay them out **left to right in this order**, matching the LCD's bottom row. Wiring them out of order means mentally translating during your demo.

Finally: one jumper from any ESP32 **GND** pin → the breadboard's negative rail. This is easy to forget and nothing works without it.

> **Pin warning:** GPIO 34–39 are input-only and cannot light an LED. GPIO 0, 2, 12, and 15 can stop the board from booting. The pins above avoid all of these. If you improvise, check against this list first.

Test with this:

```cpp
const int LED[4] = {13, 14, 27, 26};

void setup() {
  for (int i = 0; i < 4; i++) pinMode(LED[i], OUTPUT);
}

void loop() {
  for (int i = 0; i < 4; i++) {
    digitalWrite(LED[i], HIGH);
    delay(300);
    digitalWrite(LED[i], LOW);
  }
}
```

They should light one at a time, in order.

---

## 8. Milestone 4 — Wire the buttons

**Unplug USB.** Use the four **Big Push Buttons** and snap on the colored caps — red, green, blue, yellow. Put each button directly below the LED of the same color.

The buttons have 4 legs but are really 2 pairs. Straddle the breadboard's center channel with them — this guarantees you're using legs from opposite pairs.

For each button:
- One leg → the ESP32 pin below
- Leg on the **opposite side** → the negative rail

**No resistors needed.** The ESP32 has resistors built in that the code switches on.

| Agent | Cap color | ESP32 pin |
|---|---|---|
| 1 | Red | GPIO 32 |
| 2 | Green | GPIO 33 |
| 3 | Blue | GPIO 25 |
| 4 | Yellow | GPIO 4 |

Test:

```cpp
const int BTN[4] = {32, 33, 25, 4};

void setup() {
  Serial.begin(115200);
  for (int i = 0; i < 4; i++) pinMode(BTN[i], INPUT_PULLUP);
}

void loop() {
  for (int i = 0; i < 4; i++) {
    if (digitalRead(BTN[i]) == LOW) {
      Serial.print("button ");
      Serial.println(i);
      delay(200);
    }
  }
}
```

Open Tools → Serial Monitor, set the dropdown to **115200 baud**, and press buttons. You should see `button 0` through `button 3`.

If a button fires constantly without being touched, its second leg isn't reaching the negative rail.

---

## 9. Milestone 5 — The real firmware

This replaces everything above. Upload it once and you're done with Arduino.

The sketch lives at `firmware/agentpad/agentpad.ino` in this repo. It has been verified to compile for the ESP32 target (`arduino-cli compile --fqbn esp32:esp32:esp32 firmware/agentpad`), so any upload failure is a board/cable/port issue, not a code issue.

**Test it from the Serial Monitor** before writing any Python. Set the line-ending dropdown to "Newline", then type:

- `L 0 working` → LED 1 goes solid
- `L 1 blocked` → LED 2 blinks fast
- `D0 hello there` → top LCD row changes
- Press a button → `B 0` appears

If all of that works, your hardware is finished. Everything from here is software.

---

## 10. Milestone 6 — Python talks to the board

The events file and Python scripts live in this repo (`~/projects/agentpad`). Create `test.py`:

```python
import serial, time

PORT = "/dev/cu.usbserial-0001"   # <-- your port from Milestone 1

ser = serial.Serial(PORT, 115200, timeout=0.1)
time.sleep(2)          # the ESP32 reboots when the port opens

ser.write(b"D0 hello from python\n")
ser.write(b"L 0 blocked\n")

while True:
    line = ser.readline().decode(errors="ignore").strip()
    if line:
        print(line)
```

Run it: `python3 test.py` (inside the mise venv)

The LCD updates, LED 1 blinks, and pressing buttons prints `B 0` in your terminal. Ctrl+C to quit.

> **Only one program can hold the serial port.** Close the Arduino Serial Monitor before running Python, or you'll get "Resource busy."

---

## 11. Milestone 7 — Claude Code hooks

Create the reporting script:

```bash
mkdir -p ~/.claude
cat > ~/.claude/agentpad.sh << 'EOF'
#!/usr/bin/env bash
printf '{"pane":"%s","state":"%s"}\n' "$TMUX_PANE" "$1" >> "$HOME/projects/agentpad/events.jsonl"
EOF
chmod +x ~/.claude/agentpad.sh
```

Then add to `~/.claude/settings.json`:

```json
{
  "hooks": {
    "SessionStart":     [{"hooks": [{"type": "command", "command": "~/.claude/agentpad.sh idle"}]}],
    "UserPromptSubmit": [{"hooks": [{"type": "command", "command": "~/.claude/agentpad.sh working"}]}],
    "Notification":     [{"hooks": [{"type": "command", "command": "~/.claude/agentpad.sh blocked"}]}],
    "Stop":             [{"hooks": [{"type": "command", "command": "~/.claude/agentpad.sh done"}]}],
    "SessionEnd":       [{"hooks": [{"type": "command", "command": "~/.claude/agentpad.sh none"}]}]
  }
}
```

**Test it:** start tmux (`tmux new -s agents`), run `claude`, ask it anything. Then in another terminal:

```
cat ~/projects/agentpad/events.jsonl
```

You should see JSON lines with a `pane` value like `%0`. **If `pane` is empty, Claude Code isn't running inside tmux** — that's the whole mechanism, so fix it before continuing.

---

## 12. Milestone 8 — The controller

Plug it into the hub. macOS needs no driver. Create `pad.py`:

```python
import pygame

pygame.init()
pygame.joystick.init()
js = pygame.joystick.Joystick(0)
js.init()
print("pad:", js.get_name())

while True:
    for e in pygame.event.get():
        if e.type == pygame.JOYBUTTONDOWN:
            print("button", e.button)
        elif e.type == pygame.JOYHATMOTION:
            print("hat", e.value)
        elif e.type == pygame.JOYAXISMOTION and abs(e.value) > 0.5:
            print("axis", e.axis, round(e.value, 2))
```

Run it and press every button. **Write down which number each one reports** — A, B, Start, Z, and the d-pad. Cheap adapters number them unpredictably, so never assume; always check. The d-pad usually shows up as `hat` values like `(0, 1)` rather than buttons.

pygame may open a small blank window. That's normal — it needs it to receive events. Leave it open.

---

## 13. Milestone 9 — The daemon

Create `daemon.py`. Edit the CONFIG block with your port and your button numbers from Milestone 8.

```python
import json, os, time, subprocess, threading
import serial, pygame

# ===== CONFIG =====
PORT      = "/dev/cu.usbserial-0001"
BTN_A     = 0       # from pad.py
BTN_B     = 1
BTN_START = 9
APPROVE   = "1"     # what to type at a permission prompt
DENY      = "3"
EVENTS    = os.path.expanduser("~/projects/agentpad/events.jsonl")
# ==================

ser = serial.Serial(PORT, 115200, timeout=0.1)
time.sleep(2)

slots = [None] * 4          # slot index -> tmux pane id
info  = {}                  # pane id -> {"state":..., "since":...}
focus = 0

def send(line):
    ser.write((line + "\n").encode())

def slot_of(pane):
    if pane in slots:
        return slots.index(pane)
    for i in range(4):
        if slots[i] is None:
            slots[i] = pane
            return i
    return None

def state_of(i):
    p = slots[i]
    return info[p]["state"] if p and p in info else "none"

def refresh():
    letters = {"none": "-", "idle": "i", "working": "w", "blocked": "B", "done": "d"}
    p = slots[focus]
    if p and p in info:
        secs = int(time.time() - info[p]["since"])
        row0 = f"A{focus+1} {info[p]['state'].upper()[:7]} {secs//60}:{secs%60:02d}"
    else:
        row0 = f"A{focus+1} --"
    row1 = " ".join(f"{i+1}{letters[state_of(i)]}" for i in range(4))
    send(f"D0 {row0[:16]}")
    send(f"D1 {row1[:16]}")

def set_focus(i):
    global focus
    focus = i
    p = slots[i]
    if p:
        subprocess.run(["tmux", "select-pane", "-t", p])
    refresh()

def type_into(pane, text):
    subprocess.run(["tmux", "send-keys", "-t", pane, text, "Enter"])

def respond(keystroke):
    p = slots[focus]
    if not p or info.get(p, {}).get("state") != "blocked":
        send("D0 not blocked")        # refuse - avoids typing junk
        time.sleep(0.6)
        refresh()
        return
    type_into(p, keystroke)

def next_blocked():
    for i in range(4):
        if state_of(i) == "blocked":
            set_focus(i)
            return
    send("D0 nothing blocked")
    time.sleep(0.6)
    refresh()

def tail_events():
    open(EVENTS, "a").close()
    with open(EVENTS, "r") as f:
        f.seek(0, 2)
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.1)
                continue
            try:
                e = json.loads(line)
            except Exception:
                continue
            pane = e.get("pane")
            if not pane:
                continue
            i = slot_of(pane)
            if i is None:
                continue
            st = e.get("state", "idle")
            info[pane] = {"state": st, "since": time.time()}
            send(f"L {i} {st}")
            refresh()

def read_serial():
    while True:
        line = ser.readline().decode(errors="ignore").strip()
        if line.startswith("B "):
            set_focus(int(line.split()[1]))

threading.Thread(target=tail_events, daemon=True).start()
threading.Thread(target=read_serial, daemon=True).start()

pygame.init()
pygame.joystick.init()
js = pygame.joystick.Joystick(0)
js.init()

refresh()
print("agentpad running. ctrl-c to quit.")

while True:
    for e in pygame.event.get():
        if e.type == pygame.JOYBUTTONDOWN:
            if   e.button == BTN_A:     respond(APPROVE)
            elif e.button == BTN_B:     respond(DENY)
            elif e.button == BTN_START: next_blocked()
        elif e.type == pygame.JOYHATMOTION:
            x, y = e.value
            if   y ==  1: set_focus(0)
            elif x ==  1: set_focus(1)
            elif y == -1: set_focus(2)
            elif x == -1: set_focus(3)
    time.sleep(0.02)
```

Run it: `python3 daemon.py` (inside the mise venv)

---

## 14. Running it for real

1. Charger → hub's USB-C PD port. Hub → your Mac.
2. **ESP32 → a USB-A port** (via the A-to-C cable). The breadboard gets its power from the ESP32, not from USB.
3. **Controller → the other USB-A port.**
4. `tmux new -s agents`, then split into 4 panes (`Ctrl-b %` and `Ctrl-b "`)
5. Run `claude` in each pane
6. In a separate terminal: `python3 daemon.py`

Give an agent a long task. Its LED goes solid. When it hits a permission prompt, the LED blinks fast and the LCD names it. Press Start to jump there, A to approve.

---

## 15. Troubleshooting

| Symptom | Fix |
|---|---|
| No new `/dev/cu.*` when plugged in | Try a different cable first (charge-only is common). Then install the Mac VCP driver |
| Driver installed but still nothing | System Settings → Privacy & Security → approve the Silicon Labs extension, then reboot |
| Python hangs forever on `serial.Serial()` | You used `/dev/tty.*`. Use `/dev/cu.*` |
| "Failed to connect" on upload | Hold BOOT button during "Connecting..." |
| "Resource busy" on the port | Close the Arduino Serial Monitor first |
| LCD backlit but blank | Turn the contrast screw on its back |
| LCD totally dead | Change `0x27` to `0x3F` |
| One LED never lights | It's backwards — flip it. Or check its pin isn't 34–39 |
| Buttons fire constantly | Second leg isn't reaching the negative rail |
| Everything dead after adding parts | Missing GND jumper from ESP32 to the negative rail |
| `pane` is empty in events file | Claude Code isn't running inside tmux |
| `tmux: command not found` | `brew install tmux` |
| Pressing A types nothing | The agent isn't in `blocked` state — that's the safety interlock working |
| A approves the wrong thing | Change `APPROVE` — permission menus are numbered, and numbering varies |
| Port name changes after replug | Pick a hub port and stay in it; re-check with `ls /dev/cu.*` |

---

## 16. Order of operations on the day

Do these in order. Each takes about five minutes and each one, if skipped, can cost you hours later.

1. `ls /dev/cu.*` shows a new port when the ESP32 is plugged in — **write it down**
2. Blink sketch uploads (Milestone 1)
3. LCD says hello (Milestone 2)
4. LEDs cycle (Milestone 3)
5. Buttons print to Serial Monitor (Milestone 4)
6. Real firmware; test by typing into Serial Monitor (Milestone 5)
7. Python drives the board (Milestone 6)
8. Hooks write to the events file with a real `pane` value (Milestone 7)
9. Map every controller button (Milestone 8)
10. Daemon (Milestone 9)

Don't skip ahead. The whole point of this order is that when something breaks, only one thing has changed.

---

## 17. If it all goes wrong

The Wiz/Govee bulb is the fallback. Wiz bulbs take local UDP JSON on port 38899 — no cloud, no account. Have your hooks turn the bulb amber on `blocked` and back to white on `done`. That's a complete, useful project in about twenty minutes, and it works with no ESP32, no wiring, and no controller.

A working simple thing beats a broken ambitious thing at a demo.

**Record a backup video** of the working device once you have it. Ten minutes of insurance against a demo-table failure.

---

## 18. Reference links

### Software

| | |
|---|---|
| Homebrew (for tmux) | https://brew.sh |
| Arduino IDE | https://www.arduino.cc/en/software |
| Python | https://www.python.org/downloads/ |
| CP210x Mac driver (**only if needed**) | https://www.silabs.com/software-and-tools/usb-to-uart-bridge-vcp-drivers |
| ESP32 board manager URL | `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json` |

### Reference

| | |
|---|---|
| Freenove FNK0020 kit tutorial (diagrams only — ignore the Pi code) | https://docs.freenove.com/projects/fnk0020/en/latest/ |
| Claude Code hooks documentation | https://code.claude.com/docs/en/hooks |
| Emberglow — prior art, keyboard RGB as Claude status | https://emberglow.dev/ |
| Claude-Macropad-V2 — prior art, open BOM and specs | https://github.com/danielrosehill/Claude-Macropad-V2 |
