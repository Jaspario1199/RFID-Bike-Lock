"""driver_card_diagram.py -> renders/electrical/driver_card.svg/.png

The solenoid driver stage, drawn twice: as a circuit on the left and as the physical parts on
the right, because the failure modes here are orientation mistakes, not topology mistakes.
"""
import os
W, H = 1660, 1010
BG, RED, BLK, BLU, ORG = "#FAFAF8", "#C62828", "#212121", "#1565C0", "#E65100"
out = []; A = out.append
def txt(x, y, t, s=13, c="#333", a="start", w="normal", st="normal"):
    A(f'<text x="{x}" y="{y}" text-anchor="{a}" font-family="DejaVu Sans" font-size="{s}" font-weight="{w}" font-style="{st}" fill="{c}">{t}</text>')
def line(pts, c=BLK, w=3):
    d = " ".join(f"{'M' if i==0 else 'L'} {p[0]} {p[1]}" for i,p in enumerate(pts))
    A(f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>')
def dot(x,y,c=BLK): A(f'<circle cx="{x}" cy="{y}" r="5.5" fill="{c}"/>')
def panel(x,y,w,h,t,sub=""):
    A(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="#FFFFFF" stroke="#CFD8DC" stroke-width="2"/>')
    txt(x+24,y+34,t,20,"#111",w="bold");  txt(x+24,y+56,sub,12.5,"#777")

A(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
A(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
txt(40,48,"SOLENOID DRIVER — stage 5",27,"#111",w="bold")
txt(40,74,"The MOSFET is just a switch the Nano can flip. Gate = the handle · Drain and Source = the two contacts.",14,"#666")

# ---------------- circuit ----------------
panel(40,100,760,700,"THE CIRCUIT","what connects to what")
RY, GY = 210, 690
line([(110,RY),(720,RY)], RED, 4); txt(112,RY-14,"+6 V  (coil supply)",14,RED,w="bold")
line([(110,GY),(720,GY)], BLK, 4); txt(112,GY+26,"GND  — must be shared with the Nano's GND",14,"#333",w="bold")

# coil
CX = 330
line([(CX,RY),(CX,300)], BLK)
A(f'<rect x="{CX-38}" y="300" width="76" height="86" rx="6" fill="#FFEBEE" stroke="#C62828" stroke-width="2.5"/>')
for i in range(4):
    A(f'<path d="M {CX-30} {316+i*18} q 30 -14 60 0" fill="none" stroke="#C62828" stroke-width="2.4"/>')
txt(CX, 404, "SOLENOID", 13, "#C62828", "middle", "bold")
txt(CX, 421, "~6 Ω coil", 11.5, "#888", "middle")
line([(CX,386),(CX,470)], BLK)

# diode across the coil
DX = 480
line([(DX,RY),(DX,300)], BLK)
A(f'<path d="M {DX-16} 348 L {DX+16} 348 L {DX} 318 Z" fill="#37474F"/>')
A(f'<line x1="{DX-18}" y1="318" x2="{DX+18}" y2="318" stroke="#C62828" stroke-width="5"/>')
line([(DX,348),(DX,470)], BLK)
txt(DX+30, 316, "BAND (cathode)", 12.5, RED, w="bold")
txt(DX+30, 333, "→ goes to +6 V", 12, RED)
txt(DX+30, 356, "1N5819", 13, "#111", w="bold")
txt(DX+30, 373, "catches the coil's kick", 11.5, "#777")
line([(CX,470),(DX,470)], BLK); dot(CX,470); dot(DX,470)
line([(CX,RY),(DX,RY)], RED, 4); dot(CX,RY,RED); dot(DX,RY,RED)

# mosfet
MX, MY = 330, 500
A(f'<rect x="{MX-95}" y="{MY}" width="190" height="104" rx="7" fill="#ECEFF1" stroke="#37474F" stroke-width="2.5"/>')
txt(MX,MY+34,"IRLZ44N",17,"#111","middle","bold")
txt(MX,MY+54,"N-channel MOSFET",11.5,"#666","middle")
txt(MX,MY+72,"= a switch the Nano flips",11.5,"#666","middle")
txt(MX+8,MY-8,"D",13,"#111","middle","bold");  txt(MX+30,MY-8,"(drain, + the metal tab)",11,"#777")
txt(MX+8,MY+120,"S",13,"#111","middle","bold"); txt(MX+30,MY+120,"(source)",11,"#777")
txt(MX-104,MY+46,"G",13,"#111","end","bold")
line([(MX,470),(MX,MY)], BLK)
line([(MX,MY+104),(MX,GY)], BLK); dot(MX,GY)
line([(MX-95,MY+52),(MX-150,MY+52)], BLU)

# gate network
A(f'<rect x="{MX-250}" y="{MY+40}" width="60" height="24" rx="3" fill="#FFF" stroke="#37474F" stroke-width="2"/>')
txt(MX-220,MY+57,"100 Ω",11.5,"#111","middle","bold")
line([(MX-250,MY+52),(MX-300,MY+52)], BLU)
txt(MX-306,MY+57,"D5",14,BLU,"end","bold")
line([(MX-190,MY+52),(MX-150,MY+52)], BLU); dot(MX-150,MY+52,BLU)
line([(MX-150,MY+52),(MX-150,GY)], BLU)
A(f'<rect x="{MX-180}" y="{MY+110}" width="60" height="24" rx="3" fill="#FFF" stroke="#37474F" stroke-width="2"/>')
txt(MX-150,MY+127,"100 kΩ",11,"#111","middle","bold")
dot(MX-150,GY)
txt(MX-300,MY+186,"100 Ω limits the switching spike",11.5,"#777")
txt(MX-300,MY+204,"100 kΩ keeps the coil OFF while",11.5,"#777")
txt(MX-300,MY+222,"the board boots",11.5,"#777")

# cap
PX = 640
line([(PX,RY),(PX,400)], RED, 3)
A(f'<line x1="{PX-30}" y1="400" x2="{PX+30}" y2="400" stroke="{BLK}" stroke-width="5"/>')
A(f'<path d="M {PX-30} 424 q 30 18 60 0" fill="none" stroke="{BLK}" stroke-width="5"/>')
line([(PX,424),(PX,GY)], BLK, 3); dot(PX,GY); dot(PX,RY,RED)
txt(PX+22,392,"+",15,RED,w="bold")
txt(PX+26,404,"1000 µF",13,"#111",w="bold")
txt(PX+26,421,"stripe = the − side,",11.5,"#777")
txt(PX+26,437,"goes to GND",11.5,"#777")
txt(PX+26,458,"(add when it arrives)",11,"#999",st="italic")

# ---------------- physical ----------------
panel(840,100,780,700,"THE PARTS, PHYSICALLY","every mistake here is an orientation mistake")
# TO-220
bx,by = 900,190
A(f'<rect x="{bx}" y="{by}" width="86" height="112" rx="5" fill="#212121"/>')
A(f'<rect x="{bx+5}" y="{by-20}" width="76" height="24" rx="3" fill="#9E9E9E"/>')
A(f'<circle cx="{bx+43}" cy="{by-8}" r="7" fill="{BG}"/>')
txt(bx+43,by+62,"IRLZ44N",12,"#FFF","middle","bold")
for i,(nm,col) in enumerate([("G",BLU),("D",RED),("S",BLK)]):
    xx = bx+16+i*26
    A(f'<rect x="{xx}" y="{by+112}" width="9" height="40" fill="#BDBDBD"/>')
    txt(xx+4,by+172,nm,15,col,"middle","bold")
txt(bx,by+200,"printed side toward you, legs down",12,"#555")
txt(bx,by+220,"G → 100 Ω → D5",12.5,BLU,w="bold")
txt(bx,by+240,"D → the solenoid's other wire",12.5,RED,w="bold")
txt(bx,by+260,"S → GND",12.5,"#111",w="bold")
txt(bx,by+286,"⚠ the metal tab IS the drain —",12,"#B71C1C",w="bold")
txt(bx,by+303,"keep it off anything conductive",12,"#B71C1C")
# diode
dx2,dy2 = 1270,215
A(f'<rect x="{dx2}" y="{dy2}" width="96" height="34" rx="5" fill="#37474F"/>')
A(f'<rect x="{dx2+80}" y="{dy2}" width="14" height="34" fill="#EEEEEE"/>')
A(f'<line x1="{dx2-34}" y1="{dy2+17}" x2="{dx2}" y2="{dy2+17}" stroke="#BDBDBD" stroke-width="4"/>')
A(f'<line x1="{dx2+96}" y1="{dy2+17}" x2="{dx2+130}" y2="{dy2+17}" stroke="#BDBDBD" stroke-width="4"/>')
txt(dx2+87,dy2-12,"BAND",12.5,RED,"middle","bold")
A(f'<path d="M {dx2+87} {dy2+44} L {dx2+87} {dy2+64}" stroke="{RED}" stroke-width="2.5"/>')
txt(dx2+87,dy2+82,"this end to +6 V",12.5,RED,"middle","bold")
txt(dx2-34,dy2+120,"1N5819 — sits ACROSS the coil,",12.5,"#111",w="bold")
txt(dx2-34,dy2+138,"in parallel, not in series.",12.5,"#555")
txt(dx2-34,dy2+162,"Backwards = a dead short",12.5,"#B71C1C",w="bold")
txt(dx2-34,dy2+180,"the moment you apply power.",12.5,"#B71C1C")
# checklist
A(f'<rect x="880" y="560" width="700" height="210" rx="8" fill="#E8F5E9" stroke="#2E7D32" stroke-width="2"/>')
txt(904,596,"BEFORE YOU APPLY POWER",16,"#111",w="bold")
ck = ["Measure the coil: ~6 Ω confirms the 6 V 1 A winding.",
      "Diode-test the IRLZ44N to confirm G–D–S, don't trust the picture.",
      "Diode band toward +6 V. Check it twice; there is no warning if it's wrong.",
      "Coil on a SEPARATE 6 V supply for the first test (no reservoir cap yet).",
      "Tie that supply's GND to the Nano's GND, or nothing switches."]
for i,t in enumerate(ck):
    txt(908,626+i*27,"☐",14,"#2E7D32",w="bold"); txt(934,626+i*27,t,13,"#333")
# footer
A(f'<rect x="40" y="828" width="1580" height="150" rx="9" fill="#FFF8E1" stroke="#F57F17" stroke-width="2"/>')
txt(64,862,"WHY THE DIODE IS THERE",16,"#111",w="bold")
for i,t in enumerate([
  "A solenoid is a coil of wire, and a coil hates having its current stopped. The instant the MOSFET switches off, the collapsing",
  "magnetic field drives the voltage at the drain to hundreds of volts trying to keep the current going — enough to destroy the MOSFET.",
  "The 1N5819 gives that current a harmless loop back to +6 V instead. It does nothing at all while the solenoid is firing; it only",
  "matters in the microseconds after switch-off. That is also why it must sit right at the coil, not at the far end of long wires."]):
    txt(64,890+i*22,t,13,"#444")
A('</svg>')
os.makedirs("renders/electrical", exist_ok=True)
open("renders/electrical/driver_card.svg","w").write("\n".join(out))
print("ok")
