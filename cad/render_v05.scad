// v0.5 assembly preview — composites the CadQuery-exported STLs.
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
    color("#455A64") translate([4, 27.5, -58 - 2.5 - 2.2*e]) import("stl/bay_hatch.stl");
    color("#D95D39") translate([0, 0, e]) import("stl/pedestal_cart.stl");
    color("#3A3A3A") import("stl/liner_right.stl");
    color("#AEB4BA") translate([98, 36.1 + 1.5*e, -60]) rotate([-90, 0, 0]) import("stl/spool_cover.stl");
}
// ghost tube to show the clamp target in the open view
module tube_ghost() { color("#88AA88", 0.5) rotate([0, 90, 0]) translate([0,0,-15]) cylinder(d=42, h=180); }

if (view == "closed")  { fixed_set(0); door_at(0); }
if (view == "open")    { fixed_set(0); door_at(95); tube_ghost(); }
if (view == "exploded"){ fixed_set(24); door_at(50); }
