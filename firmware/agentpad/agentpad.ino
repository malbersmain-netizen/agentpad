#include <Wire.h>
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);   // change to 0x3F if blank

const int LED[4] = {13, 14, 27, 26};
const int BTN[4] = {32, 33, 25, 4};

// 0=none 1=idle 2=working 3=blocked 4=done
int state[4]              = {0, 0, 0, 0};
unsigned long doneUntil[4] = {0, 0, 0, 0};

int lastBtn[4]             = {HIGH, HIGH, HIGH, HIGH};
unsigned long lastChange[4] = {0, 0, 0, 0};

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
    pinMode(BTN[i], INPUT_PULLUP);
  }
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
  for (int i = 0; i < 4; i++) {
    int v = digitalRead(BTN[i]);
    if (v != lastBtn[i] && t - lastChange[i] > 50) {
      lastChange[i] = t;
      lastBtn[i] = v;
      if (v == LOW) {
        Serial.print("B ");
        Serial.println(i);
      }
    }
  }
}
