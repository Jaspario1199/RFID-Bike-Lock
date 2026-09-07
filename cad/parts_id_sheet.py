"""parts_id_sheet.py - renders/electrical/parts_id.svg/.png

Visual identification sheet for the small electronic modules: what each board looks like, its
real size, which pad is which, and how to tell the variant you want from the one you don't.
Boards are drawn at 2x actual size so the labels fit.
"""
import os
S = 6.8                      # px per mm (2x actual size)
W, H = 1780, 1010
BG = "#FAFAF8"
out = []; A = out.append

def txt(x, y, t, size=13, color="#333", anchor="start", weight="normal", style="normal"):
    A(f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="DejaVu Sans" font-size="{size}" '
      f'font-weight="{weight}" font-style="{style}" fill="{color}">{t}</text>')

def pcb(x, y, w_mm, h_mm, fill="#1B5E20"):
    w, h = w_mm * S, h_mm * S
    A(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{fill}" stroke="#263238" stroke-width="1.5"/>')
    return w, h

def chip(x, y, w, h, mark="", fill="#212121", tsize=10):
    A(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="2" fill="{fill}"/>')
    if mark:
        txt(x + w / 2, y + h / 2 + tsize * 0.36, mark, tsize, "#EEE", "middle", "bold")

def card(x, y, w, h, title, sub):
    A(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="#FFFFFF" stroke="#CFD8DC" stroke-width="2"/>')
    txt(x + 22, y + 32, title, 19, "#111", weight="bold")
    txt(x + 22, y + 53, sub, 12.5, "#777")

def note(x, y, lines, head="#2E7D32"):
    txt(x, y, lines[0], 13, head, weight="bold")
    for i, t in enumerate(lines[1:]):
        txt(x, y + 20 + i * 18, t, 12.5, "#555")

A(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
A(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
txt(40, 48, "PARTS IDENTIFICATION — the small modules", 28, "#111", weight="bold")
txt(40, 74, "Boards drawn at 2× actual size, to the same scale as each other. Sort your parts against this as they arrive.", 14, "#666")

# ================= TP4056 =================
card(40, 104, 840, 400, "TP4056 — the battery charger", "real size 29 × 17 mm · USB-C in · cell on B+/B− · load on OUT+/OUT−")
bx, by = 96, 190
w, h = pcb(bx, by, 29, 17, "#1B5E20")
A(f'<rect x="{bx-22}" y="{by+h/2-20}" width="24" height="40" rx="4" fill="#B0BEC5" stroke="#78909C" stroke-width="1.5"/>')
txt(bx - 10, by + h + 26, "USB-C", 12, "#555", "middle", "bold")
chip(bx + 24, by + 20, 54, 34, "TP4056", tsize=11)
chip(bx + 96, by + 16, 34, 22, "DW01", fill="#37474F", tsize=9)
chip(bx + 96, by + 48, 34, 20, "8205", fill="#37474F", tsize=9)
A(f'<rect x="{bx+10}" y="{by+18}" width="12" height="8" rx="1" fill="#E53935"/>')
A(f'<rect x="{bx+10}" y="{by+38}" width="12" height="8" rx="1" fill="#2196F3"/>')
txt(bx + 30, by - 10, "red LED = charging · blue = done", 11.5, "#555")
for nm, yy in [("B+", 8), ("B−", 34), ("OUT+", 60), ("OUT−", 86)]:
    A(f'<rect x="{bx+w-8}" y="{by+yy}" width="26" height="14" rx="2" fill="#D4AF37"/>')
    txt(bx + w + 26, by + yy + 12, nm, 12.5, "#222", weight="bold")
txt(bx, by + h + 52, "the four pads that matter →", 11.5, "#999", style="italic")
note(470, 200, ["✔  THE ONE YOU WANT — protected", "Two extra chips beside the main one:",
                "DW01 (6-pin) and FS8205 (marked 8205).", "They add over-discharge, over-current",
                "and short protection.", "Usually the USB-C version."])
note(470, 350, ["✘  The one to avoid — unprotected", "Only the TP4056 chip, no DW01, no 8205.",
                "It charges correctly but protects nothing."], head="#B71C1C")

# ================= MT3608 =================
card(910, 104, 830, 400, "MT3608 — the boost converter", "real size 36 × 17 mm · steps 3.7 V up to 6.0 V · the tall drum gives it away")
bx, by = 966, 200
w, h = pcb(bx, by, 36, 17, "#1565C0")
A(f'<circle cx="{bx+82}" cy="{by+h/2}" r="26" fill="#9E9E9E" stroke="#616161" stroke-width="2"/>')
txt(bx + 82, by + h / 2 + 5, "L", 14, "#FFF", "middle", "bold")
A(f'<rect x="{bx+150}" y="{by+22}" width="42" height="42" rx="3" fill="#1976D2" stroke="#0D47A1"/>')
A(f'<circle cx="{bx+171}" cy="{by+43}" r="14" fill="#E0E0E0" stroke="#9E9E9E"/>')
A(f'<line x1="{bx+171}" y1="{by+31}" x2="{bx+171}" y2="{by+55}" stroke="#616161" stroke-width="3"/>')
txt(bx + 171, by + h + 26, "TRIM POT", 12, "#222", "middle", "bold")
txt(bx + 171, by + h + 44, "turn this to 6.00 V first", 11.5, "#B71C1C", "middle", "bold")
for nm, yy in [("IN+", 16), ("IN−", 66)]:
    A(f'<rect x="{bx-26}" y="{by+yy}" width="26" height="14" rx="2" fill="#D4AF37"/>')
    txt(bx - 34, by + yy + 12, nm, 12.5, "#222", "end", "bold")
for nm, yy in [("OUT+", 16), ("OUT−", 66)]:
    A(f'<rect x="{bx+w}" y="{by+yy}" width="26" height="14" rx="2" fill="#D4AF37"/>')
    txt(bx + w + 34, by + yy + 12, nm, 12.5, "#222", weight="bold")
txt(bx + 82, by - 12, "6 × 6 mm inductor, stands ~5 mm proud", 11.5, "#555", "middle")
note(1330, 220, ["How to spot it", "The silver drum is taller than anything", "else here. Blue board, blue trim pot."])
note(1330, 330, ["✘  Not the same as your MP1584s", "The ones left over from RoomCleaner are",
                 "MP1584 BUCKs. A buck steps voltage DOWN —", "it cannot make 6 V from a 3.7 V cell."], head="#B71C1C")

# ================= AMS1117 + AO3401 =================
card(40, 524, 840, 380, "AMS1117-3.3 and AO3401 — the reader supply pair", "the two small parts that keep the RC522 alive, and switchable")
bx, by = 96, 620
txt(bx, by - 16, "AMS1117-3.3 module", 14, "#111", weight="bold")
w, h = pcb(bx, by, 22, 13, "#4E342E")
chip(bx + 34, by + 16, 62, 34, "AMS1117", tsize=10)
for nm, xx in [("IN", 8), ("GND", 56), ("OUT", 104)]:
    A(f'<rect x="{bx+xx}" y="{by+h-6}" width="34" height="12" rx="2" fill="#D4AF37"/>')
    txt(bx + xx + 17, by + h + 24, nm, 12, "#222", "middle", "bold")
txt(bx, by + h + 50, "22 × 13 mm · makes a clean 3.3 V", 12, "#555")
bx2 = 390
txt(bx2, by - 16, "AO3401 breakout (SOT-23)", 14, "#111", weight="bold")
w2, h2 = pcb(bx2, by, 15, 12, "#37474F")
chip(bx2 + 26, by + 18, 50, 30, "AO3401", tsize=9.5)
for nm, xx in [("G", 6), ("D", 42), ("S", 78)]:
    A(f'<rect x="{bx2+xx}" y="{by+h2-6}" width="24" height="12" rx="2" fill="#D4AF37"/>')
    txt(bx2 + xx + 12, by + h2 + 24, nm, 12, "#222", "middle", "bold")
txt(bx2, by + h2 + 50, "grain-of-rice sized · P-channel MOSFET", 12, "#555")
note(620, 610, ["What the pair does", "AO3401 switches the 5 V on and off from D7.",
                "AMS1117 turns that into 3.3 V for the reader.", "",
                "Gating upstream of the regulator means the", "regulator's own idle draw disappears too."])

# ================= IRLZ44N + 1N5819 =================
card(910, 524, 830, 380, "IRLZ44N and 1N5819 — the solenoid driver parts", "the two you can destroy by installing them backwards")
bx, by = 980, 640
txt(bx - 12, by - 20, "IRLZ44N (TO-220)", 14, "#111", weight="bold")
A(f'<rect x="{bx}" y="{by}" width="{10*S}" height="{15*S}" rx="4" fill="#212121"/>')
A(f'<rect x="{bx+5}" y="{by-16}" width="{10*S-10}" height="20" rx="3" fill="#9E9E9E"/>')
A(f'<circle cx="{bx+5*S}" cy="{by-6}" r="6" fill="{BG}"/>')
txt(bx + 5 * S, by + 40, "IRLZ44N", 11, "#FFF", "middle", "bold")
for i, nm in enumerate(["G", "D", "S"]):
    xx = bx + 12 + i * 22
    A(f'<rect x="{xx}" y="{by+15*S}" width="8" height="34" fill="#BDBDBD"/>')
    txt(xx + 4, by + 15 * S + 52, nm, 13, "#222", "middle", "bold")
txt(bx - 12, by + 15 * S + 76, "printed side toward you, legs down", 11.5, "#555")
bx3 = 1180
txt(bx3, by - 20, "1N5819 (Schottky diode)", 14, "#111", weight="bold")
A(f'<rect x="{bx3+10}" y="{by+30}" width="86" height="34" rx="5" fill="#37474F"/>')
A(f'<rect x="{bx3+82}" y="{by+30}" width="12" height="34" fill="#EEEEEE"/>')
A(f'<line x1="{bx3-18}" y1="{by+47}" x2="{bx3+10}" y2="{by+47}" stroke="#BDBDBD" stroke-width="4"/>')
A(f'<line x1="{bx3+96}" y1="{by+47}" x2="{bx3+128}" y2="{by+47}" stroke="#BDBDBD" stroke-width="4"/>')
txt(bx3 + 88, by + 20, "BAND", 12, "#B71C1C", "middle", "bold")
A(f'<path d="M {bx3+88} {by+72} L {bx3+88} {by+88}" stroke="#B71C1C" stroke-width="2.5"/>')
txt(bx3 + 88, by + 106, "this end goes to V+", 12, "#B71C1C", "middle", "bold")
note(1360, 610, ["Both have a fatal orientation", "IRLZ44N: G–D–S left to right with the",
                 "printed side toward you. Confirm it with", "your meter's diode range before soldering.", "",
                 "1N5819: the painted band is the cathode.", "Backwards = a dead short across the cell."], head="#B71C1C")

# ================= footer =================
A(f'<rect x="40" y="924" width="1700" height="66" rx="8" fill="#FFF8E1" stroke="#F57F17" stroke-width="2"/>')
txt(62, 950, "SORTING TIP:", 14, "#E65100", weight="bold")
txt(178, 950, "TP4056 is the only one with a USB socket  ·  MT3608 the only one with a tall drum and a pot  ·  "
              "AMS1117 has three pads and no LEDs  ·  RC522 is far bigger than all of them (60 × 39 mm)", 12.5, "#444")
txt(62, 974, "Full electrical detail in WIRING.md  ·  regenerate this sheet: python cad/parts_id_sheet.py", 11.5, "#999")
A('</svg>')
os.makedirs("renders/electrical", exist_ok=True)
open("renders/electrical/parts_id.svg", "w").write("\n".join(out))
print("[ok] svg")
