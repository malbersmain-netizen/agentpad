# Wiring reference

**Generated from `tools/layout.py` — do not edit.** Re-run `mise exec -- python tools/gen-wiring.py` after any layout change.

Board: 30 rows × 42 columns, 120 × 80 mm. Grid reference col 1, row 1 = top-left, viewed from the **component side**.

ESP32 seated with **USB pointing at the bottom edge**. Pin positions are counted **from the USB end**, so position 1 is the bottom socket (row 22) and position 15 is the top (row 8). The **3V3 column is board col 40** (nearest the controls); the **VIN column is col 30**.

---

## A. Every wire

**12 soldered signal/ground wires + 4 LCD-port wires = 16 total.**

| # | Wire | From — hardware | From — hole | To — socket hole | ESP32 pin | Slot |
|---:|---|---|---|---|---|---|
| 1 | LED 1 red | LED 1 (red) anode, long leg | col 4, row 2 | **col 30, row 20** | `D13` | VIN side, pos 3 |
| 2 | LED 2 green | LED 2 (green) anode, long leg | col 11, row 2 | **col 30, row 18** | `D14` | VIN side, pos 5 |
| 3 | LED 3 blue | LED 3 (blue) anode, long leg | col 18, row 2 | **col 30, row 17** | `D27` | VIN side, pos 6 |
| 4 | LED 4 yellow | LED 4 (yellow) anode, long leg | col 25, row 2 | **col 30, row 16** | `D26` | VIN side, pos 7 |
| 5 | button 1 red | Button 1 (red) signal leg | col 3, row 11 | **col 30, row 13** | `D32` | VIN side, pos 10 |
| 6 | button 2 green | Button 2 (green) signal leg | col 10, row 11 | **col 30, row 14** | `D33` | VIN side, pos 9 |
| 7 | button 3 blue | Button 3 (blue) signal leg | col 17, row 11 | **col 30, row 15** | `D25` | VIN side, pos 8 |
| 8 | button 4 yellow | Button 4 (yellow) signal leg | col 24, row 11 | **col 40, row 18** | `D4` | 3V3 side, pos 5 |
| 9 | AA (always allow) | 'AA' switch signal leg | col 4, row 19 | **col 40, row 8** | `D23` | 3V3 side, pos 15 |
| 10 | no (deny) | 'no' switch signal leg | col 13, row 19 | **col 40, row 14** | `D18` | 3V3 side, pos 9 |
| 11 | yes (approve) | 'yes' switch signal leg | col 22, row 19 | **col 40, row 13** | `D19` | 3V3 side, pos 10 |
| 12 | ground | GND bus (row 8) | col 28, row 8 | **col 40, row 21** | `GND` | 3V3 side, pos 2 |
| — | LCD GND | LCD port socket | col 30, row 2 | **col 30, row 21** | `GND` | VIN side, pos 2 |
| — | LCD VCC | LCD port socket | col 31, row 2 | **col 30, row 22** | `VIN` | VIN side, pos 1 |
| — | LCD SDA | LCD port socket | col 32, row 2 | **col 40, row 12** | `D21` | 3V3 side, pos 11 |
| — | LCD SCL | LCD port socket | col 33, row 2 | **col 40, row 9** | `D22` | 3V3 side, pos 14 |

> The LCD itself is **not** on this list — it reaches the port with 4 F-M jumpers and is never soldered.

---

## B. The ESP32 socket, slot by slot

All 30 sockets. **16 carry a wire**, the rest are soldered but unused. Leave a 2mm stub on the ones marked ●; trim the others flush.

### 3V3 side — board column 40

| Pos | Pin | Board hole | | Connected to |
|---:|---|---|:-:|---|
| 1 | 3V3 | col 40, row 22 | | *unused — trim flush* |
| 2 | **GND** | col 40, row 21 | ● | wire 12 — ground, from col 28, row 8 |
| 3 | D15 | col 40, row 20 | | *unused — trim flush* |
| 4 | D2 | col 40, row 19 | | *unused — trim flush* |
| 5 | **D4** | col 40, row 18 | ● | wire 8 — button 4 yellow, from col 24, row 11 |
| 6 | RX2 | col 40, row 17 | | *unused — trim flush* |
| 7 | TX2 | col 40, row 16 | | *unused — trim flush* |
| 8 | D5 | col 40, row 15 | | *unused — trim flush* |
| 9 | **D18** | col 40, row 14 | ● | wire 10 — no (deny), from col 13, row 19 |
| 10 | **D19** | col 40, row 13 | ● | wire 11 — yes (approve), from col 22, row 19 |
| 11 | **D21** | col 40, row 12 | ● | LCD SDA, from LCD port, col 32 row 2 |
| 12 | RX0 | col 40, row 11 | | *unused — trim flush* |
| 13 | TX0 | col 40, row 10 | | *unused — trim flush* |
| 14 | **D22** | col 40, row 9 | ● | LCD SCL, from LCD port, col 33 row 2 |
| 15 | **D23** | col 40, row 8 | ● | wire 9 — AA (always allow), from col 4, row 19 |

### VIN side — board column 30

| Pos | Pin | Board hole | | Connected to |
|---:|---|---|:-:|---|
| 1 | **VIN** | col 30, row 22 | ● | LCD VCC, from LCD port, col 31 row 2 |
| 2 | **GND** | col 30, row 21 | ● | LCD GND, from LCD port, col 30 row 2 |
| 3 | **D13** | col 30, row 20 | ● | wire 1 — LED 1 red, from col 4, row 2 |
| 4 | D12 | col 30, row 19 | | *unused — trim flush* |
| 5 | **D14** | col 30, row 18 | ● | wire 2 — LED 2 green, from col 11, row 2 |
| 6 | **D27** | col 30, row 17 | ● | wire 3 — LED 3 blue, from col 18, row 2 |
| 7 | **D26** | col 30, row 16 | ● | wire 4 — LED 4 yellow, from col 25, row 2 |
| 8 | **D25** | col 30, row 15 | ● | wire 7 — button 3 blue, from col 17, row 11 |
| 9 | **D33** | col 30, row 14 | ● | wire 6 — button 2 green, from col 10, row 11 |
| 10 | **D32** | col 30, row 13 | ● | wire 5 — button 1 red, from col 3, row 11 |
| 11 | D35 | col 30, row 12 | | *unused — trim flush* |
| 12 | D34 | col 30, row 11 | | *unused — trim flush* |
| 13 | VN | col 30, row 10 | | *unused — trim flush* |
| 14 | VP | col 30, row 9 | | *unused — trim flush* |
| 15 | EN | col 30, row 8 | | *unused — trim flush* |

---

## C. Every component, every leg

Legs that are **not** on this list do not exist — they were clipped off.

| Part | Leg | Hole | What it connects to |
|---|---|---|---|
| **LED 1 (red)** | anode, long leg (+) | col 4, row 2 | wire 1 → `D13` |
| | cathode, short leg (−) | col 4, row 3 | bent flat on the underside onto the row-4 pad |
| **220Ω R1** | top lead | col 4, row 4 | joins that bent cathode leg |
| | bottom lead | col 4, row 8 | lands **on the GND bus** |
| **LED 2 (green)** | anode, long leg (+) | col 11, row 2 | wire 2 → `D14` |
| | cathode, short leg (−) | col 11, row 3 | bent flat on the underside onto the row-4 pad |
| **220Ω R2** | top lead | col 11, row 4 | joins that bent cathode leg |
| | bottom lead | col 11, row 8 | lands **on the GND bus** |
| **LED 3 (blue)** | anode, long leg (+) | col 18, row 2 | wire 3 → `D27` |
| | cathode, short leg (−) | col 18, row 3 | bent flat on the underside onto the row-4 pad |
| **220Ω R3** | top lead | col 18, row 4 | joins that bent cathode leg |
| | bottom lead | col 18, row 8 | lands **on the GND bus** |
| **LED 4 (yellow)** | anode, long leg (+) | col 25, row 2 | wire 4 → `D26` |
| | cathode, short leg (−) | col 25, row 3 | bent flat on the underside onto the row-4 pad |
| **220Ω R4** | top lead | col 25, row 4 | joins that bent cathode leg |
| | bottom lead | col 25, row 8 | lands **on the GND bus** |
| **Button 1 (red)** | signal | col 3, row 11 | wire 5 → `D32` |
| | anchor | col 5, row 11 | soldered, no connection |
| | ~~clipped~~ | ~~col 3, row 16~~ | **cut this leg off** |
| | ground | col 5, row 16 | lands **on the GND bus** |
| **Button 2 (green)** | signal | col 10, row 11 | wire 6 → `D33` |
| | anchor | col 12, row 11 | soldered, no connection |
| | ~~clipped~~ | ~~col 10, row 16~~ | **cut this leg off** |
| | ground | col 12, row 16 | lands **on the GND bus** |
| **Button 3 (blue)** | signal | col 17, row 11 | wire 7 → `D25` |
| | anchor | col 19, row 11 | soldered, no connection |
| | ~~clipped~~ | ~~col 17, row 16~~ | **cut this leg off** |
| | ground | col 19, row 16 | lands **on the GND bus** |
| **Button 4 (yellow)** | signal | col 24, row 11 | wire 8 → `D4` |
| | anchor | col 26, row 11 | soldered, no connection |
| | ~~clipped~~ | ~~col 24, row 16~~ | **cut this leg off** |
| | ground | col 26, row 16 | lands **on the GND bus** |
| **'AA' (always allow)** | signal | col 4, row 19 | wire 9 → `D23` |
| | anchor | col 6, row 19 | soldered, no connection |
| | ~~clipped~~ | ~~col 4, row 21~~ | **cut this leg off** |
| | ground | col 6, row 21 | lands **on the GND bus** |
| **'no' (deny)** | signal | col 13, row 19 | wire 10 → `D18` |
| | anchor | col 15, row 19 | soldered, no connection |
| | ~~clipped~~ | ~~col 13, row 21~~ | **cut this leg off** |
| | ground | col 15, row 21 | lands **on the GND bus** |
| **'yes' (approve)** | signal | col 22, row 19 | wire 11 → `D19` |
| | anchor | col 24, row 19 | soldered, no connection |
| | ~~clipped~~ | ~~col 22, row 21~~ | **cut this leg off** |
| | ground | col 24, row 21 | lands **on the GND bus** |
| **LCD port** | pin 1 — GND | col 30, row 2 | wire to `GND` at col 30, row 21 |
| **LCD port** | pin 2 — VCC | col 31, row 2 | wire to `VIN` at col 30, row 22 |
| **LCD port** | pin 3 — SDA | col 32, row 2 | wire to `D21` at col 40, row 12 |
| **LCD port** | pin 4 — SCL | col 33, row 2 | wire to `D22` at col 40, row 9 |

---

## D. The buses

| Bus | Row | Spans | Carries |
|---|---:|---|---|
| GND | **8** | cols 1 → 28 | the four 220Ω bottom leads |
| GND | **16** | cols 1 → 28 | the four colour-button ground legs |
| GND | **21** | cols 1 → 28 | the three answer-button ground legs |

All three are joined by a bare wire down **column 1**, rows 8–21. One wire (#12) carries ground from col 28, row 8 to the ESP32's `GND` at col 40, row 21. There are **no other ground connections** — every ground leg sits directly on a bus.

