// Milestone 2 test: prove the I2C LCD works. Scans I2C so we learn the real
// address (0x27 or 0x3F) instead of guessing, then exercises BOTH rows across
// their FULL 16-character width.
//
// Why full width and an explicit clear(): the first version wrote two short
// strings and never called clear(), so whatever powered up in the display's
// memory sat underneath, and a row that failed to write looked identical to a
// row that was merely faint. Solid blocks separate those two cases.
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);

void setup() {
  Serial.begin(115200);
  delay(200);
  Wire.begin(21, 22);

  // I2C scan: report every address that ACKs, so we know what's really there.
  Serial.println("Scanning I2C...");
  uint8_t found = 0, count = 0;
  for (uint8_t a = 1; a < 127; a++) {
    Wire.beginTransmission(a);
    if (Wire.endTransmission() == 0) {
      Serial.print("  found device at 0x");
      Serial.println(a, HEX);
      found = a; count++;
    }
  }
  if (!found) {
    Serial.println("  NONE found -- check SDA/SCL/GND/VCC wiring");
    return;                        // nothing to drive
  }
  if (count > 1) Serial.println("  WARNING: more than one device answered");

  lcd = LiquidCrystal_I2C(found, 16, 2);
  lcd.init();
  delay(50);
  lcd.backlight();
  lcd.clear();                     // wipe whatever powered up in DDRAM
  delay(50);

  // Step 1: both rows, full width, solid blocks. A dead row is obvious, and
  // low contrast shows as faint blocks rather than as nothing at all.
  Serial.println("Filling both rows with blocks for 3s...");
  for (uint8_t r = 0; r < 2; r++) {
    lcd.setCursor(0, r);
    for (uint8_t c = 0; c < 16; c++) lcd.write(0xFF);
  }
  delay(3000);

  // Step 2: text on both rows, full width, so truncation is visible.
  lcd.clear();
  delay(50);
  lcd.setCursor(0, 0);
  lcd.print("0123456789abcdef");
  lcd.setCursor(0, 1);
  lcd.print("addr 0x");
  lcd.print(found, HEX);
  lcd.print(" OK    ");

  Serial.println();
  Serial.println("Expect on the display:");
  Serial.println("  row 0:  0123456789abcdef   <- all 16 columns");
  Serial.print  ("  row 1:  addr 0x"); Serial.print(found, HEX); Serial.println(" OK");
  Serial.println();
  Serial.println("Both rows blocked, then both rows text  -> LCD fully working");
  Serial.println("Row 0 only, even during the blocks      -> row 1 not driven");
  Serial.println("Both rows faint                         -> contrast pot on the backpack");
}

void loop() {}
