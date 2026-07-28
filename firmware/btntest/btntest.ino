// Milestone 4 test: print a line whenever a button is pressed (debounced).
const int BTN[4] = {32, 33, 25, 4};
const char* NAME[4] = {"1 RED (32)", "2 GREEN (33)", "3 BLUE (25)", "4 YELLOW (4)"};
int last[4] = {HIGH, HIGH, HIGH, HIGH};
unsigned long changed[4] = {0,0,0,0};

void setup() {
  Serial.begin(115200);
  for (int i = 0; i < 4; i++) pinMode(BTN[i], INPUT_PULLUP);
  Serial.println("button test ready - press each button");
}

void loop() {
  unsigned long t = millis();
  for (int i = 0; i < 4; i++) {
    int v = digitalRead(BTN[i]);
    if (v != last[i] && t - changed[i] > 50) {
      changed[i] = t;
      last[i] = v;
      if (v == LOW) { Serial.print("PRESS "); Serial.println(NAME[i]); }
    }
  }
}
