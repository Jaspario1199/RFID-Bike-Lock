# RFID Bike Lock — Design Document

> **v0.8 fastening rebuild (owner request):** every threaded joint is now an M3 machine
> screw into an M3 brass heat-set insert (super-refined printed prototype). Two carve-outs,
> both forced by an external part: the solenoid stays M2.5 (its tabs are drilled M2.5) and
> the PN532 stays M3 nylon into printed bosses (brass at the antenna corners kills read
> range). See cad/README.md "v0.8" and BOM items 23a–g. Gate after conversion: 0/292.

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
hook joint ──► ═╪═════════════════════════╪═   ← flanges interlock; the only screw
   (no exposed screws)                           hides at the bottom of the latch bore
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
1. Open the clamshell (hinges on the bottom); clip in the shim sleeve first if your tube
   is skinny (Ø27–32 mm — vintage/steel frames).
2. Close it around the down tube: slide the flanges' hook joint together, pick the tongue
   detent that gives a snug fit, and drive the single M4 closure screw home at the bottom
   of the latch bore (long 2.5 mm hex key). The liner fins deflect and grip the frame.
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

**Resolved:** the owner carries an iPhone, so the permanent key plan is **NTAG213 sticker
on the phone case + keychain fobs**. The Android HCE companion app is dropped from the
roadmap (kept below as reference only, in case an Android user ever builds this).

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
        ┌─────────────┤
        │             │
        │      ┌──────▼──────┐
        │      │ MT3608 boost│   + 1000 µF reservoir cap on the 5 V rail
        │      │   → 5 V     │
        │      └──────┬──────┘
        │             ├──────────────────────┐
        │             │               ┌──────▼──────┐
        │             │               │  N-MOSFET   │◄── D5 (300 ms pulse)
        │             │               │  IRLZ44N    │
        │             │               └──────┬──────┘
        │      ┌──────▼──────────┐    ┌──────▼──────┐
        │      │  Arduino Nano   │    │  Solenoid   │ JF-0530B 6 V coil
        │      │  (5V pin)       │    │  (~250 mA)  │ + flyback diode
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

Solenoid wiring: 5 V rail → solenoid → IRLZ44N drain, source → GND. 1N5819 flyback diode
across the solenoid coil (cathode to +). 1000 µF electrolytic across the 5 V rail near
the solenoid to stiffen the pulse.

**The solenoid runs off the regulated 5 V rail.** The JF-0530B has no 5 V winding — it
ships as 6 V / 12 V / 24 V — so we use the **6 V variant** at 5 V: ~20 Ω coil → ~250 mA,
which the MT3608 (2 A switch) supplies without disturbing the Nano, and the pulse strength
no longer sags with battery voltage. Expect roughly 70% of rated force at 5 V on a 6 V
coil; the pin return spring is sized to what the solenoid *actually* pulls — measure in
prototyping. If the measured pull is short, the fallback is the 12 V variant fed by its
own dedicated mini-boost, pulsed the same way.

### 4.3 Solenoid

- **JF-0530B pull-type, 6 V winding** (no 5 V version exists; 6/12/24 V are the options),
  ~20 Ω coil → ~250 mA on our 5 V rail. Rated 5 N force / 10 mm max stroke — we use ~4 mm
  of it, where pull is strongest. ⚠️ Clone specs vary wildly between sellers (some list
  the 12 V coil at 1 A); measure the actual pull force of the unit you receive.
- Verified dimensions: **body 30 × 13 × 15 mm, plunger Ø6 × 58 mm** — the full
  body+plunger train is ~65 mm long, which drives the layout in §6.5. The plunger tail can
  be trimmed to length (it's plain rod). M2.5 mounting holes, 20 cm leads.
- Energized for **300 ms max** per unlock. Duty cycle is effectively zero, so no heating
  concerns.
- Energy per unlock ≈ 0.25 A × 0.3 s ≈ **0.02 mAh** — even 20 unlocks/day is under
  0.5 mAh/day, i.e. the solenoid is *not* the battery problem; standby drain is.

### 4.4 Power budget & battery life

Battery (v0.4): one protected **103450 LiPo pouch, 2000 mAh** nominal, ~1600 mAh usable
above the cutoff (the 18650 of earlier revs doesn't package in the v0.4 bottom bay).

| State | Draw | Time share |
|---|---|---|
| Sleep (Nano power-down, PN532 off, boost quiescent) | ~1.5–3 mA (stock Nano; the USB chip + regulator leak) | ~99.9% |
| Scan window (Nano awake + PN532 field on) | ~90–130 mA | 10 s × ~6/day |
| Solenoid pulse | ~250 mA | 0.3 s × ~6/day |

Daily consumption ≈ (2.5 mA × 24 h) + (0.11 A × 60 s)/3600 + (0.25 A × 1.8 s)/3600
≈ 60 + 1.8 + 0.13 ≈ **62 mAh/day → roughly 3.5–4 weeks per charge on the 2000 mAh LiPo.**

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

*CAD v0.6 (CadQuery/STEP) implements this section as a **12-printed-part + 1-lathe-part
assembly** (was a 13-part all-printed count through v0.3 — the two Ø3 mm hinge pins and
their glued end plugs are gone, replaced by one lathe-turned hinge rod + a screwed cap;
no glue anywhere in the current assembly): the two shells stay structural/integral (clamp
+ pod + belt + latch boss), the spool drum is a separate zero-support module bolted from
inside the clamp bore (screws reachable only when unlocked), and all interior furniture
is drop-in cartridges on a standard pad system — full rationale in ASSEMBLY.md and
cad/README.md.*

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
| Clamp length | 150 mm | sized by the top pod (§6.6 packing study): battery + latch + antenna zones can't overlap, so the pod needs 150 mm and the clamp matches it. Bonus: more grip, less rocking |
| Liner | Printed TPU ribbed sleeve, 12 mm radial fins (§6.2) | free bore Ø30 mm; grips Ø32–46 mm tubes |
| Shim sleeve | Clip-in TPU ring, 3 mm solid + its own 4 mm fins | extends range down to Ø27 mm |
| Hinges | Printed knuckles + **one Ø4.0 mm 303-stainless rod** (~152 mm, integral Ø6×1.6 head, running fit in a finished Ø4.2 bore) the full length of the bottom seam, retained by a screwed hinge cap at the rear (§6.8/§6.9); steel version: same single-rod axis, riveted piano hinge | replaces the two Ø3 mm pins + glued end plugs (through v0.5) |
| Closure | Full-length hooked tongue-and-groove flange joint + **one M4×8 screw into a short M4 heat-set at the bottom of the latch bore** (§6.4) | the locked cable head covers the only screw → housing can't be opened while the bike is locked. Preload adjustment: **3 tongue detent depths only** (≈ ±2.5 mm effective clamp diameter) — the single fixed-diameter hinge rod removes the hinge-side preload freedom v0.5 relied on; the detents remain the sole adjustment and are still unmodeled in CAD (TODO) |
| Top pod (electronics) | 150 × 55 mm footprint, lid 34 mm above the shell crown | full internal layout + wiring plan in §6.6; the lid over the PN532 antenna must be plastic even on the steel version (13.56 MHz passes through plastic, not steel) |
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
2. **Closure adjustment** (±2.5 mm effective diameter via three tongue-detent depths on
   the hook joint, §6.4 — the v0.6 hinge is a single fixed-diameter rod with no slotted
   position, so the detents are the only preload knob that exists) tunes preload at
   install time and re-tightens years later if the fins relax.
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
              ══►  ╰──╯      │       │       │
                             │  [screw head] │  ← closure screw at the bore bottom:
                             └───────┼───────┘    covered by the cable head when locked
                                     │ Ø4 mm hardened pin, 3 mm engagement
                              ┌──────┴────┐
                              │ pin spring│  (locks: spring pushes pin into groove)
                              ├───────────┤
                              │ solenoid  │  (unlocks: pulls pin against spring)
                              └───────────┘
```

- **Insert (lock):** the 45° ramp on the head cams the pin back; pin snaps into the groove.
  Zero power. A weak ejector spring behind the head is compressed as it seats.
- **Remove (unlock):** solenoid pulls the pin 4 mm; ejector spring pops the head ~5 mm out
  so it can't instantly re-latch; spool retracts the cable.
- Pin = **the solenoid's own Ø6 plunger** (v0.3 change, see ASSEMBLY.md §3.1): a 45°
  ramp is filed on its nose, it runs in a Ø6.6 channel through the boss, and the
  solenoid's included return spring provides the locking preload. No separate pin,
  coupling, or spring seat. Cable-head groove widens to ≥6.5 mm to accept the Ø6 nose.
  Shear area is ample — the attack that matters is cutting the cable, not the pin.
- Fallback if the measured plunger force/geometry disappoints: the old separate Ø4
  hardened-pin design, which then needs its coupling fully drawn before printing.
- Receiver bushing: hardened steel insert so a screwdriver can't gouge the latch open.

**Male fitting trade study — square tang vs round head (resolved).** The original
concept was a square/rectangular male tang with an angled tip and a cross-hole: push it
in, the tip cams the pin back, the pin springs into the hole — the razor-scooter folding
latch. The alternative is the round mushroom head with a ring groove. Both use the exact
same cam-tip insert / spring-pin / solenoid-pull action; the shape is the only question.

| Criterion | Square tang + cross-hole | Round head + ring groove |
|---|---|---|
| Insertion | must be rotationally aligned — fiddly with a twisting retractable cable | works at any rotation, no aiming |
| Cable twist while locked | locked-in; attacker can use the cable as a torque lever on pin & socket, and normal use winds twist into the cable | head spins freely — twist self-relieves, torque never reaches the pin |
| Pin engagement | through-hole = double shear (stronger) | groove = single shear — but a Ø4 hardened pin in single shear (~11 kN) already exceeds the 4 mm cable's ~8–10 kN break strength, so the extra strength buys nothing; the cable is the fuse either way |
| Making the female side tight | square socket corners are hard to make crisp (printed or filed) → shim clearance | round bore is drilled/reamed in a hardened bushing → tight, round, shim-hostile |
| Sourcing the male part | easy DIY: flat bar + hacksaw + drill press | one lathe operation, or adapt an off-the-shelf hardened grooved pin |
| Commercial precedent | scooter folding latches (rigid hinge, orientation fixed by the frame — the one case where alignment is free) | AXA/ABUS plug-in chains (Ø10 hardened round pin into a frame lock), retractable cable-lock heads |

**Decision: round head with a square-flanked ring groove.** Cutting the groove with
square flanks (not a V) makes the pin seat against a flat wall exactly like the
cross-hole would — the groove is effectively the square design's hole, revolved 360° so
it's always aligned. The angled insertion tip from the original concept is retained
verbatim (that cam action is what makes no-power locking work). The square tang isn't
wasted: it's the recommended **bench mule** for Phase 0 — a hand-tools version to measure
real solenoid pull vs pin-spring force before any lathe work.

**Self-guarding closure screw.** The one fastener a consumer ever drives sits recessed at
the **bottom of the latch receiver bore** — the same hole the cable head locks into.
Consequences:

- **Cable locked → screw physically unreachable** (the hardened head fills the bore).
  The tongue-and-groove seam cannot be slid apart while the bike is locked, and unlocking
  requires an authorized tag. The housing's security is chained to the RFID auth — for
  *that one seam*.
- **Cable unlocked → screw exposed**, but then the bike wasn't locked anyway; the worst
  an attacker gets is the lock itself. Acceptable.
- The two flanges interlock with a **hooked tongue-and-groove joint** along the full
  110 mm seam (resists radial opening; can only disengage by sliding axially), and the
  bore screw is what blocks that axial slide. That's scoped to this one seam only: the
  hinge side is captive via the rod + screwed cap (no glue, no rivets in the v1 printed
  housing), and several *other* assembly seams — lid, hatch, spine cover, hinge cap — do
  carry ordinary external screws as of v0.6. §7 documents that exposure and its
  mitigations in full; "no screw heads anywhere on the outside except at the bore bottom"
  was true through v0.5 and is **not** true now.
- Geometry: receiver bore Ø11 mm × ~26 mm deep — cable head seats in the top ~12 mm,
  the closure screw drives down through it into the boss/flange stack below.
- **v0.6 closure stack** (corrects two defects that made the v0.5 screw non-functional).
  The hook flange stays at z25.2–28.2 but is capped at **y ≤ 6.5 mm** — a flange top that
  reaches further under the bore rises to z29.8+ and eats the bore floor the screw head
  needs to clamp against. A separate low insert **pad** at y6.5–13.0, z21.8–25.2 carries
  the fastener instead: a **short M4 brass heat-set (Ø5.6 × L3, VERIFY sourcing)** sits in
  a through-pocket installed from the pad's **top** face with the door open, flange-up, on
  the bench — insert mouth toward the screw, which is then driven from above, down the
  latch bore. The swept pockets that admit the flange and pad through the door's closing
  arc (flange prism + pad prism) peak at z26.27 in the bore column, leaving a **3.7 mm
  solid floor** under the z30 bore bottom — enough to actually clamp against. (D1: the
  v0.5 clearance hole ran through the wrong z-segment, pierced the bottom shell into the
  tube cavity, and never reached the door insert — the one consumer screw could not work
  at all, and a probe found only 2.48 of 142 mm³ left in that floor regardless. D2: the
  v0.5 insert pocket punched clean through the 3 mm flange (Ø5.6×6 cut into a 3 mm wall),
  so no insert could seat.) A 2.4×45° chamfer on the pad's lower −Y edge keeps material at
  r ≥ 23.4 mm against the Ø46 mm max-tube envelope. Screw: **M4×8 low-profile socket +
  washer**, reached with a long 2.5 mm hex key through the empty bore (deep + narrow also
  means common drivers can't get purchase if someone tries to gouge past a locked head).
  An M4×14 was sized on paper and rejected — it would hit tubes ≥Ø38 mm. The M4×8's tip
  reaches z22, clearing the Ø46 tube envelope by 1.2 mm and passing through the liner's
  swept transit window (§6.6 delta, `liner_right`) instead of gouging it. Clearance drill
  `closure_screw_d` 4.4→4.5 (standard M4 clearance).
- Fit-adjustment consequence: the ±preload adjustment for the one-size-fits-all clamp
  (§6.2) lives on the hook joint only — the tongue has **3 detent depths**, selected at
  install. (Through v0.5 this bullet also credited a slotted hinge-pin position for fine
  preload; the v0.6 hinge is a single fixed-diameter rod running in a finished bore with
  no axial or radial slack to tune, so that DOF is gone. The 3 tongue detents are the only
  preload adjustment that exists and remain unmodeled in CAD — TODO, same honest gap as
  before.)

### 6.5 Top pod internal layout & wiring plan — SUPERSEDED by the v0.4 split (§6.7)

*Kept for reference: this section describes the v0.3 layout with all electronics in the
top pod. v0.4 moves everything except the latch and reader to the bottom bay.*

Packing study with **verified part dimensions** (sources in BOM): PN532 42.7 × 40.4 × 4,
18650 holder 76 × 21 × 21, Nano 45 × 18, JF-0530B body 30 × 13 × 15 **plus its Ø6 × 58 mm
plunger** — the working solenoid train (body + plunger + pin coupling) is **~65 mm long**,
far too long to lie across a 55 mm pod, so it runs along the pod axis. Three zones that
must not overlap set the pod length — the PN532 needs a metal-free column above and below
it, the latch bore needs clear vertical depth, and the battery is a 76 mm brick →
**pod interior 150 × 55 mm, lid 34 mm above the shell crown.**

Because the pod floor is the curved shell (Ø62), depth grows from 34 mm at the centerline
to ~48 mm at the side walls — tall parts sit at the edges, and a printed half-width shelf
adds a second level over the solenoid strip.

```
 TOP VIEW, floor level (lid + shelf removed), X in mm along the frame axis
 X=0 (front / scan end)                                        X=150 (rear)
 ┌──────────────┬──────────────────────────────────────────────────┐
 │              │   18650 + holder (76×21×21)          [MT3608]    │ Y=32..53
 │   RF ZONE    │   X 55..131, along the side wall     [TP4056]▓───┼── USB-C port
 │  keep empty  ├○─────────────────────────────────────────────────┤ through rear wall
 │ (PN532 is on │bore  plunger→[solenoid body]  [ Arduino Nano ]   │ Y=4..22
 │ the lid above│Ø11   X 64..94 (tail trimmed)   X 100..145        │
 │  this void)  │X≈58                            (USB faces rear)  │
 └──────────────┴──────────────────────────────────────────────────┘
    X 0..48        "latch + drive strip" along Y≈14

 SHELF LEVEL (printed shelf at Z≈18, over the drive strip only, Y 0..26):
   perfboard X 60..100 — IRLZ44N, AO3401, flyback diode, 1000 µF cap, divider
 LID: PN532 under the plastic window (X 0..45), wake button + LEDs at X≈50
```

**Zone by zone:**

| Zone | Where | Contents & orientation |
|---|---|---|
| RF | X 0–48, full width | PN532 mounted to the **underside of the lid** (bosses), antenna up under the 2 mm plastic window. Nothing metal above or below — the void beneath stays empty except two signal runs hugging the floor edge. Battery steel can is 55+ mm away (the #1 read-range killer). Wake button + LEDs on the lid at X≈50 |
| Latch + drive strip | Y 4–22, X 48–145 | Receiver bore (Ø11 × 26 deep, vertical) at X≈58 Y≈14, over the closure flange so the bore-bottom screw clamps the halves (§6.4). Solenoid body at X 64–94 lying on the floor, plunger toward the bore (−X); pull-type: energize → plunger retracts +X, dragging the locking pin out of the bore wall. Plunger tail trimmed so the train ends ≈X 98. Nano at X 100–145, USB toward the rear wall for lid-off reflashing. Pin spring coaxial with the plunger; ejector spring under the bore floor |
| Battery side | Y 32–53, X 55–131 | 18650 holder along the side wall — the deep edge absorbs its 21 mm height. TP4056 stands vertically at the rear wall (X 140–150), **USB-C port through the rear end wall** under a rubber dust flap, 5 cm leads to the cell it charges. MT3608 beside it |
| Shelf | Z 18–30, Y 0–26, X 60–100 | Perfboard with both MOSFETs, flyback diode, 1000 µF reservoir cap, divider resistors — directly above the solenoid it drives (wire drop <30 mm through a shelf slot) |

**Why this orientation works:**

- Scan face at the front end = natural "tap here" target, maximally far from the battery.
- The solenoid train and the bore share one axis line (Y≈14) that sits directly over the
  closure flange — required by the self-guarding screw (§6.4).
- Every high-current run (battery → TP4056 → MT3608 → perfboard → solenoid) lives in the
  rear half; the RF end carries only 3 thin signal wires.
- No wiring leaves the top pod at all: the bottom spool pod is purely mechanical.

**Wiring plan (~15 conductors total):**

| Run | Wire | Route |
|---|---|---|
| Battery → TP4056 → MT3608 → perfboard 5 V bus | 22 AWG | rear corner cluster, 5–8 cm runs |
| Perfboard → solenoid | 22 AWG | straight drop through the shelf slot, <3 cm |
| Perfboard 5 V/GND → Nano | 26 AWG | 4 cm along the strip |
| Nano A4/A5 + D7 → PN532/P-FET | 28 AWG | 3-wire ribbon along the Y=0 floor channel |
| Lid parts (PN532, button, LEDs) → body | 28 AWG | one 15 cm service loop at the X≈50 hinge-side corner so the lid opens fully; JST-XH connector so it CAN unplug |

All of this is modeled in the CAD (`cad/bike_lock.scad`, v0.2), not just described:
clip-lip raceways on the floor (RF ribbon x4–54, power/solenoid run x60–100), a driver
tray bridging the Nano bay with wire notches and zip-tie holes, two battery saddles that
give the holder a level bed over the curved floor (zip-tie pass-unders included), and
mushroom-head strain-relief posts anchoring the lid's 15 cm service loop. Every off-board
connection gets a JST-XH plug so any module can be swapped without soldering.

**Fill check:** component volume ≈ 92 cm³ (battery+holder 34, latch block + solenoid train
20, PN532 + keep-out 15, Nano 10, boards 8, misc 5). Usable pod volume ≈ 195 cm³ after
subtracting the curved shell intrusion → **~47% fill, >30% reserved for wiring and
fingers** — comfortably inside the 70–75% max-fill rule of thumb for hand-assembled
enclosures.

### 6.6 v0.5 "spine + door" architecture (current) — the consumer-install redesign

**v0.4 had a fatal flaw found in assembly review: it could not be installed.** The pod
overhung the seam and the full-width bay blocked both the door's swing and the tube's
entry path. v0.5 is governed by three kinematic rules, now **machine-verified on every
CAD build** (`python bike_lock_cq.py --sweep`):

1. **Entry corridor** — the tube slides in from the left at axis height; no fixed
   material may exist in that swept slab (±23.5 mm). The pod becomes asymmetric (left
   wall at y −17, its fringe floating 0.6 mm above the closed door); the belt band and
   left fairing are gone.
2. **Door swing** — the door is a light arc panel carrying only its TPU liner half and
   the closure flange+lip; pod, bay, and drum all live right of y +7, outside the door's
   swept annulus. Verified: zero interference through 0–110° of opening.
3. **Slim drum** — spool axis turned 90° (along Y): a Ø68 × 32 wheel tucked low-right,
   cable 1.2 m × Ø4 (was 1.5 m — still loops a wheel + rack). The lock's lowest point
   rises from −121 to −94 mm; the spool cover faces outboard and is serviceable in place.

Consumer install: swing the door open, press onto the down tube, swing shut, drive ONE
hidden M4 down the latch bore. The latch line (bore, boss, solenoid, pedestal) sits at
y +10 — on the body's side of the seam, since the pod's left floor IS the closed door.
The door's flange reaches under the bore through a swept pocket (the pocket is the
union of the flange's positions through the closing arc, so engagement is rotational
and snag-free by construction).

**v0.6 delta (current):** layers onto the three kinematic rules above without changing
them. Hinge collapses to a **single Ø4.0 mm continuous rod** through both shell halves
(was two Ø3 mm pins + glued end plugs) — retention and thermal detail in §6.1/§6.8/§6.9.
The wire spine, sealed in v0.5, is now an **open lay-in raceway with a screwed cover**:
the roof over x23.5–32.5 is deleted, wires drop in instead of being fished blind, and a
curved cover plate seats on a rabbet ledge with a 0.5 mm shadow-gap reveal and 2× M3
self-tap screws (§6.8). The bay module is repacked: the LiPo now stands **on edge** along
the +Y wall instead of lying flat, because the flat-frame pocket and the TP4056 block
occupied the same floor footprint and the battery physically could not fit (D11); the
service hatch becomes a **component tray** (nesting pad, zip-anchor grid, diagonal Nano
mount) rather than a blank cover, since the floor beneath it is now a real service window
instead of the sealed floor the v0.5 hatch never actually served (D6). The liner keys onto
full-length **dovetail grooves** instead of friction+adhesive — no glue anywhere in the
assembly — and `liner_right` gains a swept **transit window** where the closure flange's
arc dips through its base ring (D10, found by the extended `--sweep` check). Two
verification parameters widened after that same extended sweep (moving set = door +
liner_left vs. every other part, not just body+bay+lid, which is what hid D10 in the first
place): entry-corridor margin `COR_Z` 23.5→**24.0 mm**, and the door-edge fringe float
0.6→**1.0 mm** (relief plane at z=32.0).

*(v0.4 "slim top" notes preserved below for reference — its layout concepts carried
into v0.5's bay brick.)*

### 6.6b v0.4 "slim top" architecture (superseded)

Owner direction: the top must be sleek; the bottom carries the mass and draws no
attention. Implemented in CAD v0.4 (`cad/bike_lock_cq.py`):

- **Top pod (126 × 56 × 25 mm outer — half the old height):** latch bore + solenoid
  (plunger-as-pin), PN532 under the lid window, wake button + LEDs. Nothing else.
- **Bottom bay** (one printed module around the spool drum, bolted by 4× M4 from inside
  the clamp bore): **front tunnel** = TP4056 + USB-C port (through the front wall, under
  a dust flap) + Nano + perfboard on a zip-anchor grid; **rear tunnel** = battery +
  MT3608. Both tunnels close with a shared bottom hatch part (printed twice).
- **Battery change: 103450 LiPo pouch (~2000 mAh, 34 × 50 × 10 mm, ~$6)** — a rigid
  76 mm 18650+holder cannot package beside the drum; anything crossing the drum's
  midsection hits the spool. Battery life drops from ~4–5 weeks to **~3.5–4 weeks**
  (§4.4 math scales linearly). Must be a cell **with protection PCB**, charged by the
  same protected TP4056.
- **Wiring paths (all printed in):** a hollow **wire spine** rib on the right shell side
  (x 96–112, void ~3.5 × 12 mm arc) carries ~11 conductors from the rear tunnel up
  through a slanted feed hole into the pod, under the belt line; a **corner duct**
  inside the bay (outside the drum ring, +Y top corner) links front↔rear tunnels for
  the 4 power wires; a short raceway inside the pod serves the PN532 ribbon.
- **Deleted in v0.4:** the cam-lock backstop (no wall tall enough in the slim pod — the
  USB power-bank unlock in §8 is the dead-battery path, as decided) and the separate
  battery saddles / driver tray / board pocket cartridges (their jobs moved into the bay).
- **Service note:** spool access now requires unbolting the bay (4 screws from the open
  clamp) — the cover can't slide out past the rear tunnel in place. Rare operation,
  accepted.


### 6.6c v0.7 delta — electronics as first-class placed bodies

Every BOM electronic now exists in the CAD as a dimensioned reference body (nominal
dims, VERIFY on arrival), placed in the assembly and covered by `--matrix`/`--gaps`:
packaging claims (solenoid body vs lid: >=1.0 mm; plunger tail TRIMMED to x98 vs the
wake button: >=1.0 mm; PN532 vs solenoid) are now machine-checked assertions, not
prose. Modeling them exposed two more v0.5 impossibilities, both fixed: (D13) the
TP4056 card slot pointed the USB-C at the floor - the board now lies FLAT in a rail
cradle at lane y=22 with the port through the wall (`usb_z` -46 -> -51.8); (D14) Nano
+ MT3608 + perfboard cannot fit the tray window co-planar (~2600 mm2 of boards vs
1195 mm2) - the tray is now a TWO-LEVEL cartridge: `nano_clamp (pod wall recess - superseded sled concept)` carries the Nano
diagonally (pins trimmed flush - the only way the stack fits), and a driver card held
a 40x29 perfboard on L-walls above it. **v0.7 final superseded all of this**: the Nano
edge-stands in the pod wall recess under `nano_clamp`, and ALL driver electronics sit
on a 42×10.7 card on two Ø7 crown bosses (x66/x96, −y strip of the pod, 2× M3 ST),
<30 mm from the solenoid. The bay holds only the cell + TP4056; the spine carries
exactly 2 conductors. See BUILD.md §2.

### 6.7 RFID face

The PN532 antenna sits directly under a **plastic** window on the top face (13.56 MHz does
not pass through stainless). Keep all steel ≥10 mm clear of the antenna loop or read range
collapses; expect 1–3 cm range through 2 mm ABS. The wake button and LED sit beside the
window.

### 6.8 Tolerances & fastening plan (v0.6)

All numbers below are parameters in `cad/bike_lock_cq.py` (single source — read the
parameter block, not this table, when the two disagree). This section replaces the
per-joint tolerance guessing that shipped through v0.5: every screw in the assembly now
has a named pilot, clearance, and countersink pulled from one shared spec.

**Clearance & fit classes.** `--gaps` checks every placed pair against these bands with
`BRepExtrema` exact min-distance; `CONTACT_OK` is a whitelisted sentinel for faces meant
to touch (only true overlap fails the check, not zero gap).

| Class | Nominal gap | Where used | Notes |
|---|---|---|---|
| Clamped faying face | 0.00 mm (`CONTACT_OK`) | shell parting line, hatch-to-bay, spool cover-to-rabbet | modeled as touching by design; whitelisted so `--gaps` doesn't flag it |
| Static insert fit | 0.10–0.30 mm | heat-set pockets (M3/M2.5/M4-short), dovetail keys | press/friction fit, no relative motion once assembled |
| Hinge rod running fit | +0.2 mm diametral (finished) | Ø4.0 rod in the Ø4.2 `HINGE_BORE` | bore is drilled to finish size through the closed, clamped halves — FDM prints it undersized/drooped, so "finished" here means post-drill, not as-printed |
| Kinematic clearance | ≥0.4 mm | door-swing sweep, knuckle-to-knuckle gaps | closure engagement clearance `clr` kept at 0.5 (unchanged from v0.5) |
| Entry corridor margin (`COR_Z`) | 24.0 mm half-height (was 23.5) | tube entry slab | max tube Ø46 → ±23 mm, +1.0 mm margin |
| Door-edge fringe float | 1.0 mm (was 0.6) | pod left-fringe relief vs. the closed door's top edge | relief plane at z=32.0 |

**Pilot / clearance / countersink numbers, by thread:**

| Thread | Self-tap pilot | Through clearance | Countersink / counterbore | Insert pocket |
|---|---|---|---|---|
| M3 machine (into heat-set) | — | 3.4 mm | 90° CS, Ø6.4×1.8 (ISO 10642 flat head) | Ø4.1×6.5 brass heat-set (VERIFY insert brand dims) |
| M3 self-tap | 2.5 mm | 3.4 mm | CS Ø7.2×2.4 (ISO 7050 flat head — VERIFY 80°/90° head angle) | — |
| M4 machine/self-tap | 3.3 mm | 4.5 mm | pan-head counterbore Ø8.6×4.35 (head fully sub-flush of the bore) | — |
| M4-short (closure) | — | 4.5 mm | none — low-profile socket head | Ø5.7 through-pocket, L3 heat-set (VERIFY sourcing) |
| M2.5 machine (into heat-set) | — | 2.7 mm | none | Ø3.6×4.5 brass heat-set |
| Generic pad-boss pilot | 2.5 mm (was 2.6) | — | — | — |

**Fastening plan — every joint in the assembly:**

| Joint | Fastener | Pilot / clearance / CS | Driver access | Visible / hidden | Flush treatment |
|---|---|---|---|---|---|
| Closure (consumer screw) | M4×8 low-profile socket + washer ×1, into short M4 heat-set | clr 4.5 through boss; insert Ø5.7 through-pocket | long 2.5 mm hex key, down the open latch bore | hidden — cable head covers it when locked | recessed at bore bottom |
| Bay module ×4 | M4×12 pan self-tap | pilot 3.3; clr 4.5; counterbore Ø8.6×4.35 | from inside the open clamp bore | hidden — clamp must be open | pan head fully sub-flush of the bore (fixes D5 — heads used to stand 1–2.5 mm proud into the liner zone) |
| Lid ×4 | M3×10 CS machine (ISO 10642), into M3 heat-set in body rim bosses | clr 3.4; CS Ø6.4×1.8 | external, straight down from the lid's top face | **visible — externally removable on the locked bike** | countersunk flush with the lid's crowned top face |
| Hatch ×2 | M3×10 CS machine (ISO 10642), into M3 heat-set in the TP4056 block + drum web | clr 3.4; CS Ø6.4×1.8 on the **external** face | external, from the bay module's underside | **visible — externally removable on the locked bike** | countersunk flush; fixes D6 (v0.5's counterbore was on the internal face, so heads stood proud outside) |
| Spool cover ×3 (90/210/330) | M3×10 CS self-tap | pilot 2.5 into the ring-wall annulus boss at r31.25 (~5.5 mm engagement, fixes D4); clr 3.4; CS Ø7.2×2.4 | external, from the +Y outboard face | visible | outer face reads flat — CS depth absorbed by an underside pad nesting in a rabbet-floor relief pocket, not a dish in the visible face |
| Spine cover ×2 | M3×10 CS self-tap | pilot 2.5 into raceway end walls; clr 3.4; CS Ø7.2×2.4 | external, from the outer skin | **visible — externally removable on the locked bike** | countersunk flush |
| Hinge cap ×1 | M3×10 CS self-tap | pilot 2.5 into the shell end face; clr 3.4; CS Ø7.2×2.4 | external, rear end face | **visible — externally removable on the locked bike; removing it frees the hinge rod (§7)** | countersunk flush |
| Pedestal pads ×2 | M3×10 pan self-tap | clr ~3.4 through the base pads; driver access bored Ø6.5 through the tower | through the tower access holes, before the solenoid is mounted | hidden — heads covered once the solenoid body seats | none (pan head, buried) |
| Solenoid mount ×2 | M2.5×8 machine, into M2.5 heat-set in the tower top | clr 2.7; insert Ø3.6×4.5 | top-down into the tower, before the solenoid covers its own screws | hidden once seated | none — cyclic load joint, no CS; a captured-nut scheme was tried and rejected (no nut-insertion path once pads moved to 76/86) |
| PN532 mount ×4 | M2.5×8 **nylon** machine, self-tapping into printed drop-bosses (no insert — antenna wraps the board perimeter, no metal at the edge) | pilot 1.05, blind 2.6 mm deep, boss dropped 1.5 mm from the pocket ceiling | from inside the lid, before the lid seats on the body | hidden once assembled | none |

Deleted from the BOM: the Ø3 mm hinge pins, the glued end plugs, and an M4×14 closure
screw that was sized and rejected on paper (hits tubes ≥Ø38 mm — never buy it). Hinge rod
stock is Ø6 mm 303 stainless bar × 165 mm — not a fastener, listed here for BOM
completeness; the turning operation is in §6.9.

### 6.9 DFM & CNC path

Per-part machinability for the steel-shell / production phase (§6.2, §10 Phase 2). None
of this blocks the v1 printed build — it's forward-looking so the CAD doesn't need a
second redesign when the shell moves to metal.

| Part | Verdict | Setups | Notes |
|---|---|---|---|
| body | 3-axis, plus a 4th-axis feature | 4 (+ rotary) | see below |
| door | 3-axis, plus a 4th-axis feature | 3 (+ rotary) | see below |
| bay_module | 3-axis | 4 | top, bottom, +Y outboard face, and the front (−X) wall each carry features that can't share one fixture orientation |
| bay_hatch | 3-axis | 1 | flat plate — tray pad, 2× CS, zip-anchor grid all reachable from one face; through-holes carry the far-side features |
| pedestal_cart | 3-axis | 1 | every hole (pad clearances, insert pockets, driver-access bores, boss scallop) runs along Z — one top-down setup |
| lid | 3-axis | 1 | window pocket, PN532 bosses, button/LED holes, and the 4× CS all sit within reach of a single blank held once |
| spool_cover | lathe + secondary drill | turn, then drill/mill | disc + hub + hubcap dish are rotationally symmetric — turn those; the 3× M3 holes at 90/210/330 break symmetry and need a secondary drilling op (live-tooling lathe or a simple jig) |
| hinge_rod | lathe, one op | 1 | Ø6 303 stainless bar → integral Ø6×1.6 head, R0.5 head fillet, 0.4×45° head chamfer, R2.2 domed tail, trimmed at dry-fit. Center-drill the tail and support it on a tailstock live center — this is a 35:1 slender turn and **will chatter unsupported** |
| hinge_cap | 3-axis | 1 | disc + ear + bridge, one blind pocket, one through-hole, one CS — all from the same face |
| spine_cover | 3-axis | 1 | curved plate cut from the outside face; 2× through-hole + CS on the arc midline |
| liner_right / liner_left / shim | stays printed or molded | — | TPU 95A — not a metal-era part; injection/compression molding is the production path if volume ever justifies a tool, CNC doesn't apply to a flexible finned part |

**Body/door — the 3 changes that get them (mostly) to 3-axis, and the one feature that
doesn't:**

1. **Hinge bore** is now one straight Ø4.2 finished bore through every knuckle and
   standoff (was two blind Ø3.2 channels + stepped pockets for the glued end plugs) — a
   single axial drill pass replaces stepped/blind tooling.
2. **Dovetail liner groove**: one straight full-length axial pass per shell half, cut
   with a form tool from the end face — no plunge, no pocket-clearing.
3. **Bay-mount and spine-cover holes** sit on constant radial lines (`bay_screw_y`, the
   raceway end-wall plane) rather than scattered depths, so the through-holes and
   counterbores on each line come off one fixture angle instead of several.

The exception: the **closure sweep pockets** (flange prism + pad prism — the volume the
door's flange and pad sweep through as it swings shut, §6.4) are literal swept forms about
the hinge axis, cut into both `body` and `door`/`liner_right`. A rigid 3-axis mill can't
cut a true swept pocket in one pass; it needs a **4th axis** (rotary about the hinge axis)
to index the cut through the arc — for the steel version that rotary axis is physically
the **piano-hinge direction**, so it's a natural addition rather than a special fixture.
FDM sidesteps this entirely (the sweep is baked into the printed geometry).

**Tube-stock strategy (body/door):** both parts are fundamentally a cylindrical shell
(`outer_cyl()` cut by `tube_bore()`, then split at the parting plane), so the steel
version should start from **tube stock** close to the finished OD (Ø57 mm steel target,
§6.1) and wall (1.5 mm), not a solid round bar turned down. Roughing a solid bar to a
1.5 mm wall removes the overwhelming majority of the stock as chips; starting from tube
removes most of that roughing volume before the half-shell split, pod, and boss features
are even touched.

**Taps replace self-taps once the shell is metal.** The pilot-hole parameter set (§6.8)
was sized for FDM self-tapping in plastic, but two of the three thread sizes already carry
over as standard tap-drill sizes — no redesign needed, just add a tapping pass instead of
relying on the screw to cut its own thread:

| Thread | Tap drill (metal) | Matches the existing plastic self-tap pilot? |
|---|---|---|
| M2.5 × 0.45 | 2.05 mm | No — the two M2.5 joints (solenoid, PN532) use heat-sets or a nylon self-tap in the printed version, not a bare pilot; size the metal tap drill fresh |
| M3 × 0.5 | 2.5 mm | Yes — `M3_PILOT = 2.5` already matches the standard M3 tap drill |
| M4 × 0.7 | 3.3 mm | Yes — `M4_PILOT = 3.3` already matches the standard M4 tap drill |

**Dovetail groove:** slide-in from the end face. `dovetail_groove()` is a constant
cross-section extrusion the full 146 mm length, so it's cut with a single straight pass of
a dovetail form tool started at the front face — same operation on a manual or CNC mill,
no plunge-milling, no multi-axis motion.

---

## 7. Security analysis — honest version

| Attack | Resistance | Mitigation / status |
|---|---|---|
| Bolt-cut the 4 mm cable | ❌ seconds | **This is the real limit of any cable lock.** 4 mm is a deterrent (opportunists, café stops), not U-lock security. Going to 6 mm cable roughly doubles cut resistance but grows the spool pod to ~Ø120 mm. ⚠️ Decide after seeing the v1 size on a real bike. |
| Unscrew the housing from the frame | ⚠️ partially, while locked | **The self-guarding closure screw (§6.4) still holds — but "every other seam is captive" is no longer true, and this row is rewritten for v0.6 honesty.** The tongue-and-groove seam itself can't be slid apart while the cable head covers its screw. Four *other* joints, though, are ordinary external screws reachable on the locked bike without unlocking anything: the **hatch** (2× M3, bay underside), the **spine cover** (2× M3, over the wire raceway), the **hinge cap** (1× M3, rear end face), and the **lid** (4× M3, top face) — full spec in §6.8. Consequences: removing the hatch or spine cover exposes the solenoid's bare drive leads, which run off the regulated 5 V rail — with those two leads and any 5 V source an attacker can fire the solenoid directly, a non-destructive unlock that never touches the RFID. Removing the hinge cap frees the rod's axial float and lets the single hinge rod slide out the front; the two shell halves then come apart, but the **bike stays cable-tethered** — the cable head is still latched in the boss/receiver, so the housing detaches while the lock itself doesn't release. The lid is the fourth instance of the same class: v0.5's lid screws had no working pilots (D3), so the lid was never really a fastened joint; v0.6 gives it real M3 pilots in the body rim (§6.8), which means removing it now gives direct mechanical access to the top of the latch boss and the solenoid's own plunger — the same "external screw → internal mechanism access" trade-off as the hatch/spine-cover lead exposure, just reaching the pin instead of the leads. **Owner-accepted for the prototype phase** ("reasonable outward screws OK for now" — a schedule trade-off being logged, not a security requirement being waived). Production mitigation list, not yet built: one-way/security screw heads or staking on lid, hatch, spine cover, and hinge cap; potted or sleeved solenoid drive leads so they can't be tapped from outside; hidden lid fastening (already roadmapped independently of this finding). |
| Cut the printed (plastic) housing | ❌ v1 only | Inherent to the printed model — it's a functional prototype, not a security device (§6.2). The steel shell closes this. |
| Clone a fob UID | ⚠️ | Real but low-likelihood for a bike; fixed by v2 challenge–response (§5). |
| Drain/wait out the battery | depends | See §8 — this is why fail-open is dangerous. |
| Smash the electronics pod | ⚠️ | Breaking the solenoid/pin area could jam it *locked*, not open it (pin is spring-into-lock). Acceptable failure direction. |

Positioning: this is a **convenience lock** — always on the bike, zero-effort, good enough
for short stops and low-theft areas, and a great engineering project. It should be honest
about not replacing a U-lock for overnight street parking.

---

## 8. Dead-battery behavior (RESOLVED: fail-secure + USB-C escape hatch)

**Decision: the lock stays locked when the battery dies (fail-secure), and the USB-C
charge port doubles as an emergency power input** — plug any phone power bank into the
port and the whole system runs immediately, even with a stone-dead cell: wake, tap,
unlock. No waiting for the battery to take charge.

Implementation note for the electronics build: the TP4056 module's OUT+/OUT− terminals
(not the battery terminals) must feed the MT3608, so the load is powered from USB
whenever USB is present. That's the standard wiring for the protected TP4056 board
anyway — just don't tap the system rail directly off the cell.

*(v0.4 update: the cam-lock backstop was deleted — the slim top has no wall tall enough
for its barrel. Bench-test the electronics thoroughly before first on-bike use; the USB
power-bank unlock is the sole dead-battery path, which is the accepted design.)*

The earlier idea (unlock on battery death) was rejected for the record — one problem of
security and one of physics:

1. **Security:** if a dead battery unlocks the cable, a thief doesn't need bolt cutters —
   they wait, or chill the pack, or just come back in a month. The lock's security would
   equal its battery life.
2. **Physics:** the natural solenoid arrangement (energize-to-unlock, spring-to-lock) is
   inherently **fail-secure** — no power means the pin stays in. Making it fail-open
   requires either holding the solenoid energized the whole time the bike is locked
   (battery dies in hours, not weeks) or a bistable/motorized latch plus supervisory
   circuitry that fires a "last gasp" unlock as voltage collapses — more parts, more cost,
   and it *still* unlocks your bike in public when it triggers.

(The cam-lock backstop adds a keyway, which is itself a pickable attack surface — an
accepted v1 trade-off while the electronics prove themselves, and the reason it's slated
for deletion rather than kept forever.)

---

## 9. Open questions

None — every design decision to date is resolved. New questions get added here as
prototyping surfaces them.

*Resolved:* one-size-fits-all fit strategy → finned TPU liner + closure detents + shim
sleeve (§6.2). First housing is 3D printed → print spec in §6.2. Housing tamper
resistance → self-guarding closure screw at the bottom of the latch bore (§6.4). Male
fitting shape → round head with square-flanked ring groove; square tang kept as the
Phase-0 bench mule (§6.4 trade study). Dead-battery
behavior → fail-secure + USB-C power-bank escape hatch + v1 hidden cam-lock backstop (§8).
Cable gauge → 4 mm (spool pod stays Ø95). Owner's down tube confirmed inside the
Ø32–46 mm core range. TPU printing available → finned liner as specced, no silicone
fallback needed. Aero/oval Ø50 mm+ tubes confirmed out of scope for v1. Phone plan →
owner has an iPhone: sticker + fobs permanent, Android HCE app dropped from the roadmap.

## 10. Build plan

| Phase | Goal | Cost |
|---|---|---|
| 0 — Breadboard | Nano + PN532 + MOSFET + solenoid on a bench PSU; firmware v1 working end-to-end | ~$25 electronics |
| 1 — **Printed v1** (the first real model) | ASA/PETG clamshell + TPU finned liner + donor-leash spool + latch; whole system living on the actual bike; measure solenoid force vs pin spring; fit-test the liner on every bike we can find (target: 5+ different tubes across Ø32–46 mm) | ~$15 filament + hardware |
| 2 — Steel housing | 304 shell (rolled sheet or machined), hardened bushing + pin, final cable; liner carries over unchanged | TBD, ~$40–80 depending on fabrication access (TAMU shop?) |
| 3 — v2 electronics | Pro Mini 3.3 V swap (months of battery) | ~$10 |
