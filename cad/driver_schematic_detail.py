"""driver_schematic_detail.py -> renders/electrical/driver_detail.svg/.png
Detailed solenoid-driver schematic: circuit diagram + breadboard row map + probe table."""
import os

W, H = 1780, 1180
BG   = "#FAFAF8"
RED, BLK, BLU, ORG, GRN, GRY = "#C62828", "#212121", "#1565C0", "#E65100", "#2E7D32", "#78909C"

o = []; A = o.append


def txt(x, y, t, s=13, c="#333", a="start", w="normal", st="normal", weight=None):
    if weight:
        w = weight
    A(f'<text x="{x}" y="{y}" text-anchor="{a}" font-family="DejaVu Sans" '
      f'font-size="{s}" font-weight="{w}" font-style="{st}" fill="{c}">{t}</text>')


def wire(pts, c=BLK, w=3.4):
    d = " ".join(f"{'M' if i == 0 else 'L'} {p[0]} {p[1]}" for i, p in enumerate(pts))
    A(f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{w}" '
      f'stroke-linecap="round" stroke-linejoin="round"/>')


def dot(x, y, c=BLK, r=6):
    A(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}"/>')


def panel(x, y, w, h, fill="#FFFFFF", stroke="#CFD8DC"):
    A(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{fill}" '
      f'stroke="{stroke}" stroke-width="2"/>')


def res(cx, cy, horiz=True, lbl="", lc="#111"):
    if horiz:
        A(f'<rect x="{cx-24}" y="{cy-11}" width="48" height="22" rx="4" '
          f'fill="#FFF8E1" stroke="#8D6E63" stroke-width="2"/>')
    else:
        A(f'<rect x="{cx-11}" y="{cy-24}" width="22" height="48" rx="4" '
          f'fill="#FFF8E1" stroke="#8D6E63" stroke-width="2"/>')


A(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
A(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
txt(40, 52, "SOLENOID DRIVER — full schematic", 28, "#111", weight="bold")
txt(40, 78, "Low-side switch: the MOSFET connects the coil's return wire to ground. "
            "The coil is ALWAYS tied to +6 V.", 14.5, "#666")

# ============================================================ PANEL A : circuit
panel(40, 100, 1100, 560)
txt(64, 138, "1 · THE CIRCUIT", 20, "#111", weight="bold")

VP, GN = 210, 570        # +6 V rail y, GND rail y
XL, XR = 130, 900        # rail extents
XS, XD, XM = 330, 520, 700   # solenoid x, diode x, mosfet x
DRAIN_Y, GATE_Y = 340, 440

# rails
wire([(XL, VP), (XR, VP)], RED, 4)
txt(XL, VP - 14, "+6 V   ( MT3608 OUT+ )", 14, RED, weight="bold")
wire([(XL, GN), (XR, GN)], BLK, 4)
txt(XL, GN + 26, "GND   ( MT3608 OUT−  AND  Nano GND — same rail )", 14, "#111", weight="bold")

# solenoid
wire([(XS, VP), (XS, 250)], RED)
for i in range(4):
    A(f'<path d="M {XS} {250 + i*17} q 22 8.5 0 17" fill="none" stroke="{RED}" stroke-width="3.4"/>')
wire([(XS, 318), (XS, DRAIN_Y)], ORG)
dot(XS, VP, RED); dot(XS, DRAIN_Y, ORG)
txt(XS - 34, 276, "SOLENOID", 14, RED, "end", "bold")
txt(XS - 34, 294, "6 V  1 A", 12, "#777", "end")
txt(XS - 34, 312, "coil — no polarity", 11.5, "#999", "end")

# diode 1N5819 (cathode up to +6 V)
wire([(XD, VP), (XD, 262)], RED)
A(f'<line x1="{XD-19}" y1="262" x2="{XD+19}" y2="262" stroke="#37474F" stroke-width="5"/>')
A(f'<path d="M {XD-19} 300 L {XD+19} 300 L {XD} 264 Z" fill="#37474F"/>')
wire([(XD, 300), (XD, DRAIN_Y)], ORG)
dot(XD, VP, RED); dot(XD, DRAIN_Y, ORG)
txt(XD + 30, 258, "1N5819  flyback", 13, "#111", weight="bold")
txt(XD + 30, 276, "BAND (silver stripe) on", 12, RED, weight="bold")
txt(XD + 30, 292, "the +6 V end — as drawn", 12, RED)
txt(XD + 30, 312, "backwards = dead short", 11.5, "#999")

# drain node
wire([(XS, DRAIN_Y), (XM, DRAIN_Y)], ORG)
txt(XM - 96, DRAIN_Y - 14, "DRAIN NODE", 13, ORG, "middle", "bold")

# MOSFET
A(f'<rect x="{XM-70}" y="390" width="140" height="100" rx="8" fill="#212121"/>')
txt(XM, 434, "IRLZ44N", 15, "#FFF", "middle", "bold")
txt(XM, 456, "logic level", 11.5, "#BDBDBD", "middle")
wire([(XM, DRAIN_Y), (XM, 390)], ORG)
wire([(XM, 490), (XM, GN)], BLK)
dot(XM, GN, BLK)
txt(XM + 14, 376, "D  middle leg", 13, ORG, "start", "bold")
txt(XM + 14, 512, "S  right leg", 13, "#111", "start", "bold")

# gate branch
wire([(XM - 70, GATE_Y), (XS, GATE_Y)], BLU)
txt(XM - 82, GATE_Y - 12, "G  left leg", 13, BLU, "end", "bold")
res(470, GATE_Y, True)
txt(470, GATE_Y - 20, "100 Ω", 13, "#111", "middle", "bold")
wire([(XS, GATE_Y), (150, GATE_Y)], BLU)
dot(XS, GATE_Y, BLU)
txt(146, GATE_Y + 5, "Nano  D5", 14, BLU, "end", "bold")
txt(146, GATE_Y + 23, "3.3 V logic", 11.5, "#999", "end")
wire([(XS, GATE_Y), (XS, GN)], BLU)
dot(XS, GN, BLK)
res(XS, 510, False)
txt(XS + 22, 508, "100 kΩ", 13, "#111", weight="bold")
txt(XS + 22, 526, "pull-down", 11.5, "#999")

txt(XM + 14, 540, "legs, printed face toward you, left → right:  G  D  S", 12, "#555")

# side notes
txt(940, 246, "WHEN D5 GOES HIGH", 14, GRN, weight="bold")
for i, ln in enumerate(["gate sees 3.3 V", "channel turns on", "drain is pulled to 0 V",
                        "the full 6 V now sits", "across the coil → CLUNK"]):
    txt(940, 272 + i * 21, "· " + ln, 12.5, "#444")

txt(940, 410, "WHEN D5 IS LOW", 14, "#B71C1C", weight="bold")
for i, ln in enumerate(["gate at 0 V (pull-down)", "channel off", "drain floats up to 6.2 V",
                        "0 V across the coil"]):
    txt(940, 436 + i * 21, "· " + ln, 12.5, "#444")

# ============================================================ PANEL B : row map
panel(40, 684, 1100, 456)
txt(64, 722, "2 · WHERE EACH LEAD GOES ON THE BREADBOARD", 20, "#111", weight="bold")
txt(64, 746, "A “row” = one group of 5 holes on one side of the centre channel. "
             "These four rows must be four DIFFERENT rows.", 13, "#666")

BARS = [
    (RED, "#FFEBEE", "+6 V row",   ["MT3608 OUT+", "solenoid wire A", "diode BAND end"]),
    (BLU, "#E3F2FD", "GATE row",   ["MOSFET left leg (G)", "100 Ω → Nano D5", "100 kΩ → GND rail"]),
    (ORG, "#FFF3E0", "DRAIN row",  ["MOSFET middle leg (D)", "solenoid wire B", "diode plain end"]),
    (BLK, "#ECEFF1", "SOURCE row", ["MOSFET right leg (S)", "jumper → GND rail"]),
]
by = 790
for col, fill, name, items in BARS:
    A(f'<rect x="290" y="{by-26}" width="800" height="52" rx="10" fill="{fill}" '
      f'stroke="{col}" stroke-width="2.5"/>')
    txt(276, by + 6, name, 16, col, "end", "bold")
    cx = 312
    for it in items:
        w_ = int(len(it) * 7.3) + 26
        A(f'<rect x="{cx}" y="{by-17}" width="{w_}" height="34" rx="7" fill="#FFFFFF" '
          f'stroke="{col}" stroke-width="1.6"/>')
        txt(cx + w_ / 2, by + 5, it, 13, "#111", "middle")
        cx += w_ + 18
    by += 82

txt(64, 1104, "Nothing else belongs in those rows. A stray lead sharing the GATE or DRAIN row "
              "is the usual reason it will not fire.", 13, "#B71C1C", weight="bold")

# ============================================================ PANEL C : probe table
panel(1180, 100, 560, 300, "#E8F5E9", GRN)
txt(1206, 138, "3 · MEASURE IT", 20, "#111", weight="bold")
txt(1206, 162, "Black probe on the GND rail the whole time.", 12.5, "#444")
txt(1216, 194, "point", 13, "#777", weight="bold")
txt(1430, 194, "idle", 13, "#777", weight="bold")
txt(1580, 194, "firing", 13, "#777", weight="bold")
for i, (p, a_, b_) in enumerate([("Nano D5", "0 V", "3.3 V"),
                                 ("gate (left leg)", "0 V", "3.3 V"),
                                 ("drain (middle)", "6.2 V", "under 0.5 V"),
                                 ("across the coil", "0 V", "6 V")]):
    yy = 226 + i * 30
    txt(1216, yy, p, 14, "#111", weight="bold")
    txt(1430, yy, a_, 14, "#444")
    txt(1580, yy, b_, 14, GRN, weight="bold")
txt(1206, 356, "The drain falling 6.2 V → 0 V IS the switch closing.", 13, "#111", weight="bold")
txt(1206, 376, "If it never moves, the gate never got there.", 12.5, "#555")

# ============================================================ PANEL D : fault tree
panel(1180, 424, 560, 716)
txt(1206, 462, "4 · IF IT STILL WON'T FIRE", 20, "#111", weight="bold")
txt(1206, 486, "Work down the list. Stop at the first failure.", 12.5, "#666")

steps = [
    ("Gate never reaches 3.3 V",
     ["D5 wire in the wrong row", "100 Ω not bridging D5 row → gate row",
      "firmware not actually pulsing D5"]),
    ("Gate is 3.3 V but drain stays 6.2 V",
     ["legs misread — G D S left→right only with", "  the printed face toward you",
      "MOSFET straddling one row (all 3 legs shorted)", "source not reaching the GND rail"]),
    ("Drain drops but coil does not move",
     ["one coil wire not in the +6 V row",
      "MT3608 sagging under 1 A load", "add the 1000 µF across +6 V / GND"]),
    ("Nothing at all, nowhere",
     ["MT3608 OUT− and Nano GND not on the SAME rail",
      "  — this is the single most common miss"]),
]
y = 522
for i, (head, items) in enumerate(steps):
    txt(1206, y, f"{i+1}.  {head}", 14.5, "#111", weight="bold")
    y += 24
    for it in items:
        txt(1226, y, ("· " + it) if not it.startswith("  ") else it, 12.5, "#555")
        y += 20
    y += 16

A(f'<rect x="1206" y="{y}" width="508" height="86" rx="8" fill="#FFF8E1" '
  f'stroke="#F9A825" stroke-width="2"/>')
txt(1226, y + 28, "Quick proof the driver works:", 13.5, "#111", weight="bold")
txt(1226, y + 50, "pull the D5 wire and touch the gate row", 12.5, "#444")
txt(1226, y + 68, "straight to +6 V. It must clunk.", 12.5, "#444")

A('</svg>')
os.makedirs("renders/electrical", exist_ok=True)
open("renders/electrical/driver_detail.svg", "w").write("\n".join(o))
print("ok")
