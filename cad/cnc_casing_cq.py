"""cnc_casing_cq.py - the machined casing (CNC_CASING.md 2A): dumb tube-half chassis +
inside-out bolted attachments. Separate lineage from bike_lock_cq.py (printed v0.8.x).

Frame: x = tube axis (0..L), z up, seam plane y=0. C1 = y>=0 chassis half (carries every
attachment), C2 = y<=0 clamp half (carries only the closure block + hook groove).

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
HOOK_Y   = 3.0                   # bottom-seam tongue: C1 crosses y=0 by this much
HOOK_R0, HOOK_R1 = 28.0, 30.5    # tongue radial band (inside the wall band)
LIP_X, LIP_R = 2.0, 25.5         # rear liner lip: x L-2..L, inward to r25.5

# ---------------- attachment fastening (M3 low-head cap, inside-out) ----------------
SCREW_X   = (25.0, 75.0, 125.0)  # 3 per row
CROWN_Y   = 6.0                  # vertical crown row (radial ~11deg -> vertical is fine)
SKIRT_Z   = 8.0                  # horizontal skirt row height |z|
CLR3, CB_D, CB_H = 3.4, 6.2, 2.3 # M3 clearance, counterbore O and head depth
TAP3      = 2.5                  # M3 tap drill (modeled pilot)
CLR4, TAP4 = 4.5, 3.3            # closure screw upgraded to M4 (threads into the steel block)

# ---------------- top box A1 ----------------
BX0, BX1 = 10.0, 140.0           # x footprint
BY0, BY1 = -14.0, 36.0           # y footprint (straddles the seam; overhang over C2 = 14)
SADDLE_R = R_O + 0.25            # box underside hugs the tube
SKIRT_Y0, SKIRT_Z0 = 32.0, 3.0   # +y skirt: inner face y32, drops to z3
BWALL    = 3.0
ZF       = 40.0                  # interior floor top (8.25 above the tube crown)
INT_H    = 30.0                  # interior height
ZTOP     = ZF + INT_H            # lid seat
LID_T    = 5.0
CORNER_R = 6.0                   # >= R4 rule (O12 tool)
LATCH_X, LATCH_Y = 58.0, -4.0    # receiver over the C2 side of the seam (closure block below)
BORE_D, BOSS_D   = 11.0, 19.0
PIN_Z    = ZF + 14.0             # plunger axis
PIN_D    = 6.6
LID_SCREWS = [(BX0 + 5, BY0 + 5), (BX0 + 5, BY1 - 5), (BX1 - 5, BY0 + 5), (BX1 - 5, BY1 - 5),
              ((BX0 + BX1) / 2, BY0 + 5), ((BX0 + BX1) / 2, BY1 - 5)]
# RF window (PN532 footprint by default - see open question Q1) + button + LEDs
WIN_L, WIN_W, WIN_CX = 45.2, 43.0, 32.0
BEZEL, WIN_STEP = 2.5, 2.0
BTN_D, BTN_X, LED_D, LED_X = 12.4, 118.0, 3.3, 100.0

# ---------------- closure block (on C2, under the box overhang) ----------------
BLK_X0, BLK_X1 = 48.0, 68.0
BLK_Y0, BLK_Y1 = -13.0, -1.0
BLK_TOP = 36.5                   # flat top; pocketed into the box underside
BLK_SCREW_X = (51.5, 64.5)       # 2x M3 from inside C2, vertical, at y=-7

# ---------------- bottom box A3 (spool cartridge, top-loaded) ----------------
SX0, SX1 = 40.0, 110.0
SPOOL_D, SPOOL_W = 62.0, 30.0    # cartridge envelope (Q2: donor-dependent placeholder)
SZ_BOT = -104.0                  # box bottom
SPOOL_CZ = -68.0                 # pocket axis (along y)
EXIT_D, EXIT_ANG = 7.0, 30.0     # bushed cable exit, angled down out the -x end wall

pod_pocket_r = 6.0

def cyl_x(r, x0, x1):
    return cq.Workplane("YZ", origin=(x0, 0, 0)).circle(r).extrude(x1 - x0)

def halfspace(y_pos):
    """y>=0 (True) or y<=0 (False) keep-box."""
    return cq.Workplane("XY", origin=(L / 2, 200 if y_pos else -200, 0)).box(L + 20, 400, 400)

def tube_half(pos):
    return cyl_x(R_O, 0, L).cut(cyl_x(R_I, -1, L + 1)).intersect(halfspace(pos))

def hook_tongue():
    # prismatic tongue along x at the BOTTOM seam, band r28-30.5, y -HOOK_Y..0
    ring = cyl_x(HOOK_R1, 0, L).cut(cyl_x(HOOK_R0, -1, L + 1))
    box = cq.Workplane("XY", origin=(L / 2, -HOOK_Y / 2, -30)).box(L + 2, HOOK_Y, 10)
    return ring.intersect(box)

def rear_lip(pos):
    lip = cyl_x(R_I + 0.01, L - LIP_X, L).cut(cyl_x(LIP_R, L - LIP_X - 1, L + 1))
    return lip.intersect(halfspace(pos))

def crown_screw_cuts(zsign):
    """vertical M3 through the crown wall at y=CROWN_Y, counterbored from INSIDE (bore side)."""
    cuts = None
    # counterbore floor: lowest inner-surface point under the O6.2 circle, plus head depth
    y_far = CROWN_Y + CB_D / 2
    z_inner_min = math.sqrt(R_I ** 2 - y_far ** 2)
    z_floor = z_inner_min - CB_H
    for x in SCREW_X:
        thru = cq.Workplane("XY", origin=(x, CROWN_Y, 0)).circle(CLR3 / 2).extrude(zsign * 40)
        cb = cq.Workplane("XY", origin=(x, CROWN_Y, zsign * 15)).circle(CB_D / 2).extrude(zsign * (z_floor - 15))
        c = thru.union(cb)
        cuts = c if cuts is None else cuts.union(c)
    return cuts

def skirt_screw_cuts(zsign):
    """horizontal M3 along +y through the side wall at z=SKIRT_Z, counterbored from inside."""
    cuts = None
    z = zsign * SKIRT_Z
    z_far = abs(z) + CB_D / 2
    y_inner_min = math.sqrt(R_I ** 2 - z_far ** 2)
    y_floor = y_inner_min + CB_H
    for x in SCREW_X:
        thru = cq.Workplane("XZ", origin=(x, 0, z)).circle(CLR3 / 2).extrude(-40)   # XZ normal is -y; extrude(-) -> +y
        cb = cq.Workplane("XZ", origin=(x, 15, z)).circle(CB_D / 2).extrude(-(y_floor - 15))
        c = thru.union(cb)
        cuts = c if cuts is None else cuts.union(c)
    return cuts

def block_screw_cuts():
    cuts = None
    y = -7.0
    y_far = abs(y) + CB_D / 2
    z_inner_min = math.sqrt(R_I ** 2 - y_far ** 2)
    z_floor = z_inner_min - CB_H
    for x in BLK_SCREW_X:
        thru = cq.Workplane("XY", origin=(x, y, 0)).circle(CLR3 / 2).extrude(40)
        cb = cq.Workplane("XY", origin=(x, y, 15)).circle(CB_D / 2).extrude(z_floor - 15)
        c = thru.union(cb)
        cuts = c if cuts is None else cuts.union(c)
    return cuts

def build_c1():
    c1 = tube_half(True).union(hook_tongue()).union(rear_lip(True))
    for zs in (+1, -1):
        c1 = c1.cut(crown_screw_cuts(zs)).cut(skirt_screw_cuts(zs))
    return c1

def build_c2():
    c2 = tube_half(False).cut(hook_tongue_clear()).union(rear_lip(False))
    c2 = c2.cut(block_screw_cuts())
    return c2

def hook_tongue_clear():
    ring = cyl_x(HOOK_R1 + 0.15, 0, L).cut(cyl_x(HOOK_R0 - 0.15, -1, L + 1))
    box = cq.Workplane("XY", origin=(L / 2, -(HOOK_Y + 0.15) / 2, -30)).box(L + 2, HOOK_Y + 0.15, 10)
    return ring.intersect(box)

def saddle_body(x0, x1, y0, y1, z_lo, z_hi, skirt_sign):
    """box block spanning z_lo..z_hi minus the tube saddle; +y skirt wraps the tube side."""
    blk = cq.Workplane("XY", origin=((x0 + x1) / 2, (y0 + y1) / 2, (z_lo + z_hi) / 2)).box(x1 - x0, y1 - y0, z_hi - z_lo)
    # skirt: extend the +y wall down/up to SKIRT_Z0 on the tube side
    if skirt_sign > 0:
        skirt = cq.Workplane("XY", origin=((x0 + x1) / 2, (SKIRT_Y0 + y1) / 2, (SKIRT_Z0 + z_lo) / 2)).box(x1 - x0, y1 - SKIRT_Y0, z_lo - SKIRT_Z0)
    else:
        skirt = cq.Workplane("XY", origin=((x0 + x1) / 2, (SKIRT_Y0 + y1) / 2, (-SKIRT_Z0 + z_hi) / 2)).box(x1 - x0, y1 - SKIRT_Y0, -SKIRT_Z0 - z_hi)
    return blk.union(skirt).cut(cyl_x(SADDLE_R, -1, L + 1))

def build_top_box():
    b = saddle_body(BX0, BX1, BY0, BY1, 20.0, ZTOP, +1)
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
    # pocket in the underside over the closure block
    b = b.cut(cq.Workplane("XY", origin=((BLK_X0 + BLK_X1) / 2, (BLK_Y0 + BLK_Y1) / 2, 0))
              .box(BLK_X1 - BLK_X0 + 0.4, BLK_Y1 - BLK_Y0 + 0.4, 2 * BLK_TOP + 0.3))
    # chassis screws thread into the floor (pilots) - crown row vertical, skirt row horizontal
    for x in SCREW_X:
        b = b.cut(cq.Workplane("XY", origin=(x, CROWN_Y, 25)).circle(TAP3 / 2).extrude(ZF - 25 - 1.5))
        b = b.cut(cq.Workplane("XZ", origin=(x, 30, SKIRT_Z)).circle(TAP3 / 2).extrude(-(BY1 - 1.5 - 30)))
    return b

def build_lid():
    p = cq.Workplane("XY", origin=((BX0 + BX1) / 2, (BY0 + BY1) / 2, ZTOP)).box(BX1 - BX0, BY1 - BY0, LID_T, centered=(True, True, False))
    p = p.edges("|Z").fillet(CORNER_R)
    # RF window: through cutout + bezel step for the polycarbonate insert
    p = p.cut(cq.Workplane("XY", origin=(WIN_CX, (BY0 + BY1) / 2, ZTOP - 1)).rect(WIN_L, WIN_W).extrude(LID_T + 2).edges("|Z").fillet(4))
    p = p.cut(cq.Workplane("XY", origin=(WIN_CX, (BY0 + BY1) / 2, ZTOP + LID_T - WIN_STEP)).rect(WIN_L + 2 * BEZEL, WIN_W + 2 * BEZEL).extrude(WIN_STEP + 1).edges("|Z").fillet(5))
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
    blk = blk.cut(cq.Workplane("XY", origin=(LATCH_X, LATCH_Y, 20)).circle(TAP4 / 2).extrude(30))  # M4 tapped (pilot)
    for x in BLK_SCREW_X:
        blk = blk.cut(cq.Workplane("XY", origin=(x, -7.0, 20)).circle(TAP3 / 2).extrude(BLK_TOP - 20 - 1.5))
    return blk

def build_bottom_box():
    b = saddle_body(SX0, SX1, BY0, BY1, SZ_BOT, -20.0, -1)
    # spool pocket: cylinder along y, top-loaded through a window toward the saddle
    pocket = cq.Workplane("XZ", origin=((SX0 + SX1) / 2, BY0 + BWALL, SPOOL_CZ)).circle(SPOOL_D / 2).extrude(-(BY1 - BY0 - 2 * BWALL))
    b = b.cut(pocket)
    load = cq.Workplane("XY", origin=((SX0 + SX1) / 2, (BY0 + BY1) / 2, SPOOL_CZ)).box(SPOOL_D, BY1 - BY0 - 2 * BWALL, -SPOOL_CZ - 20)
    b = b.cut(load)
    # bushed cable exit: angled down out the -x end wall
    ex = (cq.Workplane("YZ", origin=(SX0 - 5, 11.0, SPOOL_CZ - 8)).circle(EXIT_D / 2).extrude(25)
          .rotate((SX0, 11.0, SPOOL_CZ - 8), (SX0, 12.0, SPOOL_CZ - 8), -EXIT_ANG))
    b = b.cut(ex)
    for x in (55.0, 95.0):   # bottom box uses 2 crown + 2 skirt screws (shorter box)
        b = b.cut(cq.Workplane("XY", origin=(x, CROWN_Y, -25)).circle(TAP3 / 2).extrude(-(20 - 25 + 1.5) if False else -(-20 - (-25) - 1.5)))
        b = b.cut(cq.Workplane("XZ", origin=(x, 30, -SKIRT_Z)).circle(TAP3 / 2).extrude(-(BY1 - 1.5 - 30)))
    return b

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
    "A1_top_box": build_top_box,
    "A2_lid": build_lid,
    "A3_bottom_box": build_bottom_box,
    "liner_right": lambda: build_liner(True),
    "liner_left": lambda: build_liner(False),
}
# pairs that legitimately touch
CONTACT_OK = {("C1_chassis_half", "C2_clamp_half"), ("C2_clamp_half", "closure_block"),
              ("A1_top_box", "A2_lid"), ("C1_chassis_half", "liner_right"), ("C2_clamp_half", "liner_left"),
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
        pil = cq.Workplane("XY", origin=(x, CROWN_Y, 33)).circle(1.0).extrude(5)
        v2 = sum(s.Volume() for s in cq.Workplane(obj=tb).intersect(pil).solids().vals())
        if v > 0.01 or v2 > 0.01:
            ok = False; print(f"  screw path @x{x}: chassis blocked {v:.2f}, box pilot blocked {v2:.2f}")
    print(f"[gates] crown screw paths {'PASS' if ok else 'FAIL'}")
    return bad == 0 and left >= 2.3 and left2 >= 2.3 and ok

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
