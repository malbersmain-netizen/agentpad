# Learning to solder, from zero

Written for this build specifically. You have never soldered; by the end of section 4 you
will have made ~30 practice joints and will be ready to touch the real board.

Budget **one hour of practice** before you start. It is the highest-return hour in the
whole project — a beginner who practises first builds this in an evening; one who doesn't
spends the evening debugging cold joints.

---

## 1. Before this: how connections work

**Perfboard has no wires in it.** Every hole is an island; nothing is joined until you join
it. That single fact drives the whole design.

**→ [`CONNECTIONS.md`](CONNECTIONS.md) explains the five moves** you'll use to join things:
putting a part in, laying a bus, bending a leg to a neighbouring pad, running a wire
between boards, and soldering onto an existing joint.

Read it first. This document teaches your hands; that one teaches the plan.

---

## 1b. And the other tool you cannot skip

**→ [`MULTIMETER.md`](MULTIMETER.md)** — the jacks, continuity vs diode mode, and the three
checks you will repeat on every joint in this build. If you have never used a meter, read it
before Exercise 1; several exercises below end in "beep it".

---

## 2. Safety, briefly

- The iron is ~340°C. It looks identical hot and cold. **Park it in its stand every time.**
- Solder fumes are flux, not lead — still, work near an open window or a fan.
- Leaded solder: don't eat while working, wash hands after.
- Never "flick" solder off the iron; wipe it on brass wool or a damp sponge.
- Trimmed leads fly. Cup your hand over the cutters or wear glasses.

---

## 3. Setting up

1. **Tin the tip immediately** when it reaches temperature: melt a little solder onto it,
   wipe on brass wool. A shiny silver tip transfers heat; a dull grey one barely does.
   Re-tin every few minutes. **A dirty tip is the #1 cause of "my solder won't melt".**
2. Set the iron to **~340°C** for leaded solder.
3. Board held in helping hands or taped down. You need both hands free.
4. Solder in your dominant hand, iron in the other. Yes, really — the iron just sits there,
   the solder does the moving.

---

## 4. Practice — do these on a spare kit board

You have three boards. **Sacrifice most of one.** Work through these in order; each takes
a few minutes.

### Exercise 1 — wet a pad (×10)
Touch the iron to a copper ring for one second, feed solder in, remove. Aim for a small
shiny dome. Repeat on ten holes.
*Learning:* how fast solder melts, and what "flowing" looks like.

### Exercise 2 — solder a wire into a hole (×5)
Push a wire offcut through, heat the pad **and** the wire together, feed solder, remove
solder then iron. Trim flush.
*Pass:* the joint is shiny and cone-shaped, and the wire doesn't wiggle.

### Exercise 3 — make a bridge on purpose, then remove it (×3)
Solder two adjacent pads so they merge. Now remove it: lay desoldering braid over the
blob, press the iron on top, watch the solder wick into the braid.
*Learning:* mistakes are undoable. This removes most of the fear.

### Exercise 4 — a bus (×1, the important one)
Lay a bare wire across ten holes in a row — **beside the hole centres, not over them**,
tangent to the pads. Tack one end, check it's straight, solder every second pad.
*Pass:* multimeter beeps between all ten holes.

Now the part that matters: **push a component lead down through one of those holes from
the top.** It must reach the copper face and sit alongside the wire. If your bus is lying
*over* the hole, the lead stops at the board and connects to nothing — and the joint still
looks perfect from underneath. That single mistake would hit **11 joints** on the real
board.

> On the real board, rows that carry a bus get their **components inserted first**. Bend
> the ground leads flat along the row on the copper face, lay the bus wire on top of them,
> and solder once. Bus-first only works on rows with nothing else in them.

### Exercise 5 — a resistor and an LED (×2)
Stand a resistor in two holes, bend the leads to hold it, solder, trim. Then an LED:
**long leg = +**. Solder, then check the LED still points straight up.
*Learning:* parts move while you solder. Tack one leg, correct the alignment, then do the rest.

### Exercise 6 — a header strip (×1)
Solder a 5-pin piece of female header. Tack **one** pin, check it sits flat and square,
then do the rest.
*Learning:* headers tilt if you solder both ends first. This is exactly Step 1 of the build.

**You are ready when Exercise 2 produces a shiny joint first try, every try.**

---

## 5. The motion, precisely

1. **Heat both** — iron touches the pad *and* the lead at once. ~2 seconds.
2. **Feed solder into the joint** — never onto the iron tip. It should flow instantly and
   wick flat around the lead.
3. **Solder away first, then the iron.**
4. **Don't move it** for ~2 seconds while it solidifies.
5. **Trim** the lead flush once cool.

**Total iron contact: 2–4 seconds.** Longer than 5 lifts the copper pad off the board — a
permanent injury to that hole.

> If it isn't flowing, **stop**. Add flux, re-tin the tip, try again. Holding the iron
> there harder never works; it just cooks the part.

---

## 6. Reading a joint

| Looks like | Verdict | Fix |
|---|---|---|
| Shiny, concave, volcano around the lead | Good | — |
| Dull, grey, blobby ball | **Cold joint** — the classic failure | Add flux, reheat until it flows flat |
| Solder spanning two pads | **Bridge** | Desoldering braid |
| Pad barely covered, lead visible | Starved | Reheat, add a little solder |
| Ring of copper lifted off the board | Lifted pad | That hole is dead — use a neighbour and a jumper |

**Cold joints are the enemy.** They often *look* connected and even test connected when
cold, then fail intermittently. If something works when you press on it, it's a cold joint.

---

## 7. Habits that prevent most problems

- **Solder the lowest parts first** so the board still lies flat — but see the bus rule
  below: on a row that carries a bus, the components go in *before* the bus wire.
- **Tack one leg, verify, then finish.** Applies to every multi-leg part.
- **Beep every new joint** with the multimeter before moving on.
- **After every stage, beep each GND bus against the neighbouring signal rows.** They must
  never beep. If they do you've bridged something — find it now, not ten joints later.
  (The control surface carries no 5V at all, so the classic GND↔5V check belongs at the
  ESP32 socket, between its VIN and GND pads.)
- **Trim leads as you go.** Long leads touch each other and create shorts you can't see.
- Wipe the tip before every joint. Two seconds, saves minutes.

---

## 8. When it goes wrong

| Symptom | Almost always |
|---|---|
| Solder won't melt / balls up | Dirty or cold tip — re-tin it |
| Joint dull and lumpy | Not enough heat *on the pad* — you heated only the lead |
| Part falls out while soldering | Bend the leads out slightly to hold it before soldering |
| Two things connected that shouldn't be | Bridge — braid it off |
| Nothing works after adding one part | Beep the GND bus against its neighbouring signal row |
| Several buttons dead at once | The **ground bus**, not the switches (this happened twice on the breadboard) |
| A joint works when pressed | Cold joint — reflow it |

---

## 9. Worth watching before you start

- [SparkFun — How to Solder: Through-Hole Soldering](https://learn.sparkfun.com/tutorials/how-to-solder-through-hole-soldering/all) — the best single written tutorial; skim the photos of good vs bad joints
- [Adafruit Guide to Excellent Soldering](https://learn.adafruit.com/adafruit-guide-excellent-soldering?view=all) — especially its joint-quality gallery
- [Ladyada's soldering tutorial](https://www.ladyada.net/learn/soldering/thm.html) — short, and links NASA's series

Twenty minutes of these plus the six exercises above and you'll be ahead of most people
who've soldered a dozen kits.

---

## 10. Then build

Follow `BUILD.md` section 5. Every step ends in a test with a pass condition — do not
carry on past a failing one. The order exists so that when something breaks, exactly one
thing has changed.

Open the figures alongside it:

```bash
mise exec -- python tools/schematic.py        # schematic + a figure per solder step
mise exec -- python tools/view-plan.py        # tickable checklist
```
