# CNC_CASING.md — the machined-casing redesign (concept + DFM contract)

Goal: a casing **designed for CNC from the first sketch** — fewer parts, simpler parts,
simpler assembly. The printed v0.8.3 remains the functional-prototype lineage; DESIGN §6.9
scored machining THAT geometry at 4 setups + a 4th-axis rotary, which is exactly what this
redesign deletes.

> **Chosen concept (owner, 2026-09): "dumb chassis + bolt-on boxes."** Two simple tube
> halves are the chassis; everything with precision or electronics lives in small boxes
> that bolt onto one half **from the inside of the bore outward**, so every attachment
> screw is buried under the clamped bike tube + liner. The TPU liner still slips in.
> §2A below is the contract for this concept; §2B (two integrated billets) is kept as the
> rejected alternative for the record.

## 1. The one insight that drives everything

FDM and CNC have opposite cost functions. The printed design spends free complexity
everywhere: organic drafted pod fused to a cylinder, 8 interleaved hinge knuckles,
swept-arc pockets, bosses and brackets grown mid-air, 27 heat-set inserts because plastic
can't hold threads. **In metal, every one of those is money — and most exist only because
of printing or the hinge.** The CNC casing deletes the *reasons*, not just the features.

## 2A. Chosen architecture — tube-half chassis + inside-out bolted attachments

### The parts
| # | Part | Stock / process | Setups | What it carries |
|---|---|---|---|---|
| C1, C2 | **Tube halves** (left / right, **vertical parting plane**) | **2.5" OD × 3/16" wall 6061 tube (Ø63.5 × 4.76 → ID ≈54)**, saw-cut 150, split lengthwise, pair line-bored to Ø54.0 | 1–2 each: drill + inside-COUNTERBORE the attachment holes (vertical crown rows + horizontal skirt rows), mill the rear liner lip. C1 gets the A1 rows (x 25/75/125, y +6 / z ±8) and the A3 rows (x 35/105, y +10 / z −8); C2 gets 2+2 holes for its two blocks | The clamp. Nothing precise lives here — **no hook, no tongue, no hinge is cut into the tube** |
| A1 | **Top box** (latch + electronics) | small 6061 billet | 2 (pocket side, latch side) | Ø11 receiver bore + Ø6.6 plunger channel, electronics cavity 124 × 44 × 24, tapped holes for lid + chassis screws, closure-block pocket under its −y overhang |
| A2 | **Lid plate** | 5 mm plate | 2 (through features; underside recess for the insert) | RF window through-cutout, button, LEDs, 4 corner screws |
| A5 | **Window insert** | opaque printed / PC | — | fills the cutout flush; its flange sits in the lid's underside recess and the box wall clamps it (RTV bead) |
| A3 | **Spool puck + cradle** (spool + hinge knuckles) | small billet | 3 (pocket side, bottom, knuckle side) | a saddle cradle along the tube (chassis screws, hinge lugs) with a round **Ø62 puck** hanging off it: Ø51 vertical-axis pocket for the spool cartridge, **steel-bushed cable exit**, **two Ø11 hinge lugs** with the blind pin bore |
| A4 | **Puck cover** | Ø62 × 3 mm disc | 1 | closes the spool pocket (cartridge + power spring load from below), 4× M3 in the puck wall — external screws, but see "Security" |
| B | **Closure block** | 20 × 12 × ~7.5 steel/6061 | 1 | on C2 under A1 (2× M3 from inside C2); tapped for the closure screw |
| H | **Hinge block** | 40 × 14 × ~16, one Ø11 lug | 1 | on C2 under A3 (2× M3 from inside C2); its lug sits between A3's two lugs on the pin |
| — | **Hinge pin** | Ø5 h6 dowel × 36 | — | steel; entered through lug 1, dead-ends in lug 2's blind bore, entry plugged |
| — | Spool cartridge, pedestal cart, glands | printed | — | interior furniture stays plastic (hybrid) |
| — | TPU finned liner + shim | printed TPU (unchanged) | — | slips into the smooth Ø54 bore; retained by the clamp sandwich + the rear lip |
| — | Cable head | lathe (existing BOM drawing) | 1 | unchanged |

Twelve pieces, but two are saw-cut tube, three are plates/inserts, two are small blocks and
one is a dowel — **the real machining is two small boxes.**

### How C2 goes on (the hinge, and why it lives where it does)
The owner's requirement: a consumer hinges the clamshell open, drops it on the down tube,
swings it shut, and drives ONE screw that is only reachable through the latch bore when
the bike is unlocked. The first two models both failed that in different ways (a straight
tongue "hinge" that can't rotate and sweeps into the spool box; a hinge-less slide-and-lift
install). Rev 3 is a real hinge, placed by geometry rather than habit:

- **Pin axis** along the tube, at y −1 / z −38: 1 mm onto the C2 side of the seam, 6 mm
  under the tube. Ø5 dowel, Ø11 knuckles (3 mm wall).
- **Knuckles:** two 8 mm lugs on the spool box A3 (x 58–66 and 90–98), one 23.4 mm lug on
  the hinge block bolted to C2 from inside. All three are round about the pin, so nothing
  near the pin can ever touch during a swing.
- **Why the pin is on the C2 side:** every non-round point of C2's hardware then has
  y ≤ pin-y, and rotation about the pin can only move those points *away* from C1's side.
  The spool box body sits entirely at y ≥ +0.5, so a **90° swing never enters it** — the
  problem that killed the tongue hinge is gone by construction, not by clearance.
- **Why the pin is 1 mm past the seam and not further:** the closure block's +y face is
  at y −1; with the pin at y −1 no point of the block rises as the swing starts (a point
  at +y of the pin arcs *up* first), so the block leaves the A1 roof cleanly.
- **Rim swell:** because the pin is 6 mm under the tube, C2's rim arcs *outward* during the
  first 12° of swing (r 33.57 at 11°). A1's overhang underside over C2 is relieved to R34.0.
- **What the swing buys:** with C2 at 90° the whole clamp half lies below z −38; a Ø46
  down tube slides sideways into C1's half-bore with 15 mm to spare (gated).
- **Closure:** swing shut, the closure block enters A1's pocket through its open −y side,
  one M3 low-head down the latch bore clamps the block to the pocket roof. Liner preload
  pushing C2 away is a moment about the pin, resisted by that screw in shear (~2 kN for
  an M3 8.8) — the same joint the printed v0.8 had. Everything else is geometry.
- **Pin security:** the bore is drilled through lug 1 from its outer face and stops 2 mm
  short of lug 2's outer face (blind). The pin is 36 long, seated against the blind end,
  and a Ø5 press-fit plug fills the 2 mm behind it. Nothing can be punched *out* (blind),
  nothing can be punched *in* (already seated), and there is no pin end to grab — the
  same logic as a peened security-hinge pin, without the peening.

The gates for this: `--gates` rotates C2 + both blocks about the pin at 19 angles from 1°
to 90° against C1/A1/A2/A3/A4/pin (max overlap 0.00 mm³), slides a Ø46 cylinder from
70 mm out into C1's bore with C2 at 90° (0.00 mm³), and proves retention (a 2 mm pull on
C2 overlaps the pin by 221 mm³; the block seats on the roof).

### The problems this concept has to solve — and the answers
1. **Where does the self-guarding closure screw go?** Vertical parting plane, top box
   straddling the seam. A1 bolts inside-out to C1; A1's latch bore sits over the seam; the
   consumer screw (**M3 low-head, owner's call — it threads the steel block**) goes down the
   bore, through A1's 1.5 mm floor, into the closure block on C2. Locked head covers it.
2. **Round chassis meets flat box.** NOT flat lands — a 50-wide flat on a Ø63.5 tube is
   12 mm deep (through the wall). Instead the box underside is a **concave saddle**
   (R31.75 + 0.25) and its +y wall continues as a **skirt** down the tube's side — one CAM
   surface op on the box, nothing milled off the tube. Saddle + skirt also grips ~90° of
   the tube: much stiffer than a footprint on a flat.
3. **Screw heads under the liner.** Two axis-aligned rows per box, both pure 3-axis:
   a **vertical crown row** and a **horizontal skirt row (z=±8)**, M3 low-head cap
   screws in **Ø6.2 counterbores cut from INSIDE the bore** (a counterbore seats square on a
   curved wall; a countersink would not). Wall left under the floors: 7.3 / 2.8 mm (gated).
   The liner rides a bore with ten small recesses — nothing protrudes.
4. **Clamping without tie bolts.** Tie bolts across the bottom seam would have to be driven
   from outside (attacker-reachable) or from inside the bore before the frame is in
   (impossible for the half that goes on last). So: **hinge pin at the bottom, one guarded
   screw at the top** — see "How C2 goes on".
5. **Spool box loads from below, closed by A4.** The cartridge drops into the Ø63 pocket
   from the bottom face and a 3 mm plate closes it. A4's four screws are external — and
   that is *not* a security hole: the cable's inner end carries a swaged ball stop bigger
   than the Ø7 bushed exit, so with the spool removed the locked loop still cannot be freed.
   The hinge pin is not reachable from the pocket either (its bore never enters it).
6. **Spool size and the puck shape (owner: "why is the lower box so bulky?").** 5 ft of
   **3 mm 7×7 wire, PVC-coated to Ø4**, on a Ø32 core (10.7× wire Ø) in a 24-wide cartridge
   = 6 wraps/layer, 2 layers (1.51 m) → outer Ø48, pocket Ø51. The power spring lives
   INSIDE the hub as in every retractable reel. The pocket starts 3 mm past the knuckle zone
   (y 7.5..58.5). A3 is no longer a block: a **cradle** along the tube (x 40..100, y 0.5..36,
   down to z −44) carries the chassis screws, the hinge lugs and the cable exit, and a
   **round Ø62 puck** (5.5 mm wall, cover screws in the wall) hangs off it around the pocket.
   The skirt is a 12 mm rib (y 32..44), not the full box width. 85 cm³ instead of 202;
   the puck reaches 32 mm past the tube side and 31 mm below it. Overall height 133 mm.
7. **RF window.** A metal lid within a few mm of the reader's antenna loop detunes it, so
   the cutout stays antenna-size (45.2 × 43 = PN532 footprint + 1). What the owner wanted
   ("nothing showing") is satisfied by the insert being **opaque** — RF does not care.
   Stage 1's PETG lid is RF-transparent anyway; the cutout exists so the machined Stage 2
   lid is a drop-in. The window sits at x 20..65; the latch bore at x 78 and the 44-long
   solenoid cart at x 88..132 follow it along the box.

### Security consequence (a real upgrade)
Every attachment fastener is under the clamped bike tube. DESIGN §7's honest weakness —
"four service joints reachable on the locked bike" — is structurally gone. Only the
closure screw (covered by the cable head), the bushed cable exit, the A4 cover (harmless
because of the ball stop) and the plugged, blind hinge pin face the attacker.

### Staged path (why this concept also wins on schedule)
The tube halves are the parts that NEED metal (clamp strength, anti-cut); the boxes are
what printers do best. **Stage 1: everything printed in PETG** — the model's Ø2.5 tapped
pilots double as PETG self-tap pilots for M3, every part has a flat print face (boxes on
their lids/covers, halves on their seam faces, blocks on their tops), and the hinge pin is
a Ø5 steel rod from the hardware store. **Stage 1b: aluminum tube halves + printed
boxes.** **Stage 2:** machine A1/A3 as drop-in swaps; the chassis and hole patterns never
change.

### Assembly
Bench: bolt A1 + A3 to C1 from inside (M3 low-head in the counterbores) → electronics
into A1, window insert under the lid, lid on → spool cartridge into A3 from below, A4 on →
closure block + hinge block onto C2 from inside → hang C2's lug between A3's lugs, drive
the pin home, press the plug. The lock is now one hinged clamshell. On the bike: liner
halves in, open C2, set C1 on the down tube, swing shut, 1× closure screw down the latch
bore. **One fastener action for the consumer install.**

## 2B. Rejected alternative — two integrated billets (kept for the record)
### Move 1 — Delete the hinge. Two-bolt clamshell instead.
The door-swing is the single largest complexity source: 8 knuckles, the lathe rod, the
tail cap, AND the swept closure pockets that force a 4th axis (a rigid mill can't cut a
true swept pocket — §6.9's one hard exception). A **lift-on clamp half held by 2× M5
socket screws** (reached only from inside the open clamshell — same anti-tamper logic as
the bay bolts) replaces all of it. Straight insertion → every pocket becomes prismatic →
**the entire assembly is 3-axis**. The self-guarding closure screw stays as the third,
consumer-facing fastener, exactly as designed. Install: hold half, run 2 bolts, close,
1 screw. (The swing, sweep gates, hinge drilling op, rod, and cap all cease to exist.)

### Move 2 — Bore the tube hole like an engine main: at the parting line, halves bolted.
Both halves are fundamentally a Ø54 bore split at a plane. Machine each half prismatic,
**bolt the pair together, then bore/ream the Ø54 in one operation through both**. Perfectly
round, perfectly matched halves, zero 3D-sculpting of half-cylinders. This is century-old
practice (line-boring bearing caps) and it's the second reason the parts stay simple.
The latch receiver Ø11 and the plunger channel Ø6.5 get drilled/reamed the same way —
real H7 fits instead of printed holes.

### Move 3 — Collapse the bay into the main billet + one flat cover plate.
The printed bay_module (4 setups, its own bolts, nesting hatch) becomes a **pocket milled
into the main billet's underside** closed by a **flat 3 mm plate** (waterjet/laser-cut —
SendCutSend territory — with a machined O-ring groove option). Deletes an entire part
family; the plate is the new hatch, gasketed, 4 tapped screws.

### Move 4 — Hybrid interior: metal is the security envelope, plastic is the furniture.
Do NOT machine brackets. The pedestal cart, spool cartridge, and wire management stay
**3D-printed parts living inside the machined shell** — they hold electronics, not
attackers. This keeps machined part count at ~4 and means electronics packaging keeps
iterating at printer speed even after the shell is metal. The spool + spring stay a
printed cartridge dropped into the bay pocket; only the **cable exit becomes a machined
(steel-bushed) hole** — that's the part an attacker can reach.

### Move 5 — Threads in metal: delete all 27 heat-set inserts.
Every insert becomes a **tapped hole** (free on CNC, stronger than any insert). One tap
size everywhere it can be: M3×0.5, ≥2×D engagement. The insert coupon, pressing session,
displacement reliefs, and collar-wall worries all evaporate. Lid gasket upgrades from
EPDM tape to an **O-ring cord in a machined groove**.

(Moves 2, 4 and 5 above carry into the chosen concept unchanged: line-bore the pair, hybrid interior, tapped holes / no inserts. Move 1 is superseded by the vertical-seam closure lug; Move 3 by the bolt-on bottom box.)

## 3. What carries over UNCHANGED (do not redesign these)

| Kept | Why |
|---|---|
| Latch mechanism (Ø11 receiver, plunger-as-pin, square-flanked groove head, ejector spring, self-guarding screw) | Already designed machining-first (lathe head, reamed bores); the physics is the physics |
| TPU finned liner + shim (Ø32–46 one-size fit) | Compliant part — machining doesn't apply; bore stays Ø54 to keep the liner stack |
| All electronics + wiring plan (Nano, reader, MT3608, TP4056, 103450, driver card) | Casing-independent |
| RF window strategy | **A metal lid is opaque to 13.56 MHz.** The machined lid gets a rectangular window cutout; the polycarbonate/printed window insert seats in the bezel step the v0.7 lid already modeled "so the split is free later" — this is that later |
| Drainage philosophy | Weeps + grease notes port over as drilled holes (cheaper than in plastic) |

## 4. (superseded by §2A part table — retained for the billet alternative)

| # | Part | Stock | Setups | Ops summary |
|---|---|---|---|---|
| M1 | **Main half** (electronics side) | 6061 billet ~160×64×38 | 3 | Top: electronics cavity (one rect pocket, R6 corners), tapped patterns, window/button/LED drills. Bottom: bay pocket + cable-exit. Then the **paired boring op** (Move 2) |
| M2 | **Clamp half** | 6061 billet ~160×64×26 | 2 | Outside face chamfers + 2× M5 counterbores; then paired boring. No cavity — it's solid clamp |
| M3 | **Lid plate** | 6061 plate 5 mm | 1–2 | Window cutout, button + LED holes, screw CS, O-ring groove, bezel step for the RF insert |
| M4 | **Bay cover plate** | 6061 3 mm | 0–1 | Waterjet/laser outline + holes; optional milled gasket groove |
| — | RF window insert | polycarbonate, printed or cut | — | seats in M3's bezel step |
| — | Pedestal cart, spool cartridge, glands | printed (PETG/TPU) | — | interior furniture, Move 4 |
| — | Cable head | lathe (unchanged BOM callout) | 1 | the existing drawing |

Old→new setup ledger: body 4+rotary → **3**; door 3+rotary → **2**; bay 4 → **0
(deleted)**; hinge rod+cap → **deleted**; inserts 27 → **0**. No 4th axis anywhere.

## 5. DFM rulebook (model against these numbers)

- **Internal corner radii ≥ 4 mm** (Ø8 end mill min; prefer R6/Ø12 where the pocket allows)
- **Pocket depth ≤ 4× tool Ø** (electronics cavity ~30 deep → Ø12 tool territory, fine)
- **External edges: chamfer, don't fillet** (one chamfer tool; 3D fillets = ball-mill time)
- **Every hole a standard drill size**; reamed only where a fit demands it (Ø54 bore seat,
  Ø6.5H7 plunger channel, Ø11 receiver)
- **Min wall 2.5 mm** (alu); no feature thinner than 2 mm standing taller than 5×
- **One tap: M3×0.5** everywhere except the 2× M5 clamp bolts
- **Datum discipline:** every feature dimensioned from one corner datum per face;
  the parting plane is datum A for both halves
- **Fixturing:** each half must hold in a plain vise on parallels for every setup —
  no soft jaws until the paired boring op (which uses the assembled pair held on the
  clamp bolts)

## 6. Material + sourcing (recommendation)

**6061-T6 first.** Machines 4–5× cheaper/faster than steel, anodizes, and already moves
the security story from "plastic prototype" to "resists knives, prying, and casual
attack" (an angle grinder defeats every portable lock ever sold, including steel ones —
DESIGN §7's honesty stands). Steel (4140 or 303 per feature) is a later variant of the
SAME geometry if ever justified. Sourcing: M1/M2 are TAMU-shop-friendly 3-axis work
(that's the resume bullet made real), or ~$120–300 each outsourced (PCBWay/Xometry);
M3/M4 plates are SendCutSend-cheap.

## 7. Assembly sequence (the whole point)

1. Bolt A1 and A3 to C1 from inside the bore (M3 low-head cap screws, Ø6.2 counterbores).
2. Screw the loaded pedestal cart + electronics into A1 (tapped holes, no inserts); fit the
   opaque window insert into the lid's underside recess; lid on (gasket, 4× M3).
3. Spool cartridge + power spring into A3 from below; cable through the bushed exit,
   swaged ball stop on the inner end; A4 on (gasket, 4× M3).
4. Closure block + hinge block onto C2 from inside (2× M3 each).
5. Hang C2's lug between A3's lugs, drive the Ø5 pin through lug 1 to the blind end in
   lug 2, press the Ø5 plug flush. The lock is now a hinged clamshell.
6. On the bike: liner halves in, open C2 ~90°, set C1 on the down tube, swing shut,
   1× closure screw down the latch bore. **One consumer fastener action.**

## 8. Decisions (owner answers applied 2026-09-06)

| # | Decision | Status |
|---|---|---|
| D1 | Hinge | **DECIDED: real hinge** (owner): Ø5 pin at y −1 / z −38 along the tube, knuckles on A3 + a hinge block on C2, 90° swing gated. Rev 2's slide-and-lift is retired |
| D2 | Material | 6061-T6 now; steel variant later from the same model |
| D3 | Spool | **DECIDED: vertical-axis printed cartridge, Ø32 core × 24 wide for Ø4 (3 mm wire) coated cable, loads from below (A4); round Ø62 puck on a cradle** |
| D4 | Who machines | TAMU shop for the boxes (manual-3-axis-friendly), SendCutSend for A2/A4 plates |
| D5 | Modeling | `cad/cnc_casing_cq.py` is the model of record until the owner's SolidWorks pass; gates listed in §9 |
| D6 | Tube stock | **DECIDED: 2.5" × 3/16" 6061 (Ø63.5 × 4.76), line-bored Ø54** |
| D7 | Stage 1 | **DECIDED: print everything first (PETG), pilots double as self-tap pilots; CNC-ready geometry throughout** |
| D8 | Closure screw | **DECIDED: M3 for the printed test article** (owner); the metal production casing goes to M4 — `CLR4/TAP4` are the only constants to change |
| D9 | Window | **DECIDED: antenna-size cutout, opaque insert** (RF needs the hole; the owner needs it opaque — both) |
| D10 | Box orientation / height | any, as long as the latch works (owner) — current: A1 24 mm interior, 133 mm overall |
| open | Spool cartridge donor | envelope is a placeholder (Ø48 × 24) until a reel is in hand — pocket Ø/width are single constants |
| open | Electronics placement in A1 | window zone x 20..65 (reader over battery), latch x 78, cart x 88..132, Nano/driver/TP4056/MT3608 in the +y strip — to be modeled as reference bodies next |
| open | Top-joint shear | the closure M3 carries C2's opening moment in shear. Fine for the liner preload; if a pry test on the printed prototype worries you, the upgrade is an M4 closure screw or a Ø4 dowel beside it |

## 9. What verification looks like in this era

`python cad/cnc_casing_cq.py --gates` runs: interference matrix over all 12 parts;
counterbore wall audit (crown 7.30 / skirt 2.83 mm ≥ 2.3); screw-path probes for the A1
rows, the A3 rows and the closure screw (chassis hole = air, box pilot = air); the
**swing gate** (C2 + both blocks rotated about the pin at 19 angles from 1° to 90° against
C1/A1/A2/A3/A4/pin, max overlap must be 0); the **frame-entry gate** (a Ø46 cylinder slid
from 70 mm out into C1's bore with C2 at 90°, 0 overlap); and the **retention gate** (a
2 mm −y pull of C2 must overlap the pin; a 0.2 mm lift of the closure block must overlap
the A1 roof). No insert-collar gate (no inserts). Still to add: an R4 internal corner audit
and the paired-bore alignment stack-up.

## 10. Model status (2026-09-06, rev 3 — hinged)

`cad/cnc_casing_cq.py` builds all 12 parts (C1, C2, closure block, hinge block, hinge pin,
A1 top box, A2 lid, A3 bottom box, A4 cover plate, A5 window insert, liner L/R) as single
solids. `--gates`: 0 clashes, walls PASS, screw paths PASS, swing 0–90° 0.00 mm³ PASS,
Ø46 frame entry PASS, retention PASS. STEP set in `cnc-design/step/`
(+ `cnc_casing_assembly.step`); renders in `renders/cnc/` (`cnc_iso`, `cnc_exploded`,
`cnc_end`, `cnc_section` = slab through the latch / closure block / hinge lug + pin,
`cnc_open` = C2 at 90° with a Ø46 tube entering, `inspect_1..3` = 12-view inspection
sheets). Placeholders: spool cartridge envelope, electronics reference bodies (see §8).
