# Agent Pad

Physical control surface for Claude Code — a self-contained "code micro" clone. Four LEDs + an LCD show what four agents are doing. Six buttons on the board do everything: the four color buttons each **launch a color-tinted tmux `claude` session (if not running) and focus it**; two more buttons **approve / deny** the focused agent's permission prompt. No external game controller (deferred; `pad.py` kept for a possible later add-on).

Full build guide: `agentpad-build-guide.md` in this directory. Read it before proposing changes.

## Platform

- **macOS.** No WSL, no Windows paths.
- ESP32 (ESP-WROOM-32, CP2102, 30-pin) over USB serial at 115200
- Agents run in tmux panes; daemon runs natively; both on the same machine
- **Python via mise: project-local venv on Python 3.13** (see `mise.toml`). Run all Python from inside this dir so mise activates `.venv`.
- Python deps: `pyserial` (the daemon no longer needs `pygame` — controller deferred; `pygame` stays installed only for the optional `pad.py`).

## Architecture

```
Claude Code hooks → events.jsonl → daemon → serial → ESP32 (LEDs, LCD)
                                    daemon ← serial ← ESP32 (6 buttons)
                                    daemon → tmux new-window/select-window/send-keys
```

The daemon *launches* each agent's tmux window (running `claude`) on the first color-button press and records that window's pane id, so it maps pane → agent slot directly. Hook events (`$TMUX_PANE` + state) then light the matching LED. Approve/Deny buttons send keystrokes to the focused agent, gated by the `blocked` interlock.

The four agent windows live in one tmux session named `agentpad`, each tinted a dark color (`window-style bg=…`) matching its LED/button. Attach with `tmux attach -t agentpad`.

## Files

| Path | What |
|---|---|
| `~/projects/agentpad/daemon.py` | The brain: serial ↔ tmux ↔ LEDs/LCD. Launches/focuses agents, approve/deny. |
| `~/projects/agentpad/pad.py` | Optional/deferred: game-controller button discovery (not used by the daemon) |
| `~/projects/agentpad/test.py` | Serial smoke test |
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
B <0-5>     # 0-3 = select/launch agent, 4 = approve, 5 = deny
```

Do not replace this with a binary or JSON protocol.

## Pin map — do not change without asking

| Function | GPIO |
|---|---|
| LEDs (red, green, blue, yellow = agents 1-4) | 13, 14, 27, 26 |
| Agent-select buttons (same color order) | 32, 33, 25, 4 |
| Approve button | 19 |
| Deny button | 18 |
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

Serial port name is measured on real hardware, not guessed (this build: `/dev/cu.usbserial-0001`).

Firmware *compilation* can be verified without hardware via `arduino-cli compile --fqbn esp32:esp32:esp32 firmware/agentpad`. Uploading is done here with `arduino-cli upload -p <port> --fqbn esp32:esp32:esp32 firmware/agentpad`.

## Status

Hardware fully built + verified (LCD@0x27, 4 LEDs, 4 select buttons). Real 6-button firmware written/compiled. Approve(19)/Deny(18) buttons: being wired. Daemon rewritten for the self-contained design (launch/focus + approve/deny, no pygame). Next: wire the 2 buttons, then end-to-end test (attach `agentpad` session, run daemon, press buttons).
