# Bill of Materials

Prices are typical AliExpress/Amazon hobby prices (mid-2026); buying the electronics as a
lot from AliExpress roughly halves the Amazon total but takes 2–4 weeks.

## Electronics (~$32)

| # | Part | Spec / example | Qty | Est. |
|---|---|---|---|---|
| 1 | Arduino Nano (clone, CH340) | 5 V/16 MHz | 1 | $4 |
| 2 | PN532 NFC module | Elechouse V3 style, set to I2C | 1 | $8 |
| 3 | Linear pull solenoid | JF-0530B **6 V** variant, ~20 Ω/300 mA, 5 N/10 mm; body 30×13×15 mm, plunger Ø6×58 mm | 1 | $4 |
| 4 | 18650 Li-ion cell, protected | ≥2500 mAh (Samsung 25R class + protection PCB, or protected cell) | 1 | $6 |
| 5 | 18650 holder | single, leaf-spring; 76 × 21 × 21 mm outer | 1 | $1 |
| 6 | TP4056 charge board **with protection** (USB-C version) | has DW01 + FS8205 on board; 29 × 17.3 × 4.3 mm | 1 | $1.50 |
| 7 | MT3608 boost converter | set to 5.0 V; 36 × 17 mm | 1 | $1.50 |
| 8 | N-MOSFET (solenoid) | IRLZ44N (TO-220, logic-level) | 1 | $1 |
| 9 | P-MOSFET (PN532 power gate) | AO3401 / IRLML6402 (SOT-23 on breakout) | 1 | $0.50 |
| 10 | Flyback diode | 1N5819 Schottky | 1 | $0.20 |
| 11 | Reservoir capacitor | 1000 µF / 10 V electrolytic | 1 | $0.50 |
| 12 | Wake pushbutton | sealed momentary, panel-mount 12 mm | 1 | $1 |
| 13 | LEDs + resistors | red + green 3 mm, 470 Ω ×2, 100 Ω, 100 kΩ ×3 | — | $1 |
| 14 | MIFARE Classic fobs | 13.56 MHz keychain fobs | 3 | $2 |
| 15 | NTAG213 stickers | for phone case "phone unlock" | 5 | $2 |
| 16 | Perfboard, wire, heatshrink | — | — | $3 |

## Mechanical — Phase 1 printed v1 (~$30)

| # | Part | Spec | Qty | Est. |
|---|---|---|---|---|
| 17 | Housing filament | PETG for the first article; ASA for the unit that lives outdoors (UV), ~250 g | — | $6 |
| 17b | TPU 95A filament | finned liner + shim sleeve (DESIGN.md §6.2), ~50 g | — | $2 |
| 18 | Wire rope | 4 mm 7×7 stainless, PVC-coated, 2 m | 1 | $8 |
| 19 | Cable end stop / swage sleeves | 4 mm aluminum, crimp | 4 | $2 |
| 20 | Donor retractable reel | heavy-duty dog leash or badge reel (spring + spool) | 1 | $8 |
| 21 | Ejector spring | light compression, under the bore floor (the locking preload now comes from the solenoid's own return spring — v0.3 plunger-as-pin) | 1 | $2 |
| 22 | Silicone sponge sheet — *only if TPU printing is unavailable* (fallback liner) | 10 mm, medium density | 1 | ($8) |
| 23 | Closure hardware | 1 × M4 low-profile socket screw + washer + brass heat-set insert (lives at the bottom of the latch bore, DESIGN.md §6.4); long 2.5 mm hex key | — | $2 |
| 23b | Hinge pins | Ø3 mm stainless rod, 2 × ~55 mm (blind channels, glued printed end plugs) | 1 rod | $1 |
| 23d | Drum module screws | M4 × 12 self-tap ×4 (driven from inside the clamp bore) | 4 | $1 |
| 23c | Cam lock backstop (v1 only) | mini tubular-key cam lock, retracts the locking pin manually; hidden under a rubber plug | 1 | $4 |

## Mechanical — Phase 2 steel housing (TBD, ~$40–80)

| # | Part | Spec | Qty |
|---|---|---|---|
| 24 | 304 stainless sheet | 1.5 mm, rolled to Ø55 mm shell | 1 |
| 25 | Stainless piano hinge | 30 mm segments | 2 |
| 26 | Hardened receiver bushing | drill bushing, Ø10 mm ID | 1 |
| 27 | Locking pin | not needed in v1 (solenoid plunger is the pin); steel version may revert to Ø4 drill blank | (1) |
| 28 | Cable head | machined, hardened mushroom w/ groove (shop job) | 1 |
| 29 | ABS/polycarbonate window | 2 mm, over PN532 antenna | 1 |

## Notes

- Item 6: make sure the TP4056 board is the **protected** variant (6 pins to battery side,
  two extra chips) — item 4's protection is then a second layer, which is fine.
- Item 3: buy 2–3 solenoids; clone JF-0530B force varies a lot and we need to match the
  pin spring to the real pull force at 3.5 V.
- Item 20: before buying springs (21), gut the donor reel — its spring, spool, and even
  the ratchet often cover items 21's ejector needs too.
- Item 17b: TPU prints best slow (~25 mm/s) on a direct-drive extruder; bowden printers
  can do 95A with care. If neither is available, fall back to item 22.
