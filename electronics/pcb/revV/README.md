# VELOX Rev V — FEDC Voltera V-One prototype

This version is a two-sided printed-ink control carrier for the FEDC V-One. Open `design/VELOX_carrier_V.kicad_pro` in KiCad 9. Copper rivets connect the printed layers: small rivets for vias and large rivets for top-mounted Nano sockets and 2.54 mm headers. Bottom-mounted SMD parts are soldered to ink using the qualified Voltera process. There is no chemical through-hole plating, printed solder mask or printed silkscreen. Assembly markings are provided in the views.

The evaluated single-sided route needed16 insulated wire links, so the selected design uses two printed sides for a cleaner harness. The final layout uses25 small interlayer rivets,50 large header/socket rivets and one short insulated link, JP1 from C5.2 to C4.2. All75 rivets are installed parts, not plated holes. `rivet_map.csv` gives the drilled connection coordinates, net and rivet type; count them when estimating assembly effort.

This is an engineering review prototype, not a qualified bike-use product or a claim that FEDC has accepted the job. Digital results are in `validation.json`. Exact stock rivet fit, solder adhesion, ink resistance/current capability, component ratings, external power assembly and physical enclosure installation remain qualification gates.

## Files

- `previews/`: actual schematic, underside ink layout and annotated assembly/wire map.
- `jumpers.csv` / `jumpers.json`: install every wire, between the named existing solder lands. Cut lengths include slack as a starting estimate; route and trim to the real assembly.
- `pin_map.csv`: carrier connector and Nano pin functions.
- `BOM_review.csv`: onboard parts and remaining part-selection inputs.
- `SYSTEM_WIRING.md`: exact external power/driver architecture, panel/reader wiring, sequence and bench checks.
- `manufacturing_REVIEW_ONLY/`: top/bottom Gerbers, separate outline and 0.7/1.6 mm drill files; no copper-layer text or outlines.
- `FEDC_REVIEW_ONLY.zip`: small manufacturing review bundle for technician consultation, not an automatic service submission.
- `mechanical/`: board fit reference and conservative populated-carrier envelope. External power modules are not located by this envelope.

## FEDC process target

FEDC publishes a V-One with 128 × 116 mm area, 0.2 mm minimum trace/spacing, 0.65 mm IC pitch, 0603 passive minimum and drill sizes 0.7/0.8/0.9/1.0/1.6 mm. This layout targets >=0.35 mm signal traces, >=0.30 mm spacing, wider logic-power traces and 0805 passives. No solid ground fills are printed. Main logic-power traces target0.6mm; SMT escape necks and constrained low-current branches may be0.35mm. The coupon and loaded-rail measurements must qualify the actual process. Small interlayer rivets use0.7mm drill /1.3mm land (stock flange0.9mm); large header rivets use the dimensions below. Through-hole lands use 1.6 mm drill / 2.24 mm pad for large rivets with 1.0 mm bore / 2.2 mm head. This modest flange margin and actual header bore fit must be qualified with the stock rivets; 2.54 mm connector pitch limits widening.

Mounting holes are **1.6 mm pilots**, to match the listed drill set. Fixture and hand-finish them to 3.2 mm for M3 after curing; mount centers match Rev B. Both sides reserve a 6.6 mm diameter hardware-clearance envelope. Do not order the copper-clad milling process for this ink design. Verify a blank insulating FR1/FR4 substrate and the actual ink batch/process with the technician. Use nominal 1.6 mm substrate, subject to rivet length and final thickness qualification.

## Electrical scope

The Nano, reader, buttons, LED resistors, buzzer driver and battery divider are on the carrier. The charger, battery fuse/RUN switch, regulators and coil-power driver remain external; see `SYSTEM_WIRING.md`. This reduces vias and avoids putting the coil's high current through silver ink. It may increase external harness volume; enclosure installation needs a prototype check.

The sheet-resistance value in a datasheet is only a starting estimate. Different cure, ink thickness and temperature change actual performance. The supplied test coupon measures the specific process before committing the carrier. There is no solder mask protection on the prototype: insulating standoffs, wire jackets, strain relief and inspection matter.

## Reproduction

Run `build.py`, `route.py`, `schematic_writer.py`, `sync_board.py`, `finish.py`, then regenerate with `schematic_writer.py` and `sync_board.py` before `validate.py` and `publish.py`. `finish.py` applies the reviewed local ADC-return spacing correction and models JP1 explicitly; do not skip it. Generation/routing use pcbnew 7 and numpy; native checks/exports use KiCad CLI 9. Previews use matplotlib/CairoSVG; mechanical envelopes use CadQuery. Do not run build on the final routed board unless regenerating the full sequence.

## Primary references

- https://fedc.engr.tamu.edu/faq/prototyping-center/pcb-faq/
- https://fedc.engr.tamu.edu/facility/prototyping-center/index/
- https://fedc.engr.tamu.edu/services-home/service-request-form/
- https://docs.voltera.io/docs/v-one/learn-v-one/circuit-design-for-v-one/circuit-design-guidelines
- Nano/Pololu/AO3400A interface sources retained in `interfaces.json`.

## Validation result

Native KiCad9.0.9 checks: zero ERC violations, DRC violations, unconnected items or schematic/PCB parity issues. Independent functional checks cover62 connected pins across21 functional nets, including the installed JP1 bridge. No individual DRC exclusions are used. These are digital checks; they do not establish ink conductivity, solder/rivet reliability or a physically installable final lock assembly.
