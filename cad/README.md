# CAD — parametric housing model (v0.3, CadQuery → STEP)

`bike_lock_cq.py` is the source of truth: a parametric [CadQuery](https://cadquery.readthedocs.io)
model that builds true BREP solids and exports **STEP** (SolidWorks-ready) and STL for
every part. Every dimension from DESIGN.md §6 is a named variable at the top of the file.

**Status: v0.5 DRAFT ("spine + door")** — consumer-install architecture: the door is a
light arc panel that verifiably swings clear (0–110°, machine-checked); pod, bay, and
slim Y-axis drum all live on the body's right side; the tube's entry corridor is kept
empty by construction. `python bike_lock_cq.py --sweep` re-runs the kinematic proofs.
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
the lid, spool cover, and end plugs). In a new assembly: Insert Component → pick a file →
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

## v0.5 part set (11 printed parts)

| Part | Role |
|---|---|
| `body` | right clamp + asymmetric pod + latch boss + **wire spine** + pedestal pads + swept closure pockets |
| `door` | light arc panel + closure flange & lip + hinge knuckles — verified to swing clear |
| `bay_module` | right-side brick (LiPo frame, TP4056 slot, USB-C, zip grids) + slim Y-axis drum Ø68×32 + snout; bolts by 4× M4 from inside the bore |
| `bay_hatch` | bottom cover for the brick |
| `pedestal_cart` | solenoid mount on the pad system (VERIFY dims live here) |
| `lid` | window skin, NFC ring, button dish, PN532 pocket (board located by pocket walls + foam tape — posts were unbuildable through the pocket) |
| `liner_right/left`, `shim` | TPU fit system |
| `spool_cover` | outboard (+Y) drum face plate — spool serviceable in place |
| `end_plug` ×2 | glued caps over the blind hinge-pin channels |

The pedestal still uses the standardized flat-pad system (12 mm pads, tops at z=32).

Assembly-audit fixes implemented (ASSEMBLY.md §3): **plunger-as-pin** (Ø6.6 channel, no
separate pin/spring/coupling), **two blind ~55 mm hinge pins** inserted from the end
faces behind glued plugs (no exposed pin ends), card-edge board pockets, and all-M3
self-tap standardization (the M4 closure insert is the only heat-set left).

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
| shell_right | PETG first / ASA outdoors | pod-opening up; light support under belt + spine rib |
| shell_left | PETG / ASA | split-face down, near-zero support |
| bay_module | PETG / ASA | hatch-faces down; supports under the drum ring arc only |
| bay_hatch ×2 | PETG / ASA | flat, no support |
| lid | PETG / ASA | top-face down on a smooth sheet (window skin + NFC ring print first) |
| pedestal_cart, end plugs | PETG | flat side down, minutes each |
| liner halves, shim | TPU 95A | 2 perimeters, 15% infill, ~25 mm/s, fins vertical |

## VERIFY before printing (measure your actual parts)

- `sol_hole_dx` — mounting-hole spacing of the JF-0530B you receive (clones vary)
- `pn532_l/w/t` — your PN532 board (clone boards vary a couple of mm)
- `button_d` — thread diameter of your wake button (12 mm nominal)
- `camlock_d` — panel hole of the cam-lock backstop you buy
- Donor spool: the drum interior is Ø89 × 28 — check the reel you gut fits, or resize
  `drum_od`/`drum_w`
- LiPo: frame is cut for 34.5 × 51 × 11 (103450 + margin) — measure yours (`lipo_*`)

## Known v0.2 simplifications (TODO after first fit-check print)

1. Closure lip is a single snug hook — the 3 preload detent depths (DESIGN.md §6.4) get
   added once the on-bike fit is measured; `clr` (0.5) needs a fit print.
2. Liner halves rely on friction + adhesive; dovetail keys into the shell come later.
3. Shim is a plain C-ring approximation of the clip-over design.
4. Lid uses 4 exposed corner M3 screws — acceptable on the prototype; steel version needs
   hidden lid fastening (see ASSEMBLY.md §4 for the concrete reason).
5. Spool spring anchoring is not modeled — depends on the donor reel's spring.
6. The bay tunnels and wire-spine rib are functional but unblended boxes/bands — a
   cosmetic fairing pass comes after fit is proven (same trade as v0.3 made).
7. The plunger nose needs its 45° ramp filed/ground by hand — 10 minutes with a file;
   the cable-head groove width (≥6.5 mm) must match, noted in DESIGN.md §6.4.

## Suggested first prints (cheap fit checks before the big ones)

1. **Liner test ring**: a 30 mm-long slice of the liner on a 30 mm slice of shell — clamp
   it on the actual bike, judge fin grip across a couple of other bikes too.
2. **Latch block only**: cut the latch boss region (X 45–115) using OpenSCAD's
   intersection with a cube — test bore, pin channel, solenoid pedestal, and the bench-mule
   square tang (DESIGN.md §6.4) with the real solenoid before printing full shells.
