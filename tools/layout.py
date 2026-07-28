"""Single source of truth for the board layout.

verify-layout.py, schematic.py and gen-tables.py all import from here. Nothing else
may hard-code a row, a column or a GPIO — every table and every drawing is derived
from this file, so they cannot drift apart again. They already did, four times, and the
last time it would have shorted seven buttons to ground.

MEASURED on the actual kit parts (calipers, not datasheets):
  colored buttons  pins 3 holes ACROSS (2 pitches) x 6 holes LONG (5 pitches)
  small buttons    3x3 holes (2 pitches both ways)
  ESP32            11 holes across (pin rows 1.0in apart) x 15 long
  perfboard        18 rows x 24 cols, 50x70mm, SINGLE-SIDED, 1.0mm holes
"""

# ---- board ----------------------------------------------------------------
P            = 2.54
ROWS, COLS   = 18, 24
BOARD_W, BOARD_H = 70.0, 50.0
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

# ---- board A layout -------------------------------------------------------
LED_COLS = [3, 9, 15, 21]   # LED, its resistor and its button share a column
LED_ROWS = (1, 2)           # anode row 1 (takes the wire), cathode row 2
RES_ROWS = (3, 7)           # resistor in the CATHODE path; the cathode lead bends
                            # over on the copper face to reach the row-3 pad
BTN_COL0 = [c-1 for c in LED_COLS]
BTN_ROWS = (9, 14)          # ground leg lands directly ON the row-14 bus
ANS_COL0 = [3, 11, 19]
ANS_ROWS = (16, 18)         # ground leg lands directly ON the row-18 bus
GND_ROWS = (7, 14, 18)      # one bus per bank -> zero ground jumpers
GND_LINK_COL = 24           # the three buses join down this column
LCD_ON_BOARD_A = False      # LCD wires straight to board B; no 5V on board A

# ---- board B --------------------------------------------------------------
HDR_ROWS = (4, 14)          # 10 apart = the ESP32's 1.0in pin rows
HDR_COLS = (5, 19)          # 15 sockets

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
    """Every wire from board A to board B: (label, board-A hole, ESP32 pin, side, pos)."""
    out = []
    for i, c in enumerate(LED_COLS):
        out.append((f"LED {i+1} {LED_NAME[i]}", f"col {c}, row {LED_ROWS[0]}", f"D{LED_GPIO[i]}"))
    for i, c0 in enumerate(BTN_COL0):
        out.append((f"button {i+1} {LED_NAME[i]}", f"col {c0}, row {BTN_ROWS[0]}", f"D{BTN_GPIO[i]}"))
    for (n, g, d), c0 in zip(ANS_INFO, ANS_COL0):
        out.append((f"{n} ({d})", f"col {c0}, row {ANS_ROWS[0]}", f"D{g}"))
    out.append(("ground", f"any GND bus (row {GND_ROWS[0]}/{GND_ROWS[1]}/{GND_ROWS[2]})", "GND"))
    return [(lbl, src, pin) + esp_position(pin) for lbl, src, pin in out]


def lcd_harness():
    """The LCD's four wires — they go to board B, never to board A."""
    return [(f"LCD {a}", "F-M jumper onto the LCD's own header", b if b == "GND" else
             ("VIN" if b == "VIN" else f"D{b}")) for a, b in LCD_PINS]
