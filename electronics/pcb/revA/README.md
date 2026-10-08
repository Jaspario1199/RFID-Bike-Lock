# VELOX carrier PCB, Rev A

**ENGINEERING REVIEW PROTOTYPE. NOT RELEASED FOR FABRICATION OR INSTALLATION.**

This is a native KiCad schematic and routed two-layer carrier-board proposal for the
**Arduino Nano ESP32 ABX00083 and RC522** in `firmware/README.md`. It is not the older
classic Nano/PN532 system in the root BOM. It does not replace the solenoid clearance work.

## What this board does

The board replaces the loose inter-module wiring and driver perfboard with copper traces,
two Nano sockets, a discrete solenoid driver, a buzzer driver, LED resistors, battery sensing,
and labeled connectors. Existing charger and boost modules sit on insulated mounting areas
and connect using short wires. Their drawn interfaces are **carrier wire pads**, not guessed
clone-module solder footprints. Battery, solenoid, RFID reader, and panel controls remain
external and plug/wire into the board. Module mounting clips are not yet designed.

Proposed size: **110 x 65 x 1.6 mm**. Four 3.2 mm non-plated mounting holes at
(4,4), (106,4), (4,61), (106,61), measured from the upper-left board corner in the top view.
This is a first learning/prototyping layout, not a claim that this is the minimum footprint.
No enclosure, lid, antenna, wiring-bend, or insertion-clearance approval is implied.

## Open it

Install KiCad 7 or newer and open `design/VELOX_carrier_A.kicad_pro`.
The schematic is `.kicad_sch`; the routed board is `.kicad_pcb`.
Project-local footprints and symbols are included; embedded schematic symbols also open
without a global symbol library. Do not replace U1 with a classic Nano: B0/B1 and VBUS differ.

`previews/schematic.png` is the complete electrical schematic. Matching net names mean
connected wires, even when no long line is drawn across the sheet. The N-MOS blocks explicitly
show gate/source/drain pin numbers. `previews/layout_map.png` explains the physical arrangement.
`previews/pcb_top.png` and `pcb_bottom.png` show actual routed copper, not an artist's mockup.

## Power architecture and operating restriction

1. Protected 1S Li-ion battery -> J1 -> U2 B+/B-.
2. U2 OUT+ -> F1 -> external RUN switch (J11) -> U3 IN+ and battery-sense divider.
3. U2 OUT- is system GND. **Do not connect CELL_N/B- directly to system GND**, since doing
   so can bypass the module's low-side protection switching. The exact module must be verified.
4. U3 boost output -> COIL_6V -> Nano VIN and solenoid positive.
5. Nano 3V3 -> RC522 and an externally mounted 3.3 V active buzzer.
6. Nano D5 -> 100 ohm -> Q1 gate. Q1 switches coil negative to GND. R2 holds the gate off
   during reset; D1 cathode/band connects to the positive coil rail to absorb inductive energy.
7. D6 controls Q2 for the buzzer. The buzzer current does not flow through the Nano GPIO.

**Charge only with the RUN switch OFF and the Nano programming USB disconnected.**
This design does not implement load sharing, concurrent-use charging, or USB-powered emergency
unlock. The TP4056 is a charger, not a complete system power-path controller. If concurrent
charging/operation is required, revise this block before ordering.

The schematic preserves the bench hardware's assumed **6 V, about 1 A** coil, but that is
not a verified measurement. The legacy BOM's 300 mA is inconsistent. The boost target is
6.0 V; Arduino specifies Nano ESP32 VIN >=6 V, so loaded output droop has no nominal margin.
Do not raise the shared rail above the coil rating just to make VIN pass. If either condition
fails, revise to separate controller/coil rails or a different qualified power architecture.

At 6 V x 1 A, the coil alone requires about **2.35 A from a 3.0 V cell at an assumed 85%
conversion efficiency**: 6/(3*.85). Controller current is additional. A module advertised as
"2 A" does not establish 2 A output capability at this conversion ratio. Test cell, protection,
switch, boost, wiring and connectors together. A 1000 uF capacitor cannot provide a 300 ms
unlock pulse; it only helps brief transients. F1's provisional 3 A value is not finalized.

## Connector map (carrier pin numbering)

| Ref | Connection | Pin assignment |
|---|---|---|
| J1 | Protected 1S battery pigtail | 1 CELL+, 2 CELL-; independently check battery polarity |
| U2 | Four wires to protected TP4056 | 1 B+, 2 B-, 3 OUT+, 4 OUT- |
| U3 | Four wires to MT3608 | 1 IN+, 2 IN-, 3 OUT+, 4 OUT- |
| J11 | External latching RUN switch | 1 fused battery, 2 switched battery; open = OFF |
| J4 | Solenoid | 1 positive, 2 switched negative |
| J5 | RC522 custom 8-wire harness | 1 SS, 2 SCK, 3 MOSI, 4 MISO, 5 unused, 6 GND, 7 RST, 8 3V3 |
| J6 | Green wake button | 1 D3, 2 GND; normally open |
| J7 | Red cancel/admin button | 1 D2, 2 GND; normally open |
| J8 | Red LED | 1 anode via 220 ohm, 2 cathode/GND |
| J9 | Green LED | 1 anode via 220 ohm, 2 cathode/GND |
| J10 | 3.3 V active buzzer | 1 positive, 2 transistor-switched negative |

J4-J10 use JST XH **2.50 mm** footprints, not generic 2.54 mm headers or JST PH.
The intended 2-pin header is B2B-XH-A and 8-pin header B8B-XH-A. Use matching housings,
terminals and suitable wire. Identical two-pin housings can be swapped accidentally: label
both cable ends, and consider mechanically distinct connectors before product release.
The board's J5 order follows a common RC522 order, but map each wire to the actual reader's
silkscreen. Do not assume a straight-through harness without checking.

## Firmware

Use `firmware/rfid_bike_lock_esp32/`, with Arduino Nano ESP32 selected. The GPIO assignments
match the repo. `READER_POWER_GATED=0` is required: this revision leaves the reader powered
and D7 unused. `DEV_NO_SLEEP=1` is useful on the bench; battery-current tests require reviewing
the sleep configuration. Measure standby consumption; this PCB does not promise longer
battery life. Calibrate battery sensing against a meter; the simple 3.3/4095 ADC calculation
in the existing firmware is not a calibrated ESP32 ADC transfer function.

## What has been checked

- KiCad loads the schematic and board; native netlist export succeeds.
- All 92 intentionally connected pins match the intended schematic and PCB net map.
- KiCad geometric DRC: 0 violations, 0 unconnected pads, 0 footprint errors at the recorded
  settings (0.20 mm copper clearance, 0.25 mm minimum track, 0.50 mm copper-to-edge).
- Two copper layers, 0.25 mm signal tracks, 0.8 mm main power routing, 0.6 mm coil-return
  routing, 0.9/0.45 mm vias, ground pours, preliminary Nano antenna copper keepout.

These checks do **not** establish thermal/current capacity, RF range, charging safety,
solenoid release timing, firmware correctness, or installation fit. Power routing and solid
ground pad connections still need current/thermal and hand-solderability review. Full KiCad
ERC has not run: installed KiCad 7 CLI provides netlist export but no ERC command. Run ERC in
the GUI and resolve power-driver declarations properly; do not suppress unexplained errors.

## Required before fabrication

1. Verify Nano identity and header geometry, exact coil marking/resistance/current/duty,
   battery data and protection discharge rating, TP4056 module/charge-current setting,
   and MT3608 loaded capacity over the intended battery range.
2. Choose exact fuse and capacitor part numbers and confirm the buzzer is rated for 3.3 V.
   The capacitor footprint is D10 mm/P5 mm; reserved height limit is 20 mm. Do not order a
   different case without updating it. AO3400A is specified at 2.5 V gate drive; do not
   substitute based only on threshold voltage or an advertised amp rating.
3. Design insulated module retention and board standoffs, check the 3D assembly/insertion,
   Nano USB access, mating connector heights, wire bending and lid-mounted controls.
   Keep the remote RFID antenna away from carrier copper, battery and metal; test range.
4. Perform ERC, current/thermal review, manufacturer-specific DFM, then export Gerbers and
   plated/non-plated drill files. Fabrication outputs are deliberately not included in this
   review package to avoid mistaking this for an approved manufacturing release.
5. Bench-test a prototype: continuity and polarity, current-limited power, rails, Nano,
   RC522/buttons/LEDs, transistor driver with dummy load, actual coil and rail droop,
   release timing, temperatures, charging with RUN off, and standby current.

## Equipment

No PCB fabrication machine is necessary for this workflow. Use KiCad and a board fabricator
for plated-through-hole two-layer PCBs. For assembly: temperature-controlled soldering iron,
fine solder, flux, tweezers, magnification, solder wick, fume extraction, and a multimeter.
A current-limited bench supply is strongly useful for bring-up. The 0805/SOT-23/SMA parts can
be hand-soldered; a reflow oven is optional. An oscilloscope helps capture coil-switching
transients and brief supply dips that a multimeter can miss.

If making the bare board yourself is the learning goal, use a precision PCB CNC mill with
appropriate tooling, workholding and dust management. Home-milled two-sided boards generally
lack plated holes: vias need manual connections and top-layer socket joints can be inaccessible.
**This routed revision is designed for a board house, not directly for milling.** It needs a
separate routing/DFM revision for the chosen mill. Your K1 can print mechanical fit models and
fixtures, but not the copper circuit of this PCB.

## Sources and known repo corrections

- Arduino ABX00083 manual/pinout: https://docs.arduino.cc/resources/datasheets/ABX00083-datasheet.pdf
  and https://docs.arduino.cc/resources/pinouts/ABX00083-full-pinout.pdf
  (3.3 V logic, VIN 6-21 V, MP2322 regulator; no classic-Nano AMS1117 explanation).
- AOS AO3400A: https://www.aosmd.com/res/data_sheets/AO3400A.pdf
- JST XH: https://www.jst-mfg.com/product/pdf/eng/eXH.pdf
- MFRC522: https://www.nxp.com/docs/en/data-sheet/MFRC522.pdf
- KiCad fabrication workflow: https://docs.kicad.org/8.0/en/getting_started_in_kicad/getting_started_in_kicad.html
- Home milling limitations: https://support.bantamtools.com/hc/en-us/articles/115001658814-Double-Sided-Boards

Existing `BOM.md`, `WIRING.md` and parts of `BENCH_BUILD.md` contain obsolete classic Nano,
300 mA coil, regulator and firmware assumptions. They are evidence, not authoritative
instructions for this PCB; this work does not silently rewrite those historical guides.

## Regenerate

Python 3.12 with KiCad 7 `pcbnew`, numpy and cairosvg:
`python build.py`, then `python route.py`, export the schematic netlist using
`kicad-cli sch export netlist --format kicadxml`, then `python validate.py`.
`publish_views.py` generates the preview and documentation tables. Read validation reports
after regenerating: edits can change route completion and clearances.
