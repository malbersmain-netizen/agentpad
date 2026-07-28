// Milestone 4 test: print a line whenever a button is pressed (debounced).
// All SEVEN buttons: 4 agent-select, then approve / deny / always-allow.
const int BTN[7] = {32, 33, 25, 4, 19, 18, 23};
const char* NAME[7] = {
  "button 0  agent 1 RED (32)",
  "button 1  agent 2 GREEN (33)",
  "button 2  agent 3 BLUE (25)",
  "button 3  agent 4 YELLOW (4)",
  "button 4  APPROVE / yes (19)",
  "button 5  DENY / no (18)",
  "button 6  ALWAYS-ALLOW / AA (23)"
};
int last[7] = {HIGH, HIGH, HIGH, HIGH, HIGH, HIGH, HIGH};
unsigned long changed[7] = {0, 0, 0, 0, 0, 0, 0};

void setup() {
  Serial.begin(115200);
  for (int i = 0; i < 7; i++) pinMode(BTN[i], INPUT_PULLUP);
  Serial.println("button test ready - press each of the 7 buttons");
}

void loop() {
  unsigned long t = millis();
  for (int i = 0; i < 7; i++) {
    int v = digitalRead(BTN[i]);
    if (v != last[i] && t - changed[i] > 50) {
      changed[i] = t;
      last[i] = v;
      if (v == LOW) Serial.println(NAME[i]);
    }
  }
}
