// Milestone 3 test: light each LED one at a time, in order, and name it on serial.
const int LED[4] = {13, 14, 27, 26};
const char* NAME[4] = {"1 RED (13)", "2 GREEN (14)", "3 BLUE (27)", "4 YELLOW (26)"};

void setup() {
  Serial.begin(115200);
  for (int i = 0; i < 4; i++) { pinMode(LED[i], OUTPUT); digitalWrite(LED[i], LOW); }
}

void loop() {
  for (int i = 0; i < 4; i++) {
    Serial.println(NAME[i]);
    digitalWrite(LED[i], HIGH);
    delay(600);
    digitalWrite(LED[i], LOW);
    delay(150);
  }
}
