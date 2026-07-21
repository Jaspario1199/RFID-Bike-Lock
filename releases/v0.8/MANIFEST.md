# Release v0.8 — manifest

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
  (the card had **nothing to mount to**). The seat is raised to z35.5 (above the door-swing
  arc) and each boss rides a routed **shelf + tie + leg bracket** to the +Y crown, with the
  shelf also anchored to the −Y wall lip. Card mounts to real structure now.
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
  Exported at `stl/heatset_coupon_v08.stl` and `heatset_coupon_v08.step`.

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
| stl/shim_v08.stl | Shim sleeve — TPU clip-in for Ø27–32 tubes, optional (v0.8) |

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
