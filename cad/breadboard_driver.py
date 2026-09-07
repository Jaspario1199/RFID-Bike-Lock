"""breadboard_driver.py -> renders/electrical/breadboard_driver.svg/.png
Pictorial breadboard layout for the stage-5 solenoid driver."""
import os
W, H = 1520, 900
BG, RED, BLK, BLU, GRN = "#FAFAF8", "#C62828", "#212121", "#1565C0", "#2E7D32"
out = []; A = out.append
def txt(x,y,t,s=13,c="#333",a="start",w="normal",st="normal",weight=None):
    if weight: w = weight
    A(f'<text x="{x}" y="{y}" text-anchor="{a}" font-family="DejaVu Sans" font-size="{s}" font-weight="{w}" font-style="{st}" fill="{c}">{t}</text>')
def line(pts,c=BLK,w=3.4):
    d=" ".join(f"{'M' if i==0 else 'L'} {p[0]} {p[1]}" for i,p in enumerate(pts))
    A(f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>')
A(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
A(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
txt(40,46,"BREADBOARD LAYOUT — solenoid driver",26,"#111",w="bold")
txt(40,72,"Each row of 5 holes is ONE node. Each MOSFET leg gets its own row — never two legs in the same row.",14,"#666")

# breadboard body
BX, BY, PITCH = 300, 130, 30
COLS = "abcde fghij"
NROWS = 18
A(f'<rect x="{BX-70}" y="{BY-46}" width="{11*PITCH+140}" height="{NROWS*PITCH+96}" rx="10" fill="#F5F5F0" stroke="#BDBDBD" stroke-width="2"/>')
# power rails
for i,(rx,col,lab) in enumerate([(BX-52,RED,"+"),(BX-30,BLK,"−")]):
    A(f'<line x1="{rx}" y1="{BY-20}" x2="{rx}" y2="{BY+NROWS*PITCH+20}" stroke="{col}" stroke-width="2"/>')
    txt(rx,BY-28,lab,15,col,"middle","bold")
for i,(rx,col) in enumerate([(BX+11*PITCH+22,RED),(BX+11*PITCH+44,BLK)]):
    A(f'<line x1="{rx}" y1="{BY-20}" x2="{rx}" y2="{BY+NROWS*PITCH+20}" stroke="{col}" stroke-width="2"/>')
# holes
for r in range(NROWS):
    yy = BY + r*PITCH
    txt(BX-84, yy+5, str(r+1), 11.5, "#999", "end")
    for ci,ch in enumerate(COLS):
        if ch == " ": continue
        xx = BX + ci*PITCH
        A(f'<circle cx="{xx}" cy="{yy}" r="4.6" fill="#FFFFFF" stroke="#B0BEC5" stroke-width="1.4"/>')
    # rail holes
    for rx,col in ((BX-52,RED),(BX-30,BLK),(BX+11*PITCH+22,RED),(BX+11*PITCH+44,BLK)):
        A(f'<circle cx="{rx}" cy="{yy}" r="4.2" fill="#FFFFFF" stroke="{col}" stroke-width="1.2"/>')
for ci,ch in enumerate(COLS):
    if ch == " ": continue
    txt(BX+ci*PITCH, BY-28, ch, 13, "#777", "middle", "bold")
# centre channel
A(f'<rect x="{BX+4.6*PITCH+8}" y="{BY-16}" width="{PITCH-16}" height="{NROWS*PITCH+32}" fill="#E0E0DC"/>')

TINT = {RED: "#FFE2E2", BLU: "#DCEAFB", BLK: "#E4E6E8"}
def rowhi(r, col, label):
    yy = BY + (r-1)*PITCH
    A(f'<rect x="{BX-18}" y="{yy-13}" width="{4*PITCH+36}" height="26" rx="6" fill="{TINT[col]}" stroke="{col}" stroke-width="1.2"/>')
    for ci in range(5):
        A(f'<circle cx="{BX+ci*PITCH}" cy="{yy}" r="4.6" fill="#FFFFFF" stroke="{col}" stroke-width="1.4"/>')
    txt(BX+4*PITCH+34, yy+5, label, 14, col, weight="bold")
rowhi(6,  RED, "+6 V")
rowhi(10, BLU, "GATE")
rowhi(11, RED, "DRAIN")
rowhi(12, BLK, "SOURCE")

# MOSFET shown beside the board, its three legs pointing at rows 10/11/12
mx = BX + 4*PITCH
for i,(nm,col) in enumerate([("G",BLU),("D",RED),("S",BLK)]):
    yy = BY + (9+i)*PITCH
    A(f'<circle cx="{mx}" cy="{yy}" r="5.4" fill="{col}"/>')
px, py = BX - 175, BY + 8.4*PITCH
A(f'<rect x="{px-30}" y="{py}" width="60" height="52" rx="4" fill="#212121"/>')
A(f'<rect x="{px-25}" y="{py-13}" width="50" height="15" rx="2" fill="#9E9E9E"/>')
txt(px, py+32, "IRLZ44N", 10, "#FFF", "middle", "bold")
for i,(nm,col) in enumerate([("G",BLU),("D",RED),("S",BLK)]):
    lx = px - 18 + i*18
    A(f'<rect x="{lx-3}" y="{py+52}" width="6" height="26" fill="#BDBDBD"/>')
    txt(lx, py+94, nm, 12.5, col, "middle", "bold")
    line([(lx, py+80),(lx, py+104),(BX-30, BY+(9+i)*PITCH)], col, 1.8)
txt(px, py-26, "plugs in here,", 12, "#555", "middle")
txt(px, py-10, "legs into rows 10/11/12", 12, "#555", "middle", "bold")

# ---- wiring list ----
A(f'<rect x="880" y="130" width="600" height="470" rx="9" fill="#FFFFFF" stroke="#CFD8DC" stroke-width="2"/>')
txt(906,166,"WHAT GOES IN EACH ROW",19,"#111",w="bold")
items = [
 (RED, "Row 6 — the +6 V node", ["separate 6 V supply +", "one solenoid wire", "diode BAND end", "capacitor + leg (later)"]),
 (BLU, "Row 10 — GATE", ["MOSFET G leg", "100 Ω → jumper to Nano D5", "100 kΩ → jumper to − rail"]),
 (RED, "Row 11 — DRAIN", ["MOSFET D leg", "the other solenoid wire", "diode's non-band end"]),
 (BLK, "Row 12 — SOURCE", ["MOSFET S leg", "jumper to the − rail"]),
]
y = 200
for col, head, lines in items:
    txt(906, y, head, 14.5, col, weight="bold"); y += 22
    for l in lines:
        txt(926, y, "· " + l, 12.5, "#444"); y += 19
    y += 10
txt(906, y+4, "− rail also takes: the 6 V supply's −, and a jumper", 12.5, "#B71C1C", weight="bold")
txt(906, y+22, "to the Nano's GND. Without that shared ground", 12.5, "#B71C1C")
txt(906, y+40, "nothing switches.", 12.5, "#B71C1C")

# ---- footer ----
A(f'<rect x="40" y="700" width="1440" height="160" rx="9" fill="#E8F5E9" stroke="#2E7D32" stroke-width="2"/>')
txt(64,736,"THREE THINGS THAT TRIP PEOPLE UP HERE",16,"#111",w="bold")
for i,t in enumerate([
 "The rows are horizontal. Row 11 columns a–e are all the same wire — so the MOSFET's D leg, the coil wire and the diode leg just",
 "need to be anywhere in that row, not touching each other.",
 "The MOSFET straddles three adjacent rows. If two legs land in one row you have shorted them, and the usual symptom is a hot part.",
 "The centre channel separates a–e from f–j. Keep the whole driver on one side; the channel is not a connection."]):
    txt(64,766+i*22,t,13,"#444")
A('</svg>')
os.makedirs("renders/electrical", exist_ok=True)
open("renders/electrical/breadboard_driver.svg","w").write("\n".join(out))
print("ok")
