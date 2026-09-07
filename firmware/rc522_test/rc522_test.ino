/*
 * rc522_test — 40-line isolation sketch for the RC522 on an Arduino Nano ESP32.
 *
 * Flash this instead of the lock firmware when the reader misbehaves. It answers the
 * only question that matters at that point: is SPI working, and can it see a card?
 *
 *   0x91 / 0x92        genuine MFRC522, communicating
 *   0x88 / 0x12        clone chip, usually fine
 *   0x00 / 0xFF        NOT communicating — check SS, SCK, MOSI, MISO, RST, 3.3 V
 *   value changes      loose or intermittent connection
 *
 * Note the explicit SPI.begin(sck, miso, mosi, ss): the ESP32 core does not reliably
 * map the default bus onto the Nano's D11/D12/D13 silkscreen pins.
 */
#include <SPI.h>
#include <MFRC522.h>

#define SS_PIN   D10
#define RST_PIN  D4
#define SCK_PIN  D13
#define MISO_PIN D12
#define MOSI_PIN D11

MFRC522 rfid(SS_PIN, RST_PIN);
uint32_t lastCheck = 0;

void setup() {
  Serial.begin(115200);
  while (!Serial && millis() < 3000) { }
  Serial.println("\n\n=== RC522 test ===");

  SPI.begin(SCK_PIN, MISO_PIN, MOSI_PIN, SS_PIN);
  rfid.PCD_Init();
  delay(50);

  byte v = rfid.PCD_ReadRegister(MFRC522::VersionReg);
  Serial.print("VersionReg = 0x");
  if (v < 0x10) Serial.print("0");
  Serial.println(v, HEX);

  if (v == 0x00 || v == 0xFF) Serial.println(">>> NOT COMMUNICATING. Check wiring and 3.3 V.");
  else                        Serial.println(">>> Reader is talking. Hold a card flat on the coil.");

  rfid.PCD_SetAntennaGain(MFRC522::RxGain_max);
  rfid.PCD_AntennaOn();
}

void loop() {
  if (millis() - lastCheck > 3000) {                 // a changing value = loose wire
    lastCheck = millis();
    byte v = rfid.PCD_ReadRegister(MFRC522::VersionReg);
    Serial.print("  [alive] VersionReg = 0x");
    if (v < 0x10) Serial.print("0");
    Serial.println(v, HEX);
  }

  if (rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial()) {
    Serial.print("*** CARD READ, uid =");
    for (byte i = 0; i < rfid.uid.size; i++) {
      Serial.print(rfid.uid.uidByte[i] < 0x10 ? " 0" : " ");
      Serial.print(rfid.uid.uidByte[i], HEX);
    }
    Serial.println();
    rfid.PICC_HaltA();
    delay(600);
  }
  delay(50);
}
