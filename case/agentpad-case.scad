// Agent Pad — parametric enclosure
//
// Two printed parts: a face plate (all the cutouts) and a box (walls, floor, posts).
// Render one at a time with the PART variable, or from the CLI:
//
//   openscad -D 'PART="face"' -o face.stl agentpad-case.scad
//   openscad -D 'PART="box"'  -o box.stl  agentpad-case.scad
//
// MEASURE YOUR PARTS FIRST. The three values under "measure these" are the ones that
// vary by supplier and will ruin the print if guessed. Everything else derives from them.

PART = "both";          // "face" | "box" | "both" (preview)

/* ---------------- measure these ---------------- */
CAP        = 11.6;      // button cap, across flats (calipers on an actual cap)
CAP_H      = 12.5;      // board surface -> top of cap
HDR_H      = 8.5;       // female header height (LOW-PROFILE 5mm headers help a lot)
/* ----------------------------------------------- */

/* case */
W          = 95;        // width
D          = 140;       // depth (long axis)
WALL       = 2.5;
FACE_T     = 2.5;
CORNER_R   = 4;

/* board */
BOARD_W    = 86.4;      // 34 holes
BOARD_D    = 127;       // 50 holes
BOARD_T    = 1.6;

/* ESP32 on its header (coplanar, not stacked) */
ESP_PCB    = 1.6;
ESP_USB    = 3.5;       // USB connector height above the ESP32 pcb
ESP_H      = HDR_H + ESP_PCB + ESP_USB;

/* LCD1602 module */
LCD_WIN_W  = 64.5;      // VIEWING AREA - cut this, not the module outline
LCD_WIN_H  = 16;
LCD_HOLE_X = 75;        // M3 mounting hole centres
LCD_HOLE_Y = 31;
LCD_CX     = W/2;
LCD_CY     = 38;

/* ---- column pitch -------------------------------------------------------
   Pitch is a whole number of 0.1" perfboard holes, so the board grid and the
   printed face agree by construction. Set PITCH_HOLES to whatever the board
   can span:  8 = 20.32mm (needs 73mm)   <- original, needs a 9x15cm board
              7 = 17.78mm (needs 65mm)   <- fits a 20x27-hole 5x7cm board
              6 = 15.24mm (needs 58mm)   <- fits an 18x24-hole 5x7cm board
   Everything below derives from it, so changing this one number moves every
   hole and keeps the row centred in the case.                              */
PITCH_HOLES = 6;    // kit boards are 18 x 24 holes -> 58.4mm of hole field
PITCH       = PITCH_HOLES * 2.54;
BTN_SPAN    = 3*PITCH + CAP;                       // outer edge to outer edge
COL0        = (W - BTN_SPAN)/2 + CAP/2;            // centre of the first column
COL         = [for (i=[0:3]) COL0 + i*PITCH];

/* face-plate feature positions, from the OUTER top-left corner */
Y_LED      = 54.8;
Y_BTN      = 72.5;
Y_ANS      = 108.1;
// AA sits under column 1, no/yes under columns 3 and 4 — keeps AA well away from
// "yes" so it can't be hit by accident, and lands everything on the same 4 columns.
ANS_X      = [COL[0], COL[2], COL[3]];
LED_D      = 5.2;

echo(str("pitch ", PITCH, "mm (", PITCH_HOLES, " holes) — button row spans ",
         BTN_SPAN, "mm; columns at ", COL));

/* fasteners */
SCREW_D    = 3.2;       // M3 clearance
POST_D     = 7;
PILOT_D    = 2.5;       // self-tapping pilot
INSET      = 7;         // corner posts inset from the outer edge

/* USB-C exit, bottom edge */
USB_W      = 13;
USB_H      = 7.5;

/* ---------------- computed ---------------- */
// The face must clear the TALLEST thing standing on the board. That is usually the
// ESP32, not the buttons -- with 8.5mm headers the ESP32 wins by about a millimetre.
GAP        = max(CAP_H, ESP_H);          // face underside -> board top
UNDER      = 5;                          // wire-bend room under the board
T          = FACE_T + GAP + BOARD_T + UNDER + WALL;

echo(str("face gap needed      : ", GAP, " mm  (caps ", CAP_H, ", esp32 ", ESP_H, ")"));
echo(str("TOTAL CASE THICKNESS : ", T, " mm"));
echo(str(T <= 28 ? "OK - fits the 28mm design" :
        "TOO DEEP for 28mm -> use 5mm low-profile headers, or raise the design"));
if (CAP_H < ESP_H)
  echo("NOTE: caps are shorter than the ESP32, so buttons need a shim or taller caps");

$fn = 48;

/* ---------------- helpers ---------------- */
module rrect(w, d, h, r) {
  hull() for (x = [r, w-r], y = [r, d-r]) translate([x, y, 0]) cylinder(r=r, h=h);
}

module corner_posts(h, hole_d) {
  for (x = [INSET, W-INSET], y = [INSET, D-INSET])
    translate([x, y, 0]) difference() {
      cylinder(d=POST_D, h=h);
      translate([0,0,-1]) cylinder(d=hole_d, h=h+2);
    }
}

/* ---------------- face plate ---------------- */
module face() {
  difference() {
    union() {
      rrect(W, D, FACE_T, CORNER_R);
      // LCD standoffs hanging down from the face
      for (x = [LCD_CX-LCD_HOLE_X/2, LCD_CX+LCD_HOLE_X/2])
        for (y = [LCD_CY-LCD_HOLE_Y/2, LCD_CY+LCD_HOLE_Y/2])
          translate([x, y, FACE_T]) difference() {
            cylinder(d=6, h=4);
            translate([0,0,-1]) cylinder(d=PILOT_D, h=6);
          }
    }
    // LCD viewing window
    translate([LCD_CX-LCD_WIN_W/2, LCD_CY-LCD_WIN_H/2, -1])
      cube([LCD_WIN_W, LCD_WIN_H, FACE_T+2]);
    // LEDs
    for (x = COL) translate([x, Y_LED, -1]) cylinder(d=LED_D, h=FACE_T+2);
    // select buttons
    for (x = COL) translate([x, Y_BTN, -1])
      translate([-(CAP+0.4)/2, -(CAP+0.4)/2, 0]) cube([CAP+0.4, CAP+0.4, FACE_T+2]);
    // answer buttons
    for (x = ANS_X) translate([x, Y_ANS, -1])
      translate([-(CAP+0.4)/2, -(CAP+0.4)/2, 0]) cube([CAP+0.4, CAP+0.4, FACE_T+2]);
    // corner screws
    for (x = [INSET, W-INSET], y = [INSET, D-INSET])
      translate([x, y, -1]) cylinder(d=SCREW_D, h=FACE_T+2);
  }
}

/* ---------------- box ---------------- */
module box() {
  difference() {
    union() {
      rrect(W, D, T, CORNER_R);
      // board standoffs, so the board sits at the right height
      for (x = [(W-BOARD_W)/2+5, (W+BOARD_W)/2-5],
           y = [(D-BOARD_D)/2+5, (D+BOARD_D)/2-5])
        translate([x, y, WALL])
          cylinder(d=6, h=T-WALL-FACE_T-GAP-BOARD_T);
    }
    // hollow
    translate([WALL, WALL, WALL])
      rrect(W-2*WALL, D-2*WALL, T, CORNER_R/2);
    // USB-C slot in the bottom wall, at board level
    translate([W/2-USB_W/2, D-WALL-1, T-FACE_T-GAP-BOARD_T-USB_H+1])
      cube([USB_W, WALL+2, USB_H]);
  }
  // corner posts, drilled for self-tapping screws
  translate([0,0,WALL]) corner_posts(T-WALL-FACE_T, PILOT_D);
}

/* ---------------- render ---------------- */
if (PART == "face") face();
else if (PART == "box") box();
else {
  box();
  translate([0, 0, T + 25]) face();     // exploded preview
}
