# Rev B DFM refinement — 2026-10-08

Status: manufacturability review prototype; not an order release. Target is commercially fabricated, two-layer FR4, nominal 1.6 mm thickness, 1 oz copper, green solder mask and manual assembly. Finish is not yet selected. This revision does not qualify a milled single-sided Fab Lab PCB or an automated assembly order.

## Changes

- J6 PH connector copper pads widened to 1.35 × 1.8 mm around the existing 0.75 mm holes: minimum nominal annular ring increases from 0.225 to 0.30 mm.
- Four 6.6 mm diameter copper keepouts on both sides surround M3 mounting holes. Select screw heads/washers within this envelope, allowing hardware tolerance; no conductive hardware may extend beyond it.
- Through-hole ground pads use 0.25 mm-gap, 0.4 mm-spoke, 45-degree thermal reliefs where the existing routing supports them. J6 pin 1 and U4 pin 2 retain solid connections because reliefs were starved on the front layer. Use suitable preheat and soldering technique for those two joints.
- Silkscreen text is at least 1.0 mm high with 0.15 mm strokes; graphical lines are at least 0.15 mm. References were repositioned to avoid pads and graphics. Polarity and connector orientation markings remain. References inside module outlines help placement before installation; use the assembly view after modules cover them.
- Native rules now enforce 0.25 mm PTH nominal annular ring, 0.45 mm pad-hole separation, 0.28 mm hole-to-copper, 0.15 mm silkscreen clearance and 0.09 mm mask-to-unrelated-copper clearance. Existing minimum 0.25 mm tracks, 0.20 mm copper clearance and 0.50 mm copper-to-edge remain.
- Solder mask is nominal 1:1 with a 0.10 mm minimum web setting. A separate conservative pad-opening audit and native solder-mask checks accompany the review exports.

## Manufacturing evidence and limits

Read `validation.json`, native `drc.json` / `erc.json`, and `dfm_report.json` for results tied to source hashes. No individual DRC exclusions are used. Existing noncritical ignored rule categories remain visible in the project configuration; a zero-issue report is not a complete assembly-access test.

`manufacturing_REVIEW_ONLY/` contains copper, solder mask, silkscreen, outline and front paste Gerbers plus separate plated/nonplated Excellon drills and a drill report. Slots use routed Excellon commands. These are for CAM review, not an instruction to manufacture. A paste layer is not a qualified stencil design. Ask the fabricator to review the final files and board specifications before payment.

## Connector and mechanical release decisions

| Interface | Board nominal hole | Manufacturer reference | Required decision |
|---|---:|---:|---|
| J6 JST B8B-PH-K-S | 0.75 mm | 0.70 +0.10/−0 mm | Confirm finished holes and actual header fit; JST advises larger holes for hard fiberglass boards |
| J5 JST B8B-XH-A | 0.95 mm | 0.90 +0.10/−0 mm | Confirm finished holes and pitch with fabricator |
| J4 JST B2B-XH-A | 1.00 mm | 1.00 ±0.05 mm | Confirm finished holes and actual header fit |
| USB shield slots | 0.60 × 1.20 mm | Selected GCT footprint | Confirm plated routed slots accepted in CAM |
| Mounts | 3.20 mm NPTH | M3 clearance proposal | Check actual screws, washers, standoffs and lid access |

JLCPCB lists general through-hole tolerance +0.13/−0.08 mm and hole-position tolerance ±0.075 mm. These are wider than the JST reference hole/pitch ranges; nominal CAD compatibility alone does not guarantee a production fit. Obtain an accepted finished-hole specification or qualify a connector coupon/first article before committing multiple assemblies. Their standard 1.6 mm board tolerance is ±10%; PH reference board thickness is 0.8–1.6 mm, so confirm actual board thickness / pin protrusion with the chosen header and process.

## Hand assembly and inspection

1. Fit and inspect low-profile SMD parts first, including USB, charger, protection IC and MOSFETs; check pin 1, diode cathodes and bridges under magnification.
2. Install connectors, Nano sockets and module headers while both sides remain accessible. Use the actual modules as unpowered alignment fixtures if appropriate; do not trap solder joints beneath permanently installed modules.
3. Install polarized capacitors and modules, inspect solder joints, then verify rails with a current-limited supply before connecting the Nano, reader, battery or coil.
4. Install in the enclosure only after cable insertion/removal, strain relief, tool access and the lid have been physically demonstrated. Existing envelope checks are not physical qualification.

Still open: actual protected-cell/BMS and solenoid ratings/duty, exact ceramic capacitor MPNs and DC-bias performance, fuse coordination, header/socket stack and buzzer selection. Loaded rail/transient/temperature tests and RFID performance remain necessary. Charging is RUN OFF with Nano USB disconnected; no onboard BMS, cell-temperature sensing or concurrent-use charging power path is provided.

## Reproduction

For an already routed Rev B board using the project libraries: run `dfm_refine.py` (pcbnew 7), `validate.py` (pcbnew 7 + KiCad CLI 9), `dfm_audit.py`, then `publish_views.py`. The refinement preserves stored text anchors for repeatable positioning. Full `build.py` regeneration replaces the board/library and must be followed by routing, net synchronization, refinement and all checks. Do not treat a freshly regenerated schematic/board as this validated package without rerunning them.

## Primary references

- JLCPCB capabilities: https://jlcpcb.com/capabilities/pcb-capabilities
- JST PH: https://www.jst-mfg.com/product/pdf/eng/ePH.pdf
- JST XH: https://www.jst-mfg.com/product/pdf/eng/eXH.pdf
- KiCad 9 rule documentation: https://docs.kicad.org/9.0/en/pcbnew/pcbnew.html

Manufacturer capability pages are a review baseline, not acceptance of this order or its special tolerances.
