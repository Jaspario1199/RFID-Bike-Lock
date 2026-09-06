// CNC casing renders (cad/cnc_casing_cq.py parts). Variables:
//   view    = iso | exploded | end | install | section
//   station = install only: 0 = C2 slid out 30 mm and RISE low, 1 = in, still low, 2 = home (screw tight)
//   cut     = use the 16 mm slab-sectioned STLs through the latch / closure block / K hook (section view)
view = "iso"; station = 2; cut = false;
RISE = 2.5;
// cut=true reads pre-sectioned STLs (cnc-design/stl/section/, a 16 mm slab x 70..86 cut in CadQuery) -
// OpenSCAD preview paints intersection() results black, so the slab is cut upstream.
module part(f, c, t = [0, 0, 0]) { color(c) translate(t) import(str("../cnc-design/stl/", cut ? "section/" : "", f, ".stl")); }
module c1side(e = 0) {
  part("C1_chassis_half", "#7A8A99");
  part("A1_top_box", "#C0C6CC", [0, 0, e]);
  part("A2_lid", "#E8ECEF", [0, 0, 2 * e]);
  part("A5_window_insert", "#1E1E1E", [0, 0, 2.6 * e]);
  part("A3_bottom_box", "#B0B8BF", [0, 0, -e]);
  part("A4_cover_plate", "#D8DDE2", [0, 0, -2 * e]);
  part("liner_right", "#2E2E2E", [0, 0.5 * e, 0]);
}
module c2side(dy = 0, dz = 0) {
  part("C2_clamp_half", "#5A6A79", [0, dy, dz]);
  part("closure_block", "#D95D39", [0, dy, dz]);
  part("K_hook_block", "#D95D39", [0, dy, dz]);
  part("liner_left", "#2E2E2E", [0, dy, dz]);
}
if (view == "iso" || view == "end" || view == "section") { c1side(0); c2side(); }
if (view == "exploded") { c1side(22); c2side(-30, 0); }
if (view == "install") {
  c1side(0);
  if (station == 0) c2side(-30, -RISE);
  if (station == 1) c2side(0, -RISE);
  if (station == 2) c2side(0, 0);
}
