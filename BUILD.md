# BUILD.md — the end-to-end build workflow (v0.7)

This is the answer to "can the BOM be assembled into a workflow where the entire
thing works?" — **yes, with the additions in §1**, following the sequence in §3
exactly. Every BOM item maps to a step; every step names its tool and access;
electrical bring-up checkpoints are interleaved so failures surface at the
cheapest possible moment. Produced from a 4-lens machine-assisted audit (BOM
mapping, wiring harness, build-order simulation, firmware bring-up) against the
gate-verified v0.7 geometry.

## 1. What the BOM was missing (now added — order these too)

| Item | Why it was missing | Resolution |
|---|---|---|
| **Cable head (Phase-1)** | The core latch part only existed as a Phase-2 "shop job" — nothing to lock on first build | BOM 23k: bench-mule square tang stock (steel flat bar) for Phase 0 + the round grooved head as a TAMU-shop lathe job (Ø10 head, square-flanked groove at Ø6.6, Ø5 stem swaged to the cable). Modeled as `89_mock_cable_head` (latched position, gate-checked) |
| **Ejector spring seat** | Its documented home ("under the bore floor") was consumed by the v0.6 closure screw channel | No new geometry needed: the spring sits **in the bore, on the closure screw's washer** (z30 ledge), Ø9 × ~15 free length, compressed ~5 mm by the seated head. Dropped in AFTER the consumer screw. BOM 21 re-spec'd |
| **JST connectors** | Promised throughout DESIGN, never on the BOM | BOM 16b: JST-XH kit (2/3/4-pin) + note: factory-protected 103450 cells ship with **JST-PH 2.0** pigtails — buy one PH pigtail or re-terminate |
| **Driver card stock** | The driver stage had no defined board | Cut a 42×10.7 card from the same 4×6 cm perfboard (BOM 16) |

## 2. The v0.7-final electrical architecture (one load-bearing change)

The audit found the solenoid driver stage sat in the bay, **150–200 mm of wire
from the solenoid** — 5–7× the design target, degrading the flyback clamp and
defeating the reservoir cap. Fixed: **all driver electronics live in the pod**
on a 42×10.7 card on the pedestal-cart’s −Y platform (v0.8.2: two Ø8 cart bosses, short M3 heat-sets)
(bosses at x66/x96, 2× M3 ST), components facing up (IRLZ44N flat, AO3401,
1N5819, Ø8×12.5 cap lying, divider) — **<30 mm to the solenoid**, and the bay
perf rack is deleted. The bay now holds only the cell + TP4056.

**The spine carries exactly 2 conductors** (TP4056 OUT+ / OUT− up to the
MT3608), 22 AWG, pulled bare through the Ø7 feed hole (connectivity
machine-verified) and connectorized in the pod. The battery-sense divider taps
OUT+ pod-side — no extra crossing. Nothing crosses the door hinge.

## 3. Bench build sequence (tool · access per step)

**Stage A — parts + inserts (open bench)**
1. Print 14 parts (+ TPU liners/shim); turn or order the hinge rod (BOM callouts; zero-lathe fallback: plain Ø4 rod + a cap both ends).
2. Press the heat-sets (see BOM 23a–23f; v0.8.2 adds 2× short M3 in the cart platform bosses): 4× M3 pod-rim bosses (soldering iron, straight down through the open pod top) · 2× M3 into TP4056-block/drum-web from below · 2× M2.5 pedestal tower top · 1× short M3 into the door pad’s TOP face (v0.8: all-M3) (door open, flange-up). **Gate: VERIFY JF-0530B hole spacing (24?) BEFORE the M2.5 inserts** — the cart is a minutes-long reprint.

**Stage B — pod electronics (all straight-down access; MUST finish before the lid ever goes on)**
3. Nano into the pod wall recess (edge-standing, pins trimmed flush, USB end at x39–47) → `nano_clamp` bar onto the crown bosses, 2× M3 ST flat.
4. Pedestal cart onto the pod pads — 2× M3 pan through the tower access holes (heads hidden under the solenoid later).
5. Build + solder the driver card (42×10.7): IRLZ44N flat, AO3401, 1N5819, cap lying, divider → onto the cart platform bosses (x66/x96, y−7.25), 2× M3 machine into the short heat-sets, straight down — do this BEFORE the cart goes into the pod if you prefer bench access; the cart+driver+solenoid drop in as one module.
6. **MT3608 onto the tower end-posts BEFORE the solenoid** (0.3 mm design clearance between them; clone solenoid width varies 13–16). Set 5.00 V under load *now*, on the bench.
7. Solenoid onto the tower — 2× M2.5×8 machine into the inserts. File the plunger's 45° ramp; **trim the plunger tail to end at x98** (machine-asserted against the wake button — untrimmed it collides).
8. ⚡ **Checkpoint 1**: bench-power the pod cartridge cluster from a 5 V supply — solenoid pulse test (300 ms via D5), MT3608 rail check, before anything is enclosed.

**Stage C — bay (independent of Stage B)**
9. LiPo stands on edge at the +y wall (lead corner at the strain-relief notch); TP4056 slides −X into its cradle until the USB-C registers in the wall port.
10. ⚡ **Checkpoint 2**: charge test through the wall port; verify OUT+/− feeds (fail-secure architecture depends on OUT wiring, not cell wiring — DESIGN §8).

**Stage D — marry bay to body, then harness**
11. Bolt the loaded bay to the body — 4× M4×12 from inside the open clamp bore (heads sub-flush). **This must precede spine wiring** — the spine window halves only align once bolted.
12. Pull the 2 spine conductors bare (bay → window → raceway → feed hole → pod), connectorize pod-side (JST-XH), leave the documented service loop bay-side so dropping the hatch-tray never strains the cell leads. Lay the pair in the open raceway → `spine_cover`, 2× M3 ST flat.
13. Hatch-tray on — 2× M3 machine flat into the block/web inserts, countersunk external.

**Stage E — lid (open bench, lid detached)**
14. PN532 onto the drop bosses — 4× M2.5 **nylon** + captive 1 mm foam pad (never steel: the antenna loop wraps the board perimeter). Button through its panel hole (own nut); LEDs press-fit. Dress the 4-wire lid loop (I2C + switched 5 V) with lift-slack + JST so the lid fully detaches.
15. ⚡ **Checkpoint 3**: full-system smoke test, lid resting in place: wake → scan window → tag read → solenoid pulse → sleep current. **Reflash access = lid off** (4 screws), not the hatch — the Nano lives in the pod.
16. Lid on — 4× M3 machine flat into the rim inserts, flush.

**Stage F — mechanical completion**
17. **Liners stay OUT until after drilling.** Door closed + clamped: drill the hinge bore Ø4.2 through all 8 knuckle segments (measure the rod first; 2-stage drill; deburr 16 mouths). Insert the rod tail-first from the front; head seats flush; `hinge_cap` + 1× M3 ST flat.
18. Slide the TPU liner keys in from the front face to the blind stop (click past the bump); halves captive, no glue.
19. Donor spool into the drum (bay bolted or not — clearance-verified either way; off-body is easier for winding). **Improvise per donor** (nothing is modeled — known gap): spring outer anchor to the ring wall, spool rotation on the cover's Ø10 hub, hold preload before the cover traps it. Route the cable out the snout; swage the end stop; swage the head (or bench-mule tang) on the working end. `spool_cover`, 3× M3 ST flat, flush.
20. Ejector spring drops into the bore later — **after** the consumer closure screw exists (on-bike step): screw → washer → spring → done.

**Stage G — on-bike (the consumer step)**
21. Open door → press onto the down tube → swing shut → ONE M3×10 machine-flat down the latch bore (v0.8) → drop in the ejector spring → enroll the master fob (first boot). Locked cable head now covers the screw.

## 3b. Print orientations (v0.8.3 — matches the `--dfm` scan table in the CAD)

Run `python cad/bike_lock_cq.py --dfm` for the live overhang report. Declared orientations
(`DFM_ORIENT` in the CAD is the single source of truth):

| Part | Orientation | Supports |
|---|---|---|
| body | pod rim up (as modeled) | yes — under shell + knuckles |
| door | seam face down | yes — under knuckles + bore ceiling |
| bay_module | cover/rabbet face down | yes — brick overhangs |
| lid | underside on plate | minimal — the 4 PN532 drop-bosses start 0.3 above the plate |
| pedestal_cart | flat z32 bottom on plate (v0.8.3 flush fix) | none |
| bay_hatch, spine_cover, nano_clamp, hinge_cap, usb_plug | flat | none |
| spool_cover | as modeled **with a raft** — its 3 nesting pads hold the disc 0.8 off the plate | raft |
| liners + shim | TPU: fins up, slow (~25 mm/s) | none |

## 4. Honest remaining gaps (will not stop the build, must not be forgotten)
- **Donor spool anchoring is unmodeled by design** (donor-dependent) — step 19 is the only improvised step in the workflow.
- **VERIFY-on-arrival gates**: solenoid hole spacing + width (13–16!), PN532 corner holes + dims, MT3608 true height, TP4056 USB overhang, insert brand dims, ST flat-head angle (80/90°), Nano USB variant, plunger Ø for the 6.5 ream decision, LiPo protection-PCB bump.
- **Read-range sanity check**: the Nano now sits ~10 mm below the PN532 keep-out column — verify range on real hardware (move to the far pod end is the fallback).
- Firmware is complete but has never run on hardware; Checkpoints 1–3 are the earliest failure surfaces.
