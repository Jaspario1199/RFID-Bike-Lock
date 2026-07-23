#!/usr/bin/env python3
"""
RFID Bike Lock - parametric housing v0.3 (CadQuery / STEP edition)
==================================================================
Modular restructure per ASSEMBLY.md section 3, built on CadQuery so every
part exports as BREP STEP (SolidWorks-ready) alongside STL.

Coordinates match the OpenSCAD model: X along the frame tube (0..150),
Z up, tube axis at the origin.

v0.3 architecture (vs the v0.2 monolith):
  * drum is a separate module bolted FROM INSIDE the clamp bore (screws
    only reachable with the clamshell open = already unlocked)
  * all interior furniture (solenoid pedestal, driver tray, battery
    saddles, board pocket) are drop-in cartridges on standardized flat
    mounting pads at z=32 - the four VERIFY dimensions live in small,
    minutes-to-reprint parts instead of the shell
  * plunger-as-pin: the solenoid's own O6 plunger is the locking pin
    (45 deg ramp filed on its nose); no separate pin/spring/coupling
  * two short BLIND hinge pins inserted from the end faces, capped with
    glued plugs - no full-length threading, no exposed pin ends

Usage:
    python bike_lock_cq.py            # build + export everything
    python bike_lock_cq.py lid drum   # build only named parts
Outputs: step/<part>.step and stl/<part>.stl
"""
import math
import sys
import cadquery as cq

# ---------------- core (DESIGN.md 6.1) ----------------
shell_id, shell_wall, shell_len = 54.0, 4.0, 150.0
R_in, R_out = shell_id / 2, shell_id / 2 + shell_wall

# ---------------- pod ----------------
pod_ix, pod_iy, pod_wall, pod_h, lid_t = 150.0, 55.0, 3.0, 34.0, 3.0
z_crown = R_out                    # 31
z_lid0 = z_crown + pod_h           # 65
z_lidtop = z_lid0 + lid_t          # 68
pod_ox, pod_oy = pod_ix + 2 * pod_wall, pod_iy + 2 * pod_wall
draft, r_pod, r_belt, edge = 1.8, 11.0, 14.0, 1.2

# ---------------- belt / closure ----------------
belt_t, belt_z0 = 4.0, 14.0
belt_z1 = z_crown + 8              # 39
belt_oy = pod_oy + 2 * belt_t
gap, clr = 0.8, 0.5                # shadow gap; closure clearance (TODO tune)
pad_l, pad_w, pad_h = 26.0, 16.0, 6.0

# ---------------- latch (plunger-as-pin) ----------------
bore_d, bore_depth, bore_x = 11.0, 26.0, 58.0
bore_y = -pod_iy / 2 + 14          # -13.5
boss_d = bore_d + 8
plunger_d = 6.0                    # JF-0530B plunger IS the locking pin
pin_ch_d = plunger_d + 0.6         # its channel through the boss
head_seat = 11.5
pin_z = z_lidtop - head_seat       # 56.5
closure_screw_d = 4.4
sol_len, sol_w, sol_h = 30.0, 13.4, 15.0   # VERIFY body
sol_axis_h = 7.5                   # VERIFY plunger axis height
sol_hole_dx, sol_hole_d = 24.0, 2.2  # VERIFY mount holes
ped_top = pin_z - sol_axis_h       # 49

# ---------------- mounting pad system ----------------
PAD_Z = 32.0                       # every cartridge bolts to flat pads at this height
PAD = 12.0                         # pad square size
PAD_PILOT = 2.6                    # M3 self-tap pilot
# pad centers (x, y): pedestal x2, tray x2, saddles x2, board pocket x1
pads_pedestal = [(68, bore_y), (94, bore_y)]
pads_tray = [(110, -14), (138, -14)]
pads_saddle = [(82, 15), (118, 15)]
pads_pocket = [(140, 15)]
ALL_PADS = pads_pedestal + pads_tray + pads_saddle + pads_pocket

# ---------------- lid ----------------
pn532_l, pn532_w = 43.2, 41.0      # VERIFY board
pn532_x = 2.0
pn532_hole_dx, pn532_hole_dy = 36.5, 33.5  # VERIFY hole pattern
window_remain = 1.2
nfc_cx = 23.5
button_d, button_x, button_y = 12.4, 52.0, 12.0  # VERIFY
led_d = 3.3
usb_w, usb_h, usb_y, usb_z = 10.0, 4.0, 15.0, z_crown + 12
camlock_d = 16.4                   # VERIFY

# ---------------- liner ----------------
fin_n, fin_h, fin_t, fin_lean, liner_base = 24, 12.0, 1.4, 30.0, 2.0

# ---------------- drum module ----------------
drum_od, drum_w, drum_wall, drum_x = 95.0, 34.0, 3.0, 75.0
drum_overlap = 5.0
drum_cz = -(R_out + drum_od / 2 - drum_overlap)   # -73.5
cable_exit_d = 8.0
drum_screw_xs = (62.0, 88.0)       # M4s dropped from inside the bore
drum_screw_y = 8.0                 # both at +y and -y? right-half bias: +8 and -8 via module keying
drum_saddle_x0, drum_saddle_x1 = 52.0, 98.0

# ---------------- hinge ----------------
hinge_od, hinge_hole = 8.0, 3.2
hinge_cz = -R_out - hinge_od / 2 + 2               # -33
hinge_right = [(6, 20), (34, 48), (102, 116), (130, 144)]
hinge_left = [(20, 34), (48, 58), (96, 102), (116, 130)]
hinge_gap = 0.4
pin_depth = 60.0                   # blind pin channels from each end face

EPS = 0.01


# =====================================================================
# helpers
# =====================================================================
def rrect_sk(l, w, r):
    return cq.Sketch().rect(l, w).vertices().fillet(r)


def loft_rrect(l, w, z0, z1, r, d):
    """Drafted rounded slab centered on X=cx? -> centered at origin in XY; caller moves it."""
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
    return (
        cq.Workplane("YZ", origin=(-6, 0, 0)).circle(R_in).extrude(shell_len + 12)
    )


def outer_cyl(extra=0.0):
    return (
        cq.Workplane("YZ", origin=(-1, 0, 0)).circle(R_out + extra).extrude(shell_len + 2)
    )


def half_box(right=True):
    if right:
        return cq.Workplane("XY", origin=(-60, 100, 0)).box(shell_len + 120, 200, 520, centered=(False, True, True))
    return cq.Workplane("XY", origin=(-60, -100, 0)).box(shell_len + 120, 200, 520, centered=(False, True, True))


POD_CX, POD_CY = pod_ix / 2, 0.0   # pod plan center (x=75 - pod_wall offset handled below)
POD_PLAN_CX = (-pod_wall + (pod_ox - pod_wall)) / 2  # = 75


def pod_form(g=0.0):
    return loft_rrect(pod_ox + 2 * g, pod_oy + 2 * g, belt_z0 - 2 * g, z_lid0 + 2 * g, r_pod + g, draft).translate(
        (POD_PLAN_CX, 0, 0)
    )


def pod_interior():
    core = loft_rrect(pod_ix, pod_iy, belt_z0 - 2, z_lid0 + 1, r_pod - 1, draft).translate((POD_PLAN_CX, 0, 0))
    return core.cut(outer_cyl())


def belt_form():
    b = slab_rrect(pod_ox + 2 * belt_t, belt_oy, belt_z0, belt_z1, r_belt).translate((POD_PLAN_CX, 0, 0))
    try:
        b = b.edges(cq.selectors.NearestToPointSelector((POD_PLAN_CX, 0, belt_z0))).chamfer(edge * 2)
    except Exception:
        try:
            b = b.faces("<Z").chamfer(edge * 2)
        except Exception:
            pass
    return b


def belt_groove():
    outer = slab_rrect(pod_ox + 2 * belt_t + 2, belt_oy + 2, belt_z1 - gap, belt_z1 + EPS, r_belt).translate(
        (POD_PLAN_CX, 0, 0)
    )
    inner = slab_rrect(pod_ox + 2 * gap, pod_oy + 2 * gap, belt_z1 - gap - 1, belt_z1 + 1, r_pod + gap).translate(
        (POD_PLAN_CX, 0, 0)
    )
    return outer.cut(inner)


def side_fairing():
    s1 = rrect_sk(pod_ox, pod_oy, r_pod)
    s2 = rrect_sk(pod_ox - 10, 44, r_pod)
    f = (
        cq.Workplane("XY", origin=(POD_PLAN_CX, 0, belt_z0))
        .placeSketch(s1, s2.moved(cq.Location(cq.Vector(0, 0, -(belt_z0 - 5)))))
        .loft()
    )
    return f


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
    """Two BLIND channels from the end faces + counterbores for glued plugs."""
    front = cq.Workplane("YZ", origin=(-1, 0, hinge_cz)).circle(hinge_hole / 2).extrude(pin_depth + 1)
    back = cq.Workplane("YZ", origin=(shell_len + 1, 0, hinge_cz)).circle(hinge_hole / 2).extrude(-(pin_depth + 1))
    plug_f = cq.Workplane("YZ", origin=(-1, 0, hinge_cz)).circle(3.1).extrude(4)
    plug_b = cq.Workplane("YZ", origin=(shell_len + 1, 0, hinge_cz)).circle(3.1).extrude(-4)
    return front.union(back).union(plug_f).union(plug_b)


def drum_envelope(grow=0.0):
    """Drum module outer envelope (ring + saddle + snout) for clearance cuts."""
    ring = (
        cq.Workplane("YZ", origin=(drum_x - drum_w / 2 - grow, 0, drum_cz))
        .circle(drum_od / 2 + grow)
        .extrude(drum_w + 2 * grow)
    )
    saddle = cq.Workplane("XY", origin=((drum_saddle_x0 + drum_saddle_x1) / 2, 0, -R_out - 6)).box(
        drum_saddle_x1 - drum_saddle_x0 + 2 * grow, 40 + 2 * grow, 24, centered=(True, True, True)
    )
    sn = (
        cq.Workplane("YZ", origin=(drum_x - (cable_exit_d + 11) / 2 - grow, 0, 0))
        .center(0, 0)
        .circle((cable_exit_d + 11) / 2 + grow)
        .extrude(cable_exit_d + 11 + 2 * grow)
        .translate((0, 0, drum_cz - drum_od / 2 + 2))
        .rotate((drum_x, 0, drum_cz), (drum_x + 1, 0, drum_cz), 0)
    )
    return ring.union(saddle).union(sn)


def pad_boss(cx, cy):
    """Flat-top mounting pad rising from the curved floor to PAD_Z, with pilot."""
    b = cq.Workplane("XY", origin=(cx, cy, 10)).box(PAD, PAD, PAD_Z - 10, centered=(True, True, False))
    b = b.cut(cq.Workplane("XY", origin=(cx, cy, PAD_Z - 9)).circle(PAD_PILOT / 2).extrude(10))
    return b


def cart_base(cx_list, cy, l, w):
    """Flat cartridge base plate sitting on pads at PAD_Z with M3 clearance holes."""
    cx = sum(cx_list) / len(cx_list)
    b = cq.Workplane("XY", origin=(cx, cy, PAD_Z)).box(l, w, 3, centered=(True, True, False))
    for px in cx_list:
        b = b.cut(cq.Workplane("XY", origin=(px, cy, PAD_Z - 1)).circle(1.7).extrude(6))
    return b


# =====================================================================
# PARTS
# =====================================================================
def build_shell_right():
    base = outer_cyl().cut(tube_bore()).intersect(half_box(True))
    body = base.union(pod_form()).union(side_fairing().intersect(half_box(True)))
    body = body.union(belt_form().intersect(half_box(True)))
    body = body.union(knuckle_solids(hinge_right))
    # subtractions
    body = body.cut(pod_interior())
    body = body.cut(belt_groove())
    # ledge pocket the skirt lip hooks into (straight span)
    body = body.cut(
        cq.Workplane("XY", origin=(POD_PLAN_CX, -pod_oy / 2, belt_z1 - 1.25)).box(
            pod_ox - 30, 3, 2.5 + clr, centered=(True, True, True)
        )
    )
    # screw-pad pocket (left half's pad nests here)
    ppw = belt_oy / 2 + 1 - abs(bore_y) + pad_w / 2 + clr
    body = body.cut(
        cq.Workplane("XY", origin=(bore_x, -belt_oy / 2 - 1 + ppw / 2, z_crown - 2 - clr)).box(
            pad_l + 2 * clr, ppw, pad_h + 2 * clr, centered=(True, True, False)
        )
    )
    body = body.cut(knuckle_clear(hinge_left)).cut(hinge_pin_channels())
    # cam lock + usb
    body = body.cut(
        cq.Workplane("XZ", origin=(bore_x, -pod_oy / 2 - 5, z_crown + pod_h * 0.62))
        .circle(camlock_d / 2)
        .extrude(-(pod_wall + 8))
    )
    body = body.cut(
        cq.Workplane("XY", origin=(pod_ix - 2 + (2 * pod_wall + belt_t + 4) / 2, usb_y, usb_z + usb_h / 2)).box(
            2 * pod_wall + belt_t + 4, usb_w, usb_h, centered=(True, True, True)
        )
    )
    # usb niche recess in the rear belt face
    body = body.cut(
        cq.Workplane("XY", origin=(pod_ix + pod_wall + belt_t - 2.5 + 3, usb_y, usb_z + usb_h / 2)).box(
            6, usb_w + 7, usb_h + 7, centered=(True, True, True)
        )
    )
    # drum module: mounting holes dropped from inside the bore (counterbored flush)
    for sx in drum_screw_xs:
        for sy in (drum_screw_y, -drum_screw_y):
            zsurf = -math.sqrt(max(R_in * R_in - sy * sy, 0))
            body = body.cut(cq.Workplane("XY", origin=(sx, sy, zsurf + 1)).circle(2.2).extrude(-(shell_wall + 4)))
            body = body.cut(cq.Workplane("XY", origin=(sx, sy, zsurf + 1)).circle(4.0).extrude(-2.6))
    # latch boss + gussets (integral: the lock's load path)
    boss = cq.Workplane("XY", origin=(bore_x, bore_y, 0)).circle(boss_d / 2).extrude(z_lid0)
    for a in (45, 135, 225, 315):
        g = cq.Workplane("XY", origin=(bore_x, bore_y, 0)).box(boss_d / 2 + 5, 2.5, 36, centered=(False, True, False)).rotate(
            (bore_x, bore_y, 0), (bore_x, bore_y, 1), a
        )
        boss = boss.union(g)
    boss = boss.cut(tube_bore())
    boss = boss.cut(cq.Workplane("XY", origin=(bore_x, bore_y, z_lidtop - bore_depth)).circle(bore_d / 2).extrude(bore_depth + 2))
    boss = boss.cut(cq.Workplane("XY", origin=(bore_x, bore_y, -R_out)).circle(closure_screw_d / 2).extrude(z_lid0 + 2))
    boss = boss.cut(
        cq.Workplane("YZ", origin=(bore_x - 1, bore_y, pin_z)).circle(pin_ch_d / 2).extrude(boss_d + 2)
    )
    body = body.union(boss)
    # mounting pads for all cartridges
    for (px, py) in ALL_PADS:
        body = body.union(pad_boss(px, py))
    body = body.cut(tube_bore())
    return body


def build_shell_left():
    base = outer_cyl().cut(tube_bore()).intersect(half_box(False))
    skirt = belt_form().intersect(half_box(False)).cut(pod_form(clr))
    fair = side_fairing().intersect(half_box(False)).cut(pod_form(clr))
    lip = cq.Workplane("XY", origin=(POD_PLAN_CX, -pod_oy / 2 - 1.5 + (3 - clr) / 2 + clr, belt_z1 - 1.25 - clr)).box(
        pod_ox - 30 - 2 * clr, 3 - clr, 2.5 - clr, centered=(True, True, True)
    )
    spad = cq.Workplane("XY", origin=(bore_x, bore_y, z_crown - 2)).box(pad_l, pad_w, pad_h, centered=(True, True, False))
    strut_w = belt_oy / 2 - abs(bore_y) + pad_w / 2 - 1
    strut = cq.Workplane("XY", origin=(bore_x, -belt_oy / 2 + 1 + strut_w / 2, z_crown - 2)).box(
        pad_l, strut_w, 4, centered=(True, True, False)
    )
    body = base.union(skirt).union(fair).union(lip).union(spad).union(strut).union(knuckle_solids(hinge_left))
    body = body.cut(cq.Workplane("XY", origin=(bore_x, bore_y, z_crown - 3)).circle(2.8).extrude(pad_h + 6))  # M4 insert pocket
    body = body.cut(belt_groove())
    body = body.cut(drum_envelope(0.8))            # swing relief for the drum module
    body = body.cut(knuckle_clear(hinge_right)).cut(hinge_pin_channels())
    body = body.cut(tube_bore()).intersect(half_box(False))
    return body


def build_drum_module():
    """Separate zero-support print, bolted from inside the clamp bore."""
    ring = (
        cq.Workplane("YZ", origin=(drum_x - drum_w / 2, 0, drum_cz)).circle(drum_od / 2).extrude(drum_w)
    )
    ring = ring.cut(
        cq.Workplane("YZ", origin=(drum_x - drum_w / 2 + drum_wall, 0, drum_cz))
        .circle(drum_od / 2 - drum_wall)
        .extrude(drum_w)
    )
    # cover rabbet on the open (+X) face
    ring = ring.cut(
        cq.Workplane("YZ", origin=(drum_x + drum_w / 2 - 3, 0, drum_cz)).circle(drum_od / 2 - 1).extrude(3.2)
    )
    # saddle that hugs the shell bottom (concave upper face) + screw bosses
    saddle = cq.Workplane("XY", origin=((drum_saddle_x0 + drum_saddle_x1) / 2, 0, -R_out - 10)).box(
        drum_saddle_x1 - drum_saddle_x0, 36, 14, centered=(True, True, False)
    )
    saddle = saddle.cut(outer_cyl(0.3))            # concave seat against the shell
    body = ring.union(saddle)
    # M4 self-tap bosses under the 4 through-bore screws
    for sx in drum_screw_xs:
        for sy in (drum_screw_y, -drum_screw_y):
            zsurf = -math.sqrt(max(R_out * R_out - sy * sy, 0))
            b = cq.Workplane("XY", origin=(sx, sy, zsurf + 2)).circle(4.5).extrude(-(12))
            body = body.union(b.cut(outer_cyl(0.3)))
            body = body.cut(cq.Workplane("XY", origin=(sx, sy, zsurf)).circle(1.7).extrude(-12))
    # cable exit snout, 30 deg off vertical
    sn = cq.Workplane("XY", origin=(0, 0, 0)).circle((cable_exit_d + 10) / 2).extrude(16)
    sn = sn.translate((drum_x, 0, drum_cz - drum_od / 2 - 4)).rotate((drum_x, 0, drum_cz), (drum_x + 1, 0, drum_cz), 30)
    body = body.union(sn)
    hole = cq.Workplane("XY", origin=(0, 0, 0)).circle(cable_exit_d / 2).extrude(30)
    hole = hole.translate((drum_x, 0, drum_cz - drum_od / 2 - 12)).rotate((drum_x, 0, drum_cz), (drum_x + 1, 0, drum_cz), 30)
    body = body.cut(hole)
    # 3x M3 pockets in the open rim face
    for a in (30, 150, 270):
        r = drum_od / 2 - drum_wall / 2 - 2.5
        body = body.cut(
            cq.Workplane("YZ", origin=(drum_x + drum_w / 2 - 8, r * math.cos(math.radians(a)), drum_cz + r * math.sin(math.radians(a))))
            .circle(1.3)
            .extrude(9)
        )
    body = body.cut(tube_bore())
    return body


def build_pedestal_cart():
    """Solenoid cartridge: sits on 2 pads; positions the plunger on the pin axis."""
    base = cart_base([p[0] for p in pads_pedestal], bore_y, 44, 24)
    tower = cq.Workplane("XY", origin=(66 + sol_len / 2, bore_y, PAD_Z + 3)).box(sol_len + 6, sol_w + 6, ped_top - PAD_Z - 3, centered=(True, True, False))
    tower = tower.cut(
        cq.Workplane("XY", origin=(66 + sol_len / 2, bore_y, PAD_Z + 9)).box(sol_len - 4, sol_w + 9, ped_top, centered=(True, True, False))
    )
    body = base.union(tower)
    for dx in (sol_len / 2 - sol_hole_dx / 2, sol_len / 2 + sol_hole_dx / 2):
        body = body.cut(cq.Workplane("XY", origin=(66 + dx, bore_y, ped_top - 12)).circle(sol_hole_d / 2).extrude(13))
    return body


def build_driver_tray():
    base = cart_base([p[0] for p in pads_tray], -14, 44, 26)
    plate = cq.Workplane("XY", origin=(124, -14, 44)).box(40, 24, 2, centered=(True, True, False))
    legs = cq.Workplane("XY", origin=(124, -25, PAD_Z + 3)).box(40, 2, 44 - PAD_Z - 3, centered=(True, True, False))
    legs = legs.union(cq.Workplane("XY", origin=(124, -3, PAD_Z + 3)).box(40, 2, 44 - PAD_Z - 3, centered=(True, True, False)))
    body = base.union(plate).union(legs)
    body = body.cut(cq.Workplane("XY", origin=(108, -25, 38)).box(6, 8, 12, centered=(True, True, False)))  # wire notches
    body = body.cut(cq.Workplane("XY", origin=(140, -3, 38)).box(6, 8, 12, centered=(True, True, False)))
    for x in (112, 136):
        for y in (-20, -8):
            body = body.cut(cq.Workplane("XY", origin=(x, y, 43)).circle(1.6).extrude(4))
    return body


def build_battery_saddle():
    """One saddle (print two). Level 21.4mm bed for the 76x21x21 holder."""
    b = cq.Workplane("XY", origin=(0, 0, 0)).box(4, 27, 20, centered=(True, True, False))
    b = b.cut(cq.Workplane("XY", origin=(0, 0, 6)).box(6, 21.4, 20, centered=(True, True, False)))
    b = b.cut(cq.Workplane("XY", origin=(0, 0, 1)).box(6, 6, 4, centered=(True, True, False)))  # zip pass
    foot = cq.Workplane("XY", origin=(0, 0, -3)).box(PAD, PAD, 3, centered=(True, True, False))
    foot = foot.cut(cq.Workplane("XY", origin=(0, 0, -4)).circle(1.7).extrude(5))
    return b.union(foot)  # local coords; sits on a saddle pad


def build_board_pocket():
    """Card-edge carrier: TP4056 slides in vertically, USB-C lands in the wall slot."""
    b = cq.Workplane("XY", origin=(0, 0, 0)).box(24, 22, 3, centered=(True, True, False))
    b = b.cut(cq.Workplane("XY", origin=(0, 0, -1)).circle(1.7).extrude(5))
    # TP4056 slot: board 17.3 wide x 4.3 (clearance 0.4)
    walls = cq.Workplane("XY", origin=(6, 0, 3)).box(6, 22, 22, centered=(True, True, False))
    walls = walls.cut(cq.Workplane("XY", origin=(6, 0, 3)).box(4.7, 17.7, 23, centered=(True, True, False)))
    # MT3608 slot: board 17 wide
    walls2 = cq.Workplane("XY", origin=(-6, 0, 3)).box(8, 22, 20, centered=(True, True, False))
    walls2 = walls2.cut(cq.Workplane("XY", origin=(-6, 0, 3)).box(6.5, 17.4, 21, centered=(True, True, False)))
    return b.union(walls).union(walls2)


def build_lid():
    top = loft_rrect(pod_ox - 2 * draft, pod_oy - 2 * draft, 0, lid_t, max(r_pod - draft, 2), edge).translate((POD_PLAN_CX, 0, 0))
    ring = cq.Workplane("XY", origin=(nfc_cx, 0, lid_t)).circle(17).extrude(0.6)
    ring = ring.cut(cq.Workplane("XY", origin=(nfc_cx, 0, lid_t - 1)).circle(14).extrude(3))
    body = top.union(ring)
    body = body.cut(
        cq.Workplane("XY", origin=(pn532_x + pn532_l / 2, 0, -EPS)).box(pn532_l, pn532_w, lid_t - window_remain, centered=(True, True, False))
    )
    # PN532 mounting posts on the underside (M2.5 self-tap)  VERIFY hole pattern
    for sx in (-1, 1):
        for sy in (-1, 1):
            px = pn532_x + pn532_l / 2 + sx * pn532_hole_dx / 2
            py = sy * pn532_hole_dy / 2
            post = cq.Workplane("XY", origin=(px, py, -(6.0))).circle(2.5).extrude(6.0 - (lid_t - window_remain) + lid_t)
            post = post.cut(cq.Workplane("XY", origin=(px, py, -6.5)).circle(1.1).extrude(6))
            body = body.union(post)
    body = body.cut(cq.Workplane("XY", origin=(bore_x, bore_y, -1)).circle((bore_d + 0.6) / 2).extrude(lid_t + 4))
    body = body.cut(cq.Workplane("XY", origin=(button_x, button_y, lid_t - 1)).circle(9.5).extrude(3))       # button dish
    body = body.cut(cq.Workplane("XY", origin=(button_x, button_y, -1)).circle(button_d / 2).extrude(lid_t + 2))
    body = body.cut(cq.Workplane("XY", origin=(button_x, -6, lid_t - 0.8)).box(8, 14, 3, centered=(True, True, False)))  # LED recess
    for ly in (-3, -9):
        body = body.cut(cq.Workplane("XY", origin=(button_x, ly, -1)).circle(led_d / 2).extrude(lid_t + 2))
    for cx in (5, pod_ix - 5):
        for cy in (-pod_iy / 2 + 5, pod_iy / 2 - 5):
            body = body.cut(cq.Workplane("XY", origin=(cx, cy, -1)).circle(1.7).extrude(lid_t + 2))
            body = body.cut(cq.Workplane("XY", origin=(cx, cy, lid_t - 1.6)).circle(3.1).extrude(2))
    return body


def _liner_profile(right=True):
    """2D face: base arc ring + leaning fins, as a compound sketch."""
    pts_solid = None
    sk = cq.Sketch()
    Rl = R_in - 0.15
    sk = sk.circle(Rl).circle(Rl - liner_base, mode="s")
    for i in range(fin_n):
        ang = math.radians(i * 360.0 / fin_n)
        lean = math.radians(180 - fin_lean)
        r0 = Rl - liner_base
        cx, cy = r0 * math.cos(ang), r0 * math.sin(ang)
        ux, uy = math.cos(ang + lean), math.sin(ang + lean)
        vx, vy = -math.sin(ang + lean), math.cos(ang + lean)
        L, T = fin_h + liner_base, fin_t
        quad = [
            (cx, cy),
            (cx + L * ux, cy + L * uy),
            (cx + L * ux + T * vx, cy + L * uy + T * vy),
            (cx + T * vx, cy + T * vy),
        ]
        sk = sk.polygon(quad, mode="a")
    return sk


def build_liner(right=True):
    sk = _liner_profile(right)
    solid = cq.Workplane("YZ", origin=(0, 0, 0)).placeSketch(sk).extrude(shell_len)
    keep = half_box(right)
    return solid.intersect(keep)


def build_shim():
    shim_R = 15.0
    sk = cq.Sketch().circle(shim_R).circle(shim_R - 3, mode="s")
    for i in range(12):
        ang = math.radians(i * 30)
        lean = math.radians(180 - fin_lean)
        r0 = shim_R - 3
        cx, cy = r0 * math.cos(ang), r0 * math.sin(ang)
        ux, uy = math.cos(ang + lean), math.sin(ang + lean)
        vx, vy = -math.sin(ang + lean), math.cos(ang + lean)
        quad = [(cx, cy), (cx + 7 * ux, cy + 7 * uy), (cx + 7 * ux + 1.2 * vx, cy + 7 * uy + 1.2 * vy), (cx + 1.2 * vx, cy + 1.2 * vy)]
        sk = sk.polygon(quad, mode="a")
    solid = cq.Workplane("YZ").placeSketch(sk).extrude(shell_len)
    # 60-degree C-ring opening
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
    b = b.cut(cq.Workplane("XY", origin=(drum_cz, 0, -1)).circle(R_in + 0.4).extrude(7))  # frame-tube arc
    return b


def build_end_plug():
    p = cq.Workplane("XY").circle(3.0).extrude(4)
    p = p.union(cq.Workplane("XY", origin=(0, 0, 4)).circle(4.0).extrude(1.2))
    return p


PARTS = {
    "shell_right": build_shell_right,
    "shell_left": build_shell_left,
    "drum_module": build_drum_module,
    "pedestal_cart": build_pedestal_cart,
    "driver_tray": build_driver_tray,
    "battery_saddle": build_battery_saddle,
    "board_pocket": build_board_pocket,
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
