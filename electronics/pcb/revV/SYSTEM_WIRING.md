# Rev V system wiring — engineering prototype

The printed carrier handles the Nano ESP32, RFID, panel, buzzer and battery monitor. Coil current does not pass through its ink. This is a different connector standard from Rev B: J1/J5/J6 are 2.54 mm headers, not JST PH/XH. Label harnesses at both ends and verify each pin before connection. Numbers below are carrier pad numbers; reader and Nano labels are the authoritative signal names.

| J1 carrier pad | Function | External connection |
|---|---|---|
| 1 | NANO_7V5 | Pololu 4943 U3V16F7 VOUT, nominal 7.5 V |
| 2 | GND | Star ground shared with protected battery, both regulators and solenoid driver source |
| 3 | BAT_MON | Switched protected battery positive, after fuse and RUN switch; only the 100k/100k measurement divider |
| 4 | SOL_GATE | External AO3400A gate; onboard 330 ohm resistor from Nano D5 |

Power assembly: protected 1S battery → coordinated fuse → RUN switch → both Pololu VIN inputs. Pololu 4013 U3V40F6 powers the coil at nominal 6 V; Pololu 4943 powers Nano VIN at nominal 7.5 V. These are the same selected module interfaces as Rev B, not footprints for arbitrary regulator clones. Wire power directly with a suitably rated harness. Confirm actual cell/BMS, fuse, coil current, pulse duty and regulator performance before energizing the final assembly.

External solenoid driver: genuine AO3400A pin1 G / pin2 S / pin3 D, on a suitable copper adapter. Source to star ground, drain to coil negative. Coil positive to the 6 V regulator. Add 100k from gate to source **at the driver**, so unplugging J1 leaves it off. SS34 flyback cathode/band to coil positive, anode to coil negative; keep the suppression loop local. Retain the Rev B candidate 470uF 10 V bulk capacitor at the coil rail and 100uF battery/boost input bypass, with correct polarity. The carrier schematic intentionally has no onboard coil-power MOSFET or flyback loop. The external adapter, harness conductor size and enclosure mounts are not yet mechanically qualified.

Pololu top-view module pins, left to right along the header edge (do not use mirrored bottom labels):
- 4013: EN, VIN, GND, GND, VOUT, VOUT. Tie EN to VIN and use both GND/output pins as appropriate to the rated connection.
- 4943: VIN, GND, VOUT.

The carrier has **no charger or battery protection**. Charge the protected cell through a separately qualified charger while disconnected from the load; do not connect USB to the Nano at the same time as external VIN during this prototype's bring-up. Charger selection, charge rate and temperature constraints remain release inputs; no arbitrary TP4056 clone pinout is assumed by this layout.

| J5 pad | RC522 label |
|---|---|
| 1 | SDA / SS |
| 2 | SCK |
| 3 | MOSI |
| 4 | MISO |
| 5 | IRQ: unused, leave unconnected |
| 6 | GND |
| 7 | RST |
| 8 | 3.3 V (never 5 V) |

| J6 pad | Panel connection |
|---|---|
| 1 | Ground: LED cathodes / button returns |
| 2 | Ground: second return |
| 3 | Normally-open wake button, other terminal to ground |
| 4 | Normally-open cancel/admin button, other terminal to ground |
| 5 | Red LED anode; onboard 470 ohm resistor |
| 6 | Green LED anode; onboard 470 ohm resistor |
| 7 | Active buzzer positive, 3.3 V |
| 8 | Active buzzer switched negative; onboard AO3400A |

Firmware GPIO names retain Rev B mapping: D13 SCK, D12 MISO, D11 MOSI, D10 SS, D4 RFID reset, D9 green LED, D8 red LED, D6 buzzer, D5 solenoid, D3 wake, D2 cancel, A0 battery sense. Use the Arduino Nano ESP32's appropriate pin-numbering mode and the existing firmware; numerical GPIO constants are not interchangeable with D-pin labels. Buttons use pullups. Reader is continuously powered; keep its antenna clear of metal and the battery.

## Installation and bench acceptance

Fabricate a coupon first with the actual FEDC ink, cure and solder process. Measure resistance, inspect bridges, qualify rivet/header fit and adhesion. Assemble underside SMD parts and rivets before sockets/modules obstruct access; install and inspect every small/large copper rivet listed in `rivet_map.csv`, then install the Nano. Any listed JP wire is an installed component; an empty jumper list means none are required. Layer changes require physical copper rivets; printed ink does not line the hole walls. Measure continuity through each rivet before installing modules.

Check divider output: A0 nominally BAT_MON/2 (2.1 V at a 4.2 V cell). Measure all supply rails and idle coil-gate voltage with the Nano removed and a current-limited supply; confirm polarity and shorts. Bring up Nano/reader/panel, then connect the external driver with its pulldown present. Confirm low gate voltage during boot/reset, coil release behavior, supply droop and temperature through repeated intended pulses. Scope the logic rails for resets/interference.

The board retains the 90 × 55 mm outline and four mount centers, with a 4 mm proposed underside gap. The mechanical preview reserves 3 mm below the board for parts/rivet ends and any wiring; trim and inspect rivet/header ends and physically confirm the underside clearance. External power modules/charger/driver and cable bend radii need new retention and an installation check. The fit gauge is not approval of a fully populated lock enclosure.
