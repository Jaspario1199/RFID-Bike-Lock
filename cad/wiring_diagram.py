"""wiring_diagram.py - emits renders/electrical/wiring_diagram.svg/.png

Schematic-style wiring diagram for the rev 3c lock, matching WIRING.md's net list.
Colours: red = 6 V rail, dark red = cell (3.0-4.2 V), orange = switched reader supply,
black = ground, blue = logic. Local grounds use a ground symbol; the black bus carries only
the high-current path (cell - TP4056 - MT3608 - Nano - driver card), star point at the boost.
"""
import os

W, H = 1880, 1290
RAIL, CELL, ORG, BLK, BLU, BG = "#C62828", "#8E24AA", "#EF6C00", "#212121", "#1565C0", "#FAFAF8"
GND_Y, RAIL_Y = 1215, 250
out = []
A = out.append

def box(x, y, w, h, title, sub="", fill="#FFFFFF", stroke="#37474F", tsize=17, ssize=12.5, tdy=23):
    A(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
    A(f'<text x="{x+w/2}" y="{y+tdy}" text-anchor="middle" font-family="DejaVu Sans" font-size="{tsize}" font-weight="bold" fill="#111">{title}</text>')
    for i, line in enumerate(sub.split("\n") if sub else []):
        A(f'<text x="{x+w/2}" y="{y+tdy+21+i*17}" text-anchor="middle" font-family="DejaVu Sans" font-size="{ssize}" fill="#555">{line}</text>')

def wire(pts, color=BLU, width=2.6):
    d = " ".join(f"{'M' if i == 0 else 'L'} {p[0]} {p[1]}" for i, p in enumerate(pts))
    A(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round"/>')

def dot(x, y, color=BLK, r=5):
    A(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}"/>')

def gnd(x, y):
    """local ground symbol"""
    wire([(x, y), (x, y + 10)], BLK, 2.4)
    for i, half in enumerate((11, 7, 3.5)):
        A(f'<line x1="{x-half}" y1="{y+10+i*5}" x2="{x+half}" y2="{y+10+i*5}" stroke="{BLK}" stroke-width="2.4"/>')

def label(x, y, t, size=13, color="#333", anchor="start", weight="normal", style="normal"):
    A(f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="DejaVu Sans" font-size="{size}" font-weight="{weight}" font-style="{style}" fill="{color}">{t}</text>')

A(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
A(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
label(40, 48, "RFID BIKE LOCK — wiring diagram", 28, "#111", weight="bold")
label(40, 74, "rev 3c · RC522 build · matches the WIRING.md net list · firmware/rfid_bike_lock_rc522", 14.5, "#666")
lx = 980
for i, (c, t) in enumerate([(CELL, "cell, 3.0–4.2 V"), (RAIL, "6.0 V rail"), (ORG, "switched reader supply"),
                            (BLK, "ground (bus + local symbols)"), (BLU, "logic signal")]):
    A(f'<line x1="{lx}" y1="{34+i*17}" x2="{lx+32}" y2="{34+i*17}" stroke="{c}" stroke-width="3.4"/>')
    label(lx + 40, 39 + i * 17, t, 12.5, "#444")

# ---------------- power chain ----------------
box(40, 120, 118, 84, "USB-C", "charge in\n(TPU plug)", "#F1F8E9", tdy=30)
box(200, 120, 178, 84, "TP4056", "charger + protection\nB+  B−  OUT+  OUT−", "#F1F8E9", tdy=30)
box(420, 120, 172, 84, "103450 LiPo", "2000 mAh\nwith protection PCB", "#F1F8E9", tdy=30)
box(636, 120, 178, 84, "MT3608 boost", "SET TO 6.2-6.5 V FIRST\n(they ship at 20 V+)", "#FFF3E0", tdy=30)
wire([(158, 162), (200, 162)], BLK, 3)
wire([(378, 148), (420, 148)], CELL, 3); label(384, 141, "B+", 11.5, CELL)
wire([(378, 180), (420, 180)], BLK, 3); label(384, 197, "B−", 11.5, "#555")
wire([(592, 148), (636, 148)], CELL, 3); label(596, 141, "OUT+", 11, CELL)
wire([(592, 180), (636, 180)], BLK, 3); label(596, 197, "OUT−", 11, "#555")

# rails
wire([(725, 204), (725, RAIL_Y), (1830, RAIL_Y)], RAIL, 4)
wire([(725, RAIL_Y), (340, RAIL_Y)], RAIL, 4)
label(830, RAIL_Y - 13, "6.0 V RAIL", 16, RAIL, weight="bold")
wire([(280, 204), (280, GND_Y), (1620, GND_Y)], BLK, 4)
wire([(280, GND_Y), (120, GND_Y)], BLK, 4)
label(700, GND_Y + 26, "GROUND BUS — star point at the MT3608 input", 15, "#333", weight="bold")

# battery-sense divider off TP4056 OUT+
box(120, 296, 168, 52, "2 × 100 kΩ", "battery sense → A0", "#FFFFFF", "#90A4AE", 14, 11.5, tdy=21)
wire([(330, 204), (330, 322), (288, 322)], CELL, 2.4)
gnd(204, 348)
wire([(120, 322), (96, 322), (96, 960), (380, 960)], BLU, 2.4)
label(102, 953, "A0", 12.5, BLU, weight="bold")

# ---------------- Nano ----------------
NX, NY, NW = 380, 380, 250
box(NX, NY, NW, 585, "Arduino Nano", "ATmega328P · 5 V / 16 MHz", "#E8EAF6", tdy=26)
for name, y, col in [("VIN", 470, RAIL), ("GND", 500, BLK), ("5V", 530, RAIL)]:
    label(NX + 14, y + 5, name, 13.5, "#222", weight="bold")
wire([(354, RAIL_Y), (354, 470), (NX, 470)], RAIL, 2.8)
wire([(NX, 500), (312, 500), (312, GND_Y)], BLK, 2.8)
dot(354, RAIL_Y, RAIL); dot(312, GND_Y)
A(f'<rect x="{NX}" y="558" width="{NW}" height="390" rx="5" fill="#E8EAF6" stroke="#37474F" stroke-width="2"/>')
label(NX + 14, 552, "signal pins", 12, "#777", style="italic")
PIN = {}
rows = [("D2", "RED button"), ("D3", "GREEN button — wake"), ("D4", "RC522 RST"), ("D5", "solenoid gate"),
        ("D6", "buzzer"), ("D7", "reader power gate"), ("D8", "red LED"), ("D9", "green LED"),
        ("D10", "RC522 SS"), ("D11", "MOSI"), ("D12", "MISO"), ("D13", "SCK"), ("A0", "battery sense")]
for i, (nm, what) in enumerate(rows):
    y = 583 + i * 28
    PIN[nm] = y
    label(NX + 14, y + 5, nm, 13, "#222", weight="bold")
    label(NX + 62, y + 5, what, 12, "#666")

# ---------------- reader supply chain ----------------
box(720, 700, 152, 76, "AO3401", "P-FET high side\nD7 LOW = reader ON", "#FFF8E1", tdy=22, ssize=11.5)
box(912, 700, 168, 76, "AMS1117-3.3", "reader regulator —\nNOT the Nano 3V3 pin", "#FFF8E1", tdy=22, ssize=11.5)
box(1130, 380, 240, 250, "RC522 reader", "13.56 MHz · SPI\n3.3 V part", "#E3F2FD", tdy=28)
wire([(630, 530), (676, 530), (676, 726), (720, 726)], RAIL, 2.8)
label(560, 524, "5V pin", 11.5, RAIL)
wire([(872, 726), (912, 726)], ORG, 2.8)
wire([(1080, 726), (1104, 726), (1104, 505), (1130, 505)], ORG, 2.8)
label(1108, 498, "3.3 V", 12, ORG, weight="bold")
wire([(630, PIN["D7"]), (700, PIN["D7"]), (700, 758), (720, 758)], BLU, 2.4)
gnd(996, 776); gnd(1250, 630)

# level shifters
box(720, 830, 190, 96, "4 × divider", "1 kΩ series + 2 kΩ to GND\nSS · SCK · MOSI · RST", "#FFFFFF", "#90A4AE", 15, 11.5, tdy=22)
wire([(630, PIN["D4"]), (652, PIN["D4"]), (652, 852), (720, 852)], BLU, 2.2)
for nm, ty in (("D10", 872), ("D11", 892), ("D13", 912)):
    wire([(630, PIN[nm]), (688, PIN[nm]), (688, ty), (720, ty)], BLU, 2.2)
gnd(815, 926)
wire([(910, 878), (1010, 878), (1010, 660), (1180, 660), (1180, 630)], BLU, 2.4)
label(916, 871, "3.3 V logic → SS · SCK · MOSI · RST", 11.5, BLU)
# MISO direct
wire([(630, PIN["D12"]), (664, PIN["D12"]), (664, 990), (1320, 990), (1320, 630)], BLU, 2.2)
label(700, 984, "MISO returns direct — 3.3 V into a 5 V input, 0.3 V of margin", 12, "#B71C1C", style="italic")

# ---------------- driver card + solenoid ----------------
box(720, 1030, 600, 140, "DRIVER CARD — 42 × 10.7 mm, cut from perfboard, rides the solenoid cart", "", "#FFFDE7", "#F57F17", 15, tdy=24)
cols = [(742, "IRLZ44N  G–D–S", "laid flat, tab toward −x"), (940, "1N5819", "BAND → V+"),
        (1075, "1000 µF", "Ø8 × 12.5, lying down"), (1215, "100 Ω gate", "100 kΩ pulldown")]
for x, a_, b_ in cols:
    label(x, 1092, a_, 13.5, "#111", weight="bold")
    label(x, 1112, b_, 11.5, "#B71C1C" if "BAND" in b_ else "#666", weight="bold" if "BAND" in b_ else "normal")
wire([(640, RAIL_Y), (640, 1064), (720, 1064)], RAIL, 2.8); dot(640, RAIL_Y, RAIL)
wire([(630, PIN["D5"]), (610, PIN["D5"]), (610, 1140), (720, 1140)], BLU, 2.4)
wire([(900, 1170), (900, GND_Y)], BLK, 2.8); dot(900, GND_Y)
box(1390, 1046, 178, 92, "SOLENOID", "6 V coil\nmeasure: 15–25 Ω", "#FFEBEE", tdy=26)
wire([(1320, 1070), (1390, 1070)], RAIL, 2.8); label(1326, 1063, "V+", 11.5, RAIL)
wire([(1390, 1114), (1352, 1114), (1352, 1190), (1250, 1190), (1250, 1170)], BLK, 2.6)
label(1120, 1206, "coil − → IRLZ44N drain", 11.5, "#555")

# ---------------- lid panel ----------------
box(40, 630, 236, 300, "LID PANEL", "on a JST-XH — the lid\nmust detach to reflash", "#F3E5F5", tdy=26, ssize=11.5)
items = [("GREEN button", "D3 → GND, wake", 712, "#2E7D32"), ("RED button", "D2 → GND, cancel / admin", 762, "#C62828"),
         ("Red LED + 470 Ω", "D8", 812, "#C62828"), ("Green LED + 470 Ω", "D9", 862, "#2E7D32"),
         ("Active buzzer", "D6, ~25 mA", 906, "#6A1B9A")]
for nm, pin, y, c in items:
    A(f'<circle cx="62" cy="{y-4}" r="6" fill="{c}"/>')
    label(78, y, nm, 12.5, "#222", weight="bold")
    label(78, y + 15, pin, 11.5, "#666")
for nm in ("D2", "D3", "D6", "D8", "D9"):
    wire([(NX, PIN[nm]), (276, PIN[nm])], BLU, 2.0)
gnd(158, 930)

# ---------------- right column notes ----------------
box(1420, 120, 420, 232, "⚠  THE THREE THAT COST HARDWARE", "", "#FFF5F5", "#B71C1C", 15.5, tdy=26)
warn = [("1.  1N5819 band goes to V+.", "Backwards = a dead short across the cell."),
        ("2.  Verify the IRLZ44N pinout.", "D and S swapped = permanent conduction."),
        ("3.  Set the MT3608 to 6.2-6.5 V", "before anything is connected to it.")]
for i, (a_, b_) in enumerate(warn):
    label(1440, 178 + i * 58, a_, 14, "#B71C1C", weight="bold")
    label(1440, 198 + i * 58, b_, 12.5, "#555")

box(1420, 376, 420, 180, "RC522 IS A 3.3 V PART", "", "#F1F8E9", "#33691E", 15.5, tdy=26)
for i, t in enumerate(["Power it from an AMS1117-3.3, never the",
                       "Nano's 3V3 pin — CH340 clones can't feed it.",
                       "Level-shift SS · SCK · MOSI · RST (1 k / 2 k).",
                       "MISO returns direct: suspect it first on",
                       "intermittent reads.",
                       "Bench-only shortcut: USB power + 3V3 pin."]):
    label(1440, 424 + i * 22, ("•  " if i in (0, 2, 3, 5) else "    ") + t, 12.5, "#33691E" if i in (0, 2, 3, 5) else "#555")

box(1420, 580, 420, 172, "THE TEST THAT DECIDES BATTERY LIFE", "", "#E8F5E9", "#2E7D32", 15, tdy=26)
label(1440, 630, "Meter in series with the cell, after the", 12.5, "#333")
label(1440, 648, "scan window expires:", 12.5, "#333")
for i, (v, c, t) in enumerate([("1.5–3 mA", "#2E7D32", "correct → 3–4 weeks/charge"),
                               ("15–25 mA", "#C62828", "Nano never slept"),
                               ("40 mA +", "#C62828", "reader still powered")]):
    label(1440, 680 + i * 23, v, 14, c, weight="bold")
    label(1530, 680 + i * 23, t, 12.5, "#333")

box(1420, 776, 420, 176, "SOLENOID: MEASURE BEFORE WIRING", "", "#FFF8E1", "#F57F17", 15, tdy=26)
for i, (v, t) in enumerate([("15–25 Ω", "the 6 V winding — put it on the rail"),
                            ("2–5 Ω", "high-current variant: the boost can't"),
                            ("", "drive it. Run off the cell or swap it."),
                            ("under 1 Ω", "you're reading your leads, or it's shorted")]):
    label(1440, 826 + i * 24, v, 13.5, "#E65100", weight="bold")
    label(1540, 826 + i * 24, t, 12.5, "#444")
A('</svg>')
os.makedirs("renders/electrical", exist_ok=True)
open("renders/electrical/wiring_diagram.svg", "w").write("\n".join(out))
print("[ok] svg")
