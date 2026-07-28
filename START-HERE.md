# Start here — how the whole thing fits together

Read this once. It's the map; everything else is detail.

---

## What you're building

A physical control surface for Claude Code. Four agents run as tmux windows on your Mac.
The board shows you what each one is doing, and lets you answer them without touching the
keyboard.

```
   ┌─────────────────────────────────────────┐
   │  A3 BLOCKED 4:21                        │   16x2 LCD — which agent, what state,
   │  1w 2i 3B 4d  34%                       │   how long, context used
   └─────────────────────────────────────────┘

     ●        ●        ●        ●               4 LEDs — one per agent, colour = identity,
    ┌───┐    ┌───┐    ┌───┐    ┌───┐            blink pattern = state
    │ 1 │    │ 2 │    │ 3 │    │ 4 │            4 colour buttons — launch or focus
    └───┘    └───┘    └───┘    └───┘            that agent's tmux window

      ▫         ▫         ▫                     3 small buttons — answer the prompt
     AA        no        yes                    that's on screen right now
```

**One USB cable to the Mac.** That's the only connection. No WiFi, no battery, no second
device.

---

## The whole loop, once

This is the thing to hold in your head. Follow one permission prompt all the way round:

```
  1. You press  yes                     (a switch closes, pulling GPIO 19 to ground)
        │
  2.    └─►  ESP32 firmware debounces, prints  "B 4"  down the USB serial line
        │
  3.    └─►  daemon.py reads that line, checks the interlock, and does
        │      tmux send-keys -t <the focused agent's pane> "1" Enter
        │
  4.    └─►  Claude Code in that pane receives the keystroke and runs the command
        │
  5.    └─►  Claude Code fires its Stop hook  →  ~/.claude/agentpad.sh
        │
  6.    └─►  that appends one JSON line to  events.jsonl
        │
  7.    └─►  daemon.py is tailing that file, sees state "done" for that pane
        │
  8.    └─►  daemon writes  "L 2 done"  back down the serial line
        │
  9.    └─►  firmware sets LED 3's blink pattern. You see it change.
```

**Steps 1–2 and 8–9 are the hardware you're about to build. Steps 3–7 already work and are
not changing.**

Press to keystroke (steps 1–4) is faster than you can perceive — the firmware debounces
for 50ms and the daemon reads the port on a 100ms timeout. The LED (steps 5–9) changes
whenever the agent's state actually changes, which for a real command is however long that
command takes. The part that had to be fast is the *blocked* light, and that comes from the
`PermissionRequest` hook at +0.00s.

---

## The three layers

**Layer 1 — the board.** Dumb on purpose. It reads seven switches and drives four LEDs
and an LCD. It has no idea what Claude Code is. Its entire vocabulary is five line-based
serial commands, which you can type by hand into the Arduino Serial Monitor to test it.

| Mac → ESP32 | meaning |
|---|---|
| `L <0-3> <none\|idle\|working\|blocked\|done>` | set an LED's pattern |
| `D0 <text>` / `D1 <text>` | write an LCD row |

| ESP32 → Mac | meaning |
|---|---|
| `B <0-6>` | a button was pressed. 0–3 select an agent, 4 approve, 5 deny, 6 always-allow |

**Layer 2 — the daemon.** `daemon.py` on your Mac. It owns the serial port, launches each
agent's tmux window on first press, remembers which pane belongs to which slot, and
translates between the board and tmux.

**Layer 3 — Claude Code's hooks.** Five hooks, configured globally in
`~/.claude/settings.json`, each appending one line to `events.jsonl`. That file is how the
agents tell the daemon what they're doing.

> **Why `PermissionRequest` and not `Notification`?** Measured on this hardware:
> `Notification` fires **6.00 seconds** after the prompt appears — it exists to chase a
> user who walked away. `PermissionRequest` fires at **+0.00s**. That one measurement is
> why the board feels instant instead of broken.

---

## How the board maps onto that

The board is **one 30 × 42 hole PCB, 120 × 80mm**, split into two zones:

```
   cols 1–28  the control surface              cols 30–40  the ESP32
   ─────────────────────────────────────────   ──────────────────────────
   row  2   LED anodes (+)      → GPIO          the module plugs into two
   row  3   LED cathodes (−)                    15-way sockets and can be
   row  4   220Ω top                            pulled out any time
   row  8   ── GND bus ──  and 220Ω bottom
   row 11   colour button signal legs           cols 30–33, row 2:
   row 16   ── GND bus ──  and their gnd legs     the 4-pin LCD port
   row 19   AA / no / yes signal legs
   row 21   ── GND bus ──  and their gnd legs   USB points at the bottom edge
```

Three ideas make the layout work, and they're the ones worth understanding before you
solder anything:

**1. Perfboard connects nothing.** Every hole is an isolated island. A breadboard hides
metal clips that join each row of five for you; this has none. *You* are the wiring. →
[`CONNECTIONS.md`](CONNECTIONS.md)

**2. A "bus" is how you avoid 11 ground wires.** Ground has to reach 11 legs — four
resistor bottoms, four colour-button ground legs, three answer-button ground legs. Instead
of 11 wires you lay **one bare wire along a row and solder it to every pad**.
That turns a row of islands into one shared node. There are three of them — rows 8, 16 and
21 — joined down column 1. Every ground leg on the board lands directly on one, so there
are **zero ground jumpers**.

**3. Only 12 wires actually go anywhere.** Everything else is a component leg sitting in
the right hole. Those 12 run from a component pad to the matching pad at the ESP32 socket,
plus 4 more for the LCD port. Sixteen wires total.

---

## The parts that are not permanent

Two things must survive the build, and both unplug:

| | why | how |
|---|---|---|
| **The ESP32** | you have exactly one | it sits in a **socket**, never soldered |
| **The LCD** | you have exactly one | 4 F-F jumpers to a **port** on the board, never soldered |

The LCD port exists because of a detail that's easy to miss: once the ESP32 is seated, its
own pins are *inside* the socket, so nothing can clip onto them. The board therefore carries
its own 4-pin male header, wired to the socket pads.

---

## What actually gets soldered — and what never is

The single most important distinction in the build. Two parts are irreplaceable and
**neither is ever soldered**:

| Never soldered | Why | How it connects instead |
|---|---|---|
| **The ESP32** | you have exactly one | plugs into two **socket strips**. The *strips* are soldered; the module is not |
| **The LCD** | you have exactly one | 4 F-F jumpers to the **LCD port**, a male header soldered to the board |

Everything soldered falls into four groups, ~149 joints total:

| | Joints | |
|---|---:|---|
| **Socket strips** | 30 | two 15-way female strips. The ESP32 plugs in on top afterwards |
| **Component legs** | 37 | 4 LEDs, 4 resistors, 7 switches (**3 legs each** — one is clipped off) |
| **Buses** | 46 | bare wire along rows 8, 16, 21, linked down column 1 |
| **Wires** | 36 | 16 wires × 2 ends, plus the LCD port's 4 male pins |

```
   the ESP32          ┌───────────────┐   ← plugs in LAST, never soldered
                      │  ▼ ▼ ▼ ▼ ▼ ▼  │
   socket strip    ┌──┴───────────────┴──┐
   (SOLDER THIS)   │ ⌷  ⌷  ⌷  ⌷  ⌷  ⌷  │
   ════════════════╪══╪══╪══╪══╪══╪══╪═══  ← the board
                   ▼  ▼  ▼  ▼  ▼  ▼  ▼
                  the strip's own pins — these are what you solder
```

**Both ends of every wire are lap joints.** The hole at each end is already full — the
socket pad holds a header pin, the component pad holds the LED's or switch's leg. So you
solder the tinned wire end *onto solder that is already there*, never into an empty hole.
That is why step 1 leaves a 2mm stub on the 16 socket pads that take a wire: something to
hook the wire around.

**You don't solder every component and then every wire.** Each step fits its own
components *and* their wires, so the step ends in a test that actually runs.

---

## What you'll actually do, in order

| | | ends with |
|---|---|---|
| **See the wiring** | [`WIRING.md`](WIRING.md) — every wire, every leg, every socket slot, in flat tables | you can look up any connection in one place |
| **Learn the moves** | [`CONNECTIONS.md`](CONNECTIONS.md) — the five actions the whole build is made of | you understand what "bend the cathode onto the next pad" means |
| **Learn the meter** | [`MULTIMETER.md`](MULTIMETER.md) | you can tell a cold joint from a good one |
| **Practise** | [`SOLDERING.md`](SOLDERING.md) §4, six exercises on a spare kit board | shiny joint first try, every try |
| **Pre-flight** | [`BUILD.md`](BUILD.md) P1–P5 | parts confirmed, board confirmed, sockets cut |
| **Step 1** | the ESP32 socket | `firmware/blink` runs |
| **Step 2** | first GND bus + the ground wire | the bus beeps end to end |
| **Step 3** | LEDs, resistors, their 4 wires | `firmware/ledtest` — all four cycle |
| **Step 4** | colour buttons, second bus, the link, 4 wires | `firmware/btntest` prints 0–3 |
| **Step 5** | AA / no / yes, third bus, 3 wires | `btntest` prints 0–6 |
| **Step 6** | the LCD port | `firmware/lcdtest` finds `0x27` |
| **Step 7** | real firmware, then screw it to the wood | the whole thing works |

**Every step ends in a test that exercises what you just built.** Not a beep — a program
that lights the LEDs or prints the button numbers. If a step fails, exactly one thing has
changed since the last one that passed.

---

## The things most likely to bite you

Not a general list — these are the ones that have actually happened on this project.

**A bus wire lying over the hole centres instead of beside them.** The lead you push in
later stops on the wire and never reaches copper, but solder bridges the gap. The joint
looks perfect from underneath and it beeps. **11 joints** on this board are at risk.
`SOLDERING.md` Exercise 4 exists solely to teach you this.

**Several buttons dead at once.** It's the ground bus or the column-1 link — not the
switches. This happened twice on the breadboard.

**Soldering all four legs of a switch.** Don't. **One leg gets clipped off** before you
seat it. On this kit the switch's internally-joined pairs run the long way, which would put
a signal leg straight onto the ground bus. Clipping is safe whichever way your switches
are made.

**Uploading firmware while the daemon is running.** Fails with *"serial noise or
corruption"*, which reads like a hardware fault. Only one process can hold the port — stop
the daemon first.

---

## Everything is generated from one file

`tools/layout.py` holds every row, column and GPIO. The tables in `BUILD.md`, all the
figures, and the verifier all derive from it, so a drawing cannot disagree with a table.

```bash
mise exec -- python tools/verify-layout.py   # checks the design, ~20 assertions
mise exec -- python tools/gen-tables.py      # rebuilds BUILD.md's tables
mise exec -- python tools/gen-wiring.py      # rebuilds WIRING.md, the flat wire list
mise exec -- python tools/schematic.py       # rebuilds the figures
mise exec -- python tools/view-docs.py       # this documentation, in a browser
```

The docs drifted from the layout four times before this existed. The last time, the wire
table would have shorted seven buttons to ground.

**Never hand-edit a row, column or GPIO in a document.** Change `layout.py`, then re-run
those three.

---

Next: [`CONNECTIONS.md`](CONNECTIONS.md).
