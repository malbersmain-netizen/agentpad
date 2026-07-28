> **ARCHIVED — do not build from this.**
> This is the original breadboard-era milestone guide, written before the two-board
> soldered design. It is kept only for the hardware bring-up history. The current
> documents are `BUILD.md`, `SOLDERING.md` and `BREADBOARD.md`.

---

# Agent Pad — Complete Build Guide (macOS)

A physical control surface for Claude Code. Four LEDs show what four agents are doing and an LCD shows detail. Six buttons on the board do everything: four color buttons each launch a color-tinted tmux `claude` session (if it isn't running yet) and focus it, and two more buttons approve or deny that agent's permission prompt. No game controller — the device is self-contained.

Assumes zero electronics experience. Nothing is soldered.

---

## 1. Shopping list

### RadioShack of Bozeman — 2855 N 19th Ave, opens 9am, (406) 587-1613

| Item | Price | Notes |
|---|---|---|
| [Freenove Ultimate Starter Kit](https://radioshack-of-bozeman-640025.shoplightspeed.com/pi-4-acckit-freenove-ultimate-starter-kit-for-rasp.html) | $79.95 | **Being held for you. Only 1 in stock.** Contains LCD, LEDs, buttons, resistors, breadboard |
| [ESP32 dev board](https://radioshack-of-bozeman-640025.shoplightspeed.com/wifi-board-hiletgo-esp-wroom-32-esp32-esp-32s-deve.html) × 2 | $9.95 ea | **Only 2 in stock — buy both.** Headers confirmed pre-soldered |
| [Edgelec 30cm male-to-female jumpers](https://radioshack-of-bozeman-640025.shoplightspeed.com/electronics-parts/lights/led-strips/jumpers/) | ~$10 | **Required** — the ESP32 doesn't fit on a breadboard, and 6 buttons blow the kit's F-M budget. See §6 |
| [Hiearcool 7-in-1 USB-C hub](https://radioshack-of-bozeman-640025.shoplightspeed.com/cables-and-adapters/usb-cable-types/hubs/) | ~$40 | 100W PD passthrough lets you charge while building. You only need **1** USB-A port — the ESP32 is the only USB device |
| [USB-**A** to USB-**C** data cable](https://radioshack-of-bozeman-640025.shoplightspeed.com/cables-and-adapters/usb-cable-types/usb-type-c/usb-type-c-cables/) | ~$12 | **A-to-C, not C-to-C.** Hub USB-C ports are often power-only with no data lines. Also: not a charge-only cable |
| [Breadboard, Chanzon 400-point](https://radioshack-of-bozeman-640025.shoplightspeed.com/electronics-parts/diy/breadboards/) | ~$8 | Optional — the kit includes one |

**No soldering required.** The ESP32 ships with headers pre-attached and the LCD has its own. Skip the iron, solder, flux, and wick entirely.

**No game controller.** An earlier version of this build used an N64 USB controller for approve/deny. It's gone — approve and deny are now plain push buttons on the board. Don't buy one, and don't buy the NES backup either.

### What the Freenove kit supplies

Confirmed from the contents sheet — you need nothing else for the core build:

| Part | Qty | Used for |
|---|---|---|
| LCD Module | 1 | The display |
| Red / Green / Blue / Yellow LEDs | 10 / 4 / 4 / 4 | One per agent |
| Resistor-220 | 20 | Four, one per LED |
| Big Push Button + Red/Green/Blue/Yellow caps | 4 + 4 | Agent keys, color-matched to the LEDs |
| Push Button | 6 | **Two are load-bearing: APPROVE and DENY.** The other four are spares |
| Project Board (breadboard) | 1 | Everything else |
| 65 Jump Wire M-M | 65 | Breadboard-internal connections |
| 10 Jump Wire F-F | 10 | LCD directly to ESP32 |
| 10 Jump Wire F-M | 10 | ESP32 to breadboard — **not enough, see §6** |

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

**Total: ~$162** (was ~$185 before the controller was dropped)

### Ask at the counter

1. "Does the Freenove kit have the LCD1602 in it?" — look in the box
2. "How many USB-A ports does the Hiearcool hub have?" — 1 is enough; the ESP32 is the only USB device
3. "How many pushbuttons are in the kit?" — you need at least 2 plain ones plus the 4 big capped ones; the kit lists 6 plain
4. "Does the kit include a breadboard, and how big?" — tells you if you need the Chanzon

### Do NOT buy

Servos, LED strips, RC light kits, tactile buttons, resistors. The Freenove kit covers all of it.

**Confirmed absent from this store — don't waste time looking:** WS2812/addressable LED strips, Raspberry Pi Pico, OLED screens, loose pushbuttons, discrete resistors. The RC light kits are Traxxas closed systems and won't work.

---

## 2. What you're building, in plain English

You run four Claude Code sessions at once. The problem: you can't tell which one is waiting for you without checking each terminal.

This device tells you — and lets you answer without touching the keyboard.

```
        ┌──────────────────────────────┐
        │   A2 BLOCKED 4:21            │   ← LCD, 2 rows of 16 characters
        │   1w 2B 3i 4d                │
        └──────────────────────────────┘
          🔴     🟢     🔵     🟡         ← 4 LEDs, one per agent
         [red] [grn]  [blu]  [ylw]        ← 4 color buttons, matching caps

            [APPROVE]   [DENY]            ← 2 plain buttons, GPIO 19 / 18
```

A **color button** launches that agent's tmux window running `claude` (or focuses it if it's already running). **APPROVE** and **DENY** answer the permission prompt of whichever agent's window is on screen — and only when it really is blocked. If it isn't, the LCD flashes `not blocked` and nothing is typed.

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

1. **Claude Code sessions** — up to four, in one tmux session named `agentpad`
2. **The ESP32** — a $10 chip that drives the LEDs and LCD and reads the six buttons
3. **A Python program** — the brain connecting everything

```
  ┌─────────────────────────────────────────────────┐
  │   macOS                                         │
  │                                                 │
  │   tmux session "agentpad"        Python daemon  │
  │    ├─ A1-red  ──hooks──►     reads events.jsonl │
  │    ├─ A2-grn                                  │ │
  │    ├─ A3-blu  ◄─new-window / select-window────┤ │
  │    └─ A4-ylw  ◄─send-keys─────────────────────┤ │
  │                                               │ │
  │                              USB ↔ ESP32 ─────┘ │
  └─────────────────────────────────────────────────┘
```

Only one USB device is involved: the ESP32.

**Hooks** are Claude Code's way of running a command when something happens — a session starts, a prompt is submitted, Claude asks permission. You'll write one tiny script and point five hooks at it.

Each hook appends a line to the events file. The daemon watches that file, updates the lights, and when you press a button it uses `tmux new-window` / `select-window` to launch or focus an agent, or `tmux send-keys` to answer its prompt.

> **`blocked` comes from the `PermissionRequest` hook, not `Notification`.** This was measured on this build: `Notification` fires **6.00 seconds after** the prompt renders — it exists to chase a user who walked away, not to report a prompt. `PermissionRequest` fires at +0.00s and covers every prompt type. Using `Notification` makes the pad feel broken. Do not switch it back.

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

Don't `pip3 install` into system Python. This project uses a **project-local venv managed by [mise](https://mise.jdx.dev)** on Python 3.13, pinned by `mise.toml`:

```toml
[tools]
python = "3.13"

[env]
_.python.venv = { path = ".venv", create = true }
```

```
brew install mise
cd ~/projects/agentpad
mise install
mise exec -- pip install pyserial
```

`pyserial` is the only dependency. (Earlier drafts also installed `pygame` for the game controller — no longer needed.)

Anything you run from inside `~/projects/agentpad` picks up `.venv` automatically; from elsewhere, prefix with `mise exec --`.

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

> **Watch your F-M budget — the kit is one short.** The kit has only 10 female-to-male jumpers and they're the only ones that reach the ESP32. With six buttons the allocation is: 4 LED signals + 6 button signals + 1 GND to the negative rail = **11 wires, and you have 10.** So the 30cm Edgelec pack isn't insurance any more, it's required. Going LCD-to-ESP32 with F-F jumpers is still what keeps the number this low.

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

**Unplug USB.** There are **six** buttons: the four **Big Push Buttons** with the colored caps snapped on — red, green, blue, yellow — each directly below the LED of the same color, plus **two plain push buttons** off to the side for APPROVE and DENY.

The buttons have 4 legs but are really 2 pairs. Straddle the breadboard's center channel with them — this guarantees you're using legs from opposite pairs.

For each of the six, wiring is identical:
- One leg → the ESP32 pin below, via an F-M jumper
- The **diagonally opposite** leg → the blue negative rail, via an M-M jumper

**No resistors needed**, on any of them. The ESP32 has pull-up resistors built in that the code switches on.

| Button | Cap / label | ESP32 pin |
|---|---|---|
| Agent 1 | Red | GPIO 32 |
| Agent 2 | Green | GPIO 33 |
| Agent 3 | Blue | GPIO 25 |
| Agent 4 | Yellow | GPIO 4 |
| **APPROVE** | plain | **GPIO 19** |
| **DENY** | plain | **GPIO 18** |

Put APPROVE and DENY somewhere you won't confuse them under demo pressure — separated from the color row, and always in the same left-to-right order. Label them with tape.

Test:

```cpp
const int BTN[6] = {32, 33, 25, 4, 19, 18};   // 0-3 select, 4 approve, 5 deny

void setup() {
  Serial.begin(115200);
  for (int i = 0; i < 6; i++) pinMode(BTN[i], INPUT_PULLUP);
}

void loop() {
  for (int i = 0; i < 6; i++) {
    if (digitalRead(BTN[i]) == LOW) {
      Serial.print("button ");
      Serial.println(i);
      delay(200);
    }
  }
}
```

Open Tools → Serial Monitor, set the dropdown to **115200 baud**, and press buttons. You should see `button 0` through `button 5`.

If a button fires constantly without being touched, its second leg isn't reaching the negative rail.

---

## 9. Milestone 5 — The real firmware

This replaces everything above. Upload it once and you're done with Arduino.

The sketch lives at `firmware/agentpad/agentpad.ino` in this repo. It has been verified to compile for the ESP32 target (`arduino-cli compile --fqbn esp32:esp32:esp32 firmware/agentpad`), so any upload failure is a board/cable/port issue, not a code issue.

**Test it from the Serial Monitor** before writing any Python. Set the line-ending dropdown to "Newline", then type:

- `L 0 working` → LED 1 goes solid
- `L 1 blocked` → LED 2 blinks fast
- `D0 hello there` → top LCD row changes
- Press each of the six buttons → `B 0` through `B 5` appear. **Check 4 and 5 specifically** — they're APPROVE and DENY, they have no LED to confirm them, and a mis-wired one is invisible until the live demo

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

Run it: `cd ~/projects/agentpad && mise exec -- python test.py`

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
    "PermissionRequest":[{"hooks": [{"type": "command", "command": "~/.claude/agentpad.sh blocked"}]}],
    "Stop":             [{"hooks": [{"type": "command", "command": "~/.claude/agentpad.sh done"}]}],
    "SessionEnd":       [{"hooks": [{"type": "command", "command": "~/.claude/agentpad.sh none"}]}]
  }
}
```

`PermissionRequest` is what makes `blocked` usable — see the warning in §3. Don't substitute `Notification`.

**Test it:** start tmux (`tmux new -s test`), run `claude`, ask it anything. Then in another terminal:

```
cat ~/projects/agentpad/events.jsonl
```

You should see JSON lines with a `pane` value like `%0`. **If `pane` is empty, Claude Code isn't running inside tmux** — that's the whole mechanism, so fix it before continuing.

To see a `blocked` line you need a command that actually asks permission. **Local read-only commands don't prompt** — `date`, `df -h`, `ls` and friends are auto-allowed inside the sandbox and produce no `PermissionRequest`. Ask for something that escapes the sandbox instead; `curl -sI https://example.com` prompts reliably and is the one to use when demoing or testing.

---

## 12. Milestone 8 — The controller (dropped)

There is no controller any more. Approve and deny are the two plain buttons you wired in Milestone 4, so the whole build is self-contained on the board — one USB cable, nothing else to plug in, nothing to configure per-controller.

The controller code (`pad.py`) has been deleted, and `pygame` is no longer a dependency. Skip this milestone entirely — it survives only as a numbering placeholder so the later milestones keep the numbers used elsewhere in this guide.

---

## 13. Milestone 9 — The daemon

The daemon is `daemon.py` in this repo. Read it there rather than retyping it — it's the one file that changes most. The only thing you should normally edit is the CONFIG block at the top: `PORT` (your port from Milestone 1), `SESSION`, and `APPROVE` / `DENY` (the keystrokes typed at a permission prompt — menu numbering varies, so these get tuned live).

What it does:

- **Owns the tmux session.** On startup it creates a session named `agentpad` with a placeholder `home` window, so you can attach before any agent exists.
- **Color button (`B 0`–`B 3`) → launch or focus.** If that agent's window isn't running it spawns one (`tmux new-window` running `claude`, named `A1-red` … `A4-ylw`) and tints the whole window a dark color matching the LED. If it already exists, it just selects it. You never create panes or start `claude` by hand.
- **Approve (`B 4`) / Deny (`B 5`) → answer the prompt** of whichever agent window is *on screen*, via `tmux send-keys`. It follows tmux, so switching windows by hand works too.
- **The interlock.** Before typing anything, two independent conditions must agree: the hook says that agent is `blocked`, **and** a selection prompt is actually rendered on that pane right now (checked with `tmux capture-pane`). Either one alone can be stale. If they don't agree, it flashes `not blocked` on the LCD and types nothing. Keep this.
- **Reads `events.jsonl`** and maps each hook's `$TMUX_PANE` to an agent slot — but only panes it launched itself, so other Claude sessions on the machine can't claim a slot or receive keystrokes. Each event pushes `L <i> <state>` to the board.
- **Clears `blocked` itself** when the prompt leaves the screen (answered from the keyboard or from the pad). Setting `blocked` is the `PermissionRequest` hook's job; clearing it is the daemon's.
- **Redraws the LCD once a second** so the state timer counts live.
- **Survives restarts.** It blanks all four LEDs on startup (the ESP32 holds its last LED state across daemon restarts), re-binds existing agent windows to their color slots by window name, and replays the event log to restore states — deliberately never restoring `blocked`, since a prompt from a previous run is long gone.
- **Supervises its own worker threads**, restarting any that crash, so one exception can't silently half-kill it.

Run it:

```
cd ~/projects/agentpad && mise exec -- python daemon.py
```

It prints `agentpad running. ctrl-c to quit.` and logs to `daemon.log` — check that file first when a button seems to do nothing.

---

## 14. Running it for real

1. Charger → hub's USB-C PD port. Hub → your Mac.
2. **ESP32 → the USB-A port** (via the A-to-C cable). That's the only USB device. The breadboard gets its power from the ESP32, not from USB.
3. Start the daemon in its own terminal:
   ```
   cd ~/projects/agentpad && mise exec -- python daemon.py
   ```
4. In another terminal, attach so you can watch: `tmux attach -t agentpad`
5. **Press a color button.** That agent's window appears, tinted, already running `claude`, and focused. Press another color button for a second agent. Press a color button again any time to jump back to that agent.

Give an agent a long task. Its LED goes solid. When it hits a permission prompt, the LED blinks fast and the LCD names the agent and how long it's been waiting. Press **APPROVE** or **DENY**.

For demoing, ask for something that actually needs permission — `curl -sI https://example.com` prompts reliably. `date` and `df -h` do not: local read-only commands are auto-allowed and never produce a prompt to approve.

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
| LCD flashes `not blocked` and nothing is typed | The interlock refused. Either that agent has no live prompt on screen, or the window you're looking at isn't an agent window. Check `daemon.log` — it records the state and the on-screen check for every refusal |
| LCD flashes `no agent focused` | tmux is on the `home` window (or something you opened yourself). Press a color button first |
| Approve hits the wrong menu item | Change `APPROVE` / `DENY` in the daemon's CONFIG block — permission menus are numbered, and numbering varies |
| LEDs show stale states right after starting the daemon | Shouldn't happen — the daemon blanks all four LEDs on startup because the ESP32 keeps its last LED state. If it does, the board isn't receiving serial: check the port and that nothing else holds it |
| No prompt ever appears, so there's nothing to approve | You're asking for something the sandbox auto-allows. `date`, `df -h`, `ls` never prompt. Use a command that escapes the sandbox — `curl -sI https://example.com` |
| Port name changes after replug | Pick a hub port and stay in it; re-check with `ls /dev/cu.*` |

---

## 16. Order of operations on the day

Do these in order. Each takes about five minutes and each one, if skipped, can cost you hours later.

1. `ls /dev/cu.*` shows a new port when the ESP32 is plugged in — **write it down**
2. Blink sketch uploads (Milestone 1)
3. LCD says hello (Milestone 2)
4. LEDs cycle (Milestone 3)
5. Wire the four color buttons; they print to Serial Monitor (Milestone 4)
6. Wire APPROVE (GPIO 19) and DENY (GPIO 18); confirm `button 4` and `button 5` (Milestone 4)
7. Real firmware; test all six buttons by typing into Serial Monitor (Milestone 5)
8. Python drives the board (Milestone 6)
9. Hooks write to the events file with a real `pane` value (Milestone 7)
10. Daemon: press a color button, an agent window appears; approve a real `curl` prompt (Milestone 9)

Don't skip ahead. The whole point of this order is that when something breaks, only one thing has changed.

---

## 17. If it all goes wrong

The Wiz/Govee bulb is the fallback. Wiz bulbs take local UDP JSON on port 38899 — no cloud, no account. Have your hooks turn the bulb amber on `blocked` and back to white on `done`. That's a complete, useful project in about twenty minutes, and it works with no ESP32 and no wiring at all.

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
| mise (project-local Python 3.13 venv) | https://mise.jdx.dev |
| CP210x Mac driver (**only if needed**) | https://www.silabs.com/software-and-tools/usb-to-uart-bridge-vcp-drivers |
| ESP32 board manager URL | `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json` |

### Reference

| | |
|---|---|
| Freenove FNK0020 kit tutorial (diagrams only — ignore the Pi code) | https://docs.freenove.com/projects/fnk0020/en/latest/ |
| Claude Code hooks documentation | https://code.claude.com/docs/en/hooks |
| Emberglow — prior art, keyboard RGB as Claude status | https://emberglow.dev/ |
| Claude-Macropad-V2 — prior art, open BOM and specs | https://github.com/danielrosehill/Claude-Macropad-V2 |
