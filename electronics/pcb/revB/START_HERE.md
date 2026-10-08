# VELOX Rev B

Open `design/VELOX_carrier_B.kicad_pro` in KiCad 9. The schematic and routed
90 × 55 mm board are editable and use the included project libraries.

| File | Use |
|---|---|
| `previews/layout_map.png` | Locate the controller, regulators and connectors |
| `previews/power_map.png` | Understand power flow |
| `previews/schematic.png` / `VELOX_carrier_B.svg` | Read the complete circuit; SVG remains sharp when zoomed |
| `previews/pcb_top.png`, `pcb_bottom.png` | Inspect actual copper routing |
| `pin_map.csv` | Wire the reader, panel, battery and coil |
| `BOM_review.csv` | Review component choices and open part selections |
| `validation.json`, `erc.json`, `drc.json` | Inspect native electrical/routing checks and source hashes |
| `mechanical/PCB_outline_fit_coupon.step` or `.stl` | Print a nonfunctional board-outline/mounting-hole fit gauge at 100% scale |
| `mechanical/placement_proposal_ENVELOPES_ONLY.step` | Review the proposed populated-board arrangement; do not print this assembly |

Native checks pass: zero ERC violations, DRC violations, unconnected items or
schematic/PCB parity issues. The independent checks cover 126 connected pins,
16 isolated NC pins and the regulator interfaces. The STEP coupon is a valid
single solid; its STL is watertight.

The existing housing needs revised mounts, reader/panel positions and a rear
charging notch open to the rim. Those production housing parts are not included.
The proposal passes the documented envelope/insertion checks, not a physical
assembly test. See `mechanical/placement_report.json`.

Before ordering/energizing: close the actual protected-cell/BMS and coil ratings,
capacitor/fuse/header/buzzer selections, enclosure retention and cable access.
Then perform the bench tests in `README.md`. This package is an engineering
review prototype, not a fabrication or bike-use release. Charging uses RUN OFF
with Nano USB unplugged; the board has no onboard BMS, cell-temperature sensing
or concurrent-use charging power path.
