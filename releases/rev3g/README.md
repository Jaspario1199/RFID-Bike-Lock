# VELOX rev3g — assembly-access prototype

**Print the small solenoid/latch fit section first. Full housing files are a prototype candidate pending that physical fit test.** Rev3f's solenoid envelope did not represent the unmodified purchased unit. Do not reuse its cap, carrier or top enclosure for this layout.

## Layout change

The solenoid now sits on the opposite side of the receiver, points toward +X, and is rolled 90 degrees around its shaft so its 14 mm body dimension lies across the box and its 17 mm dimension is vertical. The original latch/closure axis remains at (90,-4), and its height remains 52 mm. The complete factory spring, rear shaft and nut are retained.

The upper housing footprint grows from 140×57 to **170×111 mm**. Its floor remains at z38; the lid underside is z70 instead of z64. The original frame attachment locations and lower saddle are retained, with the closure-block pocket reopened through the new floor. This is deliberately a spacious bench prototype; compactness and outdoor sealing are not yet validated.

Battery, reader, Nano, driver, booster and charger now have individual removable trays. The reader remains elevated near the lid, but does not sit over another component. The lid has a thin integral RF region instead of a separate A5 insert. Buttons move to the clear central strip. The charger has an end-wall port/recess, and a central 3×3 mm harness corridor is reserved. The Nano USB service envelope is checked with the lid removed.

The latch guide and upper receiver form one removable cover. Removing that cover and the bushing opens the shaft channel from above; the solenoid, spring seat and adapter can be lowered as a unit. No spring seat must be threaded through an undersized closed guide.

## Hardware geometry and remaining estimates

| Item | Value and source |
|---|---|
| Solenoid frame | 30×17×14 mm, supplied product drawing |
| Front shaft | Ø6.5 mm, drawing |
| Factory travel | 10 mm, drawing |
| Extended front projection | 30 mm, derived from the illustrated 60 mm span minus 30 mm body |
| Retracted front projection | 20 mm, derived using 10 mm travel |
| Rear projection at rest | 9.525 mm, owner's 6/16 inch measurement |
| Rear projection retracted | 19.525 mm, derived |
| Spring-seat OD | 11.1125 mm, owner's 7/16 inch measurement |
| Shared guide/seat passage | Ø12.5 mm; 0.694 mm radial clearance around the measured seat |
| Prototype adapter | Ø11.8 guide sleeve with Ø8 nose, Ø6.9 shaft socket |
| Spring envelope OD | **11.5 mm estimate**, conservative relative to the image, not a measured spring diameter |
| Seat location | **21 mm ahead of coil face at rest, 1 mm thick estimate** |
| Fork cross-pin center | **3.5 mm behind shaft tip estimate**; Ø3.2 printed cross-hole for nominal Ø3 pin |
| Rear hardware diameter | Ø6.5 mm drawing envelope; verify widest actual nut/washer |

The estimated seat/pin positions are why the small fixture is mandatory before the full housing. The supplied mounting-hole diagram does not give sufficient edge offsets; this version uses accessible ties around the metal frame instead of guessed threaded-hole positions. Spring force, coil force at full stroke, return under friction, latch self-camming, electrical function and lock strength remain bench tests.

## First print

In `01_FIT_TEST_FIRST`, print:

1. `solenoid_latch_fit_section_rev3g` — a 102×31 mm section of the actual floor/wall/receiver layout, with the same rear clearance and mounting datums.
2. `solenoid_carrier_rev3g`.
3. `latch_guide_cover_rev3g`.
4. `prototype_latch_adapter_rev3g`.
5. `prototype_bushing_rev3g`.

STEP and STL copies are bed-oriented. The guide cover is inverted for printing; inspect its split-bore roof and other overhangs in Orca. The adapter is on end. PETG and the supplied RPS material preset remain the prototype baseline; no new slicing or G-code is included.

Secure the unmodified solenoid on its carrier on the bench, using the two slots for 2.5×0.7 mm ties. Keep heads in accessible free space, away from the shaft and coil leads. Slide the adapter over the fork and check cross-hole alignment before installing its removable pin; do not force a pin into misaligned holes. Lower the carrier into the fixture. Install the guide cover, then drop the bushing in from above. Move the shaft manually through the entire 10 mm stroke: the spring seat, spring and rear nut must not rub the walls, and the adapter must remain guided. Verify both locked engagement and full release with the existing prototype cable head. If the real spring/seat/pin differs, update those explicit parameters before a full reprint.

## Assembly and service sequence

1. Attach the empty A1 box to the chassis using its retained inside-out frame fasteners, before fitting liners. The spool/hinge support remains deferred as in rev3f.
2. Prepare each tray outside the enclosure: thread ties through the slots and underside channels, fit protective insulation where needed, and attach its component. Keep ties clear of PCB components, headers and the battery pouch's vulnerable edges; do not compress the cell. Wiring and tie heads are not fully detailed solid models.
3. Lower and fasten battery, reader, Nano, driver, booster and charger trays vertically in that order. Mount the charger before threading its external plug. Board references retain rev3f envelope assumptions and need a hardware dry fit.
4. Prepare the solenoid, ties and adapter pin outside the box, then lower the complete unit with its carrier through the open top. Fasten its two exposed ears.
5. Fit the removable guide cover from above, then insert the mouth bushing. Check the full stroke by hand with power disconnected.
6. Route wiring through the central reserved corridor and leave service slack. Keep solenoid leads out of the moving shaft envelope. Attach lid controls and their nuts with the lid on the bench, plug in their harness, then lower the lid.
7. For removal, lift and disconnect the lid, remove the bushing and guide cover, disconnect solenoid leads, and lift the carrier out. No shaft/spring cutting is required.

Tray and solenoid attachments use M2×5 pan screws into Ø1.6 provisional PETG pilots, with nominal 3 mm floor engagement. The raised reader tray needs **M2×22** under-head length for the same engagement (verify availability/length before printing the full set). Guide cover: M2×14 pan, approximately 5 mm engagement. Lid: four M3×10, 90-degree countersunk. Verify actual screw-head envelopes; light prototype joints need physical retention testing. Mounting screws are accessed before wiring is laid across them.

## Validation scope

`validation.json` records valid single solids, static interference, the full 0–10 mm solenoid stroke at 1 mm increments, vertical installation paths at 1 mm increments from 70 mm above, a 5 mm driver envelope, lid installation including button nut envelopes, reserved harness/USB clearances, and the existing C2 installation hinge sweep at 0/0.5/1…60 degrees. Interference threshold is 0.05 mm³. Intentional overlap of the simplified plunger with its coil reference is excluded. Sampled paths do not prove continuous clearance, and small modeled parts/hardware variation remain physical checks.

Exports are separately checked by STEP re-import and STL watertightness. The full assembly STEP is for inspection only and includes purchased-part envelopes, not printable copies of the electronics. The source snapshot is self-contained: install CadQuery, then run `python source/redesign.py --audit` or run it without flags to export assembly-coordinate models. The frozen original source is imported only to retain the chassis saddle/attachment geometry and existing hinge components.
