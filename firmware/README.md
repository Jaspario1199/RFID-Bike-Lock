# Firmware

Three builds of the same lock, same behaviour and same key set — pick the one that matches
your board:

| Sketch | Board | Reader wiring |
|---|---|---|
| `rfid_bike_lock_esp32/` | **Arduino Nano ESP32** (3.3 V) — *the one in hand* | RC522 direct, **no level shifters** |
| `rfid_bike_lock_rc522/` | classic Nano / Uno (5 V) | RC522 via 1 k / 2 k dividers |
| `rfid_bike_lock/` | classic Nano / Uno (5 V) | PN532 over I2C |

## Nano ESP32 build

1. **Boards Manager** → install **"Arduino ESP32 Boards"**, then select *Arduino Nano ESP32*.
2. **Library Manager** → install **MFRC522** (by GithubCommunity).
3. Wire the RC522 straight to the board — both are 3.3 V parts:

| RC522 | Nano ESP32 |
|---|---|
| SDA (SS) | D10 |
| SCK | D13 |
| MOSI | D11 |
| MISO | D12 |
| RST | D4 |
| 3.3V | **3V3** |
| GND | GND |

4. Panel I/O is the same as the other builds: green button D3, red button D2, red LED D8,
   green LED D9, buzzer D6, solenoid gate D5, battery sense A0.

**Differences from the AVR builds, all platform plumbing:**

- **Deep sleep resets the chip**, so the whole scan window lives in `setup()` and the sketch
  deep-sleeps at the end of it. `loop()` never runs. Wake is ext0 on the green button.
- **Tags live in Preferences (NVS)**, not EEPROM. Same 8-byte record layout.
- **The ADC is 12-bit against 3.3 V**, so the battery maths differ. The 100 k : 100 k divider
  is unchanged.
- **Factory reset:** hold **both buttons** while powering up or pressing reset, for 1.5 s.
  Alternating LEDs and three beeps confirm it; the next wake re-enrolls a master.
- **Reader power gating is off by default** (`READER_POWER_GATED 0`). The IRF4905 you have is
  marginal at 3.3 V gate drive — its threshold is −2 to −4 V and 3.3 V logic can only reach
  −3.3 V. Fit the logic-level AO3401 from the SOT-23 kit before enabling it.

⚠️ **Honest caveat on battery life.** The Nano ESP32 is not a low-power board: the onboard
USB bridge, RGB LED and regulator all draw current in deep sleep, and reported figures are
milliamps rather than the microamps the bare ESP32-S3 can reach. Measure it (BENCH_BUILD stage
7) before trusting any battery-life estimate. If it comes in high, the fix is a bare
ESP32-S3 module or the 3.3 V Pro Mini path, not a firmware change.

---


Two sketches, one state machine (`../DESIGN.md` §5, pin map §4.2):

| Sketch | Reader | Use |
|---|---|---|
| `rfid_bike_lock_rc522/` | **RC522** (the Arduino kit board, SPI) | **build this first** — it is the reader the owner has, and the rev 3c housing is sized for it |
| `rfid_bike_lock/` | PN532 (I2C) | drop-in alternative if the RC522's range through the lid disappoints |

The two files differ only in the reader driver block (`pn532On/pn532Off/readTag`).

## RC522 wiring (hardware SPI)

| RC522 pin | Nano pin | Note |
|---|---|---|
| SDA (SS) | D10 | |
| SCK | D13 | |
| MOSI | D11 | |
| MISO | D12 | |
| RST | D4 | (D9 is the green LED) |
| IRQ | — | unused |
| 3.3V | **3V3 via the AO3401 gate** (D7) — bench step 1: straight to the Nano's 3V3 pin | the RC522 is a 3.3 V part; never 5 V on its VCC |
| GND | GND | |

## Panel I/O (both sketches)

| Part | Nano pin | Wiring |
|---|---|---|
| **GREEN button** (wake / open the scan window) | D3 (INT1) | one leg to D3, the other to GND; internal pullup. Only sleep wake source |
| **RED button** (tap = cancel the window, hold 5 s = admin mode) | D2 (INT0) | same, to GND |
| Red LED | D8 | through 470 Ω to GND |
| Green LED | D9 | through 470 Ω to GND |
| **Buzzer (ACTIVE)** | D6 | (+) to D6, (−) to GND. An active buzzer makes its own tone from DC |

Sounds: chirp on wake · two chirps on unlock · long buzz on a denied tag or a dead reader ·
three on admin mode · one long on low battery.

**Passive buzzer instead?** It needs a driven square wave. Replace the body of `beep()` with
`tone(PIN_BUZZER, 2700); delay(onMs); noTone(PIN_BUZZER);`. Note `tone()` uses Timer2 —
harmless here, but it will fight any library that wants that timer. The active one is the
simpler choice for the boxed unit; keep the passive one for the bench if you want pitch.

⚠️ A buzzer is a coil: keep it off the reader's gated rail and add a 1N5819 across it if you
ever drive it through a transistor rather than straight off the pin (an active buzzer draws
~25 mA, inside the Nano's 40 mA per-pin limit).

The Nano drives the RC522's SPI inputs at 5 V logic. Every RC522 kit tutorial does this and
it works, but it is out of spec; for the boxed unit put 1 kΩ in series with SS/SCK/MOSI/RST
(the MISO line is 3.3 V → Nano, fine).

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
