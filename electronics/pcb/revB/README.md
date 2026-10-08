# VELOX compact carrier Rev B — engineering prototype

**Supersedes Rev A for PCB development. Not released for fabrication, charging,
or bike use.** The native schematic, routed board, connector map, parts list,
and enclosure placement model are provided for review. A clean routing check
does not establish battery safety, coil performance, RFID range or physical fit.

The priority for this revision is compact, tidy packaging with a removable Nano
and practical first-board assembly. The carrier is **90 × 55 × 1.6 mm**, compared
with Rev A's 110 × 65 mm: **30.8% less board area**. It retains the existing Nano
ESP32 firmware pins. It uses two commercially built boost regulators rather than
putting a new high-current switching converter on a first DIY PCB.

## What changed

- Separate 7.5 V Nano VIN and 6 V coil rails. Rev A's shared nominal 6 V rail had
  insufficient tolerance margin against the Nano ESP32's 6 V minimum VIN.
- Onboard USB-C charging replaces the large TP4056 module mounting area. A
  MCP73831 4.2 V charger and NCP361 input protection occupy the lower-left area.
- One keyed PH8 panel harness replaces five separate button/LED/buzzer plugs.
  The RFID harness uses XH8, so these two harnesses cannot be interchanged.
- Two fixed-output Pololu modules use manufacturer-based footprints, replacing
  the unqualified MT3608 clone interface. Both coil output/ground pins are used.
- Exact radial capacitor bodies, an explicit coil return, ground pours, test
  pads, pull-downs and hand-solder footprints are included.
- The enclosure model exposes conflicts with the existing reader tray and
  panel positions. A separate proposed arrangement is included; the current
  printed enclosure is **not** approved for this carrier without changes.

## Electrical architecture

Protected 1S battery -> F1 -> BAT_FUSED. BAT_FUSED feeds the charger battery pin
and the external RUN switch. The closed switch feeds BAT_RUN, which supplies
both boost regulators and the battery-monitor divider.

| Circuit | Implementation | Design limit / unresolved evidence |
|---|---|---|
| Nano supply | Pololu U3V16F7, item 4943, 7.5 V to VIN | Published ±4% range is 7.2–7.8 V. Verify loaded rail over the real battery range. |
| Coil supply | Pololu U3V40F6, item 4013, 6 V | Published ±4% range is 5.76–6.24 V. Actual coil voltage, resistance/current and duty are unknown. |
| Logic/reader | Nano 3V3, RC522 always powered | No reader power switch. D7 is NC; firmware `READER_POWER_GATED=0`. Measure standby consumption. |
| Coil driver | AO3400A, 330 Ω gate, 100 kΩ pull-down, SS34 flyback | Genuine device is characterized at 2.5 V gate drive. Verify drain transient, heating and mechanical release delay. |
| Buzzer | Second AO3400A, SS14, 3.3 V supply | Use a qualified 3.3 V active buzzer ≤30 mA. Do not connect a high-current siren. |
| LEDs | 470 Ω series resistors | About 3.2 mA at a 1.8 V LED drop; tune only after verifying the actual LEDs. |
| Battery ADC | 100k/100k, 100nF, A0 | At 4.2 V, ADC is nominal 2.1 V. Calibrate the ESP32 ADC against a meter. |
| Charging | MCP73831-2ATI/OT, RPROG10 kΩ | Nominal 100 mA, approximate 90–110 mA IC tolerance before resistor tolerance. Cell charge rating and temperature limits must be confirmed. |
| USB input | Separate 5.1k CC pull-downs, NCP361SNT1G | 5 V charge-only USB-C; no data or USB-PD. Check hot-plug overshoot at charger VDD. |

Separate converters reduce direct coil loading of Nano VIN, but both draw from
the same battery. They do not guarantee freedom from brownouts. The coil boost's
enable is tied to BAT_RUN; disabling a boost would not by itself isolate its output.

**Charging procedure:** RUN switch open, Nano USB unplugged, battery within its
manufacturer's charging temperature range. There is no power-path controller,
automatic load-sharing interlock or battery-temperature sensor. Never infer
successful/full charging from the LED alone. At 100 mA a 2000 mAh cell takes at
least 20 hours plus the constant-voltage phase; a faster setting requires a
thermal/charge qualification rather than simply replacing R11.

**Battery protection:** Rev B does not contain the protection circuit previously
available on some TP4056 modules. The cell must have independently verified
overcharge, overdischarge and overcurrent protection. If the existing battery is
bare or relied on the charger module for protection, this architecture needs a
qualified protection stage before fabrication. Do not bypass protection.

## Current and capacitor sizing

For an illustrative 6 V/1 A coil, 6.24 V output, 3.2 V battery and 85% conversion
efficiency, the coil alone demands about 2.29 A from the battery. Allowing 0.4 W
at 3V3 with two 85%-efficient conversion stages raises the illustrative total to
about 2.47 A. These are assumptions, not measured ratings. The battery/BMS,
pigtail, switch, fuse and wiring must support the measured pulse and inrush.
A 2 A PH battery connector could be inadequate under this scenario; wire pads
on this PCB do not upgrade the existing pigtail's rating.

C1 is Panasonic EEUFR1A471, 470 uF/10 V, D8×11.5 mm, 3.5 mm lead pitch. C8 is
EEUFR1A101, 100 uF/10 V, D5×11 mm, 2 mm pitch. The 470 uF capacitor only supplies a
1 A load for about 0.235 ms before losing 0.5 V (`t=C*dV/I`); the battery and boost
must sustain the whole 300 ms firmware pulse. Do not treat bulk capacitance as
a substitute for a qualified regulator.

F1's 3 A /0467003.NR entry is a candidate, pending fuse time-current/inrush and
harness coordination. Ceramic capacitor values and footprints are selected,
but final MPNs require DC-bias curves: C10/C11 must retain at least 4.7 uF at their
operating voltage and C9 at least 1 uF at 20 V. They are explicitly open BOM items.
At 100 mA and roughly 2.9 V cell voltage, charger dissipation is around 0.23 W at
the upper USB voltage, before accounting for the NCP361 drop. Thermal regulation
protects the charger IC; it does not monitor the battery temperature.

## Connectors and assembly

| Ref | Connection | Carrier pin map |
|---|---|---|
| J1 | Protected battery wire pads | 1 battery+, 2 ground; independently verify polarity |
| J2 | Latching RUN switch | 1 fused battery+, 2 switched battery+; ≥3 A DC candidate subject to measured load |
| J3 | USB4125-GF-A | Charge-only USB-C; both CC resistors, both VBUS pins, both GND pins and shell are connected |
| J4 | B2B-XH-A / XHP-2 | 1 coil+, 2 switched coil− |
| J5 | B8B-XH-A / XHP-8 | 1 SS, 2 SCK, 3 MOSI, 4 MISO, 5 NC, 6 ground, 7 reset, 8 3V3 |
| J6 | B8B-PH-K-S / PHR-8 | 1 ground, 2 ground, 3 wake, 4 cancel/admin, 5 red LED anode, 6 green LED anode, 7 buzzer+, 8 buzzer− |

Momentary buttons connect their signal to ground. LED cathodes connect to
ground; each LED already has its own resistor on the PCB. Buzzer+ is 3V3 and
buzzer− is the switched return. Choose compatible crimp contacts for the actual
wire gauge. Do not use generic cable colors as a polarity specification.

The Nano uses two 1×15 female sockets, 2.54 mm pitch and 15.24 mm row spacing.
Reserve 14 mm above the carrier for its socketed stack until an exact socket
part is selected. Boost modules need a 2.5 mm insulated header gap plus support
under their free edge. Never let a module underside touch carrier copper.
Solder low-profile SMD parts first, inspect polarity, then connectors/caps,
then sockets and modules. Test rails with the Nano and solenoid disconnected.

`interfaces.json` records manufacturer views and pin mappings. U3's six holes
are along the **bottom** edge in the unrotated top view, left-to-right
EN/VIN/GND/GND/VOUT/VOUT. U4's body is **8.1 mm wide ×13.1 mm tall** in the
unrotated top view, with VIN/GND/VOUT left-to-right. The manufacturers' bottom
views are mirrored; confusing these views reverses a regulator connection.
Carrier pin numbers are our interface numbering, not manufacturer pin numbers.
Carrier regulator holes are 1.2 mm plated nominal with 2.0 mm pads (0.4 mm
nominal annular ring). Select the exact headers and check finished-hole and
location tolerances with the board fabricator; a hole-center check is not a
physical fit test.

## Mechanical integration

`mechanical/PCB_outline_fit_coupon.step` and `.stl` are nonfunctional dimensional
fit coupons. `carrier_envelope.step` reserves socket/module/mated-connector
height. The STEP assembly and placement report use rev 3g's 170×111 mm housing
coordinates, unchanged battery and solenoid envelopes, and conservative
component envelopes. They are not replacement production housing files.

The proposed arrangement removes the old separate electronics trays, places
the carrier in one mounting bay, moves the reader to the right with its antenna
away from carrier copper, and relocates panel components and the USB opening.
It needs new carrier supports, a reader holder, a revised lid/charging opening,
a top-open rear charge notch capped by the revised lid,
wire strain relief and verification of real mating/cable/tool access. Inspect
the proposed placement and actual parts before committing any enclosure print.
The solenoid mechanism remains a separate physical-fit qualification.

## Verification and release gates

`validation.json` records checks against the supplied file hashes. Native KiCad
9.0.9 reports **zero ERC violations, zero DRC violations, zero unconnected items
and zero schematic/PCB parity issues**, with all severities included and no
exclusions. The independent checker also verifies 126 connected pins on 32
functional nets, 16 isolated NC pins, component values, manufacturer pin
contracts and module hole positions/drills. Original reports are `erc.json`
and `drc.json`.

The envelope model detects 13 conflicts with the old electronics arrangement.
Its revised layout has no tested collisions. A continuous 40 mm vertical sweep
exposed a charging-connector collision with a closed rear aperture; the proposed
12 mm-wide notch now extends to the housing rim. The revised lid must cap that
notch. PCB insertion, lid-component lowering, M3 screwdriver access and modeled
USB plug access pass for the stated envelopes. This is not a finished housing
or a test of real cable bends, supports, fastener retention or sealing.

Before a fabrication release, close all of these:

1. Identify and measure the actual coil, protected cell/BMS/pigtail, buzzer and
   final capacitor/fuse/socket/header variants. Match charge/discharge ratings.
2. Complete enclosure mounts, port/window/panel positions, cable bends, connector
   mating and tool access; verify the complete installation with real parts.
3. Review the manufacturer footprint/polarity drawings and PCB-fab capability.
   Re-run the supplied checks after any changes. This design needs a two-layer board with plated holes/vias and solder
   mask; a K1/K1 Max prints the plastic mounts/fit coupons, not this circuit.
4. Prototype with a current-limited supply first. Scope both rails and MOSFET
   drain while pulsing the actual coil at fresh/low battery; check startup,
   fuse inrush, input sag, Nano resets and latch release. Then qualify charging
   and thermal behavior in the closed housing with the correct protected cell.
5. Check RFID range with the actual lid, battery, coil and carrier installed.
   For runtime tests, review DEBUG/DEV_NO_SLEEP and calibrate battery sensing;
   the present sketch is configured for bench uploads, not demonstrated runtime.

No Gerber/order package is labeled final in this revision. The ZIP is a review
package containing editable sources, native KiCad files, previews, reports and
mechanical fit references.

## Rebuild

The included files were checked with KiCad CLI 9.0.9. Python generators use
the KiCad 7.0.11 `pcbnew` API, Python 3.12/numpy, CairoSVG, Matplotlib and
CadQuery. Opening the native project in KiCad 9 requires no generators.

To verify the delivered board without rebuilding or rerouting:

```
python validate.py
python mechanical.py
```

`build.py` replaces the board with an unrouted layout unless passed
`--schematic-only`. Preserve routed work before running a complete rebuild:

```
python build.py
python route.py
python sync_board.py
python validate.py
python mechanical.py
python publish_views.py
```

The explicit checks and source links are part of the package. Preserve Rev A
for history; use Rev B for subsequent development.

## DFM refinement

See `DFM_REVIEW.md` for the commercial-fabrication and hand-assembly changes, connector tolerance gates and reproduction commands. `dfm_report.json` records the measured pad-mask spacing and manufacturing export hashes. `manufacturing_REVIEW_ONLY/` is for fabricator CAM review, not an order release.
