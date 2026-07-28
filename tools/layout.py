"""Single source of truth for the board layout.

verify-layout.py, schematic.py and gen-tables.py all import from here. Nothing else
may hard-code a row, a column or a GPIO — every table and every drawing is derived
from this file, so they cannot drift apart again. They already did, four times, and the
last time it would have shorted seven buttons to ground.

MEASURED on the actual kit parts (calipers, not datasheets):
  colored buttons  pins 3 holes ACROSS (2 pitches) x 6 holes LONG (5 pitches)
  small buttons    3x3 holes (2 pitches both ways)
  ESP32            11 holes across (pin rows 1.0in apart) x 15 long
  perfboard        30 rows x 42 cols, ~79x109mm, DOUBLE-SIDED, 1.0mm holes.
                   Everything fits ONE board now, with the ESP32 socketed beside the
                   controls. All joints stay on one face, so the design does not depend
                   on whether the holes are plated through.
"""

# ---- board ----------------------------------------------------------------
P            = 2.54
ROWS, COLS   = 30, 42          # the double-sided board: 42 across, 30 down
BOARD_W, BOARD_H = 109.0, 79.0
HOLE_D       = 1.0     # one lead per hole, never two
BEND         = 1.5     # straight lead between body seal and bend, per end

# ---- component footprints (mm) --------------------------------------------
BIG_LEG_COLS, BIG_LEG_ROWS = 2, 5
SMALL_LEG    = 2
BIG_BODY     = 12.0
SMALL_BODY   = 6.0
LED_D        = 6.0     # 5mm LED INCLUDING its base flange
RES_BODY     = 6.3     # 1/4W body
RES_W        = 2.5

# ---- control surface ------------------------------------------------------
# Control surface lives in columns 1-28; the ESP32 sits in columns 30-40.
LED_COLS = [4, 11, 18, 25]  # 7-col pitch -> 5.8mm between button bodies
LED_ROWS = (2, 3)           # anode row 2 (takes the wire), cathode row 3
RES_ROWS = (4, 8)           # resistor in the CATHODE path; the cathode lead bends
                            # over on the copper face to reach the row-4 pad
BTN_COL0 = [c-1 for c in LED_COLS]
BTN_ROWS = (11, 16)         # ground leg lands directly ON the row-16 bus
ANS_COL0 = [4, 13, 22]
ANS_ROWS = (19, 21)         # ground leg lands directly ON the row-21 bus
GND_ROWS = (8, 16, 21)      # one bus per bank -> zero ground jumpers
GND_LINK_COL = 28           # the three buses join down this column
BUS_COLS = (1, 28)          # buses span the control surface only, not under the ESP32
# The LCD connects by 4 F-M jumpers straight onto the ESP32's own pins — it is never
# soldered, so it stays a reusable part and no 5V ever runs across the control surface.
LCD_SOLDERED = False

# ---- ESP32, same board, columns 30-40 -------------------------------------
HDR_COLS = (30, 40)         # 10 apart = the ESP32's 1.0in pin rows
HDR_ROWS = (8, 22)          # 15 sockets running down
# The ESP32's LEFT silkscreen column sits at board column 30 -- the side nearest the
# controls -- so the 8 left-hand signals get the short runs.
HDR_SIDE_COL = {"LEFT": HDR_COLS[0], "RIGHT": HDR_COLS[1]}


def socket_hole(side, pos):
    """Board hole for an ESP32 pin: position 1 is the top of the socket."""
    return HDR_SIDE_COL[side], HDR_ROWS[0] + (pos - 1)

# ---- electrical -----------------------------------------------------------
LED_GPIO  = [13, 14, 27, 26]
BTN_GPIO  = [32, 33, 25, 4]
LED_NAME  = ["red", "green", "blue", "yellow"]
ANS_INFO  = [("AA", 23, "always allow"), ("no", 18, "deny"), ("yes", 19, "approve")]
LCD_PINS  = [("GND", "GND"), ("VCC", "VIN"), ("SDA", "21"), ("SCL", "22")]

# ESP32 silkscreen order, position 1 = top, USB at the bottom (MEASURED)
ESP_LEFT  = ["VIN","GND","D13","D12","D14","D27","D26","D25","D33","D32","D35","D34","VN","VP","EN"]
ESP_RIGHT = ["3V3","GND","D15","D2","D4","RX2","TX2","D5","D18","D19","D21","RX0","TX0","D22","D23"]

COL  = ["#c0392b", "#2e7d32", "#1565c0", "#b8860b"]
ANSC = ["#8a5a12", "#37474f", "#0f6b52"]


def esp_position(pin):
    """Where a pin physically sits: ('LEFT'|'RIGHT', 1..15)."""
    if pin in ESP_LEFT:  return "LEFT",  ESP_LEFT.index(pin) + 1
    if pin in ESP_RIGHT: return "RIGHT", ESP_RIGHT.index(pin) + 1
    raise KeyError(pin)


def harness():
    """Every wire from the control surface to the ESP32's socket, all on one board."""
    out = []
    for i, c in enumerate(LED_COLS):
        out.append((f"LED {i+1} {LED_NAME[i]}", f"col {c}, row {LED_ROWS[0]}", f"D{LED_GPIO[i]}"))
    for i, c0 in enumerate(BTN_COL0):
        out.append((f"button {i+1} {LED_NAME[i]}", f"col {c0}, row {BTN_ROWS[0]}", f"D{BTN_GPIO[i]}"))
    for (n, g, d), c0 in zip(ANS_INFO, ANS_COL0):
        out.append((f"{n} ({d})", f"col {c0}, row {ANS_ROWS[0]}", f"D{g}"))
    out.append(("ground", f"any GND bus (rows {', '.join(map(str, GND_ROWS))})", "GND"))
    rows = []
    for lbl, src, pin in out:
        side, pos = esp_position(pin)
        col, row = socket_hole(side, pos)
        rows.append((lbl, src, pin, side, pos, col, row))
    return rows


def lcd_harness():
    """The LCD's four wires — F-M jumpers onto the ESP32's pins, never soldered."""
    return [(f"LCD {a}", "F-M jumper onto the LCD's own header", b if b == "GND" else
             ("VIN" if b == "VIN" else f"D{b}")) for a, b in LCD_PINS]
