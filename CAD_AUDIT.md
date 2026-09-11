# CAD_AUDIT.md — build audit of the CNC casing (rev 3d, 2026-09-11)

**Question asked:** are all mates and parts viable to make and assemble, and does the electrical
box actually house everything *including the wiring on every module*?

**Short answer:** the rev 3c geometry gates were all green and the answer was still **no** — five
defects would have stopped the build at the bench, one of them a modelling error in the model of
record. Rev 3d adds a second layer of machine checks (`python cad/cnc_casing_cq.py --audit`) that
model the *space around* each part, and moves things until that layer is green too. Everything
below is in the log `cnc-design/audit_rev3d.log`.

```
[audit] SUMMARY gates PASS | service PASS | fasteners PASS | pin path PASS | manufacturability PASS
```

---

## 1. What the audit checks that the gates did not

The rev 3c gates proved the *bare envelopes* do not intersect: parts vs parts, the C2 swing, the
frame mouth, the screw paths. They said nothing about whether a human can wire, plug, screw or
insert anything. The audit adds:

| Check | What it models | Rule |
|---|---|---|
| **Service envelopes** | for every module: 3.5 mm over each pad edge for a solder joint and a wire; both Ø15 × 3 button nuts; LED legs + resistor (10 mm); buzzer pins (5 mm); button solder lugs (6 mm); the reflash USB-C plug at the Nano; the charge plug's shell (8.4 × 2.6 × 6.5) and overmold (11.5 × 6 × 20); the cell pigtail; the cell → charger harness channel | each envelope may overlap only its own module (and the printed tray); nothing else, and it must be inside the cavity |
| **USB-C reach** | shell inserted from the outer recess floor | ≥ 5.5 mm into the receptacle |
| **Fastener engagement** | walks every screw axis through the solid: free run to the first thread, contiguous tapped length, pilot floor or through-tap, tip position | ≥ 1.5 D (4.5 mm) in 6061, ≥ 1.0 D in the steel closure block; no bottoming; the tip must land in air, never in a neighbouring part; the manual's length must be one that works |
| **Countersink wall + head rim** | the real seat geometry in the tube wall | ≥ 2.3 mm of wall under the deepest point; seated head rim inside the bore surface, clear of the liner ring |
| **Hinge pin insertion** | a Ø5 probe from x 20 to lug 1 | air in every closed-assembly part |
| **Machining / printing numerics** | thin walls, hole depth : diameter, fin thickness in nozzle line-widths, print fits | thresholds in the script |

---

## 2. Defects found, and what changed

### 2.1 The counterbores did not exist (modelling error) — **fixed**
All ten inside-out chassis screws (and the four block screws) were specified as low-head cap
screws in "Ø6.2 counterbores 2.3 deep cut from the bore side". The counterbore cylinder in the
model was placed *inside the bore air* (its floor was 2.3 mm toward the tube axis from the inner
surface, not into the wall), so it cut nothing. Probing C1 confirmed material begins at the bore
surface. Consequence: every head would have stood its full 2 mm proud into the liner ring, which
is 0.15 mm off the bore. The "7.30 mm wall under the counterbore" gate was measuring a phantom.

Correcting the counterbore to really sink a cap head 2.3 mm leaves only **1.8 mm** of aluminum at
its far edge on this curvature (Ø63.5 tube, hole 6 mm off the crest). So rev 3d switches to
**90° countersinks + ISO 10642 flat-head screws**: a cone is deep only on its axis, leaving
**3.40 mm** of wall everywhere, and the head top sits 0.4 mm below the surface with its Ø5.5 rim at
r 26.74 — **0.11 mm** inside the liner ring's outer face. Both are now gated.

### 2.2 Hinge-block screw with no material under it — **fixed**
`HB_SCREW_X` was `LATCH_X ± 12` = x 78 and **x 102**; the hinge block spans x 58..98. The second
screw threaded into air. Now x 64 / 92 (`HX0 + 6`, `HX1 − 6`).

### 2.3 Hinge pin could not be inserted — **fixed**
The pin enters lug 1 from the −x end and travels 36 mm along its axis. The A3 cradle's front
edge (y 0.5..1.5) sat 1 mm inside the pin's Ø5 circle over x 34..57, blocking the approach. A
Ø6 scallop along that edge (x 33..58) is the entry path.

### 2.4 Screw lengths — **fixed**
With the true seats, an M3 × 8 in the A3 crown row engaged 3.5 mm; the cover screws 3.0 mm; the
closure-block screws bottomed out in a blind pilot; an M3 × 8 consumer closure screw would poke
through the block into C2's wall. Result: closure-block pilots tapped through, cover pilots
deepened to 8, and the manual now reads **14 × M3 × 10, 4 × M3 × 8, 5 × M3 × 6, all countersunk**
with the audited engagement beside each row (ASSEMBLY_CNC.md §0.3).

### 2.5 The electronics did not fit once wires were counted — **fixed by moving six things**

| Finding | Evidence | Change |
|---|---|---|
| Nano 0.65 mm under the MT3608; 16 wires solder to the Nano | `gap 0.65 ref_nano – ref_mt3608` | MT3608 lifted to z 49.5 (11.5 mm standoffs), 4 mm above the Nano's wire zone |
| Buzzer 2.15 mm above the MT3608; its pins are 5 mm | `gap 2.15`, pins envelope clash | buzzer to (103.5, 22.85), over the Nano, 10 mm of air under it |
| Driver card sat over the Nano's −y wire edge | `svc_nano_wires_a × ref_driver_card 437 mm³` | Nano to y 16..34; card 40 long at x 102.5 |
| Driver card's −x wire end inside the red button | `svc_drv_wires_a × ref_button_red` | card +2 mm in x, 1 mm lower (under the nut) |
| Two Ø15 button nuts + two LEDs in the 34 mm bay | nut–LED body distance < 0 for every placement tried | LEDs to (23, 37.2) and (29, 37.2) — the empty strip along the +y wall beside the reader deck |
| Green button's nut on the lid-screw boss; buttons touching the reader deck (0.00) | boss at x 100, deck at x 80 | buttons to x 93; 4th lid screw to x 105 |
| USB-C receptacle 7.5 mm behind the recess floor; a plug shell is 6.5 | `USB-C plug insertion 3.0 mm` | TP4056 moved so the receptacle sits 0.5 mm into the wall slot: **6.0 mm** insertion; slot 10 × 4.2, outer recess 15.4 × 9.6 × 2 |
| TP4056 clipping the +x/−y lid-screw boss | `A1 × ref_tp4056 0.9 mm³` | TP4056 to y −5.5 |
| RC522 wires: 2 mm of foam above the board, joints need 3.5 | envelope broke through the lid | wires soldered on the underside, through a deck slot at x 16.5–21.5, toward the −x wall |
| Reflashing needed the Nano out from under the boost | — | Nano's USB-C faces −x into the bay; a 25 × 12 × 7 plug envelope is gated against everything box-mounted |

Every module's service envelope now clears everything it does not own, with 0 problems.

### 2.6 Puck wall around the cover screws — **thickened**
1.5 mm of aluminum on each side of an M3 tapped hole. `PUCK_WALL` 5.5 → 6.5 (puck Ø64): 2.5 mm
outside, 1.5 mm to the pocket (the pocket side is not load-bearing). Swing / stop / frame-entry
gates unchanged (stop still at 64°).

---

## 3. What is viable as designed (checked, no change)

- **Interference matrix:** 0 clashes across 12 parts + 14 reference bodies, liner press-fits at
  the designed volume.
- **Hinge:** C2 + both blocks swing 0–60° with 0.00 mm³ overlap; stop at 64° on the puck top;
  Ø46 frame passes the 65 mm mouth; a 2 mm −y pull is held by the pin (221 mm³ overlap); the
  closure block seats on the A1 roof (44 mm³ at 0.2 mm lift).
- **Screw paths:** every chassis through-hole is air in C1, every pilot is air in its box.
- **Liner studs:** all 12 land in holes deep enough (tip 0.2 short of the floor).
- **3-axis machinability:** A1 pocket 3 × D for the Ø8 corner tool; pin bore 7.65 × D; cable exit
  5.3 × D; lug wall 2.95 mm; lid-screw boss wall 2.75 mm. The ±45° liner-stud holes and the two
  screw rows per half need the half-tube on an angled fixture — two extra setups, no 4th axis.
- **Printing:** liner fins 1.4 mm = 3.5 line-widths at 0.4 mm; studs are 1.8 mm sideways stubs
  (print each half axis-up); window insert now 0.25 mm/side (was 0.15 — too tight for PETG);
  tray walls 1 mm (2 perimeters).

---

## 4. Cautions that remain (known, accepted)

| Item | Value | Why it is acceptable / what to watch |
|---|---|---|
| A1 −y wall left by the solenoid pocket | **1.0 mm** web, 32 × 17 | 6061, light finishing pass; the pocket only exists because the measured HS-0730B is 1.75 wider than the cavity and a wider box breaks the C2 swing (gated). Check for oil-canning after machining |
| Puck wall pocket-side of the cover screws | 1.5 mm | not load-bearing; if a tap breaks through, the spool pocket is the only thing it reaches |
| Button nut assumption | Ø15 × 3 | the common 12 mm sealed button; a Ø16 nut fails the LED/boss clearance — re-run `--audit` with `BTN_NUT_D` changed before buying different buttons |
| Solenoid lead exit | +x end of the body, 0.65 mm under the lid | leads must exit sideways, not up |
| Reference-body tolerances | as measured / datasheet | the TP4056, MT3608 and driver card are envelopes; a board 1 mm larger in any axis should be re-entered before machining |
| Not yet audited | R4 internal-corner sweep, paired-bore alignment stack-up, EPDM gasket compression | listed in CNC_CASING.md §9 |

---

## 5. Reproduce

```
python cad/cnc_casing_cq.py --gates     # geometry gates only (~10 min)
python cad/cnc_casing_cq.py --audit     # gates + build audit (~15 min)  -> cnc-design/audit_rev3d.log
python cad/cnc_casing_cq.py             # STEP/STL export
python cad/cnc_drawings.py              # shop drawings
python cad/cnc_render_sets.py           # section / open STL sets for the renders
cd cad && xvfb-run -a openscad -o ../renders/cnc/cnc_interior_plan.png -D 'view="interior"' \
   --camera=80,15,50,0,0,0,400 --imgsize=1800,1000 --projection=o render_cnc.scad
```

Renders: `renders/cnc/cnc_interior_plan.png` (top-down, lid off) and `cnc_interior.png` show the
audited layout; `cnc_section.png` the latch / block / hinge slab; `cnc_open.png` C2 at 60° with a
Ø46 tube entering.
