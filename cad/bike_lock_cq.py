#!/usr/bin/env python3
"""
RFID Bike Lock - parametric housing v0.5 "spine + door" (CadQuery / STEP)
==========================================================================
Consumer-install architecture. v0.4 (archived in cad/archive/v0.4/) could
not actually be installed: the pod overhung the seam and the full-width
bay blocked both the door swing and the tube entry path. v0.5 rules:

  1. ENTRY CORRIDOR: the tube slides in from the left (-Y) at axis height.
     No fixed material may exist in the corridor slab (y<0, |z|<24.5).
     The pod therefore becomes asymmetric (left wall stands high on the
     crown at y=-17); the belt band and left fairing are deleted.
  2. DOOR SWING: the door is a light arc panel (left half-shell + its TPU
     liner + closure flange). Everything else - pod, bay, drum - lives at
     y >= +4, outside the door's swept annulus. Nothing to hit.
  3. SLIM DRUM: spool axis turns 90 deg (along Y): a 068x32 wheel tucked
     low-right, cable 1.2 m x 04 (was 1.5 m). Lock bottom rises from
     z=-121 to about -94. Spool cover sits on the outboard (+Y) face -
     serviceable in place.

  Consumer flow: swing door open, press onto down tube, swing shut,
  ONE hidden M4 down the latch bore. Done.

  The exporter runs an ENTRY-CORRIDOR interference check on every build;
  `python bike_lock_cq.py --sweep` additionally rotates the door through
  0..110 deg and asserts the swept volume misses body+bay+lid.

Usage:  python bike_lock_cq.py [part ...]   ->  step/<part>.step + stl/<part>.stl
        python bike_lock_cq.py --sweep      ->  kinematic verification only
"""
import math
import sys
import cadquery as cq

# ---------------- core ----------------
shell_id, shell_wall, shell_len = 54.0, 4.0, 150.0
R_in, R_out = shell_id / 2, shell_id / 2 + shell_wall

# ---------------- slim asymmetric pod ----------------
pod_ix, pod_wall, pod_h, lid_t = 120.0, 3.0, 22.0, 3.0
pod_y0, pod_y1 = -17.0, 31.0        # outer walls; left wall stands high on the crown
pod_oy = pod_y1 - pod_y0            # 48
pod_yc = (pod_y0 + pod_y1) / 2      # +7
pod_iy = pod_oy - 2 * pod_wall      # 42
z_crown = R_out                     # 31
z_lid0 = z_crown + pod_h            # 53
z_lidtop = z_lid0 + lid_t           # 56
pod_ox = pod_ix + 2 * pod_wall
draft, r_pod, edge = 1.5, 10.0, 1.2
POD_CX = 60.0                       # pod spans x -3..123
clr = 0.5                           # closure engagement clearance (TODO tune)

# ---------------- entry corridor (rule 1) ----------------
COR_Z = 23.5                        # half-height of the tube entry capsule (max tube 046 -> +/-23, +0.5)

# ---------------- latch (plunger-as-pin) ----------------
bore_d, bore_depth, bore_x = 11.0, 26.0, 58.0
bore_y = 10.0                       # boss/pads live on the BODY side of the seam - the pod's
                                    # left floor is the closed door itself; nothing may stand there
boss_d = bore_d + 8
plunger_d = 6.0
pin_ch_d = plunger_d + 0.6
head_seat = 11.5
pin_z = z_lidtop - head_seat        # 44.5
closure_screw_d = 4.4
sol_len, sol_w, sol_h = 30.0, 13.4, 15.0     # VERIFY
sol_axis_h = 7.5                    # VERIFY
sol_hole_dx, sol_hole_d = 24.0, 2.2  # VERIFY
ped_top = pin_z - sol_axis_h        # 37

PAD_Z, PAD, PAD_PILOT = 32.0, 12.0, 2.6
pads_pedestal = [(68, bore_y), (94, bore_y)]

# ---------------- door closure flange + lip ----------------
fl_x0, fl_x1 = 46.0, 70.0           # flange under the bore
fl_z0, fl_z1 = 25.2, 28.2
fl_y1 = 16.0                        # flange reaches under the bore at y=10
lip_x0, lip_x1 = 8.0, 116.0         # lip ridge along the pod's left wall

# ---------------- lid ----------------
pn532_l, pn532_w, pn532_x = 43.2, 41.0, 2.0          # VERIFY
window_remain, nfc_cx = 1.2, 23.6
button_d, button_x, button_y = 12.4, 106.0, 16.0     # VERIFY
led_d = 3.3

# ---------------- liner ----------------
fin_n, fin_h, fin_t, fin_lean, liner_base = 24, 12.0, 1.4, 30.0, 2.0

# ---------------- bay (rule 2: everything at y >= BAY_Y0) ----------------
BAY_Y0, BAY_Y1 = 7.0, 48.0          # left face clears the door knuckles (loft top grows 2)
BK_X0, BK_X1, BK_BOT = 4.0, 62.0, -58.0
lipo_l, lipo_w, lipo_t = 51.0, 35.0, 11.0            # 103450 + margin, long side along X
usb_z = -46.0
bay_screw_y = 12.11                 # .11/.13 nudges break an exactly-tangent OCC edge that crashed STEP export
bay_screw_xs = (10.13, 28.13, 46.13, 60.13)          # M4s from inside the bore, +Y line

# ---------------- drum (rule 3: axis along Y, slim wheel) ----------------
drum_od, drum_w, drum_wall = 68.0, 32.0, 3.5         # 1.2 m x 04 coated cable
drum_cx = 98.0
drum_cz = -(R_out + drum_od / 2 - 5.0)               # -60
DR_Y0 = BAY_Y0                       # ring spans y 4..36
DR_Y1 = BAY_Y0 + drum_w
cable_exit_d = 7.0

# ---------------- wire spine (over the brick) ----------------
SP_X0, SP_X1 = 20.0, 36.0
SP_A0, SP_A1 = 60.0, 124.0          # degrees from +Z toward +Y

# ---------------- hinge ----------------
hinge_od, hinge_hole = 8.0, 3.2
hinge_cz = -R_out - hinge_od / 2 + 2                 # -33
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
    s1 = rrect_sk(l, w, r)
    s2 = rrect_sk(l - 2 * d, w - 2 * d, max(r - d, 1.0))
    return (
        cq.Workplane("XY", origin=(0, 0, z0))
        .placeSketch(s1, s2.moved(cq.Location(cq.Vector(0, 0, z1 - z0))))
        .loft()
    )


def tube_bore():
    return cq.Workplane("YZ", origin=(-6, 0, 0)).circle(R_in).extrude(shell_len + 12)


def outer_cyl(extra=0.0):
    return cq.Workplane("YZ", origin=(-6, 0, 0)).circle(R_out + extra).extrude(shell_len + 12)


def half_box(right=True):
    y = 100 if right else -100
    return cq.Workplane("XY", origin=(-60, y, 0)).box(shell_len + 130, 200, 620, centered=(False, True, True))


def wedge_yz(a0, a1, x0, x1, rad=200.0):
    pts = [(0.0, 0.0)]
    for i in range(7):
        a = math.radians(a0 + (a1 - a0) * i / 6)
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
    pf = cq.Workplane("YZ", origin=(-1, 0, hinge_cz)).circle(3.1).extrude(6.4)
    pb = cq.Workplane("YZ", origin=(shell_len + 1, 0, hinge_cz)).circle(3.1).extrude(-6.4)
    rf = cq.Workplane("YZ", origin=(-1, 0, hinge_cz)).circle(4.2).extrude(2.4)
    rb = cq.Workplane("YZ", origin=(shell_len + 1, 0, hinge_cz)).circle(4.2).extrude(-2.4)
    return f.union(b).union(pf).union(pb).union(rf).union(rb)


def rot_about_hinge(shape_wp, deg):
    """Rotate a Workplane's solid about the hinge axis (X line through y=0, z=hinge_cz)."""
    s = shape_wp.val()
    return cq.Workplane(obj=s.rotate(cq.Vector(0, 0, hinge_cz), cq.Vector(1, 0, hinge_cz), deg))


def pod_form(g=0.0):
    return loft_rrect(pod_ox + 2 * g, pod_oy + 2 * g, 14 - 2 * g, z_lid0 + 2 * g, r_pod + g, draft).translate(
        (POD_CX, pod_yc, 0)
    )


def pod_interior():
    return loft_rrect(pod_ix, pod_iy, 12, z_lid0 + 1, r_pod - 1, draft).translate((POD_CX, pod_yc, 0)).cut(outer_cyl())


def side_fairing_right():
    s1 = rrect_sk(pod_ox, pod_oy, r_pod)
    s2 = rrect_sk(pod_ox - 10, pod_oy - 12, r_pod)
    f = (
        cq.Workplane("XY", origin=(POD_CX, pod_yc, 14))
        .placeSketch(s1, s2.moved(cq.Location(cq.Vector(0, 3, -9))))
        .loft()
    )
    return f.intersect(half_box(True))  # rule 1: no fairing on the entry side


def spine_rib():
    return outer_cyl(6).cut(outer_cyl()).intersect(wedge_yz(SP_A0, SP_A1, SP_X0, SP_X1))


def spine_void():
    return outer_cyl(5).cut(outer_cyl(1.5)).intersect(wedge_yz(SP_A0 + 3, SP_A1 - 2, SP_X0 + 2, SP_X1 - 2))


def spine_feed_hole():
    c = cq.Workplane("XY").circle(3.5).extrude(34)
    c = c.rotate((0, 0, 0), (1, 0, 0), -140)
    return c.translate((28, 19, 27))


# ---- door closure features (defined once; body cuts use their swept form)
def door_flange():
    f = cq.Workplane("XY", origin=((fl_x0 + fl_x1) / 2, (fl_y1 - 18) / 2, fl_z0)).box(
        fl_x1 - fl_x0, fl_y1 + 18, fl_z1 - fl_z0, centered=(True, True, False)
    )
    return f.cut(cq.Workplane("XY", origin=(bore_x, bore_y, fl_z0 - 1)).circle(2.8).extrude(6))  # M4 insert pocket


def door_lip():
    wall = cq.Workplane("XY", origin=((lip_x0 + lip_x1) / 2, -16.9, 26)).box(lip_x1 - lip_x0, 1.8, 8, centered=(True, True, False))
    nose = cq.Workplane("XY", origin=((lip_x0 + lip_x1) / 2, -15.1, 31.8)).box(lip_x1 - lip_x0, 1.8, 2, centered=(True, True, False))
    return wall.union(nose)


def sector_prism(y0, y1, z0, z1, x0, x1, extra_deg=30.0):
    """EXACT swept volume of a box rotated 0..extra_deg about the hinge axis:
    an annular sector prism (clean surfaces - no scalloped unions)."""
    zr0, zr1 = z0 - hinge_cz, z1 - hinge_cz
    corners = [(y0, zr0), (y0, zr1), (y1, zr0), (y1, zr1)]
    rs = [math.hypot(cy, cz) for cy, cz in corners]
    r_max = max(rs)
    r_min = zr0 if y0 < 0 < y1 else min(rs)
    # angle from +Z toward -Y (opening direction), per corner
    phis = [math.degrees(math.atan2(-cy, cz)) for cy, cz in corners]
    a0, a1 = min(phis), max(phis) + extra_deg
    pts = []
    steps = 24
    for i in range(steps + 1):
        a = math.radians(a0 + (a1 - a0) * i / steps)
        pts.append((-r_max * math.sin(a), r_max * math.cos(a) + hinge_cz))
    for i in range(steps + 1):
        a = math.radians(a1 - (a1 - a0) * i / steps)
        pts.append((-r_min * math.sin(a), r_min * math.cos(a) + hinge_cz))
    return cq.Workplane("YZ", origin=(x0, 0, 0)).polyline(pts).close().extrude(x1 - x0)


def closure_sweep_cut():
    """Body pockets that admit the door's flange+lip through the closing arc."""
    g = clr
    flange = sector_prism(-18 - g, fl_y1 + g, fl_z0 - g, fl_z1 + g, fl_x0 - g, fl_x1 + g)
    lipw = sector_prism(-17.8 - g, -16 + g, 26 - g, 34 + g, lip_x0 - g, lip_x1 + g)
    nose = sector_prism(-16 - g, -14.2 + g, 31.8 - g, 33.8 + g, lip_x0 - g, lip_x1 + g)
    return flange.union(lipw).union(nose)


def drum_ring():
    ring = cq.Workplane("XZ", origin=(drum_cx, DR_Y0, drum_cz)).circle(drum_od / 2).extrude(-drum_w)
    ring = ring.cut(
        cq.Workplane("XZ", origin=(drum_cx, DR_Y0 + drum_wall, drum_cz)).circle(drum_od / 2 - drum_wall).extrude(-drum_w)
    )
    return ring


def snout_solid(grow=0.0):
    sn = cq.Workplane("XY").circle((cable_exit_d + 9) / 2 + grow).extrude(15 + grow)
    return sn.translate((drum_cx + 14, (DR_Y0 + DR_Y1) / 2, drum_cz - drum_od / 2 - 3)).rotate(
        (drum_cx, (DR_Y0 + DR_Y1) / 2, drum_cz), (drum_cx, (DR_Y0 + DR_Y1) / 2 + 1, drum_cz), -35
    )


def snout_hole():
    h = cq.Workplane("XY").circle(cable_exit_d / 2).extrude(28)
    return h.translate((drum_cx + 14, (DR_Y0 + DR_Y1) / 2, drum_cz - drum_od / 2 - 10)).rotate(
        (drum_cx, (DR_Y0 + DR_Y1) / 2, drum_cz), (drum_cx, (DR_Y0 + DR_Y1) / 2 + 1, drum_cz), -35
    )


def bay_envelope(grow=0.0):
    brick = cq.Workplane("XY", origin=((BK_X0 + BK_X1) / 2, (BAY_Y0 + BAY_Y1) / 2, (BK_BOT - grow + 0) / 2)).box(
        BK_X1 - BK_X0 + 2 * grow, BAY_Y1 - BAY_Y0 + 2 * grow, -BK_BOT + grow, centered=(True, True, True)
    )
    ring = cq.Workplane("XZ", origin=(drum_cx, DR_Y0 - grow, drum_cz)).circle(drum_od / 2 + grow).extrude(-(drum_w + 2 * grow))
    return brick.union(ring).union(snout_solid(grow))


def pad_boss(cx, cy):
    b = cq.Workplane("XY", origin=(cx, cy, 10)).box(PAD, PAD, PAD_Z - 10, centered=(True, True, False))
    return b.cut(cq.Workplane("XY", origin=(cx, cy, PAD_Z - 9)).circle(PAD_PILOT / 2).extrude(10))


def largest_solid(wp):
    sol = wp.solids().vals()
    if len(sol) <= 1:
        return wp
    best = max(sol, key=lambda x: x.Volume())
    return cq.Workplane(obj=best)


# =====================================================================
# PARTS
# =====================================================================
def build_body():
    base = outer_cyl().cut(tube_bore()).intersect(half_box(True))
    # pod: left fringe relieved by a FLAT plane at z=31.6 - the door's top edge
    # rises radially as it swings about the offset hinge (reaches r~33.8 while
    # still under the fringe), so a cylindrical relief is not enough.
    fringe_cut = cq.Workplane("XY", origin=(75, -30, (31.6 - 60) / 2)).box(180, 60, 31.6 + 60, centered=(True, True, True))
    pod = pod_form().cut(fringe_cut)
    body = base.union(pod).union(side_fairing_right())
    body = body.union(spine_rib()).union(knuckle_solids(hinge_right))
    body = body.cut(pod_interior())
    body = body.cut(spine_void()).cut(spine_feed_hole())
    body = body.cut(knuckle_clear(hinge_left)).cut(hinge_pin_channels())
    # bay mounting: M4 through-holes from inside the bore, counterbored flush
    zs = -math.sqrt(R_in * R_in - bay_screw_y ** 2)
    for sx in bay_screw_xs:
        body = body.cut(cq.Workplane("XY", origin=(sx, bay_screw_y, zs + 1.07)).circle(2.2).extrude(-(shell_wall + 5)))
        body = body.cut(cq.Workplane("XY", origin=(sx, bay_screw_y, zs + 1.07)).circle(4.0).extrude(-2.6))
    # spine landing window into the bay brick
    body = body.cut(cq.Workplane("XY", origin=(28, 30, -18)).box(12, 12, 10))
    # latch boss (integral: the lock's load path)
    boss = cq.Workplane("XY", origin=(bore_x, bore_y, 0)).circle(boss_d / 2).extrude(z_lid0)
    for a in (45, 135, 225, 315):
        g = cq.Workplane("XY", origin=(bore_x, bore_y, 0)).box(boss_d / 2 + 5, 2.5, 18, centered=(False, True, False)).rotate(
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
    body = body.cut(closure_sweep_cut())              # admits the door's flange+lip (after boss!)
    body = body.cut(tube_bore())
    body = body.intersect(cq.Workplane("XY", origin=(shell_len / 2, 0, 0)).box(shell_len, 400, 700, centered=(True, True, True)))
    return largest_solid(body)


def build_door():
    arc = outer_cyl().cut(tube_bore()).intersect(half_box(False))
    door = arc.union(door_flange()).union(door_lip()).union(knuckle_solids(hinge_left))
    door = door.cut(knuckle_clear(hinge_right)).cut(hinge_pin_channels())
    door = door.cut(tube_bore())
    door = door.intersect(cq.Workplane("XY", origin=(shell_len / 2, 0, 0)).box(shell_len, 400, 700, centered=(True, True, True)))
    return largest_solid(door)


def build_bay_module():
    brick = loft_rrect(BK_X1 - BK_X0, BAY_Y1 - BAY_Y0, BK_BOT, -4, 8, -2).translate(
        ((BK_X0 + BK_X1) / 2, (BAY_Y0 + BAY_Y1) / 2, 0)
    )
    cav = loft_rrect(BK_X1 - BK_X0 - 6, BAY_Y1 - BAY_Y0 - 6, BK_BOT + 3, 0, 6, -2).translate(
        ((BK_X0 + BK_X1) / 2, (BAY_Y0 + BAY_Y1) / 2, 0)
    )
    web = cq.Workplane("XY", origin=(64, (DR_Y0 + DR_Y1) / 2, -44)).box(12, DR_Y1 - DR_Y0, 28, centered=(True, True, True))
    body = brick.union(drum_ring()).union(web).union(snout_solid())
    # M4 bosses under the through-bore screws (brick zone)
    zs2 = -math.sqrt(R_out * R_out - bay_screw_y ** 2)
    for sx in bay_screw_xs:
        b = cq.Workplane("XY", origin=(sx, bay_screw_y, zs2 + 2)).circle(4.5).extrude(-12)
        body = body.union(b)
    body = body.cut(cav).cut(snout_hole())
    # cover rabbet on the outboard (+Y) face - cut AFTER all unions so the web is trimmed too
    body = body.cut(cq.Workplane("XZ", origin=(drum_cx, DR_Y1 - 3, drum_cz)).circle(drum_od / 2 - 1).extrude(-3.3))
    for sx in bay_screw_xs:
        body = body.cut(cq.Workplane("XY", origin=(sx, bay_screw_y, zs2)).circle(1.7).extrude(-12))
    # spine landing window (brick top, +Y side)
    body = body.cut(cq.Workplane("XY", origin=(28, 30, -18)).box(12, 12, 10))
    # TP4056 slot block at the front wall + USB-C port + niche
    blk = cq.Workplane("XY", origin=(BK_X0 + 8.5, 24, BK_BOT + 3)).box(9, 20, 20, centered=(True, True, False))
    blk = blk.cut(cq.Workplane("XY", origin=(BK_X0 + 8.5, 24, BK_BOT + 5)).box(4.9, 18, 21, centered=(True, True, False)))
    body = body.union(blk)
    body = body.cut(cq.Workplane("XY", origin=(BK_X0 - 1, 24, usb_z)).box(10, 10.2, 4.6, centered=(True, True, True)))
    body = body.cut(cq.Workplane("XY", origin=(BK_X0 - 0.5, 24, usb_z)).box(3, 15, 10, centered=(True, True, True)))
    # LiPo retaining frame (flat on the floor, long side along X)
    fr = cq.Workplane("XY", origin=((BK_X0 + BK_X1) / 2, (BAY_Y0 + BAY_Y1) / 2, BK_BOT + 3)).box(
        lipo_l + 4, lipo_w + 4, 5, centered=(True, True, False)
    )
    fr = fr.cut(
        cq.Workplane("XY", origin=((BK_X0 + BK_X1) / 2, (BAY_Y0 + BAY_Y1) / 2, BK_BOT + 3)).box(
            lipo_l, lipo_w, 6, centered=(True, True, False)
        )
    )
    body = body.union(fr)
    # zip-anchor grid + hatch pilots
    x = BK_X0 + 10
    while x <= BK_X1 - 10:
        for y in (12, 24, 36):
            body = body.cut(cq.Workplane("XY", origin=(x, y, BK_BOT - 1)).circle(1.6).extrude(6))
        x += 12
    for dx in (-21, 21):
        for dy in (-15, 15):
            body = body.cut(
                cq.Workplane("XY", origin=((BK_X0 + BK_X1) / 2 + dx, (BAY_Y0 + BAY_Y1) / 2 + dy, BK_BOT - 1)).circle(1.3).extrude(9)
            )
    body = body.cut(outer_cyl(0.3))
    body = body.cut(tube_bore())
    return largest_solid(body)


def build_bay_hatch():
    p = (
        cq.Workplane("XY", origin=((BK_X1 - BK_X0) / 2, 0, 0))
        .placeSketch(rrect_sk(BK_X1 - BK_X0, BAY_Y1 - BAY_Y0, 8))
        .extrude(2.5)
    )
    for dx in (-21, 21):
        for dy in (-15, 15):
            p = p.cut(cq.Workplane("XY", origin=((BK_X1 - BK_X0) / 2 + dx, dy, -1)).circle(1.7).extrude(5))
            p = p.cut(cq.Workplane("XY", origin=((BK_X1 - BK_X0) / 2 + dx, dy, 1.3)).circle(3.1).extrude(2))
    return p


def build_pedestal_cart():
    cx = sum(p[0] for p in pads_pedestal) / 2
    base = cq.Workplane("XY", origin=(cx, bore_y, PAD_Z)).box(44, 24, 3, centered=(True, True, False))
    for px, py in pads_pedestal:
        base = base.cut(cq.Workplane("XY", origin=(px, py, PAD_Z - 1)).circle(1.7).extrude(6))
    tower = cq.Workplane("XY", origin=(66 + sol_len / 2, bore_y, PAD_Z + 3)).box(
        sol_len + 6, sol_w + 6, max(ped_top - PAD_Z - 3, 2), centered=(True, True, False)
    )
    body = base.union(tower)
    for dx in (sol_len / 2 - sol_hole_dx / 2, sol_len / 2 + sol_hole_dx / 2):
        body = body.cut(cq.Workplane("XY", origin=(66 + dx, bore_y, ped_top - 12)).circle(sol_hole_d / 2).extrude(13))
    # scallop: clear the latch boss column (+0.5)
    body = body.cut(cq.Workplane("XY", origin=(bore_x, bore_y, PAD_Z - 1)).circle(boss_d / 2 + 0.5).extrude(ped_top - PAD_Z + 3))
    return body


def build_lid():
    top = loft_rrect(pod_ox - 2 * draft, pod_oy - 2 * draft, 0, lid_t, max(r_pod - draft, 2), edge).translate(
        (POD_CX, pod_yc, 0)
    )
    ring = cq.Workplane("XY", origin=(nfc_cx, pod_yc, lid_t)).circle(17).extrude(0.6)
    ring = ring.cut(cq.Workplane("XY", origin=(nfc_cx, pod_yc, lid_t - 1)).circle(14).extrude(3))
    body = top.union(ring)
    body = body.cut(
        cq.Workplane("XY", origin=(pn532_x + pn532_l / 2, pod_yc, -EPS)).box(pn532_l, pn532_w, lid_t - window_remain, centered=(True, True, False))
    )
    body = body.cut(cq.Workplane("XY", origin=(bore_x, bore_y, -1)).circle((bore_d + 0.6) / 2).extrude(lid_t + 4))
    body = body.cut(cq.Workplane("XY", origin=(button_x, button_y, lid_t - 1)).circle(9.5).extrude(3))
    body = body.cut(cq.Workplane("XY", origin=(button_x, button_y, -1)).circle(button_d / 2).extrude(lid_t + 2))
    body = body.cut(cq.Workplane("XY", origin=(button_x, 3, lid_t - 0.8)).box(8, 12, 3, centered=(True, True, False)))
    for ly in (6, 0):
        body = body.cut(cq.Workplane("XY", origin=(button_x, ly, -1)).circle(led_d / 2).extrude(lid_t + 2))
    for cx in (5, pod_ix - 5):
        for cy in (pod_yc - pod_iy / 2 + 5, pod_yc + pod_iy / 2 - 5):
            body = body.cut(cq.Workplane("XY", origin=(cx, cy, -1)).circle(1.7).extrude(lid_t + 2))
            body = body.cut(cq.Workplane("XY", origin=(cx, cy, lid_t - 1.6)).circle(3.1).extrude(2))
    return largest_solid(body)


def _liner_sketch(R_hi, n, fh, ft):
    sk = cq.Sketch().circle(R_hi).circle(R_hi - liner_base, mode="s")
    embed = liner_base - 0.3
    for i in range(n):
        ang = math.radians(i * 360.0 / n)
        lean = math.radians(180 - fin_lean)
        r0 = R_hi - 0.3
        cx, cy = r0 * math.cos(ang), r0 * math.sin(ang)
        ux, uy = math.cos(ang + lean), math.sin(ang + lean)
        vx, vy = -math.sin(ang + lean), math.cos(ang + lean)
        L = fh + embed
        quad = [(cx, cy), (cx + L * ux, cy + L * uy), (cx + L * ux + ft * vx, cy + L * uy + ft * vy), (cx + ft * vx, cy + ft * vy)]
        sk = sk.polygon(quad, mode="a")
    return sk


def build_liner(right=True):
    sk = _liner_sketch(R_in - 0.15, fin_n, fin_h + liner_base, fin_t)
    solid = cq.Workplane("YZ", origin=(0, 0, 0)).placeSketch(sk).extrude(shell_len)
    return largest_solid(solid.intersect(half_box(right)))


def build_shim():
    sk = _liner_sketch(15.0, 12, 7.0, 1.2)
    solid = cq.Workplane("YZ").placeSketch(sk).extrude(shell_len)
    wedge = cq.Workplane("YZ", origin=(-1, 0, 0)).polyline([(0, 0), (40, -23), (40, 23)]).close().extrude(shell_len + 2)
    return largest_solid(solid.cut(wedge))


def build_spool_cover():
    d = drum_od - 2 - 0.4
    b = cq.Workplane("XY").circle(d / 2).extrude(3)
    b = b.union(cq.Workplane("XY").circle(10).extrude(4.2))
    for a in (30, 150, 270):
        r = drum_od / 2 - drum_wall / 2 - 2.5
        b = b.cut(cq.Workplane("XY", origin=(r * math.cos(math.radians(a)), r * math.sin(math.radians(a)), -1)).circle(1.7).extrude(6))
    b = b.cut(cq.Workplane("XY", origin=(0, 0, -1)).circle(5).extrude(7))
    return b


def build_end_plug():
    p = cq.Workplane("XY").circle(3.0).extrude(4)
    return p.union(cq.Workplane("XY", origin=(0, 0, 4)).circle(4.0).extrude(1.2))


PARTS = {
    "body": build_body,
    "door": build_door,
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


# =====================================================================
# kinematic verification
# =====================================================================
def entry_corridor():
    return cq.Workplane("XY", origin=(75, -36, 0)).box(shell_len + 20, 70, 2 * COR_Z, centered=(True, True, True))


def overlap_volume(a, b):
    """Intersection volume; OCC raises on an empty result - that's 0."""
    try:
        inter = a.intersect(b)
    except ValueError:
        return 0.0
    sols = inter.solids().vals()
    return sum(s.Volume() for s in sols) if sols else 0.0


def verify_corridor(fixed):
    return overlap_volume(fixed, entry_corridor())


def verify(sweep=False):
    print("[verify] building fixed set (body+bay+lid)...", flush=True)
    body = build_body()
    bay = build_bay_module()
    lid = cq.Workplane(obj=build_lid().val().moved(cq.Location(cq.Vector(0, 0, z_lid0))))
    fixed = body.union(bay).union(lid)
    v = verify_corridor(fixed)
    print(f"[verify] entry-corridor intersection volume = {v:.2f} mm^3 " + ("PASS" if v < 1 else "FAIL"), flush=True)
    ok = v < 1
    if sweep:
        print("[verify] door sweep 0..110 deg ...", flush=True)
        door = build_door()
        worst = 0.0
        for a in range(0, 111, 10):
            iv = overlap_volume(rot_about_hinge(door, a), fixed)
            print(f"  theta={a:3d}  overlap={iv:9.2f} mm^3", flush=True)
            worst = max(worst, iv)
        print(f"[verify] max sweep overlap = {worst:.2f} mm^3 " + ("PASS" if worst < 1 else "FAIL"), flush=True)
        ok = ok and worst < 1
    return ok


# one placements table drives --matrix, step/placed/, and the assembly file
# (name, part, translate, rotate_axis, rotate_deg)
def placements():
    return [
        ("01_body", "body", (0, 0, 0), None, 0),
        ("02_door", "door", (0, 0, 0), None, 0),
        ("03_bay_module", "bay_module", (0, 0, 0), None, 0),
        ("04_lid", "lid", (0, 0, z_lid0), None, 0),
        ("05_pedestal_cart", "pedestal_cart", (0, 0, 0), None, 0),
        ("06_liner_right", "liner_right", (0, 0, 0), None, 0),
        ("07_liner_left", "liner_left", (0, 0, 0), None, 0),
        ("08_bay_hatch", "bay_hatch", (BK_X0, (BAY_Y0 + BAY_Y1) / 2, BK_BOT - 2.5), None, 0),
        ("09_spool_cover", "spool_cover", (98, DR_Y1 - 2.9, drum_cz), (1, 0, 0), -90),
        ("10_end_plug_front", "end_plug", (5.4, 0, hinge_cz), (0, 1, 0), -90),
        ("11_end_plug_rear", "end_plug", (shell_len - 5.4, 0, hinge_cz), (0, 1, 0), 90),
    ]


def placed_solids():
    out = []
    cache = {}
    for name, part, t, axis, ang in placements():
        if part not in cache:
            cache[part] = PARTS[part]()
        v = cache[part].val()
        if ang:
            v = v.rotate(cq.Vector(0, 0, 0), cq.Vector(*axis), ang)
        out.append((name, cq.Workplane(obj=v.moved(cq.Location(cq.Vector(*t))))))
    return out


def verify_matrix():
    import itertools
    ps = placed_solids()
    bad = 0
    for (na, a), (nb, b) in itertools.combinations(ps, 2):
        v = overlap_volume(a, b)
        if v > 1:
            print(f"  CLASH {na} x {nb}: {v:.1f} mm^3", flush=True)
            bad += 1
    print(f"[verify] static interference matrix: {bad} clashing pairs " + ("PASS" if bad == 0 else "FAIL"), flush=True)
    return bad == 0


def main():
    import os

    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--sweep" in sys.argv:
        sys.exit(0 if verify(sweep=True) else 1)
    if "--matrix" in sys.argv:
        sys.exit(0 if verify_matrix() else 1)
    names = args or list(PARTS.keys())
    os.makedirs("step", exist_ok=True)
    os.makedirs("stl", exist_ok=True)
    for n in names:
        print(f"[build] {n} ...", flush=True)
        s = PARTS[n]()
        sol = s.solids().vals()
        if len(sol) > 1:
            fused = sol[0]
            for vv in sol[1:]:
                fused = fused.fuse(vv)
            fused = fused.clean()
            s = cq.Workplane(obj=fused)
            left = len(s.solids().vals())
            print(f"[warn]  {n}: fused {len(sol)} solids -> {left}", flush=True)
            if left > 1:
                raise RuntimeError(f"{n} still has {left} disconnected solids")
        cq.exporters.export(s, f"step/{n}.step")
        cq.exporters.export(s, f"stl/{n}.stl", tolerance=0.05, angularTolerance=0.2)
        print(f"[ok]    {n}", flush=True)


if __name__ == "__main__":
    main()
