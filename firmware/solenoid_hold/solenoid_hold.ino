/*
 * solenoid_hold — driver-stage test for the Nano ESP32 build.
 * Press GREEN: D5 is held HIGH for HOLD_MS so you can meter the MOSFET while it
 * is supposed to be ON. Red LED lights for the whole hold; green blinks when done.
 * Nothing else runs — no reader, no sleep, USB stays alive.
 */
const uint8_t PIN_WAKE_BTN = D3;   // GREEN button to GND
const uint8_t PIN_SOLENOID = D5;   // IRLZ44N gate via 100 Ω
const uint8_t PIN_LED_RED  = D8;
const uint8_t PIN_LED_GREEN = D9;
const uint8_t PIN_VBAT     = A0;

const uint32_t HOLD_MS = 3000;     // long enough to take a reading

void setup() {
  pinMode(PIN_WAKE_BTN, INPUT_PULLUP);
  pinMode(PIN_SOLENOID, OUTPUT);  digitalWrite(PIN_SOLENOID, LOW);
  pinMode(PIN_LED_RED, OUTPUT);   digitalWrite(PIN_LED_RED, LOW);
  pinMode(PIN_LED_GREEN, OUTPUT); digitalWrite(PIN_LED_GREEN, LOW);
  analogReadResolution(12);
  analogSetAttenuation(ADC_11db);
  Serial.begin(115200);
  delay(800);
  Serial.println("\n[hold] press GREEN: D5 HIGH for 3 s. Meter the MOSFET middle leg to GND.");
  Serial.println("[hold] expected: middle leg ~6.2 V before, under 0.5 V during, coil pulls in.");
}

void loop() {
  if (digitalRead(PIN_WAKE_BTN) != LOW) { delay(10); return; }
  delay(30);                                          // debounce
  analogRead(PIN_VBAT);
  float v = analogRead(PIN_VBAT) * (3.3f / 4095.0f) * 2.0f;
  Serial.print("[hold] vbat="); Serial.print(v); Serial.println("  D5 -> HIGH");

  digitalWrite(PIN_LED_RED, HIGH);
  digitalWrite(PIN_SOLENOID, HIGH);
  delay(HOLD_MS);
  digitalWrite(PIN_SOLENOID, LOW);
  digitalWrite(PIN_LED_RED, LOW);

  Serial.println("[hold] D5 -> LOW");
  for (int i = 0; i < 2; i++) {
    digitalWrite(PIN_LED_GREEN, HIGH); delay(100);
    digitalWrite(PIN_LED_GREEN, LOW);  delay(100);
  }
  while (digitalRead(PIN_WAKE_BTN) == LOW) delay(10);  // wait for release
}
