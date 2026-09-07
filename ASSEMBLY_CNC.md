# ASSEMBLY_CNC.md — building the rev 3c lock, step by step

The complete build order for the CNC-lineage casing (`cad/cnc_casing_cq.py`, rev 3c),
Stage 1: **everything printed in PETG + TPU**, aluminium later with no geometry change.

Read §0 once. After that the stages are meant to be followed in order — each one ends at a
test you can actually fail, so a mistake surfaces while it is still cheap to fix.

Coordinates match the CAD and the drawings: **x** runs along the tube 0→150, **y = 0** is the
seam plane (+y = C1, the half that carries the boxes), **z** is up, tube axis at z = 0.

---

## 0. Before you start

### 0.1 The parts you print

| Part | File | Print orientation | Material | Supports |
|---|---|---|---|---|
| C1 chassis half | `C1_chassis_half.step` | seam face **down** on the plate | PETG | none |
| C2 clamp half | `C2_clamp_half.step` | seam face **down** | PETG | none |
| A1 top box | `A1_top_box.step` | **open pocket up**, saddle down | PETG | yes, under the saddle |
| A2 lid | `A2_lid.step` | flat, **underside down** | PETG | none |
| A3 spool puck + cradle | `A3_bottom_box.step` | **puck opening up** (cradle down) | PETG | yes, under the cradle |
| A4 puck cover | `A4_cover_plate.step` | flat | PETG | none |
| A5 window insert | `A5_window_insert.step` | flange down | PETG (opaque) | none |
| Closure block | `closure_block.step` | flat top down | PETG | none |
| Hinge block | `hinge_block.step` | flat top down | PETG | none |
| Liner right / left | `liner_right.step`, `liner_left.step` | **on end (vertical)**, 5 mm brim | TPU 95A | none |

**PETG:** 0.2 mm layers, 4 perimeters, 40 % gyroid, 240/80 °C, 40 mm/s on external walls.
**TPU 95A:** 0.2 mm, 3 perimeters, 20 % gyroid, 225/50 °C, **20–25 mm/s**, retraction ≤ 1 mm,
direct drive strongly preferred. Vertical orientation matters: the liner profile is a
constant section, so every layer is the same slice and the fins come out clean.

### 0.2 The parts you buy

Ø5 × 36 mm steel dowel (hinge pin) · Ø5 × 2 plug (a 5 mm rod offcut) · M3 hardware below ·
3 mm 7×7 stainless cable coated to Ø4, 1.6 m · 2 swage sleeves · donor retractable reel ·
electronics per `BOM.md`.

### 0.3 Every screw in the lock

| Joint | Screw | Qty | Where it goes |
|---|---|---|---|
| A1 → C1, crown row | **M3 × 8 low-head cap** | 3 | vertical, from inside the bore at y = +6, x 25 / 75 / 135 |
| A1 → C1, skirt row | **M3 × 8 low-head cap** | 3 | horizontal (+y), from inside the bore at z = +8, same x |
| A3 → C1, crown row | **M3 × 8 low-head cap** | 2 | vertical, from inside the bore at y = +10, x 40 / 100 |
| A3 → C1, skirt row | **M3 × 8 low-head cap** | 2 | horizontal (+y), at z = −8, x 40 / 100 |
| Closure block → C2 | **M3 × 8 low-head cap** | 2 | vertical, from inside the bore at y = −7, x 83.5 / 96.5 |
| Hinge block → C2 | **M3 × 8 low-head cap** | 2 | vertical down, from inside the bore at y = −11.9, x 78 / 102 |
| A2 lid → A1 | **M3 × 10 countersunk 90°** | 4 | (14.5, −9.5) (14.5, 38.5) (145.5, −9.5) (100, 38.5) |
| A4 cover → A3 | **M3 × 8 countersunk 90°** | 4 | (50, ±20) (90, ±20) — a Ø56.5 bolt circle in the puck wall |
| Closure screw (the consumer one) | **M3 × 8 low-head cap** | 1 | down the latch bore into the closure block |

**Do not substitute M3 × 10 for the M3 × 8s.** Those pilots are 4–5.6 mm deep and a 10 will
bottom out and jack the joint apart.

⚠️ **Low-head** matters on the ten inside-the-bore screws. A normal socket cap head is 3 mm
tall and will not sink into the 2.3 mm counterbore, so it protrudes into the liner.

### 0.4 Tools

Hex drivers 2 mm and 2.5 mm · soldering iron with a fine tip · Ø2.5 mm drill (chasing print
pilots) · Ø4.2 mm drill (liner stud holes if they print tight) · small file · flush cutters ·
multimeter · wire strippers · crimpers for the swage sleeves (or a vise) · thread locker is
**not** used anywhere.

---

## 1. Stage A — clean the printed parts (30 min)

1. **Chase every tapped pilot with a Ø2.5 drill by hand.** The 22 pilots are modeled at Ø2.5
   so the M3 screws self-tap in PETG. Chasing them removes the first-layer squish and stops
   the plastic from splitting when the screw goes in.
2. **Test every screw in its own hole before anything is assembled.** Drive an M3 × 8 into
   each pilot, back it out, do the next. If one strips, drop a Ø2.5 nylon plug in and re-drill.
   Finding a stripped hole now costs nothing; finding it in stage E costs a teardown.
3. **Check the six liner stud holes per half** (Ø4.2 × 2 deep, at x 35 and 115, at −45° / 0°
   / +45° from each half's mid-arc). If your printer closed them up, open with a Ø4.2 drill
   held square to the wall — 2 mm deep only, the wall is 4.75.
4. **Deburr the bore.** Run a finger around the ten counterbores; scrape any lip flush so the
   liner sits flat.
5. **Fit-check the two halves dry**, no liner, no boxes: seam faces should meet with no rock.

---

## 2. Stage B — the hinge (20 min)

This is the joint everything else hangs off, so it comes first and gets tested alone.

1. **Hinge block onto C2.** Sit it on C2's outer surface with its lug pointing +y, spanning
   x 66.3–89.7. From **inside the bore**, drive 2 × M3 × 8 down through C2's bottom wall at
   y = −11.9, x 78 and x 102, into the block. Snug, not gorilla-tight — PETG.
2. **Dry-hang C2 on A3.** Hold A3 (the spool puck) beside C2 so the hinge block's lug drops
   between A3's two lugs (x 58–66 and 90–98). The three bores should line up on one axis.
   If the lug is too wide, file its faces, not the bore — you have 0.3 mm of end float.
3. **Drive the pin.** Push the Ø5 × 36 dowel in from the **x = 58 face** (the −x end). It
   passes lug 1, the hinge block's lug, and stops in lug 2's blind bore at x 96.
   *If it binds, back it out and ream the two A3 lugs with a Ø5.1 drill; never force it.*
4. **Swing test.** C2 should fall open under its own weight to about 60° and stop when the
   hinge block lands on the puck's flat top. That stop is designed; it is not a collision.
5. **Leave the Ø5 × 2 plug out for now.** It goes in at the very end, once you never intend
   to separate the halves again.

---

## 3. Stage C — the electronics, on the bench (2–4 h, spread over the checkpoints)

Nothing goes in the box until it works on the bench. Build up one block at a time.

### C.1 Checkpoint 1 — reader + logic (parts you already own)

Breadboard the Nano and the RC522. **RC522 power is 3.3 V, never 5 V.**

| RC522 | Nano | | Panel part | Nano |
|---|---|---|---|---|
| SDA (SS) | D10 | | Green button | D3 → GND |
| SCK | D13 | | Red button | D2 → GND |
| MOSI | D11 | | Red LED + 470 Ω | D8 |
| MISO | D12 | | Green LED + 470 Ω | D9 |
| RST | D4 | | Active buzzer (+) | D6 |
| 3.3V | 3V3 | | Buzzer (−) | GND |
| GND | GND | | | |

Flash `firmware/rfid_bike_lock_rc522/`. Install the **MFRC522** library first (Library
Manager, by GithubCommunity). Serial monitor at 115200.

**Pass when:** green button → chirp + `[wake]` · first fob tapped becomes master · a second
fob gives two red blinks and a long buzz · hold red 5 s → three beeps, tap master, tap the
second fob → it enrolls and now unlocks · tap red briefly → one blink and back to sleep.

**If the reader is not found (fast red ×5):** check SS/RST pins first, then that the module's
header is actually soldered, then that you are on 3.3 V.

### C.2 Checkpoint 2 — the solenoid driver

Build this on a **42 × 10.7 mm card** cut from your perfboard. This card is what later rides
the solenoid cart, so keep it to size.

On the card: IRLZ44N laid flat, 1N5819, 1000 µF Ø8 × 12.5 cap lying down, 100 Ω gate
resistor, 100 kΩ gate pulldown.

```
battery + ──┬─────────────── solenoid coil ── IRLZ44N drain
            │                     │
         1000 µF              1N5819  (cathode to +, band to +)
            │                     │
battery − ──┴──── IRLZ44N source ─┴── GND (common with the Nano)
Nano D5 ── 100 Ω ── IRLZ44N gate ── 100 kΩ ── GND
```

Two rules that are easy to get wrong and expensive:

- **The diode band faces the + rail.** Backwards, it is a dead short across your battery.
- **The solenoid runs straight off the cell**, not off the boost. It is the one high-current
  load; the MT3608 only feeds the Nano and reader.

**Pass when:** an authorized tap gives a solid clunk, and the Nano does not reset when it
fires. A reset means the supply is sagging — check the reservoir cap is really across the
coil supply and not somewhere useless.

### C.3 Checkpoint 3 — power chain

1. Set the **MT3608 output before connecting anything to it.** Feed it from the cell, put a
   meter on the output, turn the pot until it reads **6.00 V**, then power down.
2. Nano runs off **VIN** from that 6 V rail. The RC522 and LEDs run off the **Nano's 3.3 V
   and 5 V pins** through the AO3401 gate on D7.
3. TP4056: cell to B+/B−, load to OUT+/OUT−. **Charge with the lock asleep** — this board has
   no load sharing and a scan during charging confuses its termination.
4. Battery sense: 100 kΩ from the cell + to A0, 100 kΩ from A0 to GND.

**Pass when:** sleep current measures **1.5–3 mA**. If you see 20 mA the Nano never slept —
the usual cause is a button held low or `#define DEBUG` still keeping serial alive.

---

## 4. Stage D — load the top box (1 h)

Work with A1 on the bench, lid off, **before it goes on the chassis.**

1. **Print or fold a tray.** The reference model has a battery cradle and a 2 mm reader deck
   (`ref_tray`). Simplest version: a strip of 2 mm PETG or foam board under the reader at
   z = 53.5, with the battery below it.
2. **Battery** flat on the floor at x 19.5–69.5, y −7–27. Lead exits toward +x.
3. **Reader** on the deck, board x 19–79, **antenna end toward −x** so it sits under the
   window. Component side up. A 2 mm foam pad between it and the lid.
4. **Cart + solenoid + driver card** as one module at x 100.5–140.5. The solenoid's plunger
   must be on the channel axis: y = −4, z = 52. File the plunger's 45° nose before fitting.
   Trim the plunger tail so it ends by x 140.
5. **Nano on edge** at y 13.8, USB toward +x. Trim the pins flush after soldering.
6. **TP4056** on the floor at the +x wall, its USB-C poking into the 9.6 × 3.8 slot.
   **MT3608** on 4 mm standoffs above it.
7. **Buzzer** glued under the lid at (125, 30), over its Ø2.5 sound hole.
8. **Buttons and LEDs** into the lid: green at (86, 33), red at (86, 12), LEDs at (83, 22.5)
   and (89, 22.5). Pot the LED domes with clear RTV.
9. **Window insert** from *underneath* the lid — its flange sits in the lid's underside
   recess. RTV bead around the flange.
10. Leave the lid loose. **Repeat checkpoint 1 with everything in the box** before you screw
    it down: the metal-free PETG box should not change anything, but this is the last easy
    look inside.
11. Lid on, 4 × M3 × 10 countersunk, with the EPDM foam strip on the rim.

---

## 5. Stage E — boxes onto the chassis (30 min)

Both boxes bolt to C1 **from inside the bore**, which is why the liner is not in yet.

1. **A1 first.** Sit it on C1's top so the saddle mates. Reach into the bore and start all
   six M3 × 8: three vertical at y = +6 (x 25/75/135), three horizontal at z = +8 (same x).
   Start every screw before tightening any, then work them down in a crisscross.
2. **A3 second**, on the bottom: two vertical at y = +10 and two horizontal at z = −8, both
   at x 40 and 100.
3. **Closure block onto C2** if you have not already: 2 × M3 × 8 from inside the bore at
   y = −7, x 83.5 and 96.5. Its flat top must end up at z = 36.5.
4. **Close the clamshell and test the latch alignment.** Swing C2 shut and look down the
   latch bore from the top: you should see the closure block's tapped hole centred in it. If
   it is off, the block is rotated on C2 — loosen, nudge, retighten.

---

## 6. Stage F — the spool (1 h, the fiddly one)

This is the only step the model does not fully define, because it depends on your donor reel.

1. **Gut the donor reel.** Keep the flat power spring, its hub, and the spool if it fits a
   Ø51 pocket. Wear eye protection — those springs are under tension and will escape.
2. **Wind the cable.** 1.5 m of Ø4 coated cable on a Ø32 core is 6 wraps a layer, two layers.
   Wind it on before the spool goes in the pocket.
3. **Swage a ball stop on the inner end.** This is a security feature, not a convenience: it
   is larger than the Ø7 exit, so even with the cover off and the spool out, the locked cable
   cannot be pulled free.
4. **Route the working end out the Ø7 exit** at the −x end of the puck. Fit a steel bushing
   in that hole if you have one; the cable saws plastic over time.
5. **Anchor the spring's outer end** to the pocket wall. Improvise: a slot filed in the wall,
   or a screw through the spring's eye. Preload it two or three turns before the cover traps it.
6. **Cover on**, 4 × M3 × 8 countersunk, gasket under it.
7. **Swage the cable head** on the working end. Until the lathe part exists, a steel flat-bar
   mule with a cross-hole does the job for testing the latch.

**Pass when:** pulling the cable out and letting go reels it fully in, and the head snaps
past the plunger and stays.

---

## 7. Stage G — liners (15 min)

1. **Dry-fit one half first.** The liner half should drop into the bore with its six studs
   near their holes.
2. **Press the studs in progressively**, starting at one end and working along. They are
   Ø4.5 TPU into Ø4.2 holes — a firm push each, not one big shove.
3. A smear of silicone grease on the bore makes this much easier and does no harm.
4. Repeat for the other half. Fins should lean the same way on both.

---

## 8. Stage H — on the bike (5 min, the consumer step)

1. Open C2 to its 60° stop.
2. Set C1 on the down tube. The fins compress; that is the whole fit mechanism.
3. Swing C2 shut. It should close with hand pressure alone.
4. **One M3 × 8 down the latch bore** into the closure block. Snug it; the liner preload is
   what holds the clamp, the screw just stops it opening.
5. Drop the ejector spring into the bore on top of the screw.
6. **Drive the Ø5 × 2 plug** into the pin bore's entry at x 58, flush. From here the pin
   cannot be driven out — that is the point.
7. First boot: tap your chosen fob. It becomes master. Enroll the rest with the red button.

---

## 9. If something is wrong

| Symptom | Most likely cause |
|---|---|
| C2 will not close the last few mm | liner fins fouling the seam, or the closure block sitting proud of z 36.5 |
| C2 opens past 60° and jams | hinge block screws loose, so it is riding on the pin only |
| Screw spins forever in PETG | stripped pilot — plug with a Ø2.5 nylon rod and re-drill |
| Solenoid clunks weakly | it is on the boost rail instead of the cell, or the coil is a 12 V variant |
| Nano resets when the solenoid fires | reservoir cap not across the coil supply, or grounds not common |
| Reader works on the bench, not in the box | metal near the antenna, or the foam pad is too thick — the gap to the lid should be ~2 mm |
| Cable will not retract fully | spring preload lost during cover fitting; redo step 6.5 with one more turn |

---

## 10. What this manual does not cover

- **The donor spool anchoring** (§6.5) is the one improvised joint in the build. Everything
  else is dimensioned in the CAD.
- **Torque values.** PETG has no meaningful spec; snug plus a few degrees is the honest
  instruction. The aluminium version will get real numbers.
- **The firmware has never run on hardware.** Checkpoints 1–3 are the first time it will.
