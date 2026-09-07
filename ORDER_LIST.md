# ORDER_LIST.md — what to buy to finish the build (v0.8.3c, cross-referenced against owned inventory)

Priority = build order: P1 proves the electronics on the bench before anything prints in
final material. Links are Amazon search URLs (stable) or known listings — **Amazon blocks
automated price/stock checks, so confirm variant + price at checkout.** Prices ±20%.

## ✅ Already owned (RoomCleaner leftovers + kits) — do NOT re-buy

| Item | Source | Covers |
|---|---|---|
| Arduino Uno + breadboard + jumpers + resistors + 3mm LEDs + tactile buttons | ELEGOO UNO R3 Super Starter Kit | Entire breadboard phase; divider/gate resistors; lid LEDs |
| **RC522 RFID kit + MIFARE fobs** | Arduino RFID scanner kit | Full auth bring-up NOW (UID whitelist); maybe the final reader — see the pending range test |
| 12 V 6 A PSU + inline fuse + MP1584 bucks ×6 | RoomCleaner | Bench rig: 12 V → buck @ 6.0 V → solenoid pull tests |
| M3 button-head kit (640 pc, 6–30 mm + nuts/washers) | RoomCleaner | Bench/dry-fit fastening (finals need countersunk — P2) |
| PLA filament | owned | Fit-check prints before PETG |
| ESP32 ×3 | RoomCleaner | nothing now (v2 option) |

**Deferred pending test:** PN532 NFC module + NTAG213 tags (~$12) — only if the RC522's
read range through a 1.2 mm printed plate disappoints. Test before buying:
https://www.amazon.com/s?k=PN532+NFC+module+V3

---

## 🛒 STILL NEEDED — the checkpoint-1 order (verified against the chat log, 2026-09-07)

The transcript shows listings **vetted** but no confirmation you ordered any of them. Links are
Amazon searches pre-filled with the exact brand + title of the listing you showed me, since
ASINs were never in the pasted text. **Amazon blocks automated price/stock checks — confirm
the variant at checkout.**

| # | Item | Exact listing you vetted | Link | ~$ |
|---|---|---|---|---|
| 1 | **TP4056 charger, protected USB-C** | HiLetgo 3pcs TP4056 Type-C, "dual protection functions" | https://www.amazon.com/s?k=HiLetgo+TP4056+Type-c+USB+charging+module+dual+protection | 6 |
| 2 | **103450 LiPo 2000 mAh, protected** | YTKavq 2-pack, 10 × 34 × 50 mm, PCM, JST 1.25 mm — **the 50 mm one matches the CAD exactly**. (JLJLUP's is 52 mm and needs the tray shifted 2 mm) | https://www.amazon.com/s?k=YTKavq+103450+3.7V+2000mAh+LiPo+PCM+protection | 15 |
| 3 | **MT3608 boost** | Ferwooh MT3608 2A adjustable, pack of 5 | https://www.amazon.com/s?k=Ferwooh+MT3608+boost+converter+2A+module | 6 |
| 4 | **IRLZ44N** | ALLECIN IRLZ44N logic-level, 10 pcs TO-220 | https://www.amazon.com/s?k=ALLECIN+IRLZ44N+logic+level+mosfet+TO-220 | 10 |
| 5 | **AO3401 P-MOSFET** | VANXY 8-value SOT-23 kit, 160 pcs (AO3401 is one of the values) | https://www.amazon.com/s?k=VANXY+AO3400+AO3401+SOT23+mosfet+kit | 10 |
| 6 | **1N5819 Schottky** | EEEEE 1N5819, 150 pcs | https://www.amazon.com/s?k=EEEEE+1N5819+schottky+diode | 8 |
| 7 | **Solenoid, 6 V** | ⚠️ **NOT** the Heschen HS-0530B 3.4 A you pasted — see the note below | https://www.amazon.com/s?k=6V+pull+solenoid+10mm+stroke+small | 12 |
| 8 | **AMS1117-3.3 module** | not yet vetted — any breakout with IN/GND/OUT pads | https://www.amazon.com/s?k=AMS1117-3.3+voltage+regulator+module | 7 |
| 9 | **1000 µF 10 V+ electrolytic** | **Ø8 × 12.5 mm case** — taller ones don't fit the box | https://www.amazon.com/s?k=1000uf+16v+electrolytic+capacitor+8x12mm | 6 |
| 10 | **22 AWG silicone wire** | red/black | https://www.amazon.com/s?k=22awg+silicone+wire+red+black | 9 |
| 11 | **JST-XH kit + crimper** | for the detachable lid loop | https://www.amazon.com/s?k=JST+XH+connector+kit+crimp+tool | 12 |

**≈ $100 for everything that gets you through all three bench checkpoints.**

### ⚠️ The solenoid you pasted is the wrong variant
The **Heschen HS-0530B, 6 V 3.4 A** draws 3.4 A. Neither the MT3608 (2 A) nor the protected
cell (~1.5–2 A cutoff) can supply that — the cell's protection would trip on every unlock.
**Buy one whose listing states ~250–350 mA, or a coil resistance of 15–25 Ω.** If a listing
gives neither figure, buy two cheap ones and measure with a multimeter on arrival (`WIRING.md`
§4). This is the one part where the wrong choice stops the build.

### ✔ Already owned — do NOT re-buy
Arduino Nano · RC522 reader + fobs · active **and** passive buzzer · red + green LEDs ·
ELEGOO kit (breadboard, jumpers, resistors, tactile buttons, its power-supply module) ·
perfboard · heat-set inserts · soldering iron · **M3 button-head screw kit** — button heads are
5.7 mm across and 1.65 mm tall, so they *do* fit the Ø6.2 × 2.3 counterbores. That covers all
ten inside-the-bore screws; you only need countersunk M3 for the lid and puck cover (P2).

### ✘ Not for this project
The **ACEIRMC 2S 8.4/12.6/16.8 V board** you already own belongs to RoomCleaner's charging
dock. It charges multi-cell packs and would drive this lock's single 4.2 V cell to 8.4 V.

---

## P1 — Bench bring-up (order first; Checkpoint 1 needs only these + owned kit)

| # | Item | Spec / search term | Link | Qty | ~$ |
|---|---|---|---|---|---|
| 1 | **Solenoid** | JF-0530B pull-type, **6 V winding** (NOT 12/24 V) — VERIFY hole spacing + 13–16 mm width on arrival | https://www.amazon.com/s?k=JF-0530B+solenoid+6V+pull | 2 | 12 |
| 2 | **MT3608 boost** | 2 A adjustable boost module (your MP1584s are bucks — can't boost 3.7→5/6 V) | https://www.amazon.com/s?k=MT3608+boost+converter+module | 3–5 pk | 8 |
| 3 | **TP4056 USB-C** | protected version (has DW01 + FS8205) | https://www.amazon.com/s?k=TP4056+USB+C+charging+module+protection | 3+ pk | 7 |
| 4 | **LiPo cell** | **103450** pouch, 2000 mAh, **with protection PCB**, JST pigtail | https://www.amazon.com/s?k=103450+lipo+battery+2000mah+protected | 1 | 9 |
| 5 | **Logic-level MOSFETs + diode** | IRLZ44N (TO-220) ×5; AO3401 breakout or SOT-23 ×10; 1N5819 ×10 | https://www.amazon.com/s?k=IRLZ44N ; https://www.amazon.com/s?k=AO3401+mosfet ; https://www.amazon.com/s?k=1N5819+schottky | kits | 12 |
| 6 | **Reservoir cap** | 1000 µF / 10 V+ electrolytic, **Ø8 × 12.5 mm max** (taller variants don't fit) | https://www.amazon.com/s?k=1000uf+10v+electrolytic+capacitor+8mm | 5+ | 6 |
| 7 | **Perfboard** | 4 × 6 cm double-sided proto board (driver card cut from this) | https://www.amazon.com/s?k=4x6cm+double+sided+perfboard | pk | 6 |
| 8 | **Arduino Nano** | Nano clone (CH340), ×2 — Uno runs bring-up meanwhile; the pod fits a Nano | https://www.amazon.com/s?k=arduino+nano+ch340+3+pack | 2–3 | 12 |

## P2 — Printing + assembly tooling (order alongside P1)

| # | Item | Spec / search term | Link | Qty | ~$ |
|---|---|---|---|---|---|
| 9 | **Soldering iron + solder** | 60 W adjustable pen + 63/37 rosin core (not owned per RoomCleaner list; blocks inserts AND the driver card) | https://www.amazon.com/s?k=60w+adjustable+soldering+iron+kit | 1 | 20 |
| 10 | **M3 heat-set inserts** | Ø4.1(4.6 OD)×6.5 ~25× + **SHORT Ø4.0×L3.8** ~6× + M2.5 (Ø3.6×4.5) ×4 — ruthex/Hilitchi-style; print the coupon first | https://www.amazon.com/s?k=M3+brass+heat+set+insert+kit+3d+printing ; short: https://www.amazon.com/s?k=M3+heat+set+insert+short+3mm | kits | 14 |
| 11 | **Insert iron tips** | heat-set insert tip set for soldering irons | https://www.amazon.com/s?k=heat+set+insert+soldering+iron+tip | 1 | 9 |
| 12 | **PETG 1 kg** | HATCHBOX/OVERTURE PETG (you own only PLA) | https://www.amazon.com/HATCHBOX-3D-Filament-Dimensional-Accuracy/dp/B00J0ECR5I | 1 | 20 |
| 13 | **TPU 95A 1 kg** | OVERTURE TPU 95A 1.75 mm (liners, shim, usb_plug) | https://www.amazon.com/OVERTURE-Flexible-Printer-Filament-1-75mm/dp/B0991X92K8 | 1 | 22 |
| 14 | **M3 countersunk machine screws** | flat head ISO 10642 90°: M3×10 ×20 + M3×12 **socket cap** ×6 | https://www.amazon.com/s?k=M3+countersunk+flat+head+machine+screw+assortment ; https://www.amazon.com/s?k=M3x12+socket+head+cap+screw | kits | 10 |
| 15 | **M3 NYLON screws** | M3×8 nylon (PN532 — RF keep-out; skip if RC522 wins and I redesign its mount) | https://www.amazon.com/s?k=M3+nylon+screws+kit | kit | 6 |
| 16 | **M2.5 screws** | M2.5×8 machine (solenoid tabs) | https://www.amazon.com/s?k=M2.5x8+machine+screw | pk | 5 |

## P3 — Mechanical completion

| # | Item | Spec / search term | Link | Qty | ~$ |
|---|---|---|---|---|---|
| 17 | **Hinge rod stock** | Ø6 mm 303/304 stainless rod 300 mm (TAMU shop lathe job) — zero-lathe fallback: Ø4 mm drill rod + Ø4.2 drill bit | https://www.amazon.com/s?k=6mm+stainless+steel+rod+303 ; fallback https://www.amazon.com/s?k=4mm+drill+rod | 1 | 8 |
| 18 | **Drill bits** | Ø4.2 mm (hinge bore through clamped knuckles) + Ø6.5 mm (bore ream decision) | https://www.amazon.com/s?k=4.2mm+drill+bit ; https://www.amazon.com/s?k=6.5mm+drill+bit | 1 ea | 8 |
| 19 | **Retractable reel donor** | heavy retractable dog leash (small) or heavy-duty badge reel — donor spring+spool | https://www.amazon.com/s?k=heavy+duty+retractable+dog+leash+small | 1 | 12 |
| 20 | **Security cable** | **3 mm** 7×7 stainless wire rope, PVC coated to **4 mm**, 2 m + **swage sleeves** (CNC casing rev 3 spool is sized for Ø4; the printed v0.8 drum takes it too) | https://www.amazon.com/s?k=3mm+stainless+steel+wire+rope+pvc+coated+4mm ; https://www.amazon.com/s?k=aluminum+swage+sleeve+3mm | 1 | 12 |
| 21 | **Cable-head stock** | Phase-0 bench mule: steel flat bar ~3×20 mm (hardware store); round grooved head = TAMU lathe job later | https://www.amazon.com/s?k=steel+flat+bar+1%2F8+x+3%2F4 | 1 | 6 |
| 22 | **Spring assortment** | compression spring kit covering Ø9×~15 (ejector) — pin preload comes from the solenoid's own return spring | https://www.amazon.com/s?k=small+compression+spring+assortment+kit | kit | 9 |
| 23 | **JST connectors** | JST-XH 2/3/4-pin kit + one JST-PH 2.0 pigtail (protected 103450s ship PH) | https://www.amazon.com/s?k=JST+XH+connector+kit ; https://www.amazon.com/s?k=JST+PH+2.0+pigtail | kit | 10 |
| 24 | **Hookup wire** | 22 AWG silicone stranded red/black (RoomCleaner never bought it) | https://www.amazon.com/s?k=22awg+silicone+wire+red+black | 1 | 9 |

## P4 — Weatherproofing + finish (add to any later order)

| # | Item | Spec / search term | Link | Qty | ~$ |
|---|---|---|---|---|---|
| 25 | **Sealed wake button** | 12 mm waterproof momentary panel-mount (kit tactiles are bench-only) | https://www.amazon.com/s?k=12mm+waterproof+momentary+push+button | 2 | 8 |
| 26 | **EPDM foam tape** | 1 mm thick × ~10 mm wide adhesive strip (lid-rim gasket) | https://www.amazon.com/s?k=EPDM+foam+tape+1mm | 1 | 6 |
| 27 | **Clear RTV silicone** | small tube (LED potting + seams) | https://www.amazon.com/s?k=clear+RTV+silicone+sealant+small+tube | 1 | 5 |
| 28 | **Silicone grease** | small tube (plunger + pin channel anti-freeze film) | https://www.amazon.com/s?k=silicone+grease+dielectric+small | 1 | 4 |
| 29 | NTAG213 stickers (optional) | phone-case sticker keys — only alongside a PN532 | https://www.amazon.com/s?k=NTAG213+nfc+stickers | pk | 6 |

**New spend: ~$185–210** (P1 ≈ $72 · P2 ≈ $106 · P3 ≈ $76 · P4 ≈ $29, before the
deferred PN532). The RC522 kit + ELEGOO kit + bench PSU rig save roughly $70–90 vs
buying the BOM cold.
