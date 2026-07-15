# Assembly Plan & DFM/DFA Audit

Design-level review of whether the design can actually be put together easily.
Verdict at v0.2: sound skeleton, three real gaps. **v0.3 (the CadQuery restructure)
implements every fix in §3** plus the modular split: separate drum module bolted from
inside the bore, and all interior furniture as pad-mounted cartridges.

## 1. Intended assembly sequence (v0.6)

Part set: 12 printed parts + 1 lathe-turned hinge rod (13 items; `end_plug` ×2 is
deleted — no more glued joints anywhere in the build). New parts vs. v0.5: `hinge_rod`,
`hinge_cap`, `spine_cover`.

| Step | Operation | Access | Fasteners |
|---|---|---|---|
| 1 | Print all 12 parts; lathe the hinge rod (one op from Ø6 303 stainless bar). Install **all** heat-set inserts on the open bench: 4× M3 into the lid's pod-rim bosses (driven from the open pod top, before the lid goes on); 2× M3 into the bay module's TP4056 block and drum web (driven from below, before the hatch/tray goes on); 2× M2.5 into the pedestal cartridge's tower top (for the solenoid); 1× short M4 into the door's closure pad, from the pad's **top** face with the door open and flange-up on the bench | open bench, various faces per insert | 6× M3 (Ø4.1×6.5) + 2× M2.5 (Ø3.6×4.5) + 1× M4-short (Ø5.6×L3, VERIFY sourcing) heat-sets — 9 total |
| 2 | Bolt the pedestal cartridge onto the body's pod-rim pads: screws drive down through the tower's Ø6.5 access holes, so heads land on the pad boss and end up hidden once the solenoid covers them | from above, through the tower, open pod | 2× M3 pan self-tap |
| 2b | Solenoid onto the pedestal tower. **VERIFY the real unit's mounting-hole spacing before installing the M2.5 inserts** — `sol_hole_dx` is drawn at 24 mm; if the measured unit differs, reprint the pedestal cartridge (a minutes-long print, not a redesign) rather than force the fit. Bench-test the latch action before moving on | open bench or in place | 2× M2.5×8 machine, into brass heat-sets |
| 3 | Plunger nose = locking pin (see §3.1, unchanged) | — | none |
| 4 | LiPo cell into the bay: it stands **on edge** against the +Y wall — the block face, one retaining rail, and the wall bound it. No zip-tie pass-unders anymore | from above, open bay | — |
| 5 | TP4056 into its front-wall slot; USB-C self-aligns to the port | from above | none (pocket) |
| 6 | Hatch-tray build and close: zip the Nano (mounted **diagonally** — the service window is 40.5×29.5), MT3608, and perfboard to the tray's anchor grid. **Leave a documented service loop in the cell leads** before closing — dropping the tray for service must never strain the battery wiring. Close the tray onto the bay, countersunk on the **external** face | slides in from the front, then closes from outside | 2× M3 machine flat, into brass heat-sets from step 1 |
| 7 | Harness: lay the wire run **into** the open wire-spine raceway (it's an open lay-in channel now, not a sealed conduit you fish blind) and screw the spine cover down over it. Bay↔pod feed-hole path is unchanged | from above, open raceway | 2× M3 self-tap flat, countersunk |
| 8 | PN532 into the lid pocket: nylon screws through the board's corner holes into the lid's drop-bosses (no steel near the antenna loop, which wraps the full board perimeter), plus a captive 1 mm foam pad over the antenna face — pressure-fit, **no adhesive**. If a clone board lacks the corner holes, print the corner-clip fallback onto the same bosses. Then button + LEDs; plug the lid's JST service loop | open bench | 4× M2.5×8 NYLON machine |
| 9 | Lid on | from above | 4× M3 machine flat, into rim heat-sets from step 1 |
| 10 | Donor spool into drum module, cable out the snout, wind preload | open bench (module off the bike!) | — |
| 10b | Spool cover on, re-clocked so one screw sits on the vertical axis (90/210/330°) | open bench | 3× M3 self-tap flat, countersunk |
| 11 | Bolt the loaded bay module (drum + spool + electronics + tray) to the body — screws drop through the clamp bore wall | from inside the open clamp | 4× M4 pan self-tap |
| 12 | Hinge: door closed and clamped against the body, **drill** the Ø4.2 finished bore through all knuckles — 8 segments, each ≤14 mm, no deep-hole drilling. Measure the actual rod OD first and pick a drill for 0.15–0.2 mm diametral clearance. Deburr all 16 mouths. Insert the hinge rod **tail-first from the front**, seat the integral head in its front counterbore, fit the hinge cap over the tail (0.5 mm axial float) and drive its screw into the shell end face. **No glue anywhere in this joint** | door closed, end faces + through-bore | 1× M3 self-tap flat, countersunk |
| 13 | On the bike: open door, press onto the down tube, swing shut, lip engages, ONE M4 down the latch bore (magnet-tip 2.5 mm hex) | top | 1× M4×8 low-profile socket + washer |

Steps 1–12 are the factory build; step 13 is the only thing the consumer ever does.
Steps 1–11 are top-down or open-face bench operations. Step 12 is not blind — it's a
through-drill on an assembled, clamped pair of halves with full visual/tactile access
at both ends — but it is a machining step, not a snap-together one, and it's the last
factory operation before the unit ships. Step 13 remains the only genuinely blind
fastener (one screw, driven down a bore you can't see the bottom of) and is the
security feature working as intended — see §4 and DESIGN.md §7 for what "intended"
now honestly covers.

## 2. What already passes DFA

- Single assembly direction (top-down into the open pod); no simultaneous-hold operations.
- Modules connect by JST — any board swaps without soldering; lid tethers by a plug.
- Battery/cell replaceable without tools once the hatch/tray is off.
- Fastener variety, by BOM (v0.6): M4 ×5 (1 closure + 4 bay, pan self-tap), M3 ×14
  (6 machine-flat into heat-sets: lid 4 + hatch 2; 6 self-tap flat: spool 3 + spine 2 +
  hinge cap 1; 2 pan self-tap: pedestal), M2.5 ×6 (2 machine into heat-sets: solenoid;
  4 nylon machine: PN532), plus the one-piece hinge rod and its screwed cap. Every
  joint is a heat-set-and-machine-screw or a direct self-tap — no glue anywhere.
- The one awkward fastener (bore-bottom M4) is deliberate — it's the tamper defense,
  and as of v0.6 it actually reaches its insert (D1/D2 fixed the broken screw path
  and insert pocket — see §8).

## 3. Gaps found — ✅ all implemented in CAD v0.3 (CadQuery)

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

## 5. Print plan (v0.3)

- The latch boss stays integral to `shell_right` (cable load path + hidden closure screw),
  but the drum is now its own zero-support module bolted from inside the bore — the shell
  print drops from ~20 h with a support forest to a clean pod-up print.
- Full per-part orientation/material table in `cad/README.md`. Cartridges are minutes-long
  prints, which is the point: all four VERIFY dimensions live in them.

## 6. v0.4 "slim top" delta (current CAD)

The sequence above still holds with these substitutions:

- Steps 4–6 happen **in the bottom bay on the bench**: LiPo into its printed frame
  (rear tunnel), TP4056 into its slot with the USB-C landing in the front-wall port,
  Nano/MT3608/perfboard zip-tied to the floor anchor grids. Tunnels close with two
  copies of the shared `bay_hatch` part (4× M3 each).
- The harness runs front↔rear through the bay's corner duct, then up the **wire spine**
  on the right shell into the pod (fish it with a pull wire before closing hatches).
- Step 11 bolts the whole loaded bay (drum + electronics) to the right shell — same
  4× M4 from inside the open clamp.
- The top pod now receives only the pedestal cartridge + solenoid; PN532/button/LEDs
  stay on the lid as before.
- Spool service = unbolt the bay (the cover can't slide out past the rear tunnel
  in place). Cam-lock backstop deleted (DESIGN.md §8 note).

## 7. v0.5 "spine + door" delta (current CAD) — consumer install achieved

Assembly review of v0.4 in SolidWorks found it could not be installed (pod/bay blocked
both the door swing and the tube entry). v0.5 restructures around three kinematic rules
(DESIGN.md §6.6) and adds **automated verification**: every `--sweep` run rotates the
door 0–110° against body+bay+lid and asserts zero interference, plus an entry-corridor
check on every build. Current status: **both PASS at 0.00 mm³.**

Changes to the sequence: the factory (you) still bench-builds everything; the CONSUMER
only ever does step 13 (open door, close on tube, one screw). Parts renamed:
`shell_right` → `body`, `shell_left` → `door`. The bay is a right-side brick (y 7–48)
with the slim Y-axis drum (Ø68×32) behind it; one hatch; spool cover faces outboard
(spool serviceable in place again). Latch line moved to y +10; the door carries flange
+ lip that engage through swept pockets.
