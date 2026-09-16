"""cnc_casing_cq.py - the machined casing (CNC_CASING.md 2A): dumb tube-half chassis +
inside-out bolted attachments. Separate lineage from bike_lock_cq.py (printed v0.8.x).

Frame: x = tube axis (0..L), z up, seam plane y=0. C1 = y>=0 chassis half (carries every
attachment), C2 = y<=0 clamp half (carries the closure block + the hinge knuckle block).

Hinge (CNC_CASING.md 2A "How C2 goes on"): a O5 pin along x at P=(HINGE_Y, HINGE_Z), just
below the seam on the C2 side. Knuckles on A3 (two lugs + arms) and one lug on C2's hinge
block. C2 swings OPEN_DEG open (stop = the puck top) for the frame to enter C1, swings shut, and the single
guarded closure screw (under the cable head) clamps the top. Everything near the pin is
circular about it, so the swing is clash-free by construction; the gates prove it.

  python cad/cnc_casing_cq.py            build all parts -> cnc-design/step + stl
  python cad/cnc_casing_cq.py --gates    interference matrix + screw-path probes + wall audit
"""
import math, os, sys
import cadquery as cq

# ---------------- stock + chassis ----------------
L        = 150.0                 # tube length
R_O      = 63.5 / 2              # 2.5" OD 6061 tube
R_I      = 27.0                  # line-bored to O54 (liner stack unchanged from v0.8)
WALL     = R_O - R_I             # 4.75
HINGE_Y, HINGE_Z = -1.0, -38.0   # pin axis (along x): 1 mm onto the C2 side of the seam, 6 mm under the tube.
                                 # Every closure-block point is then at y<=HINGE_Y, so none rises into the
                                 # A1 roof as C2 starts to swing
HPIN_D, HPIN_CLR = 5.0, 0.1       # O5 dowel; running fit in every lug
LUG_D = 11.0                     # knuckle OD (3 mm wall around the pin)
LUG_R = LUG_D / 2
HX0, HX1 = 58.0, 98.0            # knuckle zone (centred under the closure block)
A3_LUGS = [(HX0, HX0 + 8.0), (HX1 - 8.0, HX1)]   # A3's two lugs
C2_LUG = (HX0 + 8.3, HX1 - 8.3)                  # C2's lug between them (0.3 end float)
OPEN_DEG = 60.0                  # swing the gates prove (mouth = 65 mm for a O46 frame; C2 sweeps nothing below z -50)
                                 # the STOP is the puck top: the hinge block lands on it a few degrees past OPEN_DEG
LIP_X, LIP_R = 2.0, 25.5         # rear liner lip: x L-2..L, inward to r25.5

# ---------------- attachment fastening (M3 countersunk flat head, inside-out) ----------------
SCREW_X   = (25.0, 75.0, 135.0)  # 3 per row (75 keeps the middle pilot clear of the latch boss at x 80.5..99.5)
CROWN_Y   = 6.0                  # vertical crown row (radial ~11deg -> vertical is fine)
SKIRT_Z   = 8.0                  # horizontal skirt row height |z|
CLR3 = 3.4                       # M3 clearance
CSK_D, CSK_SUB, HEAD_D = 6.3, 0.4, 5.5   # 90 deg countersink O at the bore surface (on the axis), head top sunk 0.4 below the
                                 # surface, ISO 10642 M3 head O5.5: the head RIM then sits r26.74 - 0.1 inside the bore, clear of
                                 # the liner ring (r26.85). A counterbore deep enough for a cap head leaves < 1.8 mm of wall at its
                                 # far edge on this curvature; a countersink is only deep on the axis, so > 3.4 mm stays everywhere
TAP3      = 2.5                  # M3 tap drill (modeled pilot)
CLR4, TAP4 = 3.4, 2.5            # closure screw stays M3 (owner) - threads the steel block; O2.5 pilot doubles as the PETG self-tap pilot in Stage 1

# ---------------- top box A1 ----------------
BX0, BX1 = 10.0, 150.0           # x footprint: the full tube length - the RC522 (60 long) needs the reader zone
BY0, BY1 = -14.0, 43.0           # y footprint (straddles the seam; 14 mm overhang over C2; 43 gives the
                                 # +y strip room for the TP4056 beside an edge-standing Nano)
SADDLE_R = R_O + 0.25            # box underside hugs the tube on the C1 side
RELIEF1_R = R_O + 2.25           # A1 underside over C2 (y<0.3): C2's rim swells to r33.57 at 11 deg of
                                 # swing (pin is 6 mm under the tube, so the rim arcs outward), +0.4
RELIEF3_R = R_O + 0.75           # A3's lug arms top out here under C2
RELIEF_Y  = 0.3                  # relief extends this far past the seam so C2's face never rubs a step
SKIRT_Y0, SKIRT_Z0 = 32.0, 3.0   # +y skirt: inner face y32, drops to z3
BWALL    = 3.0
ZF       = 38.0                  # interior floor top (6.25 above the tube crown)
INT_H    = 24.0                  # interior height: solenoid zone (cart 3 + 15 + 2) and reader zone (flat Nano 8 + reader 4 + gaps) sit SIDE BY SIDE, not stacked (owner Q5)
ZTOP     = ZF + INT_H            # lid seat
LID_T    = 5.0
CORNER_R = 4.0                   # R4 rule (O8 tool) - R6 stole the +x/+y pocket corner from the power stack
LATCH_X, LATCH_Y = 90.0, -4.0    # receiver over the C2 side of the seam (closure block below); x leaves
                                 # the reader window (x 20..65) clear on -x and the solenoid cart (44) on +x
BORE_D, BOSS_D   = 11.0, 19.0
PIN_Z    = ZF + 14.0             # latch pin axis (52)
# ---------------- latch train (rev 3e: hardened cap on the plunger, guided in a tunnel rib) ----------------
# The solenoid's soft-iron plunger never touches the cable head. A hardened steel CAP (O8, 2 mm end wall,
# bored O6.1 x 8 for the plunger, cross-pinned) is the latch pin; it runs in a close O8.1 tunnel through a
# rib that extends the latch boss toward the coil, so it is guided over >= 6 mm at every position. Its rear
# O10 flange stops against the tunnel's step: THAT sets the rest position (the solenoid's own tail bolt is
# cut off), limiting the stroke to STROKE where the coil pulls hardest. The return spring sits between the
# flange and the coil face.
PIN_PROT = 2.0                   # cap nose into the bore at rest (head shoulder engagement = 5 - 3.5 = 1.5 radial)
CAP_D, CAP_L, CAP_END, CAP_BORE = 8.0, 10.0, 2.0, 6.1
CAP_FL_D, CAP_FL_T = 10.0, 2.0   # rear flange: forward stop + spring seat
STROKE = 2.6                     # PIN_PROT + 0.6 clearance; the coil seats fully at the end of it
PL_D = 6.0                       # HS-0730B plunger
PL_MIN_PROT = 12.7               # MEASURED: nose protrusion from the coil face with the plunger fully seated (1/2")
PL_MAX_PROT = 19.05              # MEASURED: nose protrusion at the solenoid's own stop (3/4") - unused, the flange stops earlier
PL_REST_PROT = PL_MIN_PROT + STROKE          # 15.3 at rest
CAP_X0 = LATCH_X + BORE_D / 2 - PIN_PROT     # 93.5: cap nose at rest
PL_X0 = CAP_X0 + CAP_END                     # 95.5: plunger nose (inside the cap)
SOL_X0 = PL_X0 + PL_REST_PROT                # 110.8: coil face - placed by the plunger train, nothing else
SOL_TAIL = -STROKE                           # tail cut flush with the back frame at full retraction -> 2.6 inside at rest
TUN_D, TUN2_D = CAP_D + 0.1, CAP_FL_D + 0.1  # tunnel: O8.1 for the cap, O10.1 for the flange + spring
TUN_STEP_X = CAP_X0 + CAP_L - CAP_FL_T       # 101.5: the step the flange stops against
RIB_X1 = SOL_X0 - 1.0                        # 109.8: rib ends 1 mm short of the coil face
RIB_Y0, RIB_Y1, RIB_Z1 = LATCH_Y - 7.0, LATCH_Y + 7.0, PIN_Z + 6.0   # 14 wide (1.95 walls beside the O10.1), floor to 58
RSPR_OD, RSPR_ID, RSPR_FREE = 9.0, 6.6, 10.0 # return spring around the plunger, ~0.4 N/mm
# cable head: O10 cylinder (shim gap to the O10.3 bushing 0.15/side), 45 deg cone nose, square shoulder
CH_D, CH_CONE, CH_LAND, CH_GROOVE_W, CH_GROOVE_D, CH_UPPER = 10.0, 3.0, 3.0, CAP_D + 0.5, 6.8, 5.5
CH_SHOULDER_Z = PIN_Z - CAP_D / 2            # 48: shoulder bears on the cap's underside when locked
EJ_OD, EJ_ID, EJ_FREE, EJ_SOLID = 9.0, 7.6, 11.0, 4.5   # ejector spring on the bore floor, ~0.5 N/mm
BUSH_ID, BUSH_OD, BUSH_Z0 = CH_D + 0.3, 14.0, PIN_Z + TUN_D / 2 + 0.4     # hardened mouth bushing above the tunnel (56.45) to the lid top
CLS_HEAD_D, CLS_HEAD_H, CLS_WASHER_D, CLS_WASHER_T, CLS_L = 5.5, 2.0, 7.0, 0.5, 6.0   # closure screw: M3x6 LOW-HEAD cap + washer
DRAIN_D = 2.0                                # bore-floor drain out the -y face
LID_SCREWS = [(BX0 + 4.5, BY0 + 4.5), (BX0 + 4.5, BY1 - 4.5), (BX1 - 4.5, BY0 + 4.5), (105.0, BY1 - 4.5)]
# 3 corners + one mid-wall: the +x/+y corner is where the TP4056's USB-C meets the end wall, so that
# screw moves along the +y wall to x 105 (clear of the green button's O15 nut and the boost)
# RF window (PN532 footprint by default - see open question Q1) + button + LEDs
WIN_L, WIN_W = 45.2, 43.0        # through-cutout = PN532 antenna footprint + 1 (metal lid must clear the loop)
WIN_X0 = 34.8                    # window over the RC522's antenna end (board x 19..79, antenna = its +x 35 mm)
WIN_CX = WIN_X0 + WIN_L / 2      # 57.4
INS_FLANGE, INS_FL_T = 2.5, 1.5  # opaque insert: body fills the cutout flush; flange sits in a recess milled
                                 # in the lid's UNDERSIDE (nothing shows on top; the box wall clamps it)
BTN_D, BTN_X, BTN_Y = 12.4, 93.0, 32.5        # GREEN (wake/scan) sealed 12 mm button; x: its O15 nut clears the window flange (x<=82.7)
BTN_NUT_D, BTN_NUT_T = 15.0, 3.0               # the panel nut under the lid - gated like a part (audit)
BTN2_Y = 13.0                                  # RED (admin/cancel) button, same column; its nut clears the latch boss (r9.5 at y-4)
BUZ_D, BUZ_H, BUZ_X, BUZ_Y = 12.0, 9.5, 103.5, 22.85  # over the Nano (10 mm under it), NOT over the boost - its pins need 5 mm;
                                                       # x: clears the boost (x>=110) and both button nuts (>=13.5 from their centres)
BUZ_REC = 3.0                                          # buzzer RECESSED this far into the lid underside,
                                                       # so its body clears the boost below   # active buzzer under the lid, in the gap between the
                                                       # green button and the boost; sound hole O2.5
LED_D, LED_XY = 3.3, ((23.0, 37.2), (29.0, 37.2))    # LEDs in the free +y strip at the -x end (nothing under it: deck ends y34.5);
                                                     # two O15 button nuts + two LEDs cannot share the 34 mm bay (audit)
LED_LEG_H, BTN_LUG_H, BUZ_PIN_H = 10.0, 6.0, 5.0     # service depth below each lid part: legs+resistor, solder lugs, pins

# ---------------- closure block (on C2, under the box overhang) ----------------
BLK_X0, BLK_X1 = LATCH_X - 10.0, LATCH_X + 10.0
BLK_Y0, BLK_Y1 = -13.0, -1.0
BLK_TOP = 36.5                   # flat top: CONTACTS the A1 pocket roof when the closure screw is tight
BLK_SCREW_X = (LATCH_X - 6.5, LATCH_X + 6.5)   # 2x M3 from inside C2, vertical, at y=-7
# ---------------- hinge block (on C2, carries C2's lug) ----------------
HB_Y0, HB_Y1 = -15.0, HINGE_Y - LUG_R - 0.3    # body rides C2's OD outboard of A3's lugs (-15..-8.8)
HB_Z0 = HINGE_Z                  # body bottom = pin height: nothing of C2 sits below the pin
                                 # except its round lug, so a 90 deg swing never enters A3
HB_SCREW_X, HB_SCREW_Y = (HX0 + 6.0, HX1 - 6.0), -11.9   # 64/92: 2x M3 from inside C2, vertical, INSIDE the 58..98 body (audit caught x102)

# ---------------- bottom box A3 (spool cartridge, top-loaded) ----------------
SX0, SX1 = 34.0, 106.0           # A3 cradle footprint x (72): its ends carry the chassis screws outside the centred pocket
A3_Y0 = 0.5                      # A3 body sits wholly on the C1 side; only its knuckle lugs + arms reach over
ARM_Y0 = HINGE_Y                 # lug arm: from the pin centre to the body, top at -RELIEF3_R
A3_CROWN_Y = 10.0                # A3's crown row sits at y=10 (clear of the pin zone y -8.5..2.5)
SPOOL_CORE, CABLE_D, CABLE_L = 32.0, 4.0, 1500.0   # 3 mm 7x7 wire PVC-coated to O4 on a O32 core (10.7x wire O)
SPOOL_W = 24.0                   # cartridge width (6 wraps/layer): 2 layers = 1.51 m -> outer O48
POCKET_D = SPOOL_CORE + 4 * CABLE_D + 3.0   # 51: 2 cable layers + clearance
PUCK_WALL = 6.5                  # round puck wall: 2 mm of metal each side of the M3 cover-screw pilots (audit)
PUCK_R = POCKET_D / 2 + PUCK_WALL            # 31 -> O62 puck
CRADLE_Y1, CRADLE_Z0 = 44.0, -44.0           # saddle cradle along the tube: chassis screws, hinge lugs, skirt rib
SKIRT_Y1 = 44.0                  # A3 skirt is a 12 mm rib (y 32..44), not the full box width
POCKET_CY = 0.0                  # centred under the tube
PX = (SX0 + SX1) / 2             # puck axis x
PY1 = POCKET_CY + PUCK_R         # 64: outermost point of the puck
COVER_T = 3.0                    # bottom cover plate (power spring lives INSIDE the O40 hub, as in every retractable reel)
STOP_Z = -51.5                   # puck top on the C2 side = the swing STOP: 1.4 mm under everything C2 sweeps in a
                                 # 60 deg swing (-50.1); C2 lands on it at 64 deg (gated)
POCKET_TOP = STOP_Z - 2.5        # -54: pocket ceiling (2.5 mm wall under the stop face), so the puck sits CENTRED
                                 # under the tube (owner) instead of off to the C1 side
SZ_BOT = POCKET_TOP - SPOOL_W - 3.0   # -64: box bottom face
EXIT_D = 7.0                     # bushed cable exit, tangential, out the -x end wall along -x
A3_SCREW_X = (SX0 + 6.0, SX1 - 6.0)   # 40/100: in the cradle ends, outside the centred pocket circle; C1's bottom rows match
COVER_SCREWS = [(PX + (POCKET_D / 2 + 2.75) * math.cos(math.radians(a)), POCKET_CY + (POCKET_D / 2 + 2.75) * math.sin(math.radians(a)))
                for a in (45, 135, 225, 315)]   # 4 in the puck wall

pod_pocket_r = 6.0

def cyl_x(r, x0, x1):
    return cq.Workplane("YZ", origin=(x0, 0, 0)).circle(r).extrude(x1 - x0)

def halfspace(y_pos):
    """y>=0 (True) or y<=0 (False) keep-box."""
    return cq.Workplane("XY", origin=(L / 2, 200 if y_pos else -200, 0)).box(L + 20, 400, 400)

def yslab(y0, y1):
    """keep-box spanning y0..y1 (huge in x and z)."""
    return cq.Workplane("XY", origin=(L / 2, (y0 + y1) / 2, 0)).box(L + 20, y1 - y0, 400)

def xbox(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY", origin=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)).box(x1 - x0, y1 - y0, z1 - z0)

def tube_half(pos):
    return cyl_x(R_O, 0, L).cut(cyl_x(R_I, -1, L + 1)).intersect(halfspace(pos))

def rear_lip(pos):
    lip = cyl_x(R_I + 0.01, L - LIP_X, L).cut(cyl_x(LIP_R, L - LIP_X - 1, L + 1))
    return lip.intersect(halfspace(pos))

def csk_cone(plane_origin, axis_dir, s_surf):
    """90 deg countersink for an inside-out screw: the cone is O CSK_D where the axis meets the bore
    surface (s_surf along axis_dir from plane_origin), closes to O CLR3 (CSK_D-CLR3)/2 deeper, and
    starts 2 mm back in the bore air so it always breaks the surface cleanly."""
    d = cq.Vector(*axis_dir)
    o = cq.Vector(*plane_origin) + d * (s_surf - 2.0)
    depth = (CSK_D - CLR3) / 2 + 2.0
    return (cq.Workplane(cq.Plane(origin=o.toTuple(), xDir=(1, 0, 0) if abs(d.x) < 0.9 else (0, 1, 0), normal=d.toTuple()))
            .circle(CSK_D / 2 + 2.0).workplane(offset=depth).circle(CLR3 / 2).loft())

def crown_screw_cuts(zsign, xs, cy=CROWN_Y):
    """vertical M3 through the crown wall at y=cy, countersunk from INSIDE (bore side)."""
    cuts = None
    z_surf = math.sqrt(R_I ** 2 - cy ** 2)          # bore surface on the axis
    for x in xs:
        thru = cq.Workplane("XY", origin=(x, cy, 0)).circle(CLR3 / 2).extrude(zsign * 40)
        c = thru.union(csk_cone((x, cy, 0), (0, 0, zsign), z_surf))
        cuts = c if cuts is None else cuts.union(c)
    return cuts

def skirt_screw_cuts(zsign, xs):
    """horizontal M3 along +y through the side wall at z=SKIRT_Z, countersunk from inside."""
    cuts = None
    z = zsign * SKIRT_Z
    y_surf = math.sqrt(R_I ** 2 - z ** 2)
    for x in xs:
        thru = cq.Workplane("XZ", origin=(x, 0, z)).circle(CLR3 / 2).extrude(-40)   # XZ normal is -y; extrude(-) -> +y
        c = thru.union(csk_cone((x, 0, z), (0, 1, 0), y_surf))
        cuts = c if cuts is None else cuts.union(c)
    return cuts

def block_screw_cuts(xs, y, zsign):
    """vertical M3 through C2's wall at y (top wall zsign=+1, bottom wall -1), countersunk from inside."""
    cuts = None
    z_surf = math.sqrt(R_I ** 2 - y ** 2)
    for x in xs:
        thru = cq.Workplane("XY", origin=(x, y, 0)).circle(CLR3 / 2).extrude(zsign * 40)
        c = thru.union(csk_cone((x, y, 0), (0, 0, zsign), z_surf))
        cuts = c if cuts is None else cuts.union(c)
    return cuts

def build_c1():
    c1 = tube_half(True).union(rear_lip(True))
    c1 = c1.cut(crown_screw_cuts(+1, SCREW_X)).cut(skirt_screw_cuts(+1, SCREW_X))        # top rows -> A1
    c1 = c1.cut(crown_screw_cuts(-1, A3_SCREW_X, A3_CROWN_Y)).cut(skirt_screw_cuts(-1, A3_SCREW_X))  # bottom rows -> A3
    return c1.cut(stud_cuts(True))

def build_c2():
    c2 = tube_half(False).union(rear_lip(False))
    c2 = c2.cut(block_screw_cuts(BLK_SCREW_X, -7.0, +1)).cut(block_screw_cuts(HB_SCREW_X, HB_SCREW_Y, -1))
    return c2.cut(stud_cuts(False))

def saddle_body(x0, x1, y0, y1, z_lo, z_hi, skirt_sign, relief_r):
    """box block spanning z_lo..z_hi minus the tube saddle; +y skirt wraps the tube side."""
    # the block reaches the skirt height across its whole width, so once the saddle cylinder is
    # cut the underside follows the tube's diameter continuously from the seam round to the skirt
    # (owner: no flat shelf between saddle and skirt - the attachment face is all R32)
    if skirt_sign > 0:
        blk = xbox(x0, x1, y0, y1, SKIRT_Z0, z_hi)
    else:
        blk = xbox(x0, x1, y0, y1, z_lo, -SKIRT_Z0)
    body = blk.cut(cyl_x(SADDLE_R, -1, L + 1))
    relief = cyl_x(relief_r, -1, L + 1).intersect(yslab(-200, RELIEF_Y))
    return body.cut(relief)

def build_top_box():
    b = saddle_body(BX0, BX1, BY0, BY1, 20.0, ZTOP, +1, RELIEF1_R)
    # interior pocket (R6 corners) from floor to top
    b = b.cut(cq.Workplane("XY", origin=((BX0 + BX1) / 2, (BY0 + BY1) / 2, ZF))
              .rect(BX1 - BX0 - 2 * BWALL, BY1 - BY0 - 2 * BWALL).extrude(INT_H + 1)
              .edges("|Z").fillet(CORNER_R))
    # latch boss column + lid-screw corner bosses
    b = b.union(cq.Workplane("XY", origin=(LATCH_X, LATCH_Y, ZF - 1)).circle(BOSS_D / 2).extrude(INT_H + 1))
    for (sx, sy) in LID_SCREWS:
        b = b.union(cq.Workplane("XY", origin=(sx, sy, ZF - 1)).circle(4.0).extrude(INT_H + 1))
        b = b.cut(cq.Workplane("XY", origin=(sx, sy, ZTOP - 8)).circle(TAP3 / 2).extrude(9))
    # receiver bore (through the boss to the floor) + M4 closure clearance through the floor
    b = b.cut(cq.Workplane("XY", origin=(LATCH_X, LATCH_Y, ZF)).circle(BORE_D / 2).extrude(INT_H + 2))
    b = b.cut(cq.Workplane("XY", origin=(LATCH_X, LATCH_Y, 0)).circle(CLR4 / 2).extrude(ZF + 1))
    # latch rib: extends the boss toward the coil and carries the cap tunnel (O8.1) and the flange/spring
    # counterbore (O10.1); the step between them is the cap's forward stop
    b = b.union(xbox(LATCH_X, RIB_X1, RIB_Y0, RIB_Y1, ZF - 1, RIB_Z1))
    b = b.cut(cq.Workplane("XY", origin=(LATCH_X, LATCH_Y, ZF)).circle(BORE_D / 2).extrude(INT_H + 2))   # re-open the bore through the rib
    b = b.cut(cq.Workplane("XY", origin=(LATCH_X, LATCH_Y, 0)).circle(CLR4 / 2).extrude(ZF + 1))         # ... and the closure-screw hole
    b = b.cut(cq.Workplane("YZ", origin=(LATCH_X, LATCH_Y, PIN_Z)).circle(TUN_D / 2).extrude(TUN_STEP_X - LATCH_X))
    b = b.cut(cq.Workplane("YZ", origin=(TUN_STEP_X, LATCH_Y, PIN_Z)).circle(TUN2_D / 2).extrude(RIB_X1 + 1 - TUN_STEP_X))
    # hardened mouth bushing seat: O14 from just above the tunnel to the lid seat
    b = b.cut(cq.Workplane("XY", origin=(LATCH_X, LATCH_Y, BUSH_Z0)).circle(BUSH_OD / 2).extrude(ZTOP - BUSH_Z0 + 1))
    # drain: O2 from the bore floor out through the -y wall (the bore is a rain funnel; the tunnel at z52 is
    # the leak path into the cavity - this empties it first). Drilled from outside, 2 mm above the block pocket.
    b = b.cut(cq.Workplane("XZ", origin=(LATCH_X, LATCH_Y + 1.0, ZF + DRAIN_D / 2)).circle(DRAIN_D / 2).extrude(-(BY0 - 1) + (LATCH_Y + 1.0)))
    # closure-block pocket: OPEN through the -y face (the block swings in and out with C2 on
    # the hinge); x walls locate the block, the roof at BLK_TOP is what the screw clamps against
    b = b.cut(xbox(BLK_X0 - 0.2, BLK_X1 + 0.2, BY0 - 2, BLK_Y1 + 0.3, 0, BLK_TOP))
    # local pocket in the -y wall: the measured HS-0730B is 1.75 wider than the interior allows.
    # Cheaper than a wider box, which would foul the C2 swing (gated).
    b = b.cut(xbox(SOL_X0 - 2, SOL_X0 + SOL_L + 2, BY0 + POCKET_WALL, IY0 + 0.01, SOL_Z0 - 2, SOL_Z1 + 2))
    # USB-C charge port through the +x end wall at the TP4056 (TPU plug from outside, BOM 30d)
    usb_y = TP_Y0 + TP_W / 2; usb_z = ZF + TP_T + 3.3 / 2
    b = b.cut(cq.Workplane("YZ", origin=(IX1 - 0.5, usb_y, usb_z)).rect(USB_SLOT_W, USB_SLOT_H).extrude(BWALL + 1).edges("|X").fillet(1.4))
    b = b.cut(cq.Workplane("YZ", origin=(BX1 - 2.0, usb_y, usb_z)).rect(USB_SLOT_W + 5.4, USB_SLOT_H + 5.4).extrude(2.5).edges("|X").fillet(2.5))   # 15.4 x 9.6 x 2 deep: the plug overmold seats in it, the shell then reaches the receptacle
    # chassis screws thread into the floor (pilots) - crown row vertical, skirt row horizontal
    for x in SCREW_X:
        b = b.cut(cq.Workplane("XY", origin=(x, CROWN_Y, 25)).circle(TAP3 / 2).extrude(ZF - 25 - 1.0))
        b = b.cut(cq.Workplane("XZ", origin=(x, 30, SKIRT_Z)).circle(TAP3 / 2).extrude(-(BY1 - 1.5 - 30)))
    return b

def build_lid():
    p = cq.Workplane("XY", origin=((BX0 + BX1) / 2, (BY0 + BY1) / 2, ZTOP)).box(BX1 - BX0, BY1 - BY0, LID_T, centered=(True, True, False))
    p = p.edges("|Z").fillet(CORNER_R)
    # RF window: plain through cutout (the opaque insert A5 fills it from below - no bezel step)
    p = p.cut(cq.Workplane("XY", origin=(WIN_CX, (BY0 + BY1) / 2, ZTOP - 1)).rect(WIN_L, WIN_W).extrude(LID_T + 2).edges("|Z").fillet(4))
    p = p.cut(cq.Workplane("XY", origin=(WIN_CX, (BY0 + BY1) / 2, ZTOP - 1)).rect(WIN_L + 2 * INS_FLANGE + 0.4, WIN_W + 2 * INS_FLANGE + 0.4).extrude(INS_FL_T + 1).edges("|Z").fillet(5.4))
    p = p.cut(cq.Workplane("XY", origin=(LATCH_X, LATCH_Y, ZTOP - 1)).circle(BUSH_OD / 2 + 0.05).extrude(LID_T + 2))   # the bushing runs through the lid to its top
    for by in (BTN_Y, BTN2_Y):
        p = p.cut(cq.Workplane("XY", origin=(BTN_X, by, ZTOP - 1)).circle(BTN_D / 2).extrude(LID_T + 2))
    for (lx, ly) in LED_XY:
        p = p.cut(cq.Workplane("XY", origin=(lx, ly, ZTOP - 1)).circle(LED_D / 2).extrude(LID_T + 2))
    p = p.cut(cq.Workplane("XY", origin=(BUZ_X, BUZ_Y, ZTOP - 1)).circle(1.25).extrude(LID_T + 2))   # buzzer sound hole
    p = p.cut(cq.Workplane("XY", origin=(BUZ_X, BUZ_Y, ZTOP - 0.01)).circle(BUZ_D / 2 + 0.25).extrude(BUZ_REC))  # buzzer recess
    for (sx, sy) in LID_SCREWS:
        p = p.cut(cq.Workplane("XY", origin=(sx, sy, ZTOP - 1)).circle(CLR3 / 2).extrude(LID_T + 2))
        cs = (cq.Workplane("XY", origin=(sx, sy, ZTOP + LID_T + 0.01)).circle(3.2)
              .workplane(offset=-1.8).circle(1.75).loft())
        p = p.cut(cs)
    return p

def build_closure_block():
    blk = cq.Workplane("XY", origin=((BLK_X0 + BLK_X1) / 2, (BLK_Y0 + BLK_Y1) / 2, (20 + BLK_TOP) / 2)).box(BLK_X1 - BLK_X0, BLK_Y1 - BLK_Y0, BLK_TOP - 20)
    blk = blk.cut(cyl_x(R_O + 0.05, -1, L + 1))                     # sits on C2's OD
    blk = blk.cut(cq.Workplane("XY", origin=(LATCH_X, LATCH_Y, 20)).circle(TAP4 / 2).extrude(30))  # closure screw tapped pilot (M3, owner)
    for x in BLK_SCREW_X:
        blk = blk.cut(cq.Workplane("XY", origin=(x, -7.0, 20)).circle(TAP3 / 2).extrude(BLK_TOP - 20 + 1))   # tapped THROUGH: M3x8 engages 4.8 without bottoming (audit)
    return blk

def lug_cyl(x0, x1, r):
    return cq.Workplane("YZ", origin=(x0, HINGE_Y, HINGE_Z)).circle(r).extrude(x1 - x0)

def build_bottom_box():
    """Spool puck (owner Q2: vertical axis) on the C1 side + the hinge's two knuckle lugs.
    Shape = a saddle CRADLE along the tube (chassis screws, hinge lugs, cable exit) with a
    round O62 PUCK hanging off it around the spool pocket - no dead corners. The cartridge +
    power spring load from BELOW; a round cover plate closes it. The cover's external screws
    are NOT a security hole: the cable's inner end carries a swaged ball stop larger than the
    O7 bushed exit, so even with the spool removed the locked loop cannot be freed."""
    cradle = xbox(SX0, SX1, A3_Y0, CRADLE_Y1, CRADLE_Z0, -SKIRT_Z0)   # full height: saddle arc runs to the skirt, no shelf
    skirt = xbox(SX0, SX1, SKIRT_Y0, SKIRT_Y1, -20.0, -SKIRT_Z0)
    # puck: full round up to the pocket ceiling wall (its flat top is the C2 swing stop); on the
    # C1 side it keeps rising into the cradle / saddle
    puck = cq.Workplane("XY", origin=(PX, POCKET_CY, SZ_BOT)).circle(PUCK_R).extrude(STOP_Z - SZ_BOT)
    puck_hi = cq.Workplane("XY", origin=(PX, POCKET_CY, SZ_BOT)).circle(PUCK_R).extrude(-20.0 - SZ_BOT).intersect(yslab(A3_Y0, 200))
    b = cradle.union(skirt).union(puck).union(puck_hi).cut(cyl_x(SADDLE_R, -1, L + 1))
    b = b.cut(cyl_x(RELIEF3_R, -1, L + 1).intersect(yslab(-200, RELIEF_Y)))
    # knuckle lugs: O11 round the pin + an arm back to the cradle (top at -RELIEF3_R, under C2)
    for (lx0, lx1) in A3_LUGS:
        b = b.union(lug_cyl(lx0, lx1, LUG_R))
        b = b.union(xbox(lx0, lx1, ARM_Y0, A3_Y0 + 1.0, HINGE_Z - LUG_R, -RELIEF3_R))
    # clearance for C2's lug (round about the pin, so it never touches A3 in any position)
    b = b.cut(lug_cyl(C2_LUG[0] - 0.3, C2_LUG[1] + 0.3, LUG_R + 0.5))
    # pin bore: through lug 1 from its outer face, BLIND 2 mm short of lug 2's outer face -
    # the pin cannot be punched out; a press-fit plug hides its entry (CNC_CASING 2A)
    b = b.cut(lug_cyl(A3_LUGS[0][0] - 1, A3_LUGS[1][1] - 2.0, (HPIN_D + HPIN_CLR) / 2))
    # pin ENTRY path: the pin is slid in along +x from outside lug 1, so the cradle's front edge
    # (y 0.5..1.5 inside the pin circle) gets a O6 scallop from the cradle end to the lug (audit)
    b = b.cut(lug_cyl(SX0 - 1, A3_LUGS[0][0], (HPIN_D + HPIN_CLR) / 2 + 0.5))
    b = b.cut(cq.Workplane("XY", origin=(PX, POCKET_CY, SZ_BOT - 1)).circle(POCKET_D / 2).extrude(POCKET_TOP - SZ_BOT + 1))
    # tangential cable exit along -x through the puck wall at the pocket's -y tangent line
    b = b.cut(cq.Workplane("YZ", origin=(SX0 - 1, POCKET_CY - POCKET_D / 2 + EXIT_D / 2 + 0.5, (POCKET_TOP + SZ_BOT) / 2))
              .circle(EXIT_D / 2).extrude(PX - SX0))
    # cover-plate tapped pilots in the puck wall
    for (sx, sy) in COVER_SCREWS:
        b = b.cut(cq.Workplane("XY", origin=(sx, sy, SZ_BOT - 1)).circle(TAP3 / 2).extrude(9))   # 8 tapped: M3x8 countersunk engages 6.8
    # chassis screws: 2 crown (vertical, from inside C1's bottom, y=A3_CROWN_Y) + 2 skirt (horizontal)
    for x in A3_SCREW_X:
        b = b.cut(cq.Workplane("XY", origin=(x, A3_CROWN_Y, -25)).circle(TAP3 / 2).extrude(-(-20 - (-25) - 1.5) - 8))
        b = b.cut(cq.Workplane("XZ", origin=(x, 30, -SKIRT_Z)).circle(TAP3 / 2).extrude(-(SKIRT_Y1 - 1.5 - 30)))
    return b

def build_hinge_block():
    """C2's knuckle: body rides C2's OD outboard of A3's lugs, a web (only over C2's lug span)
    reaches the pin, and the round lug wraps it. Body bottom = pin height, so a 90 deg swing
    keeps every non-round point of it on the C2 side of the seam."""
    body = xbox(HX0, HX1, HB_Y0, HB_Y1, HB_Z0, -20.0)
    web = xbox(C2_LUG[0], C2_LUG[1], HB_Y1 - 0.01, HINGE_Y, HB_Z0, -20.0)
    lug = lug_cyl(C2_LUG[0], C2_LUG[1], LUG_R)
    h = body.union(web).union(lug).cut(cyl_x(R_O + 0.05, -1, L + 1))
    h = h.cut(lug_cyl(C2_LUG[0] - 1, C2_LUG[1] + 1, (HPIN_D + HPIN_CLR) / 2))
    for x in HB_SCREW_X:
        h = h.cut(cq.Workplane("XY", origin=(x, HB_SCREW_Y, HB_Z0 + 1.5)).circle(TAP3 / 2).extrude(30))
    return h

def build_hinge_pin():
    """O5 dowel from 2 mm inside lug 1's face to the blind end in lug 2."""
    return lug_cyl(A3_LUGS[0][0] + 2.0, A3_LUGS[1][1] - 2.0, HPIN_D / 2)

def build_cover_plate():
    p = cq.Workplane("XY", origin=(PX, POCKET_CY, SZ_BOT - COVER_T)).circle(PUCK_R).extrude(COVER_T)
    for (sx, sy) in COVER_SCREWS:
        p = p.cut(cq.Workplane("XY", origin=(sx, sy, SZ_BOT - COVER_T - 1)).circle(CLR3 / 2).extrude(COVER_T + 2))
        cs = (cq.Workplane("XY", origin=(sx, sy, SZ_BOT - COVER_T - 0.01)).circle(3.2)
              .workplane(offset=1.8).circle(1.75).loft())
        p = p.cut(cs)
    return p

def build_window_insert():
    """OPAQUE printed/PC panel (owner Q1: nothing shows). Body fills the through-cutout flush with
    the lid top; the flange sits in a recess in the lid's underside and is clamped by the box wall
    (fitted from inside before the lid goes on, RTV bead). Full antenna-size - a metal lid within a
    few mm of the loop detunes it, so the opening must be at least the board; opacity is free."""
    body = cq.Workplane("XY", origin=(WIN_CX, (BY0 + BY1) / 2, ZTOP + INS_FL_T)).rect(WIN_L - 0.5, WIN_W - 0.5).extrude(LID_T - INS_FL_T).edges("|Z").fillet(3.8)
    flange = cq.Workplane("XY", origin=(WIN_CX, (BY0 + BY1) / 2, ZTOP)).rect(WIN_L + 2 * INS_FLANGE, WIN_W + 2 * INS_FLANGE).extrude(INS_FL_T).edges("|Z").fillet(5.3)
    return body.union(flange)

# ---------------- liner: v0.8 finned geometry + snap studs ----------------
FIN_N, FIN_H, FIN_T, FIN_LEAN = 24, 12.0, 1.4, 30.0   # the v0.8 liner: 24 fins, 12 tall, leaning 30 deg
LINER_BASE, LINER_CLR = 2.0, 0.15                     # base ring thickness / radial clearance to the bore
STUD_D, STUD_H, STUD_HOLE_D, STUD_HOLE_H = 4.5, 1.8, 4.2, 2.0   # TPU press-fit studs: O4.5 printed into O4.2 (+0.1/-0) blind holes,
                                                                    # 0.3 diametral interference - all the compliance is the TPU
STUD_X = (35.0, 115.0)                                # clear of every screw row (25/40/75/100/125)
STUD_PHI = (-45.0, 0.0, 45.0)                         # deg from the half's mid-arc (+y for C1): 3 per x -> 6 studs per half;
                                                      # the mid-arc one sits between the skirt rows, the 45s are 28 deg from both rows

def liner_profile(R_hi):
    """v0.8 fin sketch: base ring + FIN_N fins rooted 0.3 into the ring, leaning FIN_LEAN off radial."""
    sk = cq.Sketch().circle(R_hi).circle(R_hi - LINER_BASE, mode="s")
    embed = LINER_BASE - 0.3
    for i in range(FIN_N):
        ang = math.radians(i * 360.0 / FIN_N + 180.0 / FIN_N)   # fins centred between the seam faces
        lean = math.radians(180 - FIN_LEAN)
        r0 = R_hi - 0.3
        cx, cy = r0 * math.cos(ang), r0 * math.sin(ang)
        ux, uy = math.cos(ang + lean), math.sin(ang + lean)
        vx, vy = -math.sin(ang + lean), math.cos(ang + lean)
        Lf = FIN_H + embed
        quad = [(cx, cy), (cx + Lf * ux, cy + Lf * uy), (cx + Lf * ux + FIN_T * vx, cy + Lf * uy + FIN_T * vy), (cx + FIN_T * vx, cy + FIN_T * vy)]
        sk = sk.polygon(quad, mode="a")
    return sk

def stud_sites(pos):
    """(x, y, z, radial unit vector) of each stud on the half `pos` (True = y>=0)."""
    out = []
    for x in STUD_X:
        for phi in STUD_PHI:
            a = math.radians(phi)
            uy, uz = math.cos(a), math.sin(a)
            if not pos:
                uy = -uy
            out.append((x, uy, uz))
    return out

def stud_cuts(pos):
    """blind radial holes in the tube's inner wall for the liner studs."""
    cuts = None
    for (x, uy, uz) in stud_sites(pos):
        r0 = R_I - 0.5
        c = (cq.Workplane(cq.Plane(origin=(x, uy * r0, uz * r0), xDir=(1, 0, 0), normal=(0, uy, uz)))
             .circle(STUD_HOLE_D / 2).extrude(0.5 + STUD_HOLE_H))
        cuts = c if cuts is None else cuts.union(c)
    return cuts

def build_liner(pos):
    """TPU liner half: v0.8 fins (24 x 12 tall x 1.4, 30 deg lean) on a 2 mm base ring, plus
    4 snap studs on the outside that pop into blind holes in the tube wall - no glue, no
    hardware in the bore, pull to replace. Rear lip locates it axially."""
    R_hi = R_I - LINER_CLR
    body = (cq.Workplane("YZ", origin=(1.0, 0, 0)).placeSketch(liner_profile(R_hi)).extrude(L - LIP_X - 1.5))
    for (x, uy, uz) in stud_sites(pos):
        r0 = R_hi - 0.3
        stud = (cq.Workplane(cq.Plane(origin=(x, uy * r0, uz * r0), xDir=(1, 0, 0), normal=(0, uy, uz)))
                .circle(STUD_D / 2).extrude(0.3 + STUD_H))
        body = body.union(stud)
    half = body.intersect(halfspace(pos))
    # leaning fins next to the seam get sliced by the y=0 plane; keep the ring + rooted fins,
    # drop the detached slivers (they belong to the other half's space)
    best = max(half.solids().vals(), key=lambda x: x.Volume())
    return cq.Workplane(obj=best)


# ---------------- electronics reference bodies (stack-up) ----------------
# Real envelopes of the purchased parts, placed where they live in A1. They are exported as
# ref_* so the SolidWorks pass has them, and the interference matrix + a clearance report
# gate them against the box, the lid and each other.
IX0, IX1 = BX0 + BWALL, BX1 - BWALL          # interior x 13..147
IY0, IY1 = BY0 + BWALL, BY1 - BWALL          # interior y -11..40
BAT_L, BAT_W, BAT_T = 50.0, 34.0, 10.5       # 103450 LiPo (protection PCB end included)
RDR_L, RDR_W, RDR_T = 60.0, 39.0, 4.5        # RC522 board + components (pins removed), antenna in its +x 35 mm; a PN532 (43 x 40.5) fits the same deck
TRAY_T = 1.0                                 # printed tray floor / deck / walls
NANO_L, NANO_W, NANO_H = 45.0, 18.0, 7.5     # Nano LYING FLAT under the boost, pins trimmed flush, USB-C toward -x (the wiring
                                             # bay) so it can be reflashed with the lid off and nothing else removed
TP_L, TP_W, TP_T = 29.0, 17.3, 1.0           # TP4056 USB-C board; connector 9 x 7.5 x 3.3 on top, 1.5 proud of the end
MT_L, MT_W, MT_H = 36.0, 17.0, 7.0           # MT3608 (inductor is the 7)
SOL_L, SOL_W, SOL_H = 28.6, 17.5, 12.7       # Heschen HS-0730B, MEASURED (1 1/8" x 5.5/8" x 1/2")
NANO_X0 = 100.5
DRV_L, DRV_W, DRV_H = 40.0, 10.7, 13.6       # driver card incl. TO-220 lying + O8 cap lying (40: its -x wire end must clear the red button nut)
DRV_X0 = 102.5                               # its -x wire end clears the red button body (x<=99.2)
DRV_Z0 = PIN_Z - SOL_H / 2 - 0.5             # 45.15: top 58.75 sits under the button nuts (z>=59)
BAT_X0 = IX0 + 6.5                           # 19.5: past the lid-screw column (x<=19)
BAT_Y0 = -7.0
RDR_CX, RDR_CY = IX0 + 6.0 + RDR_L / 2, 14.5     # board x 19..79: 1.5 short of the boss; y -5..34 clears both corner columns
DECK_Z = ZTOP - 2.0 - RDR_T - 2.0            # 52: reader top sits 2 under the lid (foam pad)
# The measured HS-0730B is 17.5 wide, so centred on the plunger axis it overhangs the -y
# interior wall by 1.75. A1 gets a LOCAL POCKET in that wall; widening the whole box was tried
# and breaks the C2 swing and the frame-entry mouth (both gated).
SOL_Y0, SOL_Y1 = LATCH_Y - SOL_W / 2, LATCH_Y + SOL_W / 2     # -12.75 .. 4.75
SOL_Z0, SOL_Z1 = PIN_Z - SOL_H / 2, PIN_Z + SOL_H / 2         # 45.65 .. 58.35
POCKET_WALL = 1.0                            # wall left after the local pocket
# layer A (floor -> solenoid underside): TP4056 under the coil, Nano lying flat beside it
TP_Y0 = -5.5                                 # clear of the lid-screw boss (r4 at 145.5,-9.5 reaches y-5.5) and the R4 pocket corner
NANO_Y0 = 16.0                               # clear of the driver card (y<=15.7) so its -y wire edge is reachable
# layer B (beside the solenoid): driver card nearest the coil, then the boost
DRV_Y0 = 5.0                                 # 9 mm from the coil - a short flyback loop
MT_Y0 = 17.0
TP_X1 = IX1 - 1.0                            # board 1 off the end wall; the receptacle face reaches 0.5 INTO the slot so a plug shell
                                             # (6.5 long) mates from the outer recess floor (audit: USB plug gate)
USB_SLOT_W, USB_SLOT_H = 10.0, 4.2               # receptacle 9 x 3.3; the R1.4 corners still clear its square corners

def _box(x0, y0, z0, dx, dy, dz):
    return xbox(x0, x0 + dx, y0, y0 + dy, z0, z0 + dz)

def build_ref_tray():
    """printed furniture: battery cradle floor + 2 walls + reader deck (2 mm, spans the pocket)."""
    t = _box(BAT_X0 - 0.5, BAT_Y0 - 1.5, ZF, BAT_L + 1.0, BAT_W + 3.0, TRAY_T)
    for y in (BAT_Y0 - 1.5, BAT_Y0 + BAT_W + 0.5):
        t = t.union(_box(BAT_X0 - 0.5, y, ZF, BAT_L + 1.0, 1.0, DECK_Z - ZF))
    deck = _box(RDR_CX - RDR_L / 2 - 1.0, RDR_CY - RDR_W / 2 - 0.5, DECK_Z, RDR_L + 2.0, RDR_W + 0.5, 2.0)   # no +y overhang: the LED strip starts at y34
    return t.union(deck)

def build_ref_battery():
    return _box(BAT_X0, BAT_Y0, ZF + TRAY_T, BAT_L, BAT_W, BAT_T)

def build_ref_reader():
    return _box(RDR_CX - RDR_L / 2, RDR_CY - RDR_W / 2, DECK_Z + 2.0, RDR_L, RDR_W, RDR_T)

def build_ref_solenoid():
    """HS-0730B body on two pillars in the -y strip beside the TP4056 (y < -5.5)."""
    body = xbox(SOL_X0, SOL_X0 + SOL_L, SOL_Y0, SOL_Y1, SOL_Z0, SOL_Z1)
    for px in (SOL_X0 + 1, SOL_X0 + SOL_L - 6):
        body = body.union(xbox(px, px + 5, IY0 + 0.5, TP_Y0 - 0.5, ZF, SOL_Z0))
    return body

def _xcyl(x0, x1, r):
    return cq.Workplane("YZ", origin=(x0, LATCH_Y, PIN_Z)).circle(r).extrude(x1 - x0)

def build_ref_cap():
    """hardened latch cap: O8 x 10 with a O10 x 2 rear flange, bored O6.1 x 8 for the plunger."""
    c = _xcyl(CAP_X0, CAP_X0 + CAP_L, CAP_D / 2).union(_xcyl(TUN_STEP_X, CAP_X0 + CAP_L, CAP_FL_D / 2))
    return c.cut(_xcyl(PL_X0, CAP_X0 + CAP_L + 0.1, CAP_BORE / 2))

def build_ref_ret_spring():
    """return spring: flange rear to the coil face."""
    return _xcyl(CAP_X0 + CAP_L, SOL_X0, RSPR_OD / 2).cut(_xcyl(CAP_X0 + CAP_L - 0.1, SOL_X0 + 0.1, RSPR_ID / 2))

def build_ref_bushing():
    """hardened mouth bushing, O10.3 ID, pressed in the boss, through the lid to its top face."""
    z1 = ZTOP + LID_T
    return (cq.Workplane("XY", origin=(LATCH_X, LATCH_Y, BUSH_Z0)).circle(BUSH_OD / 2).extrude(z1 - BUSH_Z0)
            .cut(cq.Workplane("XY", origin=(LATCH_X, LATCH_Y, BUSH_Z0 - 0.1)).circle(BUSH_ID / 2).extrude(z1 - BUSH_Z0 + 0.2)))

def build_ref_head(lift=0.0):
    """cable head, locked position: shoulder on the cap's underside. lift = ejector travel after unlock."""
    zs = CH_SHOULDER_Z + lift
    o = cq.Workplane("XY", origin=(LATCH_X, LATCH_Y, zs - CH_LAND - CH_CONE))
    cone = o.circle(2.0).workplane(offset=CH_CONE).circle(CH_D / 2).loft()
    land = cq.Workplane("XY", origin=(LATCH_X, LATCH_Y, zs - CH_LAND)).circle(CH_D / 2).extrude(CH_LAND)
    groove = cq.Workplane("XY", origin=(LATCH_X, LATCH_Y, zs)).circle(CH_GROOVE_D / 2).extrude(CH_GROOVE_W)
    upper = cq.Workplane("XY", origin=(LATCH_X, LATCH_Y, zs + CH_GROOVE_W)).circle(CH_D / 2).extrude(CH_UPPER)
    ferrule = cq.Workplane("XY", origin=(LATCH_X, LATCH_Y, zs + CH_GROOVE_W + CH_UPPER)).circle(4.0).extrude(ZTOP + LID_T + 12 - (zs + CH_GROOVE_W + CH_UPPER))
    return cone.union(land).union(groove).union(upper).union(ferrule)

def build_ref_ejector():
    """ejector spring on the bore floor around the screw head, compressed under the head's cone."""
    z_top = CH_SHOULDER_Z - CH_LAND - CH_CONE + (EJ_ID / 2 - 2.0) / ((CH_D / 2 - 2.0) / CH_CONE)   # where the cone meets the spring ID
    return (cq.Workplane("XY", origin=(LATCH_X, LATCH_Y, ZF)).circle(EJ_OD / 2).extrude(z_top - ZF)
            .cut(cq.Workplane("XY", origin=(LATCH_X, LATCH_Y, ZF - 0.1)).circle(EJ_ID / 2).extrude(z_top - ZF + 0.2)))

def build_ref_closure_screw():
    """M3x6 low-head cap on a O7 washer on the bore floor, shank down through A1's floor into the block."""
    w = cq.Workplane("XY", origin=(LATCH_X, LATCH_Y, ZF)).circle(CLS_WASHER_D / 2).extrude(CLS_WASHER_T)
    h = cq.Workplane("XY", origin=(LATCH_X, LATCH_Y, ZF + CLS_WASHER_T)).circle(CLS_HEAD_D / 2).extrude(CLS_HEAD_H)
    sh = cq.Workplane("XY", origin=(LATCH_X, LATCH_Y, ZF + CLS_WASHER_T - CLS_L)).circle(1.5).extrude(CLS_L)
    return w.union(h).union(sh)

def build_ref_driver_card():
    return _box(DRV_X0, DRV_Y0, DRV_Z0, DRV_L, DRV_W, DRV_H)

def build_ref_plunger():
    """O6 plunger at rest: nose inside the cap, through the coil, tail cut so it is flush with the back
    frame at full retraction (2.6 inside at rest)."""
    return _xcyl(PL_X0, SOL_X0 + SOL_L + SOL_TAIL, PL_D / 2)

def build_ref_nano():
    return _box(NANO_X0, NANO_Y0, ZF, NANO_L, NANO_W, NANO_H)

def build_ref_tp4056():
    b = _box(TP_X1 - TP_L, TP_Y0, ZF, TP_L, TP_W, TP_T)
    con = _box(TP_X1 - 7.5, TP_Y0 + (TP_W - 9.0) / 2, ZF + TP_T, 9.0, 9.0, 3.3)   # USB-C receptacle, 1.5 proud
    return b.union(con)

WIRE_H = 3.5                                 # solder joint + wire lying on a pad: service height over any board edge
MT_Z0 = ZF + NANO_H + WIRE_H + 0.5           # 49.5: the boost rides above the Nano's wire zone, not on the Nano
def build_ref_mt3608():
    return _box(TP_X1 - MT_L, MT_Y0, MT_Z0, MT_L, MT_W, MT_H)

def build_ref_button(by):
    """12 mm sealed momentary: O12 body 15 deep below the lid + nut"""
    return cq.Workplane("XY", origin=(BTN_X, by, ZTOP - 15.0)).circle(6.0).extrude(15.0)

def build_ref_led(i):
    """5 mm LED body below its lid hole"""
    lx, ly = LED_XY[i]
    return cq.Workplane("XY", origin=(lx, ly, ZTOP - 8.0)).circle(2.6).extrude(8.0)

def build_ref_buzzer():
    """O12 x 9.5 active buzzer, seated up in the lid recess so only 6.5 mm reaches into the cavity"""
    return cq.Workplane("XY", origin=(BUZ_X, BUZ_Y, ZTOP + BUZ_REC - 0.2 - BUZ_H)).circle(BUZ_D / 2).extrude(BUZ_H)

REF_PARTS = {
    "ref_tray": build_ref_tray, "ref_battery": build_ref_battery, "ref_reader": build_ref_reader,
    "ref_solenoid": build_ref_solenoid, "ref_driver_card": build_ref_driver_card,
    "ref_plunger": build_ref_plunger, "ref_cap": build_ref_cap, "ref_ret_spring": build_ref_ret_spring,
    "ref_bushing": build_ref_bushing, "ref_head": build_ref_head, "ref_ejector": build_ref_ejector,
    "ref_closure_screw": build_ref_closure_screw, "ref_nano": build_ref_nano,
    "ref_tp4056": build_ref_tp4056, "ref_mt3608": build_ref_mt3608,
    "ref_button_green": lambda: build_ref_button(BTN_Y), "ref_button_red": lambda: build_ref_button(BTN2_Y),
    "ref_led_1": lambda: build_ref_led(0), "ref_led_2": lambda: build_ref_led(1), "ref_buzzer": build_ref_buzzer,
}

PARTS = {
    "C1_chassis_half": build_c1,
    "C2_clamp_half": build_c2,
    "closure_block": build_closure_block,
    "hinge_block": build_hinge_block,
    "hinge_pin": build_hinge_pin,
    "A1_top_box": build_top_box,
    "A2_lid": build_lid,
    "A3_bottom_box": build_bottom_box,
    "A4_cover_plate": build_cover_plate,
    "A5_window_insert": build_window_insert,
    "liner_right": lambda: build_liner(True),
    "liner_left": lambda: build_liner(False),
}
PARTS.update(REF_PARTS)
# pairs that legitimately touch
ALLOWED_OVERLAP = {("ref_solenoid", "ref_plunger"),       # the plunger runs through the coil
                   ("ref_closure_screw", "closure_block")}  # M3 thread in the O2.5 tapped pilot
CONTACT_OK = {("C1_chassis_half", "C2_clamp_half"), ("C2_clamp_half", "closure_block"),
              ("C2_clamp_half", "hinge_block"), ("closure_block", "A1_top_box"),
              ("A1_top_box", "A2_lid"), ("A3_bottom_box", "A4_cover_plate"), ("A2_lid", "A5_window_insert"),
              ("C1_chassis_half", "liner_right"), ("C2_clamp_half", "liner_left"),
              ("liner_right", "liner_left")}

def gates():
    solids = {k: v().val() for k, v in PARTS.items()}
    names = list(solids)
    bad = 0
    print("[gates] interference matrix")
    n_studs = len(stud_sites(True))
    fit_v = n_studs * math.pi / 4 * (STUD_D ** 2 - STUD_HOLE_D ** 2) * (STUD_H - LINER_CLR)   # designed press-fit volume per liner (embedded depth)
    PRESS_FIT = {("C1_chassis_half", "liner_right"): fit_v, ("C2_clamp_half", "liner_left"): fit_v}
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            inter = cq.Workplane(obj=solids[a]).intersect(cq.Workplane(obj=solids[b]))
            v = sum(s.Volume() for s in inter.solids().vals())
            if (a, b) in ALLOWED_OVERLAP or (b, a) in ALLOWED_OVERLAP:
                continue
            want = PRESS_FIT.get((a, b))
            if want is not None:
                okfit = abs(v - want) <= 0.2 * want
                print(f"  press fit {a} x {b}: {v:.2f} mm^3 (designed {want:.2f}) {'OK' if okfit else 'WRONG'}")
                if not okfit: bad += 1
            elif v > 0.05:
                print(f"  CLASH {a} x {b}: {v:.2f} mm^3"); bad += 1
    print(f"[gates] {bad} clashes")
    # stack-up clearance report: every reference body vs the box, the lid and each other
    env = ["A1_top_box", "A2_lid", "A5_window_insert"] + list(REF_PARTS)
    tight = []
    for i in range(len(env)):
        for j in range(i + 1, len(env)):
            a, b_ = env[i], env[j]
            if a.startswith("ref_") or b_.startswith("ref_"):
                dmin = solids[a].distance(solids[b_])
                if dmin < 1.0:
                    tight.append((dmin, a, b_))
    print("[stackup] reference bodies inside A1 (interior %.0f x %.0f x %.0f):" % (IX1 - IX0, IY1 - IY0, INT_H))
    for n in REF_PARTS:
        bb = solids[n].BoundingBox()
        # two parts deliberately sit in machined recesses rather than the plain cavity
        y_lo = BY0 + POCKET_WALL if n == "ref_solenoid" else IY0
        z_hi = ZTOP + BUZ_REC if n == "ref_buzzer" else (ZTOP + LID_T + 20 if n in ("ref_head", "ref_bushing") else ZTOP)
        z_lo = ZF - CLS_L if n == "ref_closure_screw" else ZF
        x_hi = IX1 + BWALL + 1 if n == "ref_tp4056" else IX1
        inside = (IX0 - 1e-3 <= bb.xmin and bb.xmax <= x_hi + 1e-3 and y_lo - 1e-3 <= bb.ymin
                  and bb.ymax <= IY1 + 1e-3 and z_lo - 1e-3 <= bb.zmin and bb.zmax <= z_hi + 1e-3)
        print(f"  {n:16s} x {bb.xmin:6.1f}..{bb.xmax:6.1f}  y {bb.ymin:6.1f}..{bb.ymax:6.1f}  z {bb.zmin:5.1f}..{bb.zmax:5.1f}  {'in' if inside else 'OUTSIDE'}")
    for dmin, a, b_ in sorted(tight):
        print(f"  gap {dmin:4.2f} mm: {a} - {b_}{'  (contact)' if dmin < 0.01 else ''}")
    print("[stackup] gaps < 1 mm listed above; contacts are the tray floor / cart base on the floor, deck under the reader, plunger at the solenoid face")
    # wall audit: chassis wall left under the deepest point of every countersink (on its axis) >= 2.3,
    # and the seated head's rim must stay inside the bore surface, clear of the liner ring
    csk_depth = (CSK_D - CLR3) / 2
    left = 99.0
    for a in (CROWN_Y, SKIRT_Z, A3_CROWN_Y, 7.0, abs(HB_SCREW_Y)):      # every inside-out row's lateral offset
        left = min(left, math.sqrt(R_O ** 2 - a ** 2) - (math.sqrt(R_I ** 2 - a ** 2) + csk_depth))
    print(f"[gates] chassis wall under the deepest countersink point (all rows): {left:.2f} mm (need >= 2.3) {'PASS' if left >= 2.3 else 'FAIL'}")
    rim_r = math.hypot(R_I - CSK_SUB, HEAD_D / 2)
    left2 = (R_I - LINER_CLR) - rim_r                                   # positive = the head rim is outside the liner ring
    print(f"[gates] seated head rim at r{rim_r:.2f} vs liner ring outer face r{R_I - LINER_CLR:.2f}: {left2:.2f} mm clear {'PASS' if left2 >= 0.05 else 'FAIL'}")
    left2 = 2.3 + left2                                                  # fold into the existing pass condition (>= 2.3 <=> clear >= 0)
    # screw-path probes: each chassis through-hole must be AIR in C1 and land in a box pilot
    c1 = solids["C1_chassis_half"]; tb = solids["A1_top_box"]
    ok = True
    for x in SCREW_X:
        probe = cq.Workplane("XY", origin=(x, CROWN_Y, 26)).circle(1.2).extrude(6)
        v = sum(s.Volume() for s in cq.Workplane(obj=c1).intersect(probe).solids().vals())
        pil = cq.Workplane("XY", origin=(x, CROWN_Y, 33)).circle(1.0).extrude(ZF - 1.0 - 33)
        v2 = sum(s.Volume() for s in cq.Workplane(obj=tb).intersect(pil).solids().vals())
        if v > 0.01 or v2 > 0.01:
            ok = False; print(f"  screw path @x{x}: chassis blocked {v:.2f}, box pilot blocked {v2:.2f}")
    a3 = solids["A3_bottom_box"]
    for x in A3_SCREW_X:
        probe = cq.Workplane("XY", origin=(x, A3_CROWN_Y, -26)).circle(1.2).extrude(-6)
        v = sum(s.Volume() for s in cq.Workplane(obj=c1).intersect(probe).solids().vals())
        pil = cq.Workplane("XY", origin=(x, A3_CROWN_Y, -33)).circle(1.0).extrude(-3)
        v2 = sum(s.Volume() for s in cq.Workplane(obj=a3).intersect(pil).solids().vals())
        if v > 0.01 or v2 > 0.01:
            ok = False; print(f"  A3 screw path @x{x}: chassis blocked {v:.2f}, box pilot blocked {v2:.2f}")
    # closure screw: O3.2 probe from the bore floor through A1's floor into the block's pilot
    probe = cq.Workplane("XY", origin=(LATCH_X, LATCH_Y, 30)).circle(1.2).extrude(ZF + 2 - 30)
    for n in ("A1_top_box", "closure_block"):
        v = sum(s.Volume() for s in cq.Workplane(obj=solids[n]).intersect(probe).solids().vals())
        if v > 0.01:
            ok = False; print(f"  closure screw path blocked in {n}: {v:.2f}")
    print(f"[gates] screw paths (A1 crown, A3 crown, closure) {'PASS' if ok else 'FAIL'}")
    # liner studs: each stud must land in its hole (liner x chassis is already in the clash matrix);
    # here we check the hole is deep enough: stud tip 0.2 short of the hole floor
    for pos, ln, ch in ((True, "liner_right", "C1_chassis_half"), (False, "liner_left", "C2_chassis_half" if False else "C2_clamp_half")):
        for (x, uy, uz) in stud_sites(pos):
            tip = R_I - LINER_CLR - 0.3 + 0.3 + STUD_H
            probe = cq.Workplane(cq.Plane(origin=(x, uy * tip, uz * tip), xDir=(1, 0, 0), normal=(0, uy, uz))).circle(0.8).extrude(0.15)
            v = sum(s.Volume() for s in cq.Workplane(obj=solids[ch]).intersect(probe).solids().vals())
            if v > 0.01:
                ok = False; print(f"  stud @x{x} on {ln}: hole too shallow ({v:.2f} mm^3 of wall at the tip)")
    print(f"[gates] liner stud seats {'PASS' if ok else 'FAIL'}")
    # swing gate: C2 (+ closure block + hinge block) rotates about the pin, 0..OPEN_DEG,
    # against everything on C1. Fine steps near closed (rim swell), coarse to full open.
    movers = ("C2_clamp_half", "closure_block", "hinge_block")
    fixed = ("C1_chassis_half", "A1_top_box", "A2_lid", "A3_bottom_box", "A4_cover_plate", "hinge_pin")
    P0, P1 = cq.Vector(0, HINGE_Y, HINGE_Z), cq.Vector(1, HINGE_Y, HINGE_Z)
    worst = 0.0
    angles = [1, 2, 3, 5, 7, 9, 11, 13, 16, 20, 25, 30, 40, 50, 60, 70, 80, 85, 90]
    angles = [a for a in angles if a <= OPEN_DEG] + [OPEN_DEG]
    rot = {}
    for deg in angles:
        for mv in movers:
            m = solids[mv].rotate(P0, P1, deg)
            rot[(deg, mv)] = m
            for fx in fixed:
                v = sum(x.Volume() for x in cq.Workplane(obj=m).intersect(cq.Workplane(obj=solids[fx])).solids().vals())
                worst = max(worst, v)
                if v > 0.05:
                    print(f"  swing {deg:5.1f}deg: {mv} x {fx} {v:.2f} mm^3")
    print(f"[gates] C2 swing 0-{OPEN_DEG:.0f}deg about the pin: max overlap {worst:.2f} mm^3 {'PASS' if worst <= 0.05 else 'FAIL'}")
    # hinge stop (informational): first angle past OPEN_DEG at which C2's hardware lands on A3
    for deg in range(int(OPEN_DEG) + 1, int(OPEN_DEG) + 25):
        hit = None
        for mv in movers:
            m = solids[mv].rotate(P0, P1, deg)
            v = sum(x.Volume() for x in cq.Workplane(obj=m).intersect(cq.Workplane(obj=solids["A3_bottom_box"])).solids().vals())
            if v > 0.05:
                hit = mv; break
        if hit:
            print(f"[gates] hinge stop: {hit} lands on A3 at {deg} deg (info)"); break
    # frame-entry gate: with C2 at OPEN_DEG, a O46 down tube (the biggest the liner covers)
    # must pass through the MOUTH between C1's rim and C2's swung rim into C1's half-bore.
    # The path is a straight slide along the mouth's bisector (from the origin toward the
    # midpoint of the two rims), which is how a person offers the open clamshell to a tube.
    th = math.radians(OPEN_DEG)
    c2rim = (HINGE_Y + (0 - HINGE_Y) * math.cos(th) - (R_I - HINGE_Z) * math.sin(th),
             HINGE_Z + (0 - HINGE_Y) * math.sin(th) + (R_I - HINGE_Z) * math.cos(th))
    mid = ((0 + c2rim[0]) / 2, (R_I + c2rim[1]) / 2)
    n = math.hypot(*mid); d = (mid[0] / n, mid[1] / n)
    mouth = math.hypot(c2rim[0] - 0, c2rim[1] - R_I)
    print(f"  mouth at {OPEN_DEG:.0f} deg: {mouth:.1f} mm between rims (O46 needs > 46); entry direction ({d[0]:.2f}, {d[1]:.2f})")
    frame_ok = True
    fworst = 0.0
    for t in (80, 70, 60, 50, 40, 30, 20, 12, 6, 0):
        fr = cq.Workplane("YZ", origin=(-5, t * d[0], t * d[1])).circle(23.0).extrude(L + 10).val()
        for nme in movers:
            v = sum(x.Volume() for x in cq.Workplane(obj=rot[(OPEN_DEG, nme)]).intersect(cq.Workplane(obj=fr)).solids().vals())
            fworst = max(fworst, v)
            if v > 0.05:
                frame_ok = False; print(f"  frame entry t={t}: O46 tube x {nme} {v:.1f} mm^3")
        for nme in ("C1_chassis_half", "A1_top_box", "A3_bottom_box"):
            v = sum(x.Volume() for x in cq.Workplane(obj=solids[nme]).intersect(cq.Workplane(obj=fr)).solids().vals())
            fworst = max(fworst, v)
            if v > 0.05:
                frame_ok = False; print(f"  frame entry t={t}: O46 tube x {nme} {v:.1f} mm^3")
    print(f"[gates] O46 frame enters C1 through the mouth with C2 open {OPEN_DEG:.0f}deg: max overlap {fworst:.2f} mm^3 {'PASS' if frame_ok else 'FAIL'}")
    # retention gate: C2 home; pulling it 2 mm in -y MUST be stopped by the pin (hinge block
    # overlaps it) and the closure block MUST seat on the A1 roof (0.2 mm lift overlaps)
    cap = True
    m = solids["hinge_block"].translate(cq.Vector(0, -2.0, 0))
    v = sum(x.Volume() for x in cq.Workplane(obj=m).intersect(cq.Workplane(obj=solids["hinge_pin"])).solids().vals())
    print(f"  retention: hinge block pulled 2mm in -y overlaps the pin by {v:.1f} mm^3 {'(held)' if v > 5 else 'NOT HELD'}")
    cap = cap and v > 5
    m = solids["closure_block"].translate(cq.Vector(0, 0, 0.2))
    v = sum(x.Volume() for x in cq.Workplane(obj=m).intersect(cq.Workplane(obj=solids["A1_top_box"])).solids().vals())
    print(f"  retention: block lifted 0.2mm overlaps A1 roof by {v:.1f} mm^3 {'(seated)' if v > 5 else 'NOT SEATED'}")
    cap = cap and v > 5
    print(f"[gates] retention {'PASS' if cap else 'FAIL'}")
    return bad == 0 and left >= 2.3 and left2 >= 2.3 and ok and worst <= 0.05 and frame_ok and cap


# ---------------- build / wiring audit (--audit) ----------------
# Service envelopes: the space each module needs AROUND it to actually be wired and serviced -
# solder joints and wire exits on its pad edges, panel nuts, LED legs, the USB plug that has to
# reach the TP4056, the harness channel from the cell to the charger. Each may overlap ITS OWN
# module (and the tray); it may not overlap any other module, another envelope, the box or the lid.
SVC_OWNER = {}
LID_MOUNTED = {"ref_button_green", "ref_button_red", "ref_led_1", "ref_led_2", "ref_buzzer", "A2_lid", "A5_window_insert"}

def _svc(name, owner, body):
    SVC_OWNER[name] = owner
    return name, body

def build_svc():
    out = {}
    def add(name, owner, body): out[name] = body; SVC_OWNER[name] = owner
    # Nano: wires soldered on the pin stubs along both long edges, on top
    nx0 = NANO_X0
    add("svc_nano_wires_a", "ref_nano", _box(nx0, NANO_Y0, ZF + NANO_H, NANO_L, 4.0, WIRE_H))
    add("svc_nano_wires_b", "ref_nano", _box(nx0, NANO_Y0 + NANO_W - 4.0, ZF + NANO_H, NANO_L, 4.0, WIRE_H))
    # Nano USB-C plug for reflashing: lid off, plug comes in from -x along the wiring bay
    add("svc_nano_usb_plug", "ref_nano", _box(nx0 - 25.0, NANO_Y0 + NANO_W / 2 - 6.0, ZF, 25.0, 12.0, 7.0))
    # MT3608: pads at both x ends, wires on top
    add("svc_mt_wires_a", "ref_mt3608", _box(TP_X1 - MT_L, MT_Y0, MT_Z0 + MT_H, 4.0, MT_W, WIRE_H))
    add("svc_mt_wires_b", "ref_mt3608", _box(TP_X1 - 4.0, MT_Y0, MT_Z0 + MT_H, 4.0, MT_W, WIRE_H))
    # TP4056: B+/B-/OUT+/OUT- at the -x end (opposite the USB)
    add("svc_tp_wires", "ref_tp4056", _box(TP_X1 - TP_L, TP_Y0, ZF + TP_T, 4.0, TP_W, WIRE_H))
    # driver card: wires at both x ends
    add("svc_drv_wires_a", "ref_driver_card", _box(DRV_X0 - 3.0, DRV_Y0, DRV_Z0, 3.0, DRV_W, DRV_H))
    add("svc_drv_wires_b", "ref_driver_card", _box(DRV_X0 + DRV_L, DRV_Y0, DRV_Z0, 3.0, DRV_W, DRV_H))
    # solenoid: coil leads exit the +x end of the body
    add("svc_sol_leads", "ref_solenoid", _box(SOL_X0 + SOL_L, -5.0, SOL_Z0 + 2.0, 3.0, SOL_Y1 - 1.0 + 5.0, SOL_H - 4.0))   # leads dressed toward +y, clear of the corner boss
    # RC522: header end (-x), wires soldered on top and dropping past the board end
    add("svc_reader_wires", "ref_reader", _box(IX0 + 1.0, RDR_CY - 10.5, DECK_Z - WIRE_H, RDR_CX - RDR_L / 2 + 2.5 - (IX0 + 1.0), 21.0, WIRE_H + 2.0))
    # cell: JST-PH pigtail leaves the protection-PCB end (+x), through a notch in the cradle wall
    add("svc_cell_pigtail", "ref_battery", _box(BAT_X0 + BAT_L, BAT_Y0 + 12.0, ZF + TRAY_T, 8.0, 10.0, 6.0))
    # harness channel cell -> TP4056 along the floor, past the latch boss on its +y side
    add("svc_harness", None, _box(BAT_X0 + BAT_L + 8.0, 6.0, ZF, TP_X1 - TP_L - (BAT_X0 + BAT_L + 8.0), 5.5, 3.0))
    # lid parts: nuts + what hangs below them
    for nm, by in (("green", BTN_Y), ("red", BTN2_Y)):
        add(f"svc_btn_{nm}_nut", f"ref_button_{nm}", cq.Workplane("XY", origin=(BTN_X, by, ZTOP - BTN_NUT_T)).circle(BTN_NUT_D / 2).extrude(BTN_NUT_T))
        add(f"svc_btn_{nm}_lugs", f"ref_button_{nm}", cq.Workplane("XY", origin=(BTN_X, by, ZTOP - 15.0 - BTN_LUG_H)).circle(5.0).extrude(BTN_LUG_H))
    for i, (lx, ly) in enumerate(LED_XY):
        add(f"svc_led_{i+1}_legs", f"ref_led_{i+1}", cq.Workplane("XY", origin=(lx, ly, ZTOP - 8.0 - LED_LEG_H)).circle(2.6).extrude(LED_LEG_H))
    bz0 = ZTOP + BUZ_REC - 0.2 - BUZ_H
    add("svc_buzzer_pins", "ref_buzzer", cq.Workplane("XY", origin=(BUZ_X, BUZ_Y, bz0 - BUZ_PIN_H)).circle(4.0).extrude(BUZ_PIN_H))
    # USB-C charge plug: shell 6.5 long, 8.4 x 2.6, overmold 12 x 6.5 x 20 - must reach the receptacle
    usb_y = TP_Y0 + TP_W / 2; usb_z = ZF + TP_T + 3.3 / 2
    add("svc_usb_shell", "ref_tp4056", cq.Workplane("YZ", origin=(BX1 - 2.0 - 6.5, usb_y, usb_z)).rect(8.4, 2.6).extrude(6.5))
    add("svc_usb_overmold", None, cq.Workplane("YZ", origin=(BX1 - 2.0, usb_y, usb_z)).rect(11.5, 6.0).extrude(20.0))
    return out

def service_gate(solids):
    svc = build_svc()
    others = ["A1_top_box", "A2_lid", "A5_window_insert"] + list(REF_PARTS)
    bad = 0
    print("[audit] service envelopes (wires, nuts, legs, plugs) vs everything they do not own")
    for n, b in svc.items():
        bb = b.val().BoundingBox()
        # every envelope except the two external ones must be inside the cavity
        if n not in ("svc_usb_overmold", "svc_usb_shell"):
            z_hi = ZTOP + BUZ_REC if n == "svc_buzzer_pins" else ZTOP
            inside = (IX0 - 1e-3 <= bb.xmin and bb.xmax <= IX1 + 1e-3 and IY0 - 1e-3 <= bb.ymin and bb.ymax <= IY1 + 1e-3
                      and ZF - 1e-3 <= bb.zmin and bb.zmax <= z_hi + 1e-3)
            if not inside:
                print(f"  OUTSIDE cavity: {n} x {bb.xmin:.1f}..{bb.xmax:.1f} y {bb.ymin:.1f}..{bb.ymax:.1f} z {bb.zmin:.1f}..{bb.zmax:.1f}"); bad += 1
        for o in others:
            if o == SVC_OWNER[n] or o == "ref_tray" or (o == "ref_plunger" and SVC_OWNER[n] == "ref_solenoid"):
                continue
            if n == "svc_nano_usb_plug" and o in LID_MOUNTED:
                continue
            if n == "svc_usb_shell" and o == "A1_top_box":
                pass   # the shell passes through the wall slot: that overlap must be ZERO too
            v = sum(x.Volume() for x in b.intersect(cq.Workplane(obj=solids[o])).solids().vals())
            if v > 0.05:
                print(f"  CLASH {n} x {o}: {v:.1f} mm^3"); bad += 1
    names = list(svc)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b_ = names[i], names[j]
            if SVC_OWNER[a] is not None and SVC_OWNER[a] == SVC_OWNER[b_]:
                continue
            if "svc_nano_usb_plug" in (a, b_) and (SVC_OWNER[a] in LID_MOUNTED or SVC_OWNER[b_] in LID_MOUNTED):
                continue
            v = sum(x.Volume() for x in svc[a].intersect(svc[b_]).solids().vals())
            if v > 0.05:
                print(f"  CLASH {a} x {b_}: {v:.1f} mm^3"); bad += 1
    # USB plug reach: the shell must overlap the receptacle body by >= 5.5 mm along x
    rec = solids["ref_tp4056"]
    inter = svc["svc_usb_shell"].intersect(cq.Workplane(obj=rec))
    depth = 0.0
    if inter.solids().vals():
        ib = inter.val().BoundingBox(); depth = ib.xmax - ib.xmin
    print(f"  USB-C plug insertion into the receptacle: {depth:.1f} mm (need >= 5.5) {'PASS' if depth >= 5.5 else 'FAIL'}")
    if depth < 5.5: bad += 1
    print(f"[audit] service envelopes: {bad} problems {'PASS' if bad == 0 else 'FAIL'}")
    return bad == 0, svc

def _axis_scan(solid, p0, d, length, r_off, step=0.25):
    """walk from p0 along unit d; return list of (t, inside) sampled at radius r_off (4 points)."""
    import itertools
    # two perpendiculars
    ax = cq.Vector(*d)
    tmp = cq.Vector(1, 0, 0) if abs(ax.x) < 0.9 else cq.Vector(0, 1, 0)
    u = ax.cross(tmp).normalized(); v = ax.cross(u).normalized()
    out = []
    t = 0.0
    while t <= length + 1e-9:
        c = cq.Vector(*p0) + ax * t
        hit = False
        for k in range(4):
            q = c + u * (r_off * math.cos(k * math.pi / 2)) + v * (r_off * math.sin(k * math.pi / 2))
            if solid.isInside(q, 1e-3):
                hit = True; break
        out.append((t, hit)); t += step
    return out

def fastener_audit(solids):
    """For every tapped joint: walk the screw axis from the head seat; report the free run to
    the first thread, the tapped length available, and grade the shortest stock screw."""
    ok = True
    print("[audit] fastener engagement (M3 countersunk, inside-out: >= 1.5 D = 4.5 mm in 6061, >= 1.0 D in the steel closure block; no bottoming, tip in air)")
    rows = []
    def seat(a):          # head TOP of an inside-out countersunk screw, measured ALONG its axis, at lateral offset a
        return math.sqrt(R_I ** 2 - a ** 2) + CSK_SUB
    # A1 crown row: axis +z at (x, CROWN_Y), head seat at the counterbore floor inside C1
    for x in SCREW_X:
        rows.append(("A1 crown", (x, CROWN_Y, seat(CROWN_Y)), (0, 0, 1), "A1_top_box", 10.0))
        rows.append(("A1 skirt", (x, seat(SKIRT_Z), SKIRT_Z), (0, 1, 0), "A1_top_box", 10.0))
    for x in A3_SCREW_X:
        rows.append(("A3 crown", (x, A3_CROWN_Y, -seat(A3_CROWN_Y)), (0, 0, -1), "A3_bottom_box", 10.0))
        rows.append(("A3 skirt", (x, seat(SKIRT_Z), -SKIRT_Z), (0, 1, 0), "A3_bottom_box", 10.0))
    for (sx, sy) in LID_SCREWS:
        rows.append(("lid", (sx, sy, ZTOP + LID_T - 1.8), (0, 0, -1), "A1_top_box", 8.0))
    for (sx, sy) in COVER_SCREWS:
        rows.append(("cover", (sx, sy, SZ_BOT - COVER_T + 1.8), (0, 0, 1), "A3_bottom_box", 6.0))   # countersunk: seat 1.8 into the plate
    for x in BLK_SCREW_X:
        rows.append(("closure blk", (x, -7.0, seat(7.0)), (0, 0, 1), "closure_block", 10.0))
    for x in HB_SCREW_X:
        rows.append(("hinge blk", (x, HB_SCREW_Y, -seat(abs(HB_SCREW_Y))), (0, 0, -1), "hinge_block", 10.0))
    rows.append(("closure M3", (LATCH_X, LATCH_Y, ZF + 0.5), (0, 0, -1), "closure_block", 6.0))   # head on a 0.5 washer on the bore floor
    STOCK = (6.0, 8.0, 10.0, 12.0, 16.0, 20.0, 25.0)
    others = [n for n in solids if not n.startswith("ref_") and not n.startswith("liner")]
    for name, p0, d, target, screw in rows:
        tgt = solids[target]
        thread = _axis_scan(tgt, p0, d, 32.0, 1.4)     # material at r1.4: between pilot (r1.25) and shank (r1.5) = tapped wall
        axis = _axis_scan(tgt, p0, d, 32.0, 0.0)       # material ON the axis = pilot ends (blind floor)
        ts = [t for t, h in thread if h]
        if not ts:
            print(f"  {name:12s} @({p0[0]:.0f},{p0[1]:.0f},{p0[2]:.0f}): NO THREAD FOUND"); ok = False; continue
        free = ts[0]
        end = free
        for t, h in thread:                              # contiguous tapped run (a through-tap has no axis floor)
            if t < free: continue
            if h: end = t
            else: break
        floor = next((t for t, h in axis if h and t > free), None)
        avail = (floor if floor is not None else end + 0.25) - free
        need = 3.0 if target == "closure_block" else 4.5      # closure block is steel (1.0 D); everything else 6061 (1.5 D)
        def tip_hits(L):
            tip = cq.Vector(*p0) + cq.Vector(*d) * (L + 0.2)
            return [o for o in others if o != target and solids[o].isInside(tip, 1e-3)]
        good = []
        for L in STOCK:
            eng = min(L - free, avail)
            if eng >= need and not (floor is not None and L - free > avail + 0.3) and L - free <= avail + 0.3 + (99 if floor is None else 0):
                # a through-tap may protrude past the block only into AIR
                if L - free > avail and tip_hits(L): continue
                if floor is None and L - free > avail + 3.0: continue   # do not hang 3+ mm out of a through-tap
                good.append((eng, L))
        if not good:
            ok = False
            print(f"  {name:12s} @x{p0[0]:6.1f}: free run {free:4.1f}  tapped avail {avail:4.1f}  NO STOCK LENGTH WORKS (need {need})"); continue
        spec = [g for g in good if g[1] == screw]
        if spec:                                            # the manual's length works: report it
            eng, L = spec[0]; flag = "OK"
        else:                                               # it does not: fail, and name the shortest that does
            eng, L = min(good, key=lambda g: g[1]); flag = f"FAIL: manual says M3x{screw:.0f}, use M3x{L:.0f}"; ok = False
        print(f"  {name:12s} @x{p0[0]:6.1f}: free run {free:4.1f}  tapped avail {avail:4.1f}{' (thru)' if floor is None else ''}  M3x{L:.0f} engages {eng:4.1f}  {flag}")
    print(f"[audit] fasteners {'PASS' if ok else 'FAIL'}")
    return ok

def insertion_audit(solids):
    """Hinge pin must be pushable in along +x from outside lug 1; a O5 probe from x=20 to the
    bore mouth must be air in every closed-assembly part."""
    ok = True
    probe = lug_cyl(20.0, A3_LUGS[0][0] - 0.5, HPIN_D / 2)
    for n in ("C1_chassis_half", "C2_clamp_half", "A1_top_box", "A3_bottom_box", "A4_cover_plate", "hinge_block", "closure_block"):
        v = sum(x.Volume() for x in probe.intersect(cq.Workplane(obj=solids[n])).solids().vals())
        if v > 0.05:
            print(f"  hinge pin insertion path blocked by {n}: {v:.1f} mm^3"); ok = False
    print(f"[audit] hinge pin insertion path (from -x) {'PASS' if ok else 'FAIL'}")
    # the plug that hides the pin: 2 mm of bore at lug 1's outer face
    return ok

def latch_audit(solids):
    """The latch as a mechanism: rest, retracted and ejected positions, all against the real solids."""
    ok = True
    print("[audit] latch mechanism")
    P = cq.Vector(STROKE, 0, 0)
    movers = {n: cq.Workplane(obj=solids[n].translate(P)) for n in ("ref_cap", "ref_plunger")}
    sp_rest = SOL_X0 - (CAP_X0 + CAP_L); sp_ret = sp_rest - STROKE
    print(f"  return spring: {sp_rest:.1f} mm at rest, {sp_ret:.1f} mm retracted (free {RSPR_FREE}, needs solid <= {sp_ret - 0.3:.1f}) {'PASS' if sp_ret >= 4.0 else 'FAIL'}")
    ok &= sp_ret >= 4.0
    fixed = ["A1_top_box", "A2_lid", "ref_bushing", "ref_head", "ref_solenoid", "ref_tp4056", "ref_driver_card", "ref_nano", "ref_mt3608"]
    for mn, m in movers.items():
        for f in fixed:
            if (mn, f) in (("ref_plunger", "ref_solenoid"),): continue
            v = sum(x.Volume() for x in m.intersect(cq.Workplane(obj=solids[f])).solids().vals())
            if v > 0.05:
                print(f"  RETRACTED {mn} x {f}: {v:.1f} mm^3"); ok = False
    nose_clear = (CAP_X0 + STROKE) - (LATCH_X + BORE_D / 2)
    print(f"  cap nose clear of the bore when retracted: {nose_clear:.2f} mm (need >= 0.5) {'PASS' if nose_clear >= 0.5 else 'FAIL'}")
    ok &= nose_clear >= 0.5
    guided_rest = min(CAP_X0 + CAP_L - CAP_FL_T, TUN_STEP_X) - (LATCH_X + BORE_D / 2)
    guided_ret = TUN_STEP_X - (LATCH_X + BORE_D / 2 + STROKE) if CAP_X0 + STROKE < LATCH_X + BORE_D / 2 else TUN_STEP_X - (CAP_X0 + STROKE)
    print(f"  cap guided in the O8.1 tunnel: {guided_rest:.1f} mm at rest, {guided_ret:.1f} mm retracted (need >= 5) {'PASS' if min(guided_rest, guided_ret) >= 5 else 'FAIL'}")
    ok &= min(guided_rest, guided_ret) >= 5
    prot = PL_REST_PROT
    print(f"  plunger protrusion at rest {prot:.1f} (must lie in the measured {PL_MIN_PROT}..{PL_MAX_PROT}) {'PASS' if PL_MIN_PROT < prot < PL_MAX_PROT else 'FAIL'}")
    ok &= PL_MIN_PROT < prot < PL_MAX_PROT
    tail_ret = SOL_X0 + SOL_L + SOL_TAIL + STROKE
    print(f"  plunger tail at full retraction x{tail_ret:.1f} vs interior wall x{IX1:.1f}: {IX1 - tail_ret:.1f} mm {'PASS' if tail_ret <= IX1 - 0.5 else 'FAIL'}")
    ok &= tail_ret <= IX1 - 0.5
    # ejector: the head must rise until its shoulder is above the cap's centre, or the re-extending cap re-latches it
    ej_travel = EJ_FREE - (solids["ref_ejector"].BoundingBox().zmax - ZF)
    ej_solid_ok = (solids["ref_ejector"].BoundingBox().zmax - ZF) >= EJ_SOLID
    need = CAP_D / 2 + 0.5
    print(f"  ejector travel {ej_travel:.1f} mm (need >= {need:.1f} so the shoulder clears the cap centre); compressed length {solids['ref_ejector'].BoundingBox().zmax - ZF:.1f} >= solid {EJ_SOLID} {'PASS' if ej_travel >= need and ej_solid_ok else 'FAIL'}")
    ok &= ej_travel >= need and ej_solid_ok
    lifted = build_ref_head(ej_travel)
    on_land = PIN_PROT - (BORE_D / 2 - CH_D / 2)          # 1.5: the cap can only re-extend until its nose meets the O10 land
    cap_on_land = cq.Workplane(obj=solids["ref_cap"].translate(cq.Vector(on_land, 0, 0)))
    v = sum(x.Volume() for x in lifted.intersect(cap_on_land).solids().vals())
    shoulder = CH_SHOULDER_Z + ej_travel
    print(f"  ejected head vs cap resting on its land ({on_land:.1f} back): overlap {v:.1f} mm^3; shoulder at z{shoulder:.1f} vs cap centre z{PIN_Z} {'PASS' if v < 0.05 and shoulder > PIN_Z + 0.5 else 'FAIL'}")
    ok &= v < 0.05 and shoulder > PIN_Z + 0.5
    for f in ("A1_top_box", "A2_lid", "ref_bushing"):
        v = sum(x.Volume() for x in lifted.intersect(cq.Workplane(obj=solids[f])).solids().vals())
        if v > 0.05: print(f"  ejected head x {f}: {v:.1f} mm^3"); ok = False
    eng = CH_D / 2 - (BORE_D / 2 - PIN_PROT)
    print(f"  shoulder engagement on the cap: {eng:.2f} mm radial; cap nose to groove root {(BORE_D / 2 - PIN_PROT) - CH_GROOVE_D / 2:.2f} mm clear")
    gap = (BUSH_ID - CH_D) / 2
    print(f"  shim gap head / bushing: {gap:.2f} mm per side (<= 0.25) {'PASS' if gap <= 0.25 else 'FAIL'}"); ok &= gap <= 0.25
    print(f"  groove {CH_GROOVE_W} wide vs cap O{CAP_D}: over-push tolerance {CH_GROOVE_W - CAP_D:.1f} mm")
    nose_tip = CH_SHOULDER_Z - CH_LAND - CH_CONE
    print(f"  head nose tip z{nose_tip:.1f} vs closure screw head top z{ZF + CLS_WASHER_T + CLS_HEAD_H:.1f}: {nose_tip - (ZF + CLS_WASHER_T + CLS_HEAD_H):.1f} mm clear")
    print(f"[audit] latch {'PASS' if ok else 'FAIL'}")
    return bool(ok)

def manufacturability_audit():
    ok = True
    print("[audit] machining / printing numerics")
    checks = [
        ("A1 -y wall left by the solenoid pocket", POCKET_WALL, 1.0, "mm (thin web 32 x 17 - light finishing pass)"),
        ("puck wall outside the cover-screw pilot", PUCK_R - (POCKET_D / 2 + 2.75) - TAP3 / 2, 1.5, "mm"),
        ("puck wall between cover-screw pilot and pocket", (POCKET_D / 2 + 2.75) - TAP3 / 2 - POCKET_D / 2, 1.5, "mm"),
        ("lug wall around the pin bore", LUG_R - (HPIN_D + HPIN_CLR) / 2, 2.5, "mm"),
        ("lid-screw boss wall around the pilot", 4.0 - TAP3 / 2, 2.5, "mm"),
        ("boss wall around the O14 bushing seat", BOSS_D / 2 - BUSH_OD / 2, 2.0, "mm"),
        ("rib wall beside the O10.1 counterbore", (RIB_Y1 - RIB_Y0) / 2 - TUN2_D / 2, 0.9, "mm (the boss carries the load; this is a guide)"),
        ("cap tunnel depth : O8.1", (TUN_STEP_X - (LATCH_X + BORE_D / 2)) / TUN_D, 0, "x D"),
        ("cap end wall (hardened)", CAP_END, 1.5, "mm"),
        ("A1 pocket depth : corner tool O8", INT_H / 8.0, 0, "x D (<= 4 OK)"),
        ("hinge pin blind bore depth : O5.1", (A3_LUGS[1][1] - 2.0 - (A3_LUGS[0][0] - 1)) / (HPIN_D + HPIN_CLR), 0, "x D (<= 10 OK)"),
        ("cable exit bore depth : O7", (PX - (SX0 - 1)) / EXIT_D, 0, "x D"),
        ("liner fin thickness : 0.4 nozzle", FIN_T / 0.4, 3.0, "line widths"),
        ("liner stud overhang (printed axis-up)", STUD_H, 0, "mm sideways stub (<= 2 prints clean in TPU)"),
        ("window insert clearance per side", 0.25, 0.2, "mm (PETG)"),
        ("tray wall", TRAY_T, 0.8, "mm (2 perimeters PETG)"),
    ]
    for label, val, need, unit in checks:
        flag = "" if val >= need else "  <-- LOW"
        if flag: ok = False
        print(f"  {label:48s} {val:6.2f} {unit}{flag}")
    print(f"[audit] manufacturability {'PASS' if ok else 'FAIL'}")
    return ok

def audit():
    g = gates()
    solids = {k: v().val() for k, v in PARTS.items()}
    sv, _ = service_gate(solids)
    f = fastener_audit(solids)
    ins = insertion_audit(solids)
    la = latch_audit(solids)
    m = manufacturability_audit()
    print(f"[audit] SUMMARY gates {'PASS' if g else 'FAIL'} | service {'PASS' if sv else 'FAIL'} | fasteners {'PASS' if f else 'FAIL'} | pin path {'PASS' if ins else 'FAIL'} | latch {'PASS' if la else 'FAIL'} | manufacturability {'PASS' if m else 'FAIL'}")
    return g and sv and f and ins and la and m

if __name__ == "__main__":
    if "--gates" in sys.argv:
        sys.exit(0 if gates() else 1)
    if "--audit" in sys.argv:
        sys.exit(0 if audit() else 1)
    os.makedirs("cnc-design/step", exist_ok=True); os.makedirs("cnc-design/stl", exist_ok=True)
    # sweep out exports of parts that no longer exist (renamed/retired), so the STEP set = PARTS
    keep = set(PARTS) | {"cnc_casing_assembly"}
    for d, ext in (("cnc-design/step", ".step"), ("cnc-design/stl", ".stl")):
        for f in os.listdir(d):
            if f.endswith(ext) and f[: -len(ext)] not in keep:
                os.remove(os.path.join(d, f)); print(f"[clean] removed stale {d}/{f}")
    asm = cq.Assembly()
    for n, f in PARTS.items():
        print(f"[build] {n}", flush=True)
        s = f()
        sol = s.solids().vals()
        if len(sol) != 1:
            raise RuntimeError(f"{n}: {len(sol)} solids")
        cq.exporters.export(s, f"cnc-design/step/{n}.step")
        cq.exporters.export(s, f"cnc-design/stl/{n}.stl", tolerance=0.05, angularTolerance=0.2)
        asm.add(s, name=n)
    asm.save("cnc-design/step/cnc_casing_assembly.step")
    print("[ok] exported")
