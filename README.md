# RFID Bike Lock

A frame-mounted, RFID/NFC-unlocked bike lock with a retractable anti-cut steel cable.

The lock is a stainless-steel clamshell cylinder that clamps permanently onto the bike
frame over a compressible liner. A retractable steel cable lives on a spring-loaded spool
in the bottom of the housing; you pull it out, loop it through the wheel or around a rack,
and click the cable head into a latch on top. Tapping an authorized NFC fob (or phone —
see the design doc for the honest caveats) fires a solenoid that pulls the locking pin and
releases the cable, which then reels itself back in.

## Repo map

| File | What it is |
|---|---|
| [`DESIGN.md`](DESIGN.md) | The full engineering design document: user workflow, electronics, wiring, power budget, mechanical dimensions, security analysis, open questions |
| [`BOM.md`](BOM.md) | Bill of materials — every part, quantity, and estimated price |
| [`firmware/`](firmware/) | Arduino sketch (v1, ready to flash) + bench bring-up guide |

## Status

**Design phase — firmware written, nothing physically built yet.** The next milestones
(detailed at the end of `DESIGN.md`) are:

1. Breadboard the electronics (Nano + PN532 + solenoid) and prove the unlock flow —
   the firmware and a step-by-step bring-up guide are waiting in `firmware/`
2. 3D-print the v1 housing (ASA/PETG) — the first real model is plastic, steel comes later
3. Fabricate the stainless housing

## Key design decisions so far

- **MCU:** Arduino Nano (upgrade path to 3.3 V Pro Mini for longer battery life)
- **Reader:** PN532 NFC module — the only cheap module that can talk to phones at all
- **Battery:** single 18650 Li-ion + TP4056 USB-C charge board
- **Locking:** insert-to-lock needs **no power** (ramped cable head snaps past a spring pin);
  power is only used for the ~300 ms unlock pulse and brief scan windows
- **One-size-fits-all fit:** a printed TPU *finned* liner (fins bend instead of foam
  crushing, so it stays snug for years) covers Ø32–46 mm down tubes, closure
  detents fine-tune preload, and an included shim sleeve extends down to Ø27 mm skinny
  steel frames — see `DESIGN.md` §6.2
- **Self-guarding closure:** the only screw holding the housing shut sits at the bottom
  of the latch bore, so the locked cable head physically covers it — the case can't be
  unscrewed off the frame while the bike is locked (`DESIGN.md` §6.4)
- **v1 housing is 3D printed** (ASA for outdoor UV resistance); the latch keeps a steel
  pin + bushing even in plastic
- **Dead-battery behavior:** still open — see the fail-safe section of `DESIGN.md` for why
  "unlocks when dead" is both a security hole and physically the harder option to build
