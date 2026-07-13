# RFID Bike Lock — Design Document

*Rev 0.1 — first full write-up of the concept. Everything here is open to change; sections
marked ⚠️ are known problems we still need to solve.*

---

## 1. Concept summary

A permanently frame-mounted bike lock. The housing is a stainless-steel clamshell cylinder
that clamps around the bike's down tube over a compressible liner. Inside:

- **Bottom pod:** a spool holding ~1.5 m of plastic-coated steel cable, wound against a
  spiral return spring (tape-measure / retractable-dog-leash style) so the cable
  self-retracts.
- **Top pod:** the electronics — Arduino Nano, PN532 NFC reader (face-up, so you tap the
  top of the lock), a pull-type linear solenoid, an 18650 battery with USB-C charging, and
  the cable latch.

**Locking is mechanical and needs no power:** the cable's mushroom-shaped head has a
ramped face, so pushing it into the latch shoves the spring-loaded locking pin aside until
the pin snaps into the head's groove. **Unlocking needs power:** tap an authorized
tag/fob, the solenoid pulls the pin for ~300 ms, a small ejector spring pops the head out,
and the spool reels the cable home.

```
                       tap fob here
                            ▼
                ┌───────[PN532 face]──────┐
                │  latch ○   electronics  │   ← top pod (latch, solenoid,
                ├─────────────────────────┤      Nano, PN532, 18650)
   screws ──►  ═╪═════════════════════════╪═   ← overlap flange + screws
                │ ░░░ compressible liner ░│
                │ ░░┌─────────────────┐░░ │
                │ ░░│   BIKE FRAME    │░░ │   ← clamp section
                │ ░░│    (down tube)  │░░ │
                │ ░░└─────────────────┘░░ │
                ├────hinge─────────hinge──┤   ← hinges along the bottom
                │      cable spool +      │
                │      spiral spring      │   ← bottom pod
                └───────────○─────────────┘
                            ▲
                     cable exits here
```

---

## 2. User workflow

### One-time install
1. Open the clamshell (hinges on the bottom), fit the EPDM foam liner for your tube size.
2. Close it around the down tube, drive the security-Torx screws through the top overlap
   flange. The liner compresses ~30% and grips the frame.
3. Enroll your tags (see below).

### Locking the bike (no power used)
1. Pull the cable out of the bottom pod (spool spring provides light resistance).
2. Loop it through the front wheel and/or around a rack.
3. Push the cable head into the top latch until it clicks. Done — the electronics never
   woke up.

### Unlocking
1. Press the **wake button** on the top face. Status LED blinks green: reader is live for
   a 10-second scan window.
2. Tap your fob / NFC sticker / (Android) phone on the top face.
3. Authorized → solenoid pulses, head pops out, cable auto-retracts, LED solid green 1 s.
4. Unauthorized → LED blinks red twice, window stays open until the 10 s expire.
5. No tap within 10 s → everything goes back to sleep.

### Enrolling / removing tags
- Hold the wake button for 5 s → LED alternates red/green → tap the **master fob**
  (enrolled at first boot) → now in admin mode:
  - Tap an unknown tag → added (green triple-blink).
  - Tap a known tag → removed (red triple-blink).
  - 15 s idle → exit admin mode.
- Tag UIDs are stored in the Nano's EEPROM (survives battery death). Capacity: dozens of
  tags; we'll cap at 10.

### Charging / low battery
- LED gives a red triple-blink after any wake when the battery is below ~3.5 V.
- Charge through the USB-C port (TP4056 board) with the same cable as your phone.
- Battery state is checked on every wake via a voltage divider.

---

## 3. RFID/NFC reader choice — and the truth about phones

**Chosen module: PN532** (Elechouse V3 or clone, ~$8, 40 × 43 mm, I2C mode).

You asked for the lowest-power small reader **that can read your phone**. Reading a phone
means NFC (13.56 MHz, ISO 14443), and among hobby modules only the PN532 speaks the
protocols phones use. The popular cheap RC522 **cannot** talk to phones.

⚠️ **Honest phone caveats — read this before counting on phone-unlock:**

| Key type | Works? | Notes |
|---|---|---|
| MIFARE Classic fob / card (~$0.50) | ✅ Reliable | The v1 workhorse. |
| NTAG213 **sticker** on your phone case (~$0.30) | ✅ Reliable | This is the practical way to "unlock with your phone." |
| **Android phone** via HCE app | ⚠️ Possible, v2 | Android randomizes its UID on every tap, so simple UID matching fails. It works properly with a small companion app doing challenge–response (APDU/AID) — a genuinely better-than-fob security level, but real firmware+app work. Planned for v2. |
| **iPhone** | ❌ Not feasible | Apple only lets Wallet passes act as cards; a hobby lock can't enroll one. Use the sticker approach. |

**Power reality:** the PN532's RF field draws 50–100 mA while scanning — you cannot leave
it polling 24/7 on a battery. Two design decisions fix this:

1. The PN532's power rail is **switched by a P-MOSFET** — it is fully off except during
   the 10 s scan window (its own "low-power" modes still leak too much on clone boards).
2. Scanning only happens after a **wake-button press**. No button, no field, no drain.

---

## 4. Electronics

### 4.1 Block diagram

```
                    USB-C
                      │
              ┌───────▼────────┐
              │ TP4056 charger │
              │  + DW01 protect│
              └───────┬────────┘
                      │
               18650 Li-ion (2500 mAh, 3.0–4.2 V)
                      │
        ┌─────────────┼──────────────────────┐
        │             │                      │
        │      ┌──────▼──────┐        ┌──────▼──────┐
        │      │ MT3608 boost│        │  N-MOSFET   │◄── D5 (300 ms pulse)
        │      │   → 5 V     │        │  IRLZ44N    │
        │      └──────┬──────┘        └──────┬──────┘
        │             │                      │
        │      ┌──────▼──────────┐    ┌──────▼──────┐
        │      │  Arduino Nano   │    │  Solenoid   │ + flyback diode
        │      │  (5V pin)       │    │  JF-0530B   │ + 1000 µF reservoir cap
        │      └──┬───┬───┬───┬──┘    └─────────────┘
        │         │   │   │   │
        │   I2C ──┘   │   │   └── D3: wake button (pin-change interrupt)
        │   (A4/A5)   │   └────── D8/D9: red/green status LEDs
        │      │      └── D7 ──► P-MOSFET gate (PN532 power switch)
        │  ┌───▼────┐
        │  │ PN532  │◄── 5 V via P-MOSFET (off when asleep)
        │  └────────┘
        └── A0: battery voltage divider (2 × 100 kΩ)
```

### 4.2 Pin map

| Nano pin | Connects to | Purpose |
|---|---|---|
| A4 (SDA), A5 (SCL) | PN532 (I2C mode, DIP switches set to I2C) | Tag reading |
| D7 | P-MOSFET gate (e.g. AO3401 + pullup) | Hard power switch for PN532 |
| D3 (INT1) | Wake pushbutton → GND (internal pullup) | Wake from power-down sleep |
| D5 | IRLZ44N gate via 100 Ω, 100 kΩ pulldown | Solenoid pulse |
| D8 / D9 | Red / green LED via 470 Ω | Status |
| A0 | 100 kΩ/100 kΩ divider from battery + | Battery voltage sense |
| 5V | MT3608 output | System power |

Solenoid wiring: battery + → solenoid → IRLZ44N drain, source → GND. 1N5819 flyback diode
across the solenoid coil (cathode to +). 1000 µF electrolytic across battery input near
the solenoid to stiffen the pulse.

**Note the solenoid runs straight off the battery, not the boost converter** — a 5 V
solenoid at 3.7–4.2 V still yields ~80% of rated force, and this keeps the ~1 A pulse off
the MT3608 (which would brown out the Nano mid-unlock). The pin return spring is sized to
what the solenoid actually pulls at 3.5 V (worst-case battery) — measure in prototyping.

### 4.3 Solenoid

- **JF-0530B pull-type**, 5 V winding, ~4.5 Ω coil → ~0.9 A at nominal battery voltage,
  ~5 N pull at small air gap, 3–5 mm stroke, 30 × 15 × 14 mm, ~$4.
- Energized for **300 ms max** per unlock. Duty cycle is effectively zero, so no heating
  concerns.
- Energy per unlock ≈ 0.9 A × 0.3 s ≈ **0.075 mAh** — even 20 unlocks/day is only
  1.5 mAh/day, i.e. the solenoid is *not* the battery problem; standby drain is.

### 4.4 Power budget & battery life

Battery: one protected 18650, 2500 mAh nominal, ~2000 mAh usable above the 3.3 V cutoff we
care about.

| State | Draw | Time share |
|---|---|---|
| Sleep (Nano power-down, PN532 off, boost quiescent) | ~1.5–3 mA (stock Nano; the USB chip + regulator leak) | ~99.9% |
| Scan window (Nano awake + PN532 field on) | ~90–130 mA | 10 s × ~6/day |
| Solenoid pulse | ~900 mA | 0.3 s × ~6/day |

Daily consumption ≈ (2.5 mA × 24 h) + (0.11 A × 60 s)/3600 + (0.9 A × 1.8 s)/3600
≈ 60 + 1.8 + 0.45 ≈ **62 mAh/day → roughly 4–5 weeks per charge.**

The standby leak dominates everything. Upgrade path (v2): swap the Nano for a **3.3 V/8 MHz
Pro Mini with its regulator and power LED removed** → sleep current drops to ~10 µA,
boost converter deleted (everything runs at battery voltage), and battery life becomes
**6–12 months**. The firmware is identical. Recommended as soon as the breadboard
prototype works.

⚠️ Winter note: Li-ion loses capacity below 0 °C and must not be *charged* below 0 °C.
Fine for College Station; document it anyway.

---

## 5. Firmware design (state machine)

```
 POWER_ON ──► first boot? ──yes──► ENROLL_MASTER (first tag tapped = master, store in EEPROM)
     │                                   │
     ▼                                   ▼
   SLEEP  ◄──────────────────────────────┘
     │  (power-down, all peripherals off, ~µA on Pro Mini)
     │  wake button (INT1)
     ▼
   WAKE ──► check battery (A0) ──► low? blink red 3× (but continue)
     │
     ▼
   SCAN (PN532 powered, 10 s window)
     │ tag read
     ▼
   AUTH ──► UID in EEPROM list? ──no──► blink red 2×, back to SCAN
     │ yes
     ▼
   UNLOCK: solenoid HIGH 300 ms → LED green 1 s → SLEEP

   (button held 5 s during WAKE) ──► ADMIN: master tap required,
        then tap-to-add / tap-to-remove, 15 s timeout → SLEEP
```

Implementation notes:
- `avr/sleep.h` power-down mode + pin-change wake on D3; disable ADC/brown-out during sleep.
- Adafruit_PN532 library, I2C mode.
- EEPROM layout: `[magic byte][count][master UID 7B][UID slots 10 × 7B]`.
- Debounce unlocks: ignore repeat reads of the same UID for 2 s.
- v2 (Android HCE): replace UID matching with an APDU SELECT of our custom AID + an HMAC
  challenge–response against a key shared with the companion app. Also fixes clone-ability
  of MIFARE UIDs.

⚠️ **Security honesty:** v1 authenticates by UID only, and MIFARE UIDs can be cloned with
a $20 gadget by someone who taps your fob. For a bike lock this is an acceptable v1 risk
(the cable is the weaker link anyway — see §7), but v2 challenge–response closes it.

---

## 6. Mechanical design

**v1 housing is 3D printed** (see §6.2 print spec); the stainless shell moves to a later
phase once the geometry is proven. All dimensions below apply to both.

### 6.1 Overall envelope

**One-size-fits-all requirement:** one product, no size variants, snug on the range of
average down tubes. Design targets:

- **Core range: Ø32–46 mm** (modern alu/steel road + most MTB) with the standard liner
- **Extended range: Ø27–32 mm** (skinny steel/vintage frames) via an included clip-in shim
  sleeve — still "in the box," no separate SKU
- Out of scope for v1: non-round aero/carbon tubes (Ø50 mm+ ovals). Flagged, not solved.

No single feature spans Ø27–46 mm, so the fit stacks **three** mechanisms — see §6.2.

| Element | Dimension | Notes |
|---|---|---|
| Clamp shell ID | Ø54 mm | v1: printed, 4 mm wall → OD Ø62 mm. Steel version: 304, 1.5 mm wall → OD Ø57 mm |
| Clamp length | 110 mm | longer = more grip on the frame, less rocking |
| Liner | Printed TPU ribbed sleeve, 12 mm radial fins (§6.2) | free bore Ø30 mm; grips Ø32–46 mm tubes |
| Shim sleeve | Clip-in TPU ring, 3 mm solid + its own 4 mm fins | extends range down to Ø27 mm |
| Hinges | Printed knuckles + Ø3 mm stainless pin along the bottom seam (steel version: riveted piano hinge) | |
| Closure | Top overlap flanges, 4 × M4 × 12 security-Torx into **brass heat-set inserts**; **slotted holes give 0–8 mm of flange-gap adjustment** | slots ≈ ±2.5 mm of effective clamp diameter; also takes up liner wear over the years. ⚠️ see §7 tamper note |
| Top pod (electronics) | 115 × 55 × 32 mm box printed/welded onto shell top | Fits Nano 45×18, PN532 43×40 face-up under a 2 mm ABS window (RF passes through plastic, NOT through steel — the lid over the antenna must be plastic even on the steel version), 18650 65×18, solenoid, boards |
| Bottom pod (spool) | Ø95 mm × 34 mm drum hanging under shell | |
| Total added weight | v1 printed ~500–650 g; steel ~750–900 g | comparable to a mid U-lock |

### 6.2 One-size-fits-all liner — material & geometry

**Why solid foam fails this requirement:** a foam thick enough to grip a Ø32 mm tube
inside a Ø54 mm shell is 11 mm thick; on a Ø46 mm tube that same foam must squash to
4 mm — ~65% compression, held permanently, outdoors. Every foam takes *compression set*
under those conditions (it never springs back), so the lock is loose within months. Foam
also can't be "cut to tube size" in a one-size product — that was the old spec, now dead.

**Chosen approach: a printed TPU finned liner.** Instead of compressing material
volumetrically, angled rubber fins *bend* out of the way — like the ribs inside a bike
computer mount. Bending strain is far below the material's set threshold, so fins stay
springy for years, and the grip force is nearly constant across the whole tube range.

```
   shell wall ─►│
               │╲╲╲╲╲╲╲   ← fins angled ~30° off radial,
               │ ╲╲╲╲╲╲     12 mm tall, 1.4 mm thick,
               │  (tube)     ~24 around the circumference
               │ ╱╱╱╱╱╱      small tube: fins barely deflect
               │╱╱╱╱╱╱╱      big tube: fins fold to ~35° — still elastic
```

| Liner spec | Value |
|---|---|
| Material | TPU 95A (printable on any hobby printer that does flexibles) |
| Form | Two half-sleeves, dovetail-keyed into each shell half (replaceable — a wear part by design) |
| Fins | 12 mm tall × 1.4 mm thick, 30° lean, 24 per circumference, running axially |
| Base | 2 mm solid backing bonded/keyed to shell |
| Free bore | Ø30 mm → 1–2 mm fin preload even on the smallest core-range tube |
| Grip aids | Fin tips textured; TPU is naturally high-friction on paint without marring it |

Material trade study (for the record):

| Material | Snug across range | Lasts outdoors (set/UV/temp) | Cost | Verdict |
|---|---|---|---|---|
| **TPU 95A printed fins** | ✅ bending, not crushing | ✅ excellent abrasion/tear, good UV, fins replaceable | ~$2 of filament | **v1 and probably final** |
| Silicone sponge sheet | ⚠️ ~50% compression max | ✅ best-in-class compression set (<10%), −60…+200 °C | ~3× EPDM | Backup for steel version if fins underperform |
| EPDM closed-cell foam | ⚠️ same limit | ⚠️ good UV but 20–40% set at high compression → loosens | cheap | Demoted: fine for a quick mock-up only |
| Neoprene foam | ⚠️ | ❌ worse UV than EPDM | cheap | No |

The three stacked fit mechanisms, in order of action:

1. **Fins** absorb the big spread (Ø32–46 mm) elastically.
2. **Slotted closure** (±2.5 mm effective diameter) tunes preload at install time and
   re-tightens years later if the fins relax.
3. **Shim sleeve** (included) clips over the fins for Ø27–32 mm skinny tubes.

**v1 print spec (housing):** PETG for the first print (easy), **ASA for the outdoor
unit** (UV-stable; PETG chalks and creeps in Texas sun). 4 mm walls / 6 perimeters, 40%
gyroid infill, brass heat-set inserts for every screw (printed threads don't survive
re-tightening), printed hinge knuckles with a stainless pin. The latch keeps its
**steel** receiver bushing and pin even in the printed housing — plastic there would let
someone pry the head out with a screwdriver. Obvious caveat, stated once: a plastic
housing is a functional model, not a security device; the steel shell is what makes the
housing itself attack-resistant.

### 6.3 Cable and spool

| Item | Spec |
|---|---|
| Cable | 4 mm 7×7 stainless wire rope, clear PVC jacket to Ø5 mm, 1.8 m on spool / ~1.5 m usable |
| Spool | Core Ø40 mm, flanges Ø85 mm, 26 mm between flanges → 1.8 m fits in ~2 layers |
| Return spring | Spiral power spring (constant-force preferred), 15 × 0.15 mm strip — the spring+spool unit from a heavy retractable dog leash or badge reel is a perfect donor for prototyping |
| Cable exit | Brass-lined grommet at bottom of pod, angled 30° down so the cable doesn't kink |
| Cable head | Hardened steel "mushroom": Ø10 mm head, ramped 45° nose, 3 mm-deep annular groove Ø7 mm behind the head |

Minimum bend: 4 mm 7×7 rope tolerates the Ø40 mm core (10× rule of thumb) — this is why
the core can't be smaller.

### 6.4 Latch + locking pin (the heart of it)

```
        cable head (mushroom)          hardened receiver bushing
              ══►  ╭──╮      ┌───────────────┐
   insert ─────────┤  ├──────►   ○ groove    │
              ══►  ╰──╯      └──────┬────────┘
                                    │ Ø4 mm hardened pin, 3 mm engagement
                              ┌─────┴─────┐
                              │ pin spring│  (locks: spring pushes pin into groove)
                              ├───────────┤
                              │ solenoid  │  (unlocks: pulls pin against spring)
                              └───────────┘
```

- **Insert (lock):** the 45° ramp on the head cams the pin back; pin snaps into the groove.
  Zero power. A weak ejector spring behind the head is compressed as it seats.
- **Remove (unlock):** solenoid pulls the pin 4 mm; ejector spring pops the head ~5 mm out
  so it can't instantly re-latch; spool retracts the cable.
- Pin: Ø4 mm hardened dowel (drill blank), engagement 3 mm into the groove. Shear area is
  ample — the attack that matters is cutting the cable, not shearing the pin.
- Pin spring: sized so the solenoid still wins at 3.5 V battery (~4 N pull) → choose
  ~2 N spring preload. Prototype and measure.
- Receiver bushing: hardened steel insert so a screwdriver can't gouge the latch open.

### 6.5 RFID face

The PN532 antenna sits directly under a **plastic** window on the top face (13.56 MHz does
not pass through stainless). Keep all steel ≥10 mm clear of the antenna loop or read range
collapses; expect 1–3 cm range through 2 mm ABS. The wake button and LED sit beside the
window.

---

## 7. Security analysis — honest version

| Attack | Resistance | Mitigation / status |
|---|---|---|
| Bolt-cut the 4 mm cable | ❌ seconds | **This is the real limit of any cable lock.** 4 mm is a deterrent (opportunists, café stops), not U-lock security. Going to 6 mm cable roughly doubles cut resistance but grows the spool pod to ~Ø120 mm. ⚠️ Decide after seeing the v1 size on a real bike. |
| Unscrew the housing from the frame | ⚠️ | Security-Torx helps but isn't enough. **Design intent: place the 4 closure screws under the latch area so the locked cable head physically covers them.** Needs careful layout in CAD — flagged as a v1 requirement. |
| Cut the printed (plastic) housing | ❌ v1 only | Inherent to the printed model — it's a functional prototype, not a security device (§6.2). The steel shell closes this. |
| Clone a fob UID | ⚠️ | Real but low-likelihood for a bike; fixed by v2 challenge–response (§5). |
| Drain/wait out the battery | depends | See §8 — this is why fail-open is dangerous. |
| Smash the electronics pod | ⚠️ | Breaking the solenoid/pin area could jam it *locked*, not open it (pin is spring-into-lock). Acceptable failure direction. |

Positioning: this is a **convenience lock** — always on the bike, zero-effort, good enough
for short stops and low-theft areas, and a great engineering project. It should be honest
about not replacing a U-lock for overnight street parking.

---

## 8. Dead-battery behavior ⚠️ (open decision — revisit)

Current choice on record: **unlocks when the battery dies.** Two serious problems with
that, one of security and one of physics:

1. **Security:** if a dead battery unlocks the cable, a thief doesn't need bolt cutters —
   they wait, or chill the pack, or just come back in a month. The lock's security would
   equal its battery life.
2. **Physics:** the natural solenoid arrangement (energize-to-unlock, spring-to-lock) is
   inherently **fail-secure** — no power means the pin stays in. Making it fail-open
   requires either holding the solenoid energized the whole time the bike is locked
   (battery dies in hours, not weeks) or a bistable/motorized latch plus supervisory
   circuitry that fires a "last gasp" unlock as voltage collapses — more parts, more cost,
   and it *still* unlocks your bike in public when it triggers.

**Recommended resolution — fail-secure + external power escape hatch:** keep
spring-locked/solenoid-unlocked, and make the TP4056's USB-C port double as an emergency
input: a phone power bank plugged into the port runs the whole system even with a stone-dead
cell, so you can unlock immediately, no waiting for charge. Costs nothing extra — the
charge port already exists; we just route it so the system bus is alive during charging.

Alternative if you want a no-electronics backstop: a small cam lock (tubular key) that
manually retracts the same pin, hidden under a rubber plug. ~$4, adds a keyway that is
itself a (pickable) attack surface.

**Decision needed before the latch is CADed** — the escape-hatch options change the top-pod
layout. My recommendation: fail-secure + USB-C power bank unlock, optionally + the hidden
cam lock in v1 while the electronics are still unproven.

---

## 9. Open questions

1. §8 fail-safe decision — blocks latch CAD.
2. 4 mm vs 6 mm cable — blocks spool pod sizing.
3. Your phone: Android or iPhone? Determines whether v2 phone-unlock (HCE app) is worth
   building or whether stickers/fobs are the permanent plan.
4. Measure your own down tube anyway (circumference ÷ π) — a sanity check that it lands
   inside the Ø32–46 mm core range, and the first fit-test article.
5. Aero/oval and Ø50 mm+ tubes are declared out of scope for v1 (§6.1) — confirm you're
   fine with that, or the shell ID has to grow.
6. Does your printer (or the TAMU makerspace's) print TPU? If not, the fallback liner for
   the first article is silicone sponge sheet.

*Resolved:* one-size-fits-all fit strategy → finned TPU liner + slotted closure + shim
sleeve (§6.2). First housing is 3D printed → print spec in §6.2.

## 10. Build plan

| Phase | Goal | Cost |
|---|---|---|
| 0 — Breadboard | Nano + PN532 + MOSFET + solenoid on a bench PSU; firmware v1 working end-to-end | ~$25 electronics |
| 1 — **Printed v1** (the first real model) | ASA/PETG clamshell + TPU finned liner + donor-leash spool + latch; whole system living on the actual bike; measure solenoid force vs pin spring; fit-test the liner on every bike we can find (target: 5+ different tubes across Ø32–46 mm) | ~$15 filament + hardware |
| 2 — Steel housing | 304 shell (rolled sheet or machined), hardened bushing + pin, final cable; liner carries over unchanged | TBD, ~$40–80 depending on fabrication access (TAMU shop?) |
| 3 — v2 electronics | Pro Mini 3.3 V swap (months of battery), Android HCE challenge–response app | ~$10 |
