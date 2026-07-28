# How you actually connect things

Read this once before `BUILD.md`. Everything in that document is one of the five moves
below, repeated. If these make sense, the build is just following a list.

---

## The one idea everything rests on

**A perfboard hole is an island.**

Each hole has a ring of copper around it — a **pad**. (Your board is double-sided, so
there is a pad on each face; we solder on one face throughout, which keeps things simple
and means the design works whether or not the holes are plated through.) Pads are not connected to each other. Not to the one next door, not to the one
across the board. **Nothing is connected to anything until you connect it.**

That's the whole difference from a breadboard, where the plastic hides little metal clips
that join each row of five holes for you. Perfboard has none of that. You are the wiring.

```
   TOP  (components live here)          UNDERSIDE (every joint made here)

   ┌───────────────────────┐            ┌───────────────────────┐
   │  ◎   ◎   ◎   ◎   ◎    │            │  ◎   ◎   ◎   ◎   ◎    │  ◎ = copper pad
   │  ◎   ◎   ◎   ◎   ◎    │            │  ◎   ◎   ◎   ◎   ◎    │
   └───────────────────────┘            └───────────────────────┘
     pads here too — we ignore them       every pad isolated
```

> **"The copper face" means nothing on this board.** Yours is **double-sided**: there is a
> pad on *both* faces of every hole. That phrase was left over from the single-sided kit
> boards. Throughout these documents, **"the underside" means the face you solder on** —
> the one facing away from the components — and **every joint in this build is made there**,
> including all three ground buses. The top pads are simply left bare.
>
> Why one face? Because then the design doesn't care whether your holes are plated through.
> If they are, a joint underneath also reaches the top pad — a bonus, not a requirement.

So when the build sheet says *"LED 1 anode, col 4 row 2 → D13"*, that means: the LED's long
leg goes through the hole at column 4, row 2, and **you** run a wire from that pad to the
D13 pad at the ESP32 socket. Nothing happens automatically.

---

## Move 1 — put a component in and solder it

The basic action. Everything else is a variation.

1. **From the TOP**, push the component's legs down through its holes.
2. Turn the board over. The legs stick out through the pads.
3. **Splay each leg outward ~30°** so the part can't fall out while you work.
4. Touch the iron so it heats **the pad and the leg at the same time**, ~2 seconds.
5. Feed solder **into the joint** — not onto the iron. It flows and wets flat.
6. Solder away first, then the iron. Don't move it while it cools.
7. **Snip the leg flush** with flush cutters.

```
   side view, mid-solder

      component body
   ═════╤═══════╤═════   ← top face
        │       │
   ─────┴───────┴─────   ← board
        ▲       ▲
     ╱▔▔▔╲   ╱▔▔▔╲       ← solder fillet: shiny, concave, volcano-shaped
     leg      leg
```

That is one **joint**. This build has about 149 of them.

---

## Move 2 — a bare wire that joins a whole row (a "bus")

Ground has to reach 11 different legs — four resistor bottoms, four colour-button
ground legs and three answer-button ground legs. Running 11 separate wires would be
miserable, so
instead you lay **one bare wire along a row of pads and solder it to each one**. That turns
a row of islands into a single connected node. That node is called a **bus**.

This board has **three GND buses**, joined to each other down **column 1**. Anything that
needs ground just has to reach the nearest bus.

> **Why column 1 and not the right-hand end?** The link is *bare* wire. Every signal wire
> on this board leaves its component at column 3 or higher and runs *right*, toward the
> ESP32 — so the far-left column is the one line none of them cross. When the link lived at
> column 28, all seven button and answer wires ran straight over it, each one a nicked
> insulator away from a dead short. `verify-layout.py` now fails if that ever comes back.

**How to lay one:**

1. Cut a bare (or tinned) wire a bit longer than the row. **24AWG**, not 22 — thinner is
   far easier to heat.
2. Lay it on the **underside**, along the row of pads.
3. ⚠️ **Beside the hole centres, not across them.** Tangent to the pads, so the holes stay
   clear.
4. Tack one end. Check it's straight. Solder it to every second or third pad.

```
   underside, looking at a bus row

   ◎───◎───◎───◎───◎───◎     ← RIGHT: wire runs beside the pads, holes clear
   ═══════════════════════

   ◉═══◉═══◉═══◉═══◉═══◉     ← WRONG: wire over the hole centres.
                                A lead pushed down later hits it and stops.
```

**Why that matters so much:** if the wire covers the hole, a component lead pushed in later
never reaches the copper — but solder still bridges the gap and **the joint looks perfect
from underneath**. Eighteen joints on this board could fail that way, invisibly.

**Consequence for the build order:** rows 16 and 21 carry a bus *and* button legs. On those
rows, **fit the buttons first**, bend their ground legs flat along the row, then lay the bus
on top of the bent legs and solder once. Only row 8 is empty enough to bus first.

---

## Move 1b — clipping a leg you must NOT fit

Every tactile switch on this board goes in with **three legs, not four.** The fourth — the
one in the signal column on the ground-bus row — gets snipped flush with the body before
the switch is seated.

The reason is that a switch's two internally-joined pairs may run along its short axis or
its long axis depending on the part, and this kit's run the long way. If they do, that
fourth leg is on the *signal* node, and dropping it onto the ground bus welds the button
closed. Clipping it is correct either way, so the board does not care which switch you
bought. `tools/verify-layout.py` simulates both pairings and fails if the design ever
assumes all four legs can be fitted.

Three legs is plenty of anchoring for a part this size.

---

## Move 3 — bending a leg to reach a neighbouring pad

Used once per LED. The LED's cathode is in row 3 and its resistor's top lead is in row 4 —
next-door pads that must be joined.

Rather than adding a wire, **use the LED's own leg**:

1. Solder the LED's cathode in its own hole as normal, **but don't snip it**.
2. Bend the leftover length flat along the underside until it lies on the row-3 pad.
3. Solder it there too — same joint as the resistor lead.
4. Now snip.

```
   underside

   row 3  ◎  ← LED cathode soldered here
          │
          ╰──╮   leg bent flat along the underside
   row 4  ◎◄─╯  ← and soldered onto this pad, where the resistor already sits
```

An LED leg is ~20mm; you need 2.54mm. There's plenty.

> **Why not just put both leads in the same hole?** A hole is 1.0mm; two leads are ~1.25mm
> side by side, and there'd be no room left for solder. **One lead per hole, always.**

---

## Move 4 — a signal wire across the board

Sixteen of these — 12 from the control surface to the ESP32 socket, and 4 more from the
LCD port to the socket. All identical:

1. Cut 22AWG solid wire, generously long — you can always shorten.
2. **Strip ~4mm** off each end.
3. **Tin both ends**: melt a little solder into the bare copper so it turns silver. Tinned
   wire slides into a joint predictably; untinned wire frays and wanders.
4. Push one end down through its hole **from the top**, solder underneath, snip.
5. Do the same at the far end, into the pad under the ESP32 socket pin it serves.

> **Label both ends before you solder the second one.** Sixteen identical wires become
> indistinguishable the moment they're in a bundle. Masking-tape flags with the signal
> name.

**The LCD's own four wires are not soldered.** They're F-F jumpers from the LCD's header to
the board's 4-pin **LCD port** — a male header at cols 30–33, row 2. The port exists because
the ESP32's pins disappear inside the socket the moment the module is seated, so there is
nothing left to clip a jumper onto. The port's four *wires* (port → socket pads) are soldered
like any other; the LCD itself just plugs in.

---

## Move 5 — soldering a wire onto a pad that already has a pin in it

Each signal wire lands on a pad that already holds a socket pin. You don't need a free
hole — **you solder the wire onto the pin's existing joint**.

First, the thing people expect and shouldn't: **you do not add a male pin to the socket.**
The female strip is an ordinary component. It sits on top, its own pins come through the
board, and you solder those to the pads underneath. That's the whole joint.

```
   TOP        ┌──────────┐  ← female socket strip. The ESP32 plugs in HERE, later.
              │ ⌷ ⌷ ⌷ ⌷ │
   ═══════════╪═╪═╪═╪═══╪═══  ← the board
              │ │ │ │
   UNDERSIDE  ▼ ▼ ▼ ▼   ← the strip's own pins poke through. THIS is what you solder,
             ╱▔╲            and later what each signal wire laps onto.
```

Then, for each wire:

1. Do all 30 socket joints first.
2. Lay the tinned wire end against the target pin's solder blob — or hook it around the
   2mm stub, if you left one there (`BUILD.md` step 1 says which 16 pads to leave stubs on).
3. Touch the iron to both until the existing solder melts and takes the wire.
4. Remove the iron, hold still 2 seconds.

That's called a *lap joint* and it's completely normal. One joint, holding two things.

---

## Putting it together — one LED, start to finish

Every part of the build is these moves in sequence. Here's LED 1 in full:

| # | Move | What you do |
|---|---|---|
| 1 | Move 1 | LED long leg (+) into **col 4, row 2**; short leg (−) into **col 4, row 3** |
| 2 | Move 1 | 220Ω into **col 4, row 4** and **col 4, row 8** |
| 3 | Move 3 | Bend the LED's cathode leg from row 3 onto the row-4 pad and solder |
| 4 | Move 2 | The resistor's bottom lead is in row 8 — **that row is a GND bus**, so it's grounded the moment the bus is on |
| 5 | Move 4 | Wire from **col 4, row 2** to the **D13** pad at the ESP32 socket (col 30, row 10) — both ends are lap joints, Move 5 |

Follow the current: **D13 → wire → LED anode → through the LED → cathode → bent leg →
resistor → GND bus → back to the ESP32's GND.** Every step is a connection you made.

---

## The mental checklist for any connection

Before you solder anything, ask:

1. **Which two pads am I joining?**
2. **What joins them** — a component lead, a bent leg, a bus, or a wire?
3. **Is either pad already part of a bus?** If so, it's already connected to everything else
   on that bus. Ground legs land *on* a bus deliberately; signal legs must never touch one.

That third question is the one that bites. A signal leg landing on a ground bus is a dead
short, and it looks completely normal.

---

Next: [`SOLDERING.md`](SOLDERING.md) to practise the moves, then [`BUILD.md`](BUILD.md) to
do them in order.
