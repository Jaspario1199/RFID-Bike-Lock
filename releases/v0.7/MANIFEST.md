# Release v0.7 — manifest

Snapshot of CAD v0.7 ("electronics packaging machine-verified"), frozen from branch
`claude/file-contents-review-q89289` at the gate-green state. Every file in this
folder carries the `_v07` label. The live toolchain regenerates the unversioned
working copies under `cad/`; this folder is the fixed reference set.

**Gate at freeze: gaps 0 violations / 292 checks · matrix 0 clashing pairs @ 0.01 mm³ ·
door sweep 0.00 mm³ (0–110°) · entry corridor 0.00 mm³.**

## Printed parts (PETG first / ASA outdoor; liners + shim TPU 95A) — insert in numbered order

| File | Part (v0.7) |
|---|---|
| placed/01_body_v07.step | Body — right clamp + pod + latch boss + spine raceway + lid-insert bosses + Nano recess & crown clamp bosses + PN532 wall reliefs (v0.7) |
| placed/02_door_v07.step | Door — arc panel + hook flange + stepped closure flap with M4×L3 insert pad + dovetail groove + knuckles (v0.7) |
| placed/03_bay_module_v07.step | Bay module — brick + slim drum + service window + TP4056 flat cradle + LiPo edge-stand rail + hatch/spool insert seats (v0.7) |
| placed/04_lid_v07.step | Lid — crowned window skin, NFC ring, PN532 drop bosses + bezel step, countersunk screw frame (v0.7) |
| placed/05_pedestal_cart_v07.step | Pedestal cartridge — solenoid mount (M2.5 heat-sets) + MT3608 end-post rails + pad-screw access holes (v0.7) |
| placed/06_liner_right_v07.step | Liner right — TPU fin sleeve + dovetail keys + closure transit window (v0.7) |
| placed/07_liner_left_v07.step | Liner left — TPU fin sleeve + dovetail keys, swings with the door (v0.7) |
| placed/08_bay_hatch_v07.step | Bay hatch — service door / component tray: nesting pad, zip grid, rack screw holes, external countersinks (v0.7) |
| placed/09_spool_cover_v07.step | Spool cover — hubcap dish, countersunk triad at 90/210/330 on r31.25 (v0.7) |
| placed/10_hinge_rod_v07.step | Hinge rod — Ø4×~152 303 stainless, integral Ø6 head; ONE lathe op, see BOM callouts (v0.7) |
| placed/11_hinge_cap_v07.step | Hinge tail cap — screwed rod retention, 0.5 mm thermal float (v0.7) |
| placed/12_spine_cover_v07.step | Spine cover — flush raceway lid, 0.5 reveal, drip grooves (v0.7) |
| placed/13_perf_rack_v07.step | Perf rack — end towers for the vertical 40×23 cut perfboard (v0.7) |
| placed/14_nano_clamp_v07.step | Nano clamp — bar on crown bosses pressing the edge-standing Nano (v0.7) |
| stl/shim_v07.stl | Shim sleeve — TPU clip-in for Ø27–32 tubes, optional, not in the placed assembly (v0.7) |

## Electronics reference bodies (NOT printed — placement/packaging verification)

| File | Reference body (v0.7) |
|---|---|
| placed/90_mock_nano_v07.step | Arduino Nano — edge-standing in the pod wall recess, pins trimmed flush (v0.7) |
| placed/91_mock_perf_stack_v07.step | Perfboard 40×23 + component envelope, cap lying (v0.7) |
| placed/92_mock_tp4056_v07.step | TP4056 USB-C — flat in the bay cradle, port through the wall (v0.7) |
| placed/93_mock_lipo_v07.step | LiPo 103450 — edge-standing at the +Y bay wall (v0.7) |
| placed/94_mock_pn532_v07.step | PN532 — under the lid window on drop bosses, nylon M2.5 (v0.7) |
| placed/95_mock_solenoid_v07.step | JF-0530B solenoid + plunger TRIMMED to x98 (v0.7) |
| placed/96_mock_button_v07.step | 12 mm wake button — panel-mounted in the lid (v0.7) |
| placed/97_mock_led_a_v07.step / 98_mock_led_b_v07.step | 3 mm status LEDs — press-fit in the lid (v0.7) |
| placed/99_mock_mt3608_v07.step | MT3608 — vertical on the pedestal tower end-posts (v0.7) |

## Assembly-level files
- `bike_lock_assembly_v07.step` — true STEP assembly, named + colored components
- `bike_lock_combined_v07.step` — single multibody STEP (most reliable SolidWorks import)
- `renders/assembly_{closed,open,exploded}_v07.png`
- `docs/` — DESIGN / ASSEMBLY / BOM / HANDOFF / cad README snapshots at freeze
