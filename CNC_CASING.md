# CNC_CASING.md — the machined-casing redesign (concept + DFM contract)

Goal: a casing **designed for CNC from the first sketch** — fewer parts, simpler parts,
simpler assembly — not the printed geometry with machining notes bolted on (that's §6.9,
which honestly scored the printed body at 4 setups **plus a 4th-axis rotary**). This doc
is the architecture contract to model against (SolidWorks or parametric); the printed
v0.8.3 remains the functional-prototype lineage.

## 1. The one insight that drives everything

FDM and CNC have opposite cost functions. The printed design spends free complexity
everywhere: organic drafted pod fused to a cylinder, 8 interleaved hinge knuckles,
swept-arc pockets, bosses and brackets grown mid-air, 27 heat-set inserts because plastic
can't hold threads. **In metal, every one of those is money — and most exist only because
of printing or the hinge.** The CNC casing deletes the *reasons*, not just the features.

## 2. The five simplification moves

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

## 3. What carries over UNCHANGED (do not redesign these)

| Kept | Why |
|---|---|
| Latch mechanism (Ø11 receiver, plunger-as-pin, square-flanked groove head, ejector spring, self-guarding screw) | Already designed machining-first (lathe head, reamed bores); the physics is the physics |
| TPU finned liner + shim (Ø32–46 one-size fit) | Compliant part — machining doesn't apply; bore stays Ø54 to keep the liner stack |
| All electronics + wiring plan (Nano, reader, MT3608, TP4056, 103450, driver card) | Casing-independent |
| RF window strategy | **A metal lid is opaque to 13.56 MHz.** The machined lid gets a rectangular window cutout; the polycarbonate/printed window insert seats in the bezel step the v0.7 lid already modeled "so the split is free later" — this is that later |
| Drainage philosophy | Weeps + grease notes port over as drilled holes (cheaper than in plastic) |

## 4. Part architecture (machined count: 4, plus plates)

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
| D1 | Hinge: keep vs **two-bolt clamshell** | Delete the hinge (Move 1) — it's the 4th-axis and half the part count |
| D2 | Material | 6061-T6 now; steel variant later from the same model |
| D3 | Drum: round pocket in billet vs **printed cartridge in a rectangular pocket** | Cartridge — billet stays prismatic, spool iterates in plastic |
| D4 | Who machines | TAMU shop for M1/M2 (design manual-3-axis-friendly), SendCutSend for plates |
| D5 | Modeling | SolidWorks by owner against this contract, or parametric+gates by Claude — either way the interfaces in §3 are frozen |

## 9. What verification looks like in this era

The gate suite simplifies with the design: no sweep gate (nothing swings), no insert
collar gate (no inserts). Keeps: interference/clearance matrix, screw-path checks, min
internal corner radius audit (new — every internal corner ≥ R4), wall-thickness audit,
and the paired-bore alignment stack-up. If modeled in SolidWorks: interference detection
+ hole-wizard discipline substitute, per the workflow prompt.
