# VELOX rev3f with supplied RPS v9 presets

Use the 16 labeled STEP files in this package. Units are mm; suggested orientations are already applied. Print the two latch fit coupons first. Spool parts and the metal hinge pin remain excluded.

## Filament assignment

- All 14 rigid parts and coupons: **RPS Settings - PETG**, inheriting **Creality Generic PETG**.
- Both liners: **RPS Settings - TPU**, inheriting **Creality Generic TPU**. The preset does not specify Shore hardness; verify the intended TPU95A material before accepting the press fit.
- Supplied ASA/PLA presets are preserved but not assigned to these parts.

## What the supplied archive establishes

The profiles list Creality K1, K1 Max, K1C and K2 Plus with 0.4 mm nozzles. This does not establish which machine is being used. PETG and TPU contain no explicit nozzle/bed temperature, flow ratio, retraction, volumetric speed or shrinkage overrides: these must resolve from the named installed base presets. JSON version fields are profile metadata, not confirmation of the installed slicer version.

Import these filament presets into the shop's compatible slicer and confirm each base resolves without warnings. Select the actual machine and process profile. Keep PETG and TPU on separate plates/jobs. Refer to PRINT_BUILD_REV3F.md for part-specific orientation and support requirements. Review support removability, the 0.6 mm stop and 0.7–0.8 mm carrier rails, bore bridges and bed fit in the actual preview. Do not add global hole/XY compensation before printing and measuring the orientation-specific coupons: allowances are already in the CAD.

This package assigns supplied material presets to parts; it does not contain sliced projects or G-code. Exact printer model and slicer/process profile remain needed. No geometry changes were made from these filament-only profiles.
