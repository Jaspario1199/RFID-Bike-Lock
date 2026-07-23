// =====================================================================
// RFID Bike Lock — parametric housing, v0.2 (industrial-design pass)
// Matches DESIGN.md rev 0.1 (§6). Units: mm.
//
// v0.2 applies FDM design-for-manufacturing and product-design rules:
//   * one radius family: R14 belt / R11 pod corners / R3 details / 1.2 edge breaks
//   * drafted (tapering) pod walls, uniform ~3 mm wall thickness
//   * belt band wraps the body; the closure skirt IS the belt's left half,
//     so the part line is a design line (shadow gap), not an afterthought
//   * fairings blend pod->tube and drum->body (teardrop), overhangs <= 45°
//   * modeled wiring: floor raceways with clip lips, driver tray with wire
//     slot, battery cradles with zip-tie slots, strain-relief post
//
// VERIFY = measure your real part first.  TODO = refine after fit print.
// =====================================================================

// ---------------- what to render ----------------
part = "assembly"; // ["assembly", "shell_right", "shell_left", "lid", "liner_right", "liner_left", "shim", "spool_cover", "section_latch", "section_clamp", "section_wiring"]

$fn = 96;
eps = 0.01;

// ---------------- core (DESIGN.md §6.1) ----------------
shell_id   = 54;
shell_wall = 4;
shell_len  = 150;
R_in  = shell_id/2;
R_out = R_in + shell_wall;

// ---------------- top pod (§6.5) ----------------
pod_ix   = 150;
pod_iy   = 55;
pod_wall = 3;
pod_h    = 34;
lid_t    = 3;
z_crown  = R_out;
z_lid0   = z_crown + pod_h;
z_lidtop = z_lid0 + lid_t;
pod_ox   = pod_ix + 2*pod_wall;
pod_oy   = pod_iy + 2*pod_wall;
draft    = 1.8;    // pod side draft, base->lid (product taper + easy release)
r_pod    = 11;     // pod corner radius
r_belt   = 14;     // belt corner radius
edge     = 1.2;    // universal edge-break chamfer

// ---------------- belt band (closure skirt = its left half) ----------------
belt_t   = 4;                      // band stand-off each side
belt_z0  = 14;                     // bottom of band
belt_z1  = z_crown + 8;            // top of band (= lip hook height, 39)
belt_oy  = pod_oy + 2*belt_t;      // 69
gap      = 0.8;                    // shadow-gap groove width
clr      = 0.5;                    // closure engagement clearance  TODO tune

// ---------------- latch (§6.4) ----------------
bore_d      = 11;
bore_depth  = 26;
bore_x      = 58;
bore_y      = -pod_iy/2 + 14;
boss_d      = bore_d + 8;
pin_d       = 4.2;
head_seat   = 11.5;  // deep enough that solenoid body top (axis+7.5) clears the lid
pin_z       = z_lidtop - head_seat;
closure_screw_d = 4.4;
sol_x0      = 66;    sol_len = 30;   sol_w = 13.4;   sol_h = 15;
sol_axis_h  = 7.5;   // VERIFY
sol_hole_dx = 24;    // VERIFY
sol_hole_d  = 2.2;
ped_top     = pin_z - sol_axis_h;

// ---------------- lid features ----------------
pn532_x = 2;  pn532_l = 43.2;  pn532_w = 41.0;   // VERIFY board
window_remain = 1.2;
nfc_cx = 23.5;                       // embossed target ring center
button_d = 12.4;  button_x = 52;  button_y = 12; // VERIFY thread
led_d = 3.3;
usb_slot_w = 10;  usb_slot_h = 4;  usb_y = 15;  usb_z = z_crown + 12;
camlock_d = 16.4;                    // VERIFY

// ---------------- liner (§6.2) ----------------
fin_n = 24;  fin_h = 12;  fin_t = 1.4;  fin_lean = 30;  liner_base = 2;

// ---------------- spool pod (§6.3) ----------------
drum_od = 95;  drum_w = 34;  drum_wall = 3;  drum_x = 75;
drum_overlap = 5;                    // reduced: clamshell swing clearance
drum_cz = -(R_out + drum_od/2 - drum_overlap);
cable_exit_d = 8;

// ---------------- hinge ----------------
hinge_od = 8;  hinge_hole = 3.2;
hinge_cz = -R_out - hinge_od/2 + 2;
hinge_right = [[6,20],[34,48],[102,116],[130,144]];
hinge_left  = [[20,34],[48,58],[96,102],[116,130]];
hinge_gap = 0.4;

// ---------------- closure pad ----------------
lip_in = 4;  pad_l = 26;  pad_w = 16;  pad_h = 6;

// =====================================================================
// 2D / solid helpers
// =====================================================================
module rrect(l, w, r) { // rounded rect, corner at origin
    hull() for (x = [r, l-r]) for (y = [r, w-r]) translate([x, y]) circle(r);
}
// drafted rounded slab: base (l,w) at z0, shrinks by 2*d at z1
module rslab_draft(l, w, z0, z1, r, d) {
    hull() {
        translate([0, 0, z0]) linear_extrude(eps) rrect(l, w, r);
        translate([d, d, z1-eps]) linear_extrude(eps) rrect(l-2*d, w-2*d, max(r-d, 1));
    }
}
// straight rounded slab with a chamfered bottom edge (prints cleanly)
module rslab_cham(l, w, z0, z1, r, ch) {
    hull() {
        translate([ch, ch, z0]) linear_extrude(eps) rrect(l-2*ch, w-2*ch, max(r-ch,1));
        translate([0, 0, z0+ch]) linear_extrude(z1-z0-ch) rrect(l, w, r);
    }
}
module tube_bore()   { rotate([0,90,0]) translate([0,0,-6]) cylinder(r=R_in, h=shell_len+12); }
module outer_cyl()   { rotate([0,90,0]) translate([0,0,-1]) cylinder(r=R_out, h=shell_len+2); }
module half_space(right=true) {
    if (right) translate([-60, 0, -250]) cube([shell_len+120, 200, 500]);
    else       translate([-60, -200, -250]) cube([shell_len+120, 200, 500]);
}

module knuckles(spans) { for (s = spans) translate([s[0], 0, hinge_cz]) rotate([0,90,0]) cylinder(d=hinge_od, h=s[1]-s[0]); }
module knuckle_clearance(spans) { for (s = spans) translate([s[0]-hinge_gap, 0, hinge_cz]) rotate([0,90,0]) cylinder(d=hinge_od+2*hinge_gap, h=s[1]-s[0]+2*hinge_gap); }
module hinge_drill() { translate([-6, 0, hinge_cz]) rotate([0,90,0]) cylinder(d=hinge_hole, h=shell_len+12); }

// =====================================================================
// BODY FORMS (shared by both halves, cut at the Y=0 plane)
// =====================================================================
module pod_form(g=0) { // drafted capsule; g grows it for clearance cuts
    translate([-pod_wall-g, -pod_oy/2-g, 0]) rslab_draft(pod_ox+2*g, pod_oy+2*g, belt_z0-2*g, z_lid0+2*g, r_pod+g, draft);
}
module pod_interior() { // same draft -> uniform 3 mm walls
    difference() {
        translate([-pod_wall+pod_wall, -pod_iy/2, 0]) rslab_draft(pod_ix, pod_iy, belt_z0-2, z_lid0+1, r_pod-1, draft);
        outer_cyl(); // floor follows the shell surface
    }
}
module belt_form() { // full wrap band, chamfered bottom
    translate([-pod_wall-belt_t, -belt_oy/2, 0]) rslab_cham(pod_ox+2*belt_t, belt_oy, belt_z0, belt_z1, r_belt, edge*2);
}
module belt_groove() { // shadow gap where belt meets pod, all the way round
    translate([-pod_wall-belt_t-1, -belt_oy/2-1, belt_z1-gap])
        difference() {
            linear_extrude(gap+eps) rrect(pod_ox+2*belt_t+2, belt_oy+2, r_belt);
            translate([belt_t+1-gap, belt_t+1-gap, -1]) linear_extrude(gap+2) rrect(pod_ox+2*gap, pod_oy+2*gap, r_pod+gap);
        }
}
module side_fairing() { // pod -> tube blend, both sides, <=45° faces
    hull() {
        translate([-pod_wall, -pod_oy/2, 0]) translate([0,0,belt_z0]) linear_extrude(1) rrect(pod_ox, pod_oy, r_pod);
        translate([2, -22, 5]) linear_extrude(1) rrect(pod_ox-10, 44, r_pod);
    }
}
module drum_fairing() { // teardrop blend drum -> body
    hull() {
        translate([drum_x - drum_w/2, 0, drum_cz]) rotate([0,90,0]) cylinder(d=drum_od, h=drum_w);
        translate([drum_x - drum_w/2 - 8, -19, -R_out-4]) cube([drum_w+16, 38, 6]);
    }
}
module drum_hollow() {
    translate([drum_x - drum_w/2 + drum_wall, 0, drum_cz]) rotate([0,90,0]) cylinder(d=drum_od-2*drum_wall, h=drum_w);
}
module cover_rabbet() { // recessed seat so the cover sits flush
    translate([drum_x + drum_w/2 - 3, 0, drum_cz]) rotate([0,90,0]) cylinder(d=drum_od - 2, h=3.2);
}
module snout() { // cable-exit teardrop
    translate([drum_x, 0, drum_cz]) rotate([30,0,0]) translate([0,0,-drum_od/2+2]) hull() {
        sphere(d=cable_exit_d+7);
        translate([0,0,8]) sphere(d=cable_exit_d+11);
    }
}
module snout_drill() {
    translate([drum_x, 0, drum_cz]) rotate([30,0,0]) translate([0,0,-drum_od/2-9]) cylinder(d=cable_exit_d, h=22);
}
module usb_niche() { // sheltered recess around the port, in the rear belt face
    translate([pod_ix+pod_wall+belt_t-2.5, usb_y - usb_slot_w/2 - 3.5, usb_z - 3.5]) cube([6, usb_slot_w+7, usb_slot_h+7]);
}
module usb_drill() { translate([pod_ix - 2, usb_y - usb_slot_w/2, usb_z]) cube([2*pod_wall + belt_t + 4, usb_slot_w, usb_slot_h]); }
module camlock_drill() { translate([bore_x, -pod_oy/2 - 2, z_crown + pod_h*0.62]) rotate([-90,0,0]) cylinder(d=camlock_d, h=pod_wall + 4); }

// ---- closure: skirt = left belt half; lip + ledge on the straight span ----
module right_ledge_cut() { // pocket in the right pod wall the lip hooks into
    translate([12, -pod_oy/2 - 1.5, belt_z1 - 2.5]) cube([pod_ox - 30, 3, 2.5 + clr]);
}
module left_lip() { // inward hook on the skirt's top edge, straight span only
    translate([12+clr, -pod_oy/2 - 1.5 + clr, belt_z1 - 2.5 - clr]) cube([pod_ox - 30 - 2*clr, 3 - clr, 2.5 - clr]);
}
module screw_pad() { // hidden-M4 target under the bore + strut to the skirt
    translate([bore_x - pad_l/2, bore_y - pad_w/2, z_crown - 2]) cube([pad_l, pad_w, pad_h]);
    translate([bore_x - pad_l/2, -belt_oy/2 + 1, z_crown - 2]) cube([pad_l, belt_oy/2 - abs(bore_y) + pad_w/2 - 1, 4]);
}
module pad_pocket() {
    translate([bore_x - pad_l/2 - clr, -belt_oy/2 - 1, z_crown - 2 - clr]) cube([pad_l + 2*clr, belt_oy/2 + 1 - abs(bore_y) + pad_w/2 + clr, pad_h + 2*clr]);
}

// =====================================================================
// INTERIOR FITTINGS (added after cavity subtraction)
// =====================================================================
module latch_boss() {
    difference() {
        union() {
            translate([bore_x, bore_y, 0]) cylinder(d=boss_d, h=z_lid0);
            for (a = [45, 135, 225, 315]) // gussets: strength without mass
                translate([bore_x, bore_y, 0]) rotate([0,0,a]) translate([0, -1.25, 0]) cube([boss_d/2 + 5, 2.5, min(z_lid0-14, 36)]);
        }
        tube_bore();
        translate([bore_x, bore_y, z_lidtop - bore_depth]) cylinder(d=bore_d, h=bore_depth+2);
        translate([bore_x, bore_y, -R_out]) cylinder(d=closure_screw_d, h=z_lid0+2);
        translate([bore_x, bore_y, pin_z]) rotate([0,90,0]) cylinder(d=pin_d, h=boss_d);
        translate([bore_x + boss_d/2 - 2, bore_y, pin_z]) rotate([0,90,0]) cylinder(d=pin_d+3, h=4);
    }
}
module solenoid_pedestal() {
    difference() {
        translate([sol_x0 - 3, bore_y - sol_w/2 - 3, 0]) cube([sol_len + 6, sol_w + 6, ped_top]);
        tube_bore();
        translate([sol_x0 + 2, bore_y - sol_w/2 + 1.6, 12]) cube([sol_len - 4, sol_w + 2.8, ped_top]); // hollow the core: uniform walls
        for (dx = [sol_len/2 - sol_hole_dx/2, sol_len/2 + sol_hole_dx/2])
            translate([sol_x0 + dx, bore_y, ped_top - 12]) cylinder(d=sol_hole_d, h=13);
    }
}
module lid_bosses() {
    for (cx = [5, pod_ix - 5]) for (cy = [-pod_iy/2 + 5, pod_iy/2 - 5])
        translate([cx, cy, z_lid0 - 12]) difference() {
            union() { cylinder(d=9, h=12); translate([-1.25, (cy>0?0:-6), 0]) cube([2.5, 6, 12]); } // boss + gusset toward wall
            translate([0, 0, 2]) cylinder(d=2.6, h=11);
        }
}

// ---- WIRING: raceways, tray, cradles, anchors (DESIGN.md §6.5 table) ----
module raceway(x0, x1, yc) { // U-channel on the curved floor, clip lips every 24
    difference() {
        union() {
            for (side = [-1, 1]) translate([x0, yc + side*4 - 0.8, 6]) cube([x1-x0, 1.6, 17]);
            for (x = [x0+6 : 24 : x1-6]) for (side = [-1, 1])
                translate([x, yc + side*2.6 - 0.8, 21]) cube([4, side*1 > 0 ? 2.4 : 2.4, 1.6]); // lips overhang inward
        }
        rotate([0,90,0]) translate([0,0,-1]) cylinder(r=R_in+0.2, h=shell_len+2); // sit on floor
    }
}
module driver_tray() { // perfboard shelf over the Nano bay: boards get ~19 mm headroom
    difference() {
        union() {
            translate([104, -26, 0]) cube([40, 2, 46]);   // rails from floor
            translate([104, -4,  0]) cube([40, 2, 46]);
            translate([104, -26, 44]) cube([40, 24, 2]);  // tray plate (Nano slides in underneath)
        }
        tube_bore();
        translate([106, -27, 38]) cube([6, 26, 9]);        // wire notch, front rail pair
        translate([136, -27, 38]) cube([6, 26, 9]);        // wire notch, rear
        for (x = [112, 134] ) for (y = [-22, -8]) translate([x, y, 43]) cylinder(d=3.2, h=4); // zip-tie holes
    }
}
module battery_cradles() { // two saddles giving the 76x21x21 holder a LEVEL bed
    for (cx = [82, 118]) translate([cx, 0, 0]) difference() {
        translate([-2, 3, 0]) cube([4, 24.5, 48]);
        translate([-3, 4.1, z_crown]) cube([6, 21.4, 18]);         // holder slot, bed at crown height
        translate([-3, 4.1, z_crown + 8]) cube([6, 21.4, 12]);     // open top for drop-in
        translate([-3, 12, z_crown + 2]) cube([6, 6, 4]);          // zip-tie pass under the holder
        rotate([0,90,0]) translate([0,0,-4]) cylinder(r=R_in+0.2, h=8);
    }
}
module strain_posts() { // lid service-loop + JST anchor posts
    for (p = [[10, -18], [57, -25]]) translate([p[0], p[1], 12]) difference() {
        union() { cylinder(d=5, h=14); translate([0,0,12]) cylinder(d=8, h=2); } // mushroom head holds a zip tie
        rotate([0,90,0]) translate([0,0,-5]) cylinder(r=R_in+0.2, h=10);
    }
}

// =====================================================================
// THE TWO SHELL HALVES
// =====================================================================
module shell_right() {
    union() {
        difference() {
            union() {
                intersection() { difference() { outer_cyl(); tube_bore(); } half_space(true); }
                pod_form();
                intersection() { side_fairing(); half_space(true); }
                intersection() { belt_form(); half_space(true); }
                drum_fairing(); snout(); // drum assembly rides with the right half
                knuckles(hinge_right);
            }
            pod_interior();
            drum_hollow();
            cover_rabbet();
            snout_drill();
            belt_groove();
            right_ledge_cut();
            pad_pocket();
            knuckle_clearance(hinge_left);
            hinge_drill();
            camlock_drill();
            usb_niche();
            usb_drill();
            translate([bore_x, bore_y, -R_out]) cylinder(d=closure_screw_d, h=z_lid0+2);
            tube_bore();
        }
        latch_boss();
        solenoid_pedestal();
        lid_bosses();
        raceway(4, 54, -24);      // RF-zone signal ribbon (PN532 I2C + power gate)
        raceway(60, 100, -24.5);  // solenoid + 5V runs, past the pedestal to the tray
        driver_tray();
        battery_cradles();
        strain_posts();
    }
}

module drum_fairing_clear() { // right-half drum fairing + snout, grown ~0.6
    for (o = [[0,0,0],[0,0.6,0],[0,-0.6,0],[0,0,0.6],[0,0,-0.6]]) translate(o) { drum_fairing(); snout(); }
}
module shell_left() {
    difference() {
        union() {
            intersection() { difference() { outer_cyl(); tube_bore(); } half_space(false); }
            difference() { intersection() { belt_form(); half_space(false); } pod_form(clr); }      // the skirt = left belt half
            difference() { intersection() { side_fairing(); half_space(false); } pod_form(clr); }   // left side fairing rides with the left half
            left_lip();
            screw_pad();
            knuckles(hinge_left);
        }
        translate([bore_x, bore_y, z_crown - 3]) cylinder(d=5.6, h=pad_h + 6); // M4 heat-set pocket
        belt_groove();
        drum_fairing_clear();   // relief where the right half's drum fairing wraps under the seam
        knuckle_clearance(hinge_right);
        hinge_drill();
        tube_bore();
        half_space(true);
    }
}

module spool_cover() { // sits flush in the rabbet; local +Z = global +X
    difference() {
        union() {
            cylinder(d=drum_od - 2 - 0.4, h=3);
            translate([0,0,0]) cylinder(d=22, h=4.2); // center hub detail, proud 1.2
        }
        for (a = [30, 150, 270])
            translate([(drum_od/2 - drum_wall/2 - 2.5)*cos(a), (drum_od/2 - drum_wall/2 - 2.5)*sin(a), -1]) cylinder(d=3.4, h=6);
        translate([0,0,-1]) cylinder(d=12, h=7);
        translate([drum_cz, 0, -1]) cylinder(r=R_in + 0.4, h=7);
        translate([drum_cz - hinge_cz, 0, -1]) cylinder(d=3.6, h=7);
    }
}

// =====================================================================
// LID — matches the drafted pod top; NFC target ring, button dish
// =====================================================================
module lid() {
    difference() {
        union() {
            translate([-pod_wall + draft, -pod_oy/2 + draft, 0])
                rslab_draft(pod_ox - 2*draft, pod_oy - 2*draft, 0, lid_t, max(r_pod - draft, 2), edge); // top edge break
            translate([nfc_cx, 0, lid_t - eps]) difference() { cylinder(d=34, h=0.6); translate([0,0,-1]) cylinder(d=28, h=3); } // NFC target ring emboss
        }
        translate([pn532_x, -pn532_w/2, -eps]) cube([pn532_l, pn532_w, lid_t - window_remain]);
        translate([bore_x, bore_y, -1]) cylinder(d=bore_d + 0.6, h=lid_t + 4);
        translate([bore_x, bore_y, lid_t - 0.8]) cylinder(d1=bore_d + 0.6, d2=bore_d + 3, h=0.81 + 3); // chamfered bore mouth guides the cable head in
        translate([button_x, button_y, lid_t - 1]) cylinder(d=19, h=3);          // button dish
        translate([button_x, button_y, -1]) cylinder(d=button_d, h=lid_t + 2);
        translate([button_x, -3, lid_t - 0.8]) hull() { cylinder(d=6, h=3); translate([0,-6,0]) cylinder(d=6, h=3); } // LED slot recess
        translate([button_x, -3, -1])  cylinder(d=led_d, h=lid_t + 2);
        translate([button_x, -9, -1]) cylinder(d=led_d, h=lid_t + 2);
        for (cx = [5, pod_ix - 5]) for (cy = [-pod_iy/2 + 5, pod_iy/2 - 5]) {
            translate([cx, cy, -1]) cylinder(d=3.4, h=lid_t + 2);
            translate([cx, cy, lid_t - 1.6]) cylinder(d=6.2, h=2); // countersink pocket, screws sit flush
        }
    }
}

// =====================================================================
// LINER + SHIM (unchanged mechanically from v0.1)
// =====================================================================
module liner_2d() {
    union() {
        difference() { circle(r=R_in - 0.15); circle(r=R_in - liner_base); }
        for (i = [0 : fin_n-1]) rotate([0, 0, i*360/fin_n]) translate([R_in - 0.15 - liner_base, 0]) rotate([0, 0, 180 - fin_lean]) translate([0, -fin_t/2]) square([fin_h + liner_base, fin_t]);
    }
}
module liner_half(right=true) {
    rotate([0,90,0]) rotate([0,0,90]) linear_extrude(height=shell_len)
        intersection() { liner_2d(); if (right) translate([-2*R_in, -2*R_in]) square([2*R_in, 4*R_in]); else translate([0, -2*R_in]) square([2*R_in, 4*R_in]); }
}
module shim() {
    shim_R = 15;
    rotate([0,90,0]) linear_extrude(height=shell_len)
        intersection() {
            union() {
                difference() { circle(r=shim_R); circle(r=shim_R - 3); }
                for (i = [0 : 11]) rotate([0, 0, i*30]) translate([shim_R - 3, 0]) rotate([0, 0, 180 - fin_lean]) translate([0, -0.6]) square([7, 1.2]);
            }
            rotate([0,0,210]) difference() { circle(r=shim_R+1); polygon([[0,0],[100,0],[100,-100],[0,-100],[0,-1],[87,-50]]); }
        }
}

// =====================================================================
// render selector
// =====================================================================
module assembly() {
    color("#2E4057") shell_right();
    color("#3D5A73") shell_left();
    color("#C8CDD2") translate([0, 0, z_lid0]) lid();
    color("#3A3A3A") liner_half(true);
    color("#454545") liner_half(false);
    color("#AEB4BA") translate([drum_x + drum_w/2 - 3 + 0.2, 0, drum_cz]) rotate([0,90,0]) spool_cover();
}
if (part == "shell_right") shell_right();
if (part == "shell_left")  shell_left();
if (part == "lid")         lid();
if (part == "liner_right") liner_half(true);
if (part == "liner_left")  liner_half(false);
if (part == "shim")        shim();
if (part == "spool_cover") spool_cover();
if (part == "assembly")    assembly();
if (part == "section_latch")  intersection() { assembly(); translate([bore_x - 60, bore_y - 0.5, -R_out - 95]) cube([120, 60, 250]); }
if (part == "section_clamp")  intersection() { assembly(); translate([20, -100, -200]) cube([1.5, 200, 400]); }
if (part == "section_wiring") intersection() { assembly(); translate([-10, -100, -200]) cube([170, 100 - 18, 200 + z_lid0 - 2]); } // lid + battery side removed

echo("free liner bore Ø ≈", 2*(R_in - liner_base - fin_h*cos(fin_lean)));
echo("pin/plunger axis z =", pin_z, " pedestal top z =", ped_top);
echo("belt band z", belt_z0, "..", belt_z1, "  pod top z =", z_lid0);
echo("drum lowest z =", drum_cz - drum_od/2);
