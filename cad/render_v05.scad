// v0.6 assembly preview — composites the CadQuery-exported STLs.
view = "closed"; // ["closed", "open", "exploded"]
hinge_z = -33;

module door_at(angle) {
    translate([0, 0, hinge_z]) rotate([angle, 0, 0]) translate([0, 0, -hinge_z]) {
        color("#3D5A73") import("stl/door.stl");
        color("#454545") import("stl/liner_left.stl");
    }
}
module fixed_set(e=0) {
    color("#2E4057") import("stl/body.stl");
    color("#C8CDD2") translate([0, 0, 53 + 1.6*e]) import("stl/lid.stl");
    color("#22303C") translate([0, e, -1.2*e]) import("stl/bay_module.stl");
    color("#455A64") translate([4, 27.5, -58 - 3.0 - 2.2*e]) import("stl/bay_hatch.stl");
    color("#D95D39") translate([0, 0, e]) import("stl/pedestal_cart.stl");
    color("#3A3A3A") import("stl/liner_right.stl");
    color("#AEB4BA") translate([98, 36.1 + 1.5*e, -60]) rotate([-90, 0, 0]) import("stl/spool_cover.stl");
    // v0.6: single hinge rod + screwed tail cap (replace glued end plugs), spine cover
    color("#C2C6CB") translate([-1.4*e, 0, 0]) import("stl/hinge_rod.stl");
    color("#4C6172") translate([1.8*e, 0, 0]) import("stl/hinge_cap.stl");
    color("#4C6172") translate([0, 0.9*e, 1.4*e]) import("stl/spine_cover.stl");
    color("#D95D39") translate([0, 0.5*e, -1.6*e]) import("stl/perf_rack.stl");
    color("#D95D39") translate([0, -0.4*e, 1.2*e]) import("stl/nano_clamp.stl");
    // electronics reference bodies (green PCBs / grey cell+solenoid)
    color("#22703A") translate([0, -0.7*e, 0.8*e]) import("stl/mock_nano.stl");
    color("#22703A") translate([0, 0.6*e, -1.9*e]) import("stl/mock_perf_stack.stl");
    color("#22703A") translate([0, 0.3*e, -2.2*e]) import("stl/mock_tp4056.stl");
    color("#22703A") translate([0, 0, 0.9*e]) import("stl/mock_pn532.stl");
    color("#22703A") translate([0, 0.8*e, 0.6*e]) import("stl/mock_mt3608.stl");
    color("#8A8F96") translate([0, 1.1*e, -1.4*e]) import("stl/mock_lipo.stl");
    color("#6E7480") translate([0, 0, 0.5*e]) import("stl/mock_solenoid.stl");
    color("#26262A") import("stl/mock_button.stl");
}
// ghost tube to show the clamp target in the open view
module tube_ghost() { color("#88AA88", 0.5) rotate([0, 90, 0]) translate([0,0,-15]) cylinder(d=42, h=180); }

if (view == "closed")  { fixed_set(0); door_at(0); }
if (view == "open")    { fixed_set(0); door_at(95); tube_ghost(); }
if (view == "exploded"){ fixed_set(24); door_at(50); }