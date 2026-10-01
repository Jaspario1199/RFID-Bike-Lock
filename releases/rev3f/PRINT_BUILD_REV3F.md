# VELOX rev 3f — printable prototype, spool deferred

This supersedes the rev 3e **printing and electronics-mounting** instructions. Use the rev 3f STEP/STL set with `cad/cnc_casing_cq.py --profile print`. Do not mix its 2 mm taller A1/A2/window/bushing with rev 3e or the old v0.8.3 lineage. This is a prototype geometry release pending printer calibration and delivered-component fit; it is not a security or machining release.

## What changed

- A real, separate **electronics_cradle** now provides the solenoid's two supports, locating stops, driver-card shelf, Nano locating rails, charger edge guides and elevated boost shelf. Four M2×5 pan-head screws attach it to A1. Purchased-component references no longer contain pretend mounting furniture.
- The reader/battery table is still called **ref_tray**, but it is a printable part. Two M3×6 pan-head screws now attach it to A1; it has battery-strap space and reader-strap slots.
- Eleven **2.5 mm × 0.7 mm retention ties**, with assumed **4×4×3 mm lock heads**, are modeled in the assembly: coil×1, Nano×1, charger×1, battery×2, reader×2, driver×2, boost×2. Use ties long enough for each loop (coil lengthwise loop >83 mm before its lock head, reader perimeter >100 mm): **150 mm minimum length** is the starter specification, or longer trimmed. Measure your actual tie width/thickness/head; these are procurement assumptions.
- A1 has shallow open floor channels for the battery, Nano and charger straps. Its interior is **26 mm high**, 2 mm taller than rev 3e, so the boost shelf and ties have clearance. Nano moves +1.5 mm in Y; driver moves +0.6 mm; boost moves +1.5 mm in Y and rises to z51.7. Latch, coil axis, main floor and hinge remain at their previous positions.
- A2 and A4 have actual **90°** countersinks. The audit measures the conical faces rather than trusting comments. Their screw lengths are **M3×10** and **M3×8**, respectively; the corrected audit uses the top of the seated countersunk head as the length datum. It conservatively reports about **5.2 mm engagement** at 0.25 mm sampling resolution.
- One Nano-side lid boss uses a **2.7 mm radius**, retaining a **1.45 mm collar** around its M3 pilot. The other lid bosses retain 4 mm radius. That local collar is for a light prototype lid joint, not a high-load security claim.
- Print/CNC fit profiles are separate. CNC exports go to `cnc-design/cnc-profile/` by default so they cannot overwrite the print set.

## Print-fit defaults (all tunable after calibration)

| Interface | Print profile | CNC nominal profile |
|---|---:|---:|
| Cap body / tunnel | Ø8 / Ø8.35 | Ø8 / Ø8.10 |
| Cap flange / counterbore | Ø10 / Ø10.35 | Ø10 / Ø10.10 |
| Ø6 plunger / cap bore | Ø6 / Ø6.30 | Ø6 / Ø6.10 |
| Bushing OD / A1 seat | Ø14 / Ø14.30 | Ø14 / Ø14.00 |
| Bushing OD / lid opening | Ø14 / Ø14.50 | Ø14 / Ø14.10 |
| Head / bushing ID | Ø10 / Ø10.30 | Ø10 / Ø10.30 |
| TPU stud / shell hole | Ø4.5 / Ø4.2, intentional interference | same |

Clearances are **diametral**, not per side. CNC profile remains a nominal engineering comparison, not authorization to machine. Printed cap wall at the Ø6.3 bore is 0.85 mm; the prototypes are only for motion/fit testing. Do not force the actual plunger or bushing into a tight print, or drill the cap's Ø8.35 running tunnel with an Ø8 drill and assume it has the required fit.

**Coupons first:**
- `latch_fit_coupon`: notch at the lowest-diameter corner. Four columns, left to right. Near-notch row: 8.15/8.25/8.35/8.45; middle: 6.10/6.20/6.30/6.40; far row: 10.3/10.4/10.5/10.6. These are vertical bores, with the coupon flat on the bed.
- `horizontal_latch_coupon`: base down, X-axis through-bores. Low row: 8.15/8.25/8.35/8.45; high row: 10.15/10.25/10.35/10.45, ordered away from the notched Y end. This reproduces horizontal tunnel orientation. A good vertical fit does not establish horizontal roundness.

## Print scope and orientations

The print package intentionally omits **A3 spool housing, A4 spool cover and the metal hinge pin**. The spool remains a separate unfinished mechanism. The cover's corrected model is retained in the full CAD but is not on today's print list. Other purchased `ref_*` models and assembly STEP files are for inspection, not slicing.

| Part | Bed orientation | Starting support requirement |
|---|---|---|
| A1 top box | pocket UP, saddle DOWN | supports under saddle and carrier attachment geometry as slicer preview requires; keep removable support out of running bores if possible |
| A2 lid | exterior TOP face DOWN | underside recesses face UP; inspect screw-hole first layers |
| A5 insert | flange DOWN | none expected |
| electronics_cradle | assembled FLOOR faces DOWN | supports under elevated shelves/bridge; inspect 0.6 mm front stop and 0.7–0.8 mm rails with chosen nozzle |
| ref_tray | reader DECK DOWN | local support under screw ears; new ears make the old support-free claim obsolete |
| C1/C2 | seam faces DOWN | preview curved bores and side holes |
| closure_block | suitable flat face DOWN | saddle surface may need support; check contact face |
| hinge_block | pin axis vertical is a trial alternative | underside/locating surfaces require slicer review; no guaranteed support-free orientation |
| liner halves | tube axis vertical, brim | TPU studs remain short sideways overhangs; print a fit section before both full liners |
| proto_cable_head | nose DOWN, brim | inspect horizontal cord hole bridge |
| proto_cap | flange DOWN | inspect 6.3 mm blind-bore roof bridge and cross-hole |
| proto_bushing | on end | none expected |
| both latch coupons | base DOWN | do not change orientation of horizontal test bores |

The package includes copies in these suggested orientations, dropped to Z=0. Block orientations are trials that still require your slicer review. No G-code or printer-specific toolpaths have been released. PETG for rigid parts, TPU95A for liners is the starting material choice; temperatures, perimeters and supports will be tuned from your printer settings.

## Hardware

Keep the existing chassis-to-box and clamp-to-block M3×10 countersunk screws. Changes/additions:

| Joint | Hardware |
|---|---|
| A2 → A1 | 4× M3×10, 90° countersunk; assumed head Ø5.5 |
| A4 → A3, **deferred** | 4× M3×8, 90° countersunk |
| Carrier → A1 | 4× M2×5 pan, head envelope Ø4×1.6; Ø2.4 carrier clearance, Ø1.6 A1 pilot; 3 mm nominal engagement |
| Tray → A1 | 2× M3×6 pan, head envelope Ø5.5×2.4; Ø3.4 clearance, Ø2.5 A1 pilot; 4 mm nominal engagement for a light tray |
| Consumer closure | M3×6 **low-head cap** plus Ø7×0.5 washer, on flat bore floor; **not a countersunk screw with a washer** |
| Retention | 11× 2.5×0.7 ties with heads no larger than the modeled 4×4×3 envelope; 150 mm or longer |

In PETG, these pilots are provisional self-tap pilots. Test a spare hole, drive gently and verify retention; the audit checks geometric engagement, not pullout strength. Do not insert heat-set inserts in these holes. Verify your head dimensions and screw lengths before final assembly.

## Electronics mounting sequence

1. Clean A1, carrier and tray. Check tie slots, screw wells, board seats and running bores. Dry-fit all purchased parts before fastening.
2. Thread loose battery/Nano/charger ties into A1's floor grooves. Feed coil, driver and boost ties around their carrier seats, and reader ties through the tray slots. Put reader lock heads **under the deck**, not above the antenna board; other heads go in the modeled free zones.
3. Drop the empty carrier into A1 and attach with four M2×5 screws. Two screw heads sit on the coil-side floor rail; the two rear screws are reached through open wells in the boost-support rail. Install these before the coil/boards.
4. Battery sits directly on A1 at x19.5–69.5, y−7–27, z38. Set its straps snug enough to locate it, **without squeezing the pouch**. Do not place sharp tie heads against the cell. The pouch's actual thickness/protection board/pigtail must match its envelope.
5. Place the tray above the cell and drive two M3×6 screws at (16.2,8) and (16.2,22). Its screw heads and tool paths stay clear of the cell. Reader sits on the deck at z57.5, component side up, wires down through the header slot. Fit reader straps with their heads under the deck, clear of the battery straps. Actual PCB components may need thin foam where a tie contacts them; do not bend the PCB or cover header pads.
6. TP4056 sits on the floor at x117–146, y−5.5–11.8, USB toward +X, guided by the carrier rails. Fit its strap at x128, clear of its −X solder pads and USB receptacle. The battery harness passes beneath the carrier's raised cross-bridge.
7. Nano sits on the floor at x100.5–145.5, y17.5–35.5, USB toward −X. Its central lengthwise strap avoids the modeled side pin/wire zones. **Cut/remove this replaceable strap and lift the lid to reflash over USB**; put a new strap on afterward. Its front strap obstructs the USB plug when retained.
8. Driver card sits at x102.5–142.5, y5.6–16.3, base z45.15. Fit its two straps at x118 and130. Use the **40×10.7×13.6 envelope** from the current CAD; old 42 mm card instructions are obsolete for this packaging.
9. MT3608 sits at x110–146, y18.5–35.5, base z51.7 on the raised shelf, with wires at its X ends. Straps at x122 and135 avoid these end-pad zones. The shelf is supported outside the Nano footprint, with space beneath it for Nano wiring.
10. Assemble the latch cap/front spring and seat the coil on the two real carrier pillars: x110.8–139.4, y−12.75–4.75, z45.65–58.35. The **lengthwise coil tie at y−10.5** stays clear of the plunger/front spring. Stops locate its X ends; verify that tightening the tie does not shift the 2.6 mm stroke setting. Solenoid tab holes have intentionally not been guessed.
11. Dry-fit the lid-mounted buttons/LEDs/buzzer and revised bushing/window. Test scan/unlock on the bench before closing the lid. Check the real nut, wire, tie-head and solder-joint envelopes. Use the repo's current Nano/RC522 layout; an ESP32 or another board needs a different carrier.
12. Test printed head insertion/release repeatedly by hand, then powered, without security loads. Real spring solid height/rate, coil force, wire bends, component heights, screw pullout and printer fits remain physical checks. Nothing here completes the donor spool or its spring anchorage.

## Reproduce

```bash
python cad/cnc_casing_cq.py --profile print --audit
python cad/cnc_casing_cq.py --profile print
python cad/cnc_casing_cq.py --profile cnc --audit
python cad/cnc_casing_cq.py --mounts
python review/rev3f/validate_release.py
```

The full audit checks the complete static assembly, installation hinge sweep at 0/0.5/1…60° including the left TPU liner and every fixed component, frame entry, latch states, wiring envelopes, screw engagement, actual countersink angles, carrier/tray mounting-axis clearance, real support beneath each component and single-solid validity. Interference threshold remains 0.05 mm³. Sampled motion is not a continuous-motion proof. Physical locking strength, spring force and print fidelity are not claimed.

Old rev3e shop drawings and inspection renders are superseded for changed parts. Do not machine from those drawings or from this print-profile release.
