# RFID Bike Lock

A frame-mounted, RFID/NFC-unlocked bike lock with a retractable anti-cut steel cable.

The lock is a stainless-steel clamshell cylinder that clamps permanently onto the bike
frame over a compressible liner. A retractable steel cable lives on a spring-loaded spool
in the bottom of the housing; you pull it out, loop it through the wheel or around a rack,
and click the cable head into a latch on top. Tapping an authorized NFC fob (or phone —
see the design doc for the honest caveats) fires a solenoid that pulls the locking pin and
releases the cable, which then reels itself back in.

## Repo map — everything lives on one branch, organized by iteration

| Path | What it is |
|---|---|
| [`DESIGN.md`](DESIGN.md) | The full engineering design document: user workflow, electronics, wiring, power budget, mechanical dimensions, water/power hardening (§4.5), security analysis |
| [`BOM.md`](BOM.md) | Bill of materials — every part, quantity, estimated price (v0.8 all-M3 heat-set fastener standard + v0.8.3 weatherproofing items) |
| [`BUILD.md`](BUILD.md) | The authoritative bench build sequence + print-orientation table (`--dfm`) |
| [`ASSEMBLY.md`](ASSEMBLY.md) | Assembly/DFM audit + v0.8.3 weatherproofing steps |
| [`firmware/`](firmware/) | Arduino sketch (v1, ready to flash) + bench bring-up guide |
| [`cad/bike_lock_cq.py`](cad/) | **The single source of truth**: parametric CadQuery model with built-in verification gates (`--gaps`, `--matrix`, `--sweep`, `--support`, `--dfm`) |
| [`releases/`](releases/) | **Frozen STEP file sets, one folder per iteration** (see index below) |
| `renders/` | Current assembly renders (closed / open / exploded) |
| `step/`, `stl/` | *Generated build outputs — gitignored; `python cad/bike_lock_cq.py` regenerates them* |

## Iteration index (newest first)

Each `releases/vX/` folder holds the frozen **STEP files** for that iteration (per-part
`placed/` set + full assembly + combined multibody) and a `MANIFEST.md` describing exactly
what changed. Older bulk formats (STL, doc snapshots) were trimmed for clarity — git
history preserves every byte.

| Iteration | Where | What it was |
|---|---|---|
| **v0.8.3** (current) | [`releases/v0.8.3/`](releases/v0.8.3/) | Environmental + DFM hardening: latch-bore & drum weep drains, TPU USB port plug, flush-printing cart, `--dfm` orientation scan, 6 V-rail power option, weatherproofing BOM |
| v0.8.2 | git history of `releases/v0.8.3/` (MANIFEST §v0.8.2) | Structural audit: `--support` gate, all 17 under-supported heat-set holes fixed, driver card moved onto the pedestal cart (Option C) |
| v0.8 / v0.8.1 | same MANIFEST, §v0.8/§v0.8.1 | All-M3 heat-set fastener rebuild + snug-fit pocket tuning (Ø4.0 locked) + test coupon |
| v0.7 | [`releases/v0.7/`](releases/v0.7/) | Electronics as placed reference bodies; driver relocation; release process begins |
| v0.5–v0.6 | `cad/` git history | Spine+door consumer-install architecture; hinge rod; verification gates born |
| v0.3–v0.4 | [`cad/archive/`](cad/archive/) | Early CadQuery restructure + slim-top architecture (source + STEP kept) |
| v0.2 | `cad/legacy_bike_lock_v02.scad` | Original OpenSCAD sketch |

## Status

**Design phase — firmware written, nothing physically built yet.** The next milestones
(detailed at the end of `DESIGN.md`) are:

1. Breadboard the electronics (Nano + PN532 + solenoid) and prove the unlock flow —
   the firmware and a step-by-step bring-up guide are waiting in `firmware/`
2. 3D-print the v1 housing (PETG first article; ASA for the outdoor unit) from
   `releases/v0.8.3/` — print orientations in `BUILD.md` §3b
3. Fabricate the stainless housing

## Key design decisions so far

- **MCU:** Arduino Nano (upgrade path to 3.3 V Pro Mini for longer battery life)
- **Reader:** PN532 NFC module. Keys: NTAG213 sticker on the owner's phone case +
  keychain fobs (owner has an iPhone, which can't act as a hobby NFC key, so no
  companion app is planned)
- **Battery:** 103450 LiPo pouch 2000 mAh (protected) + TP4056 USB-C charge board — the 18650 stopped packaging at v0.4
- **Locking:** insert-to-lock needs **no power** (ramped cable head snaps past a spring pin);
  power is only used for the ~300 ms unlock pulse and brief scan windows
- **One-size-fits-all fit:** a printed TPU *finned* liner (fins bend instead of foam
  crushing, so it stays snug for years) covers Ø32–46 mm down tubes, closure
  detents fine-tune preload, and an included shim sleeve extends down to Ø27 mm skinny
  steel frames — see `DESIGN.md` §6.2
- **Self-guarding closure:** the only screw holding the housing shut sits at the bottom
  of the latch bore, so the locked cable head physically covers it — the case can't be
  unscrewed off the frame while the bike is locked (`DESIGN.md` §6.4). Note: as of the
  v0.6 CAD audit, four *other* service joints (hatch, spine cover, hinge cap, lid) are
  ordinary external screws reachable on the locked bike without unlocking anything —
  see `DESIGN.md` §7 for the honest security consequences and the production mitigation
  plan
- **v1 housing is 3D printed** (ASA for outdoor UV resistance); the latch keeps a steel
  pin + bushing even in plastic
- **Dead-battery behavior:** fail-secure — a dead battery stays locked, and the USB-C
  charge port doubles as the sole emergency input: any phone power bank runs the lock
  instantly for an unlock (`DESIGN.md` §8). There is no cam-lock backstop — it was
  deleted at v0.4 (the slim top never had a wall tall enough for its barrel)
