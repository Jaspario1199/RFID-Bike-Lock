"""bench_wiring_esp32.py -> renders/electrical/bench_wiring_esp32.svg/.png

The bench wiring for the Arduino Nano ESP32 build: exactly what to connect now, and what
gets added at stage 5. 3.3 V logic throughout, so the RC522 goes on direct.
"""
import os
W, H = 1760, 1080
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
txt(40, 48, "BENCH WIRING — Arduino Nano ESP32 build", 27, "#111", weight="bold")
txt(40, 74, "3.3 V logic throughout: the RC522 connects DIRECT — no level shifters, no AMS1117, no 5 V anywhere.", 14, "#666")

# ---------------- Nano ----------------
NX, NY, NW, NH = 560, 200, 300, 620
box(NX, NY, NW, NH, "Arduino Nano ESP32", "ESP32-S3 · 3.3 V logic\nflash firmware/rfid_bike_lock_esp32/", "#E8EAF6")
PIN = {}
rows = [("VIN", "6.2–6.5 V in", RAIL), ("GND", "ground", BLK), ("3V3", "3.3 V out → reader", RAIL),
        ("", "", None),
        ("D2", "RED button", RED2), ("D3", "GREEN button — wake", GRN), ("D4", "RC522 RST", BLU),
        ("D5", "solenoid gate (stage 5)", DIM), ("D6", "buzzer", BLU), ("D7", "reader gate — NOT USED", DIM),
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

# ---------------- stage 5 (later) ----------------
box(60, 640, 430, 200, "STAGE 5 — add later", "", "#FFFDE7", "#F57F17", 16, dash="7 5")
txt(80, 700, "Driver card: IRLZ44N + 1N5819 + 1000 µF", 13.5, "#111", weight="bold")
txt(80, 722, "D5 ─ 100 Ω ─ gate, 100 kΩ gate→GND", 12.5, "#555")
txt(80, 742, "coil from the 6 V rail, diode BAND to +", 12.5, "#B71C1C", weight="bold")
txt(80, 768, "Power the coil from a SEPARATE 6 V", 12.5, "#555")
txt(80, 786, "source until the 1000 µF cap arrives —", 12.5, "#555")
txt(80, 804, "a 1 A pulse can dip a shared rail enough", 12.5, "#555")
txt(80, 822, "to reset the board.", 12.5, "#555")
wire([(NX, PIN["D5"]), (500, PIN["D5"]), (500, 700), (490, 700)], DIM, 2.2, dash="6 4")

# ---------------- notes ----------------
box(60, 880, 1660, 170, "WHAT TO DO NOW", "", "#E8F5E9", "#2E7D32", 16)
notes = [
 ("1.", "Add the two buttons and the buzzer.", "The green button on D3 is the only thing that wakes the board — without it nothing happens."),
 ("2.", "Use 220 Ω LED resistors, not 470 Ω.", "470 was sized for a 5 V board; on 3.3 V it gives ~2.5 mA and the LEDs look dim."),
 ("3.", "Flash firmware/rfid_bike_lock_esp32/", "Boards Manager → Arduino ESP32 Boards → Arduino Nano ESP32. Library Manager → MFRC522."),
 ("4.", "Press green, tap a fob.", "First fob tapped becomes master. Second fob → 2 red blinks + long buzz. Hold red 5 s for admin."),
]
for i, (n, a_, b_) in enumerate(notes):
    txt(84, 925 + i * 30, n, 14, "#2E7D32", weight="bold")
    txt(110, 925 + i * 30, a_, 13.5, "#111", weight="bold")
    txt(470, 925 + i * 30, b_, 12.5, "#444")
A('</svg>')
os.makedirs("renders/electrical", exist_ok=True)
open("renders/electrical/bench_wiring_esp32.svg", "w").write("\n".join(out))
print("[ok]")
