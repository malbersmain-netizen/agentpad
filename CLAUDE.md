# Agent Pad

Physical control surface for Claude Code — a self-contained "code micro" clone. Four LEDs + an LCD show what four agents are doing. Six buttons on the board do everything: the four color buttons each **launch a color-tinted tmux `claude` session (if not running) and focus it**; two more buttons **approve / deny** the on-screen agent's permission prompt. **Single device — there is no game controller.** Don't reintroduce one.

Full build guide: `agentpad-build-guide.md` in this directory. Read it before proposing changes.

## Platform

- **macOS.** No WSL, no Windows paths.
- ESP32 (ESP-WROOM-32, CP2102, 30-pin) over USB serial at 115200
- Agents run as tmux **windows** in one session named `agentpad`, which the daemon creates itself; daemon runs natively; all on the same machine
- **Python via mise: project-local venv on Python 3.13** (see `mise.toml`). Run all Python from inside this dir so mise activates `.venv`.
- Python deps: `pyserial` only.

## Architecture

```
Claude Code hooks → events.jsonl → daemon → serial → ESP32 (LEDs, LCD)
                                    daemon ← serial ← ESP32 (6 buttons)
                                    daemon → tmux new-window/select-window/send-keys
                                    daemon → tmux capture-pane (has the prompt cleared?)
```

The daemon *launches* each agent's tmux window (running `claude`) on the first color-button press and records that window's pane id, so it maps pane → agent slot directly. Hook events (`$TMUX_PANE` + state) then light the matching LED. Approve/Deny send keystrokes to whichever agent window is **on screen**, gated by the `blocked` interlock.

The four agent windows are each tinted a dark color (`window-style bg=…`) matching their LED/button. Attach with `tmux attach -t agentpad`.

### `blocked` comes from the PermissionRequest hook — do not "simplify" this

Measured on this hardware, three ways to learn an agent is waiting:

| Source | Latency |
|---|---|
| `Notification` hook | **+6.00s** — fires late *by design* (it exists to chase a user who walked away) |
| screen scraping | +0.24s — plus fragile string matching |
| **`PermissionRequest` hook** | **+0.00s** — used |

`PermissionRequest` fires only when a prompt is genuinely shown (verified: `df -h` auto-allowed → no hook; `curl -sI` prompts → hook), and it covers every prompt shape — tool permission, plan approval, trust dialogs — with no text matching, so Claude's own prose can never trigger it.

Screen reading survives only to notice the prompt has been **answered**, and matches prompt *structure* (numbered option rows), not wording — so it also handles "Would you like to proceed?", not just "Do you want to proceed?".

## Files

| Path | What |
|---|---|
| `daemon.py` | The brain: serial ↔ tmux ↔ LEDs/LCD. Launches/focuses agents, approve/deny. |
| `test.py` | Serial smoke test |
| `hooks/agentpad.sh` | Source of truth for the hook script — **copy to `~/.claude/agentpad.sh`** (see Install) |
| `firmware/agentpad/agentpad.ino` | The real firmware. Folder name matches the `.ino` so `arduino-cli` can build it. |
| `firmware/{blink,lcdtest,ledtest,btntest}/` | Milestone test sketches, kept for hardware debugging |
| `agentpad-build-guide.md` | Full build guide (hardware + software) |
| `mise.toml` | Python 3.13 venv definition |
| `events.jsonl`, `daemon.log` | Runtime state; both gitignored |
| `~/.claude/agentpad.sh` | Installed copy of the hook script (appends one JSON line per event) |
| `~/.claude/settings.json` | Five hooks pointing at that script (global, not in this repo) |

## Install (the hooks live outside the repo)

The daemon is deaf without these, and they are **not** version-controlled by default:

```bash
cp hooks/agentpad.sh ~/.claude/agentpad.sh && chmod +x ~/.claude/agentpad.sh
```

Then `~/.claude/settings.json` needs five hooks, each running `~/.claude/agentpad.sh <state>`:

| Hook event | State |
|---|---|
| `SessionStart` | `idle` |
| `UserPromptSubmit` | `working` |
| `PermissionRequest` | `blocked` |
| `Stop` | `done` |
| `SessionEnd` | `none` |

Run the daemon with `mise exec -- python daemon.py` from this directory.

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
- **Keep the approve/deny interlock.** The daemon must refuse to send keystrokes unless the agent is genuinely blocked. Two independent conditions must agree — the `PermissionRequest` state *and* a prompt visible on screen — and the state is cleared immediately after sending so a double press can't type into the normal input box. This is what stops junk being injected into a prompt.
- **Only panes the daemon launched may receive keystrokes.** The hooks are global, so every Claude session on the machine writes to `events.jsonl`; unknown panes must never be assigned a slot.
- **`APPROVE` and `DENY` stay top-level config constants.** Permission menu numbering varies; these get tuned live.
- **Debounce lives in firmware**, not Python. 50ms.
- LEDs are single-color. Color = agent identity. Blink pattern = state.

## What you cannot verify

You cannot see the hardware. You cannot confirm an LED lit, the LCD shows text, or a button registered. When a step depends on physical observation, say so and wait for the human to report back rather than assuming success.

Serial port name is measured on real hardware, not guessed (this build: `/dev/cu.usbserial-0001`).

Firmware *compilation* can be verified without hardware via `arduino-cli compile --fqbn esp32:esp32:esp32 firmware/agentpad`. Uploading is done here with `arduino-cli upload -p <port> --fqbn esp32:esp32:esp32 firmware/agentpad`.

## Testing note

Permission prompts only fire for commands that escape the sandbox. **`curl -sI https://example.com` prompts reliably; `date` and `df -h` do not** (this machine runs `acceptEdits`). Use curl when demoing or testing the interlock — otherwise the LED just goes solid "working" and never blinks.

## Status

**Working end-to-end.** Hardware fully built and verified (LCD@0x27, 4 LEDs, 6 buttons). Firmware, daemon, and hooks all confirmed on real hardware: color button → tmux window spawn/focus → hooks → LED state → approve/deny button → keystroke lands in the correct pane.
