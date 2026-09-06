// CNC casing renders (cad/cnc_casing_cq.py parts). Variables:
//   view = iso | exploded | end | section | open | interior
//   section reads cnc-design/stl/section/ (16 mm slab through the latch - cut in CadQuery because
//   OpenSCAD preview paints intersection() black); open reads cnc-design/stl/open/ (C2 set pre-rotated).
//   interior = A1 with the lid + insert removed, electronics reference bodies coloured.
view = "iso";
dir = view == "section" ? "section/" : "";
module part(f, c, t = [0, 0, 0], d = dir) { color(c) translate(t) import(str("../cnc-design/stl/", d, f, ".stl")); }
module refs(e = 0) {
  part("ref_tray", "#B9A46B", [0, 0, e]);          part("ref_battery", "#3B6FB6", [0, 0, e]);
  part("ref_reader", "#2E8B57", [0, 0, e]);        part("ref_cart_module", "#E8842A", [0, 0, e]);
  part("ref_plunger", "#C8CDD2", [0, 0, e]);       part("ref_nano", "#2F6F8F", [0, 0, e]);
  part("ref_tp4056", "#8B3A62", [0, 0, e]);        part("ref_mt3608", "#4F7942", [0, 0, e]);
  part("ref_button", "#333333", [0, 0, e]);        part("ref_led_1", "#D33", [0, 0, e]); part("ref_led_2", "#3C3", [0, 0, e]);
}
module c1side(e = 0, lid = true) {
  part("C1_chassis_half", "#7A8A99");
  part("A1_top_box", "#C0C6CC", [0, 0, e]);
  if (lid) { part("A2_lid", "#E8ECEF", [0, 0, 2 * e]); part("A5_window_insert", "#1E1E1E", [0, 0, 2.6 * e]); }
  part("A3_bottom_box", "#B0B8BF", [0, 0, -e]);
  part("A4_cover_plate", "#D8DDE2", [0, 0, -2 * e]);
  part("hinge_pin", "#404040", [1.6 * e, 0, 0]);
  part("liner_right", "#2E2E2E", [0, 0.5 * e, 0]);
  refs(e);
}
module c2side(dy = 0, d = dir) {
  part("C2_clamp_half", "#5A6A79", [0, dy, 0], d);
  part("closure_block", "#D95D39", [0, dy, 0], d);
  part("hinge_block", "#D95D39", [0, dy, 0], d);
  part("liner_left", "#2E2E2E", [0, dy, 0], d);
}
if (view == "iso" || view == "end" || view == "section") { c1side(0); c2side(); }
if (view == "exploded") { c1side(22); c2side(-30); }
if (view == "open") { c1side(0); c2side(0, "open/"); color("#9BB7A0", 0.9) rotate([0, 90, 0]) translate([0, -60, -5]) cylinder(h = 160, d = 46, $fn = 96); }
if (view == "interior") { c1side(0, false); c2side(); }
