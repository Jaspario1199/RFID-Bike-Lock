/*  hw_selftest — Arduino Nano ESP32 bring-up test for the RFID bike lock.
 *
 *  A serial menu at 115200 that exercises each subsystem on its own, so a fault is
 *  isolated to one block instead of hidden inside the lock firmware's state machine.
 *  No deep sleep, so uploads always work.
 *
 *  Suggested order: 'a' first (everything passive), then 3 (buttons), then 5 (solenoid).
 *  Hold the solenoid body down before firing — 10 mm of stroke will jump it off the bench.
 */
#include <SPI.h>
#include <MFRC522.h>

#define PIN_ADMIN_BTN  D2
#define PIN_WAKE_BTN   D3
#define PIN_RC522_RST  D4
#define PIN_SOLENOID   D5
#define PIN_BUZZER     D6
#define PIN_LED_RED    D8
#define PIN_LED_GREEN  D9
#define PIN_RC522_SS   D10
#define PIN_RC522_MOSI D11
#define PIN_RC522_MISO D12
#define PIN_RC522_SCK  D13
#define PIN_VBAT       A0

#define SOLENOID_MS    300      // try 150 if the pull is strong

MFRC522 rfid(PIN_RC522_SS, PIN_RC522_RST);

void menu() {
  Serial.println(F("\n================ HARDWARE SELF TEST ================"));
  Serial.println(F("  1  LEDs        2  buzzer      3  buttons"));
  Serial.println(F("  4  reader      5  SOLENOID    6  battery / A0"));
  Serial.println(F("  a  run 1,2,4,6 (everything except buttons + solenoid)"));
  Serial.println(F("Type a number and press Enter."));
}

void testLeds() {
  Serial.println(F("[1] LEDs — red 3x, then green 3x"));
  for (int i = 0; i < 3; i++) { digitalWrite(PIN_LED_RED, HIGH); delay(250); digitalWrite(PIN_LED_RED, LOW); delay(250); }
  for (int i = 0; i < 3; i++) { digitalWrite(PIN_LED_GREEN, HIGH); delay(250); digitalWrite(PIN_LED_GREEN, LOW); delay(250); }
  Serial.println(F("    did you see 3 red then 3 green?"));
}

void testBuzzer() {
  Serial.println(F("[2] buzzer — short, short, long"));
  digitalWrite(PIN_BUZZER, HIGH); delay(80);  digitalWrite(PIN_BUZZER, LOW); delay(150);
  digitalWrite(PIN_BUZZER, HIGH); delay(80);  digitalWrite(PIN_BUZZER, LOW); delay(150);
  digitalWrite(PIN_BUZZER, HIGH); delay(500); digitalWrite(PIN_BUZZER, LOW);
}

void testButtons() {
  Serial.println(F("[3] buttons — press each one. 10 s. (idle reads 1, pressed 0)"));
  uint32_t t0 = millis();
  int lastG = -1, lastR = -1;
  while (millis() - t0 < 10000) {
    int g = digitalRead(PIN_WAKE_BTN), r = digitalRead(PIN_ADMIN_BTN);
    if (g != lastG) { Serial.print(F("    GREEN(D3) = ")); Serial.println(g); lastG = g; }
    if (r != lastR) { Serial.print(F("    RED(D2)   = ")); Serial.println(r); lastR = r; }
    delay(30);
  }
  Serial.println(F("    if a pin never changed, that button is miswired"));
}

void testReader() {
  Serial.println(F("[4] reader"));
  SPI.begin(PIN_RC522_SCK, PIN_RC522_MISO, PIN_RC522_MOSI, PIN_RC522_SS);
  rfid.PCD_Init(); delay(50);
  byte v = rfid.PCD_ReadRegister(MFRC522::VersionReg);
  Serial.print(F("    VersionReg = 0x")); if (v < 0x10) Serial.print("0"); Serial.println(v, HEX);
  if (v == 0x00 || v == 0xFF) { Serial.println(F("    >>> NOT COMMUNICATING")); return; }
  rfid.PCD_SetAntennaGain(MFRC522::RxGain_max);
  rfid.PCD_AntennaOn();
  Serial.println(F("    hold a fob on the coil — 10 s"));
  uint32_t t0 = millis();
  while (millis() - t0 < 10000) {
    if (rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial()) {
      Serial.print(F("    *** CARD uid ="));
      for (byte i = 0; i < rfid.uid.size; i++) {
        Serial.print(rfid.uid.uidByte[i] < 0x10 ? " 0" : " ");
        Serial.print(rfid.uid.uidByte[i], HEX);
      }
      Serial.println();
      rfid.PICC_HaltA(); delay(600);
    }
    delay(30);
  }
}

void testSolenoid() {
  Serial.println(F("[5] SOLENOID — hold the body down, it will jump."));
  for (int i = 3; i > 0; i--) { Serial.print(F("    firing in ")); Serial.println(i); delay(1000); }
  Serial.println(F("    FIRE"));
  digitalWrite(PIN_SOLENOID, HIGH);
  delay(SOLENOID_MS);
  digitalWrite(PIN_SOLENOID, LOW);
  Serial.println(F("    done. Clunk? If not: gate wiring, coil supply, or MOSFET pinout."));
  Serial.println(F("    Now touch the MOSFET and diode — both should be COOL."));
}

void testBattery() {
  analogRead(PIN_VBAT);
  int raw = analogRead(PIN_VBAT);
  float v = raw * (3.3f / 4095.0f) * 2.0f;      // 100k:100k divider
  Serial.print(F("[6] A0 raw = ")); Serial.print(raw);
  Serial.print(F("   -> ")); Serial.print(v); Serial.println(F(" V at the battery"));
  Serial.println(F("    A0 floating reads noise; jumper A0->3V3 to silence the low-battery warning"));
}

void setup() {
  pinMode(PIN_WAKE_BTN, INPUT_PULLUP);
  pinMode(PIN_ADMIN_BTN, INPUT_PULLUP);
  pinMode(PIN_SOLENOID, OUTPUT);  digitalWrite(PIN_SOLENOID, LOW);
  pinMode(PIN_BUZZER, OUTPUT);    digitalWrite(PIN_BUZZER, LOW);
  pinMode(PIN_LED_RED, OUTPUT);   digitalWrite(PIN_LED_RED, LOW);
  pinMode(PIN_LED_GREEN, OUTPUT); digitalWrite(PIN_LED_GREEN, LOW);
  analogReadResolution(12);
  analogSetAttenuation(ADC_11db);

  Serial.begin(115200);
  uint32_t t0 = millis();
  while (!Serial && millis() - t0 < 2000) { }
  menu();
}

void loop() {
  if (!Serial.available()) { delay(50); return; }
  char c = Serial.read();
  while (Serial.available()) Serial.read();     // flush the newline
  switch (c) {
    case '1': testLeds(); break;
    case '2': testBuzzer(); break;
    case '3': testButtons(); break;
    case '4': testReader(); break;
    case '5': testSolenoid(); break;
    case '6': testBattery(); break;
    case 'a': testLeds(); testBuzzer(); testReader(); testBattery(); break;
    default: break;
  }
  menu();
}
