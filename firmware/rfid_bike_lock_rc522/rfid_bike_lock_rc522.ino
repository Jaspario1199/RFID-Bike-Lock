/*
 * RFID Bike Lock — v1 firmware
 * Target: Arduino Nano (ATmega328P, 5V/16MHz)
 * Reader: MFRC522 (the "RC522" Arduino kit board) on hardware SPI - see firmware/README.md
 * This is the RC522 variant of rfid_bike_lock.ino: identical state machine, EEPROM layout,
 * pins and behaviour; only the reader driver differs. Reads MIFARE Classic fobs and NTAG213
 * stickers (both ISO 14443A). It cannot talk to phones (that needs a PN532 + HCE) - same
 * key plan either way: fobs + a sticker on the phone case.
 *
 * Implements the state machine from DESIGN.md §5:
 *   SLEEP -> (wake button) -> SCAN (10 s) -> AUTH -> UNLOCK pulse -> SLEEP
 *   plus first-boot master enrollment and button-hold admin (add/remove tags).
 *
 * Power design notes (matches DESIGN.md §4):
 *   - The RC522's 3.3 V supply is hard-switched by a P-MOSFET on PIN_PN532_PWR
 *     (drive LOW to power the reader, HIGH/idle = off).
 *   - Between events the MCU sits in power-down sleep; the wake button on
 *     D3 (INT1) is the only wake source.
 *   - The solenoid fires for SOLENOID_PULSE_MS only after a successful auth.
 */

#include <SPI.h>
#include <MFRC522.h>          // Library Manager: "MFRC522" by GithubCommunity (miguelbalboa)
#include <EEPROM.h>
#include <avr/sleep.h>
#include <avr/power.h>

// ---------- Debug ----------
// Comment out for the battery-powered unit: Serial keeps the USB chip busy
// and the prints cost power. Leave on for bench bring-up.
#define DEBUG

#ifdef DEBUG
  #define DBG(x)   Serial.print(x)
  #define DBGLN(x) Serial.println(x)
#else
  #define DBG(x)
  #define DBGLN(x)
#endif

// ---------- Pins (DESIGN.md §4.2) ----------
const uint8_t PIN_WAKE_BTN   = 3;   // INT1, momentary to GND, internal pullup
const uint8_t PIN_SOLENOID   = 5;   // IRLZ44N gate (HIGH = solenoid energized)
const uint8_t PIN_PN532_PWR  = 7;   // P-MOSFET gate (LOW = reader powered) - name kept for the PN532 build
const uint8_t PIN_RC522_SS   = 10;  // SPI: SS=D10, SCK=D13, MOSI=D11, MISO=D12 (hardware SPI)
const uint8_t PIN_RC522_RST  = 4;   // D9 is the green LED, so RST moves to D4
const uint8_t PIN_LED_RED    = 8;
const uint8_t PIN_LED_GREEN  = 9;
const uint8_t PIN_VBAT_SENSE = A0;  // battery / 2 via 100k:100k divider

// ---------- Tuning ----------
const uint32_t SCAN_WINDOW_MS      = 10000; // reader live after wake press
const uint32_t SOLENOID_PULSE_MS   = 300;   // unlock pulse
const uint32_t ADMIN_HOLD_MS       = 5000;  // button hold to enter admin
const uint32_t ADMIN_TIMEOUT_MS    = 15000; // idle exit from admin mode
const uint32_t SAME_UID_LOCKOUT_MS = 2000;  // ignore repeat reads of same tag
const float    VBAT_LOW            = 3.50;  // red triple-blink threshold (V)
const float    VBAT_DIVIDER        = 2.0;   // 100k:100k
const float    VREF                = 5.0;   // Nano ADC ref = 5V rail

// ---------- EEPROM layout ----------
// [0]        magic (EE_MAGIC when initialized)
// [1]        count of authorized slots in use (0..MAX_TAGS)
// [2..9]     master tag:      [len][uid bytes, zero-padded to 7]
// [10..]     MAX_TAGS slots:  [len][uid bytes, zero-padded to 7] each
const uint8_t  EE_MAGIC      = 0x42;
const int      EE_ADDR_MAGIC = 0;
const int      EE_ADDR_COUNT = 1;
const int      EE_ADDR_MASTER= 2;
const int      EE_ADDR_SLOTS = 10;
const uint8_t  UID_REC_SIZE  = 8;   // 1 len byte + up to 7 uid bytes
const uint8_t  MAX_TAGS      = 10;

MFRC522 rfid(PIN_RC522_SS, PIN_RC522_RST);

// ----------------------------------------------------------------------
// Wake interrupt — body intentionally empty; its only job is to end sleep.
void wakeISR() {}

// ---------- LED helpers ----------
void blink(uint8_t pin, uint8_t times, uint16_t onMs = 120, uint16_t offMs = 120) {
  for (uint8_t i = 0; i < times; i++) {
    digitalWrite(pin, HIGH); delay(onMs);
    digitalWrite(pin, LOW);  delay(offMs);
  }
}

void blinkAlternating(uint8_t cycles) { // admin-mode signature: red/green
  for (uint8_t i = 0; i < cycles; i++) {
    digitalWrite(PIN_LED_RED, HIGH);  delay(100);
    digitalWrite(PIN_LED_RED, LOW);
    digitalWrite(PIN_LED_GREEN, HIGH); delay(100);
    digitalWrite(PIN_LED_GREEN, LOW);
  }
}

// ---------- Battery ----------
float readBatteryVolts() {
  analogRead(PIN_VBAT_SENSE);              // throwaway read after sleep (settles mux)
  int raw = analogRead(PIN_VBAT_SENSE);
  return raw * (VREF / 1023.0) * VBAT_DIVIDER;
}

// ---------- EEPROM tag records ----------
void eeWriteRecord(int addr, const uint8_t *uid, uint8_t len) {
  EEPROM.update(addr, len);
  for (uint8_t i = 0; i < 7; i++) EEPROM.update(addr + 1 + i, i < len ? uid[i] : 0);
}

bool eeMatchRecord(int addr, const uint8_t *uid, uint8_t len) {
  if (EEPROM.read(addr) != len) return false;
  for (uint8_t i = 0; i < len; i++)
    if (EEPROM.read(addr + 1 + i) != uid[i]) return false;
  return true;
}

bool isMaster(const uint8_t *uid, uint8_t len) {
  return eeMatchRecord(EE_ADDR_MASTER, uid, len);
}

// Returns slot index 0..count-1, or -1 if not found.
int findTag(const uint8_t *uid, uint8_t len) {
  uint8_t count = EEPROM.read(EE_ADDR_COUNT);
  if (count > MAX_TAGS) count = 0; // corrupt guard
  for (uint8_t s = 0; s < count; s++)
    if (eeMatchRecord(EE_ADDR_SLOTS + s * UID_REC_SIZE, uid, len)) return s;
  return -1;
}

bool isAuthorized(const uint8_t *uid, uint8_t len) {
  return isMaster(uid, len) || findTag(uid, len) >= 0;
}

bool addTag(const uint8_t *uid, uint8_t len) {
  uint8_t count = EEPROM.read(EE_ADDR_COUNT);
  if (count >= MAX_TAGS) return false;
  eeWriteRecord(EE_ADDR_SLOTS + count * UID_REC_SIZE, uid, len);
  EEPROM.update(EE_ADDR_COUNT, count + 1);
  return true;
}

void removeTagAt(int slot) {
  uint8_t count = EEPROM.read(EE_ADDR_COUNT);
  // Move the last record into the freed slot, shrink count.
  int last = EE_ADDR_SLOTS + (count - 1) * UID_REC_SIZE;
  int dst  = EE_ADDR_SLOTS + slot * UID_REC_SIZE;
  for (uint8_t i = 0; i < UID_REC_SIZE; i++)
    EEPROM.update(dst + i, EEPROM.read(last + i));
  EEPROM.update(EE_ADDR_COUNT, count - 1);
}

// ---------- RC522 power gating ----------
bool pn532On() {                       // name kept so the state machine below is byte-identical
  digitalWrite(PIN_PN532_PWR, LOW);    // P-MOSFET on -> 3.3 V to the RC522
  delay(50);                           // module power-up + oscillator
  SPI.begin();
  rfid.PCD_Init();
  byte v = rfid.PCD_ReadRegister(MFRC522::VersionReg);   // 0x91 / 0x92 on genuine parts, 0xB2/0x12 on clones
  if (v == 0x00 || v == 0xFF) return false;              // nothing on the bus
  rfid.PCD_AntennaOn();
  rfid.PCD_SetAntennaGain(rfid.RxGain_max);              // best range through the lid
  return true;
}

void pn532Off() {
  rfid.PCD_AntennaOff();
  SPI.end();
  // Park every line LOW so the 5 V Nano pins can't back-feed the dead 3.3 V rail
  for (uint8_t p : {PIN_RC522_SS, PIN_RC522_RST, (uint8_t)13, (uint8_t)11, (uint8_t)12}) {
    pinMode(p, OUTPUT); digitalWrite(p, LOW);
  }
  digitalWrite(PIN_PN532_PWR, HIGH);   // P-MOSFET off
}

// Poll for a tag with a bounded wait. Returns true and fills uid/len (4 or 7 bytes).
bool readTag(uint8_t *uid, uint8_t *len, uint16_t timeoutMs) {
  uint32_t t0 = millis();
  while (millis() - t0 < timeoutMs) {
    if (rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial()) {
      *len = rfid.uid.size > 7 ? 7 : rfid.uid.size;
      memcpy(uid, rfid.uid.uidByte, *len);
      rfid.PICC_HaltA();               // so the same tag isn't re-read until it leaves the field
      return true;
    }
    delay(25);
  }
  return false;
}

// ---------- Solenoid ----------
void fireUnlock() {
  digitalWrite(PIN_SOLENOID, HIGH);
  delay(SOLENOID_PULSE_MS);
  digitalWrite(PIN_SOLENOID, LOW);
}

// ---------- Sleep ----------
void goToSleep() {
  pn532Off();
  digitalWrite(PIN_LED_RED, LOW);
  digitalWrite(PIN_LED_GREEN, LOW);
  digitalWrite(PIN_SOLENOID, LOW);

#ifdef DEBUG
  Serial.flush();
#endif

  ADCSRA &= ~_BV(ADEN);               // ADC off (~300 µA)
  set_sleep_mode(SLEEP_MODE_PWR_DOWN);
  noInterrupts();
  attachInterrupt(digitalPinToInterrupt(PIN_WAKE_BTN), wakeISR, LOW);
  sleep_enable();
  sleep_bod_disable();                // brown-out detector off during sleep
  interrupts();
  sleep_cpu();                        // ---- asleep here ----
  sleep_disable();
  detachInterrupt(digitalPinToInterrupt(PIN_WAKE_BTN));
  ADCSRA |= _BV(ADEN);                // ADC back on
}

// ---------- Admin mode ----------
void runAdminMode() {
  DBGLN(F("[admin] waiting for master"));
  blinkAlternating(3);

  uint8_t uid[7]; uint8_t len;
  uint32_t start = millis();
  bool masterOk = false;
  while (millis() - start < ADMIN_TIMEOUT_MS) {
    if (readTag(uid, &len, 400) && isMaster(uid, len)) { masterOk = true; break; }
  }
  if (!masterOk) { blink(PIN_LED_RED, 2); return; }

  DBGLN(F("[admin] master ok — tap to add/remove"));
  blink(PIN_LED_GREEN, 1, 400, 0);

  uint32_t lastActivity = millis();
  while (millis() - lastActivity < ADMIN_TIMEOUT_MS) {
    if (!readTag(uid, &len, 400)) continue;
    lastActivity = millis();

    if (isMaster(uid, len)) { blink(PIN_LED_RED, 1); continue; } // master not removable

    int slot = findTag(uid, len);
    if (slot >= 0) {
      removeTagAt(slot);
      DBGLN(F("[admin] tag removed"));
      blink(PIN_LED_RED, 3);
    } else if (addTag(uid, len)) {
      DBGLN(F("[admin] tag added"));
      blink(PIN_LED_GREEN, 3);
    } else {
      DBGLN(F("[admin] list full"));
      blink(PIN_LED_RED, 5, 60, 60);
    }
    delay(SAME_UID_LOCKOUT_MS); // force tag removal before next action
  }
  DBGLN(F("[admin] timeout, exiting"));
}

// ---------- First boot: enroll master ----------
void enrollMaster() {
  DBGLN(F("[enroll] first boot — tap the tag that becomes MASTER"));
  uint8_t uid[7]; uint8_t len;
  // Blink alternating forever until a tag shows up; this only ever runs once.
  while (true) {
    blinkAlternating(1);
    if (readTag(uid, &len, 400)) break;
  }
  eeWriteRecord(EE_ADDR_MASTER, uid, len);
  EEPROM.update(EE_ADDR_COUNT, 0);
  EEPROM.update(EE_ADDR_MAGIC, EE_MAGIC);
  DBGLN(F("[enroll] master stored"));
  blink(PIN_LED_GREEN, 5);
}

// ---------- Scan window ----------
void runScanWindow() {
  float v = readBatteryVolts();
  DBG(F("[wake] vbat=")); DBGLN(v);
  if (v < VBAT_LOW) blink(PIN_LED_RED, 3);

  if (!pn532On()) {
    DBGLN(F("[err] PN532 not responding"));
    blink(PIN_LED_RED, 5, 60, 60);
    return;
  }

  if (EEPROM.read(EE_ADDR_MAGIC) != EE_MAGIC) enrollMaster();

  uint8_t uid[7]; uint8_t len;
  uint8_t lastUid[7] = {0}; uint8_t lastLen = 0;
  uint32_t lastReadAt = 0;
  uint32_t windowStart = millis();
  uint32_t btnDownAt = 0;

  digitalWrite(PIN_LED_GREEN, HIGH); delay(60); digitalWrite(PIN_LED_GREEN, LOW);

  while (millis() - windowStart < SCAN_WINDOW_MS) {

    // --- admin entry: hold the wake button for ADMIN_HOLD_MS ---
    if (digitalRead(PIN_WAKE_BTN) == LOW) {
      if (btnDownAt == 0) btnDownAt = millis();
      else if (millis() - btnDownAt >= ADMIN_HOLD_MS) {
        runAdminMode();
        return; // sleep after admin
      }
    } else {
      btnDownAt = 0;
    }

    // --- tag polling ---
    if (!readTag(uid, &len, 300)) continue;

    // debounce: same tag within lockout -> ignore
    bool same = (len == lastLen) && (millis() - lastReadAt < SAME_UID_LOCKOUT_MS);
    if (same) for (uint8_t i = 0; i < len; i++) if (uid[i] != lastUid[i]) { same = false; break; }
    if (same) continue;
    memcpy(lastUid, uid, len); lastLen = len; lastReadAt = millis();

#ifdef DEBUG
    DBG(F("[scan] uid="));
    for (uint8_t i = 0; i < len; i++) { DBG(uid[i] < 16 ? "0" : ""); Serial.print(uid[i], HEX); }
    DBGLN("");
#endif

    if (isAuthorized(uid, len)) {
      DBGLN(F("[auth] OK -> unlock"));
      fireUnlock();
      digitalWrite(PIN_LED_GREEN, HIGH); delay(1000); digitalWrite(PIN_LED_GREEN, LOW);
      return; // job done, back to sleep
    } else {
      DBGLN(F("[auth] denied"));
      blink(PIN_LED_RED, 2);
      // window stays open for another attempt
    }
  }
  DBGLN(F("[scan] window expired"));
}

// ----------------------------------------------------------------------
void setup() {
  pinMode(PIN_WAKE_BTN, INPUT_PULLUP);
  pinMode(PIN_SOLENOID, OUTPUT);   digitalWrite(PIN_SOLENOID, LOW);
  pinMode(PIN_PN532_PWR, OUTPUT);  digitalWrite(PIN_PN532_PWR, HIGH); // reader off
  pinMode(PIN_LED_RED, OUTPUT);    digitalWrite(PIN_LED_RED, LOW);
  pinMode(PIN_LED_GREEN, OUTPUT);  digitalWrite(PIN_LED_GREEN, LOW);

#ifdef DEBUG
  Serial.begin(115200);
  DBGLN(F("RFID bike lock v1"));
#endif

  power_spi_disable();   // unused peripherals off for good
  power_timer2_disable();
}

void loop() {
  goToSleep();           // blocks until wake-button press
  delay(30);             // debounce the press that woke us
  runScanWindow();       // scan -> auth -> unlock (or timeout)
}
