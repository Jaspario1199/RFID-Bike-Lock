# CAD_METHOD.md — how to model and verify mechanical parts with an agent

A portable working method, extracted from a real project (an RFID bike lock: a hinged
aluminium clamshell with bolted-on electronics and spool boxes, taken from concept to
gated STEP files and shop drawings). Nothing here is specific to that product. Hand this
to an agent at the start of a mechanical CAD project.

---

## 0. The one principle

**A part is not "done" because it renders correctly. It is done when a script proves it.**

Renders lie. They hide interference behind opaque faces, they hide a 0.3 mm gouge, and they
never show you that a screw can't physically reach its thread. Every claim about geometry —
"the parts don't collide", "the door swings", "the screw fits", "the electronics fit inside" —
must be produced by code that returns a number, and that code must live in the repo and be
re-runnable after every change.

Everything below is machinery for that principle.

---

## 1. Structure

**One parametric script is the source of truth.** Python + CadQuery works well (`pip install
cadquery`); the method transfers to any scripted CAD. Rules:

- **Every dimension is a named constant at the top**, with a comment saying *why* it has that
  value. `WALL = 3.0` is useless; `WALL = 3.0  # 3-perimeter PETG, and the M3 boss needs 1.5
  of meat around the pilot` survives being questioned six weeks later.
- **One coordinate frame, stated in the module docstring.** Which axis runs along the part,
  where the origin sits, what the parting plane is. Every later conversation depends on it.
- **A `PARTS` dict** mapping name → builder function. The exporter, the interference matrix
  and the render script all iterate that one dict, so they can never drift apart.
- **The exporter refuses multi-body parts.** A part that quietly became two solids is a bug
  every time. Fail loudly:

```python
sol = shape.solids().vals()
if len(sol) != 1:
    raise RuntimeError(f"{name}: {len(sol)} solids")
```

- **Generated output is gitignored**, except the release set you actually hand over.

Run modes: `python model.py` builds and exports; `python model.py --gates` runs every check
and exits non-zero on failure.

---

## 2. The gate catalogue

Write these as functions inside the model script. Not all apply to every project; add the ones
that match your failure modes.

### 2.1 Interference matrix (always)
Every pair of parts, intersected, volume reported. Anything over ~0.05 mm³ is a clash.

```python
inter = cq.Workplane(obj=a).intersect(cq.Workplane(obj=b))
v = sum(s.Volume() for s in inter.solids().vals())
```

Keep a `CONTACT_OK` whitelist for pairs that *should* touch (a lid on its rim, a press fit).
For a designed interference — a press fit — assert the volume **equals the intended amount**
rather than zero, so a fit that silently becomes a clearance is caught too.

### 2.2 Motion gates
Anything that hinges, slides or swings gets stepped through its range and re-checked against
everything static. Fine steps where geometry is tight, coarse elsewhere.

```python
for deg in [1,2,3,5,7,9,12,16,20,30,45,60]:
    moved = part.rotate(axis_p0, axis_p1, deg)
    ... intersect against every fixed part ...
```

This is the highest-value gate in the catalogue. On the source project it killed an entire
architecture: a hinge that looked obviously fine swept its lower quadrant into a box below,
and no amount of staring at renders would have shown it.

### 2.3 Assembly-path gates
Motion gates prove the mechanism moves. Path gates prove it can be *assembled* and that the
thing it's meant to accept can get in. Step the workpiece along its real insertion path —
including approach direction, not just the final position.

### 2.4 Fastener-path probes
For every screw: a cylinder along its axis must be **air** where it passes through clearance
holes, and must **land in material** where it threads. Two probes per screw. This catches the
classic defect where a screw's clearance hole is right but a wall behind it blocks the driver,
or the pilot is 2 mm short of reachable.

### 2.5 Wall and material audits
Compute remaining wall thickness under counterbores, around pockets, beside bores. Compare
against a stated minimum. Print the number, not a boolean — you want to see 2.83 mm and judge
it, not read "PASS".

### 2.6 Reference-body stack-up
Model every purchased component as a plain box at its **real measured envelope**, placed where
it will actually sit. Then run the interference matrix over them and print a clearance report
listing every gap under 1 mm.

This converts "it should fit" into "it fits, and the tightest gap is 0.3 mm at the connector."
It also produces the layout drawing for free. Ask the owner to measure real parts on arrival —
datasheet dimensions and delivered dimensions differ constantly, and a 4 mm surprise on one
component can force a whole interior re-layout.

### 2.7 Manufacturing gates
Whatever your process cares about: overhang angle per declared print orientation, minimum
internal corner radius for a given cutter, draft, tool reach. State the process assumption in
the code, because it is a design input.

---

## 3. The loop

1. **Change one thing.**
2. **Rebuild and run all gates.** Not the one you think you affected — all of them. Fixes
   routinely break distant things.
3. **If a gate fails, find the root cause, then look for siblings.** One reported clash on the
   source project turned out to be seven instances of the same mistake. That is why the
   pairwise matrix exists.
4. **If a gate still fails after two focused attempts, stop and question the architecture.**
   Persistent geometric failure usually means the concept is wrong, not the numbers. Say so.
5. **Commit with a message that explains the reasoning**, not just the diff.

---

## 4. Honesty rules

These matter more than any technique.

- **Never report a gate as passing without running it.** If you changed the model and did not
  re-run, say that.
- **When something is provably impossible, say so and document the carve-out.** On the source
  project three fastener bosses could not physically get the required wall thickness — pinched
  between a bore, an outer skin and a swing envelope. The right answer was a documented
  exception with the reasoning, not a quiet fudge of the threshold.
- **Distinguish measured from assumed.** Maintain a running list of dimensions that are
  placeholders awaiting real parts. Re-flag them whenever the owner is about to spend money.
- **Report the number.** "Max overlap 2679.94 mm³ FAIL" is useful. "There's a small clash" is not.
- **When the owner reports a defect, believe the report and find the cause.** Do not explain
  why the render looks fine.

---

## 5. Traps that cost real time

CadQuery/OCC specific, but the shape of them generalises:

- **`Workplane.intersect` raises on empty intersection.** Wrap it; never call it raw in a check.
- **OCC segfaults on degenerate or tangent booleans.** Fix with 0.1 mm position nudges, or
  replace rotated-copy unions with analytic prisms. If export dies silently, bisect features in
  a subprocess.
- **Extrude directions are not intuitive** on rotated workplanes. Probe them rather than assume.
- **Loft with negative draft grows the top face.** Clearance maths must use the grown plan.
- **Slicing a part with a plane leaves detached slivers.** Keep the largest solid, or the
  exporter's single-body check will fire on geometry that is visually fine.
- **A "part" that a boolean split into two bodies still renders normally.** Only the solid count
  catches it.

---

## 6. What to hand over

- The model script, with gates, runnable by the owner.
- A STEP set — one file per part, plus a placed assembly. STEP, not STL, if it's going into
  real CAD. Delete exports of retired parts automatically so the folder always equals `PARTS`.
- Renders: isometric, exploded, section through the critical feature, and one showing the
  mechanism at its extreme of travel. Send them after every significant change; visual review
  by a human catches real bugs that gates don't express.
- Dimensioned drawings if the parts are going to a shop: one sheet per part, hidden-line ortho
  views, a hole schedule, and a title block. These can be generated from the same model.
- A design document recording **decisions and their reasoning**, including rejected
  alternatives and why they were rejected. The rejected ones stop the same idea being
  re-proposed in three weeks.

---

## 7. Suggested opening prompt for a new project

> You are modelling *[part/assembly]* in CadQuery. Work to CAD_METHOD.md.
>
> Before geometry: state the coordinate frame, list the parameters with reasoning, and tell me
> which dimensions are assumptions I need to verify against real parts.
>
> Build the model with every dimension as a named constant. Then write `--gates`: an
> interference matrix over all parts, a motion gate for anything that moves, fastener-path
> probes, a wall audit, and a reference-body stack-up for purchased components.
>
> Do not tell me a design works until the gates say so, with numbers. If a gate cannot pass
> because the geometry is genuinely constrained, tell me that plainly and propose the
> architectural change rather than relaxing the threshold.
