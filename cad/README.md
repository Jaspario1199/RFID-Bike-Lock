# CAD — parametric housing model (v0.6, CadQuery → STEP)

`bike_lock_cq.py` is the source of truth: a parametric [CadQuery](https://cadquery.readthedocs.io)
model that builds true BREP solids and exports **STEP** (SolidWorks-ready) and STL for
every part. Every dimension from DESIGN.md §6 is a named variable at the top of the file.

**Status: v0.6** — closure/hinge/verification overhaul on top of the v0.5 "spine + door"
architecture (still current: the door is a light arc panel that verifiably swings clear,
0–110°, machine-checked; pod, bay, and slim Y-axis drum all live on the body's right
side; the entry corridor is kept empty by construction). v0.6 was driven by a full
geometric audit that found and fixed 12 defects (D1–D12, all machine-confirmed) the old
verification missed: the closure screw now reaches a real M4 insert over a solid floor
instead of piercing into the tube cavity (D1/D2); the lid, spool cover, hatch, and bay
screws all land on working pilots instead of open cavities (D3–D6); the two glued end
plugs and their blind pins are gone, replaced by a single Ø4×~152 stainless **hinge rod**
with an integral turned head and a screwed **hinge cap** (owner request, no glue); the
sealed wire spine opened into a lay-in raceway closed by a screwed **spine_cover** (owner
request); the liner is retained by dovetail keys instead of adhesive/foam tape; the
battery bay was repacked so the LiPo and TP4056 no longer contest the same floor (D11);
and a merged pedestal/solenoid hole pair was separated (D12). Verification grew a
`--gaps` exact-distance mode, `--matrix`'s clash floor tightened to 0.01 mm³ (`--strict`
0.001), the sweep's moving set now includes `liner_left` (the old fixed-set sweep is
what hid D10, a liner gouge), and `--export-assembly` regenerates every STEP output off
one `placements()` table — see **Verification** below for all four modes.
v0.3 and v0.4 are preserved in `archive/`. Rendered and verified; nothing test-printed.

## Working in SolidWorks

**Fastest start: open `step/bike_lock_combined.step`** — all 12 parts positioned, as a
single multibody file (imports the same reliable way as the individual parts; each body
is separately selectable/hideable in the Solid Bodies folder). `bike_lock_assembly.step`
is the same content as a true STEP *assembly* with named, colored components — some
SolidWorks configurations open it blank; if so, untick Tools → Options → Import →
"Enable 3D Interconnect" and reopen, or just use the combined file. Neither carries
mates (STEP can't); parts are frozen in their correct positions. The optional `shim`
isn't included since it occupies the liner's space.

Open any `step/<part>.step` directly — each imports as a clean solid body (real faces,
direct-editable, measurable, assemblable, FEA-able). STEP carries no feature tree; to
iterate parametrically either edit `bike_lock_cq.py` and re-export, or rebuild a part
natively in SW using the parameter block as the spec.

**Native SW assembly in 2 minutes (no mates needed):** use `step/placed/01..12_*.step`
— every part is exported already moved/rotated into its final global position (including
the lid, spool cover, hinge rod, hinge cap, and spine cover). In a new assembly: Insert Component → pick a file →
press the green ✓ WITHOUT clicking in the viewport (drops at the assembly origin = its
correct position). Repeat through the numbered list; every component arrives placed and
Fixed. These are single-solid files — the format that imports/display most reliably.

**If a multibody/assembly STEP opens with a populated tree but a blank viewport:** show
the bodies (right-click Solid Bodies folder → Show), press `f`; if still blank, untick
Options → Performance → "Enhanced graphics performance" (restart), or as a last resort
enable software OpenGL — and verify the file itself in eDrawings.

To regenerate everything: `pip install cadquery` then `python bike_lock_cq.py`
(or `python bike_lock_cq.py lid drum_module` for specific parts).
`legacy_bike_lock_v02.scad` is the retired OpenSCAD v0.2, kept for reference;
`render_v03.scad` only composites the exported STLs for preview renders.

## v0.7 part set (14 printed parts + 1 lathe rod + 11 electronics reference bodies)

v0.7 adds machine-verified ELECTRONICS PACKAGING: every BOM electronic is a
placed reference body (89+ numbering, green in renders, in `step/placed/` for
SolidWorks placement work - NOT printed), and every board has a modular
holder: the driver card (42×10.7 cut perfboard) sits on two Ø7 crown bosses
on the pod's −y strip (x66/x96, 2× M3 ST, <30 mm from the solenoid — the bay
perf rack was deleted, see BUILD.md §2), `nano_clamp` (edge-standing Nano in
a pod wall recess, clamp bar on crown bosses), TP4056 flat cradle rails (USB
correctly through the wall - the v0.5 vertical slot pointed it at the floor),
MT3608 end-posts on the pedestal tower, edge-standing LiPo with rail + wall +
block face. `89_mock_cable_head` models the latched cable head (Ø10 head,
ring groove at the plunger line, ~1.6 mm plunger engagement). The --gaps
table asserts the packaging: solenoid-to-lid 1.0, plunger-tail-to-button 1.0
(tail MUST be trimmed to x98), board recess seats, cell containment,
cable-head latch engagement - 292 checks.

| Part | Role |
|---|---|
| `body` (v0.7) | right clamp + asymmetric pod + latch boss + **open wire-spine raceway** + pedestal pads + swept closure pockets (D1/D2 fixed: the screw now reaches a real insert over a 3.7 mm solid floor instead of piercing the flange) |
| `door` (v0.7) | light arc panel + closure hook flange & low insert pad + hinge knuckles — verified to swing clear |
| `bay_module` (v0.7) | right-side brick (LiPo stood on edge to clear the TP4056 block — D11 — plus zip grids), slim Y-axis drum Ø68×32, snout; bolts by 4× M4 pan screws from inside the bore, now fully sub-flush (D5) |
| `bay_hatch` (v0.7) | bottom cover, doubles as the component **tray** (nesting pad + zip-anchor grid); 2× M3 machine screws into heat-sets on the external face — leave a service loop so pulling the tray doesn't strain the cell leads |
| `pedestal_cart` (v0.7) | solenoid mount on the pad system; attach pads moved off the solenoid holes (D12; VERIFY dims live here) |
| `lid` (v0.7) | window skin, NFC ring, button dish, PN532 pocket on drop-bosses (4× nylon M2.5, no tape); now has real pilots in the body rim (D3) — 4× M3 CS machine into heat-sets |
| `liner_right` / `liner_left` (v0.7) | TPU fit system, dovetail-keyed into each shell half (no adhesive); `liner_left` carries the closure's swept-form transit window (D10 fix) |
| `shim` (v0.7) | TPU fit-system C-ring extension (unchanged; not in `placements()` — occupies the liner's space) |
| `spool_cover` (v0.7) | outboard (+Y) drum face plate; screw circle moved onto the ring-wall boss and re-clocked so one screw sits on the vertical axis (D4/D5 fix) |
| `hinge_cap` (v0.7) | screwed tail cap capturing the hinge rod's 0.5 mm axial float — replaces the glued end plugs (D7) |
| `spine_cover` (v0.7) | screwed cover plate closing the wire raceway, drip grooves on the underside (owner request) |
| `hinge_rod` *(lathe, not printed)* (v0.7) | single Ø4.00×~152 mm 303-stainless rod, integral Ø6.0×1.6 turned head — one lathe op from Ø6 bar |

The pedestal still uses the standardized flat-pad system (12 mm pads, tops at z=32).

Assembly-audit fixes implemented (ASSEMBLY.md §3): **plunger-as-pin** (Ø6.6 channel, no
separate pin/spring/coupling), the **single hinge rod** (owner request, replacing the two
blind hinge pins and their glued end plugs — D7), card-edge board pockets, and near-total
M3 self-tap standardization (the M4 closure, the M2.5 solenoid pair, and the M3 lid/hatch
pair now use brass heat-sets; everything else is a direct self-tap).

## Verification (v0.6)

`bike_lock_cq.py` runs an entry-corridor interference check on every export automatically.
Four more checks run as explicit CLI modes — none of these ship parts, they only assert
things about the model:

- **`--sweep`** — rotates the door **and `liner_left`** 0–110° about the hinge against
  everything else and asserts 0 mm³ overlap at every step. The moving set used to be
  door-only against a body+bay+lid-only fixed set; that gap is exactly what hid D10 (a
  25.5 mm³ gouge through `liner_right`'s base ring at θ=10° that the body-side relief
  never covered because the liner never got its own).
- **`--matrix`** — full pairwise static-interference check over every part in
  `placements()`. The true-clash floor tightened from 1 mm³ to **0.01 mm³** (an OCC-noise
  study); `--strict` drops it further to **0.001 mm³**, which stays clean at exact
  tangency but is finer than FDM tolerance can act on, so it's opt-in.
- **`--gaps`** — exact minimum-distance check (`BRepExtrema_DistShapeShape`) on every
  placed pair, layered on top of the boolean clash gate so a true overlap and an intended
  tight fit can't be confused. Each pair is checked against `GAP_SPECS`: a `(min, max)`
  mm band (e.g. liner-in-bore 0.05–0.30), the `CONTACT_OK` sentinel for clamped faying
  faces where 0.00 mm is correct and only actual interpenetration should fail (seam/hook,
  pod rim, pedestal pads, hinge-rod head seat, hinge-cap seat, spine-cover seat), or the
  plain clash-only floor if the pair is unlisted. `feature_probes()` adds local box probes
  for fits a whole-pair distance can't isolate on its own — a 0.00 mm contact anywhere
  else on the same pair would swamp the measurement otherwise — currently the knuckle
  axial gap (0.6–1.0 mm at 6 x-stations, asserting `hinge_gap`'s ~0.8 mm net float) and
  the hinge-rod running-bore fit (0.05–0.15 mm, checked separately in `body` and `door`).
- **`--export-assembly`** — regenerates `step/placed/`, the combined multibody STEP, and
  the assembly STEP, all off the same `placements()` table `--matrix` and `--gaps` read,
  so the three outputs can't drift apart from each other.

All four currently PASS.

## Design principles applied in v0.2

Standard FDM design-for-manufacturing + product-design practice:

- **One radius family** (R14 belt / R11 pod / R3 details / 1.2 mm edge breaks) so every
  surface looks like it belongs to the same object.
- **Drafted walls**: the pod tapers 1.8 mm base→lid, with the interior drafted the same
  amount → **uniform ~3 mm walls** everywhere (no massive solids; the latch boss and
  solenoid pedestal are gusseted/hollowed instead of solid).
- **The part line is a design line**: the closure skirt is the left half of a full
  wrap-around **belt band**, separated from the pod by a 0.8 mm shadow-gap groove — the
  seam reads as intentional, and the hidden-screw closure lives inside it.
- **Fairings, not intersections**: pod→tube and drum→body transitions are blended
  (teardrop), keeping overhangs ≤45° so the shells print without heavy support.
- **Chamfered bottom edges** everywhere a part meets the build plate; countersunk lid
  screws; recessed USB niche; embossed NFC target ring so the user knows where to tap.
- **Wiring is modeled, not implied**: two clip-lip floor raceways (RF-zone ribbon x4–54,
  power/solenoid run x60–100), a driver tray over the Nano bay with wire notches and
  zip-tie holes, two battery saddles giving the 18650 holder a level bed (with zip-tie
  pass-unders), and two mushroom strain-relief posts for the lid's service loop.

## Print guide

| Part | Material | Orientation / notes |
|---|---|---|
| body (shell_right) | PETG first / ASA outdoors | pod-opening up; light support under belt + spine rib |
| door (shell_left) | PETG / ASA | split-face down, near-zero support |
| bay_module | PETG / ASA | hatch-faces down; supports under the drum ring arc only |
| bay_hatch | PETG / ASA | flat, no support — now the component tray, see drill-out note below |
| lid | PETG / ASA | top-face down on a smooth sheet (window skin + NFC ring print first) |
| pedestal_cart, hinge_cap | PETG | flat side down, minutes each |
| spine_cover | PETG / ASA | curved face up; dry-fit before drilling — see orientation/warp VERIFY below |
| liner halves, shim | TPU 95A | 2 perimeters, 15% infill, ~25 mm/s, fins vertical; keys separate — see dovetail VERIFY below |
| hinge_rod | 303 stainless bar, lathe | not printed — see "Hinge" in the change notes for the lathe callouts |

### Drill-out / bench ops after printing (new in v0.6)

- **Hinge bore.** Modeled finished at Ø4.2 (`HINGE_BORE`), but FDM print holes come out
  undersized and drooped — don't trust the as-printed bore. **Drill Ø4.2 straight through
  the body and door with the two shells closed and clamped together** (i.e. after the
  liner/closure dry-fit, not before): this crosses 8 interrupted knuckle segments, each
  ≤14 mm long (L:D ≤3.5), so it's a series of short through-holes, not deep-hole drilling
  — the printed pilot self-centers the bit. Blow out swarf before the liner or rod goes in.
- **Plunger channel.** `pin_ch_d` is modeled at `plunger_d + 0.6` = 6.6 mm. Ream to 6.5 mm
  only once the real JF-0530B plunger is measured — VERIFY before committing to the ream.
- **Dovetail groove.** The 60° groove/key pair is orientation-sensitive on FDM (layer
  lines cross the flank at an angle); print and slide-fit a short test length before
  committing a full liner print — see "Suggested first prints" below.
- **Spine cover.** Dry-fit on the r35 rabbet ledge before drilling the 2× M3 pilots — a
  bowed or under-radius print won't seat flush, and the 0.5 mm shadow-gap reveal makes
  any unevenness obvious.
- **Hatch/tray.** `bay_hatch` is now the component tray (nesting pad + zip-anchor grid),
  not just a cover — check the nesting pad registers flush with the remaining bay floor
  before loading components, and leave a lead service loop so removing the tray doesn't
  strain the LiPo/TP4056 wiring.

## VERIFY before printing (measure your actual parts)

- `sol_hole_dx` — mounting-hole spacing of the JF-0530B you receive (clones vary) —
  merged with the pedestal attach holes in v0.5 (D12); confirm before installing the
  M2.5 heat-sets
- `pn532_l/w/t` — your PN532 board (clone boards vary a couple of mm)
- PN532 corner mounting holes — `PN532_HOLE_INSET` (2.54 mm) assumes Elechouse V3
  corner holes at Ø3; clones may lack them, in which case the printed corner clips (same
  drop-bosses) are the fallback
- `button_d` — thread diameter of your wake button (12 mm nominal)
- ST flat-head countersink angle — modeled at 90° (`M3_ST_CS_D`/`M3_ST_CS_T`); confirm
  your self-tap screws are 80° or 90° before cutting countersinks to depth
- M4-short heat-set (Ø5.6×L3, closure) and M3/M2.5 brass insert dimensions — confirm the
  actual insert OD/length you buy against `INS4_D`, `INS3_D`/`INS3_T`, `INS25_D`/`INS25_T`
  before drilling insert pockets
- Plunger diameter — `pin_ch_d` (6.6 mm) is a placeholder for the 6.5 mm reamed channel;
  confirm against the real plunger (see drill-out note above)
- TP4056 slot width — confirm against your board before trusting the D11 bay repack
- Dovetail groove print-orientation test — slide-fit a short liner slice before running
  a full liner print
- Spine cover warp/orientation test — dry-fit flush on the rabbet ledge before drilling
- LiPo edge-stand fit — measure your actual 103450 pouch (`lipo_l/w/t`) against the
  on-edge bay repack (D11) before trusting it packable
- Donor spool: the drum interior is Ø61 × 28.5 (v0.5 slim drum) — check the reel you gut fits, or resize
  `drum_od`/`drum_w` (frame otherwise cut for 34.5 × 51 × 11 / 103450 + margin — measure
  yours against `lipo_*`)

## Known simplifications (TODO after first fit-check print)

1. Closure lip is a single snug hook — the 3 preload detent depths (DESIGN.md §6.4) get
   added once the on-bike fit is measured; `clr` (0.5) needs a fit print.
2. ~~Liner halves rely on friction + adhesive; dovetail keys into the shell come later.~~
   **SOLVED in v0.6:** a full-length 60° dovetail groove per shell half (mid-arc, one
   straight axial pass) with 4× 28 mm TPU keys sliding in from the front, captive both
   ways (blind stop + click-bump) — no adhesive anywhere in the liner retention path.
3. Shim is a plain C-ring approximation of the clip-over design.
4. Lid uses 4 M3 screws. In v0.6 these landed on **real pilots in the body rim for the
   first time** (D3 — v0.5's screws had no working pilots at all, two of them even fell
   inside the PN532 window's 1.2 mm skin) and drive into brass M3 heat-sets, so it's now
   an actual fastened joint rather than a nominal one. It is still externally removable
   on the locked bike — that's now documented as one of four such joints (hatch, spine
   cover, hinge cap, lid), not a uniquely accepted exception; see DESIGN.md §7 for the
   full consequence list and the production mitigation plan (security/one-way heads,
   staking, eventual hidden lid fastening).
5. Spool spring anchoring is not modeled — depends on the donor reel's spring.
6. The bay tunnels are functional but unblended boxes — the v0.6 industrial-design pass
   (bay-brick bottom chamfer, knuckle chamfers, lid inset/reveal, radius family) softened
   the visible skin, but a full cosmetic fairing pass on the bay tunnels still comes
   after fit is proven. The wire-spine rib itself is gone: it's now an open raceway under
   a separate screwed `spine_cover` (see the part table above), not a molded-in band.
7. The plunger nose needs its 45° ramp filed/ground by hand — 10 minutes with a file;
   the cable-head groove width (≥6.5 mm) must match, noted in DESIGN.md §6.4.

## Suggested first prints (cheap fit checks before the big ones)

1. **Liner test ring**: a 30 mm-long slice of the liner on a 30 mm slice of shell — clamp
   it on the actual bike, judge fin grip across a couple of other bikes too.
2. **Latch block only**: cut the latch boss region (X 45–115) using OpenSCAD's
   intersection with a cube — test bore, pin channel, solenoid pedestal, and the bench-mule
   square tang (DESIGN.md §6.4) with the real solenoid before printing full shells.
