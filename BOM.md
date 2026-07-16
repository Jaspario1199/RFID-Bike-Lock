# Bill of Materials

Prices are typical AliExpress/Amazon hobby prices (mid-2026); buying the electronics as a
lot from AliExpress roughly halves the Amazon total but takes 2–4 weeks.

## Electronics (~$32)

| # | Part | Spec / example | Qty | Est. |
|---|---|---|---|---|
| 1 | Arduino Nano (clone, CH340) | 5 V/16 MHz | 1 | $4 |
| 2 | PN532 NFC module | Elechouse V3 style, set to I2C | 1 | $8 |
| 3 | Linear pull solenoid | JF-0530B **6 V** variant, ~20 Ω/300 mA, 5 N/10 mm; body 30×13×15 mm, plunger Ø6×58 mm | 1 | $4 |
| 4 | **103450 LiPo pouch, with protection PCB** | 2000 mAh, 34 × 50 × 10 mm (v0.4: the 18650 no longer packages in the bottom bay; stands on edge in v0.6 bay — 50×34 mm face vertical, clears the TP4056 block) | 1 | $6 |
| 5 | ~~18650 holder~~ | not needed in v0.4 — the LiPo sits in a printed frame in the bay | — | — |
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
| 16 | Perfboard 4×6 cm, wire, heatshrink | CUT the 40×60 board to **40×23 mm** (v0.7: it stands vertically against the bay wall; the clamp-bore wedge caps the height). 1000 µF cap mounts **lying down** (Ø8×12.5 spec — order that case size). MT3608 mounts on the pedestal tower rails in the pod, NOT on the perfboard. Nano pins: **trim flush** after soldering (edge-stand recess policy) | — | $3 |

## Mechanical — Phase 1 printed v1 (~$40)

| # | Part | Spec | Qty | Est. |
|---|---|---|---|---|
| 17 | Housing filament | PETG for the first article; ASA for the unit that lives outdoors (UV), ~250 g | — | $6 |
| 17b | TPU 95A filament | finned liner + shim sleeve (DESIGN.md §6.2), ~50 g | — | $2 |
| 18 | Wire rope | 4 mm 7×7 stainless, PVC-coated, 1.5 m (1.2 m on the v0.5 slim drum) | 1 | $8 |
| 19 | Cable end stop / swage sleeves | 4 mm aluminum, crimp | 4 | $2 |
| 20 | Donor retractable reel | heavy-duty dog leash or badge reel (spring + spool) | 1 | $8 |
| 21 | Ejector spring | light compression, under the bore floor (the locking preload now comes from the solenoid's own return spring — v0.3 plunger-as-pin) | 1 | $2 |
| 22 | Silicone sponge sheet — *only if TPU printing is unavailable* (fallback liner) | 10 mm, medium density | 1 | ($8) |
| 23a | Closure screw + insert | M4×8 low-profile socket machine screw + washer ×1 + short M4 heat-set (Ø5.6×L3, VERIFY sourcing) ×1 — closure | 1 | $2 |
| 23b | Bay module screws | M4×12 pan self-tap ×4 — bay module (counterbored sub-flush, inside bore) | 4 | $1 |
| 23c | Lid/hatch/spine screws + inserts | M3×10 countersunk machine (ISO 10642) ×8 + M3 brass heat-set ×6 — lid 4, hatch 2 (into inserts, service joints); spine cover 2 (thread-forming into Ø2.5 pilots, no insert — the ST flat head cone was too deep for the 1.85mm plate) | 8 + 6 | $2 |
| 23d | Spool/spine/hinge-cap/cartridge screws | M3×10 countersunk self-tap ×10 — spool 3, hinge cap 1 (visible, flush); nano sled 2, perfboard shelf 2 (hatch external face); spine cover 2 switched to machine flat (23c) | 8 | $1.50 |
| 23e | Pedestal screws | M3×10 pan self-tap ×2 — pedestal pads (hidden) | 2 | $0.50 |
| 23f | Solenoid screws + inserts | M2.5×8 machine ×2 + M2.5 brass heat-set ×2 — solenoid (cyclic load) | 2 + 2 | $1 |
| 23g | PN532 screws | M2.5×8 **NYLON** machine ×4 — PN532 (RF keep-out; the antenna loop wraps the whole board perimeter, no steel at the edges) | 4 | $1.50 |
| 23h | Hinge rod stock | Ø6 303 stainless bar, 165 mm. ONE lathe op: center-drill the far end and support it on the tailstock live center — a 140 mm Ø4 turn is 35:1 slenderness and **will chatter unsupported**; turn the Ø4.00 shank in light passes, leave the Ø6.0×1.6 head integral, R0.5 head fillet, 0.4×45° head chamfer, R2.2 domed tail; trim to length at dry-fit. Zero-lathe fallback: plain Ø4 ground rod or drill rod stock, cut to length, with a screwed cap at EACH end (no integral head, no lathe op) | 1 | $3 |
| 23i | ~~Cam lock backstop~~ | dropped in v0.4 (no wall tall enough in the slim pod); USB power-bank unlock is the dead-battery path | — | — |

| 23h | Nano sled + perfboard shelf | printed cartridges on the hatch tray (v0.7): Nano rides the tray DIAGONALLY (45mm board, 40.5×29.5 window), pins trimmed flush; perfboard shelf on L-walls above it carries MT3608 + power parts | — | — |
| 23i | Perfboard | 4×6 cm (40×60 mm) stock, CUT to 40×29 along a hole row — neither stock size fits the tray window as purchased | 1 | $1 |
| 23j | Reservoir cap size spec | order Ø8×12.5 mm 1000 µF/10 V explicitly — taller Ø10×16.8 variants exist and eat the shelf headroom | 1 | — |

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

### VERIFY before buying / installing (v0.6)

- Items 23a/23c/23f (inserts): confirm the actual brass heat-set brand/dims match the
  pockets they're pressed into before ordering a set — M3 Ø4.1×6.5, M2.5 Ø3.6×4.5, and the
  short M4 Ø5.6×L3 (item 23a). The M4×L3 length is the least common of the three and may
  need to be sourced from a specialty kit or trimmed down from a longer M4 insert on a
  belt sander/lathe before pressing in; if it can't be sourced at all, the fallback is a
  self-tapped M4 pilot straight into the PETG/ASA pad (no insert) — treat that joint as
  single-use, since re-tapping PETG/ASA repeatedly strips the pilot.
- Item 23d (ST flat-head self-tap screws — spool, spine cover, hinge cap): measure the
  actual screw's included head angle — clone self-tap flat heads ship as either 80° or
  90° — **before** countersinking; the printed countersink (Ø7.2×2.4) is cut for one
  angle and the wrong screw will either sit proud or bottom out before the head seats
  flush. (Item 23c's machine screws are a fixed 90° ISO 10642 countersink and don't need
  this check.)
- Item 3 (solenoid): before drilling the tower for the M2.5 attach inserts, measure the
  real JF-0530B's mounting-hole spacing against `sol_hole_dx` (24 mm in the CAD) — clone
  units vary, and the pedestal cart is a fast reprint but the inserts are not.
- Item 2 (PN532): confirm the board revision actually has the corner mounting holes
  (Ø3, 2.54 mm inset) before relying on the drop-bosses — some clones omit them, in which
  case fall back to the printed corner clips on the same bosses.
- Do **not** buy an M4×14 for the closure screw — it hits the tube envelope on any tube
  ≥Ø38 mm. The closure screw is M4×8 low-profile socket + washer (item 23a).
