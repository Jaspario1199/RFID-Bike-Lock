#!/usr/bin/env python3
"""
RFID Bike Lock - parametric housing v0.4 "slim top" (CadQuery / STEP)
=====================================================================
Layout change from v0.3 (which is archived in cad/archive/v0.3/):

  * TOP POD is slim: only the latch (bore + solenoid), the PN532 under its
    window, wake button + LEDs. Pod shrinks 156x61x37 -> 126x56x25 outer.
  * BOTTOM BAY: everything else lives beside the spool drum in a saddle-bag
    module - LiPo battery + MT3608 in the rear tunnel, TP4056 + USB-C in
    the front tunnel, zip-anchor grids for Nano/perfboard.
  * WIRE SPINE: a hollow rib on the right shell side carries the harness
    from the bay's rear tunnel up into the pod (feed drilled through the
    pod wall under the belt). A corner duct inside the bay links the two
    tunnels past the drum.
  * Battery switches 18650 -> 103450 LiPo pouch (34 x 50.5 x 10.5) because
    a 76 mm rigid cell cannot package beside the drum. Cam-lock backstop
    dropped (no wall tall enough in the slim pod); USB power-bank unlock
    remains the dead-battery path.

Usage:  python bike_lock_cq.py [part ...]   ->  step/<part>.step + stl/<part>.stl
"""
import math
import sys
import cadquery as cq

# ---------------- core ----------------
shell_id, shell_wall, shell_len = 54.0, 4.0, 150.0
R_in, R_out = shell_id / 2, shell_id / 2 + shell_wall

# ---------------- slim top pod ----------------
pod_ix, pod_iy, pod_wall, pod_h, lid_t = 120.0, 50.0, 3.0, 22.0, 3.0
z_crown = R_out                      # 31
z_lid0 = z_crown + pod_h             # 53
z_lidtop = z_lid0 + lid_t            # 56
pod_ox, pod_oy = pod_ix + 2 * pod_wall, pod_iy + 2 * pod_wall
draft, r_pod, r_belt, edge = 1.5, 10.0, 13.0, 1.2
POD_CX = 60.0                        # pod plan center -> pod spans x -3..123

# ---------------- belt / closure ----------------
belt_t, belt_z0 = 4.0, 14.0
belt_z1 = z_crown + 8
belt_oy = pod_oy + 2 * belt_t
gap, clr = 0.8, 0.5
pad_l, pad_w, pad_h = 26.0, 16.0, 6.0

# ---------------- latch (plunger-as-pin) ----------------
bore_d, bore_depth, bore_x = 11.0, 26.0, 58.0
bore_y = -pod_iy / 2 + 14            # -11
boss_d = bore_d + 8
plunger_d = 6.0
pin_ch_d = plunger_d + 0.6
head_seat = 11.5
pin_z = z_lidtop - head_seat         # 44.5
closure_screw_d = 4.4
sol_len, sol_w, sol_h = 30.0, 13.4, 15.0     # VERIFY
sol_axis_h = 7.5                     # VERIFY
sol_hole_dx, sol_hole_d = 24.0, 2.2  # VERIFY
ped_top = pin_z - sol_axis_h         # 37

# ---------------- pads (pedestal only in v0.4) ----------------
PAD_Z, PAD, PAD_PILOT = 32.0, 12.0, 2.6
pads_pedestal = [(68, bore_y), (94, bore_y)]

# ---------------- lid ----------------
pn532_l, pn532_w, pn532_x = 43.2, 41.0, 2.0          # VERIFY
pn532_hole_dx, pn532_hole_dy = 36.5, 33.5            # VERIFY
window_remain, nfc_cx = 1.2, 23.6
button_d, button_x, button_y = 12.4, 106.0, 8.0      # VERIFY
led_d = 3.3

# ---------------- liner ----------------
fin_n, fin_h, fin_t, fin_lean, liner_base = 24, 12.0, 1.4, 30.0, 2.0

# ---------------- drum + bay ----------------
drum_od, drum_w, drum_wall, drum_x = 95.0, 34.0, 3.0, 75.0
drum_overlap = 5.0
drum_cz = -(R_out + drum_od / 2 - drum_overlap)      # -73.5
cable_exit_d = 8.0
bay_screw_xs, bay_screw_y = (62.0, 88.0), 8.0        # M4s from inside the bore
# tunnels (front = TP4056/USB + Nano/perf, rear = LiPo + MT3608)
FT_X0, FT_X1 = 8.0, 54.0
RT_X0, RT_X1 = 96.0, 142.0
BAY_W, BAY_BOT = 64.0, -60.0
# corner duct linking tunnels past the drum (+Y top corner, outside the ring)
DUCT_Y0, DUCT_Y1, DUCT_Z0, DUCT_Z1 = 25.0, 32.0, -33.0, -25.0
# wire spine (hollow rib on the right shell side)
SP_X0, SP_X1 = 96.0, 112.0
SP_A0, SP_A1 = 60.0, 124.0           # degrees from +Z toward +Y
lipo_l, lipo_w, lipo_t = 34.5, 51.0, 11.0            # 103450 pouch + margin

# ---------------- hinge ----------------
hinge_od, hinge_hole = 8.0, 3.2
hinge_cz = -R_out - hinge_od / 2 + 2
hinge_right = [(6, 20), (34, 48), (102, 116), (130, 144)]
hinge_left = [(20, 34), (48, 58), (96, 102), (116, 130)]
hinge_gap, pin_depth = 0.4, 60.0

EPS = 0.01


# =====================================================================
# helpers
# =====================================================================
def rrect_sk(l, w, r):
    return cq.Sketch().rect(l, w).vertices().fillet(r)


def loft_rrect(l, w, z0, z1, r, d):
    """Rounded slab lofted from (l,w)@z0 to (l-2d, w-2d)@z1. Negative d grows."""
    s1 = rrect_sk(l, w, r)
    s2 = rrect_sk(l - 2 * d, w - 2 * d, max(r - d, 1.0))
    return (
        cq.Workplane("XY", origin=(0, 0, z0))
        .placeSketch(s1, s2.moved(cq.Location(cq.Vector(0, 0, z1 - z0))))
        .loft()
    )


def slab_rrect(l, w, z0, z1, r):
    return cq.Workplane("XY", origin=(0, 0, z0)).placeSketch(rrect_sk(l, w, r)).extrude(z1 - z0)


def tube_bore():
    return cq.Workplane("YZ", origin=(-6, 0, 0)).circle(R_in).extrude(shell_len + 12)


def outer_cyl(extra=0.0):
    return cq.Workplane("YZ", origin=(-6, 0, 0)).circle(R_out + extra).extrude(shell_len + 12)


def half_box(right=True):
    y = 100 if right else -100
    return cq.Workplane("XY", origin=(-60, y, 0)).box(shell_len + 130, 200, 620, centered=(False, True, True))


def wedge_yz(a0, a1, x0, x1, rad=200.0):
    """Angular wedge (degrees from +Z toward +Y) as a prism along X."""
    pts = [(0.0, 0.0)]
    steps = 6
    for i in range(steps + 1):
        a = math.radians(a0 + (a1 - a0) * i / steps)
        pts.append((rad * math.sin(a), rad * math.cos(a)))
    return cq.Workplane("YZ", origin=(x0, 0, 0)).polyline(pts).close().extrude(x1 - x0)


def knuckle_solids(spans):
    w = None
    for x0, x1 in spans:
        k = cq.Workplane("YZ", origin=(x0, 0, hinge_cz)).circle(hinge_od / 2).extrude(x1 - x0)
        w = k if w is None else w.union(k)
    return w


def knuckle_clear(spans):
    w = None
    for x0, x1 in spans:
        k = (
            cq.Workplane("YZ", origin=(x0 - hinge_gap, 0, hinge_cz))
            .circle(hinge_od / 2 + hinge_gap)
            .extrude(x1 - x0 + 2 * hinge_gap)
        )
        w = k if w is None else w.union(k)
    return w


def hinge_pin_channels():
    f = cq.Workplane("YZ", origin=(-1, 0, hinge_cz)).circle(hinge_hole / 2).extrude(pin_depth + 1)
    b = cq.Workplane("YZ", origin=(shell_len + 1, 0, hinge_cz)).circle(hinge_hole / 2).extrude(-(pin_depth + 1))
    pf = cq.Workplane("YZ", origin=(-1, 0, hinge_cz)).circle(3.1).extrude(4)
    pb = cq.Workplane("YZ", origin=(shell_len + 1, 0, hinge_cz)).circle(3.1).extrude(-4)
    return f.union(b).union(pf).union(pb)


def pod_form(g=0.0):
    return loft_rrect(pod_ox + 2 * g, pod_oy + 2 * g, belt_z0 - 2 * g, z_lid0 + 2 * g, r_pod + g, draft).translate(
        (POD_CX, 0, 0)
    )


def pod_interior():
    return loft_rrect(pod_ix, pod_iy, belt_z0 - 2, z_lid0 + 1, r_pod - 1, draft).translate((POD_CX, 0, 0)).cut(
        outer_cyl()
    )


def belt_form():
    b = slab_rrect(pod_ox + 2 * belt_t, belt_oy, belt_z0, belt_z1, r_belt).translate((POD_CX, 0, 0))
    try:
        b = b.faces("<Z").chamfer(edge * 2)
    except Exception:
        pass
    return b


def belt_groove():
    outer = slab_rrect(pod_ox + 2 * belt_t + 2, belt_oy + 2, belt_z1 - gap, belt_z1 + EPS, r_belt).translate((POD_CX, 0, 0))
    inner = slab_rrect(pod_ox + 2 * gap, pod_oy + 2 * gap, belt_z1 - gap - 1, belt_z1 + 1, r_pod + gap).translate((POD_CX, 0, 0))
    return outer.cut(inner)


def side_fairing():
    s1 = rrect_sk(pod_ox, pod_oy, r_pod)
    s2 = rrect_sk(pod_ox - 10, 40, r_pod)
    return (
        cq.Workplane("XY", origin=(POD_CX, 0, belt_z0))
        .placeSketch(s1, s2.moved(cq.Location(cq.Vector(0, 0, -(belt_z0 - 5)))))
        .loft()
    )


def spine_rib():
    band = outer_cyl(6).cut(outer_cyl()).intersect(wedge_yz(SP_A0, SP_A1, SP_X0, SP_X1))
    return band


def spine_void():
    v = outer_cyl(5).cut(outer_cyl(1.5)).intersect(wedge_yz(SP_A0 + 3, SP_A1 - 2, SP_X0 + 2, SP_X1 - 2))
    return v


def spine_feed_hole():
    """Slanted drill from the pod floor edge, through wall+belt, into the rib."""
    c = cq.Workplane("XY").circle(3.5).extrude(34)
    c = c.rotate((0, 0, 0), (1, 0, 0), -140)
    return c.translate((104, 19, 27))


def bay_envelope(grow=0.0):
    """Whole bay outer envelope (for the left shell's swing relief)."""
    ring = cq.Workplane("YZ", origin=(drum_x - drum_w / 2 - grow, 0, drum_cz)).circle(drum_od / 2 + grow).extrude(drum_w + 2 * grow)
    ft = loft_rrect(FT_X1 - FT_X0 + 2 * grow, BAY_W + 2 * grow, BAY_BOT - grow, -4, 8, -2).translate(((FT_X0 + FT_X1) / 2, 0, 0))
    rt = loft_rrect(RT_X1 - RT_X0 + 2 * grow, BAY_W + 2 * grow, BAY_BOT - grow, -4, 8, -2).translate(((RT_X0 + RT_X1) / 2, 0, 0))
    duct = cq.Workplane("XY", origin=((FT_X1 + RT_X0) / 2, (DUCT_Y0 + DUCT_Y1) / 2, (DUCT_Z0 + DUCT_Z1) / 2)).box(
        RT_X0 - FT_X1 + 12 + 2 * grow, DUCT_Y1 - DUCT_Y0 + 2 * grow, DUCT_Z1 - DUCT_Z0 + 2 * grow
    )
    sn = snout_solid(grow)
    return ring.union(ft).union(rt).union(duct).union(sn)


def snout_solid(grow=0.0):
    sn = cq.Workplane("XY").circle((cable_exit_d + 10) / 2 + grow).extrude(16 + grow)
    return sn.translate((drum_x, 0, drum_cz - drum_od / 2 - 4)).rotate((drum_x, 0, drum_cz), (drum_x + 1, 0, drum_cz), 30)


def snout_hole():
    h = cq.Workplane("XY").circle(cable_exit_d / 2).extrude(30)
    return h.translate((drum_x, 0, drum_cz - drum_od / 2 - 12)).rotate((drum_x, 0, drum_cz), (drum_x + 1, 0, drum_cz), 30)


def pad_boss(cx, cy):
    b = cq.Workplane("XY", origin=(cx, cy, 10)).box(PAD, PAD, PAD_Z - 10, centered=(True, True, False))
    return b.cut(cq.Workplane("XY", origin=(cx, cy, PAD_Z - 9)).circle(PAD_PILOT / 2).extrude(10))


# =====================================================================
# PARTS
# =====================================================================
def build_shell_right():
    base = outer_cyl().cut(tube_bore()).intersect(half_box(True))
    body = base.union(pod_form()).union(side_fairing().intersect(half_box(True)))
    body = body.union(belt_form().intersect(half_box(True)))
    body = body.union(spine_rib())
    body = body.union(knuckle_solids(hinge_right))
    body = body.cut(pod_interior()).cut(belt_groove())
    body = body.cut(spine_void()).cut(spine_feed_hole())
    # closure: lip ledge + pad pocket
    body = body.cut(
        cq.Workplane("XY", origin=(POD_CX, -pod_oy / 2, belt_z1 - 1.25)).box(pod_ox - 30, 3, 2.5 + clr, centered=(True, True, True))
    )
    ppw = belt_oy / 2 + 1 - abs(bore_y) + pad_w / 2 + clr
    body = body.cut(
        cq.Workplane("XY", origin=(bore_x, -belt_oy / 2 - 1 + ppw / 2, z_crown - 2 - clr)).box(
            pad_l + 2 * clr, ppw, pad_h + 2 * clr, centered=(True, True, False)
        )
    )
    body = body.cut(knuckle_clear(hinge_left)).cut(hinge_pin_channels())
    # bay mounting: M4 through-holes from inside the bore, counterbored flush
    for sx in bay_screw_xs:
        for sy in (bay_screw_y, -bay_screw_y):
            zs = -math.sqrt(max(R_in * R_in - sy * sy, 0))
            body = body.cut(cq.Workplane("XY", origin=(sx, sy, zs + 1)).circle(2.2).extrude(-(shell_wall + 4)))
            body = body.cut(cq.Workplane("XY", origin=(sx, sy, zs + 1)).circle(4.0).extrude(-2.6))
    # latch boss (integral)
    boss = cq.Workplane("XY", origin=(bore_x, bore_y, 0)).circle(boss_d / 2).extrude(z_lid0)
    for a in (45, 135, 225, 315):
        g = cq.Workplane("XY", origin=(bore_x, bore_y, 0)).box(boss_d / 2 + 5, 2.5, 20, centered=(False, True, False)).rotate(
            (bore_x, bore_y, 0), (bore_x, bore_y, 1), a
        )
        boss = boss.union(g)
    boss = boss.cut(tube_bore())
    boss = boss.cut(cq.Workplane("XY", origin=(bore_x, bore_y, z_lidtop - bore_depth)).circle(bore_d / 2).extrude(bore_depth + 2))
    boss = boss.cut(cq.Workplane("XY", origin=(bore_x, bore_y, -R_out)).circle(closure_screw_d / 2).extrude(z_lid0 + 2))
    boss = boss.cut(cq.Workplane("YZ", origin=(bore_x - 1, bore_y, pin_z)).circle(pin_ch_d / 2).extrude(boss_d + 2))
    body = body.union(boss)
    for (px, py) in pads_pedestal:
        body = body.union(pad_boss(px, py))
    body = body.cut(tube_bore())
    return body


def build_shell_left():
    base = outer_cyl().cut(tube_bore()).intersect(half_box(False))
    skirt = belt_form().intersect(half_box(False)).cut(pod_form(clr))
    fair = side_fairing().intersect(half_box(False)).cut(pod_form(clr))
    lip = cq.Workplane("XY", origin=(POD_CX, -pod_oy / 2 - 1.5 + (3 - clr) / 2 + clr, belt_z1 - 1.25 - clr)).box(
        pod_ox - 30 - 2 * clr, 3 - clr, 2.5 - clr, centered=(True, True, True)
    )
    spad = cq.Workplane("XY", origin=(bore_x, bore_y, z_crown - 2)).box(pad_l, pad_w, pad_h, centered=(True, True, False))
    strut_w = belt_oy / 2 - abs(bore_y) + pad_w / 2 - 1
    strut = cq.Workplane("XY", origin=(bore_x, -belt_oy / 2 + 1 + strut_w / 2, z_crown - 2)).box(
        pad_l, strut_w, 4, centered=(True, True, False)
    )
    body = base.union(skirt).union(fair).union(lip).union(spad).union(strut).union(knuckle_solids(hinge_left))
    body = body.cut(cq.Workplane("XY", origin=(bore_x, bore_y, z_crown - 3)).circle(2.8).extrude(pad_h + 6))
    body = body.cut(belt_groove())
    body = body.cut(bay_envelope(0.8))
    body = body.cut(knuckle_clear(hinge_right)).cut(hinge_pin_channels())
    body = body.cut(tube_bore()).intersect(half_box(False))
    return body


def build_bay_module():
    ring = cq.Workplane("YZ", origin=(drum_x - drum_w / 2, 0, drum_cz)).circle(drum_od / 2).extrude(drum_w)
    ring = ring.cut(
        cq.Workplane("YZ", origin=(drum_x - drum_w / 2 + drum_wall, 0, drum_cz)).circle(drum_od / 2 - drum_wall).extrude(drum_w)
    )
    ring = ring.cut(cq.Workplane("YZ", origin=(drum_x + drum_w / 2 - 3, 0, drum_cz)).circle(drum_od / 2 - 1).extrude(3.2))
    # tunnels
    ft = loft_rrect(FT_X1 - FT_X0, BAY_W, BAY_BOT, -4, 8, -2).translate(((FT_X0 + FT_X1) / 2, 0, 0))
    rt = loft_rrect(RT_X1 - RT_X0, BAY_W, BAY_BOT, -4, 8, -2).translate(((RT_X0 + RT_X1) / 2, 0, 0))
    ft_cav = loft_rrect(FT_X1 - FT_X0 - 6, BAY_W - 6, BAY_BOT + 3, 0, 6, -2).translate(((FT_X0 + FT_X1) / 2, 0, 0))
    rt_cav = loft_rrect(RT_X1 - RT_X0 - 6, BAY_W - 6, BAY_BOT + 3, 0, 6, -2).translate(((RT_X0 + RT_X1) / 2, 0, 0))
    # corner duct
    duct = cq.Workplane("XY", origin=((FT_X1 + RT_X0) / 2, (DUCT_Y0 + DUCT_Y1) / 2, (DUCT_Z0 + DUCT_Z1) / 2)).box(
        RT_X0 - FT_X1 + 12, DUCT_Y1 - DUCT_Y0, DUCT_Z1 - DUCT_Z0
    )
    duct_v = cq.Workplane("XY", origin=((FT_X1 + RT_X0) / 2, (DUCT_Y0 + DUCT_Y1) / 2, (DUCT_Z0 + DUCT_Z1) / 2)).box(
        RT_X0 - FT_X1 + 16, DUCT_Y1 - DUCT_Y0 - 3, DUCT_Z1 - DUCT_Z0 - 3
    )
    # seat plate + M4 bosses under the shell
    seat = cq.Workplane("XY", origin=(drum_x, 0, -34)).box(42, 40, 8, centered=(True, True, False))
    body = ring.union(ft).union(rt).union(duct).union(seat).union(snout_solid())
    for sx in bay_screw_xs:
        for sy in (bay_screw_y, -bay_screw_y):
            zs = -math.sqrt(max(R_out * R_out - sy * sy, 0))
            b = cq.Workplane("XY", origin=(sx, sy, zs + 2)).circle(4.5).extrude(-12)
            body = body.union(b)
            body = body.cut(cq.Workplane("XY", origin=(sx, sy, zs)).circle(1.7).extrude(-12))
    body = body.cut(ft_cav).cut(rt_cav).cut(duct_v).cut(snout_hole())
    # spine landing window (rear tunnel, +Y upper wall)
    body = body.cut(cq.Workplane("XY", origin=(104, 30, -17)).box(12, 10, 8))
    # front wall: TP4056 slot block + USB-C port + niche
    blk = cq.Workplane("XY", origin=(16.5, 20, BAY_BOT + 3)).box(9, 17, 21, centered=(True, True, False))
    blk = blk.cut(cq.Workplane("XY", origin=(16.5, 20, BAY_BOT + 5)).box(4.9, 18, 22, centered=(True, True, False)))
    body = body.union(blk)
    body = body.cut(cq.Workplane("XY", origin=(FT_X0 - 2, 20, -49)).box(12, 10.2, 4.6, centered=(True, True, True)))
    body = body.cut(cq.Workplane("XY", origin=(FT_X0 - 1.2, 20, -49)).box(4, 15, 10, centered=(True, True, True)))
    # rear tunnel: LiPo retaining frame (103450 flat on the floor)
    fr = cq.Workplane("XY", origin=((RT_X0 + RT_X1) / 2, 0, BAY_BOT + 3)).box(lipo_l + 4, lipo_w + 4, 5, centered=(True, True, False))
    fr = fr.cut(cq.Workplane("XY", origin=((RT_X0 + RT_X1) / 2, 0, BAY_BOT + 3)).box(lipo_l, lipo_w, 6, centered=(True, True, False)))
    body = body.union(fr)
    # zip-anchor grids in both tunnel floors
    for cx0, cx1 in ((FT_X0 + 8, FT_X1 - 8), (RT_X0 + 8, RT_X1 - 8)):
        x = cx0
        while x <= cx1:
            for y in (-20, 0, 20):
                body = body.cut(cq.Workplane("XY", origin=(x, y, BAY_BOT - 1)).circle(1.6).extrude(6))
            x += 12
    # hatch pilots (shared hatch part, printed twice)
    for cx in ((FT_X0 + FT_X1) / 2, (RT_X0 + RT_X1) / 2):
        for dx in (-17, 17):
            for dy in (-26, 26):
                body = body.cut(cq.Workplane("XY", origin=(cx + dx, dy, BAY_BOT - 1)).circle(1.3).extrude(9))
    body = body.cut(outer_cyl(0.3))
    body = body.cut(tube_bore())
    return body


def build_bay_hatch():
    """Bottom cover plate; same part fits front and rear tunnels."""
    p = slab_rrect(FT_X1 - FT_X0, BAY_W, 0, 2.5, 8).translate(((FT_X1 - FT_X0) / 2, 0, 0))
    for dx in (-17, 17):
        for dy in (-26, 26):
            cx = (FT_X1 - FT_X0) / 2
            p = p.cut(cq.Workplane("XY", origin=(cx + dx, dy, -1)).circle(1.7).extrude(5))
            p = p.cut(cq.Workplane("XY", origin=(cx + dx, dy, 1.3)).circle(3.1).extrude(2))
    return p


def build_pedestal_cart():
    base_y = bore_y
    cx = sum(p[0] for p in pads_pedestal) / 2
    base = cq.Workplane("XY", origin=(cx, base_y, PAD_Z)).box(44, 24, 3, centered=(True, True, False))
    for px, py in pads_pedestal:
        base = base.cut(cq.Workplane("XY", origin=(px, py, PAD_Z - 1)).circle(1.7).extrude(6))
    tower = cq.Workplane("XY", origin=(66 + sol_len / 2, base_y, PAD_Z + 3)).box(
        sol_len + 6, sol_w + 6, max(ped_top - PAD_Z - 3, 2), centered=(True, True, False)
    )
    body = base.union(tower)
    for dx in (sol_len / 2 - sol_hole_dx / 2, sol_len / 2 + sol_hole_dx / 2):
        body = body.cut(cq.Workplane("XY", origin=(66 + dx, base_y, ped_top - 12)).circle(sol_hole_d / 2).extrude(13))
    return body


def build_lid():
    top = loft_rrect(pod_ox - 2 * draft, pod_oy - 2 * draft, 0, lid_t, max(r_pod - draft, 2), edge).translate((POD_CX, 0, 0))
    ring = cq.Workplane("XY", origin=(nfc_cx, 0, lid_t)).circle(17).extrude(0.6)
    ring = ring.cut(cq.Workplane("XY", origin=(nfc_cx, 0, lid_t - 1)).circle(14).extrude(3))
    body = top.union(ring)
    body = body.cut(
        cq.Workplane("XY", origin=(pn532_x + pn532_l / 2, 0, -EPS)).box(pn532_l, pn532_w, lid_t - window_remain, centered=(True, True, False))
    )
    for sx in (-1, 1):
        for sy in (-1, 1):
            px = pn532_x + pn532_l / 2 + sx * pn532_hole_dx / 2
            py = sy * pn532_hole_dy / 2
            post = cq.Workplane("XY", origin=(px, py, -6.0)).circle(2.5).extrude(6.0 - (lid_t - window_remain) + lid_t)
            post = post.cut(cq.Workplane("XY", origin=(px, py, -6.5)).circle(1.1).extrude(6))
            body = body.union(post)
    body = body.cut(cq.Workplane("XY", origin=(bore_x, bore_y, -1)).circle((bore_d + 0.6) / 2).extrude(lid_t + 4))
    body = body.cut(cq.Workplane("XY", origin=(button_x, button_y, lid_t - 1)).circle(9.5).extrude(3))
    body = body.cut(cq.Workplane("XY", origin=(button_x, button_y, -1)).circle(button_d / 2).extrude(lid_t + 2))
    body = body.cut(cq.Workplane("XY", origin=(button_x, -5, lid_t - 0.8)).box(8, 12, 3, centered=(True, True, False)))
    for ly in (-2, -8):
        body = body.cut(cq.Workplane("XY", origin=(button_x, ly, -1)).circle(led_d / 2).extrude(lid_t + 2))
    for cx in (5, pod_ix - 5):
        for cy in (-pod_iy / 2 + 5, pod_iy / 2 - 5):
            body = body.cut(cq.Workplane("XY", origin=(cx, cy, -1)).circle(1.7).extrude(lid_t + 2))
            body = body.cut(cq.Workplane("XY", origin=(cx, cy, lid_t - 1.6)).circle(3.1).extrude(2))
    return body


def _liner_sketch(R_hi, n, fh, ft):
    sk = cq.Sketch().circle(R_hi).circle(R_hi - liner_base, mode="s")
    for i in range(n):
        ang = math.radians(i * 360.0 / n)
        lean = math.radians(180 - fin_lean)
        r0 = R_hi - liner_base
        cx, cy = r0 * math.cos(ang), r0 * math.sin(ang)
        ux, uy = math.cos(ang + lean), math.sin(ang + lean)
        vx, vy = -math.sin(ang + lean), math.cos(ang + lean)
        quad = [
            (cx, cy),
            (cx + fh * ux, cy + fh * uy),
            (cx + fh * ux + ft * vx, cy + fh * uy + ft * vy),
            (cx + ft * vx, cy + ft * vy),
        ]
        sk = sk.polygon(quad, mode="a")
    return sk


def build_liner(right=True):
    sk = _liner_sketch(R_in - 0.15, fin_n, fin_h + liner_base, fin_t)
    solid = cq.Workplane("YZ", origin=(0, 0, 0)).placeSketch(sk).extrude(shell_len)
    return solid.intersect(half_box(right))


def build_shim():
    sk = _liner_sketch(15.0, 12, 7.0, 1.2)
    solid = cq.Workplane("YZ").placeSketch(sk).extrude(shell_len)
    wedge = cq.Workplane("YZ", origin=(-1, 0, 0)).polyline([(0, 0), (40, -23), (40, 23)]).close().extrude(shell_len + 2)
    return solid.cut(wedge)


def build_spool_cover():
    d = drum_od - 2 - 0.4
    b = cq.Workplane("XY").circle(d / 2).extrude(3)
    b = b.union(cq.Workplane("XY").circle(11).extrude(4.2))
    for a in (30, 150, 270):
        r = drum_od / 2 - drum_wall / 2 - 2.5
        b = b.cut(cq.Workplane("XY", origin=(r * math.cos(math.radians(a)), r * math.sin(math.radians(a)), -1)).circle(1.7).extrude(6))
    b = b.cut(cq.Workplane("XY", origin=(0, 0, -1)).circle(6).extrude(7))
    b = b.cut(cq.Workplane("XY", origin=(drum_cz, 0, -1)).circle(R_in + 0.4).extrude(7))
    return b


def build_end_plug():
    p = cq.Workplane("XY").circle(3.0).extrude(4)
    return p.union(cq.Workplane("XY", origin=(0, 0, 4)).circle(4.0).extrude(1.2))


PARTS = {
    "shell_right": build_shell_right,
    "shell_left": build_shell_left,
    "bay_module": build_bay_module,
    "bay_hatch": build_bay_hatch,
    "pedestal_cart": build_pedestal_cart,
    "lid": build_lid,
    "liner_right": lambda: build_liner(True),
    "liner_left": lambda: build_liner(False),
    "shim": build_shim,
    "spool_cover": build_spool_cover,
    "end_plug": build_end_plug,
}


def main():
    import os

    names = sys.argv[1:] or list(PARTS.keys())
    os.makedirs("step", exist_ok=True)
    os.makedirs("stl", exist_ok=True)
    for n in names:
        print(f"[build] {n} ...", flush=True)
        s = PARTS[n]()
        cq.exporters.export(s, f"step/{n}.step")
        cq.exporters.export(s, f"stl/{n}.stl", tolerance=0.05, angularTolerance=0.2)
        print(f"[ok]    {n}", flush=True)


if __name__ == "__main__":
    main()
