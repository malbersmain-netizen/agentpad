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

/* face-plate feature positions, from the OUTER top-left corner */
COL        = [17.0, 37.3, 57.6, 78.0];   // 20.32mm pitch = exactly 8 perfboard holes
Y_LED      = 54.8;
Y_BTN      = 72.5;
Y_ANS      = 108.1;
ANS_X      = [17.0, 65.3, 80.5];         // AA . no . yes
LED_D      = 5.2;

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
