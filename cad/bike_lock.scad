// =====================================================================
// RFID Bike Lock — parametric housing, v0.1 DRAFT geometry
// Matches DESIGN.md rev 0.1 (§6). Units: mm.
//
// DRAFT means: correct architecture and dimensions per the design doc,
// but not yet test-printed. Items marked VERIFY need a measurement of
// the real purchased part before printing that piece. Items marked
// TODO are simplifications to refine after the first fit-check print.
//
// Open in OpenSCAD. Pick what to render/export with the `part`
// variable (Customizer panel), then F6 + STL export.
// =====================================================================

// ---------------- what to render ----------------
part = "assembly"; // ["assembly", "shell_right", "shell_left", "lid", "liner_right", "liner_left", "shim", "spool_cover", "section_latch", "section_clamp"]

// ---------------- global quality ----------------
$fn = 96;
eps = 0.01;

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
z_lidtop = z_lid0 + lid_t;
pod_ox = pod_ix + 2*pod_wall;
pod_oy = pod_iy + 2*pod_wall;

// ---------------- latch (§6.4) ----------------
bore_d      = 11;    // receiver bore for the cable head
bore_depth  = 26;    // measured down from the lid TOP surface
bore_x      = 58;                    // from front end (X=0)
bore_y      = -pod_iy/2 + 14;        // drive strip line (≈ -13.5)
boss_d      = bore_d + 8;
pin_d       = 4.2;                   // Ø4 hardened pin, clearance
head_seat   = 9;                     // groove center below lid top when seated
pin_z       = z_lidtop - head_seat;  // pin/plunger axis height
closure_screw_d = 4.4;               // M4 clearance at bore bottom
// solenoid (JF-0530B: body 30 x 13 x 15, plunger Ø6 x 58)
sol_x0        = 66;                  // body front face (plunger toward bore)
sol_len       = 30;
sol_w         = 13.4;
sol_h         = 15;
sol_axis_h    = 7.5;   // VERIFY: plunger axis above solenoid base
sol_hole_dx   = 24;    // VERIFY: mounting hole spacing of your unit
sol_hole_d    = 2.2;   // self-tap M2.5
ped_top       = pin_z - sol_axis_h;  // pedestal top so plunger aligns with pin

// ---------------- lid features (§6.5) ----------------
pn532_x  = 2;                        // PCB pocket from front
pn532_l  = 43.2;  pn532_w = 41.0;    // VERIFY vs your board
window_remain = 1.2;                 // plastic left over the antenna
button_d = 12.4;  button_x = 52;  button_y = 12;   // VERIFY thread Ø
led_d    = 3.3;
usb_slot_w = 10;  usb_slot_h = 4;    // USB-C through rear wall
usb_y = 15;                          // battery-side (global +Y)
usb_z = z_crown + 12;
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
hinge_cz   = -R_out - hinge_od/2 + 2;   // knuckle center, mostly proud of shell
// knuckle X spans [start, end] — interleaved between halves, gap at the drum
hinge_right = [[6,20],[34,48],[102,116],[130,144]];
hinge_left  = [[20,34],[48,58],[96,102],[116,130]];
hinge_gap   = 0.4;

// ---------------- closure: suitcase-lip joint (§6.4) ----------------
// The clamshell closes on the bottom hinge; the LEFT half's flange wall
// rises past the crown and its inward lip hooks over the RIGHT half's
// pod-floor ledge as it closes. The hidden M4 at the bore bottom clamps
// the left half's screw pad up against the pod floor — the joint cannot
// rotate open until that screw is removed, and the screw is covered by
// the locked cable head.
lip_h   = 8;     // flange rise above crown
lip_t   = 4;     // flange wall thickness
lip_in  = 4;     // how far the lip reaches inward (+Y)
clr     = 0.5;   // rotational-entry clearance   TODO: tune after print
pad_l   = 26;    // screw pad under the bore
pad_w   = 16;
pad_h   = 6;

// =====================================================================
// helpers
// =====================================================================
module tube_bore() { rotate([0,90,0]) translate([0,0,-1]) cylinder(r=R_in, h=shell_len+2); }
module outer_cyl(extra=0) { rotate([0,90,0]) translate([0,0,-1]) cylinder(r=R_out+extra, h=shell_len+2); }

module knuckles(spans) {
    for (s = spans) translate([s[0], 0, hinge_cz]) rotate([0,90,0]) cylinder(d=hinge_od, h=s[1]-s[0]);
}
module knuckle_clearance(spans) { // carve room for the OTHER half's knuckles
    for (s = spans) translate([s[0]-hinge_gap, 0, hinge_cz]) rotate([0,90,0]) cylinder(d=hinge_od+2*hinge_gap, h=s[1]-s[0]+2*hinge_gap);
}
module hinge_drill() { translate([-1, 0, hinge_cz]) rotate([0,90,0]) cylinder(d=hinge_hole, h=shell_len+2); }

// =====================================================================
// SHELL HALVES. Split plane: vertical (X-Z). Right = +Y (top pod, latch,
// solenoid, spool drum). Left = -Y (lip flange, screw pad, spool cover).
// =====================================================================

module half_cyl(right=true) {
    intersection() {
        difference() { outer_cyl(); tube_bore(); }
        if (right) translate([-2, 0, -R_out-drum_od]) cube([shell_len+4, R_out+2, 2*(R_out+drum_od)]);
        else       translate([-2, -R_out-2, -R_out-drum_od]) cube([shell_len+4, R_out+2, 2*(R_out+drum_od)]);
    }
}

module pod_walls() {
    difference() {
        translate([-pod_wall, -pod_oy/2, 0]) cube([pod_ox, pod_oy, z_lid0]);
        translate([0, -pod_iy/2, -eps]) cube([pod_ix, pod_iy, z_lid0+1]);   // interior
        translate([0,0,-eps]) scale([1,1,1]) outer_cyl();                    // don't fill the tube zone
    }
}
module pod_cavity() { // interior volume above the curved shell surface
    difference() {
        translate([0, -pod_iy/2, 0]) cube([pod_ix, pod_iy, z_lid0 + eps]);
        outer_cyl();
    }
}

module drum() {
    translate([drum_x - drum_w/2, 0, drum_cz]) rotate([0,90,0])
        difference() {
            cylinder(d=drum_od, h=drum_w);
            translate([0,0,drum_wall]) cylinder(d=drum_od-2*drum_wall, h=drum_w+2); // open toward +X
        }
}
module drum_drills() {
    // cable exit at the drum bottom, 30° off vertical (DESIGN.md §6.3)
    translate([drum_x, 0, drum_cz]) rotate([30,0,0]) translate([0,0,-drum_od/2-4]) cylinder(d=cable_exit_d, h=drum_wall+8);
    // three M3 heat-set pockets in the open (+X) rim face
    for (a = [30, 150, 270])
        translate([drum_x + drum_w/2 - 7, (drum_od/2 - drum_wall/2 - 2.5)*cos(a), drum_cz + (drum_od/2 - drum_wall/2 - 2.5)*sin(a)])
            rotate([0,90,0]) cylinder(d=4.0, h=8);
}

// ---- right-half interior fittings (added AFTER cavity subtraction) ----
module latch_boss() {
    difference() {
        translate([bore_x, bore_y, 0]) cylinder(d=boss_d, h=z_lid0);
        tube_bore();
        translate([bore_x, bore_y, z_lidtop - bore_depth]) cylinder(d=bore_d, h=bore_depth+2);  // receiver bore
        translate([bore_x, bore_y, -R_out]) cylinder(d=closure_screw_d, h=z_lid0+2);            // closure screw shaft
        translate([bore_x, bore_y, pin_z]) rotate([0,90,0]) cylinder(d=pin_d, h=boss_d);        // pin channel → +X
        // spring pocket behind the pin exit (between boss and solenoid)
        translate([bore_x + boss_d/2 - 2, bore_y, pin_z]) rotate([0,90,0]) cylinder(d=pin_d+3, h=4);
    }
}
module solenoid_pedestal() {
    difference() {
        translate([sol_x0 - 3, bore_y - sol_w/2 - 3, 0]) cube([sol_len + 6, sol_w + 6, ped_top]);
        tube_bore();
        for (dx = [sol_len/2 - sol_hole_dx/2, sol_len/2 + sol_hole_dx/2])
            translate([sol_x0 + dx, bore_y, ped_top - 12]) cylinder(d=sol_hole_d, h=13);
    }
}

// ---- closure joint geometry ----
module right_ledge() { // pod floor edge ledge the lip hooks over (-Y side)
    difference() {
        translate([-pod_wall, -pod_oy/2 - lip_t - clr, z_crown + lip_h - 2]) cube([pod_ox, lip_t + clr + pod_wall, 5]);
        translate([-pod_wall-1, -pod_oy/2 - lip_t - clr - 1, z_crown + lip_h - 2 - eps]) cube([pod_ox + 2, lip_t + clr + 1, 2.5]); // undercut the lip snaps into
    }
}
module left_lip() {
    // flange wall rising from the left shell edge, with inward lip
    translate([0, -pod_oy/2 - lip_t, -2]) cube([shell_len, lip_t, 2 + z_crown + lip_h]);
    translate([0, -pod_oy/2 - lip_t, z_crown + lip_h - 2]) cube([shell_len, lip_t + lip_in, 2]);
    // screw pad under the bore — the hidden M4's target
    translate([bore_x - pad_l/2, bore_y - pad_w/2, z_crown - 2]) cube([pad_l, pad_w, pad_h]);
    // strut connecting pad to the flange wall
    translate([bore_x - pad_l/2, -pod_oy/2 - lip_t, z_crown - 2]) cube([pad_l, pod_oy/2 - abs(bore_y) + lip_t + pad_w/2, 4]);
}
module left_lip_drills() {
    translate([bore_x, bore_y, z_crown - 3]) cylinder(d=5.6, h=pad_h + 4);  // M4 heat-set pocket
}
module pad_pocket() { // clearance in the right half's pod floor for pad + strut
    translate([bore_x - pad_l/2 - clr, -pod_oy - 1, z_crown - 2 - clr]) cube([pad_l + 2*clr, pod_oy + 1 - abs(bore_y) + pad_w/2 + clr, pad_h + 2*clr]);
}

module camlock_drill() { // §8 backstop, front pod wall near the latch
    translate([bore_x, -pod_oy/2 - lip_t - 1, z_crown + pod_h*0.62]) rotate([-90,0,0]) cylinder(d=camlock_d, h=pod_wall + lip_t + 3);
}
module usb_drill() {
    translate([pod_ix - 1, usb_y - usb_slot_w/2, usb_z]) cube([2*pod_wall + 2, usb_slot_w, usb_slot_h]);
}

module lid_bosses() {
    for (cx = [5, pod_ix - 5]) for (cy = [-pod_iy/2 + 5, pod_iy/2 - 5])
        translate([cx, cy, z_lid0 - 12]) difference() {
            translate([-5, -5, 0]) cube([10, 10, 12]);
            translate([0, 0, 2]) cylinder(d=2.6, h=11); // M3 self-tap pilot
        }
}

module shell_right() {
    union() {
        difference() {
            union() { half_cyl(true); pod_walls(); drum(); knuckles(hinge_right); right_ledge(); }
            pod_cavity();
            pad_pocket();
            knuckle_clearance(hinge_left);
            hinge_drill();
            drum_drills();
            camlock_drill();
            usb_drill();
            // bore + screw continue through the pod floor / shell crown
            translate([bore_x, bore_y, -R_out]) cylinder(d=closure_screw_d, h=z_lid0+2);
            tube_bore();
        }
        latch_boss();
        solenoid_pedestal();
        lid_bosses();
    }
}

module shell_left() {
    difference() {
        union() { half_cyl(false); left_lip(); knuckles(hinge_left); }
        left_lip_drills();
        knuckle_clearance(hinge_right);
        hinge_drill();
        tube_bore();
    }
}

module spool_cover() { // face plate for the drum's open (+X) rim
    // local frame: printed flat; in the assembly local +Z faces global +X,
    // local -X faces global +Z (the frame tube sits at local (drum_cz, 0)).
    difference() {
        cylinder(d=drum_od, h=3);
        for (a = [30, 150, 270])
            translate([(drum_od/2 - drum_wall/2 - 2.5)*cos(a), (drum_od/2 - drum_wall/2 - 2.5)*sin(a), -1]) cylinder(d=3.4, h=5);
        translate([0,0,-1]) cylinder(d=12, h=5); // center hole for spool axle stub
        translate([drum_cz, 0, -1]) cylinder(r=R_in + 0.4, h=5);       // clear the frame tube
        translate([drum_cz - hinge_cz, 0, -1]) cylinder(d=3.6, h=5);   // hinge pin passes through (and retains the cover)
    }
}

// =====================================================================
// LID — TODO(security): v0 uses 4 exposed corner M3 screws; fine for the
// prototype (they expose electronics, not the frame closure).
// =====================================================================
module lid() {
    difference() {
        translate([-pod_wall, -pod_oy/2, 0]) cube([pod_ox, pod_oy, lid_t]);
        translate([pn532_x, -pn532_w/2, -eps]) cube([pn532_l, pn532_w, lid_t - window_remain]); // PN532 pocket, RF skin stays on top
        translate([bore_x, bore_y, -1]) cylinder(d=bore_d + 0.6, h=lid_t + 2);
        translate([button_x, button_y, -1]) cylinder(d=button_d, h=lid_t + 2);
        translate([button_x, -2, -1])  cylinder(d=led_d, h=lid_t + 2);
        translate([button_x, -8, -1]) cylinder(d=led_d, h=lid_t + 2);
        for (cx = [5, pod_ix - 5]) for (cy = [-pod_iy/2 + 5, pod_iy/2 - 5])
            translate([cx, cy, -1]) cylinder(d=3.4, h=lid_t + 2);
    }
}

// =====================================================================
// LINER — TPU 95A half-sleeves with leaning fins (§6.2). Free bore ≈ Ø30.
// =====================================================================
module liner_2d() {
    union() {
        difference() { circle(r=R_in - 0.15); circle(r=R_in - liner_base); }
        for (i = [0 : fin_n-1])
            rotate([0, 0, i*360/fin_n])
                translate([R_in - 0.15 - liner_base, 0])
                    rotate([0, 0, 180 - fin_lean])
                        translate([0, -fin_t/2]) square([fin_h + liner_base, fin_t]);
    }
}
module liner_half(right=true) {
    rotate([0,90,0]) rotate([0,0,90]) // put the half split on the X-Z plane
        linear_extrude(height=shell_len)
            intersection() {
                liner_2d();
                if (right) translate([-2*R_in, -2*R_in]) square([2*R_in, 4*R_in]);
                else       translate([0, -2*R_in]) square([2*R_in, 4*R_in]);
            }
    // TODO: dovetail keys into the shell; v0 = friction + adhesive dabs.
}

// SHIM for Ø27–32 tubes: TPU C-ring with short fins (v0 approximation).
module shim() {
    shim_R = 15;
    rotate([0,90,0]) linear_extrude(height=shell_len)
        intersection() {
            union() {
                difference() { circle(r=shim_R); circle(r=shim_R - 3); }
                for (i = [0 : 11]) rotate([0, 0, i*30])
                    translate([shim_R - 3, 0]) rotate([0, 0, 180 - fin_lean]) translate([0, -0.6]) square([7, 1.2]);
            }
            rotate([0,0,210]) difference() { circle(r=shim_R+1); wedge(); } // 300° C-ring
        }
}
module wedge() { polygon([[0,0],[100,0],[100,-100],[0,-100],[0,-1],[87,-50]]); } // 60° cutout helper

// =====================================================================
// render selector
// =====================================================================
module assembly() {
    color("SteelBlue")  shell_right();
    color("SkyBlue")    shell_left();
    color("Gainsboro")  translate([0, 0, z_lid0]) lid();
    color("DimGray")    liner_half(true);
    color("DarkGray")   liner_half(false);
    color("LightGray")  translate([drum_x + drum_w/2, 0, drum_cz]) rotate([0,90,0]) spool_cover();
}

if (part == "shell_right") shell_right();
if (part == "shell_left")  shell_left();
if (part == "lid")         lid();
if (part == "liner_right") liner_half(true);
if (part == "liner_left")  liner_half(false);
if (part == "shim")        shim();
if (part == "spool_cover") spool_cover();
if (part == "assembly")    assembly();
// diagnostic cuts
if (part == "section_latch")  intersection() { assembly(); translate([bore_x - 60, bore_y - 0.5, -R_out - 5]) cube([120, 40, z_lidtop + R_out + 10]); }
if (part == "section_clamp")  intersection() { assembly(); translate([20, -100, -200]) cube([1.5, 200, 400]); }

// sanity echoes
echo("free liner bore Ø ≈", 2*(R_in - liner_base - fin_h*cos(fin_lean)));
echo("pin/plunger axis z =", pin_z, " pedestal top z =", ped_top);
echo("bore bottom z =", z_lidtop - bore_depth, " (screw head sits below this)");
echo("drum lowest z =", drum_cz - drum_od/2);
