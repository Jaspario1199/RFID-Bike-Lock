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
| C1, C2 | **Tube halves** (left / right, **vertical parting plane**) | **2.5" OD × 3/16" wall 6061 tube (Ø63.5 × 4.76 → ID ≈54)**, saw-cut 150, split lengthwise, pair line-bored to Ø54.0 | 1–2 each: drill + inside-COUNTERBORE the attachment holes (vertical crown row y=+6 + horizontal skirt row z=±8), mill the bottom-seam hook tongue/groove + rear liner lip; C2 gets the 2 closure-block holes | The clamp. Nothing precise lives here |
| A1 | **Top box** (latch + electronics) | small 6061 billet | 2 (pocket side, latch side) | Ø11 receiver bore + Ø6.5H7 plunger channel (reamed), solenoid + driver + Nano cavity, tapped holes for lid + chassis screws |
| A2 | **Lid plate** | 5 mm plate | 1–2 | RF window cutout + bezel step for the insert, button, LEDs, O-ring groove |
| A3 | **Bottom box** (spool) | small billet or plate box | 2 | pocket for the printed spool cartridge, **steel-bushed cable exit** (the one attacker-reachable hole) |
| ~~A4~~ | ~~Bottom cover plate~~ | — | — | **deleted** — the spool box is top-loaded (see problem 5) |
| — | RF window insert | polycarbonate / printed | — | seats in A2's bezel step (v0.7 lid already modeled this seat) |
| — | Spool cartridge, pedestal cart, glands | printed | — | interior furniture stays plastic (hybrid) |
| — | TPU finned liner + shim | printed TPU (unchanged) | — | slips into the smooth Ø54 bore; retained by the clamp sandwich + an end lip (dovetail keys deleted) |
| — | Cable head | lathe (existing BOM drawing) | 1 | unchanged |

Six machined pieces, but two are saw-cut tube and two are flat plates — **the real
machining is two small boxes.**

### The three problems this concept has to solve — and the answers
1. **Where does the self-guarding closure screw go?** Vertical parting plane, top box
   straddling the seam. A1 bolts inside-out to C1; A1's latch bore sits over the seam;
   the consumer screw (M4 now — it threads a steel block, not plastic) goes down the bore,
   through A1's floor, into the **closure block bolted to C2 from inside** under the box.
   Locked head covers it — unchanged security logic. Clamp preload from the bottom hook
   (problem 4).
2. **Round chassis meets flat box.** NOT flat lands — a 50-wide flat on a Ø63.5 tube is
   12 mm deep (through the wall). Instead the box underside is a **concave saddle**
   (R31.75 + 0.25) and its +y wall continues as a **skirt** down the tube's side — one CAM
   surface op on the box, nothing milled off the tube. Saddle + skirt also grips ~90° of
   the tube: much stiffer than a footprint on a flat.
3. **Screw heads under the liner.** Two axis-aligned rows per box, both pure 3-axis:
   a **vertical crown row (y=+6)** and a **horizontal skirt row (z=±8)**, M3 low-head cap
   screws in **Ø6.2 counterbores cut from INSIDE the bore** (a counterbore seats square on a
   curved wall; a countersink would not). Wall left under the floors: 7.3 / 2.8 mm (gated).
   The liner rides a bore with six small recesses — nothing protrudes.
4. **Clamping without the hinge (and without tie bolts).** The **bottom seam is a
   tongue-and-groove hook** (C1 tongue r28–30.5 × 3 mm crosses the seam into a C2 groove —
   a straight axial mill pass on each half): hook the bottom, swing the top shut, ONE M4
   closure screw down the latch bore into the **closure block** (a small steel block bolted
   to C2 from inside, sitting in a pocket under the box's overhang). Exactly the original
   single-consumer-screw intent; the 2× M5 idea is dropped.
5. **Spool box is top-loaded, so it has no external cover.** The Ø62 cartridge pocket opens
   toward the saddle; the cartridge drops in before the box is bolted under the tube, and
   the clamped bike tube then seals it. Zero attacker-reachable screws anywhere except the
   covered closure screw and the bushed cable exit.

### Security consequence (a real upgrade)
Every attachment fastener is under the clamped bike tube. DESIGN §7's honest weakness —
"four service joints reachable on the locked bike" — is structurally gone. Only the
closure screw (covered by the cable head) and the bushed cable exit face the attacker.

### Staged path (why this concept also wins on schedule)
The tube halves are the parts that NEED metal (clamp strength, anti-cut); the boxes are
what printers do best. **Stage 1: aluminum halves + PETG-printed boxes** using the same
inside-out bolt pattern — a metal-where-it-matters prototype months early. **Stage 2:**
machine A1/A3 as drop-in swaps; the chassis and hole patterns never change.

### Assembly
Bench: liner-free halves → bolt A1 + A3 to C1 from inside (M3 flat, flush) → load
electronics into A1, spool cartridge into A3 → lid + cover plates. On the bike: slip the
liner, hang C1 on the tube, C2 on, 2× M5 from inside, 1× closure screw down the latch bore.

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

1. Drop printed spool cartridge into the bay pocket; route cable through the bushed exit.
2. Screw the loaded pedestal cart + electronics into the cavity (tapped holes, no inserts).
3. Lid: O-ring cord in groove, RF insert in bezel, 4× M3.
4. Bay cover plate: gasket, 4× M3.
5. On the bike: liner in, clamp half on, 2× M5 from inside the bore, close, 1× closure
   screw down the latch bore. Done — **3 fastener actions for the consumer install.**

## 8. Open decisions (pick before modeling)

| # | Decision | Recommendation |
|---|---|---|
| D1 | Hinge | **DECIDED: deleted.** Two M5 inside the bore + closure lug |
| D2 | Material | 6061-T6 now; steel variant later from the same model |
| D3 | Spool | **DECIDED: printed cartridge inside the bolt-on bottom box (A3)** |
| D4 | Who machines | TAMU shop for M1/M2 (design manual-3-axis-friendly), SendCutSend for plates |
| D5 | Modeling | SolidWorks by owner against §2A; Claude checks hole patterns, wall/countersink stack-ups, and the closure-lug geometry |
| D6 | Tube stock | **DECIDED: 2.5" × 3/16" 6061 (Ø63.5 × 4.76), line-bored Ø54** — Ø60×5 would have given a Ø50 bore (too small for the liner) |
| D7 | Stage 1 boxes printed? | Yes — PETG boxes on aluminum halves first (same bolt pattern), machine later |

## 9. What verification looks like in this era

The gate suite simplifies with the design: no sweep gate (nothing swings), no insert
collar gate (no inserts). Keeps: interference/clearance matrix, screw-path checks, min
internal corner radius audit (new — every internal corner ≥ R4), wall-thickness audit,
and the paired-bore alignment stack-up. If modeled in SolidWorks: interference detection
+ hole-wizard discipline substitute, per the workflow prompt.

## 10. Model status (2026-09-06)

`cad/cnc_casing_cq.py` builds all 8 parts (C1, C2, closure block, A1 top box, A2 lid, A3
bottom box, liner L/R) as single solids; `--gates` = interference matrix (0 clashes),
counterbore wall audit, screw-path probes — all green. STEP set in `cnc-design/step/`
(+ `cnc_casing_assembly.step`), renders in `renders/cnc/`. Placeholders awaiting owner
input are listed in the chat handoff: reader footprint (Q1), spool cartridge envelope +
axis (Q2), overall height (Q3), cable exit direction (Q4), closure screw size (Q5).
