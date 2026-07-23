# Assembly Plan & DFM/DFA Audit

> **v0.8 FASTENER STANDARD (supersedes the per-step screw callouts below):** every
> threaded joint is now an **M3 machine screw into an M3 brass heat-set insert** — press
> **all** inserts on the open bench before assembly. Two carve-outs, both forced by an
> external part: the **solenoid** stays **M2.5** (its own tabs are drilled M2.5), and the
> **PN532** stays **M3 nylon** into printed bosses (brass at the antenna corners kills
> read range). The closure screw is now a **short M3 heat-set** (Ø4.0×L3.8) in the shallow
> door pad; the bay screws are **M3 socket-cap into inserts** (were M4 self-tap). Insert
> tally: **~19 full M3 (Ø4.1×6.5) + 3 short M3 (Ø4.0×L3.8) + 2 M2.5 (Ø3.6×4.5)**; PN532 = 4 nylon, no insert.
>
> **v0.7 FINAL: the authoritative bench build sequence now lives in [BUILD.md](BUILD.md)**
> (4-lens audited: BOM mapping, harness, build-order simulation, bring-up checkpoints).
> Key corrections vs the tables below: the Nano edge-stands in the POD wall recess
> (nano_clamp on crown bosses - reflash = lid off, NOT the tray); ALL driver
> electronics sit on a 42×10.7 card **on the pedestal-cart's −Y platform (v0.8.2 Option C —
> short M3 heat-sets in the cart bosses, driver+solenoid+cart pull as one module)**; the
> bay perf rack is deleted (the spine carries only 2 conductors); MT3608 mounts BEFORE the
> solenoid (0.3mm clearance); liners install AFTER hinge drilling (swarf); the
> spine is wired AFTER the bay is bolted (window halves align only then); the
> ejector spring drops into the bore AFTER the consumer closure screw.
>
> **v0.8.3 weatherproofing steps (do these at the marked points in BUILD.md):**
> 1. Before the lid goes on (BUILD step 16): lay **1 mm EPDM foam tape** (BOM 30a) on the
>    pod rim, holes punched at the 4 screw bosses — the 4 lid screws compress it into the
>    water stop behind the cosmetic reveal gap.
> 2. When the LEDs go in: seat them from below, then pot the domes + the two Ø3.3 lid
>    holes with **clear RTV silicone** (BOM 30b). Fill from the top recess; wipe flush.
> 3. At solenoid install: film of **silicone grease** (BOM 30c) on the plunger and the pin
>    channel mouth — the latch-bore weep drains the rain, the grease keeps the residue from
>    freezing the pin.
> 4. After charging, always press the **`usb_plug`** (TPU, printed) back into the bay USB
>    port — it's the only thing between wheel spray and the TP4056.
> 5. Do NOT plug the two small weep holes (latch-bore floor, drum-ring bottom): they are
>    drains, not defects.

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
- Battery/cell reachable by removing the hatch/tray's 2 screws — no soldering, no glue,
  and the service loop in the leads means dropping the tray can't strain the wiring.
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

### v0.7 addendum — tray cartridges
Steps 4-6 refine to: (i) screw the `nano_sled` and `shelf_cart` to the tray (4x M3x10
ST flat from the external face); (ii) zip the Nano to the sled (pins TRIMMED flush),
seat the cut 40x29 perfboard on the shelf pegs; (iii) TP4056 slides -X under the bay
cradle noses until the USB-C registers in the wall port; (iv) the cell stands on edge
against the +Y wall. Reflash = drop the tray, plug in on the bench - no in-situ USB
access needed.

## 4. Security note recorded during the audit

v0.6 status (full rewrite — see DESIGN.md §7 "Security analysis — honest version" for
the complete analysis; a judge finding forced that section's rewrite because its old
"every other seam is captive" claim is false): four fastener groups are externally
removable on the locked, closed bike — the lid (4× M3), the hatch/tray (2× M3), the
spine cover (2× M3), and the hinge cap (1× M3). Consequences:

- Removing the hatch or the spine cover exposes the solenoid's drive leads — a 5V
  source is a non-destructive path to actuate the latch without going through the app.
- Removing the hinge cap lets the rod slide out the front (the O6 head cannot pass the O4.2 bore, so it exits head-first from its front counterbore); the housing detaches from the
  clamp. The bike stays cable-tethered (the clamshell is still closed around the tube),
  but the lock body itself comes off.

This is the same class of finding as the v0.5-accepted lid→plunger exposure and is
accepted on the same basis: this is a prototype, and the owner has signed off on
"reasonable outward screws OK for now." It is not accepted silently — it is the
documented state, not an oversight.

Production mitigation list (now covering all four seams, not just the lid): one-way or
security-drive fastener heads, or staking, on the lid, hatch, spine cover, and hinge
cap; potted or sleeved solenoid drive leads so they can't be tapped from outside;
hidden lid fastening (already on the CAD TODO list — same item as before, now with a
concrete reason and three siblings).

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

## 8. v0.6 "no-glue rebuild" delta (current CAD)

A full defect sweep (D1–D12, machine-confirmed by the new `--gaps` min-distance probe
and an extended `--sweep` whose moving set is now door+liner_left against *all* other
parts — the old body+bay+lid-only sweep is what let D10 hide) found that most of the
housing's fastened joints either couldn't be assembled at all or weren't fastened
correctly. The kinematic rules from §6.6 are untouched; the sequence above (§1) is the
rewrite. What actually moved, in build order:

- **Step 1 grew from one insert to nine.** v0.5 needed a single M4 insert for the
  closure; v0.6 needs 6× M3 + 2× M2.5 + 1× M4-short, because D3 (lid), D4 (spool
  cover), D6 (hatch), and D12 (pedestal/solenoid) all turned out to be missing- or
  wrong-fastener defects, not just missing-hole ones. Doing all of them in one bench
  pass, before anything else is bolted on, is the only way to keep the build linear.
- **The closure screw path is fixed, not just re-specified.** D1 and D2 meant the
  v0.5 "ONE hidden M4" in step 13 physically could not be driven — the clearance hole
  hit the wrong z-segment and the insert pocket punched through the flange. The pad
  geometry, insert, and screw are new; step 13's *description* is unchanged because
  the consumer-facing action never changed, only the mechanism it now correctly drives.
- **Pedestal and solenoid split into two verified operations.** D12 found the pedestal
  attach holes and the solenoid mounting holes only 1 mm apart (68/94 vs. 69/93) —
  effectively merged into one hole. The attach pads moved to 76/86, giving each a clear
  ~7 mm to its nearest solenoid hole, and installing the solenoid's own inserts now
  waits on a VERIFY of the real unit's hole spacing.
- **The battery mount changed shape, not just fastening.** D11: the old flat-frame
  LiPo pocket and the TP4056 block occupied the same floor real estate — the cell
  could never have fit as drawn. It now stands on edge against a wall it can't collide
  with.
- **The hatch became a real, correctly-fastened service joint.** D6: it used to cover
  a solid floor with no pilots and heads that stood proud outside. It's now a
  removable component tray, with heads flush on the external face, threading into the
  inserts placed in step 1.
- **The spine went from a sealed, blind-fished conduit to an open lay-in raceway with
  a screwed cover** (owner request) — step 7 no longer starts with "fish it with a
  pull wire."
- **The hinge is one rod, not two glued-pin joints — this is the biggest sequence
  change.** D7 (glued plugs, no axial retention) is gone. Step 12 used to be
  glue-and-wait at each end face; it's now a single measured drill-through (Ø4.2,
  8 segments ≤14 mm, pick the bit off the actual rod OD) followed by a tail-first
  insertion and a *screwed* cap with a thermally-sized float. No adhesive appears
  anywhere in the v0.6 sequence.
- **PN532 mounting lost its foam tape.** Nylon screws into drop-bosses (steel would
  sit inside the antenna loop) plus a captive, non-adhesive foam pad.
- **Step 13's text is unchanged** — one M4×8, consumer-only — but see the closure-path
  point above: in v0.5 that step described a screw that could not reach its insert.

Net effect: 12 printed parts (was 13 — the two glued end plugs are deleted) + 1 lathe
rod, zero glued joints, and every removable fastener now has somewhere real to bite.
The security cost of that serviceability is in §4 and DESIGN.md §7.
