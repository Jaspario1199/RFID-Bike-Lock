# BENCH_BUILD.md — building from the MT3608 forward, with the parts on hand

Everything downstream of the charger, using only what has been delivered. The TP4056 hasn't
arrived, so the cell can't be recharged yet — this guide works around that by running the bench
off the ELEGOO supply and the RoomCleaner 12 V rig, and saving the LiPo for the tests that
actually need it.

Wiring reference: [`WIRING.md`](WIRING.md) · diagram: `renders/electrical/wiring_diagram.png`
Firmware: `firmware/rfid_bike_lock_rc522/`

---

## 0. What you have, what's missing, and the workaround

| Needed | Status | Workaround until it arrives |
|---|---|---|
| MT3608 boost | ✅ delivered | — |
| HS-0730B solenoid, 6 V 1 A | ✅ delivered | — |
| IRLZ44N, 1N5819 | ✅ delivered | — |
| IRF4905 (P-FET reader gate) | ✅ delivered | use instead of the AO3401 — same circuit, TO-220 package |
| 103450 LiPo | ✅ delivered | ships part-charged (~3.7–3.8 V). **You cannot recharge it yet**, so use it only for stages 5–6 |
| Nano, RC522, buttons, LEDs, buzzer, resistors | ✅ owned | — |
| **TP4056** | ❌ not ordered | none — the cell simply can't be recharged. Don't run it below 3.0 V |
| **AMS1117-3.3** | ❌ not ordered | the ELEGOO supply module's **3.3 V rail** powers the RC522 on the bench |
| **1000 µF cap** | ❌ not ordered | drive the coil from a *separate* supply in stage 5 so rail dips can't reset the Nano |

**Two rules for the whole session.** Set the MT3608's output *before* connecting anything to
it — they ship at 20 V and will kill the Nano. And the 1N5819's painted band goes to the
**positive** rail; backwards it is a dead short.

---

## Stage 1 — set the MT3608 to 6.00 V (10 min)

Nothing else connected. Feed it 5 V from the ELEGOO module (or 12 V from the RoomCleaner PSU
through an MP1584 — the MT3608 takes 2–24 V in).

1. IN+ / IN− to the supply. Multimeter on OUT+ / OUT−.
2. Turn the trim pot. Many turns do nothing at first; keep going, then it climbs fast.
3. Land on **6.00 V ± 0.05**. Power down.

Mark the module with tape so you don't confuse it with the other four in the pack.

---

## Stage 2 — Nano on the 6 V rail (10 min)

| From | To |
|---|---|
| MT3608 OUT+ | Nano **VIN** |
| MT3608 OUT− | Nano **GND** |

| Measure | Expect |
|---|---|
| Nano 5V pin → GND | 4.9–5.1 V (its onboard regulator working) |
| VIN → GND | 6.0 V |

If the 5V pin reads 6 V, you're on the wrong pin — that would put 6 V into everything.

---

## Stage 3 — panel I/O, no reader yet (30 min)

This proves the sketch, the buttons, the LEDs and the buzzer before any reader complexity.

| Part | Nano pin | Wiring |
|---|---|---|
| GREEN button | D3 | one leg → D3, other leg → GND |
| RED button | D2 | same |
| Red LED | D8 | anode → 470 Ω → D8, cathode → GND |
| Green LED | D9 | same on D9 |
| Active buzzer | D6 | (+) → D6, (−) → GND |

Flash `firmware/rfid_bike_lock_rc522/`. Install the **MFRC522** library first (Library Manager,
by GithubCommunity). Serial monitor at 115200.

**Expect:** press green → short chirp, `[wake]` on serial, then a fast red ×5 and a long buzz
because no reader answers. That failure *is* the pass condition for this stage — it means
buttons, LEDs, buzzer and the state machine all work.

Tap red during the window → one red blink, a 150 ms beep, back to sleep.

---

## Stage 4 — RC522 (30 min)

**The RC522 is a 3.3 V part.** On the bench, power it from the **ELEGOO module's 3.3 V rail**,
not the Nano's 3V3 pin. Tie the ELEGOO ground to the Nano ground.

Level-shift the four Nano→reader signals. Eight resistors, all in your kit:

```
Nano pin ──[1 kΩ]──┬── RC522 pin
                   │
                 [2 kΩ]
                   │
                  GND
```

| Nano | through divider → | RC522 |
|---|---|---|
| D10 | ✔ | SDA (SS) |
| D13 | ✔ | SCK |
| D11 | ✔ | MOSI |
| D4 | ✔ | RST |
| D12 | **direct, no divider** | MISO |

**Expect:** green button → chirp → tap a fob → `[scan] uid=…`. The first fob ever tapped
becomes master and is written to EEPROM. A second fob gives two red blinks and a long buzz.
Hold red 5 s → three beeps → tap master → tap the second fob → it enrolls, green ×3.

If you get the fast red ×5: check SS and RST first, then that 3.3 V is actually present at the
module, then that the dividers aren't swapped.

---

## Stage 5 — solenoid driver (45 min)

Build the driver on a scrap of perfboard for now; cut the final 42 × 10.7 card later.

```
coil supply + ──┬──────────── solenoid ──── IRLZ44N drain
                │                 │
            (cap later)        1N5819   band toward +
                │                 │
coil supply − ──┴── IRLZ44N source ┴── GND, common with the Nano
Nano D5 ── 100 Ω ── IRLZ44N gate ── 100 kΩ ── GND
```

**Power the coil from a separate 6 V source for this first test** — the RoomCleaner 12 V PSU
through an MP1584 set to 6 V is ideal. Without the reservoir cap, a 1 A pulse on a shared rail
can dip it enough to reset the Nano, and you'd waste an hour chasing a fault that isn't there.
Grounds still tie together.

| Measure | Expect |
|---|---|
| Coil resistance before wiring | ~6 Ω (confirms the 6 V 1 A winding) |
| Across the coil, idle | 0 V |
| Across the coil during the 300 ms pulse | 5.5–6 V |
| Gate at D5 during the pulse | ~5 V |

**Expect:** an authorized fob → clunk. File the plunger's 45° nose before testing the latch
itself; for now you're only proving the electrical path.

If the pull feels weak, try `SOLENOID_PULSE_MS = 150` — shorter is fine, the plunger moves in
tens of milliseconds — and check you're at 6 V, not 5.

---

## Stage 6 — reader power gate with the IRF4905 (20 min)

The IRF4905 is a P-channel in TO-220. Facing the printed side with the legs down: **G – D – S**.
The metal tab is connected to the drain, so it sits at the load's voltage — keep it off
anything conductive.

| IRF4905 | To |
|---|---|
| **S** (source) | Nano 5V pin |
| **D** (drain) | reader supply (the AMS1117's input when it arrives; the RC522 directly for now, **only if you keep it on 3.3 V** — see note) |
| **G** (gate) | Nano D7, plus a 10 kΩ from gate to 5 V |

⚠️ **Do not feed the RC522 from the 5 V drain.** Until the AMS1117 arrives, leave the reader on
the ELEGOO 3.3 V rail and test the gate with an LED and resistor on the drain instead: D7 low →
LED on, D7 high → LED off. That proves the gate logic without risking the module.

| Measure | Expect |
|---|---|
| Drain to GND, D7 driven LOW | ≈ 5 V (FET on) |
| Drain to GND, D7 HIGH | ≈ 0 V (FET off) |

If it's backwards — on when it should be off — source and drain are swapped.

---

## Stage 7 — the sleep-current test (15 min, needs the LiPo)

This is the one that decides whether the lock lasts weeks or days. Now switch the MT3608's
input to the **LiPo**, since a bench supply's own draw would swamp the reading.

Meter in series with the cell's positive lead, sketch running, let the scan window expire.

| Reading | Meaning |
|---|---|
| **1.5–3 mA** | correct → 3–4 weeks per charge |
| 15–25 mA | the Nano never slept — a button holding D3 low, or `#define DEBUG` still on |
| 40 mA + | the reader is still powered — D7 logic or the FET orientation |

Comment out `#define DEBUG` for this test; serial keeps the USB chip awake.

**Watch the cell voltage.** You can't recharge until the TP4056 arrives, so stop at 3.4 V and
leave the rest for later.

---

## When the missing parts arrive

1. **TP4056** — cell to B+/B−, then OUT+/OUT− becomes the input to the MT3608. The cell is
   never tapped by anything else. Charge with the lock asleep; this board has no load sharing.
2. **AMS1117-3.3** — insert between the IRF4905's drain and the RC522, and drop the ELEGOO
   rail. Gating upstream of the regulator kills its idle draw too.
3. **1000 µF (Ø8 × 12.5, or Ø10 up to 20 mm — both fit the driver card)** — across the coil
   supply, right at the card. Then move the coil onto the shared 6 V rail and re-run stage 5.
