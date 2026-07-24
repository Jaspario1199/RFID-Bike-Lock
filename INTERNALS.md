# INTERNALS.md — how every electronic mates inside the lock (v0.8.3c)

Companion to [BUILD.md](BUILD.md) (which gives the *order*); this file gives the *mating* —
what surface sits on what, with which screws, keyed to the renders in
[`renders/internals/`](renders/internals/). Coordinates are the CAD's global frame
(x along the lock, z up, all mm).

> **SolidWorks note:** `newest-design/bike_lock_assembly_v083.step` imports with every
> component ALREADY in its mated position — you don't need to build mates to see the truth.
> If you are re-assembling from individual part STEPs, use the positions/contacts below
> (fix the body, then place each part by its listed contact faces).

> **The ORANGE part around the solenoid is the `pedestal_cart`** (file
> `05_pedestal_cart_v083.step`) — the printed carrier that holds the solenoid tower, the
> driver-card platform, and the MT3608 rails. The nano_clamp bar is the same orange.

## The one-module concept (render 02)

The **pedestal cart is a drop-in module**: on the bench you bolt the solenoid on top,
screw the driver card to its −Y platform, and slide the MT3608 into its +Y rails — then
the loaded cart drops into the pod as one unit and is held by 2 screws. Pull 2 screws and
the whole drive stage comes back out with its wiring intact.

## Pod deck (renders 01, 02, 03)

| # | Part | Sits on / in | Fastened by | Key contacts |
|---|---|---|---|---|
| 1 | **Pedestal cart** (ORANGE) | Its base plate (z32 underside) rests on the two Ø12 body pads at (79,10) & (87,10) | 2× M3×? machine down through the base counterbores into the pads' short heat-sets — driven through the Ø6.5 access holes in the tower top, BEFORE the solenoid goes on | Base bottom ↔ pad tops (z32). Scallop in the cart clears the Ø19 latch boss by 0.5 |
| 2 | **Solenoid JF-0530B** (grey) | Flat on the cart tower top (z37), body centered on y10, plunger pointing −X toward the latch bore | 2× M2.5×8 machine into the tower's M2.5 heat-sets (x71 & x95) | Tower top ↔ solenoid underside (contact). Plunger nose reaches x61.4 → **0.10 mm engagement gap** to the cable-head groove (by design). ⚠ VERIFY the real unit's hole spacing = 24 mm before pressing the inserts |
| 3 | **Driver card** (green, 42×10.7 perfboard) | On the two Ø8 boss tops on the cart's −Y platform, seat z36.3, centerline y−7.25 | 2× M3 machine into the SHORT heat-sets in the bosses (x66 & x96) | Card underside ↔ boss tops only (1.3 mm air gap over the platform — intentional, drainage). Components face UP. <25 mm wire run to the solenoid |
| 4 | **MT3608** (green) | Vertical in the cart's +Y rail slots (posts at x65.5 & x102.5), PCB plane y~23, components facing the tower | Friction slot, slide in from the top | PCB edges ↔ rail slots. Inductor lives in the 4.2 mm gap toward the tower. 0.3 min gap to the solenoid |
| 5 | **Arduino Nano** (green) | EDGE-STANDING in the wall recess at y26.3–28, x1.5–47.5 (USB end at x39–47, pins trimmed flush) | `nano_clamp` bar (orange) over it: 2× M3 machine into the crown-boss heat-sets at (12,18) & (37,18) | Board edge in the 1.7 mm recess slot; clamp bar edge presses the PCB's −Y face along the SMD-free strip |
| 6 | **Cable head** (brass color) | Drops into the Ø11 latch bore at (58,10) from the top | Nothing — the solenoid plunger snaps into its ring groove (that IS the lock) | Head Ø10 in the Ø11 bore; groove floor at plunger height z44.5 |
| 7 | **1000 µF cap** (on the driver card) | LYING DOWN on the card | soldered | Ø8×12.5 case only — taller variants hit the lid |

## RFID layer + lid (render 03 — lid shown lifted)

| # | Part | Sits on / in | Fastened by | Key contacts |
|---|---|---|---|---|
| 8 | **PN532** (green) | Under the lid: pressed up against the 4 Ø6 drop-bosses hanging from the lid's window-pocket ceiling; board top at z52.7, corner holes at 2.54 in from each corner | 4× M3 **NYLON** screws up into the boss pilots (no brass here — RF) | Board top face ↔ boss tips. Board edges ride in the body's 1.3 mm-wall rim rebate (x5–48.2). Install on the lid FIRST, then lower lid+board together |
| 9 | **Wake button** (12 mm sealed) | Panel-mounts through the lid hole at (106, 13.5) | Its own nut from below | Lid top recess ↔ button bezel |
| 10 | **LEDs 2× 3 mm** | Through the two Ø3.3 lid holes at x98 (y0 & y6), inserted from below | Clear RTV silicone pot (BOM 30b) — this is also the water seal | Dome tops sit in the lid's top recess |
| 11 | **Lid** | On the pod rim at z53 (0.5 reveal inset all around) | 4× M3×10 countersunk machine into the rim-boss heat-sets at (54,−9)(54,23)(114,−9)(114,23) | Lid underside ↔ rim face — lay the EPDM gasket tape (BOM 30a) on the rim first, punch the 4 screw holes |

## Battery bay (renders 04, 05 — viewed from below)

| # | Part | Sits on / in | Fastened by | Key contacts |
|---|---|---|---|---|
| 12 | **TP4056 USB-C** | Standing on its LONG edge in the two slot blocks at x18.5 & x33 (PCB plane y29.05–30.65), components facing −Y | Slots + the USB-C port registering in the bay wall opening | Slide −X until the port seats in the wall port. Plug the **`usb_plug`** (TPU) in when not charging |
| 13 | **LiPo 103450** (silver) | ON EDGE along the +Y bay wall (50×34 face vertical), y34.3–44.3 | +Y wall on one side, the printed rail at y33.25 on the other | 0.4 gap to the TP4056 block. Leads exit toward the spine window (leave the documented service loop) |
| 14 | **Bay hatch / tray** | Its raised pad nests up into the floor window (0.15/side clearance); Nano-era zip grid on the pad carries nothing now — use it for wire dressing | 2× M3×10 countersunk machine up into the bay heat-sets at (13,20) & (60,23), heads flush on the OUTSIDE face | Pad ↔ window walls; the tray's zip holes double as weep drains |
| 15 | **Bay module itself** | Its saddle against the shell from below | 4× M3×12 socket-cap from INSIDE the clamp bore (x10.1–60.1 along y12.11), heads sub-flush in Ø6 counterbores | Bay bosses ↔ shell wall. Only reachable with the door open — that's the anti-tamper |

## Wiring paths (fixed by the geometry)

- **Bay → pod**: exactly 2 conductors (battery + and −) leave the bay through the spine
  window (x28, +Y side), run the open spine raceway, enter the pod through the feed hole.
  `spine_cover` screws over the raceway last (2× M3).
- **Inside the pod**: battery pair → MT3608 IN. MT3608 OUT (set 5.0 V, or 6.0 V per the
  DESIGN §4.5 full-force option) → driver card bus → solenoid (<25 mm), → Nano, → PN532
  via the P-FET gate. Keep the flyback diode + reservoir cap ON the driver card.
- **Solenoid leads**: 20 cm stock leads shorten to the adjacent driver card — trim.

## Collision status (machine-checked at v0.8.3c)

Every pair in the assembly is verified: **0 interpenetrations at 0.01 mm³ floor, 292 gap
checks green, door sweep 0.00 mm³**. Solenoid specifically: cart contact = bolted joint
(intended), cable-head 0.10 mm = the designed plunger engagement, body 0.30, MT3608 0.30,
lid 1.0, button 1.0, driver card 3.9, everything else >10 mm.
