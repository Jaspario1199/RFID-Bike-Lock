/*
 * RFID Bike Lock — v1 firmware, Arduino Nano ESP32 build
 * Target: Arduino Nano ESP32 (ESP32-S3), 3.3 V logic
 * Reader: RC522 over SPI — wired DIRECTLY, no level shifters (both are 3.3 V parts)
 *
 * Same behaviour and same key set as the AVR builds; the differences are all
 * platform plumbing:
 *   - Sleep is ESP32 DEEP SLEEP, which resets the chip on wake. So the whole
 *     scan window lives in setup() and the sketch deep-sleeps at the end of it;
 *     loop() never runs. Waking is ext0 on the GREEN button (LOW level).
 *   - Tag storage is Preferences (NVS), not the AVR EEPROM library. Records are
 *     kept as fixed 8-byte blobs so the layout still mirrors DESIGN.md §5.
 *   - The ADC is 12-bit against 3.3 V, so the battery maths differ from AVR's
 *     10-bit / 5 V. Divider is unchanged (100k:100k).
 *
 * Power notes (WIRING.md):
 *   - The 6.2–6.5 V rail feeds VIN; the board's own regulator makes 3.3 V.
 *   - The RC522 runs from the board's 3V3 pin.
 *   - The solenoid runs from the 6 V rail through the IRLZ44N; a 3.3 V gate
 *     drives it adequately for a ~1 A coil.
 */

#include <SPI.h>
#include <MFRC522.h>
#include <Preferences.h>
#include <esp_sleep.h>

// ---------- Debug ----------
// Comment out for the battery-powered unit: USB CDC keeps the radio-side awake
// and costs current.
#define DEBUG

#ifdef DEBUG
  #define DBG(x)   Serial.print(x)
  #define DBGLN(x) Serial.println(x)
#else
  #define DBG(x)
  #define DBGLN(x)
#endif

// ---------- Pins (Nano ESP32 silkscreen names) ----------
const uint8_t PIN_WAKE_BTN   = D3;   // GREEN button to GND — the ONLY deep-sleep wake source
const uint8_t PIN_ADMIN_BTN  = D2;   // RED button to GND — tap = cancel, hold = admin
const uint8_t PIN_RC522_RST  = D4;
const uint8_t PIN_SOLENOID   = D5;   // IRLZ44N gate (HIGH = energized)
const uint8_t PIN_BUZZER     = D6;   // ACTIVE buzzer (+); HIGH = sound
const uint8_t PIN_READER_PWR = D7;   // P-FET gate, LOW = reader powered (optional; see NOTE)
const uint8_t PIN_LED_RED    = D8;
const uint8_t PIN_LED_GREEN  = D9;
const uint8_t PIN_RC522_SS   = D10;
// The ESP32 core does not always map the default SPI bus onto the Nano's D11/D12/D13
// silkscreen pins, so SPI.begin() is called with them explicitly below.
const uint8_t PIN_RC522_SCK  = D13;
const uint8_t PIN_RC522_MISO = D12;
const uint8_t PIN_RC522_MOSI = D11;
const uint8_t PIN_VBAT_SENSE = A0;   // battery / 2 via 100k:100k

// NOTE on PIN_READER_PWR: gating a 3.3 V rail with the IRF4905 is marginal (its
// gate threshold is -2..-4 V, and 3.3 V logic can only reach -3.3 V). Use the
// AO3401 from the SOT-23 kit, which is logic-level, or leave the reader
// permanently powered until the sleep-current measurement says it matters.
#define READER_POWER_GATED 0         // set to 1 once a logic-level P-FET is fitted

// ---------- Development switch ----------
// Deep sleep kills the USB peripheral, so the IDE can't reset the board into its
// bootloader and every upload fails with "No DFU capable USB device available"
// until you double-tap RESET by hand. With DEV_NO_SLEEP the board idles awake
// between scan windows instead, USB stays alive, and uploads just work.
// SET THIS TO 0 FOR THE BATTERY BUILD — idling awake costs ~10x the current.
#define DEV_NO_SLEEP 1

// ---------- Timing ----------
const uint32_t SCAN_WINDOW_MS      = 10000;
const uint32_t SOLENOID_PULSE_MS   = 300;   // try 150 once you see how hard it pulls
const uint32_t ADMIN_HOLD_MS       = 5000;
const uint32_t ADMIN_TIMEOUT_MS    = 15000;
const uint32_t SAME_UID_LOCKOUT_MS = 2000;

// ---------- Battery ----------
const float    VBAT_LOW      = 3.50;  // low-battery warning threshold (V)
const float    VBAT_DIVIDER  = 2.0;   // 100k:100k
const float    VREF          = 3.3;   // ESP32 ADC full scale with 11 dB attenuation
const int      ADC_MAX       = 4095;  // 12-bit

// ---------- Tag store (Preferences / NVS) ----------
// Keys: "magic" (u8), "count" (u8), "master" (8-byte blob), "t0".."t9" (8-byte blobs).
// Blob layout matches the AVR builds: [len][uid bytes, zero-padded to 7].
const uint8_t  NVS_MAGIC   = 0x42;
const uint8_t  UID_REC_SIZE = 8;
const uint8_t  MAX_TAGS     = 10;
Preferences store;

MFRC522 rfid(PIN_RC522_SS, PIN_RC522_RST);

// ---------- LED helpers ----------
void blink(uint8_t pin, uint8_t times, uint16_t onMs = 120, uint16_t offMs = 120) {
  for (uint8_t i = 0; i < times; i++) {
    digitalWrite(pin, HIGH); delay(onMs);
    digitalWrite(pin, LOW);  delay(offMs);
  }
}

void blinkAlternating(uint8_t cycles) {
  for (uint8_t i = 0; i < cycles; i++) {
    digitalWrite(PIN_LED_RED, HIGH);   delay(100); digitalWrite(PIN_LED_RED, LOW);
    digitalWrite(PIN_LED_GREEN, HIGH); delay(100); digitalWrite(PIN_LED_GREEN, LOW);
  }
}

// ---------- Buzzer (ACTIVE type: on/off only) ----------
void beep(uint16_t onMs, uint8_t n = 1, uint16_t gapMs = 80) {
  for (uint8_t i = 0; i < n; i++) {
    digitalWrite(PIN_BUZZER, HIGH); delay(onMs);
    digitalWrite(PIN_BUZZER, LOW);
    if (i + 1 < n) delay(gapMs);
  }
}
#define BEEP_WAKE()    beep(40)
#define BEEP_OK()      beep(60, 2, 60)
#define BEEP_DENIED()  beep(400)
#define BEEP_ADMIN()   beep(120, 3, 80)
#define BEEP_LOWBAT()  beep(700)

// ---------- Battery ----------
float readBatteryVolts() {
  analogRead(PIN_VBAT_SENSE);                  // throwaway read settles the mux
  int raw = analogRead(PIN_VBAT_SENSE);
  return raw * (VREF / (float)ADC_MAX) * VBAT_DIVIDER;
}

// ---------- Tag records ----------
static void recKey(char *buf, int slot) { snprintf(buf, 8, "t%d", slot); }

void recWrite(const char *key, const uint8_t *uid, uint8_t len) {
  uint8_t rec[UID_REC_SIZE] = {0};
  rec[0] = len;
  for (uint8_t i = 0; i < 7 && i < len; i++) rec[1 + i] = uid[i];
  store.putBytes(key, rec, UID_REC_SIZE);
}

bool recMatch(const char *key, const uint8_t *uid, uint8_t len) {
  uint8_t rec[UID_REC_SIZE] = {0};
  if (store.getBytes(key, rec, UID_REC_SIZE) != UID_REC_SIZE) return false;
  if (rec[0] != len) return false;
  for (uint8_t i = 0; i < len; i++) if (rec[1 + i] != uid[i]) return false;
  return true;
}

bool isMaster(const uint8_t *uid, uint8_t len) { return recMatch("master", uid, len); }

int findTag(const uint8_t *uid, uint8_t len) {
  uint8_t count = store.getUChar("count", 0);
  if (count > MAX_TAGS) count = 0;                    // corrupt guard
  char key[8];
  for (uint8_t s = 0; s < count; s++) {
    recKey(key, s);
    if (recMatch(key, uid, len)) return s;
  }
  return -1;
}

bool isAuthorized(const uint8_t *uid, uint8_t len) {
  return isMaster(uid, len) || findTag(uid, len) >= 0;
}

bool addTag(const uint8_t *uid, uint8_t len) {
  uint8_t count = store.getUChar("count", 0);
  if (count >= MAX_TAGS) return false;
  char key[8]; recKey(key, count);
  recWrite(key, uid, len);
  store.putUChar("count", count + 1);
  return true;
}

void removeTag(int slot) {                            // compact: move the last record down
  uint8_t count = store.getUChar("count", 0);
  if (count == 0 || slot < 0 || slot >= count) return;
  char dst[8], src[8];
  recKey(dst, slot); recKey(src, count - 1);
  if (slot != count - 1) {
    uint8_t rec[UID_REC_SIZE] = {0};
    store.getBytes(src, rec, UID_REC_SIZE);
    store.putBytes(dst, rec, UID_REC_SIZE);
  }
  store.putUChar("count", count - 1);
}

// ---------- Reader ----------
bool readerOn() {
#if READER_POWER_GATED
  digitalWrite(PIN_READER_PWR, LOW);
  delay(30);
#endif
  SPI.begin(PIN_RC522_SCK, PIN_RC522_MISO, PIN_RC522_MOSI, PIN_RC522_SS);
  rfid.PCD_Init();
  delay(10);
  byte v = rfid.PCD_ReadRegister(MFRC522::VersionReg);
#ifdef DEBUG
  DBG(F("[reader] VersionReg = 0x"));
  if (v < 0x10) DBG("0");
  Serial.println(v, HEX);
  DBGLN(F("        0x91/0x92 = genuine · 0x88/0x12 = clone, usually fine"));
  DBGLN(F("        0x00/0xFF = NOT COMMUNICATING (check SS, SCK, MOSI, MISO, RST, 3V3)"));
#endif
  if (v == 0x00 || v == 0xFF) return false;           // nothing answering on the bus
  rfid.PCD_AntennaOn();
  rfid.PCD_SetAntennaGain(MFRC522::RxGain_max);       // max gain: best chance through a lid
  return true;
}

void readerOff() {
  rfid.PCD_AntennaOff();
  rfid.PCD_SoftPowerDown();
  SPI.end();
#if READER_POWER_GATED
  digitalWrite(PIN_READER_PWR, HIGH);
#endif
}

// Poll for a tag with a bounded wait. Returns true and fills uid/len.
bool readTag(uint8_t *uid, uint8_t *len, uint16_t timeoutMs) {
  uint32_t t0 = millis();
  while (millis() - t0 < timeoutMs) {
#ifdef DEBUG
    static uint32_t lastPoll = 0;
    if (rfid.PICC_IsNewCardPresent() && millis() - lastPoll > 500) {
      lastPoll = millis();
      DBGLN(F("[reader] card detected, reading serial..."));
    }
#endif
    if (rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial()) {
      *len = rfid.uid.size;
      for (uint8_t i = 0; i < *len && i < 7; i++) uid[i] = rfid.uid.uidByte[i];
      rfid.PICC_HaltA();
      return true;
    }
    delay(20);
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
// Shared teardown: everything off, reader parked, NVS closed.
void powerDown() {
  readerOff();
  digitalWrite(PIN_LED_RED, LOW);
  digitalWrite(PIN_LED_GREEN, LOW);
  digitalWrite(PIN_SOLENOID, LOW);
  digitalWrite(PIN_BUZZER, LOW);
  store.end();
#ifdef DEBUG
  Serial.flush();
#endif
}

void goToSleep() {
  powerDown();
  DBGLN(F("[sleep] deep sleep — press GREEN to wake"));
  // ext0: wake when the GREEN button pulls its pin LOW.
  esp_sleep_enable_ext0_wakeup((gpio_num_t)digitalPinToGPIONumber(PIN_WAKE_BTN), 0);
  esp_deep_sleep_start();                              // ---- never returns ----
}

// Development idle: same teardown, but stay awake so USB survives and uploads work.
void idleUntilWake() {
  powerDown();
  DBGLN(F("[idle] awake for uploads (DEV_NO_SLEEP) — press GREEN for another window"));
  while (digitalRead(PIN_WAKE_BTN) == HIGH) delay(20);
  while (digitalRead(PIN_WAKE_BTN) == LOW)  delay(20);   // wait for release
  delay(30);                                            // debounce
  store.begin("biketags", false);
}

// ---------- Admin mode ----------
void runAdminMode() {
  DBGLN(F("[admin] entered — tap master to confirm"));
  blinkAlternating(6);
  BEEP_ADMIN();

  uint8_t uid[7]; uint8_t len;
  bool masterOk = false;
  uint32_t t0 = millis();
  while (millis() - t0 < ADMIN_TIMEOUT_MS) {
    if (readTag(uid, &len, 400) && isMaster(uid, len)) { masterOk = true; break; }
  }
  if (!masterOk) { blink(PIN_LED_RED, 2); BEEP_DENIED(); return; }

  DBGLN(F("[admin] confirmed — tap a tag to add or remove"));
  blink(PIN_LED_GREEN, 1, 400, 0);
  BEEP_ADMIN();

  t0 = millis();
  while (millis() - t0 < ADMIN_TIMEOUT_MS) {
    if (!readTag(uid, &len, 400)) continue;
    t0 = millis();

    if (isMaster(uid, len)) { blink(PIN_LED_RED, 1); continue; }   // master not removable

    int slot = findTag(uid, len);
    if (slot >= 0) {
      removeTag(slot);
      DBGLN(F("[admin] removed"));
      blink(PIN_LED_RED, 3);
      beep(300);
    } else if (addTag(uid, len)) {
      DBGLN(F("[admin] added"));
      blink(PIN_LED_GREEN, 3);
      BEEP_OK();
    } else {
      DBGLN(F("[admin] full"));
      blink(PIN_LED_RED, 5, 60, 60);
    }
  }
  DBGLN(F("[admin] exit"));
  blinkAlternating(3);
  BEEP_ADMIN();
}

// ---------- First-boot master enrollment ----------
void enrollMaster() {
  DBGLN(F("[enroll] FIRST BOOT — present a fob to make it the MASTER key"));
  DBGLN(F("[enroll] (red/green alternating until one is read)"));
  uint8_t uid[7]; uint8_t len;
  while (true) {
    blinkAlternating(2);
    if (readTag(uid, &len, 400)) break;
  }
  recWrite("master", uid, len);
  store.putUChar("count", 0);
  store.putUChar("magic", NVS_MAGIC);
  DBGLN(F("[enroll] master stored"));
  blink(PIN_LED_GREEN, 5);
  BEEP_OK();
}

// ---------- Scan window ----------
void runScanWindow() {
  float v = readBatteryVolts();
  DBG(F("[wake] vbat=")); DBGLN(v);
  if (v < VBAT_LOW) { blink(PIN_LED_RED, 3); BEEP_LOWBAT(); }

  if (!readerOn()) {
    DBGLN(F("[err] RC522 not responding"));
    blink(PIN_LED_RED, 5, 60, 60);
    BEEP_DENIED();
    return;
  }

  if (store.getUChar("magic", 0) != NVS_MAGIC) enrollMaster();

  uint8_t uid[7]; uint8_t len;
  uint8_t lastUid[7] = {0}; uint8_t lastLen = 0;
  uint32_t lastReadAt = 0;
  uint32_t windowStart = millis();
  uint32_t btnDownAt = 0;

  digitalWrite(PIN_LED_GREEN, HIGH); delay(60); digitalWrite(PIN_LED_GREEN, LOW);
  BEEP_WAKE();

  while (millis() - windowStart < SCAN_WINDOW_MS) {

    // RED button: tap = cancel the window, hold ADMIN_HOLD_MS = admin mode
    if (digitalRead(PIN_ADMIN_BTN) == LOW) {
      if (btnDownAt == 0) btnDownAt = millis();
      else if (millis() - btnDownAt >= ADMIN_HOLD_MS) {
        runAdminMode();
        return;
      }
    } else {
      if (btnDownAt != 0) {
        DBGLN(F("[scan] cancelled (red)"));
        blink(PIN_LED_RED, 1); beep(150);
        return;
      }
      btnDownAt = 0;
    }

    if (!readTag(uid, &len, 300)) continue;

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
      BEEP_OK();
      digitalWrite(PIN_LED_GREEN, HIGH); delay(1000); digitalWrite(PIN_LED_GREEN, LOW);
      return;
    } else {
      DBGLN(F("[auth] denied"));
      blink(PIN_LED_RED, 2);
      BEEP_DENIED();
    }
  }
  DBGLN(F("[scan] window expired"));
}

// ----------------------------------------------------------------------
// Deep sleep resets the chip, so setup() IS the main loop: it runs one scan
// window per wake and then sleeps again. loop() is never reached.
void setup() {
  pinMode(PIN_WAKE_BTN, INPUT_PULLUP);
  pinMode(PIN_ADMIN_BTN, INPUT_PULLUP);
  pinMode(PIN_SOLENOID, OUTPUT);   digitalWrite(PIN_SOLENOID, LOW);
  pinMode(PIN_BUZZER, OUTPUT);     digitalWrite(PIN_BUZZER, LOW);
  pinMode(PIN_LED_RED, OUTPUT);    digitalWrite(PIN_LED_RED, LOW);
  pinMode(PIN_LED_GREEN, OUTPUT);  digitalWrite(PIN_LED_GREEN, LOW);
#if READER_POWER_GATED
  pinMode(PIN_READER_PWR, OUTPUT); digitalWrite(PIN_READER_PWR, HIGH);   // reader off
#endif

  analogReadResolution(12);
  analogSetAttenuation(ADC_11db);          // full 0–3.3 V range on A0

#ifdef DEBUG
  Serial.begin(115200);
  uint32_t t0 = millis();
  while (!Serial && millis() - t0 < 1500) { }   // USB CDC needs a moment, but don't hang on battery
  DBGLN(F("\n[boot] RFID bike lock — Nano ESP32"));
  DBG(F("[boot] wake cause = ")); DBGLN((int)esp_sleep_get_wakeup_cause());
#endif

  store.begin("biketags", false);          // NVS namespace, read/write

  // Factory reset: hold BOTH buttons while pressing the board's reset, or while
  // powering up. Wipes the master and every enrolled tag.
  if (digitalRead(PIN_WAKE_BTN) == LOW && digitalRead(PIN_ADMIN_BTN) == LOW) {
    delay(1500);                                       // must be held, not brushed
    if (digitalRead(PIN_WAKE_BTN) == LOW && digitalRead(PIN_ADMIN_BTN) == LOW) {
      store.clear();
      DBGLN(F("[reset] tag store cleared — next wake re-enrolls the master"));
      blinkAlternating(10);
      beep(200, 3, 120);
      goToSleep();
    }
  }

#if DEV_NO_SLEEP
  while (true) {                           // USB stays alive; uploads work normally
    runScanWindow();
    idleUntilWake();
  }
#else
  runScanWindow();
  goToSleep();                             // ---- never returns ----
#endif
}

void loop() { }                            // unreachable in both paths
