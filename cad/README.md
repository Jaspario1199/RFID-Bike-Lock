# CAD — parametric housing model

`bike_lock.scad` is a parametric [OpenSCAD](https://openscad.org) model of the whole
v1 printed housing, matching DESIGN.md §6. Every dimension from the design doc is a
named variable at the top of the file — change it, press F5, and the geometry updates.

**Status: v0.2 DRAFT** — industrial-design pass done, rendered and visually verified,
but no part has been test-printed yet. Expect to iterate — that's what parametric means.

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

## How to use

1. Install OpenSCAD (free, openscad.org).
2. Open `bike_lock.scad`. The **Customizer** panel (Window → Customizer) exposes `part`:
   - `assembly` — everything together, for visual inspection
   - `shell_right` — the half that carries the top pod, latch boss, solenoid pedestal, and spool drum
   - `shell_left` — the half with the hook tongue and hinge knuckles
   - `lid` — with PN532 pocket, RF window skin, button/LED holes, bore pass-through
   - `liner_right` / `liner_left` — TPU finned half-sleeves
   - `shim` — TPU C-ring for Ø27–32 mm skinny tubes
   - `spool_cover` — drum face plate
3. F6 (full render) → File → Export → STL, one part at a time.

## Print guide

| Part | Material | Notes |
|---|---|---|
| shell halves, lid, spool cover | PETG first / ASA for the outdoor unit | 6 perimeters, 40% gyroid; shells print pod-opening-up with organic supports under the drum |
| liner halves, shim | TPU 95A | 2 perimeters, 15% infill, ~25 mm/s, fins vertical (they print as clean walls) |

## VERIFY before printing (measure your actual parts)

- `sol_hole_dx` — mounting-hole spacing of the JF-0530B you receive (clones vary)
- `pn532_l/w/t` — your PN532 board (clone boards vary a couple of mm)
- `button_d` — thread diameter of your wake button (12 mm nominal)
- `camlock_d` — panel hole of the cam-lock backstop you buy
- Donor spool: the drum interior is Ø89 × 28 — check the reel you gut fits, or resize
  `drum_od`/`drum_w`

## Known v0.2 simplifications (TODO after first fit-check print)

1. Closure lip is a single snug hook — the 3 preload detent depths (DESIGN.md §6.4) get
   added once the on-bike fit is measured.
2. Liner halves rely on friction + adhesive; dovetail keys into the shell come later.
3. Shim is a plain C-ring approximation of the clip-over design.
4. Lid uses 4 exposed corner M3 screws — acceptable on the prototype (they expose the
   electronics, not the frame closure); the steel version needs the front-lip + hidden
   rear fastening.
5. Spool spring anchoring is not modeled — it depends entirely on the donor reel's spring.

## Suggested first prints (cheap fit checks before the big ones)

1. **Liner test ring**: a 30 mm-long slice of the liner on a 30 mm slice of shell — clamp
   it on the actual bike, judge fin grip across a couple of other bikes too.
2. **Latch block only**: cut the latch boss region (X 45–115) using OpenSCAD's
   intersection with a cube — test bore, pin channel, solenoid pedestal, and the bench-mule
   square tang (DESIGN.md §6.4) with the real solenoid before printing full shells.
