# Agent Pad

Physical control surface for Claude Code — a self-contained "code micro" clone. Four LEDs + an LCD show what four agents are doing. Seven buttons on the board do everything: the four color buttons each **launch a color-tinted tmux `claude` session (if not running) and focus it**; three more **approve / deny / always-allow** the on-screen agent's permission prompt. **Single device — there is no game controller.** Don't reintroduce one.

**Soldered build: `BUILD.md` + `SOLDERING.md`. Breadboard prototype: `BREADBOARD.md`.**
`docs-archive-breadboard-era.md` is the superseded milestone guide — do not build from it.

## Platform

- **macOS.** No WSL, no Windows paths.
- ESP32 (ESP-WROOM-32, CP2102, 30-pin) over USB serial at 115200
- Agents run as tmux **windows** in one session named `agentpad`, which the daemon creates itself; daemon runs natively; all on the same machine
- **Python via mise: project-local venv on Python 3.13** (see `mise.toml`). Run all Python from inside this dir so mise activates `.venv`.
- Python deps: `pyserial` only.

## Architecture

```
Claude Code hooks → events.jsonl → daemon → serial → ESP32 (LEDs, LCD)
                                    daemon ← serial ← ESP32 (7 buttons)
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
| `hooks/agentpad-status.sh` | statusLine script — the only source of context-window % |
| `firmware/agentpad/agentpad.ino` | The real firmware. Folder name matches the `.ino` so `arduino-cli` can build it. |
| `firmware/{blink,lcdtest,ledtest,btntest}/` | Milestone test sketches, kept for hardware debugging |
| `BUILD.md` | The soldered build — parts, board layout, wiring, steps. Tables between `<!-- GEN:… -->` markers are GENERATED |
| `SOLDERING.md` | From-zero soldering course with practice exercises |
| `MULTIMETER.md` | From-zero multimeter guide — continuity, diode and resistance tests |
| `BREADBOARD.md` | Rebuilding the breadboard prototype |
| `START-HERE.md` | **The map** — how board, daemon and hooks fit together. Read first |
| `WIRING.md` | **GENERATED** flat point-to-point list: every wire, leg and socket slot |
| `CONNECTIONS.md` | **How you physically join two points on perfboard** |
| `tools/layout.py` | **Single source of truth** for every row, column, GPIO, mount hole and connector |
| `tools/verify-layout.py` | Checks bodies, overlaps, hole occupancy and connectivity |
| `tools/gen-tables.py` | Regenerates BUILD.md's tables from `layout.py` |
| `tools/gen-wiring.py` | Regenerates `WIRING.md` from `layout.py` |
| `tools/view-docs.py` | Renders every doc into one browsable `docs.html` |
| `tools/schematic.py` | Generates `schematics.html` from `layout.py` |
| `tools/view-plan.py` | Renders BUILD.md into a tickable bench checklist |
| `docs-archive-breadboard-era.md` | Superseded milestone guide — do not build from it |
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
B <0-6>     # 0-3 select/launch agent, 4 approve, 5 deny, 6 always-allow
```

Do not replace this with a binary or JSON protocol.

## Pin map — do not change without asking

| Function | GPIO |
|---|---|
| LEDs (red, green, blue, yellow = agents 1-4) | 13, 14, 27, 26 |
| Agent-select buttons (same color order) | 32, 33, 25, 4 |
| Approve button | 19 |
| Deny button | 18 |
| Always-allow button ("yes, don't ask again") | 23 |
| LCD I²C SDA / SCL | 21, 22 |
| *free* | 5, 16, 17 |

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

Firmware *compilation* can be verified without hardware via `arduino-cli compile --fqbn esp32:esp32:esp32 firmware/agentpad`. Upload with `arduino-cli compile -u -p <port> --fqbn esp32:esp32:esp32 <sketch>` — bare `upload` does not compile and fails on a clean cache.

**Never hand-edit a row, column or GPIO in BUILD.md or schematic.py.** Change `tools/layout.py`, then run `verify-layout.py`, `gen-tables.py` and `schematic.py`. The docs drifted from the layout four times; the last time the wire table would have shorted seven buttons to ground. That is why the tables are generated.

**Stop the daemon before uploading.** Only one process can hold the serial port; uploading while the daemon runs fails with "Serial data stream stopped: Possible serial noise or corruption", which reads like a hardware fault but isn't.

## Testing note

Permission prompts only fire for commands that escape the sandbox. **`curl -sI https://example.com` prompts reliably; `date` and `df -h` do not** (this machine runs `bypassPermissions` globally, and the daemon launches agent windows with `--permission-mode manual` so they still prompt). Use curl when demoing or testing the interlock — otherwise the LED just goes solid "working" and never blinks.

## Context usage

The focused agent's context-window usage shows on the LCD bottom row (`1w 2B 3i 4d 34%`). It comes from Claude Code's **statusLine** payload (`context_window.used_percentage`) — the only place that value is exposed — and is attributed per agent because the statusLine command inherits `$TMUX_PANE` inside a tmux window. See `hooks/agentpad-status.sh`.

An LED bar graph was designed and coded (74HC595, `G <0-100>` serial command, battery semantics: full = fresh) but **deliberately not wired** — see `BUILD.md`. The firmware and daemon support is still present and harmless, so it can be added later without other changes.

## Status

**Working end-to-end.** Hardware built and verified: LCD@0x27, 4 LEDs, **7 buttons** (4 select + approve/deny/always-allow). Firmware, daemon, and hooks all confirmed on real hardware: color button → tmux window spawn/focus → hooks → LED state → approve/deny/always button → keystroke lands in the correct pane. Survives unplug/replug of the ESP32.

Next: soldered build on **one 30 × 42 double-sided PCB** (control surface in cols 1–28, ESP32 socketed at cols 30–40, 4-pin LCD port at cols 30–33 row 2), screwed to a wooden plate — see `BUILD.md`, `SOLDERING.md`, `BREADBOARD.md`.

**On the soldered board the LCD plugs into a board-mounted 4-pin male port, not the ESP32's pins** — those are inside the socket once the module is seated. On the *breadboard* prototype the jumpers do go straight onto the ESP32's pins; both are correct for their own build.
