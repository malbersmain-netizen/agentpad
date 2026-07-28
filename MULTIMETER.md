# Using the multimeter, from zero

Written for this build. The meter is the single most useful tool here — nearly every
failure in a project like this is a cold joint or an invisible bridge, and both are
silent until you beep them.

Everything in this document is done with **nothing plugged in and no power anywhere**.
The meter supplies a couple of milliamps of its own; you cannot hurt yourself or the parts.

---

## 1. Set it up — once

**Two jacks matter.**

```
   ┌──────────────────────┐
   │   [ 10A ]  [ VΩmA ]  │   ← red lead here
   │           [  COM  ]  │   ← black lead here, always
   └──────────────────────┘
```

- **Black → COM.** It never moves.
- **Red → VΩmA** (may read `VΩ`, `mAVΩ`, or `+`).
- **Never the 10A jack.** That jack is for measuring current and is a dead short across
  the probes. It is the classic first-day mistake.

**Three dial positions:**

| Symbol | Name | Used for |
|---|---|---|
| `•)))` sound waves | **continuity** | joints, buses, buttons — beeps when two points are connected |
| `▶\|` arrow into a bar | **diode** | LEDs — which way current flows, and is it alive |
| `Ω` | **resistance** | the 220Ω resistors |

On most cheap meters **continuity and diode share one dial position**. Land on it, then
press `MODE` / `SELECT` to cycle. The little symbol in the corner of the display tells you
which mode you are actually in.

---

## 2. Prove the meter works before you trust it

Dial to continuity. **Touch the probe tips together.**

- Beeps continuously, reads near `0.0` / `000`.
- Pull apart: silence, display shows **`OL`** or **`1.`**

`OL` means *open loop* — no connection. It is the reading you will see most of the time
and it is not an error.

No beep with the tips touching → flat battery, or the red lead is in the wrong jack.

---

## 3. Testing a tactile switch — pre-flight P1

A 4-leg tactile switch is **two pairs**. The legs within a pair are joined permanently;
pressing connects one pair to the other.

**Which pair is which varies by part.** On this kit's switches, the joined pairs run the
**long way, down the columns** — measured, not assumed. An early draft of this layout
assumed the opposite and would have shorted all seven buttons to ground.

**The board no longer depends on it.** The build clips one leg off every switch, and
`verify-layout.py` proves the remaining three work whichever way the pairs run. So this
test is now just confirming the parts are alive and behave like switches.

**The test:**

1. Continuity mode. One spare colored switch, one spare small switch.
2. Beep all six leg pairings **without pressing**.
3. Press and hold, then beep any pair that was silent.

Doing it systematically beats free-handing it: **clip the black lead to one leg** and touch
red to the other three, then move the clip to the next leg. That covers all six pairs with
one lead never moving.

| Result | Meaning |
|---|---|
| **Exactly two pairs beep unpressed; all four beep pressed** | Normal. Use it |
| Only one pair beeps | Probe slipped, or a leg is lacquered — scrape it and retry. If it repeats, the switch is faulty |
| Three or more pairs beep unpressed | Shorted internally. Discard it |
| Nothing changes when pressed | Dead switch, or you are not pressing hard enough to latch it |

You do **not** need to record which pair is which, and the square small buttons do **not**
need marking — the signal leg and the clipped leg are defined by *position on the board*,
not by the switch's internals. Any orientation works.

---

## 4. Testing an LED — pre-flight P3

**Diode mode `▶|`, not continuity.** Continuity mode does not push enough voltage through
an LED to tell you anything.

1. **Red probe on the long leg** (anode), **black on the short leg** (cathode).
2. Reads roughly `1.8`–`2.4` for red/yellow, `2.6`–`3.2` for green/blue — the forward
   voltage. **The LED glows faintly**, lit by the meter's own test current.
3. **Swap the probes.** Now it reads `OL`.

That is a good LED, and it identifies the legs: **the leg on the red probe when it lights
is the anode**, and that is the one that goes in row 2.

> **Both directions `OL` on a blue LED?** Suspect the meter, not the LED. Some cheap meters
> only push ~2.5V in diode mode, below a blue LED's forward voltage. Test a red one first
> to confirm your technique before condemning a blue one.

---

## 5. Testing a resistor — pre-flight P2

Dial to **`Ω`**. Manual-ranging meter: pick the `2k` range.

Probe both ends — resistors are not polarised, direction does not matter. You want
**209–231Ω**. It may read `218` or `0.218` depending on range.

Bands are **red · red · brown · gold**. ~100Ω means you grabbed brown-black-brown;
~2.2kΩ means red-red-red. Both "work" but the LEDs end up too bright or too dim.

---

## 6. The three checks you will repeat all build

Once soldering starts, these three are most of the debugging:

**Is this joint actually connected?** Continuity. One probe on the component lead *above*
the board, one on the pad below. Beeps = the solder wetted both. Silent = cold joint,
reflow it with flux.

**Is this bus continuous?** Continuity. Probe the two far ends of the bus. Then probe a few
holes along it. All should beep to each other.

**Did I bridge something?** Continuity. Probe each GND bus against the signal row next to
it. **It must never beep.** Do this after every stage — a bridge found now is one joint to
fix; found later it is thirty joints to search.

> **The trap that beeps clean and still fails:** a bus wire lying *over* the hole centres
> instead of beside them. A lead pushed in from the top stops on the wire and never reaches
> copper, but the solder bridges the gap and the joint looks perfect from underneath, and
> beeps. That is why `SOLDERING.md` Exercise 4 has you push a lead through a bussed hole and
> confirm it reaches the copper face.

---

## 7. What the display is telling you

| Shows | Means |
|---|---|
| `OL` or `1.` on the left | Open — no connection. Normal most of the time |
| `0.0` and beeping | Connected |
| `0.4`–`2.0` and beeping weakly | Connected but resistive — usually a cold joint |
| Numbers drifting around | Probes not making firm contact; press harder or scrape the flux off |
| Reading changes when you press on a joint | **Cold joint.** Reflow it |

---

Next: the six soldering exercises in [`SOLDERING.md`](SOLDERING.md), then the pre-flight
section of [`BUILD.md`](BUILD.md).
