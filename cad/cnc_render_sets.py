"""cnc_render_sets.py -> cnc-design/stl/section/, cnc-design/stl/latch/ and cnc-design/stl/open/

Derived STL sets for cad/render_cnc.scad:
  section/  every part (+ the lid-mounted reference bodies) intersected with a 16 mm slab
            through the latch axis (x LATCH_X-8 .. LATCH_X+8) - OpenSCAD paints its own
            intersection() black in preview, so the cut is done here.
  open/     the C2 set (C2, closure block, hinge block, liner_left) rotated OPEN_DEG about the pin.
Run after `python cad/cnc_casing_cq.py` (needs the parts; rebuilds them here).
"""
import os, sys
sys.argv = [sys.argv[0]]
sys.path.insert(0, os.path.dirname(__file__))
from cnc_casing_cq import *   # noqa

os.makedirs("cnc-design/stl/section", exist_ok=True)
os.makedirs("cnc-design/stl/open", exist_ok=True)
os.makedirs("cnc-design/stl/latch", exist_ok=True)
slab = xbox(LATCH_X - 8.0, LATCH_X + 8.0, -200, 200, -200, 200)
latch_cut = xbox(78.0, IX1 + 1, -200, LATCH_Y, -200, 200)   # latch/: everything at y <= the latch axis plane, x 78..wall - the whole train in one section
sect = ["C1_chassis_half", "C2_clamp_half", "closure_block", "hinge_block", "hinge_pin", "A1_top_box", "A2_lid",
        "A3_bottom_box", "A4_cover_plate", "A5_window_insert", "liner_right", "liner_left",
        "ref_button_green", "ref_button_red", "ref_plunger", "ref_solenoid", "ref_driver_card",
        "ref_cap", "ref_ret_spring", "ref_bushing", "ref_head", "ref_ejector", "ref_closure_screw"]
for n in sect:
    s = PARTS[n]().intersect(slab)
    if s.solids().vals():
        cq.exporters.export(s, f"cnc-design/stl/section/{n}.stl", tolerance=0.05, angularTolerance=0.2)
        print("[section]", n)
for n in sect + ["ref_tp4056", "ref_nano", "ref_mt3608"]:
    s = PARTS[n]().intersect(latch_cut)
    if s.solids().vals():
        cq.exporters.export(s, f"cnc-design/stl/latch/{n}.stl", tolerance=0.05, angularTolerance=0.2)
        print("[latch]", n)
P0, P1 = cq.Vector(0, HINGE_Y, HINGE_Z), cq.Vector(1, HINGE_Y, HINGE_Z)
for n in ("C2_clamp_half", "closure_block", "hinge_block", "liner_left"):
    s = cq.Workplane(obj=PARTS[n]().val().rotate(P0, P1, OPEN_DEG))
    cq.exporters.export(s, f"cnc-design/stl/open/{n}.stl", tolerance=0.05, angularTolerance=0.2)
    print("[open]", n)
print("[ok] render sets")
