"""Milestone 9: the daemon.

Reads Claude Code hook events from events.jsonl, drives the ESP32 (LEDs + LCD),
reads buttons from the ESP32, reads the game controller via pygame, and uses
tmux to focus panes and type approve/deny keystrokes.

Fill in BTN_A / BTN_B / BTN_START from pad.py before running.
"""
import json, os, time, subprocess, threading
import serial, pygame

# ===== CONFIG =====
PORT      = "/dev/cu.usbserial-0001"   # confirmed on this build
BTN_A     = 0       # <-- set from pad.py (approve)
BTN_B     = 1       # <-- set from pad.py (deny)
BTN_START = 9       # <-- set from pad.py (jump to next blocked)
APPROVE   = "1"     # keystroke typed at a permission prompt to approve
DENY      = "3"     # keystroke typed to deny
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
        send("D0 not blocked")        # safety interlock: never type unless blocked
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
