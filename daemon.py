"""Agent Pad daemon (self-contained: all control on the board, no game controller).

Flow:
  - Color buttons (serial "B 0".."B 3") launch a color-tinted tmux window running
    `claude` if that agent isn't running yet, then focus it.
  - Approve / Deny buttons (serial "B 4" / "B 5") send a keystroke to the agent whose
    window is on screen -- but ONLY when it is genuinely blocked (safety interlock).
  - Claude Code hooks append to events.jsonl (pane + state); the daemon lights the
    matching LED and updates the LCD.

`blocked` comes from the PermissionRequest hook, which fires exactly when a permission
prompt is shown -- instantly, and for every prompt type. Do NOT switch this back to the
Notification hook: measured on this hardware, Notification fires 6.00s AFTER the prompt
renders (it exists to chase a user who walked away), which made the pad useless.

Run it in its own terminal, then attach to the session in another:
    tmux attach -t agentpad
"""
import json, os, re, time, subprocess, threading
import serial

# ===== CONFIG =====
PORT     = "/dev/cu.usbserial-0001"     # confirmed on this build
SESSION  = "agentpad"                    # tmux session name
APPROVE  = "1"                           # keystroke sent to approve a prompt
DENY     = "3"                           # keystroke sent to deny a prompt
CLAUDE   = "claude"                      # command launched in each agent window
EVENTS   = os.path.expanduser("~/projects/agentpad/events.jsonl")
LOGFILE  = os.path.expanduser("~/projects/agentpad/daemon.log")
# per-agent identity (index 0-3 = red, green, blue, yellow)
NAMES  = ["A1-red", "A2-grn", "A3-blu", "A4-ylw"]
COLORS = ["colour52", "colour22", "colour17", "colour58"]  # dark tint per window
STATES = {"none", "idle", "working", "blocked", "done"}
# ==================

ser = serial.Serial(PORT, 115200, timeout=0.1)
time.sleep(2)
ser_lock = threading.Lock()   # serial is shared by several threads

slots     = [None] * 4     # agent index -> tmux pane id (once launched)
pane_slot = {}             # pane id -> agent index
info      = {}             # pane id -> {"state":..., "since":..., "prev":...}
focus     = 0

def log(msg):
    try:
        with open(LOGFILE, "a") as f:
            f.write(f"{time.strftime('%H:%M:%S')} {msg}\n")
    except OSError:
        pass

def send(line):
    with ser_lock:
        ser.write((line + "\n").encode())

def tmux(*args):
    return subprocess.run(["tmux", *args], capture_output=True, text=True)

def set_state(pane, i, st, keep_prev=None):
    """Record a state change and push it to the LED. Resets the timer only when the
    state actually changes, so repeat events don't restart the clock."""
    prev = info.get(pane)
    if not prev or prev["state"] != st:
        info[pane] = {"state": st, "since": time.time(),
                      "prev": keep_prev if keep_prev is not None
                      else (prev or {}).get("state", "idle")}
    else:
        prev["state"] = st
    send(f"L {i} {st}")

def ensure_session():
    """Create the session (with a placeholder 'home' window) so you can attach
    immediately and watch agent windows appear as you press buttons."""
    if tmux("has-session", "-t", SESSION).returncode != 0:
        tmux("new-session", "-d", "-s", SESSION, "-n", "home")

def sync_slots():
    """Bind each agent window's pane to its slot BY NAME. Authoritative and
    idempotent, so color/slot stays correct even after a daemon restart (when the
    windows already exist and we never re-spawn them)."""
    if tmux("has-session", "-t", SESSION).returncode != 0:
        return
    out = tmux("list-windows", "-t", SESSION, "-F", "#{window_name}\t#{pane_id}").stdout
    live = {}
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) != 2:
            continue
        name, pane = parts
        if name in NAMES:
            live[NAMES.index(name)] = pane
    for i, pane in live.items():
        old = slots[i]
        if old and old != pane:
            pane_slot.pop(old, None)   # window respawned: drop the orphan mapping
            info.pop(old, None)
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
    row1 = " ".join(f"{i+1}{letters.get(state_of(i), '?')}" for i in range(4))
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
        wins = tmux("list-windows", "-t", SESSION,
                    "-F", "#{window_name}").stdout.splitlines()
    if NAMES[i] not in wins:
        _spawn(i)
    sync_slots()   # keep color/slot binding authoritative
    tmux("select-window", "-t", f"{SESSION}:{NAMES[i]}")
    focus = i
    refresh()

def active_slot():
    """Agent slot whose tmux window is currently active, or None if not an agent
    window. Lets the pad follow tmux even when you switch windows by hand."""
    name = tmux("display-message", "-p", "-t", SESSION, "#{window_name}").stdout.strip()
    return NAMES.index(name) if name in NAMES else None

# A selection prompt renders as numbered option rows at the bottom of the screen.
# Matching that STRUCTURE (rather than specific wording) covers every prompt shape --
# "Do you want to proceed?", "Would you like to proceed?", trust dialogs, plan mode --
# without depending on prose that Claude might merely be talking about.
OPTION_RE = re.compile(r"^\s*[❯>]?\s*[1-9]\.\s+\S")

def prompt_visible(pane):
    """True if a live selection/permission prompt is on that pane's screen RIGHT NOW."""
    r = tmux("capture-pane", "-p", "-t", pane)
    if r.returncode != 0:
        return False
    tail = r.stdout.splitlines()[-20:]
    return sum(1 for l in tail if OPTION_RE.match(l)) >= 2

def respond(keystroke):
    """Answer the prompt on the agent that is actually on screen."""
    global focus
    i = active_slot()
    if i is None:
        # not looking at an agent window -- refuse rather than guess a target
        log(f"respond({keystroke!r}) refused: active window is not an agent")
        send("D0 no agent focused")
        time.sleep(0.6)
        refresh()
        return
    focus = i
    p = slots[focus]
    # Small grace window: the hook and the button race by a few ms.
    if p and info.get(p, {}).get("state") != "blocked":
        deadline = time.time() + 0.4
        while time.time() < deadline and info.get(p, {}).get("state") != "blocked":
            time.sleep(0.02)
    st = info.get(p, {}).get("state") if p else None
    snapshot = {k: v["state"] for k, v in list(info.items())}
    # Two independent conditions must agree before we type anything: the hook says
    # blocked AND a prompt is on screen right now. Either alone can be stale.
    on_screen = prompt_visible(p) if p else False
    log(f"respond({keystroke!r}) slot={i} pane={p} state={st} on_screen={on_screen} "
        f"info={snapshot}")
    if not p or st != "blocked" or not on_screen:
        send("D0 not blocked")
        time.sleep(0.6)
        refresh()
        return
    r = tmux("send-keys", "-t", p, keystroke, "Enter")
    # Clear immediately so a second press can't re-fire into the now-normal input box.
    set_state(p, i, "working")
    refresh()
    log(f"  sent {keystroke!r} to {p} rc={r.returncode} err={r.stderr.strip()!r}")

def slot_of(pane):
    """Map a hook's pane to an agent slot. Only panes we launched count -- the hooks
    are global, so every Claude session on the machine writes to events.jsonl and a
    stranger must never be able to claim a slot (or receive our keystrokes)."""
    return pane_slot.get(pane)

def tail_events():
    open(EVENTS, "a").close()
    with open(EVENTS, "r") as f:
        f.seek(0, 2)
        while True:
            line = f.readline()
            if not line or not line.endswith("\n"):
                if line:                     # partial write: rewind and re-read whole
                    f.seek(-len(line), os.SEEK_CUR)
                time.sleep(0.02)
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
            if st not in STATES:
                continue
            set_state(pane, i, st)
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

def watch_prompts():
    """Clear `blocked` once the prompt leaves the screen (answered here or from the
    pad). Setting `blocked` is the PermissionRequest hook's job, not ours."""
    while True:
        time.sleep(0.2)
        for i, p in enumerate(list(slots)):
            if not p or info.get(p, {}).get("state") != "blocked":
                continue
            if not prompt_visible(p):
                back = info.get(p, {}).get("prev") or "working"
                if back == "blocked":
                    back = "working"
                set_state(p, i, back)
                log(f"prompt cleared pane={p} slot={i} -> {back}")
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
    seamless. `blocked` is deliberately NOT restored: a prompt from a previous run is
    long gone, and reviving it would open the interlock with nothing on screen."""
    try:
        lines = open(EVENTS).read().splitlines()
    except FileNotFoundError:
        return
    for line in lines:
        try:
            e = json.loads(line)
        except Exception:
            continue
        pane, st = e.get("pane"), e.get("state", "idle")
        if pane in pane_slot and st in STATES and st != "blocked":
            info[pane] = {"state": st, "since": time.time(), "prev": st}
    for pane, i in pane_slot.items():
        if pane in info:
            send(f"L {i} {info[pane]['state']}")

def supervise(fn):
    """Keep a worker alive. Without this one exception silently half-kills the daemon
    (e.g. buttons stop working) while the process still looks healthy."""
    def wrapper():
        while True:
            try:
                fn()
            except Exception as exc:
                log(f"!! {fn.__name__} crashed: {exc!r} -- restarting in 1s")
                time.sleep(1)
    return wrapper

ensure_session()
blank_leds()      # clear stale LED state the board held from a previous run
sync_slots()      # bind existing agent windows to their color slots on startup
recover_state()   # restore last-known LED states (never `blocked`) after a restart
for worker in (tail_events, read_serial, tick, watch_prompts):
    threading.Thread(target=supervise(worker), daemon=True).start()

refresh()
print("agentpad running. ctrl-c to quit.")
print(f"attach the board's sessions with:  tmux attach -t {SESSION}")

try:
    while True:
        time.sleep(0.2)
except KeyboardInterrupt:
    pass
finally:
    try:
        ser.close()
    except Exception:
        pass
