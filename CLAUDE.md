# Agent Pad

Physical control surface for Claude Code. Four LEDs + an LCD show what four agents are doing; four buttons and a USB game controller (N64, NES as backup) select an agent and approve/deny its permission prompts.

Full build guide: `agentpad-build-guide.md` in this directory. Read it before proposing changes.

## Platform

- **macOS.** No WSL, no Windows paths.
- ESP32 (ESP-WROOM-32, CP2102, 30-pin) over USB serial at 115200
- Agents run in tmux panes; daemon runs natively; both on the same machine
- **Python via mise: project-local venv on Python 3.13** (see `mise.toml`). The global mise Python is 3.14, where `pygame` wheels may not exist yet — the venv pins 3.13 to avoid that. Run all Python from inside this dir so mise activates `.venv`.
- Python deps: `pyserial`, `pygame`

## Architecture

```
Claude Code hooks → events.jsonl → daemon → serial → ESP32 (LEDs, LCD)
                                    daemon ← serial ← ESP32 (buttons)
                                    daemon ← pygame ← game pad
                                    daemon → tmux send-keys / select-pane
```

Agent identity comes from `$TMUX_PANE`, which the hook script inherits. The daemon maps pane id → slot 0-3.

## Files

| Path | What |
|---|---|
| `~/projects/agentpad/daemon.py` | The brain (not yet written — see Build order) |
| `~/projects/agentpad/pad.py` | Controller button discovery (not yet written) |
| `~/projects/agentpad/test.py` | Serial smoke test (not yet written) |
| `~/projects/agentpad/events.jsonl` | Runtime event stream; gitignored |
| `~/.claude/agentpad.sh` | Hook script, appends one JSON line to events.jsonl |
| `~/.claude/settings.json` | Five hooks pointing at that script |
| `firmware/agentpad/agentpad.ino` | Arduino sketch (staged; upload from Arduino IDE). Folder name matches the `.ino` so `arduino-cli` can build it. |

**Path note:** the code repo lives at `~/projects/agentpad`, not `~/agentpad`. The events file and all Python live here too; the hook script writes to `~/projects/agentpad/events.jsonl`. If you copy commands from an older draft that used `~/agentpad`, fix the path.

## Serial protocol

Line-based, human-readable on purpose — it must stay testable by typing into the Arduino Serial Monitor.

**Mac → ESP32**
```
L <0-3> <none|idle|working|blocked|done>
D0 <up to 16 chars>
D1 <up to 16 chars>
```

**ESP32 → Mac**
```
B <0-3>
```

Do not replace this with a binary or JSON protocol.

## Pin map — do not change without asking

| Function | GPIO |
|---|---|
| LEDs (red, green, blue, yellow = agents 1-4) | 13, 14, 27, 26 |
| Buttons (same color order) | 32, 33, 25, 4 |
| LCD I²C SDA / SCL | 21, 22 |

GPIO 34-39 are input-only with no internal pull-up. GPIO 0, 2, 12, 15 are boot strapping pins. Avoid all of them.

## Constraints

- **Serial only.** Do not convert the ESP32 to WiFi/HTTP. The venue network is not trusted and serial is debuggable from the Serial Monitor.
- **`/dev/cu.*` never `/dev/tty.*`** — pyserial hangs forever on tty.
- **Keep the approve/deny interlock.** The daemon must refuse to send keystrokes unless that agent's state is `blocked`. This prevents injecting junk into a prompt box.
- **`APPROVE` and `DENY` stay top-level config constants.** Permission menu numbering varies; these get tuned live.
- **Debounce lives in firmware**, not Python. 50ms.
- LEDs are single-color. Color = agent identity. Blink pattern = state.

## What you cannot verify

You cannot see the hardware. You cannot confirm an LED lit, the LCD shows text, or a button registered. When a step depends on physical observation, say so and wait for the human to report back rather than assuming success.

Serial port name and controller button numbers are unknown until measured on real hardware. Do not guess them — ask.

Firmware *compilation* can be verified without hardware via `arduino-cli compile --fqbn esp32:esp32:esp32 firmware/agentpad` (verified building clean, 22% flash).

## Build order

Hardware milestones (1-5 in the guide) come first and are human-only. Software starts at milestone 6. Do not write the daemon before the firmware is confirmed working from the Serial Monitor.
