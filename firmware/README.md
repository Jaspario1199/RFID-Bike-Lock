# Firmware

Arduino sketch for the v1 lock: `rfid_bike_lock/rfid_bike_lock.ino`.
Implements the state machine from `../DESIGN.md` §5 on the pin map from §4.2.

## Setup

1. **Arduino IDE** → board *Arduino Nano*, processor *ATmega328P* (pick
   *Old Bootloader* if upload fails on a clone).
2. **Library:** install **Adafruit PN532** via Library Manager (pulls in Adafruit BusIO).
3. **PN532 module DIP switches → I2C mode:** on Elechouse-V3-style boards set
   `SEL0 = ON (1)`, `SEL1 = OFF (0)`. Boards silk-screen this next to the switches —
   trust the silkscreen if it disagrees.

## Bench bring-up (do these in order — don't wire everything at once)

| Step | Wire up | Expect |
|---|---|---|
| 1 | Nano + PN532 only (5 V, GND, A4→SDA, A5→SCL). Temporarily jumper D7's P-MOSFET out: power PN532 straight from 5 V. Serial monitor @115200 | On button press (D3→GND): `[wake]`, then tap a fob → `[scan] uid=…`. First tag ever tapped becomes **master** |
| 2 | Add the P-MOSFET power gate on D7 | Same behavior; PN532 LED only lights during the 10 s window |
| 3 | Add LEDs (D8 red, D9 green) | Denied tag → 2 red blinks; authorized → 1 s green |
| 4 | Add IRLZ44N + flyback diode + solenoid, **on a bench supply or fresh battery** | Authorized tap → 300 ms clunk |
| 5 | Measure sleep current (multimeter in series with battery, after the window expires) | Stock Nano: ~1.5–3 mA. If you see 20 mA+, the Nano never slept — check nothing is holding D3 low |

## Behavior recap

- **Press wake button** → 10 s scan window (green blip at start).
- **Authorized tag** → solenoid pulse, green 1 s, sleep.
- **Unknown tag** → red ×2, window stays open.
- **Low battery** (<3.5 V) → red ×3 right after wake, then continues normally.
- **First boot** → red/green alternating: the first tag tapped becomes the master
  (kept even through battery swaps; stored in EEPROM).
- **Hold button 5 s during the window** → admin mode: red/green alternating, tap
  **master** to confirm, then tap any tag to add (green ×3) or remove (red ×3) it.
  Master itself can't be removed. 15 s idle exits.
- **PN532 unresponsive** → fast red ×5 (check wiring/DIP switches).

## Config knobs (top of the sketch)

`SCAN_WINDOW_MS`, `SOLENOID_PULSE_MS`, `ADMIN_HOLD_MS`, `VBAT_LOW`, `MAX_TAGS`, and
`#define DEBUG` — comment DEBUG out for the battery-powered unit.

## Factory reset

Flash `File → Examples → EEPROM → eeprom_clear` once, then re-flash the lock sketch:
next boot re-runs master enrollment.

## Known v1 limitations (by design — see DESIGN.md)

- Auth is UID-matching only; UIDs are cloneable. v2 = challenge–response (HCE app).
- No cable-state sensor: an authorized tap pulses the solenoid whether or not the
  cable head is latched. Harmless; a latch microswitch is a v2 nicety.
- Phones can't act as keys directly (iPhone: Apple blocks it; Android: random UID per
  tap) — the permanent plan is fobs + an NTAG213 sticker on the phone case.
