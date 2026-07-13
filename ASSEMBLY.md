# Assembly Plan & DFM/DFA Audit

Design-level review of whether the v0.2 design can actually be put together easily.
Verdict: **sound skeleton, three real gaps** (§3) to close in the CAD before the big
prints. Nothing here changes the electronics or the mechanism concept.

## 1. Intended assembly sequence

| Step | Operation | Access | Fasteners |
|---|---|---|---|
| 1 | Print 7 parts; install brass insert in left screw pad | open bench | 1× M4 insert |
| 2 | Solenoid onto pedestal | from above, open pod | 2× M2.5 self-tap |
| 3 | Plunger nose = locking pin (see §3.1) | — | none |
| 4 | Battery holder into saddles, zip-tie through pass-unders | from above | zip ties |
| 5 | TP4056 + MT3608 into card-edge pockets (§3.3); USB-C self-aligns to rear slot | from above | none (pockets) |
| 6 | Nano under driver tray; perfboard onto tray, zip-tied | slides from front / above | zip ties |
| 7 | Harness: JST runs laid into the two raceways, loop on strain posts | from above | clips |
| 8 | PN532 + button + LEDs onto lid; plug lid's JST service loop | open bench | posts / panel nut |
| 9 | Lid on | from above | 4× M3 self-tap |
| 10 | Donor spool into drum, cable out the snout, wind preload | open drum face | — |
| 11 | Spool cover into rabbet | from the side | 3× M3 self-tap |
| 12 | Hinge: mate halves, insert TWO short pins from the end faces, glue end plugs (§3.2) | end faces | 2× Ø3 pins |
| 13 | On the bike: close clamshell, lip engages, ONE M4 down the latch bore (magnet-tip 2.5 mm hex) | top | 1× M4 |

Every operation is top-down or open-face — no blind assembly except step 13, which is
one screw and is the security feature working as intended.

## 2. What already passes DFA

- Single assembly direction (top-down into the open pod); no simultaneous-hold operations.
- Modules connect by JST — any board swaps without soldering; lid tethers by a plug.
- Battery/cell replaceable without tools (leaf-spring holder) once the lid is off.
- Low fastener variety: M4 ×1, M3 ×7, M2.5 ×2, plus two hinge pins.
- The one awkward fastener (bore-bottom M4) is deliberate — it's the tamper defense.

## 3. Gaps found — CAD changes queued

1. **Plunger-as-pin (deletes the worst subassembly).** The separate Ø4 pin needed a
   coupling to the plunger, a spring seat, and a retaining clip inside a cramped channel —
   all unspecified. Change: the JF-0530B's own Ø6 plunger becomes the locking pin: file a
   45° ramp on its nose, widen the boss channel to Ø6.4 and the cable-head groove to
   ~6.5 mm, use the solenoid's included return spring. Zero added parts, self-aligning.
   *(Fallback if measured plunger force disappoints: revert to the separate-pin design,
   but then the coupling must be fully drawn before printing.)*
2. **Two short hinge pins, not one long one.** A 150 mm pin threaded through ~10
   interleaved knuckles plus the spool cover can't be aligned by hand. Change: ~55 mm
   pins inserted from each end face (knuckle spans already leave the middle empty),
   entry holes capped with glued printed plugs — which also hides the pin ends from view
   and from tampering.
3. **Card-edge pockets for TP4056 and MT3608.** Both boards currently have no mounts, and
   the TP4056's USB-C port must land flush in the rear-wall slot. Printed slide-in
   pockets fix retention and port alignment in one feature. Also: 4 corner posts (or clip
   tabs) for the PN532 on the lid underside; side rails + foam pad for the Nano.
4. **Fastener standardization:** all M3 = self-tap into 2.6 mm pilots (drop the drum-rim
   heat-set inserts); heat-set stays only for the M4 closure.
5. **Build-guide notes:** magnet-tip long hex key for the bore screw; thread the cable
   before winding spring preload.

## 4. Security note recorded during the audit

With the v1 lid held by 4 exposed M3s, removing the lid exposes the plunger — it can be
retracted by hand, releasing the cable. On the printed prototype this is accepted (the
housing itself is plastic and cuttable; the prototype is a function model, per
DESIGN.md §6.2). The steel version must use the hidden lid fastening already on the CAD
TODO list — this is the same item, now with the concrete reason.

## 5. Print plan (unchanged by this audit)

- `shell_right` is deliberately one integral part (pod + drum + latch) — screws would be
  attack points. Cost: it's the long print (~20 h) with supports under the drum. Accepted.
- `shell_left` prints split-face down, minimal support; `lid` prints top-face down on a
  smooth sheet (window skin and NFC ring form the first layers); liner/shim in TPU, fins
  vertical.
