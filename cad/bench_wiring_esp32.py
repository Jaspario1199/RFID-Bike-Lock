"""bench_wiring_esp32.py -> renders/electrical/bench_wiring_esp32.svg/.png

The bench wiring for the Arduino Nano ESP32 build: exactly what to connect now, and what
gets added at stage 5. 3.3 V logic throughout, so the RC522 goes on direct.
"""
import os
W, H = 1760, 1170
BG, RAIL, CELL, BLK, BLU, GRN, RED2, DIM = "#FAFAF8", "#C62828", "#8E24AA", "#212121", "#1565C0", "#2E7D32", "#C62828", "#9E9E9E"
out = []; A = out.append

def txt(x, y, t, size=13, color="#333", anchor="start", weight="normal", style="normal"):
    A(f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="DejaVu Sans" font-size="{size}" '
      f'font-weight="{weight}" font-style="{style}" fill="{color}">{t}</text>')

def box(x, y, w, h, title, sub="", fill="#FFFFFF", stroke="#37474F", tsize=17, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    A(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" fill="{fill}" stroke="{stroke}" stroke-width="2"{d}/>')
    txt(x + w / 2, y + 26, title, tsize, "#111", "middle", "bold")
    for i, line in enumerate(sub.split("\n") if sub else []):
        txt(x + w / 2, y + 46 + i * 17, line, 12, "#666", "middle")

def wire(pts, color=BLU, width=2.6, dash=None):
    d = " ".join(f"{'M' if i == 0 else 'L'} {p[0]} {p[1]}" for i, p in enumerate(pts))
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    A(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round"{dd}/>')

def gnd(x, y):
    wire([(x, y), (x, y + 9)], BLK, 2.4)
    for i, half in enumerate((11, 7, 3.5)):
        A(f'<line x1="{x-half}" y1="{y+9+i*5}" x2="{x+half}" y2="{y+9+i*5}" stroke="{BLK}" stroke-width="2.4"/>')

A(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
A(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
txt(40, 48, "COMPLETE CIRCUIT — Arduino Nano ESP32 build", 27, "#111", weight="bold")
txt(40, 74, "Every connection on the bench right now. 3.3 V logic throughout; the only 6 V nets are the coil and the Nano's VIN.", 14, "#666")

# ---------------- Nano ----------------
NX, NY, NW, NH = 560, 200, 300, 620
box(NX, NY, NW, NH, "Arduino Nano ESP32", "ESP32-S3 · 3.3 V logic\nflash firmware/rfid_bike_lock_esp32/", "#E8EAF6")
PIN = {}
rows = [("VIN", "6.2–6.5 V in", RAIL), ("GND", "ground", BLK), ("3V3", "3.3 V out → reader", RAIL),
        ("", "", None),
        ("D2", "RED button", RED2), ("D3", "GREEN button — wake", GRN), ("D4", "RC522 RST", BLU),
        ("D5", "solenoid gate → driver", "#E65100"), ("D6", "buzzer", BLU), ("D7", "reader gate — NOT USED", DIM),
        ("D8", "red LED", RED2), ("D9", "green LED", GRN), ("D10", "RC522 SS", BLU),
        ("D11", "MOSI", BLU), ("D12", "MISO", BLU), ("D13", "SCK", BLU), ("A0", "battery sense", BLU)]
y = NY + 90
for nm, what, col in rows:
    if not nm:
        y += 12; continue
    PIN[nm] = y
    txt(NX + 16, y + 5, nm, 13.5, "#222", weight="bold")
    txt(NX + 66, y + 5, what, 12, col if col else "#666")
    y += 30

# ---------------- power ----------------
box(60, 200, 210, 96, "103450 LiPo", "3.7 V, part charged\nno charger yet — don't\nrun below 3.4 V", "#F3E5F5")
box(60, 360, 210, 92, "MT3608 boost", "SET TO 6.2–6.5 V\nBEFORE connecting\nanything to its output", "#FFF3E0")
wire([(165, 296), (165, 360)], CELL, 3)
txt(175, 332, "IN+ / IN−", 12, CELL)
wire([(270, 392), (400, 392), (400, PIN["VIN"]), (NX, PIN["VIN"])], RAIL, 3)
txt(300, 385, "OUT+ → VIN", 12, RAIL, weight="bold")
wire([(270, 424), (370, 424), (370, PIN["GND"]), (NX, PIN["GND"])], BLK, 3)
txt(300, 444, "OUT− → GND", 12, "#555")
gnd(370, 470)

# ---------------- RC522 ----------------
box(1120, 170, 300, 300, "RC522 reader", "13.56 MHz · SPI · 3.3 V\nkeep these wires under 20 cm", "#E3F2FD")
rc = [("SDA (SS)", "D10"), ("SCK", "D13"), ("MOSI", "D11"), ("MISO", "D12"), ("RST", "D4"), ("3.3V", "3V3"), ("GND", "GND")]
for i, (a_, b_) in enumerate(rc):
    yy = 250 + i * 30
    txt(1140, yy + 5, a_, 13, "#222", weight="bold")
    txt(1290, yy + 5, "← " + b_, 12.5, BLU if b_.startswith("D") else ("#C62828" if b_ == "3V3" else "#555"))
for i in range(7):
    yy = 250 + i * 30
    src = PIN[rc[i][1]] if rc[i][1] in PIN else PIN["GND"]
    wire([(NX + NW, src), (960 + i * 8, src), (960 + i * 8, yy), (1120, yy)], BLU if rc[i][1].startswith("D") else (RAIL if rc[i][1] == "3V3" else BLK), 2.0)

# ---------------- panel ----------------
box(1120, 520, 300, 320, "PANEL PARTS", "wire these next — the green button\nis the ONLY thing that wakes the board", "#F3E5F5")
items = [("GREEN button", "D3 → button → GND", 615, GRN),
         ("RED button", "D2 → button → GND", 668, RED2),
         ("Red LED", "D8 → 220 Ω → LED → GND", 721, RED2),
         ("Green LED", "D9 → 220 Ω → LED → GND", 774, GRN),
         ("Active buzzer", "D6 → buzzer (+), (−) → GND", 820, "#6A1B9A")]
for nm, wiring, yy, c in items:
    A(f'<circle cx="1142" cy="{yy-4}" r="6" fill="{c}"/>')
    txt(1158, yy, nm, 13, "#222", weight="bold")
    txt(1158, yy + 16, wiring, 11.5, "#666")
for nm, yy in (("D3", 611), ("D2", 664), ("D8", 717), ("D9", 770), ("D6", 816)):
    wire([(NX + NW, PIN[nm]), (900 + list(PIN).index(nm) * 4, PIN[nm]), (900 + list(PIN).index(nm) * 4, yy), (1120, yy)], BLU, 2.0)
gnd(1270, 850)

# ---------------- driver stage ----------------
ORG = "#E65100"
DY = 560
box(60, DY, 430, 250, "SOLENOID DRIVER", "low-side IRLZ44N · coil on the 6 V rail", "#FFF3E0", ORG, 16)
# +6V bus from MT3608 OUT+
wire([(400, 392), (400, 470), (130, 470), (130, DY + 60)], RAIL, 3)
txt(140, 464, "+6 V bus (same OUT+)", 11.5, RAIL, weight="bold")
wire([(130, DY + 60), (430, DY + 60)], RAIL, 3)
# coil
wire([(200, DY + 60), (200, DY + 80)], RAIL, 2.6)
for k in range(4):
    A(f'<path d="M 200 {DY+80+k*12} q 16 6 0 12" fill="none" stroke="{RAIL}" stroke-width="2.6"/>')
wire([(200, DY + 128), (200, DY + 150)], ORG, 2.6)
txt(190, DY + 100, "coil", 11.5, RAIL, "end", "bold")
txt(190, DY + 115, "6 V 1 A", 10.5, "#888", "end")
# diode
wire([(300, DY + 60), (300, DY + 90)], RAIL, 2.6)
A(f'<line x1="288" y1="{DY+90}" x2="312" y2="{DY+90}" stroke="#37474F" stroke-width="4"/>')
A(f'<path d="M 288 {DY+118} L 312 {DY+118} L 300 {DY+91} Z" fill="#37474F"/>')
wire([(300, DY + 118), (300, DY + 150)], ORG, 2.6)
txt(314, DY + 100, "1N5819", 11, "#111", weight="bold")
txt(314, DY + 114, "band up (+6 V)", 10.5, RED2)
# drain node
wire([(200, DY + 150), (380, DY + 150)], ORG, 2.6)
A(f'<circle cx="200" cy="{DY+150}" r="4" fill="{ORG}"/>'); A(f'<circle cx="300" cy="{DY+150}" r="4" fill="{ORG}"/>')
txt(290, DY + 144, "drain node", 10.5, ORG, "middle")
# mosfet
A(f'<rect x="{380-42}" y="{DY+165}" width="84" height="40" rx="5" fill="#212121"/>')
txt(380, DY + 190, "IRLZ44N", 11.5, "#FFF", "middle", "bold")
wire([(380, DY + 150), (380, DY + 165)], ORG, 2.6)
txt(390, DY + 162, "D", 11, ORG, weight="bold")
wire([(380, DY + 205), (380, DY + 225)], BLK, 2.6)
txt(390, DY + 222, "S", 11, "#111", weight="bold")
gnd(380, DY + 225)
# gate
GY = DY + 185
wire([(NX, PIN["D5"]), (520, PIN["D5"]), (520, GY), (338, GY)], ORG, 2.4)
A(f'<rect x="440" y="{GY-9}" width="34" height="18" rx="3" fill="#FFF8E1" stroke="#8D6E63" stroke-width="1.6"/>')
txt(457, GY - 14, "100 Ω", 10.5, "#111", "middle", "bold")
txt(330, GY + 4, "G", 11, ORG, "end", "bold")
wire([(432, GY), (432, DY + 220), (380, DY + 220)], ORG, 1.8)
A(f'<rect x="{432-8}" y="{DY+196}" width="16" height="20" rx="3" fill="#FFF8E1" stroke="#8D6E63" stroke-width="1.6"/>')
txt(446, DY + 211, "100 k", 10, "#111")
txt(80, DY + 242, "add 1000 µF across +6 V / GND (long leg = +)", 10.5, "#777")

# ---------------- battery sense ----------------
BY = 830
box(60, BY, 430, 120, "BATTERY SENSE", "A0 reads the cell, not the 6 V rail", "#E8EAF6", "#3949AB", 15)
wire([(60, 290), (44, 290), (44, BY + 72), (120, BY + 72)], CELL, 2.2)
txt(52, 284, "cell +", 10.5, CELL, "end")
txt(120, BY + 92, "cell +", 10.5, CELL, "middle", "bold")
A(f'<circle cx="120" cy="{BY+72}" r="4" fill="{CELL}"/>')
wire([(120, BY + 72), (145, BY + 72)], CELL, 2.2)
A(f'<rect x="145" y="{BY+63}" width="40" height="18" rx="3" fill="#FFF8E1" stroke="#8D6E63" stroke-width="1.6"/>')
txt(165, BY + 58, "100 k", 10.5, "#111", "middle", "bold")
wire([(185, BY + 72), (540, BY + 72), (540, PIN["A0"]), (NX, PIN["A0"])], BLU, 2.2)
A(f'<circle cx="230" cy="{BY+72}" r="4" fill="{BLU}"/>')
txt(300, BY + 66, "→ A0", 11, BLU, weight="bold")
wire([(230, BY + 72), (230, BY + 82)], BLU, 2.2)
A(f'<rect x="{230-9}" y="{BY+82}" width="18" height="22" rx="3" fill="#FFF8E1" stroke="#8D6E63" stroke-width="1.6"/>')
txt(244, BY + 97, "100 k", 10.5, "#111")
wire([(230, BY + 104), (230, BY + 108)], BLK, 2.2)
gnd(230, BY + 100)

# ---------------- notes ----------------
box(60, 980, 1660, 170, "ONE GROUND", "", "#E8F5E9", "#2E7D32", 16)
notes = [
 ("1.", "Every GND is the same rail.", "MT3608 OUT−, Nano GND, RC522 GND, both buttons, both LEDs, buzzer (−), MOSFET source, 100 kΩ, divider bottom."),
 ("2.", "Only two things touch 6 V.", "Nano VIN and the coil / diode-band end. Nothing else — the RC522, LEDs and gate all live at 3.3 V."),
 ("3.", "Reader on 3V3, never VIN.", "SS D10 · SCK D13 · MOSI D11 · MISO D12 · RST D4 · 3.3V ← 3V3 · GND. IRQ left empty."),
 ("4.", "Firmware: rfid_bike_lock_esp32", "Green = wake + scan. Red tap = cancel, red hold 5 s = admin. Both held at reset = factory wipe."),
]
for i, (n, a_, b_) in enumerate(notes):
    txt(84, 1025 + i * 30, n, 14, "#2E7D32", weight="bold")
    txt(110, 1025 + i * 30, a_, 13.5, "#111", weight="bold")
    txt(420, 1025 + i * 30, b_, 12.5, "#444")
A('</svg>')
os.makedirs("renders/electrical", exist_ok=True)
open("renders/electrical/bench_wiring_esp32.svg", "w").write("\n".join(out))
print("[ok]")
