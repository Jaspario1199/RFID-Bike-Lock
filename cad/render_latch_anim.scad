// Latch mechanism cutaway animation — sectioned at the bore centerline (y=10).
// Frame param F: 0..27. Kinematics mirror DESIGN.md 6.4:
//   insert: 45-deg nose cams the plunger back; plunger snaps into the ring groove
//   unlock: solenoid retracts plunger; ejector spring pops the head; spool retracts
F = 0;

// ---- geometry constants (from the CAD) ----
BX = 58; BY = 10;          // bore center
PZ = 44.5;                 // plunger axis z
EXT = 61.4;                // plunger tip x, extended (2.1 into the bore)
RIDE = 63.2;               // tip riding the O10 bulb
RET = 64.2;                // tip fully retracted (solenoid)
GROOVE_W = 6.6;            // head ring-groove axial width

// ---- head position hz (0 = latched) per frame ----
function hz_of(f) =
    f <= 9  ? 26 - 26 * f / 9 :
    f <= 12 ? 0 :
    f <= 15 ? 0 :
    f <= 20 ? (f - 15) * 1.6 :          // ejector pop + spool, to 8
    8 + (f - 20) * 3.2;                  // exit

// ---- plunger tip x per frame (cam-follower during insert; solenoid during unlock) ----
function cam_tip(hz) =
    hz > 10.3 ? EXT :
    hz > 7.3  ? EXT + (RIDE - EXT) * (10.3 - hz) / 3 :   // nose ramp pushes back
    hz > 3.3  ? RIDE :                                    // riding the bulb
    EXT;                                                  // snapped into the groove
function tip_of(f) =
    f <= 12 ? cam_tip(hz_of(f)) :
    f <= 15 ? EXT + (RET - EXT) * (f - 12) / 3 :          // solenoid energizes
    f <= 20 ? (hz_of(f) > 7.3 ? EXT : RET) :              // held until bulb clears
    EXT;
function sol_on(f) = (f >= 13 && f <= 19) ? 1 : 0;

hz  = hz_of(F);
tip = tip_of(F);

// ================= static cutaway =================
color("#4A6178") import("../stl/section_body.stl");
color("#D95D39") import("../stl/section_pedestal_cart.stl");
// lid slab (drawn: the crop of the real lid came back empty) with the bore pass-through
color("#C8CDD2") difference() {
    translate([32, 10, 53]) cube([70, 18, 3]);
    translate([BX, BY, 50]) cylinder(h = 8, d = 11.6, $fn = 48);
}
// solenoid body on the tower (orange flash = energized)
color(sol_on(F) ? "#E8842A" : "#8A9099")
    translate([68, 10, 37]) cube([30, 8, 15]);
// closure screw + washer at the bore floor (self-guarding: covered when locked)
color("#3A3A3A") translate([BX, BY, 30]) cylinder(h = 1.9, d = 5.6, $fn = 32);
color("#9AA0A8") translate([BX, BY, 31.9]) cylinder(h = 0.8, d = 8.2, $fn = 32);

// ================= moving parts =================
// plunger (= the locking pin): O6 rod from the solenoid, 45-deg filed nose
color("#C8CDD2") {
    translate([tip + 1.5, BY, PZ]) rotate([0, 90, 0])
        cylinder(h = 74 - tip, d = 6, $fn = 40);              // shank back into the solenoid (+x)
    translate([tip, BY, PZ]) rotate([0, 90, 0])
        cylinder(h = 1.5, d1 = 3, d2 = 6, $fn = 40);          // 45-deg nose (points -x)
}
// cable head: stem / shoulder / ring groove / O10 bulb / 45-deg nose  (hz=0 latched)
color("#C8A24B") translate([BX, BY, hz]) {
    translate([0, 0, 47.8]) cylinder(h = 24, d = 5, $fn = 48);               // stem (cable swage)
    translate([0, 0, 44.8]) cylinder(h = 3.0, d = 10, $fn = 48);             // upper shoulder
    translate([0, 0, 44.8 - GROOVE_W]) cylinder(h = GROOVE_W, d = 6.8, $fn = 48); // ring groove floor
    translate([0, 0, 34.2]) cylinder(h = 4.0, d = 10, $fn = 48);             // bulb
    translate([0, 0, 31.2]) cylinder(h = 3.0, d1 = 4, d2 = 10, $fn = 48);    // 45-deg ramped nose
}
// ejector spring: washers evenly spaced between the screw washer and the head nose
spring_top = 31.2 + hz - 0.4;
spring_bot = 32.9;
n = 5;
if (spring_top > spring_bot + 1)
    color("#2E8B57") for (i = [0 : n - 1])
        translate([BX, BY, spring_bot + (spring_top - spring_bot) * i / (n - 1)])
            cylinder(h = 0.7, d = 8.4, $fn = 32);

// ================= phase label =================
lbl = F <= 8  ? "1. INSERT - 45deg nose cams the pin back (zero power)" :
      F <= 12 ? "2. LOCKED - pin snapped into the ring groove" :
      F <= 15 ? "3. UNLOCK - solenoid pulls the pin (300ms pulse)" :
      F <= 20 ? "4. EJECT - spring pops the head clear" :
                "5. RELEASED - spool reels the cable in";
color("#222222") translate([26, 9, 61]) rotate([90, 0, 0])
    text(lbl, size = 2.1, font = "Liberation Sans:style=Bold");
