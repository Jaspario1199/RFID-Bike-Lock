// v0.4 assembly preview — composites the CadQuery-exported STLs.
view = "assembly"; // ["assembly", "exploded"]

module core(e=0) {
    color("#2E4057") import("stl/shell_right.stl");
    color("#3D5A73") translate([0, -e, 0]) import("stl/shell_left.stl");
    color("#C8CDD2") translate([0, 0, 53 + 1.6*e]) import("stl/lid.stl");
    color("#22303C") translate([0, 0, -1.5*e]) import("stl/bay_module.stl");
    color("#455A64") translate([8, 0, -60 - 2.5 - 2.4*e]) import("stl/bay_hatch.stl");
    color("#455A64") translate([96, 0, -60 - 2.5 - 2.4*e]) import("stl/bay_hatch.stl");
    color("#D95D39") translate([0, 0, e]) import("stl/pedestal_cart.stl");
    color("#3A3A3A") import("stl/liner_right.stl");
    color("#454545") translate([0, -e, 0]) import("stl/liner_left.stl");
    color("#AEB4BA") translate([92.2, 0, -73.5 - 1.5*e]) rotate([0, 90, 0]) import("stl/spool_cover.stl");
}
if (view == "assembly") core(0);
if (view == "exploded") core(26);
