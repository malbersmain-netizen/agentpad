"""Single source of truth for the board layout.

verify-layout.py, schematic.py and gen-tables.py all import from here. Nothing else
may hard-code a row, a column or a GPIO — every table and every drawing is derived
from this file, so they cannot drift apart again. They already did, four times, and the
last time it would have shorted seven buttons to ground.

MEASURED on the actual kit parts (calipers, not datasheets):
  colored buttons  pins 3 holes ACROSS (2 pitches) x 6 holes LONG (5 pitches)
  small buttons    3x3 holes (2 pitches both ways)
  ESP32            11 holes across (pin rows 1.0in apart) x 15 long
  perfboard        30 rows x 42 cols, 120x80mm (silkscreen: 12*8CM 2.54MM),
                   DOUBLE-SIDED, 1.0mm holes, 4 FACTORY CORNER HOLES already drilled.
                   VERIFIED with a meter on the real board: adjacent pads are isolated
                   (true perfboard, not stripboard), and the elongated edge pads are
                   individual -- NOT power rails. That is what makes col 1 safe for the
                   GND link and makes every "nothing is connected until you connect it"
                   statement in the docs literally true here.
                   Everything fits ONE board now, with the ESP32 socketed beside the
                   controls. All joints stay on one face, so the design does not depend
                   on whether the holes are plated through.
"""

# ---- board ----------------------------------------------------------------
P            = 2.54
ROWS, COLS   = 30, 42          # the double-sided board: 42 across, 30 down
BOARD_W, BOARD_H = 120.0, 80.0   # from the silkscreen: 12*8CM
HOLE_D       = 1.0     # one lead per hole, never two
BEND         = 1.5     # straight lead between body seal and bend, per end

# ---- component footprints (mm) --------------------------------------------
BIG_LEG_COLS, BIG_LEG_ROWS = 2, 5
SMALL_LEG    = 2
BIG_BODY     = 12.0
SMALL_BODY   = 6.0
ESP_BODY_W   = 28.0    # module outline, wider than its pin rows
ESP_BODY_L   = 55.0    # including the USB connector
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
GND_LINK_COL = 1            # the three buses join down this column. It is BARE wire, so
                            # it must not be crossed by any signal run: every signal wire
                            # leaves its part at col >= 3 and heads RIGHT to the riser, so
                            # the left end is the one column none of them pass over. At
                            # col 28 all seven button/answer wires crossed it.
BUS_COLS = (1, 28)          # buses span the control surface only, not under the ESP32
# The single ground wire leaves the RIGHT end of the first bus -- the end nearest the
# socket, and the bus that goes on first, so the LEDs can be tested before the other two
# buses exist.
GND_WIRE_FROM = (BUS_COLS[1], GND_ROWS[0])
# The LCD is never soldered, so it stays a reusable part, and no 5V ever runs across the
# control surface — its port lives over at the ESP32 columns. See LCD_PORT_ROW below.
LCD_SOLDERED = False

# ---- ESP32, same board, columns 30-40 -------------------------------------
HDR_COLS = (30, 40)         # 10 apart = the ESP32's 1.0in pin rows
HDR_ROWS = (8, 22)          # 15 sockets running down
#
# ORIENTATION -- this cost a full set of wrong wire destinations once, so it is spelled
# out. The sides are named after their power pin, never "left"/"right", because left and
# right swap the moment you turn the module round.
#
#   * The USB connector is at the VIN / 3V3 end (CONFIRMED on the real module).
#   * We seat it USB pointing at the BOTTOM edge, so the cable exits away from the LCD,
#     which mounts above the board. That fixes everything else:
#       - pin position 1 (VIN, 3V3) is at the BOTTOM of the socket, board row 22
#       - position 15 (EN, D23)    is at the TOP,    board row 8
#       - viewed from the top with USB down, a DevKit V1 has 3V3 on the LEFT and VIN on
#         the RIGHT, so the 3V3 column is board col 30 and the VIN column is col 40
#
ESP_USB_END   = "bottom"
HDR_SIDE_COL  = {"3V3": HDR_COLS[0], "VIN": HDR_COLS[1]}


def socket_hole(side, pos):
    """Board hole for an ESP32 pin. Position 1 is the USB end, at the BOTTOM."""
    return HDR_SIDE_COL[side], HDR_ROWS[1] - (pos - 1)


# ---- the LCD port ---------------------------------------------------------
# The LCD is never soldered -- but once the ESP32 is seated, its pins are INSIDE the
# socket and nothing can clip onto them. So the board carries a 4-pin MALE header of
# its own, wired to the socket pads, and the LCD reaches it with 4 F-F jumpers.
# Order matches the LCD backpack's own header so the jumpers run straight, no crossing.
# Row 2 is the only band at these columns that clears the module: the ESP32's 55mm body
# overhangs its pin rows by ~3.8 rows at each end, so it shadows rows 4..26 here. Below
# the module is worse than it looks -- that is where the USB cable comes out.
LCD_PORT_ROW  = 2                  # clear band ABOVE the ESP32 body
LCD_PORT_COL0 = HDR_COLS[0]        # 4 holes: cols 30, 31, 32, 33

def lcd_port():
    """[(lcd pin, board hole, esp32 pin, socket hole)] for the 4-way LCD header."""
    out = []
    for i, (name, pin) in enumerate(LCD_PINS):
        esp = pin if pin in ("GND", "VIN") else f"D{pin}"
        out.append((name, (LCD_PORT_COL0 + i, LCD_PORT_ROW), esp,
                    socket_hole(*esp_position(esp, gnd_for="lcd"))))
    return out


# ---- mounting -------------------------------------------------------------
# THE BOARD ALREADY HAS FOUR CORNER HOLES, drilled at the factory, outside the pad grid.
# Use them -- do not drill anything. The computed positions below are only a fallback for
# a board without them, kept because verify-layout still proves they would be legal.
FACTORY_CORNER_HOLES = True
MOUNT_DRILL  = 2.2      # M2 clearance, fallback only
MOUNT_HEAD_R = 2.2      # M2 pan head + nylon washer, radius
EDGE_MIN     = 3.0      # material left between hole edge and board edge

# ---- electrical -----------------------------------------------------------
LED_GPIO  = [13, 14, 27, 26]
BTN_GPIO  = [32, 33, 25, 4]
LED_NAME  = ["red", "green", "blue", "yellow"]
ANS_INFO  = [("AA", 23, "always allow"), ("no", 18, "deny"), ("yes", 19, "approve")]
LCD_PINS  = [("GND", "GND"), ("VCC", "VIN"), ("SDA", "21"), ("SCL", "22")]

# ESP32 silkscreen, READ FROM THE USB END. Position 1 is the pin beside the USB socket.
# Transcribed from the real module.
ESP_VIN_SIDE = ["VIN","GND","D13","D12","D14","D27","D26","D25","D33","D32","D35","D34","VN","VP","EN"]
ESP_3V3_SIDE = ["3V3","GND","D15","D2","D4","RX2","TX2","D5","D18","D19","D21","RX0","TX0","D22","D23"]
# GND exists on both sides. Take it from the 3V3 side for the board's ground wire (that
# column is nearest the control surface) and from the VIN side for the LCD, which keeps
# the LCD's power pair together on one column.
GND_SIDE_FOR = {"board": "3V3", "lcd": "VIN"}

COL  = ["#c0392b", "#2e7d32", "#1565c0", "#b8860b"]
ANSC = ["#8a5a12", "#37474f", "#0f6b52"]


def esp_position(pin, gnd_for="board"):
    """Where a pin physically sits: ('VIN'|'3V3', 1..15), counted from the USB end."""
    if pin == "GND":
        side = GND_SIDE_FOR[gnd_for]
        return side, (ESP_VIN_SIDE if side == "VIN" else ESP_3V3_SIDE).index("GND") + 1
    if pin in ESP_VIN_SIDE: return "VIN", ESP_VIN_SIDE.index(pin) + 1
    if pin in ESP_3V3_SIDE: return "3V3", ESP_3V3_SIDE.index(pin) + 1
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
    out.append(("ground", f"col {GND_WIRE_FROM[0]}, row {GND_WIRE_FROM[1]}", "GND"))
    rows = []
    for lbl, src, pin in out:
        side, pos = esp_position(pin)
        col, row = socket_hole(side, pos)
        rows.append((lbl, src, pin, side, pos, col, row))
    return rows


# ---- geometry, in millimetres ---------------------------------------------
BX = (BOARD_W - (COLS-1)*P) / 2      # edge -> col 1
BY = (BOARD_H - (ROWS-1)*P) / 2      # edge -> row 1

def xy(col, row):
    return BX + (col-1)*P, BY + (row-1)*P


def bodies():
    """Every physical part footprint in mm. The one place footprints are computed."""
    out = []
    def add(name, cx, cy, w, h, where):
        out.append(dict(name=name, x0=cx-w/2, x1=cx+w/2, y0=cy-h/2, y1=cy+h/2, where=where))
    for i, c in enumerate(LED_COLS):
        x, y = xy(c, (LED_ROWS[0]+LED_ROWS[1])/2)
        add(f"LED{i+1}", x, y, LED_D, LED_D, f"col {c}, rows {LED_ROWS[0]}-{LED_ROWS[1]}")
        ry = (xy(c, RES_ROWS[0])[1] + xy(c, RES_ROWS[1])[1]) / 2
        add(f"R{i+1}", x, ry, RES_W, RES_BODY, f"col {c}, rows {RES_ROWS[0]}-{RES_ROWS[1]}")
    for i, c0 in enumerate(BTN_COL0):
        x0, y0 = xy(c0, BTN_ROWS[0]); x1, y1 = xy(c0+BIG_LEG_COLS, BTN_ROWS[1])
        add(f"BTN{i+1}", (x0+x1)/2, (y0+y1)/2, BIG_BODY, BIG_BODY,
            f"cols {c0}-{c0+BIG_LEG_COLS}, rows {BTN_ROWS[0]}+{BTN_ROWS[1]}")
    for n, c0 in zip(["AA", "no", "yes"], ANS_COL0):
        x0, y0 = xy(c0, ANS_ROWS[0]); x1, y1 = xy(c0+SMALL_LEG, ANS_ROWS[1])
        add(n, (x0+x1)/2, (y0+y1)/2, SMALL_BODY, SMALL_BODY,
            f"cols {c0}-{c0+SMALL_LEG}, rows {ANS_ROWS[0]}+{ANS_ROWS[1]}")
    ex0, ey0 = xy(HDR_COLS[0], HDR_ROWS[0]); ex1, ey1 = xy(HDR_COLS[1], HDR_ROWS[1])
    add("ESP32", (ex0+ex1)/2, (ey0+ey1)/2, ESP_BODY_W, ESP_BODY_L,
        f"cols {HDR_COLS[0]}-{HDR_COLS[1]}, rows {HDR_ROWS[0]}-{HDR_ROWS[1]}")
    for c in HDR_COLS:                       # the socket strips themselves
        sx, sy0 = xy(c, HDR_ROWS[0]); _, sy1 = xy(c, HDR_ROWS[1])
        add(f"socket c{c}", sx, (sy0+sy1)/2, P, (sy1-sy0)+P, f"col {c}")
    px0, py = xy(LCD_PORT_COL0, LCD_PORT_ROW)
    px1, _  = xy(LCD_PORT_COL0+len(LCD_PINS)-1, LCD_PORT_ROW)
    add("LCD port", (px0+px1)/2, py, (px1-px0)+P, P,
        f"cols {LCD_PORT_COL0}-{LCD_PORT_COL0+len(LCD_PINS)-1}, row {LCD_PORT_ROW}")
    return out


def switch_legs(c0, span, rows):
    """The four legs of one tactile switch, and what happens to each.

    MEASURED on the kit's switches: the internally-joined pairs run the LONG way, down
    the columns -- NOT the short way as the first draft assumed. Rather than depend on
    that, the build clips ONE leg and the design then works either way:

        (c0,      rows[0])  signal   -- takes the wire
        (c0+span, rows[0])  solder   -- isolated pad, anchoring only
        (c0,      rows[1])  CLIP     -- would sit on the GND bus. Under column-wise
                                        pairing that is the SIGNAL node: a dead short.
        (c0+span, rows[1])  ground   -- lands on the GND bus, which is what we want

    verify-layout.py proves this holds under both pairings; do not "tidy" it by
    soldering all four legs.
    """
    return [((c0,      rows[0]), "signal"),
            ((c0+span, rows[0]), "anchor"),
            ((c0,      rows[1]), "clip"),
            ((c0+span, rows[1]), "ground")]


def occupied_holes():
    """{(col,row): [what]} for every hole that already takes a lead or a pin."""
    h = {}
    def claim(c, r, who): h.setdefault((c, r), []).append(who)
    for i, c in enumerate(LED_COLS):
        claim(c, LED_ROWS[0], f"LED{i+1} anode");  claim(c, LED_ROWS[1], f"LED{i+1} cathode")
        claim(c, RES_ROWS[0], f"R{i+1} top");      claim(c, RES_ROWS[1], f"R{i+1} bottom")
    for i, c0 in enumerate(BTN_COL0):            # four legs, three of them fitted
        for hole, role in switch_legs(c0, BIG_LEG_COLS, BTN_ROWS):
            if role != "clip": claim(*hole, f"BTN{i+1} {role} leg")
    for n, c0 in zip(["AA","no","yes"], ANS_COL0):
        for hole, role in switch_legs(c0, SMALL_LEG, ANS_ROWS):
            if role != "clip": claim(*hole, f"{n} {role} leg")
    for sd, names in (("VIN", ESP_VIN_SIDE), ("3V3", ESP_3V3_SIDE)):
        for i, nm in enumerate(names):
            claim(*socket_hole(sd, i+1), f"socket {sd}-side pos {i+1} ({nm})")
    for name, hole, _, _ in lcd_port():
        claim(*hole, f"LCD port {name}")
    return h


def mount_candidates():
    """Holes a mounting screw could actually use, checked against real geometry."""
    taken = set(occupied_holes())
    bods  = bodies()
    r     = MOUNT_DRILL/2
    ok    = []
    for c in range(1, COLS+1):
        for rw in range(1, ROWS+1):
            if (c, rw) in taken: continue
            x, y = xy(c, rw)
            if min(x, BOARD_W-x, y, BOARD_H-y) < r + EDGE_MIN: continue
            if rw in GND_ROWS and BUS_COLS[0] <= c <= BUS_COLS[1]: continue
            if c == GND_LINK_COL and GND_ROWS[0] <= rw <= GND_ROWS[-1]: continue
            keep = True
            for b in bods:                     # screw head must clear every body
                if (x + MOUNT_HEAD_R > b["x0"] and b["x1"] > x - MOUNT_HEAD_R and
                    y + MOUNT_HEAD_R > b["y0"] and b["y1"] > y - MOUNT_HEAD_R):
                    keep = False; break
            if keep: ok.append((c, rw))
    return ok


def mount_holes():
    """Four well-spread mount holes: in each quadrant, the one nearest that corner."""
    cand = mount_candidates()
    if not cand: return []
    cx, cy = (COLS+1)/2, (ROWS+1)/2
    out = []
    for qc, qr in ((1, 1), (COLS, 1), (1, ROWS), (COLS, ROWS)):
        quad = [h for h in cand if (h[0] <= cx) == (qc == 1) and (h[1] <= cy) == (qr == 1)]
        if quad:
            out.append(min(quad, key=lambda h: (h[0]-qc)**2 + (h[1]-qr)**2))
    return out


def lcd_harness():
    """DEPRECATED — the soldered build uses lcd_port(). This described the breadboard
    arrangement, where the jumpers really do go onto the ESP32's own pins because the
    module is not in a socket. Kept only so BREADBOARD.md's generator still works."""
    return [(f"LCD {a}", "F-M jumper onto the LCD's own header", b if b == "GND" else
             ("VIN" if b == "VIN" else f"D{b}")) for a, b in LCD_PINS]
