// Assembly preview for the v0.3 CadQuery build — composites the exported STLs.
// Not a source file: geometry lives in bike_lock_cq.py. Render with:
//   openscad -o renders/assembly_hero.png -D 'view="assembly"' render_v03.scad ...
view = "assembly"; // ["assembly", "exploded", "modules"]

PAD_Z = 32;

module place_cartridges(explode=0) {
    color("#D95D39") translate([0, 0, explode])      import("stl/pedestal_cart.stl");
    color("#D95D39") translate([0, 0, explode])      import("stl/driver_tray.stl");
    color("#D95D39") translate([82, 15, PAD_Z + explode])  import("stl/battery_saddle.stl");
    color("#D95D39") translate([118, 15, PAD_Z + explode]) import("stl/battery_saddle.stl");
    color("#D95D39") translate([140, 15, PAD_Z + explode]) import("stl/board_pocket.stl");
}

module core(explode=0) {
    color("#2E4057") import("stl/shell_right.stl");
    color("#3D5A73") translate([0, -explode, 0]) import("stl/shell_left.stl");
    color("#C8CDD2") translate([0, 0, 65 + 1.6*explode]) import("stl/lid.stl");
    color("#22303C") translate([0, 0, -1.4*explode]) import("stl/drum_module.stl");
    color("#3A3A3A") import("stl/liner_right.stl");
    color("#454545") translate([0, -explode, 0]) import("stl/liner_left.stl");
    color("#AEB4BA") translate([92 - 1.4*0, 0, -73.5 - 1.4*explode]) rotate([0, 90, 0]) import("stl/spool_cover.stl");
}

if (view == "assembly") { core(0); place_cartridges(0); }
if (view == "exploded") { core(26); place_cartridges(30); }
if (view == "modules")  { place_cartridges(0); color("#22303C") import("stl/drum_module.stl"); }
