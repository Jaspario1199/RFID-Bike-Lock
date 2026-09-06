view = "iso";
module all(explode=0) {
  color("#7A8A99") import("../cnc-design/stl/C1_chassis_half.stl");
  color("#5A6A79") translate([0,-explode,0]) import("../cnc-design/stl/C2_clamp_half.stl");
  color("#3A3A3A") translate([0,-explode,0]) import("../cnc-design/stl/closure_block.stl");
  color("#C0C6CC") translate([0,0,explode]) import("../cnc-design/stl/A1_top_box.stl");
  color("#E8ECEF") translate([0,0,2*explode]) import("../cnc-design/stl/A2_lid.stl");
  color("#B0B8BF") translate([0,0,-explode]) import("../cnc-design/stl/A3_bottom_box.stl");
  color("#2E2E2E") translate([0,0.5*explode,0]) import("../cnc-design/stl/liner_right.stl");
  color("#2E2E2E") translate([0,-1.5*explode,0]) import("../cnc-design/stl/liner_left.stl");
}
if (view=="iso") all(0);
if (view=="exploded") all(22);
if (view=="end") all(0);
