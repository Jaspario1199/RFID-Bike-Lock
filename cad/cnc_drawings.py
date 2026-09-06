"""cnc_drawings.py - shop drawings for the CNC casing (cad/cnc_casing_cq.py), one A3 sheet per
part: hidden-line orthographic views (OCCT HLR), overall dimensions, feature callouts, a hole
schedule and a title block. Output: cnc-design/drawings/cnc_casing_drawings.pdf (+ PNG per
sheet). Scale is true on every sheet (noted in the title block).

  python cad/cnc_drawings.py
"""
import math, os, sys, datetime
sys.path.insert(0, os.path.dirname(__file__))
sys.argv = [sys.argv[0]]
import cadquery as cq
import cnc_casing_cq as m
from OCP.HLRBRep import HLRBRep_Algo, HLRBRep_HLRToShape
from OCP.HLRAlgo import HLRAlgo_Projector
from OCP.gp import gp_Ax2, gp_Pnt, gp_Dir
from OCP.BRepLib import BRepLib
from OCP.BRepAdaptor import BRepAdaptor_Curve
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle

OUT = "cnc-design/drawings"
REV = "rev 3b"
TODAY = datetime.date.today().isoformat()

# ---------------- views: name -> (normal N = direction the viewer looks FROM, X direction) ----------------
def V(n, x):
    n = cq.Vector(*n).normalized(); x = cq.Vector(*x).normalized()
    return (n, x, n.cross(x))
VIEWS = {
    "TOP":    V((0, 0, 1), (1, 0, 0)),     # looking down: 2D x = X, 2D y = Y
    "BOTTOM": V((0, 0, -1), (1, 0, 0)),    # 2D x = X, 2D y = -Y
    "FRONT":  V((0, -1, 0), (1, 0, 0)),    # from the C2 side: 2D x = X, 2D y = Z
    "BACK":   V((0, 1, 0), (-1, 0, 0)),    # from the C1 side: 2D x = -X, 2D y = Z
    "RIGHT":  V((1, 0, 0), (0, 1, 0)),     # from +x: 2D x = Y, 2D y = Z
    "LEFT":   V((-1, 0, 0), (0, -1, 0)),   # from -x: 2D x = -Y, 2D y = Z
    "ISO":    V((1, -1, 1), (1, 1, 0)),
}

def project(p, view):
    n, x, y = VIEWS[view]
    p = cq.Vector(*p)
    return (p.dot(x), p.dot(y))

def hlr_polylines(shape, view):
    """visible + hidden edges of `shape` projected on `view`, as lists of (x, y) polylines."""
    n, x, y = VIEWS[view]
    hlr = HLRBRep_Algo(); hlr.Add(shape.wrapped)
    ax = gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(n.x, n.y, n.z), gp_Dir(x.x, x.y, x.z))
    hlr.Projector(HLRAlgo_Projector(ax)); hlr.Update(); hlr.Hide()
    hs = HLRBRep_HLRToShape(hlr)
    out = {"vis": [], "hid": []}
    for key, comps in (("vis", (hs.VCompound(), hs.Rg1LineVCompound(), hs.OutLineVCompound())),
                       ("hid", (hs.HCompound(), hs.OutLineHCompound()))):
        for c in comps:
            if c.IsNull():
                continue
            BRepLib.BuildCurves3d_s(c)
            for e in cq.Shape.cast(c).Edges():
                npts = 2 if e.geomType() == "LINE" else 48
                ad = BRepAdaptor_Curve(e.wrapped)
                t0, t1 = ad.FirstParameter(), ad.LastParameter()
                pts = [ad.Value(t0 + (t1 - t0) * i / (npts - 1)) for i in range(npts)]
                out[key].append([(p.X(), p.Y()) for p in pts])
    return out

# ---------------- dimensioning helpers (all in sheet mm) ----------------
def dim_h(ax, x0, x1, y, text, off=4, s=1.0):
    ax.plot([x0, x1], [y, y], color="#1a4d8f", lw=0.6)
    for xx in (x0, x1):
        ax.plot([xx, xx], [y - off * 0.6, y + off * 0.6], color="#1a4d8f", lw=0.6)
    ax.annotate("", (x0, y), (x1, y), arrowprops=dict(arrowstyle="<->", color="#1a4d8f", lw=0.6, shrinkA=0, shrinkB=0))
    ax.text((x0 + x1) / 2, y + 1.2, text, ha="center", va="bottom", fontsize=6.5, color="#1a4d8f")

def dim_v(ax, y0, y1, x, text, off=4):
    ax.plot([x, x], [y0, y1], color="#1a4d8f", lw=0.6)
    for yy in (y0, y1):
        ax.plot([x - off * 0.6, x + off * 0.6], [yy, yy], color="#1a4d8f", lw=0.6)
    ax.annotate("", (x, y0), (x, y1), arrowprops=dict(arrowstyle="<->", color="#1a4d8f", lw=0.6, shrinkA=0, shrinkB=0))
    ax.text(x + 1.2, (y0 + y1) / 2, text, ha="left", va="center", fontsize=6.5, color="#1a4d8f", rotation=90)

def draw_view(ax, polys, ox, oy, s, callouts=()):
    for pl in polys["hid"]:
        ax.plot([ox + s * p[0] for p in pl], [oy + s * p[1] for p in pl], color="#9a9a9a", lw=0.35, ls=(0, (3, 2)))
    for pl in polys["vis"]:
        ax.plot([ox + s * p[0] for p in pl], [oy + s * p[1] for p in pl], color="black", lw=0.7)
    for (px, py, text, dx, dy) in callouts:
        ax.annotate(text, (ox + s * px, oy + s * py), (ox + s * px + dx, oy + s * py + dy), fontsize=6,
                    color="#8a1a1a", arrowprops=dict(arrowstyle="-|>", color="#8a1a1a", lw=0.5, shrinkA=0, shrinkB=0),
                    ha="left" if dx >= 0 else "right", va="center")

# ---------------- part definitions ----------------
def fmt(v):
    return f"{v:g}"
P = {}   # name -> dict(title, material, qty, views, notes, holes, callouts)
def part(name, title, material, qty, views, notes, holes, callouts=None, process=""):
    P[name] = dict(title=title, material=material, qty=qty, views=views, notes=notes, holes=holes,
                   callouts=callouts or {}, process=process)

TAP = "M3 tapped (Ø2.5 pilot modeled; tap M3x0.5 in metal, self-tap in PETG)"
part("C1_chassis_half", "C1 - chassis half (carries the boxes)", "6061-T6 tube 2.5\" OD x 3/16\" wall, or PETG (stage 1)", 1,
     ["TOP", "BACK", "RIGHT"],
     ["Pair of halves from one saw-cut tube, split on the y=0 plane, line-bored together to Ø54.0",
      "All screw counterbores are cut from the BORE side (heads sit under the liner)",
      "Rear liner lip: x 148..150, inward to R25.5",
      "Top rows feed A1 (x 25/75/125); bottom rows feed A3 (x 40/100). Do not mix them up"],
     [("A", "3x Ø3.4 THRU vertical at y=+6 (top crown row), Ø6.2 C'BORE 2.3 deep from the bore", "x 25, 75, 125"),
      ("B", "3x Ø3.4 THRU horizontal (+y) at z=+8 (top skirt row), Ø6.2 C'BORE from the bore", "x 25, 75, 125"),
      ("C", "2x Ø3.4 THRU vertical at y=+10 (bottom crown row), Ø6.2 C'BORE from the bore", "x 40, 100"),
      ("D", "2x Ø3.4 THRU horizontal (+y) at z=-8 (bottom skirt row), Ø6.2 C'BORE from the bore", "x 40, 100")],
     {"TOP": [((25, 6, 31.75), "A", 8, 10)], "BACK": [((75, 31.75, 8), "B", 8, 10), ((100, 31.75, -8), "D", 8, -10)],
      "RIGHT": [((150, 10, -31), "C", 10, -8)]})
part("C2_clamp_half", "C2 - clamp half (hinged)", "6061-T6 tube 2.5\" OD x 3/16\" wall, or PETG (stage 1)", 1,
     ["TOP", "FRONT", "RIGHT"],
     ["Mate of C1 (same tube, same line-bore)", "Counterbores from the BORE side", "Rear liner lip: x 148..150, inward to R25.5"],
     [("A", "2x Ø3.4 THRU vertical at y=-7 (closure block), Ø6.2 C'BORE from the bore", f"x {fmt(m.BLK_SCREW_X[0])}, {fmt(m.BLK_SCREW_X[1])}"),
      ("B", f"2x Ø3.4 THRU vertical at y={fmt(m.HB_SCREW_Y)} through the BOTTOM wall (hinge block), Ø6.2 C'BORE from the bore", f"x {fmt(m.HB_SCREW_X[0])}, {fmt(m.HB_SCREW_X[1])}"),
      ("S", f"4x Ø{fmt(m.STUD_HOLE_D)} +0.1/-0 x {fmt(m.STUD_HOLE_H)} BLIND radial, from the bore (liner press-fit studs)", f"x {fmt(m.STUD_X[0])}, {fmt(m.STUD_X[1])} at 45/135deg from the seam")],
     {"TOP": [((m.BLK_SCREW_X[0], -7, 31), "A", -8, 10)], "FRONT": [((m.HB_SCREW_X[1], -31, -25), "B", 8, -10)]})
part("closure_block", "B - closure block (on C2, under A1)", "steel or 6061 (PETG stage 1)", 1,
     ["TOP", "FRONT", "RIGHT"],
     ["Underside is a saddle R31.8 - sits on C2's OD", "Top face is flat and CONTACTS the A1 pocket roof under the closure screw",
      "The closure screw comes down the latch bore: M3x8 low-head"],
     [("A", "M3 closure-screw thread THRU, " + TAP, f"({fmt(m.LATCH_X)}, {fmt(m.LATCH_Y)})"),
      ("B", "2x " + TAP + ", from the saddle side, 6 deep", f"x {fmt(m.BLK_SCREW_X[0])}, {fmt(m.BLK_SCREW_X[1])} at y=-7")],
     {"TOP": [((m.LATCH_X, m.LATCH_Y, 36.5), "A", 6, 6), ((m.BLK_SCREW_X[1], -7, 36.5), "B", 6, -6)]})
part("hinge_block", "H - hinge block (on C2, carries C2's lug)", "6061-T6 (PETG stage 1)", 1,
     ["TOP", "FRONT", "RIGHT"],
     ["Body rides C2's OD (saddle R31.8); lug is round about the pin", "Body bottom = pin height by design (swing clearance) - do not extend it",
      f"Lug spans x {fmt(m.C2_LUG[0])}..{fmt(m.C2_LUG[1])} (0.3 end float between A3's lugs)"],
     [("A", f"Ø{fmt(m.HPIN_D + m.HPIN_CLR)} pin bore THRU the lug, axis at (y {fmt(m.HINGE_Y)}, z {fmt(m.HINGE_Z)})", "along x"),
      ("B", "2x " + TAP + ", from the saddle side", f"x {fmt(m.HB_SCREW_X[0])}, {fmt(m.HB_SCREW_X[1])} at y={fmt(m.HB_SCREW_Y)}")],
     {"RIGHT": [((98, m.HINGE_Y, m.HINGE_Z), "A", 10, -6)], "TOP": [((m.HB_SCREW_X[0], m.HB_SCREW_Y, -29), "B", -6, 6)]})
part("hinge_pin", "hinge pin", "steel dowel Ø5 h6", 1, ["FRONT", "RIGHT"],
     ["Standard Ø5 x 36 dowel (cut a 40 to length if needed); ends chamfered",
      "Assembly: enter through A3 lug 1 (x 58 face) to the blind end, then press a Ø5 x 2 plug flush behind it"],
     [("A", "Ø5 h6 x 36", "")], {})
part("A1_top_box", "A1 - top box (latch + electronics)", "6061-T6 billet (PETG stage 1)", 1,
     ["TOP", "FRONT", "RIGHT", "BOTTOM"],
     ["Underside: saddle R32.0 on the C1 side, relieved to R34.0 over C2 (y<0.3) - C2's rim arcs outward as it swings",
      f"Interior pocket {fmt(m.BX1 - m.BX0 - 2 * m.BWALL)} x {fmt(m.BY1 - m.BY0 - 2 * m.BWALL)} x {fmt(m.INT_H)} deep from z={fmt(m.ZF)}, R6 corners",
      f"Closure-block pocket under the -y overhang: x {fmt(m.BLK_X0 - 0.2)}..{fmt(m.BLK_X1 + 0.2)}, open toward -y, roof at z={fmt(m.BLK_TOP)}",
      "Latch boss Ø19 rises from the floor around the receiver bore"],
     [("A", f"Ø{fmt(m.BORE_D)} receiver bore from the top down to the floor (z {fmt(m.ZF)})", f"({fmt(m.LATCH_X)}, {fmt(m.LATCH_Y)})"),
      ("B", f"Ø{fmt(m.CLR4)} closure-screw clearance THRU the floor (1.5 thick) under A", "same axis"),
      ("C", f"Ø{fmt(m.PIN_D)} plunger channel, horizontal along +x from the bore, axis z={fmt(m.PIN_Z)}", f"(x {fmt(m.LATCH_X)}.., y {fmt(m.LATCH_Y)})"),
      ("D", "4x " + TAP + " lid screws, 8 deep from the top", ", ".join(f"({fmt(x)}, {fmt(y)})" for x, y in m.LID_SCREWS)),
      ("E", "3x " + TAP + " vertical from the saddle at y=+6 (crown row), to z=37", "x 25, 75, 125"),
      ("F", "3x " + TAP + " horizontal (+y) at z=+8 into the skirt (skirt row)", "x 25, 75, 125")],
     {"TOP": [((m.LATCH_X, m.LATCH_Y, 62), "A", 8, -8), ((15, -9, 62), "D", -8, -8)],
      "BOTTOM": [((75, 6, 20), "E", 8, 8)], "RIGHT": [((140, 34, 8), "F", 6, 6)],
      "FRONT": [((m.LATCH_X + 9.5, m.LATCH_Y, m.PIN_Z), "C", 10, 6)]})
part("A2_lid", "A2 - lid plate", "6061 plate 5 mm (PETG stage 1)", 1, ["TOP", "FRONT", "BOTTOM"],
     [f"RF window {fmt(m.WIN_L)} x {fmt(m.WIN_W)} THRU, R4 corners; underside recess {fmt(m.WIN_L + 2 * m.INS_FLANGE + 0.2)} x {fmt(m.WIN_W + 2 * m.INS_FLANGE + 0.2)} x {fmt(m.INS_FL_T)} deep for the insert flange",
      "Lid screws countersunk 90deg from the top for M3 flat head"],
     [("A", f"window {fmt(m.WIN_L)} x {fmt(m.WIN_W)} THRU", f"centre ({fmt(m.WIN_CX)}, {fmt((m.BY0 + m.BY1) / 2)})"),
      ("B", f"Ø{fmt(m.BORE_D + 0.6)} THRU (latch bore pass-through)", f"({fmt(m.LATCH_X)}, {fmt(m.LATCH_Y)})"),
      ("C", f"Ø{fmt(m.BTN_D)} THRU (sealed button)", f"({fmt(m.BTN_X)}, 12)"),
      ("D", f"2x Ø{fmt(m.LED_D)} THRU (LEDs)", f"({fmt(m.LED_X)}, 6) ({fmt(m.LED_X)}, 18)"),
      ("E", "4x Ø3.4 THRU, 90deg C'SINK Ø6.4 from the top", ", ".join(f"({fmt(x)}, {fmt(y)})" for x, y in m.LID_SCREWS))],
     {"TOP": [((m.WIN_CX, 11, 67), "A", 0, 12), ((m.LATCH_X, m.LATCH_Y, 67), "B", 8, -8), ((m.BTN_X, 12, 67), "C", 8, 8),
              ((m.LED_X, 18, 67), "D", -4, 10), ((135, 31, 67), "E", 6, 6)]})
part("A3_bottom_box", "A3 - spool puck + cradle (hinge knuckles)", "6061-T6 billet (PETG stage 1)", 1,
     ["TOP", "FRONT", "RIGHT", "BOTTOM"],
     [f"Cradle x {fmt(m.SX0)}..{fmt(m.SX1)}, y {fmt(m.A3_Y0)}..{fmt(m.CRADLE_Y1)}, saddle R32.0 on top; skirt rib y 32..44 up to z=-3",
      f"Puck Ø{fmt(2 * m.PUCK_R)} centred under the tube (x {fmt(m.PX)}, y 0); flat top at z={fmt(m.STOP_Z)} on the C2 side = hinge STOP",
      f"Two hinge lugs Ø{fmt(m.LUG_D)} about the pin axis (y {fmt(m.HINGE_Y)}, z {fmt(m.HINGE_Z)}) at x {fmt(m.A3_LUGS[0][0])}..{fmt(m.A3_LUGS[0][1])} and {fmt(m.A3_LUGS[1][0])}..{fmt(m.A3_LUGS[1][1])}; Ø12 clearance between them for C2's lug",
      "Spool cartridge + power spring load from below; A4 closes the pocket"],
     [("A", f"Ø{fmt(m.POCKET_D)} spool pocket from the bottom face up to z={fmt(m.POCKET_TOP)} (depth {fmt(m.POCKET_TOP - m.SZ_BOT)})", f"axis ({fmt(m.PX)}, 0)"),
      ("B", f"Ø{fmt(m.HPIN_D + m.HPIN_CLR)} pin bore along x from lug 1's outer face (x {fmt(m.A3_LUGS[0][0])}), BLIND, ends at x {fmt(m.A3_LUGS[1][1] - 2)}", f"axis (y {fmt(m.HINGE_Y)}, z {fmt(m.HINGE_Z)})"),
      ("C", f"Ø{fmt(m.EXIT_D)} cable exit along x through the puck wall (fit a steel bushing)", f"y {fmt(m.POCKET_CY - m.POCKET_D / 2 + m.EXIT_D / 2 + 0.5)}, z {fmt((m.POCKET_TOP + m.SZ_BOT) / 2)}"),
      ("D", "4x " + TAP + " cover screws, 6 deep from the bottom face, in the puck wall", "PCD " + fmt(2 * (m.POCKET_D / 2 + 2.75)) + " at 45/135/225/315deg"),
      ("E", "2x " + TAP + f" vertical from the saddle at y={fmt(m.A3_CROWN_Y)} (crown row)", f"x {fmt(m.A3_SCREW_X[0])}, {fmt(m.A3_SCREW_X[1])}"),
      ("F", "2x " + TAP + " horizontal (+y) at z=-8 into the skirt rib (skirt row)", f"x {fmt(m.A3_SCREW_X[0])}, {fmt(m.A3_SCREW_X[1])}")],
     {"BOTTOM": [((m.PX, 0, m.SZ_BOT), "A", 10, 10), ((m.COVER_SCREWS[0][0], m.COVER_SCREWS[0][1], m.SZ_BOT), "D", 8, -8)],
      "FRONT": [((m.A3_LUGS[0][0], m.HINGE_Y, m.HINGE_Z), "B", -10, -8), ((m.SX0, -21.5, -67.5), "C", -8, -6)],
      "TOP": [((m.A3_SCREW_X[0], m.A3_CROWN_Y, -20), "E", -8, 8)], "RIGHT": [((m.SX1, 40, -8), "F", 8, 6)]})
part("A4_cover_plate", "A4 - puck cover", "6061 plate 3 mm (PETG stage 1)", 1, ["TOP", "FRONT"],
     [f"Ø{fmt(2 * m.PUCK_R)} disc, 3 thick; gasket under it", "Screws countersunk 90deg from the outside for M3 flat head"],
     [("A", "4x Ø3.4 THRU, 90deg C'SINK Ø6.4", "PCD " + fmt(2 * (m.POCKET_D / 2 + 2.75)) + " at 45/135/225/315deg")],
     {"TOP": [((m.COVER_SCREWS[1][0], m.COVER_SCREWS[1][1], m.SZ_BOT - 3), "A", -8, 8)]})
part("A5_window_insert", "A5 - RF window insert (opaque)", "printed PETG/ASA or polycarbonate", 1, ["TOP", "FRONT"],
     ["Body fills the lid cutout flush with the lid top; flange sits in the lid's underside recess", "Opaque by choice - RF does not care; keep it non-metallic"],
     [("A", f"body {fmt(m.WIN_L - 0.3)} x {fmt(m.WIN_W - 0.3)} x {fmt(m.LID_T - m.INS_FL_T)}, flange {fmt(m.WIN_L + 2 * m.INS_FLANGE)} x {fmt(m.WIN_W + 2 * m.INS_FLANGE)} x {fmt(m.INS_FL_T)}", "")], {})
part("liner_right", "liner (right half, C1 side)", "TPU 95A, printed on its seam face", 1, ["RIGHT", "TOP"],
     ["Base ring R24.85..26.85 with 24 fins (1.2 wide x 4 tall) - fins bend to grip Ø32..46 down tubes", "Left half is the mirror (liner_left)"],
     [("A", "24 fins on 15deg pitch, 1.4 x 12, leaning 30deg", ""),
      ("B", f"4x press-fit studs Ø{fmt(m.STUD_D)} ±0.1 x {fmt(m.STUD_H)} on the outside; mate: Ø{fmt(m.STUD_HOLE_D)} +0.1/-0 x {fmt(m.STUD_HOLE_H)} blind holes in the tube wall (0.3 interference)", f"x {fmt(m.STUD_X[0])}, {fmt(m.STUD_X[1])} at 45/135deg from the seam")], {})
part("liner_left", "liner (left half, C2 side)", "TPU 95A, printed on its seam face", 1, ["LEFT", "TOP"],
     ["Mirror of liner_right"], [("A", "24 fins on 15deg pitch, 1.4 x 12, leaning 30deg", ""), ("B", f"4x press-fit studs Ø{fmt(m.STUD_D)} x {fmt(m.STUD_H)} - see liner_right", "")], {})

# ---------------- sheet composer ----------------
SHEET_W, SHEET_H = 420.0, 297.0   # A3 landscape, mm
def sheet(pdf, idx, total, name, shape):
    d = P[name]
    bb = shape.BoundingBox()
    views = d["views"]
    polys = {v: hlr_polylines(shape, v) for v in views + ["ISO"]}
    # extents per view (in view mm)
    ext = {}
    for v, pl in polys.items():
        xs = [p[0] for l in pl["vis"] + pl["hid"] for p in l]; ys = [p[1] for l in pl["vis"] + pl["hid"] for p in l]
        ext[v] = (min(xs), max(xs), min(ys), max(ys))
    # layout: drawing area x 10..300, y 40..287 ; views in a 2x2 grid (third angle: TOP over FRONT, RIGHT beside FRONT)
    fig = plt.figure(figsize=(SHEET_W / 25.4, SHEET_H / 25.4))
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, SHEET_W); ax.set_ylim(0, SHEET_H); ax.set_aspect("equal"); ax.axis("off")
    ax.add_patch(Rectangle((5, 5), SHEET_W - 10, SHEET_H - 10, fill=False, lw=1.0))
    grid = {"FRONT": (0, 0), "RIGHT": (1, 0), "LEFT": (1, 0), "BACK": (1, 0), "TOP": (0, 1), "BOTTOM": (1, 1)}
    cells = {}
    for v in views:
        c = grid.get(v, (1, 1))
        if c in cells.values():          # collision (e.g. RIGHT and BOTTOM both want (1,1)/(1,0)) -> next free
            for cc in ((0, 0), (1, 0), (0, 1), (1, 1)):
                if cc not in cells.values():
                    c = cc; break
        cells[v] = c
    CW, CH = 140.0, 118.0
    cell_origin = {(0, 0): (12, 40), (1, 0): (160, 40), (0, 1): (12, 165), (1, 1): (160, 165)}
    # one scale for all ortho views
    s = min(min((CW - 30) / max(1e-6, e[1] - e[0]), (CH - 30) / max(1e-6, e[3] - e[2])) for v, e in ext.items() if v != "ISO")
    s = min(s, 2.0)
    for v in views:
        e = ext[v]; ox0, oy0 = cell_origin[cells[v]]
        ox = ox0 + 12 + (CW - 30 - s * (e[1] - e[0])) / 2 - s * e[0]
        oy = oy0 + 14 + (CH - 30 - s * (e[3] - e[2])) / 2 - s * e[2]
        cos = [(*project(p, v), t, dx, dy) for (p, t, dx, dy) in d["callouts"].get(v, [])]
        draw_view(ax, polys[v], ox, oy, s, cos)
        ax.text(ox0 + 2, oy0 + CH - 4, v, fontsize=7, weight="bold")
        # overall dims of the view
        dim_h(ax, ox + s * e[0], ox + s * e[1], oy + s * e[2] - 6, f"{e[1] - e[0]:.1f}")
        dim_v(ax, oy + s * e[2], oy + s * e[3], ox + s * e[1] + 6, f"{e[3] - e[2]:.1f}")
    # iso (own scale) top-right of the notes column
    e = ext["ISO"]; si = min(95 / max(1e-6, e[1] - e[0]), 70 / max(1e-6, e[3] - e[2]), 1.2)
    ox = 312 + (95 - si * (e[1] - e[0])) / 2 - si * e[0]; oy = 212 + (70 - si * (e[3] - e[2])) / 2 - si * e[2]
    pi = {"vis": polys["ISO"]["vis"], "hid": []}
    draw_view(ax, pi, ox, oy, si)
    ax.text(312, 284, "ISO (not to scale)", fontsize=7, weight="bold")
    # notes + hole schedule
    y = 205
    ax.text(312, y, "NOTES", fontsize=7, weight="bold"); y -= 5
    for n in d["notes"]:
        for line in wrap(n, 62):
            ax.text(312, y, "• " + line if line is n or n.startswith(line) else "   " + line, fontsize=5.6); y -= 4.2
        y -= 1
    y -= 2
    ax.text(312, y, "HOLE / FEATURE SCHEDULE", fontsize=7, weight="bold"); y -= 5
    for (tag, desc, where) in d["holes"]:
        lines = wrap(f"{tag}: {desc}" + (f"   @ {where}" if where else ""), 62)
        for i, line in enumerate(lines):
            ax.text(312, y, line if i == 0 else "   " + line, fontsize=5.6, color="#8a1a1a" if i == 0 else "black"); y -= 4.2
        y -= 1
    # general notes
    gy = 40
    ax.text(312, gy + 18, "GENERAL", fontsize=7, weight="bold")
    for i, t in enumerate(["Units mm. Datum: tube axis = X, seam plane y=0, Z up. Break sharp edges 0.3.",
                           "Stage 1 (PETG): print on the face noted, pilots self-tap M3. Metal: tap M3x0.5.",
                           "Internal corners R4 unless the model shows R6. Tolerance ±0.1 on fits, ±0.3 elsewhere."]):
        ax.text(312, gy + 13 - 4.2 * i, t, fontsize=5.4)
    # title block
    ax.add_patch(Rectangle((5, 5), SHEET_W - 10, 28, fill=False, lw=1.0))
    ax.plot([5, SHEET_W - 5], [19, 19], color="black", lw=0.5)
    for xx in (150, 250, 330):
        ax.plot([xx, xx], [5, 33], color="black", lw=0.5)
    ax.text(8, 27, "RFID BIKE LOCK - CNC CASING", fontsize=9, weight="bold")
    ax.text(8, 21, f"cad/cnc_casing_cq.py  {REV}", fontsize=6)
    ax.text(8, 13, d["title"], fontsize=8, weight="bold")
    ax.text(8, 8, f"file: cnc-design/step/{name}.step", fontsize=6)
    ax.text(153, 27, "MATERIAL", fontsize=5.5); ax.text(153, 22, d["material"], fontsize=6.5)
    ax.text(153, 13, "QTY", fontsize=5.5); ax.text(153, 8, str(d["qty"]), fontsize=6.5)
    ax.text(253, 27, "SCALE (ortho views)", fontsize=5.5); ax.text(253, 22, f"{s:.2f} : 1", fontsize=6.5)
    ax.text(253, 13, "BOUNDING BOX x / y / z", fontsize=5.5)
    ax.text(253, 8, f"{bb.xlen:.1f} / {bb.ylen:.1f} / {bb.zlen:.1f}   (x {bb.xmin:.1f}..{bb.xmax:.1f}, y {bb.ymin:.1f}..{bb.ymax:.1f}, z {bb.zmin:.1f}..{bb.zmax:.1f})", fontsize=5.6)
    ax.text(333, 27, "DATE", fontsize=5.5); ax.text(333, 22, TODAY, fontsize=6.5)
    ax.text(333, 13, "SHEET", fontsize=5.5); ax.text(333, 8, f"{idx} / {total}", fontsize=6.5)
    ax.text(370, 13, "3rd angle", fontsize=5.5); ax.text(370, 8, "A3 landscape", fontsize=6.5)
    pdf.savefig(fig)
    fig.savefig(f"{OUT}/{idx:02d}_{name}.png", dpi=110)
    plt.close(fig)

def wrap(text, n):
    words = text.split(" "); lines = []; cur = ""
    for w in words:
        if len(cur) + len(w) + 1 > n and cur:
            lines.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur: lines.append(cur)
    return lines

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    names = list(P)
    with PdfPages(f"{OUT}/cnc_casing_drawings.pdf") as pdf:
        for i, n in enumerate(names, 1):
            print(f"[sheet {i}/{len(names)}] {n}", flush=True)
            sheet(pdf, i, len(names), n, m.PARTS[n]().val())
    print("[ok]", f"{OUT}/cnc_casing_drawings.pdf")
