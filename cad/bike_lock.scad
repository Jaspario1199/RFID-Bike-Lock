// =====================================================================
// RFID Bike Lock — parametric housing, v0 DRAFT geometry
// Matches DESIGN.md rev 0.1 (§6). Units: mm.
//
// DRAFT means: correct architecture and dimensions per the design doc,
// but nothing has been test-printed yet. Items marked VERIFY need a
// measurement of the real purchased part before printing that piece.
// Items marked TODO are simplifications to refine after the first
// fit-check print.
//
// Open in OpenSCAD (openscad.org). Pick what to render/export with the
// `part` variable below (use the Customizer panel), then F6 + STL export.
// =====================================================================

// ---------------- what to render ----------------
part = "assembly"; // ["assembly", "shell_right", "shell_left", "lid", "liner_right", "liner_left", "shim", "spool_cover"]

// ---------------- global quality ----------------
$fn = 96;

// ---------------- core parameters (DESIGN.md §6.1) ----------------
shell_id     = 54;    // clamp bore over the liner
shell_wall   = 4;     // printed wall (steel version: 1.5)
shell_len    = 150;   // clamp length = pod length
R_in  = shell_id/2;           // 27
R_out = R_in + shell_wall;    // 31

// ---------------- top pod (§6.5) ----------------
pod_ix   = 150;   // interior length (X, along frame axis)
pod_iy   = 55;    // interior width  (Y)
pod_wall = 3;
pod_h    = 34;    // lid underside above shell crown
lid_t    = 3;
z_crown  = R_out;             // top of shell
z_lid0   = z_crown + pod_h;   // lid underside
pod_ox = pod_ix + 2*pod_wall;
pod_oy = pod_iy + 2*pod_wall;

// ---------------- latch (§6.4) ----------------
bore_d      = 11;    // receiver bore for the cable head
bore_depth  = 26;
bore_x      = 58;                    // from front end (X=0)
bore_y      = -pod_iy/2 + 14;        // drive strip line, Y≈14 from wall
boss_d      = bore_d + 8;
pin_d       = 4.2;                   // Ø4 hardened pin, clearance
pin_z       = z_lid0 - 9;            // groove height when head is seated
closure_screw_d = 4.4;               // M4 clearance at bore bottom
// solenoid (JF-0530B: body 30x13x15, plunger Ø6x58)
sol_x0        = 64;                  // body front face
sol_len       = 30;
sol_w         = 13.4;
sol_hole_dx   = 24;    // VERIFY: mounting hole spacing of your unit
sol_hole_d    = 2.2;   // self-tap M2.5

// ---------------- lid features (§6.5) ----------------
pn532_x  = 2;                        // PCB pocket from front
pn532_l  = 43.2;  pn532_w = 41.0;  pn532_t = 4.6;  // VERIFY vs your board
window_remain = 1.2;                 // plastic left over the antenna
button_d = 12.4;  button_x = 52;  button_y = 10;   // VERIFY thread Ø
led_d    = 3.3;
usb_slot_w = 10;  usb_slot_h = 4;    // USB-C through rear wall
usb_y = 15;                          // battery-side (global +Y)
camlock_d = 16.4;                    // VERIFY: panel hole of your cam lock

// ---------------- liner (§6.2, print in TPU 95A) ----------------
fin_n     = 24;
fin_h     = 12;
fin_t     = 1.4;
fin_lean  = 30;    // degrees off radial
liner_base = 2;

// ---------------- spool pod (§6.3) ----------------
drum_od   = 95;
drum_w    = 34;         // along X
drum_wall = 3;
drum_x    = 75;         // centered on shell
drum_overlap = 8;       // how far drum merges up into shell bottom
drum_cz   = -(R_out + drum_od/2 - drum_overlap);
cable_exit_d = 8;

// ---------------- hinge (bottom seam) ----------------
hinge_od   = 8;
hinge_hole = 3.2;      // Ø3 stainless pin
// knuckle X spans [start, end] — gaps interleave the other half's
hinge_right = [[8,22],[36,50],[100,114],[128,142]];
hinge_left  = [[22,36],[50,58],[92,100],[114,128]];

// ---------------- hook joint (top seam, §6.4) ----------------
hook_h = 6;      // tongue rise above crown
hook_t = 4;      // tongue thickness
// TODO: 3 preload detent depths — v0 uses a single snug slot;
// detents get added after the first on-bike fit check.

// ---------------- small helpers ----------------
module knuckles(spans, y_side) {
    for (s = spans)
        translate([s[0], 0, -R_out + hinge_od/2 - 1])
            rotate([0,90,0])
                cylinder(d=hinge_od, h=s[1]-s[0]);
}
module hinge_drill() {
    translate([-1, 0, -R_out + hinge_od/2 - 1])
        rotate([0,90,0]) cylinder(d=hinge_hole, h=shell_len+2);
}

// =====================================================================
// SHELL HALVES.  Split plane: vertical (X-Z).  Right = +Y (carries top
// pod and spool drum), Left = -Y (carries hook tongue and spool cover).
// =====================================================================

module shell_tube() {
    difference() {
        cylinder(r=R_out, h=shell_len);
        translate([0,0,-1]) cylinder(r=R_in, h=shell_len+2);
    }
}

// oriented: axis along X, so rotate the native Z cylinder
module shell_tube_x() { rotate([0,90,0]) shell_tube(); }

module pod_outer() {
    translate([-pod_wall, -pod_oy/2, z_crown-6])
        cube([pod_ox, pod_oy, 6 + pod_h + 0]); // walls stop at lid plane
}
module pod_cavity() {
    difference() {
        translate([0, -pod_iy/2, 0])
            // tall so it also cuts the lid seat opening
            cube([pod_ix, pod_iy, z_lid0 + 20]);
        // floor follows the curved shell outer surface
        rotate([0,90,0]) translate([0,0,-1]) cylinder(r=R_out, h=shell_len+2);
    }
}

module latch_boss() {
    translate([bore_x, bore_y, 0])
        cylinder(d=boss_d, h=z_lid0);   // column floor→lid; floor merge via union
}
module latch_drills() {
    translate([bore_x, bore_y, z_lid0 - bore_depth])
        cylinder(d=bore_d, h=bore_depth + lid_t + 2);          // receiver bore
    translate([bore_x, bore_y, -R_out-1])
        cylinder(d=closure_screw_d, h=z_lid0);                 // closure screw shaft
    // pin channel: from bore wall toward solenoid (+X), at groove height
    translate([bore_x, bore_y, pin_z])
        rotate([0,90,0]) cylinder(d=pin_d, h=(sol_x0 - bore_x) + 2);
}

module solenoid_pedestal() {
    difference() {
        translate([sol_x0-3, bore_y - sol_w/2 - 3, z_crown-8])
            cube([sol_len+6, sol_w+6, 10]);
        for (dx = [sol_len/2 - sol_hole_dx/2, sol_len/2 + sol_hole_dx/2])
            translate([sol_x0+dx, bore_y, z_crown-8])
                cylinder(d=sol_hole_d, h=14);
    }
}

module camlock_drill() { // v1 backstop (§8), side wall near the latch
    translate([bore_x, -pod_oy/2-1, z_crown + pod_h/2])
        rotate([-90,0,0]) cylinder(d=camlock_d, h=pod_wall+2);
}
module usb_drill() {     // rear wall, battery side
    translate([pod_ix, usb_y - usb_slot_w/2, z_crown + 12])
        cube([pod_wall+2, usb_slot_w, usb_slot_h]);
}

module drum() {
    translate([drum_x - drum_w/2, 0, drum_cz]) rotate([0,90,0]) rotate([0,0,90])
        difference() {
            cylinder(d=drum_od, h=drum_w);
            translate([0,0,drum_wall]) cylinder(d=drum_od-2*drum_wall, h=drum_w+2);
        }
}
module drum_drills() {
    // cable exit: 30° off vertical at the bottom of the drum
    translate([drum_x, 0, drum_cz])
        rotate([30,0,0]) translate([0,0,-drum_od/2-2]) cylinder(d=cable_exit_d, h=drum_wall+6);
    // three M3 insert holes on the drum rim for the cover plate
    for (a = [30, 150, 270])
        translate([drum_x - drum_w/2 - 1, (drum_od/2-6)*cos(a), drum_cz + (drum_od/2-6)*sin(a)])
            rotate([0,90,0]) cylinder(d=4.0, h=8); // heat-set M3 pocket
}

module hook_tongue() { // on LEFT half: rises past crown, hooks toward +Y
    translate([0, -hook_t, z_crown-2]) cube([shell_len, hook_t, hook_h+2]);
    translate([0, -hook_t, z_crown+hook_h-2]) cube([shell_len, hook_t+5, hook_t]);
}
module hook_slot() {   // in RIGHT half pod floor: clearance for the tongue
    translate([-1, -hook_t-0.4, z_crown-2.2])
        cube([shell_len+2, hook_t+0.8, hook_h+2.4]);
    translate([-1, -hook_t-0.4, z_crown+hook_h-2.2])
        cube([shell_len+2, hook_t+5.8, hook_t+0.6]);
}

module shell_right() {
    difference() {
        union() {
            intersection() { shell_tube_x(); translate([-1,0,-R_out-drum_od]) cube([shell_len+2, R_out+1, 2*(R_out+drum_od)]); }
            pod_outer();
            latch_boss();
            solenoid_pedestal();
            drum();
            knuckles(hinge_right, 1);
        }
        pod_cavity();
        latch_drills();
        camlock_drill();
        usb_drill();
        drum_drills();
        hook_slot();
        hinge_drill();
        // reopen the tube bore where pod/boss unions crossed it
        rotate([0,90,0]) translate([0,0,-1]) cylinder(r=R_in, h=shell_len+2);
    }
}

module shell_left() {
    difference() {
        union() {
            intersection() { shell_tube_x(); translate([-1,-R_out-1,-R_out-drum_od]) cube([shell_len+2, R_out+1, 2*(R_out+drum_od)]); }
            hook_tongue();
            knuckles(hinge_left, -1);
        }
        hinge_drill();
        // M4 heat-set pocket in the tongue, under the bore (closure screw target)
        translate([bore_x, bore_y, z_crown-3]) cylinder(d=5.6, h=hook_h+6);
        rotate([0,90,0]) translate([0,0,-1]) cylinder(r=R_in, h=shell_len+2);
    }
}

module spool_cover() { // left face plate of the drum, 3x M3
    difference() {
        cylinder(d=drum_od, h=3);
        for (a = [30, 150, 270])
            translate([(drum_od/2-6)*cos(a), (drum_od/2-6)*sin(a), -1]) cylinder(d=3.4, h=5);
    }
}

// =====================================================================
// LID — slides onto the pod; PN532 pocket, window, button, LEDs, bore.
// TODO(security): v0 uses 4 corner M3 screws (exposed). Fine for the
// printed prototype; the steel version should switch to front-lip +
// rear screws under a trim strip.
// =====================================================================
module lid() {
    difference() {
        translate([-pod_wall, -pod_oy/2, 0]) cube([pod_ox, pod_oy, lid_t]);
        // PN532 pocket from below, leaving the RF window skin
        translate([pn532_x, -pn532_w/2, -0.01])
            cube([pn532_l, pn532_w, lid_t - window_remain]);
        // bore passes through the lid
        translate([bore_x, bore_y, -1]) cylinder(d=bore_d+0.6, h=lid_t+2);
        // button + LEDs
        translate([button_x, button_y, -1]) cylinder(d=button_d, h=lid_t+2);
        translate([button_x, -5, -1])  cylinder(d=led_d, h=lid_t+2);
        translate([button_x, -12, -1]) cylinder(d=led_d, h=lid_t+2);
        // 4 corner screws
        for (cx = [4, pod_ix-4]) for (cy = [-pod_iy/2+4, pod_iy/2-4])
            translate([cx, cy, -1]) cylinder(d=3.4, h=lid_t+2);
    }
}

// =====================================================================
// LINER — TPU 95A. Half-sleeves with leaning fins (§6.2).
// Free bore ≈ Ø30; grips Ø32–46 tubes.
// =====================================================================
module liner_2d() {
    union() {
        difference() { circle(r=R_in); circle(r=R_in - liner_base); }
        for (i = [0 : fin_n-1])
            rotate([0,0,i*360/fin_n])
                translate([R_in - liner_base, 0])
                    rotate([0,0,180-fin_lean])
                        translate([0,-fin_t/2]) square([fin_h + liner_base, fin_t]);
    }
}
module liner_half(right=true) {
    rotate([0,90,0])
        linear_extrude(height=shell_len)
            intersection() {
                liner_2d();
                if (right) translate([-2*R_in,0]) square([4*R_in, 2*R_in]);
                else       translate([-2*R_in,-2*R_in]) square([4*R_in, 2*R_in]);
            }
    // TODO: dovetail keys into the shell; v0 relies on friction + a dab
    // of contact adhesive at the ends.
}

// SHIM for Ø27–32 tubes: TPU C-ring with its own short fins.
// TODO: v0 approximation — clips inside the main fins as a C-spring.
module shim() {
    shim_R = 15; // outer radius ≈ main-fin bore
    rotate([0,90,0]) linear_extrude(height=shell_len)
        intersection() {
            union() {
                difference() { circle(r=shim_R); circle(r=shim_R-3); }
                for (i = [0 : 11]) rotate([0,0,i*30])
                    translate([shim_R-3,0]) rotate([0,0,180-fin_lean])
                        translate([0,-0.6]) square([4+3, 1.2]);
            }
            rotate([0,0,-60]) polygon([[0,0],[100,0],[100,100],[-87,100],[-87,50]]); // ~300° C-ring
        }
}

// =====================================================================
// render selector
// =====================================================================
if (part == "shell_right") shell_right();
if (part == "shell_left")  shell_left();
if (part == "lid")         lid();
if (part == "liner_right") liner_half(true);
if (part == "liner_left")  liner_half(false);
if (part == "shim")        shim();
if (part == "spool_cover") spool_cover();
if (part == "assembly") {
    color("SteelBlue")  shell_right();
    color("SkyBlue")    shell_left();
    color("Gainsboro")  translate([0,0,z_lid0]) lid();
    color("DimGray")    liner_half(true);
    color("DimGray")    liner_half(false);
    color("LightGray")  translate([drum_x - drum_w/2 - 3, 0, drum_cz]) rotate([0,90,0]) rotate([0,0,90]) spool_cover();
}

// quick sanity echoes
echo("free liner bore Ø ≈", 2*(R_in - liner_base - fin_h*cos(fin_lean)));
echo("pod exterior:", pod_ox, "x", pod_oy, " lid plane z =", z_lid0);
echo("drum center z =", drum_cz, " lowest point z =", drum_cz - drum_od/2);
