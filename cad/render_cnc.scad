// CNC casing renders (cad/cnc_casing_cq.py parts). Variables:
//   view = iso | exploded | end | section | open
//   section reads cnc-design/stl/section/ (16 mm slab x 70..86 through the latch, closure block,
//   hinge lug and pin - cut in CadQuery because OpenSCAD preview paints intersection() black);
//   open reads cnc-design/stl/open/ (the C2 set pre-rotated OPEN_DEG about the hinge pin).
view = "iso";
dir = view == "section" ? "section/" : "";
module part(f, c, t = [0, 0, 0], d = dir) { color(c) translate(t) import(str("../cnc-design/stl/", d, f, ".stl")); }
module c1side(e = 0) {
  part("C1_chassis_half", "#7A8A99");
  part("A1_top_box", "#C0C6CC", [0, 0, e]);
  part("A2_lid", "#E8ECEF", [0, 0, 2 * e]);
  part("A5_window_insert", "#1E1E1E", [0, 0, 2.6 * e]);
  part("A3_bottom_box", "#B0B8BF", [0, 0, -e]);
  part("A4_cover_plate", "#D8DDE2", [0, 0, -2 * e]);
  part("hinge_pin", "#404040", [1.6 * e, 0, 0]);
  part("liner_right", "#2E2E2E", [0, 0.5 * e, 0]);
}
module c2side(dy = 0, d = dir) {
  part("C2_clamp_half", "#5A6A79", [0, dy, 0], d);
  part("closure_block", "#D95D39", [0, dy, 0], d);
  part("hinge_block", "#D95D39", [0, dy, 0], d);
  part("liner_left", "#2E2E2E", [0, dy, 0], d);
}
if (view == "iso" || view == "end" || view == "section") { c1side(0); c2side(); }
if (view == "exploded") { c1side(22); c2side(-30); }
if (view == "open") { c1side(0); c2side(0, "open/"); color("#9BB7A0", 0.9) translate([-5, -44.6, 17.8]) rotate([0, 90, 0]) cylinder(h = 160, d = 46, $fn = 96); }
