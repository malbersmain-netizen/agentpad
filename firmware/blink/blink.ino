// Milestone 1 smoke test: blink the onboard LED (GPIO 2 on ESP32 Dev Module).
void setup() {
  pinMode(2, OUTPUT);
}

void loop() {
  digitalWrite(2, HIGH);
  delay(300);
  digitalWrite(2, LOW);
  delay(300);
}
