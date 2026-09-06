"""cnc_casing_cq.py - the machined casing (CNC_CASING.md 2A): dumb tube-half chassis +
inside-out bolted attachments. Separate lineage from bike_lock_cq.py (printed v0.8.x).

Frame: x = tube axis (0..L), z up, seam plane y=0. C1 = y>=0 chassis half (carries every
attachment), C2 = y<=0 clamp half (carries only the closure block + the K hook block).

Install kinematics (no hinge - see CNC_CASING.md 2A "How C2 goes on"): C2 approaches in +y
sitting RISE low, then the single guarded closure screw lifts it RISE: the closure block rises
behind A1's lip and K's head rises behind A3's lip. Two hooks, one screw, nothing external.

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
RISE     = 2.5                   # C2 installs this much LOW, the closure screw lifts it into both hooks
HK_CLR   = 0.3                   # hook running clearances
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
BY0, BY1 = -17.0, 36.0           # y footprint (straddles the seam; -y overhang carries the block lip)
SADDLE_R = R_O + 0.25            # box underside hugs the tube on the C1 side
RELIEF1_R = R_O + 0.5            # A1 underside over C2 (y<0.3): C2 only ever moves AWAY from A1
RELIEF3_R = R_O + RISE + 0.5     # A3 underside over C2: C2 passes RISE low during install
RELIEF_Y  = 0.3                  # relief extends this far past the seam so C2's face never rubs a step
SWEEP1_Z  = R_O - RISE + 0.5     # 29.75: A1's overhang underside is FLAT at this height outboard of the
                                 # cylinder relief, so the lowered C2 can slide in under it
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
INS_FLANGE, INS_FL_T = 1.5, 1.5  # opaque insert: body fills the cutout flush, flange UNDER the lid (no bezel step to machine)
BTN_D, BTN_X, LED_D, LED_X = 12.4, 118.0, 3.3, 98.0

# ---------------- closure block (on C2, under the box overhang) ----------------
BLK_X0, BLK_X1 = LATCH_X - 10.0, LATCH_X + 10.0
BLK_Y0, BLK_Y1 = -13.0, -1.0
BLK_TOP = 36.5                   # flat top: CONTACTS the A1 pocket roof when the closure screw is tight
BLK_SCREW_X = (LATCH_X - 6.5, LATCH_X + 6.5)   # 2x M3 from inside C2, vertical, at y=-7
LIP1_Y   = BLK_Y0 - HK_CLR       # A1 lip inner face (lip = BY0..LIP1_Y); block rises behind it
LIP1_BOT = BLK_TOP - RISE + 0.5  # 34.5: lip bottom clears the lowered block by 0.5
# ---------------- K hook block (on C2, bottom seam) ----------------
KX0, KX1 = LATCH_X - 20.0, LATCH_X + 20.0   # 40 long, centred under the closure block (no torsion on C2)
K_Y0, K_Y1 = -13.0, -4.3         # body rides C2's OD outboard of A3's lip
K_NECK_Z0, K_NECK_Z1 = -45.5, -43.0   # foot passes under A3's lip
K_HEAD_Y0, K_HEAD_Y1 = -0.9, 3.7      # upturned toe, inside A3's chamber
K_HEAD_TOP = -39.3
K_SCREW_X, K_SCREW_Y = (LATCH_X - 12.0, LATCH_X + 12.0), -8.65   # 2x M3 from inside C2, vertical
LIP3_Y0, LIP3_Y1 = -4.0, -1.2    # A3 lip = the chamber's outer wall (A3 footprint starts at LIP3_Y0)
LIP3_BOT = K_HEAD_TOP - RISE + HK_CLR        # -41.5: clears the lowered head by 0.3, captures 2.2 when risen
CH_Y0, CH_Y1, CH_TOP = -1.2, 4.0, -39.0      # chamber: slot from A3's bottom face (A4 closes it)

# ---------------- bottom box A3 (spool cartridge, top-loaded) ----------------
SX0, SX1 = 30.0, 120.0           # puck box footprint x (90)
A3_Y0 = LIP3_Y0                  # A3 footprint starts at its lip (-4); nothing further over C2
SPOOL_CORE, CABLE_D, CABLE_L = 40.0, 5.0, 1500.0   # O40 core = 10x rope O (7x7 bend rule); 5 ft of O5 coated cable
SPOOL_W = 25.0                   # cartridge width (5 wraps/layer): 2 layers = 1.57 m -> outer O60
POCKET_D = SPOOL_CORE + 4 * CABLE_D + 3.0   # 63: 2 cable layers + clearance
POCKET_CY = CH_Y1 + BWALL + POCKET_D / 2    # 38.5: pocket starts BWALL past the hook chamber
PY1 = POCKET_CY + POCKET_D / 2 + BWALL      # 73
COVER_T = 3.0                    # bottom cover plate (power spring lives INSIDE the O40 hub, as in every retractable reel)
POCKET_TOP = -36.0               # pocket ceiling: below the saddle's lowest point (-32) minus a 4mm floor
SZ_BOT = POCKET_TOP - SPOOL_W - 3.0   # -64: box bottom face
EXIT_D = 7.0                     # bushed cable exit, tangential, out the -x end wall along -x
A3_SCREW_X = (SX0 + 5.0, SX1 - 5.0)   # 35/115: outside the pocket circle and the K chamber; C1's bottom rows match
COVER_SCREWS = [(SX0 + 5, A3_Y0 + 5), (SX0 + 5, PY1 - 5), (SX1 - 5, A3_Y0 + 5), (SX1 - 5, PY1 - 5)]

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

def crown_screw_cuts(zsign, xs):
    """vertical M3 through the crown wall at y=CROWN_Y, counterbored from INSIDE (bore side)."""
    cuts = None
    # counterbore floor: lowest inner-surface point under the O6.2 circle, plus head depth
    y_far = CROWN_Y + CB_D / 2
    z_inner_min = math.sqrt(R_I ** 2 - y_far ** 2)
    z_floor = z_inner_min - CB_H
    for x in xs:
        thru = cq.Workplane("XY", origin=(x, CROWN_Y, 0)).circle(CLR3 / 2).extrude(zsign * 40)
        cb = cq.Workplane("XY", origin=(x, CROWN_Y, zsign * 15)).circle(CB_D / 2).extrude(zsign * (z_floor - 15))
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
    c1 = c1.cut(crown_screw_cuts(-1, A3_SCREW_X)).cut(skirt_screw_cuts(-1, A3_SCREW_X))  # bottom rows -> A3
    return c1

def build_c2():
    c2 = tube_half(False).union(rear_lip(False))
    c2 = c2.cut(block_screw_cuts(BLK_SCREW_X, -7.0, +1)).cut(block_screw_cuts(K_SCREW_X, K_SCREW_Y, -1))
    return c2

def saddle_body(x0, x1, y0, y1, z_lo, z_hi, skirt_sign, relief_r, sweep_z=None):
    """box block spanning z_lo..z_hi minus the tube saddle; +y skirt wraps the tube side."""
    blk = cq.Workplane("XY", origin=((x0 + x1) / 2, (y0 + y1) / 2, (z_lo + z_hi) / 2)).box(x1 - x0, y1 - y0, z_hi - z_lo)
    # skirt: extend the +y wall down/up to SKIRT_Z0 on the tube side
    if skirt_sign > 0:
        skirt = cq.Workplane("XY", origin=((x0 + x1) / 2, (SKIRT_Y0 + y1) / 2, (SKIRT_Z0 + z_lo) / 2)).box(x1 - x0, y1 - SKIRT_Y0, z_lo - SKIRT_Z0)
    else:
        skirt = cq.Workplane("XY", origin=((x0 + x1) / 2, (SKIRT_Y0 + y1) / 2, (-SKIRT_Z0 + z_hi) / 2)).box(x1 - x0, y1 - SKIRT_Y0, -SKIRT_Z0 - z_hi)
    body = blk.union(skirt).cut(cyl_x(SADDLE_R, -1, L + 1))
    relief = cyl_x(relief_r, -1, L + 1).intersect(yslab(-200, RELIEF_Y))
    body = body.cut(relief)
    if sweep_z is not None:   # flat sweep clearance over C2 (its lowered install slide)
        body = body.cut(xbox(-1, L + 1, -200, RELIEF_Y, -200, sweep_z))
    return body

def build_top_box():
    b = saddle_body(BX0, BX1, BY0, BY1, 20.0, ZTOP, +1, RELIEF1_R, SWEEP1_Z)
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
    # closure-block hook pocket (the TOP hook): chamber LIP1_Y..BLK_Y1+0.3 up to the roof at
    # BLK_TOP (block contacts it when the screw is tight); mouth notch through the -y face below
    # LIP1_BOT so the block, riding RISE low, slides in under the lip and then rises behind it
    b = b.cut(xbox(BLK_X0 - 0.2, BLK_X1 + 0.2, LIP1_Y, BLK_Y1 + HK_CLR, 0, BLK_TOP))
    b = b.cut(xbox(BLK_X0 - 0.2, BLK_X1 + 0.2, BY0 - 2, LIP1_Y + 0.01, 0, LIP1_BOT))
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

def build_bottom_box():
    """Vertical-axis spool puck (owner Q2). Cartridge + power spring load from BELOW; a flat
    cover plate closes it. The cover's external screws are NOT a security hole: the cable's
    inner end carries a swaged ball stop larger than the O7 bushed exit, so even with the
    spool removed the locked loop cannot be freed (see CNC_CASING 2A)."""
    b = saddle_body(SX0, SX1, A3_Y0, PY1, SZ_BOT, -20.0, -1, RELIEF3_R)
    # the BOTTOM hook: chamber slot from the bottom face (closed by A4) for K's head, and the
    # mouth under the lip (LIP3_Y0..LIP3_Y1, down to LIP3_BOT) that K's foot passes through
    b = b.cut(xbox(KX0 - 0.3, KX1 + 0.3, CH_Y0, CH_Y1, SZ_BOT - 1, CH_TOP))
    b = b.cut(xbox(KX0 - 0.3, KX1 + 0.3, LIP3_Y0 - 1, CH_Y0 + 0.01, SZ_BOT - 1, LIP3_BOT))
    cx = (SX0 + SX1) / 2
    b = b.cut(cq.Workplane("XY", origin=(cx, POCKET_CY, SZ_BOT - 1)).circle(POCKET_D / 2).extrude(POCKET_TOP - SZ_BOT + 1))
    # tangential cable exit along -x through the -x end wall, at the pocket's -y tangent line
    b = b.cut(cq.Workplane("YZ", origin=(SX0 - 1, POCKET_CY - POCKET_D / 2 + EXIT_D / 2 + 0.5, (POCKET_TOP + SZ_BOT) / 2))
              .circle(EXIT_D / 2).extrude(BWALL + 4))
    # cover-plate tapped pilots in the 4 corners (outside the round pocket)
    for (sx, sy) in COVER_SCREWS:
        b = b.cut(cq.Workplane("XY", origin=(sx, sy, SZ_BOT - 1)).circle(TAP3 / 2).extrude(7))
    # chassis screws: 2 crown (vertical, from inside C1's bottom) + 2 skirt (horizontal, +y side)
    for x in A3_SCREW_X:
        b = b.cut(cq.Workplane("XY", origin=(x, CROWN_Y, -25)).circle(TAP3 / 2).extrude(-(-20 - (-25) - 1.5) - 8))
        b = b.cut(cq.Workplane("XZ", origin=(x, 30, -SKIRT_Z)).circle(TAP3 / 2).extrude(-(PY1 - 1.5 - 30)))
    return b

def build_k_block():
    """K hook block on C2 (bottom seam): body rides C2's OD, foot (neck) reaches +y under A3's
    lip, upturned head sits in A3's chamber. Rising RISE with C2 puts the head behind the lip."""
    body = xbox(KX0, KX1, K_Y0, K_Y1, K_NECK_Z0, -20.0).cut(cyl_x(R_O + 0.05, -1, L + 1))
    neck = xbox(KX0, KX1, K_Y1 - 0.01, K_HEAD_Y1, K_NECK_Z0, K_NECK_Z1)
    head = xbox(KX0, KX1, K_HEAD_Y0, K_HEAD_Y1, K_NECK_Z0, K_HEAD_TOP)
    k = body.union(neck).union(head)
    for x in K_SCREW_X:
        k = k.cut(cq.Workplane("XY", origin=(x, K_SCREW_Y, K_NECK_Z0 + 1.5)).circle(TAP3 / 2).extrude(30))
    return k

def build_cover_plate():
    p = cq.Workplane("XY", origin=((SX0 + SX1) / 2, (A3_Y0 + PY1) / 2, SZ_BOT - COVER_T)).box(SX1 - SX0, PY1 - A3_Y0, COVER_T, centered=(True, True, False))
    p = p.edges("|Z").fillet(CORNER_R)
    for (sx, sy) in COVER_SCREWS:
        p = p.cut(cq.Workplane("XY", origin=(sx, sy, SZ_BOT - COVER_T - 1)).circle(CLR3 / 2).extrude(COVER_T + 2))
        cs = (cq.Workplane("XY", origin=(sx, sy, SZ_BOT - COVER_T - 0.01)).circle(3.2)
              .workplane(offset=1.8).circle(1.75).loft())
        p = p.cut(cs)
    return p

def build_window_insert():
    """OPAQUE printed/PC panel (owner Q1: nothing shows). Body fills the through-cutout flush with
    the lid top; the flange sits UNDER the lid (fitted from inside before the lid goes on, RTV bead). Full antenna-size - a metal lid within a
    few mm of the loop detunes it, so the opening must be at least the board; opacity is free."""
    body = cq.Workplane("XY", origin=(WIN_CX, (BY0 + BY1) / 2, ZTOP)).rect(WIN_L - 0.3, WIN_W - 0.3).extrude(LID_T).edges("|Z").fillet(3.8)
    flange = cq.Workplane("XY", origin=(WIN_CX, (BY0 + BY1) / 2, ZTOP - INS_FL_T)).rect(WIN_L + 2 * INS_FLANGE, WIN_W + 2 * INS_FLANGE).extrude(INS_FL_T).edges("|Z").fillet(5.3)
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
    "K_hook_block": build_k_block,
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
              ("C2_clamp_half", "K_hook_block"), ("closure_block", "A1_top_box"),
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
        probe = cq.Workplane("XY", origin=(x, CROWN_Y, -26)).circle(1.2).extrude(-6)
        v = sum(s.Volume() for s in cq.Workplane(obj=c1).intersect(probe).solids().vals())
        pil = cq.Workplane("XY", origin=(x, CROWN_Y, -33)).circle(1.0).extrude(-3)
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
    # install-path gate: C2 (+ block + K) approaches in +y sitting RISE low, then rises.
    # Every station along both legs must be clash-free against everything on C1.
    movers = ("C2_clamp_half", "closure_block", "K_hook_block")
    fixed = ("C1_chassis_half", "A1_top_box", "A2_lid", "A3_bottom_box", "A4_cover_plate")
    worst = 0.0
    stations = [(-dy, -RISE) for dy in (40, 30, 20, 12, 8, 5, 3, 1.5, 0.5, 0.0)] + \
               [(0.0, -RISE * f) for f in (0.8, 0.6, 0.4, 0.2, 0.0)]
    for (dy, dz) in stations:
        for mv in movers:
            m = solids[mv].translate(cq.Vector(0, dy, dz))
            for fx in fixed:
                v = sum(x.Volume() for x in cq.Workplane(obj=m).intersect(cq.Workplane(obj=solids[fx])).solids().vals())
                worst = max(worst, v)
                if v > 0.05:
                    print(f"  install dy={dy:5.1f} dz={dz:4.1f}: {mv} x {fx} {v:.2f} mm^3")
    print(f"[gates] C2 install path (slide in {RISE} low, rise {RISE}): max overlap {worst:.2f} mm^3 {'PASS' if worst <= 0.05 else 'FAIL'}")
    # capture gate: with C2 home, a -y pull MUST be stopped by BOTH lips (hooks engaged), and the
    # block must sit on the A1 roof (the closure screw clamps against it)
    cap = True
    for mv, fx in (("closure_block", "A1_top_box"), ("K_hook_block", "A3_bottom_box")):
        m = solids[mv].translate(cq.Vector(0, -2.0, 0))
        v = sum(x.Volume() for x in cq.Workplane(obj=m).intersect(cq.Workplane(obj=solids[fx])).solids().vals())
        print(f"  capture: {mv} pulled 2mm in -y overlaps {fx} by {v:.1f} mm^3 {'(hooked)' if v > 5 else 'NOT HOOKED'}")
        cap = cap and v > 5
    m = solids["closure_block"].translate(cq.Vector(0, 0, 0.2))
    v = sum(x.Volume() for x in cq.Workplane(obj=m).intersect(cq.Workplane(obj=solids["A1_top_box"])).solids().vals())
    print(f"  capture: block lifted 0.2mm overlaps A1 roof by {v:.1f} mm^3 {'(seated)' if v > 5 else 'NOT SEATED'}")
    cap = cap and v > 5
    print(f"[gates] hook capture {'PASS' if cap else 'FAIL'}")
    return bad == 0 and left >= 2.3 and left2 >= 2.3 and ok and worst <= 0.05 and cap

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
