// Milestone 2 test: prove the I2C LCD works. Also scans I2C so we learn the
// real address (0x27 or 0x3F) instead of guessing.
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);   // will retry 0x3F automatically below

void setup() {
  Serial.begin(115200);
  Wire.begin(21, 22);

  // I2C scan: report every address that ACKs, so we know what's really there.
  Serial.println("Scanning I2C...");
  uint8_t found = 0;
  for (uint8_t a = 1; a < 127; a++) {
    Wire.beginTransmission(a);
    if (Wire.endTransmission() == 0) {
      Serial.print("  found device at 0x");
      Serial.println(a, HEX);
      found = a;
    }
  }
  if (!found) Serial.println("  NONE found -- check SDA/SCL/GND/VCC wiring");

  // Drive whichever address we found (fall back to 0x27).
  uint8_t addr = found ? found : 0x27;
  lcd = LiquidCrystal_I2C(addr, 16, 2);
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("agentpad ready");
  lcd.setCursor(0, 1);
  lcd.print("addr 0x");
  lcd.print(addr, HEX);
}

void loop() {}
