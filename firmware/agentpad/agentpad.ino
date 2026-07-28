#include <Wire.h>
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);   // change to 0x3F if blank

const int LED[4] = {13, 14, 27, 26};
// Buttons: 0-3 = agent select (red, green, blue, yellow).
//          4   = APPROVE (GPIO 19)   -> "1. Yes"
//          5   = DENY    (GPIO 18)   -> "3. No"
//          6   = ALWAYS  (GPIO 23)   -> "2. Yes, and don't ask again"
const int BTN[7] = {32, 33, 25, 4, 19, 18, 23};
const int NBTN   = 7;

// 74HC595 shift register driving the LED bar graph (context-window usage).
// 8 segments, so each one is 12.5%.
const int SR_DATA  = 16;   // pin 14 DS
const int SR_CLOCK = 17;   // pin 11 SH_CP
const int SR_LATCH = 5;    // pin 12 ST_CP
const int SR_SEGS  = 8;

// 0=none 1=idle 2=working 3=blocked 4=done
int state[4]                = {0, 0, 0, 0};
unsigned long doneUntil[4]   = {0, 0, 0, 0};

int lastBtn[7]              = {HIGH, HIGH, HIGH, HIGH, HIGH, HIGH, HIGH};
unsigned long lastChange[7]  = {0, 0, 0, 0, 0, 0, 0};

String buf = "";

void setup() {
  Serial.begin(115200);
  Wire.begin(21, 22);
  lcd.init();
  lcd.backlight();
  lcd.clear();
  lcd.print("agentpad ready");
  for (int i = 0; i < 4; i++) {
    pinMode(LED[i], OUTPUT);
    digitalWrite(LED[i], LOW);
  }
  for (int i = 0; i < NBTN; i++) pinMode(BTN[i], INPUT_PULLUP);
  pinMode(SR_DATA, OUTPUT);
  pinMode(SR_CLOCK, OUTPUT);
  pinMode(SR_LATCH, OUTPUT);
  writeGauge(0);           // bar dark until the Mac reports a percentage
}

// Bar graph reads like a battery: charge 100 = all segments lit (fresh context),
// charge 0 = dark (context spent). The Mac sends the remaining percentage.
// With MSBFIRST the bit at position k lands on output Qk, so a run of low bits
// lights the segments nearest Q0.
void writeGauge(int charge) {
  int pct = charge;
  if (pct < 0)   pct = 0;
  if (pct > 100) pct = 100;
  int lit = (pct * SR_SEGS + 50) / 100;
  byte bits = 0;
  for (int i = 0; i < lit; i++) bits |= (1 << i);
  digitalWrite(SR_LATCH, LOW);
  shiftOut(SR_DATA, SR_CLOCK, MSBFIRST, bits);
  digitalWrite(SR_LATCH, HIGH);
}

void loop() {
  readSerial();
  updateLeds();
  readButtons();
}

void readSerial() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n')      { handle(buf); buf = ""; }
    else if (c != '\r') { buf += c; }
  }
}

void handle(String s) {
  if (s.startsWith("L ")) {
    int i = s.substring(2, 3).toInt();
    if (i < 0 || i > 3) return;
    String st = s.substring(4);
    st.trim();
    if      (st == "none")    state[i] = 0;
    else if (st == "idle")    state[i] = 1;
    else if (st == "working") state[i] = 2;
    else if (st == "blocked") state[i] = 3;
    else if (st == "done")  { state[i] = 4; doneUntil[i] = millis() + 2000; }
  }
  else if (s.startsWith("G ")) {
    String v = s.substring(2);
    v.trim();
    writeGauge(v.toInt());          // battery charge: 100 = fresh, 0 = context spent
  }
  else if (s.startsWith("D0 ") || s.startsWith("D1 ")) {
    int row = s.charAt(1) - '0';
    String text = s.substring(3);
    while (text.length() < 16) text += " ";
    lcd.setCursor(0, row);
    lcd.print(text.substring(0, 16));
  }
}

void updateLeds() {
  unsigned long t = millis();
  for (int i = 0; i < 4; i++) {
    bool on = false;
    switch (state[i]) {
      case 0: on = false;                  break;   // no session
      case 1: on = (t % 2000) < 60;        break;   // idle heartbeat
      case 2: on = true;                   break;   // working
      case 3: on = (t % 400) < 200;        break;   // BLOCKED - blinking
      case 4: on = true;
              if (t > doneUntil[i]) state[i] = 1;
              break;                                // done
    }
    digitalWrite(LED[i], on ? HIGH : LOW);
  }
}

void readButtons() {
  unsigned long t = millis();
  for (int i = 0; i < NBTN; i++) {
    int v = digitalRead(BTN[i]);
    if (v != lastBtn[i] && t - lastChange[i] > 50) {
      lastChange[i] = t;
      lastBtn[i] = v;
      if (v == LOW) {
        Serial.print("B ");
        Serial.println(i);    // 0-3 select, 4 approve, 5 deny, 6 always-allow
      }
    }
  }
}
