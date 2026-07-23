# Release v0.8.3 — manifest

This folder holds the **current frozen STEP set** (files labeled `_v083`). It carries the
whole v0.8 lineage — the sections below record each sub-iteration (v0.8 → v0.8.1 → v0.8.2 →
v0.8.3); older sub-states are recoverable from git history. Per the repo reorg, releases are
**STEP-only** (per-part `placed/` + assembly + combined); STL/renders/doc-snapshots are
regenerable from the source at this tag.

## v0.8.3c — pod-corner "swooping horn" root-cause fix (owner-flagged)

The knife-edge cusps at the pod's top corners were root-caused past the rebate itself: the
**PN532 board's square corners sat only 0.3 mm from the pod's OUTER corner surface** — no
relief could clear them without carving the corner wall to a blade. Systemic fix, all
machine-verified (gaps 0/292 · support 0/27 · matrix 0 · sweep 0.00):
- **Board shifted +3 mm in X** (`pn532_x` 2→5; lid window/bezel/bosses/NFC ring follow the
  one parameter) so its corners fit inside a uniform-wall boundary with 0.4 clearance.
- **Rebate contour rebuilt as an inward offset of the OUTER plan** (−1.3/side, corner arcs
  concentric with the pod's outer corners) → the remaining wall is a uniform 1.3 mm by
  construction, corners included. It also now stops at the z53 seat plane (the board top
  dropped to z52.7 via `PN532_BOSS_DROP` 1.5→2.1), so the seat rim stays full thickness.
- **Front lid screws moved x50→x54** — the board shift put the board edge and the lid's
  drop-bosses into the old rim-boss columns (gate-caught); at x54 everything clears ≥1 mm.

## v0.8.3b — pod-rim visual-flow fix (owner-flagged divots)

The PN532 wall reliefs were FIVE separate stepped box cuts whose raw terminations read as
divots gouged out of the top-wall corners. Replaced with **one continuous board-seat
rebate** following the pod interior's own rounded contour (+1.8/side, r4 corners for the
board's square-corner clearance), terminating at the x=50 lid-boss centerlines so the step
ends are swallowed by the boss cylinders. Same function (admits the 41 mm board), now reads
as an intentional ledge. Re-gated: gaps 0/292 · support 0/27 · matrix 0. STEP set refreshed
in place (`_v083` labels kept).

## v0.8.3 — environmental + DFM hardening (hard critique pass)

Multi-domain critique (manufacturability / water ingress / power), every finding either
fixed in CAD and machine-verified, or resolved in the docs:

**Water** (nothing was addressed before this pass — full table in DESIGN.md §4.5):
- **Latch-bore weep** (Ø2.2, offset from the screw axis): the Ø11×26 bore is open to the
  sky and pooled rain on the plunger — it now drains into the tube bore. Grease the plunger.
- **Drum-void weep** (Ø2.5 at the ring's lowest point): the snout enters at z≈−74 but the
  void bottoms at −90.5 — a 16 mm bucket under the donor spring, now drained.
- **New `usb_plug` printed TPU part**: squish-fit plug for the bay USB-C port (wheel-spray
  zone), flange + pull tab + lanyard hole.
- Documented seals (ASSEMBLY + BOM 30a-30c): EPDM foam tape on the lid rim, clear RTV over
  the LED domes, silicone grease on the plunger. Weeps must NOT be plugged.

**Manufacturability:**
- **Pedestal cart now prints dead flat**: the driver bosses hung 1 mm below the base plane
  (the part rocked on the plate). Base + platform + bosses now share one z32 bottom;
  DRV_SEAT rose to 36.3 (insert pocket keeps a 0.5 printed floor); the card gained an
  air gap under it (bonus drainage). Driver station nudged +0.4 y for wall clearance
  (gate-caught at 0.075 mm).
- **New `--dfm` mode**: report-only overhang scan of every printed part in its declared
  orientation (`DFM_ORIENT` = the documented orientation table, mirrored in BUILD.md §3b).
  Spool cover: print with a raft (its 3 nesting pads hold the disc 0.8 off the plate).

**Power (DESIGN.md §4.5):**
- **6 V-rail option documented as the first fallback**: MT3608 → 6.0 V, solenoid at full
  rated force (kills the 70%-at-5V compromise), Nano moves to VIN, PN532 feeds from the
  Nano 5 V pin through the existing P-FET gate. Zero new parts.
- **TP4056 load-sharing honesty**: charge with the lock asleep; clean load-share fix
  logged as a v2 item.

**Gate at freeze: gaps 0/292 · matrix 0 · sweep 0.00 mm³ · support 0/27 · dfm reviewed.**

---

# v0.8 lineage notes (original v0.8 manifest follows)

Snapshot of CAD v0.8 ("all-M3 heat-set fastening rebuild"), frozen from branch
`claude/file-contents-review-q89289` at the gate-green state. Every file in this
folder carries the `_v08` label. The live toolchain regenerates the unversioned
working copies under `cad/`; this folder is the fixed reference set.

**Gate at freeze: gaps 0 violations / 292 checks · matrix 0 clashing pairs @ 0.01 mm³ ·
door sweep 0.00 mm³ (0–110°) · entry corridor 0.00 mm³.**

## v0.8.2 structural pass — every load-bearing hole backed by solid, machine-audited

A new **`--support` gate** (collar-containment wall check) was built to catch the exact
failure the owner flagged: *"holes cut into thin walls / features stacked on top of each
other without connecting to solid."* It probes a required collar around all 27 load-bearing
threaded holes and reports the real backing wall. Initial run: **17 under-supported holes.**
All 17 are now resolved, re-verified against every gate (**gaps 0/292 · matrix 0 · sweep
0.00 mm³ · support 0/27**):

- **Bay bolts ×4** — the Ø9 boss was unioned *before* the cavity cut, so the cavity ate it
  to a crescent (~0 wall). Now unioned *after* → full 2.5 mm collar merging into the near wall.
- **Hatch ×2** — the Ø4 pocket pierced the 3 mm floor into the cavity. Relocated to clear
  spots (drum web / free floor lane) with floor→cavity backing pillars; a pad notch admits them.
- **Spool ×3** — buttress was clipped to the drum bore, starving 2 of 3. Now a full Ø9
  buttress behind the rabbet floor → 2.5 mm.
- **Pedestal pads ×2** — the pad overhangs the tube bore; switched to a **short M3** insert
  that sits above the bore, and moved 76/86 → **79/87** to clear the solenoid collar.
- **Solenoid @71** — its collar is capped ~1.35 mm on the boss side by the mandatory latch-boss
  clearance (documented; full ≥1.5 on the other three sides).
- **PN532 ×4** — the nylon pilot pierced the drafted RF window skin; now **blind** (grip is
  the full-wall boss), and the antenna-corner window skin stays unbroken.
- **Driver-card bosses ×2** *(design-level)* — were disconnected lumps the builder DROPPED
  (the card had **nothing to mount to**). **Final resolution (Option C): the driver card now
  rides the pedestal-cart's −Y platform**, not the body — the cart already carries the
  solenoid, so this puts the driver in a tiny flyback loop with the coil it drives, on a
  solid printed part (no body bracket), and makes driver+solenoid+cart one serviceable module
  with good RF separation from the lid antenna. The platform stays above the door-swing arc.
- **Closure insert** *(design-level)* — the door flap was being **erased by the tube bore**;
  it's now unioned after the bore (it lives in the liner's transit-window gap) and **both**
  liners carry a relief. Its −Y-bottom corner is at the Ø46-tube surface (chamfered for
  clearance, backed by the mounted tube in service; low-cycle set-once clamp).
- **Hinge tail-cap** *(carve-out)* — no boss can back it without breaking the door swing
  (rod + tube + OD + swing all converge), so it reverts to an **M3 self-tap** (its v0.7 spec)
  — a near-zero-load, single-assembly rod retainer.

Also: the lid top-cover perimeter is filleted (was a sharp arris) so the crowned face flows
into the sides. **Re-export the STEP/STL and renders from the v0.8.2 source before printing.**

## v0.8.1 refinement — heat-set holes tuned for a snug, clean fit

- **Pocket Ø 4.1 → 4.0, LOCKED** (owner decision + research: ruthex / Prusa/Voron / CNC
  Kitchen / Hiren size chart all spec ~Ø4.0 for M3 heat-sets with OD ~4.4–4.6, which is the
  typical generic-assortment M3). No test-fit needed to order. **One number** (`INS3_D` /
  `INS3S_D` in the CAD) sets every M3 pocket — change it once and the whole design re-cuts.
- **Lead-in relief at every pocket mouth** (Ø `INS3_D+1.4` × 1.0, plus a smaller one at the
  M2.5 solenoid pocket): gives the plastic the insert displaces somewhere to go, so the
  insert seats flush and clean instead of mushrooming. This relief is wider than any
  candidate bore (3.7–4.2), so tuning the pocket Ø never disturbs it.
- **`heatset_coupon` (new, NOT in the assembly)** — a graduated test bar: M3 holes at
  3.7/3.8/3.9/4.0/4.1/4.2 (front row) + M2.5 at 3.4/3.5 (back row), each with the same
  lead-in relief and a corner notch marking the small-Ø end. **Print it first** in the same
  material/settings, press one insert from your kit into each hole, and pick the Ø that
  grips snug + seats clean. Report that number and every pocket in the design locks to it.
  Exported at `heatset_coupon_v083.step` (STL regenerable from source).

## What changed from v0.7 → v0.8

Fastening only — the geometry envelope is identical to v0.7 (all changes are internal
pocket/boss geometry). **Every threaded joint is now an M3 machine screw into an M3 brass
heat-set insert**, for a super-refined printed prototype. Conversions:

| Joint | v0.7 | v0.8 |
|---|---|---|
| Closure screw (consumer) | M4×8 + short M4 heat-set | **M3×10 + short M3 heat-set** (Ø4.0×L3.8) |
| Bay module → body (×4) | M4×12 pan self-tap | **M3×12 socket-cap + M3 heat-set** (Ø6.0 counterbore) |
| Pedestal pads (×2) | M3 pan self-tap | **M3 + M3 heat-set** in the body pads |
| Driver-card bosses (×2) | M3 self-tap | **M3 + short M3 heat-set** (card rests on boss top) |
| nano-clamp (×2) | M3 ST flat self-tap | **M3 machine-flat + M3 heat-set** |
| Spine cover (×2) | M3 self-tap | **M3 machine-flat + M3 heat-set** |
| Spool cover (×3) | M3 ST flat self-tap | **M3 machine-flat + M3 heat-set** (ring-wall buttresses added) |
| Hinge cap (×1) | M3 ST flat self-tap | **M3 machine-flat + M3 heat-set** |
| Lid (×4), Hatch (×2) | M3 machine-flat + M3 heat-set | unchanged (already inserts) |
| **Solenoid (×2) — carve-out** | M2.5 machine + M2.5 heat-set | unchanged (its tabs are M2.5) |
| **PN532 (×4) — carve-out** | M2.5 nylon | **M3 nylon** into printed bosses (no brass — RF) |

Also removed 2 vestigial features (nano-*sled* foot pilots; deleted perf-rack's hatch
cartridge screws). Insert tally: **~19 full M3 (Ø4.1×6.5) + 3 short M3 (Ø4.0×L3.8) + 2 M2.5
(Ø3.6×4.5)**; the PN532 uses 4 nylon M3 into printed bosses (no insert).

## Printed parts (PETG first / ASA outdoor; liners + shim TPU 95A) — insert in numbered order

| File | Part (v0.8) |
|---|---|
| placed/01_body_v08.step | Body — right clamp + pod + latch boss + spine raceway + M3 heat-set pockets throughout (lid rim, nano/driver crown bosses, hinge-cap end, closure pad) (v0.8) |
| placed/02_door_v08.step | Door — arc panel + hook flange + stepped closure flap with **short M3 insert** pad + dovetail groove + knuckles (v0.8) |
| placed/03_bay_module_v08.step | Bay module — brick + slim drum + service window + TP4056/LiPo holders + **M3 heat-sets** for bay bolts, hatch & spool cover (3 ring-wall buttresses) (v0.8) |
| placed/04_lid_v08.step | Lid — crowned window skin, NFC ring, PN532 drop bosses (**M3 nylon**), countersunk M3 screw frame (v0.8) |
| placed/05_pedestal_cart_v08.step | Pedestal cartridge — solenoid mount (**M2.5 heat-sets**, carve-out) + MT3608 rails + M3 pad-screw access (v0.8) |
| placed/06_liner_right_v08.step | Liner right — TPU fin sleeve + dovetail keys + closure transit window (v0.8) |
| placed/07_liner_left_v08.step | Liner left — TPU fin sleeve + dovetail keys, swings with the door (v0.8) |
| placed/08_bay_hatch_v08.step | Bay hatch — service tray; 2× M3 machine-flat into bay inserts (vestigial cartridge screws removed) (v0.8) |
| placed/09_spool_cover_v08.step | Spool cover — hubcap dish, 3× M3 machine-flat into ring-wall heat-sets (v0.8) |
| placed/10_hinge_rod_v08.step | Hinge rod — Ø4×~152 303 stainless, integral Ø6 head; one lathe op (v0.8) |
| placed/11_hinge_cap_v08.step | Hinge tail cap — M3 machine-flat into the shell-end heat-set, 0.5 mm thermal float (v0.8) |
| placed/12_spine_cover_v08.step | Spine cover — flush raceway lid, 2× M3 machine-flat into raceway heat-sets, drip grooves (v0.8) |
| placed/13_nano_clamp_v08.step | Nano clamp — bar on crown bosses, 2× M3 machine-flat into heat-sets (v0.8) |
| shim_v083.step | Shim sleeve — TPU clip-in for Ø27–32 tubes, optional (print from STEP or regenerate the STL) |

## Electronics reference bodies (NOT printed — placement/packaging verification)

| File | Reference body (v0.8) |
|---|---|
| placed/89_mock_cable_head_v08.step | Cable head (Phase-1 lathe job) — latched in the bore (v0.8) |
| placed/90_mock_nano_v08.step | Arduino Nano — edge-standing in the pod wall recess (v0.8) |
| placed/91_mock_driver_stack_v08.step | Driver card 42×10.7 on pod crown bosses, <30 mm from the solenoid (v0.8) |
| placed/92_mock_tp4056_v08.step | TP4056 USB-C — flat in the bay cradle (v0.8) |
| placed/93_mock_lipo_v08.step | LiPo 103450 — edge-standing at the +Y bay wall (v0.8) |
| placed/94_mock_pn532_v08.step | PN532 — under the lid window on M3-nylon drop bosses (v0.8) |
| placed/95_mock_solenoid_v08.step | JF-0530B solenoid + plunger trimmed to x98 (v0.8) |
| placed/96_mock_button_v08.step | 12 mm wake button — panel-mounted in the lid (v0.8) |
| placed/97_mock_led_a_v08.step / 98_mock_led_b_v08.step | 3 mm status LEDs (v0.8) |
| placed/99_mock_mt3608_v08.step | MT3608 — vertical on the pedestal tower end-posts (v0.8) |

## Assembly-level files
- `bike_lock_assembly_v08.step` — true STEP assembly, named + colored components
- `bike_lock_combined_v08.step` — single multibody STEP (most reliable SolidWorks import)
- `renders/assembly_{closed,open,exploded}_v08.png`
- `docs/` — DESIGN / ASSEMBLY / BOM / HANDOFF / BUILD / cad README snapshots at freeze

## VERIFY-on-arrival (v0.8 additions)
- **M3 brass heat-set brand/dims** — pockets are Ø4.1×6.5 (full) and Ø4.0×L3.8 (short, closure + driver). Confirm your insert set matches before pressing.
- **Bay clamp strength** — the 4 bay bolts dropped M4→M3; fine for a prototype clamp, but if the bay ever works loose, that joint is the first to revisit (or go back to M4 there only).
- **PN532 read range** — nylon M3 preserves it, but still bench-test range on real hardware (the Nano sits ~10 mm under the antenna).
- Everything on the v0.7 VERIFY list still applies (solenoid hole spacing, PN532 corner holes, MT3608 height, TP4056 USB overhang, ST vs machine flat-head angles now all machine 90°).
