# HANDOFF — RFID Bike Lock project

Context document for an agent taking over this project. State is current through
**CAD v0.6, all pushed to `main`** of `Jaspario1199/RFID-Bike-Lock`. Read this, then
skim DESIGN.md → ASSEMBLY.md → cad/README.md in that order.

## 1. What this project is

A consumer product being developed by Jasper (owner, TAMU student, iPhone user, has
SolidWorks + a TPU-capable 3D printer): a **frame-mounted RFID bike lock**. A clamshell
clamps permanently around the bike's down tube over a compressible TPU finned liner. A
retractable steel cable (spring spool) locks into a latch; tapping an NFC fob/sticker
fires a solenoid that releases it.

**Product vision (owner's words, load-bearing):** the customer receives a fully
assembled product and installs it by opening the hinged door, closing it around the
down tube, and driving ONE hidden screw. No other consumer assembly, ever. The
manufacturer (Jasper, at first) bench-builds everything else.

## 2. Locked-in design decisions (do not relitigate without cause)

- **Reader:** PN532 (I2C) — only hobby module that could ever talk to phones. Owner has
  an iPhone → phones can't be keys (Apple gates card emulation behind commercial
  agreements; researched and settled). Permanent keys: **MIFARE fobs + NTAG213 sticker
  on the phone case.** No companion app on the roadmap.
- **MCU/power:** Arduino Nano; PN532 hard power-gated by P-MOSFET (D7), wake button
  (D3) opens a 10 s scan window; MT3608 5 V rail; TP4056 (protected, USB-C) charging;
  **103450 LiPo pouch 2000 mAh** (an 18650 stopped packaging at v0.4). ~3.5–4 weeks per
  charge; upgrade path = 3.3 V Pro Mini (~6–12 months).
- **Solenoid:** JF-0530B **6 V** coil run at the 5 V rail (~250 mA pulse). **Plunger-as-pin:**
  the solenoid's own Ø6 plunger IS the locking pin (45° ramp filed on its nose, Ø6.6
  channel, its built-in return spring gives locking preload). No separate pin parts.
- **Latch:** cable's hardened mushroom head, round with a **square-flanked ring groove**
  (trade study vs the owner's original square tang: rotation-free insertion won; the
  square tang remains the recommended hand-tools bench mule). Insert-to-lock needs no
  power; unlock = 300 ms pulse.
- **Closure/security:** ONE M4×8 low-profile socket screw, driven from the pad top with
  the door open, into a short brass heat-set (Ø5.6×L3) in a low pad on the door's
  closure flange (y6.5–13, z21.8–25.2) — covered by the locked cable head, so the
  housing can't be opened while locked. v0.6 fixed the path itself: v0.5's clearance
  hole ran through the wrong segment and a 1.3 mm solid floor blocked the screw from
  ever reaching the insert (D1), and the insert pocket had already punched through the
  flange (D2) — neither defect was survivable. Fail-secure on dead battery; **USB-C
  port doubles as the power-bank emergency unlock** (wire the system rail from TP4056
  OUT, not the cell). Cam-lock backstop was deleted at v0.4 (no wall for it).
- **Firmware:** complete and committed (`firmware/`) — sleep/wake, scan window,
  EEPROM tag list, master enrollment, admin add/remove, battery check. Not yet run on
  hardware (parts NOT ordered yet — that's the standing critical path).
- **Fasteners:** M3 self-tap (2.5 pilot) is the default — spool cover, spine cover,
  hinge cap, pedestal pads. Two service joints (lid ×4, hatch ×2) upgraded to M3
  machine screws into brass heat-sets in v0.6 so they're real fastened joints, not
  nominal ones (D3/D6). Plus: one M4×8 low-profile socket into a short M4 heat-set
  (closure), 4× M4 pan self-tap (bay module, now sub-flush — D5), 2× M2.5 machine into
  brass heat-sets (solenoid, cyclic load), 4× M2.5 NYLON self-tap (PN532, RF keep-out).
  No pins: the hinge is a single Ø4×~152 stainless rod (integral turned head) with a
  screwed tail cap, replacing the old two blind Ø3 hinge pins and their glued end plugs.

## 3. v0.5 architecture ("spine + door") — WHY it is this way

v0.1–v0.4 all had a fatal flaw discovered late: **they could not be installed** — fixed
material blocked the tube's entry path and the door's swing. v0.5 is governed by three
kinematic rules, and **the CAD verifies them mechanically on demand**:

1. **Entry corridor** (±23.5 mm slab left of the seam at axis height) contains no fixed
   material. Hence the pod is asymmetric (left wall at y −17, fringe floating 0.6 mm
   above the closed door — relieved by a FLAT plane at z 31.6, not a cylinder, because
   the door's edge rises radially as it swings about the offset hinge).
2. **Door swing**: the `door` is a light arc panel (its TPU liner half + closure
   flange/lip + knuckles). Pod, bay, drum are all right of y ≈ +7. The door's flange
   and lip engage the body through **analytically swept sector pockets** (exact annular-
   sector prisms — NOT unions of rotated copies, which segfault OCC).
3. **Slim drum**: spool axis along Y — Ø68 × 32 wheel at the lower right; cable 1.2 m ×
   Ø4; lock bottom at ≈ −94 (was −121); spool cover on the outboard face, serviceable.

Latch line (bore/boss/pedestal) sits at **y +10** — on the body's side — because the
pod's left floor IS the closed door; nothing may stand on it.

## 4. The toolchain (this is the crown jewel — keep it)

- **Source of truth:** `cad/bike_lock_cq.py` (CadQuery 2.8, Python, `pip install cadquery`).
  Every dimension is a named parameter. Coordinate frame: X along the tube (0–150),
  Z up, tube axis at origin; hinge axis at (y 0, z −33) along X.
- `python bike_lock_cq.py` → exports every part as **STEP (SolidWorks) + STL** into
  `cad/step/`, `cad/stl/`. The exporter **refuses multi-body parts** (fuses or dies loud).
- **Automated verifications — run them after ANY geometry change:**
  - entry-corridor interference (in `verify()`),
  - `--sweep`: door + `liner_left` rotated 0–110° vs everything else, asserts 0 overlap
    (v0.6 widened the moving/fixed split from door-vs-body+bay+lid — that gap is what
    hid D10, a real gouge through the liner's base ring),
  - `--matrix`: full pairwise static interference over all placed parts, clash floor
    tightened to **0.01 mm³** (`--strict` drops it to 0.001 mm³),
  - `--gaps` (v0.6, new): exact min-distance check per pair against spec bands, a
    `CONTACT_OK` whitelist for intended clamped contact, and feature probes for fits a
    whole-pair distance can't isolate (knuckle axial float, hinge-rod running bore).
  All currently **PASS at 0.00 mm³ / 0 pairs / 0 gap violations**. The `placements()`
  table is the single source for `--matrix`, `--gaps`, `step/placed/`, and both
  assembly STEPs — keep it that way.
- **SolidWorks workflow (owner's preference):** owner opens STEPs directly. His SW
  chokes on multi-body/assembly STEP display (viewport blank, cause unresolved), so the
  reliable path is `step/placed/01..12_*.step` — every part pre-positioned, inserted at
  the assembly origin one by one (README documents it). Regenerate placed/combined/
  assembly files after every export with `python bike_lock_cq.py --export-assembly`
  (v0.6: a real CLI mode now, no longer an ad-hoc script pattern).
- **Renders:** OpenSCAD (installed via apt) composites `stl/` via `cad/render_v05.scad`
  (closed / open / exploded) → `cad/renders/`. The owner is shown renders after every
  significant change (send as files). Visual inspection of renders has caught real bugs.

## 5. Hard-won pitfalls (cost real time — don't rediscover)

- OCC **segfaults** on degenerate/tangent booleans: fixed once by 0.1 mm position nudges
  (`bay_screw_*`), once by replacing rotated-copy sweep unions with analytic sector
  prisms. If STEP export dies silently or segfaults: bisect features in a subprocess.
- `Workplane.intersect` **raises ValueError on empty intersection** — use
  `overlap_volume()` helper, never raw intersect for checks.
- CQ `Sketch` fins fused only after **embedding roots into the base ring**; the
  `largest_solid()` filter drops seam-sliver orphans. Exporter guards against multi-body.
- "XZ" workplane `extrude(-d)` goes **+Y**. Probe extrude directions when unsure.
- Don't name scratch scripts after stdlib modules (`bisect.py` shadowed stdlib).
- OpenSCAD `--camera=tx,ty,tz,rx,ry,rz,dist` + `--autocenter --viewall` for unknown framing.
- Loft with negative draft **grows** the top face — clearance calcs must use the grown plan.

## 6. Working style the owner expects

- Honest engineering: state caveats plainly, flag unproven geometry as DRAFT, keep
  VERIFY-dimension lists (solenoid hole spacing, PN532 board, button thread, LiPo size,
  donor reel — all still unmeasured, parts unordered).
- When he reports a defect, find the ROOT cause and check for siblings (the pairwise
  matrix exists because one reported clash turned out to be seven).
- When he asks for "minimal fixes," touch the fewest parts possible.
- Ship every change: commit with substantive messages, push to `main`, send renders.
- Version discipline: architecture pivots get archived (`cad/archive/v0.3/`, `v0.4/`)
  before rebuilding; he explicitly asked that old versions never be deleted.
- He works in SolidWorks and checks the assembly himself — expect sharp follow-ups.

## 7. Repo map

| Path | Content |
|---|---|
| `DESIGN.md` | Full engineering doc; §6.6 = v0.5 architecture; §8 fail-safe decision |
| `ASSEMBLY.md` | Build sequence + DFA audit; §7 = v0.5 delta |
| `BOM.md` | Parts + verified dimensions + prices (LiPo swap noted) |
| `firmware/` | Complete Nano sketch + bench bring-up guide |
| `cad/bike_lock_cq.py` | Parametric model + all verification modes |
| `cad/step/`, `cad/stl/` | Current exports; `step/placed/` = pre-positioned set |
| `cad/renders/` | closed / open / exploded previews |
| `cad/archive/` | v0.3 and v0.4 complete snapshots |
| `cad/legacy_bike_lock_v02.scad` | retired OpenSCAD v0.2 |

## 8. Standing next steps (as of handoff)

1. **Order the electronics** (BOM 1–16 with the LiPo) + donor retractable reel — the
   whole physical track is blocked on this; firmware and bring-up guide are waiting.
2. Measure the VERIFY dimensions when parts arrive → update parameters → reprint the
   small cartridges (that's why they're separate parts).
3. First prints: liner test ring + latch region before any big shell.
4. Known cosmetic debt: the bay brick is still an unblended box pending a fairing pass
   after fit is proven (the wire-spine rib itself is gone in v0.6 — it's now an open
   lay-in raceway closed by a screwed `spine_cover`, not a molded rib); closure
   `clr = 0.5` needs a fit print to tune. v0.6 also repacked the bay (D11: the LiPo
   and TP4056 block used to occupy the same floor and the cell physically could not
   fit) — LiPo now stands on edge along the +Y wall; re-check the fit once the real
   cell is in hand.
5. Steel (Phase 2) and hidden-lid-fastening remain future items (ASSEMBLY.md §4).
