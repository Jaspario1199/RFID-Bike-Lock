"""cnc_casing_cq.py - the machined casing (CNC_CASING.md 2A): dumb tube-half chassis +
inside-out bolted attachments. Separate lineage from bike_lock_cq.py (printed v0.8.x).

Frame: x = tube axis (0..L), z up, seam plane y=0. C1 = y>=0 chassis half (carries every
attachment), C2 = y<=0 clamp half (carries the closure block + the hinge knuckle block).

Hinge (CNC_CASING.md 2A "How C2 goes on"): a O5 pin along x at P=(HINGE_Y, HINGE_Z), just
below the seam on the C2 side. Knuckles on A3 (two lugs + arms) and one lug on C2's hinge
block. C2 swings OPEN_DEG open for the frame to drop into C1, swings shut, and the single
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
OPEN_DEG = 90.0                  # swing the gates prove
LIP_X, LIP_R = 2.0, 25.5         # rear liner lip: x L-2..L, inward to r25.5

# ---------------- attachment fastening (M3 low-head cap, inside-out) ----------------
SCREW_X   = (25.0, 75.0, 125.0)  # 3 per row
CROWN_Y   = 6.0                  # vertical crown row (radial ~11deg -> vertical is fine)
SKIRT_Z   = 8.0                  # horizontal skirt row height |z|
CLR3, CB_D, CB_H = 3.4, 6.2, 2.3 # M3 clearance, counterbore O and head depth
TAP3      = 2.5                  # M3 tap drill (modeled pilot)
CLR4, TAP4 = 3.4, 2.5            # closure screw stays M3 (owner) - threads the steel block; O2.5 pilot doubles as the PETG self-tap pilot in Stage 1

# ---------------- top box A1 ----------------
BX0, BX1 = 10.0, 140.0           # x footprint
BY0, BY1 = -14.0, 36.0           # y footprint (straddles the seam; 14 mm overhang over C2)
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
CORNER_R = 6.0                   # >= R4 rule (O12 tool)
LATCH_X, LATCH_Y = 78.0, -4.0    # receiver over the C2 side of the seam (closure block below); x leaves
                                 # the reader window (x 20..65) clear on -x and the solenoid cart (44) on +x
BORE_D, BOSS_D   = 11.0, 19.0
PIN_Z    = ZF + 14.0             # plunger axis
PIN_D    = 6.6
LID_SCREWS = [(BX0 + 5, BY0 + 5), (BX0 + 5, BY1 - 5), (BX1 - 5, BY0 + 5), (BX1 - 5, BY1 - 5)]   # 4 corners (the 43-wide window leaves no side band for more)
# RF window (PN532 footprint by default - see open question Q1) + button + LEDs
WIN_L, WIN_W = 45.2, 43.0        # through-cutout = PN532 antenna footprint + 1 (metal lid must clear the loop)
WIN_X0 = BX0 + 10.0              # 20: past the -x corner lid screws
WIN_CX = WIN_X0 + WIN_L / 2      # 42.6
INS_FLANGE, INS_FL_T = 2.5, 1.5  # opaque insert: body fills the cutout flush; flange sits in a recess milled
                                 # in the lid's UNDERSIDE (nothing shows on top; the box wall clamps it)
BTN_D, BTN_X, LED_D, LED_X = 12.4, 118.0, 3.3, 98.0

# ---------------- closure block (on C2, under the box overhang) ----------------
BLK_X0, BLK_X1 = LATCH_X - 10.0, LATCH_X + 10.0
BLK_Y0, BLK_Y1 = -13.0, -1.0
BLK_TOP = 36.5                   # flat top: CONTACTS the A1 pocket roof when the closure screw is tight
BLK_SCREW_X = (LATCH_X - 6.5, LATCH_X + 6.5)   # 2x M3 from inside C2, vertical, at y=-7
# ---------------- hinge block (on C2, carries C2's lug) ----------------
HB_Y0, HB_Y1 = -15.0, HINGE_Y - LUG_R - 0.3    # body rides C2's OD outboard of A3's lugs (-15..-8.8)
HB_Z0 = HINGE_Z                  # body bottom = pin height: nothing of C2 sits below the pin
                                 # except its round lug, so a 90 deg swing never enters A3
HB_SCREW_X, HB_SCREW_Y = (LATCH_X - 12.0, LATCH_X + 12.0), -11.9   # 2x M3 from inside C2, vertical

# ---------------- bottom box A3 (spool cartridge, top-loaded) ----------------
SX0, SX1 = 40.0, 100.0           # A3 cradle footprint x (60)
A3_Y0 = 0.5                      # A3 body sits wholly on the C1 side; only its knuckle lugs + arms reach over
ARM_Y0 = HINGE_Y                 # lug arm: from the pin centre to the body, top at -RELIEF3_R
A3_CROWN_Y = 10.0                # A3's crown row sits at y=10 (clear of the pin zone y -8.5..2.5)
SPOOL_CORE, CABLE_D, CABLE_L = 32.0, 4.0, 1500.0   # 3 mm 7x7 wire PVC-coated to O4 on a O32 core (10.7x wire O)
SPOOL_W = 24.0                   # cartridge width (6 wraps/layer): 2 layers = 1.51 m -> outer O48
POCKET_D = SPOOL_CORE + 4 * CABLE_D + 3.0   # 51: 2 cable layers + clearance
PUCK_WALL = 5.5                  # round puck wall (thick enough to carry the cover screws in it)
PUCK_R = POCKET_D / 2 + PUCK_WALL            # 31 -> O62 puck
CRADLE_Y1, CRADLE_Z0 = 36.0, -44.0           # saddle cradle along the tube: carries the chassis screws + hinge lugs
SKIRT_Y1 = 44.0                  # A3 skirt is a 12 mm rib (y 32..44), not the full box width
POCKET_CY = HINGE_Y + LUG_R + BWALL + POCKET_D / 2   # 33: pocket starts BWALL past the lug zone
PX = (SX0 + SX1) / 2             # puck axis x
PY1 = POCKET_CY + PUCK_R         # 64: outermost point of the puck
COVER_T = 3.0                    # bottom cover plate (power spring lives INSIDE the O40 hub, as in every retractable reel)
POCKET_TOP = -36.0               # pocket ceiling: below the saddle's lowest point (-32) minus a 4mm floor
SZ_BOT = POCKET_TOP - SPOOL_W - 3.0   # -64: box bottom face
EXIT_D = 7.0                     # bushed cable exit, tangential, out the -x end wall along -x
A3_SCREW_X = (SX0 + 5.0, SX1 - 5.0)   # 45/95: in the cradle corners, 8 mm outside the pocket circle; C1's bottom rows match
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

def crown_screw_cuts(zsign, xs, cy=CROWN_Y):
    """vertical M3 through the crown wall at y=cy, counterbored from INSIDE (bore side)."""
    cuts = None
    # counterbore floor: lowest inner-surface point under the O6.2 circle, plus head depth
    y_far = cy + CB_D / 2
    z_inner_min = math.sqrt(R_I ** 2 - y_far ** 2)
    z_floor = z_inner_min - CB_H
    for x in xs:
        thru = cq.Workplane("XY", origin=(x, cy, 0)).circle(CLR3 / 2).extrude(zsign * 40)
        cb = cq.Workplane("XY", origin=(x, cy, zsign * 15)).circle(CB_D / 2).extrude(zsign * (z_floor - 15))
        c = thru.union(cb)
        cuts = c if cuts is None else cuts.union(c)
    return cuts

def skirt_screw_cuts(zsign, xs):
    """horizontal M3 along +y through the side wall at z=SKIRT_Z, counterbored from inside."""
    cuts = None
    z = zsign * SKIRT_Z
    z_far = abs(z) + CB_D / 2
    y_inner_min = math.sqrt(R_I ** 2 - z_far ** 2)
    y_floor = y_inner_min + CB_H
    for x in xs:
        thru = cq.Workplane("XZ", origin=(x, 0, z)).circle(CLR3 / 2).extrude(-40)   # XZ normal is -y; extrude(-) -> +y
        cb = cq.Workplane("XZ", origin=(x, 15, z)).circle(CB_D / 2).extrude(-(y_floor - 15))
        c = thru.union(cb)
        cuts = c if cuts is None else cuts.union(c)
    return cuts

def block_screw_cuts(xs, y, zsign):
    """vertical M3 through C2's wall at y (top wall zsign=+1, bottom wall -1), counterbored from inside."""
    cuts = None
    y_far = abs(y) + CB_D / 2
    z_inner_min = math.sqrt(R_I ** 2 - y_far ** 2)
    z_floor = z_inner_min - CB_H
    for x in xs:
        thru = cq.Workplane("XY", origin=(x, y, 0)).circle(CLR3 / 2).extrude(zsign * 40)
        cb = cq.Workplane("XY", origin=(x, y, zsign * 15)).circle(CB_D / 2).extrude(zsign * (z_floor - 15))
        c = thru.union(cb)
        cuts = c if cuts is None else cuts.union(c)
    return cuts

def build_c1():
    c1 = tube_half(True).union(rear_lip(True))
    c1 = c1.cut(crown_screw_cuts(+1, SCREW_X)).cut(skirt_screw_cuts(+1, SCREW_X))        # top rows -> A1
    c1 = c1.cut(crown_screw_cuts(-1, A3_SCREW_X, A3_CROWN_Y)).cut(skirt_screw_cuts(-1, A3_SCREW_X))  # bottom rows -> A3
    return c1

def build_c2():
    c2 = tube_half(False).union(rear_lip(False))
    c2 = c2.cut(block_screw_cuts(BLK_SCREW_X, -7.0, +1)).cut(block_screw_cuts(HB_SCREW_X, HB_SCREW_Y, -1))
    return c2

def saddle_body(x0, x1, y0, y1, z_lo, z_hi, skirt_sign, relief_r):
    """box block spanning z_lo..z_hi minus the tube saddle; +y skirt wraps the tube side."""
    blk = cq.Workplane("XY", origin=((x0 + x1) / 2, (y0 + y1) / 2, (z_lo + z_hi) / 2)).box(x1 - x0, y1 - y0, z_hi - z_lo)
    # skirt: extend the +y wall down/up to SKIRT_Z0 on the tube side
    if skirt_sign > 0:
        skirt = cq.Workplane("XY", origin=((x0 + x1) / 2, (SKIRT_Y0 + y1) / 2, (SKIRT_Z0 + z_lo) / 2)).box(x1 - x0, y1 - SKIRT_Y0, z_lo - SKIRT_Z0)
    else:
        skirt = cq.Workplane("XY", origin=((x0 + x1) / 2, (SKIRT_Y0 + y1) / 2, (-SKIRT_Z0 + z_hi) / 2)).box(x1 - x0, y1 - SKIRT_Y0, -SKIRT_Z0 - z_hi)
    body = blk.union(skirt).cut(cyl_x(SADDLE_R, -1, L + 1))
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
    # plunger channel from the +x side into the bore
    b = b.cut(cq.Workplane("YZ", origin=(LATCH_X, LATCH_Y, PIN_Z)).circle(PIN_D / 2).extrude(BOSS_D))
    # closure-block pocket: OPEN through the -y face (the block swings in and out with C2 on
    # the hinge); x walls locate the block, the roof at BLK_TOP is what the screw clamps against
    b = b.cut(xbox(BLK_X0 - 0.2, BLK_X1 + 0.2, BY0 - 2, BLK_Y1 + 0.3, 0, BLK_TOP))
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
    p = p.cut(cq.Workplane("XY", origin=(WIN_CX, (BY0 + BY1) / 2, ZTOP - 1)).rect(WIN_L + 2 * INS_FLANGE + 0.2, WIN_W + 2 * INS_FLANGE + 0.2).extrude(INS_FL_T + 1).edges("|Z").fillet(5.4))
    p = p.cut(cq.Workplane("XY", origin=(LATCH_X, LATCH_Y, ZTOP - 1)).circle(BORE_D / 2 + 0.3).extrude(LID_T + 2))
    p = p.cut(cq.Workplane("XY", origin=(BTN_X, 12.0, ZTOP - 1)).circle(BTN_D / 2).extrude(LID_T + 2))
    for ly in (6.0, 18.0):
        p = p.cut(cq.Workplane("XY", origin=(LED_X, ly, ZTOP - 1)).circle(LED_D / 2).extrude(LID_T + 2))
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
        blk = blk.cut(cq.Workplane("XY", origin=(x, -7.0, 20)).circle(TAP3 / 2).extrude(BLK_TOP - 20 - 1.5))
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
    cradle = xbox(SX0, SX1, A3_Y0, CRADLE_Y1, CRADLE_Z0, -20.0)
    skirt = xbox(SX0, SX1, SKIRT_Y0, SKIRT_Y1, -20.0, -SKIRT_Z0)
    puck = cq.Workplane("XY", origin=(PX, POCKET_CY, SZ_BOT)).circle(PUCK_R).extrude(-20.0 - SZ_BOT)
    b = cradle.union(skirt).union(puck).cut(cyl_x(SADDLE_R, -1, L + 1))
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
    b = b.cut(cq.Workplane("XY", origin=(PX, POCKET_CY, SZ_BOT - 1)).circle(POCKET_D / 2).extrude(POCKET_TOP - SZ_BOT + 1))
    # tangential cable exit along -x through the puck wall at the pocket's -y tangent line
    b = b.cut(cq.Workplane("YZ", origin=(SX0 - 1, POCKET_CY - POCKET_D / 2 + EXIT_D / 2 + 0.5, (POCKET_TOP + SZ_BOT) / 2))
              .circle(EXIT_D / 2).extrude(PX - SX0))
    # cover-plate tapped pilots in the puck wall
    for (sx, sy) in COVER_SCREWS:
        b = b.cut(cq.Workplane("XY", origin=(sx, sy, SZ_BOT - 1)).circle(TAP3 / 2).extrude(7))
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
    body = cq.Workplane("XY", origin=(WIN_CX, (BY0 + BY1) / 2, ZTOP + INS_FL_T)).rect(WIN_L - 0.3, WIN_W - 0.3).extrude(LID_T - INS_FL_T).edges("|Z").fillet(3.8)
    flange = cq.Workplane("XY", origin=(WIN_CX, (BY0 + BY1) / 2, ZTOP)).rect(WIN_L + 2 * INS_FLANGE, WIN_W + 2 * INS_FLANGE).extrude(INS_FL_T).edges("|Z").fillet(5.3)
    return body.union(flange)

def build_liner(pos):
    """unchanged v0.8 liner concept: base ring r24.85-26.85 + 24 fins, split at the seam."""
    base = cyl_x(26.85, 1.0, L - LIP_X - 0.5).cut(cyl_x(24.85, 0, L))
    fins = None
    for i in range(24):
        a = 2 * math.pi * i / 24 + math.pi / 24
        f = (cq.Workplane("XY", origin=((L - LIP_X - 0.5 + 1.0) / 2, 0, 0))
             .box(L - LIP_X - 1.5, 1.2, 4.0, centered=(True, True, False)).translate((0, 0, 21.0))
             .rotate((0, 0, 0), (1, 0, 0), math.degrees(a)))
        fins = f if fins is None else fins.union(f)
    return base.union(fins).intersect(halfspace(pos))

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
# pairs that legitimately touch
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
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            inter = cq.Workplane(obj=solids[a]).intersect(cq.Workplane(obj=solids[b]))
            v = sum(s.Volume() for s in inter.solids().vals())
            if v > 0.05:
                print(f"  CLASH {a} x {b}: {v:.2f} mm^3"); bad += 1
    print(f"[gates] {bad} clashes")
    # wall audit: remaining chassis wall under every counterbore >= 2.3
    y_far = CROWN_Y + CB_D / 2
    left = (math.sqrt(R_O ** 2 - y_far ** 2)) - (math.sqrt(R_I ** 2 - y_far ** 2) - CB_H)
    print(f"[gates] crown-row wall under counterbore floor: {left:.2f} mm (need >= 2.3) {'PASS' if left >= 2.3 else 'FAIL'}")
    z_far = SKIRT_Z + CB_D / 2
    left2 = math.sqrt(R_O ** 2 - z_far ** 2) - (math.sqrt(R_I ** 2 - z_far ** 2) + CB_H)
    print(f"[gates] skirt-row wall under counterbore floor: {left2:.2f} mm (need >= 2.3) {'PASS' if left2 >= 2.3 else 'FAIL'}")
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
    # frame-entry gate: with C2 at OPEN_DEG, a O46 down tube (the biggest the liner covers)
    # must slide sideways into C1's half-bore without touching the open C2 or anything on C1
    frame_ok = True
    fworst = 0.0
    for dy in (-70, -60, -50, -40, -30, -20, -10, -5, 0):
        fr = cq.Workplane("YZ", origin=(-5, dy, 0)).circle(23.0).extrude(L + 10).val()
        for n in movers:
            v = sum(x.Volume() for x in cq.Workplane(obj=rot[(OPEN_DEG, n)]).intersect(cq.Workplane(obj=fr)).solids().vals())
            fworst = max(fworst, v)
            if v > 0.05:
                frame_ok = False; print(f"  frame entry dy={dy}: O46 tube x {n} {v:.1f} mm^3")
        for n in ("C1_chassis_half", "A1_top_box", "A3_bottom_box"):
            v = sum(x.Volume() for x in cq.Workplane(obj=solids[n]).intersect(cq.Workplane(obj=fr)).solids().vals())
            fworst = max(fworst, v)
            if v > 0.05:
                frame_ok = False; print(f"  frame entry dy={dy}: O46 tube x {n} {v:.1f} mm^3")
    print(f"[gates] O46 frame enters C1 with C2 open {OPEN_DEG:.0f}deg: max overlap {fworst:.2f} mm^3 {'PASS' if frame_ok else 'FAIL'}")
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

if __name__ == "__main__":
    if "--gates" in sys.argv:
        sys.exit(0 if gates() else 1)
    os.makedirs("cnc-design/step", exist_ok=True); os.makedirs("cnc-design/stl", exist_ok=True)
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
