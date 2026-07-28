"""Agent Pad daemon (self-contained: all control on the board, no game controller).

Flow:
  - Color buttons (serial "B 0".."B 3") launch a color-tinted tmux window running
    `claude` if that agent isn't running yet, then focus it.
  - Approve / Deny buttons (serial "B 4" / "B 5") send a keystroke to the focused
    agent -- but ONLY when that agent's state is `blocked` (safety interlock).
  - Claude Code hooks append to events.jsonl (pane + state); the daemon lights the
    matching LED and updates the LCD.

Run it in its own terminal, then attach to the session in another:
    tmux attach -t agentpad
"""
import json, os, time, subprocess, threading
import serial

# ===== CONFIG =====
PORT     = "/dev/cu.usbserial-0001"     # confirmed on this build
SESSION  = "agentpad"                    # tmux session name
APPROVE  = "1"                           # keystroke sent to approve a prompt
DENY     = "3"                           # keystroke sent to deny a prompt
CLAUDE   = "claude"                      # command launched in each agent window
EVENTS   = os.path.expanduser("~/projects/agentpad/events.jsonl")
# per-agent identity (index 0-3 = red, green, blue, yellow)
NAMES  = ["A1-red", "A2-grn", "A3-blu", "A4-ylw"]
COLORS = ["colour52", "colour22", "colour17", "colour58"]  # dark tint per window
# ==================

ser = serial.Serial(PORT, 115200, timeout=0.1)
time.sleep(2)
ser_lock = threading.Lock()   # serial is shared by tail/read/tick threads

slots     = [None] * 4     # agent index -> tmux pane id (once launched)
pane_slot = {}             # pane id -> agent index
info      = {}             # pane id -> {"state":..., "since":...}
focus     = 0

def send(line):
    with ser_lock:
        ser.write((line + "\n").encode())

def tmux(*args):
    return subprocess.run(["tmux", *args], capture_output=True, text=True)

def ensure_session():
    """Create the session (with a placeholder 'home' window) so you can attach
    immediately and watch agent windows appear as you press buttons."""
    if tmux("has-session", "-t", SESSION).returncode != 0:
        tmux("new-session", "-d", "-s", SESSION, "-n", "home")

def sync_slots():
    """Bind each agent window's pane to its slot BY NAME. Authoritative and
    idempotent, so color↔slot stays correct even after a daemon restart (when the
    windows already exist and we never re-spawn them)."""
    if tmux("has-session", "-t", SESSION).returncode != 0:
        return
    out = tmux("list-windows", "-t", SESSION, "-F", "#{window_name}\t#{pane_id}").stdout
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) != 2:
            continue
        name, pane = parts
        if name in NAMES:
            i = NAMES.index(name)
            slots[i] = pane
            pane_slot[pane] = i

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

def _spawn(i):
    """Create the tmux window for agent i running claude; record its pane id."""
    if tmux("has-session", "-t", SESSION).returncode != 0:
        r = tmux("new-session", "-d", "-s", SESSION, "-n", NAMES[i],
                 "-P", "-F", "#{pane_id}", CLAUDE)
    else:
        r = tmux("new-window", "-t", SESSION, "-n", NAMES[i],
                 "-P", "-F", "#{pane_id}", CLAUDE)
    pane = r.stdout.strip()
    if pane:
        slots[i] = pane
        pane_slot[pane] = i
    # tint the whole window so you can tell agents apart at a glance
    tmux("set-option", "-w", "-t", f"{SESSION}:{NAMES[i]}", "window-style",
         f"bg={COLORS[i]}")

def launch_or_focus(i):
    global focus
    wins = []
    if tmux("has-session", "-t", SESSION).returncode == 0:
        wins = tmux("list-windows", "-t", SESSION, "-F", "#{window_name}").stdout.split()
    if NAMES[i] not in wins:
        _spawn(i)
    sync_slots()   # keep color↔slot binding authoritative
    tmux("select-window", "-t", f"{SESSION}:{NAMES[i]}")
    focus = i
    refresh()

def active_slot():
    """Agent slot whose tmux window is currently active, or None if not an agent
    window. Lets the pad follow tmux even when you switch windows by hand."""
    name = tmux("display-message", "-p", "-t", SESSION, "#{window_name}").stdout.strip()
    return NAMES.index(name) if name in NAMES else None

def log(msg):
    with open(os.path.expanduser("~/projects/agentpad/daemon.log"), "a") as f:
        f.write(f"{time.strftime('%H:%M:%S')} {msg}\n")

def respond(keystroke):
    # Target the window actually on screen, not just the last button pressed --
    # otherwise switching windows inside tmux silently aims approve at the wrong agent.
    global focus
    i = active_slot()
    if i is not None:
        focus = i
    p = slots[focus]
    # The prompt renders on screen slightly BEFORE the Notification hook reaches us,
    # so a quick press would be refused on a stale state. Wait briefly for `blocked`
    # to land. Still never types unless the agent really is blocked.
    if p and info.get(p, {}).get("state") != "blocked":
        deadline = time.time() + 0.5   # just covers the 200ms screen-poll interval
        while time.time() < deadline and info.get(p, {}).get("state") != "blocked":
            time.sleep(0.05)
    st = info.get(p, {}).get("state") if p else None
    log(f"respond({keystroke!r}) active_slot={i} focus={focus} pane={p} state={st} "
        f"slots={slots} info={ {k: v['state'] for k, v in info.items()} }")
    if not p or st != "blocked":
        send("D0 not blocked")          # interlock: never type unless blocked
        time.sleep(0.6)
        refresh()
        return
    r = tmux("send-keys", "-t", p, keystroke, "Enter")
    log(f"  sent {keystroke!r} to {p} rc={r.returncode} err={r.stderr.strip()!r}")

def slot_of(pane):
    """Map a hook's pane to an agent slot (known if we launched it; else first free)."""
    if pane in pane_slot:
        return pane_slot[pane]
    for i in range(4):
        if slots[i] is None:
            slots[i] = pane
            pane_slot[pane] = i
            return i
    return None

def tail_events():
    open(EVENTS, "a").close()
    with open(EVENTS, "r") as f:
        f.seek(0, 2)
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.02)   # tight poll: the LED should blink the moment
                continue           # the prompt appears, not 100ms later
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
            if st == "blocked":
                continue    # screen detection owns `blocked`; the hook is ~6s stale
            prev = info.get(pane)
            if not prev or prev["state"] != st:
                info[pane] = {"state": st, "since": time.time()}  # state changed: reset timer
            else:
                prev["state"] = st                                # same state repeated: keep timer
            send(f"L {i} {st}")
            log(f"event pane={pane} slot={i} state={st}")
            refresh()

def read_serial():
    while True:
        line = ser.readline().decode(errors="ignore").strip()
        if not line.startswith("B "):
            continue
        try:
            n = int(line.split()[1])
        except (IndexError, ValueError):
            continue
        if   0 <= n <= 3: launch_or_focus(n)
        elif n == 4:      respond(APPROVE)
        elif n == 5:      respond(DENY)

def prompt_visible(pane):
    """True if a live permission prompt is on that pane's screen RIGHT NOW.

    Claude Code delays the Notification hook by ~6s (measured), because notifications
    are meant to chase an absent user. That's far too slow for a status light, so
    `blocked` is detected by reading the screen instead -- which is instant.
    Requires both the question and the numbered selector so Claude's prose about
    permission prompts can't trigger a false positive.
    """
    txt = tmux("capture-pane", "-p", "-t", pane).stdout
    tail = "\n".join(txt.splitlines()[-25:])
    return "Do you want" in tail and "1. Yes" in tail

def watch_prompts():
    """Poll each agent's screen so the LED blinks the moment the prompt appears."""
    while True:
        time.sleep(0.2)
        for i, p in enumerate(slots):
            if not p:
                continue
            try:
                vis = prompt_visible(p)
            except Exception:
                continue
            cur = info.get(p, {}).get("state")
            if vis and cur != "blocked":
                info[p] = {"state": "blocked", "since": time.time()}
                send(f"L {i} blocked")
                log(f"screen-detect BLOCKED pane={p} slot={i}")
                refresh()
            elif not vis and cur == "blocked":
                # prompt cleared (answered here or from the pad) -- back to working
                info[p] = {"state": "working", "since": time.time()}
                send(f"L {i} working")
                log(f"screen-detect cleared pane={p} slot={i}")
                refresh()

def tick():
    """Re-render the LCD every second so the state timer counts live, and follow
    whichever agent window tmux has active (you may switch windows by hand)."""
    global focus
    while True:
        time.sleep(1)
        i = active_slot()
        if i is not None and i != focus:
            focus = i
        refresh()

def blank_leds():
    """Turn all four LEDs off. The ESP32 holds its last-known LED state across
    daemon restarts, so without this a fresh start shows stale lights."""
    for i in range(4):
        send(f"L {i} none")

def recover_state():
    """Rebuild last-known agent state from the events log so a daemon restart is
    seamless (LEDs + blocked interlock correct immediately, not on next event)."""
    try:
        lines = open(EVENTS).read().splitlines()
    except FileNotFoundError:
        return
    for line in lines:
        try:
            e = json.loads(line)
        except Exception:
            continue
        pane = e.get("pane")
        if pane in pane_slot:                     # only known agent panes
            info[pane] = {"state": e.get("state", "idle"), "since": time.time()}
    for pane, i in pane_slot.items():
        if pane in info:
            send(f"L {i} {info[pane]['state']}")

ensure_session()
blank_leds()      # clear stale LED state the board held from a previous run
sync_slots()      # bind existing agent windows to their color slots on startup
recover_state()   # restore last-known LED states + interlock after a restart
threading.Thread(target=tail_events, daemon=True).start()
threading.Thread(target=read_serial, daemon=True).start()
threading.Thread(target=tick, daemon=True).start()
threading.Thread(target=watch_prompts, daemon=True).start()

refresh()
print("agentpad running. ctrl-c to quit.")
print(f"attach the board's sessions with:  tmux attach -t {SESSION}")

try:
    while True:
        time.sleep(0.2)
except KeyboardInterrupt:
    pass
