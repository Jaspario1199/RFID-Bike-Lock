"""Publish exact KiCad views, annotated placement, connector tables and review ZIP."""
from pathlib import Path
import json,csv,subprocess,zipfile,sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Circle,FancyArrowPatch
import cairosvg
R=Path(__file__).resolve().parent;D=R/'design';P=R/'previews'
for args in [
 ['sch','export','svg','-o',str(P)+'/',str(D/'VELOX_carrier_B.kicad_sch')],
 ['sch','export','netlist','--format','kicadxml','-o',str(D/'VELOX_carrier_B.xml'),str(D/'VELOX_carrier_B.kicad_sch')],
 ['pcb','export','svg','--layers','F.Cu,F.Silkscreen,Edge.Cuts','--page-size-mode','2','--exclude-drawing-sheet','-o',str(P/'pcb_top.svg'),str(D/'VELOX_carrier_B.kicad_pcb')],
 ['pcb','export','svg','--layers','B.Cu,Edge.Cuts','--page-size-mode','2','--exclude-drawing-sheet','--mirror','-o',str(P/'pcb_bottom.svg'),str(D/'VELOX_carrier_B.kicad_pcb')]]:
    subprocess.run(['kicad-cli']+args,check=True)
for src,dst,w in [('VELOX_carrier_B.svg','schematic.png',6000),('pcb_top.svg','pcb_top.png',2200),('pcb_bottom.svg','pcb_bottom.png',2200)]:
    cairosvg.svg2png(url=str(P/src),write_to=str(P/dst),output_width=w)

parts=json.loads((D/'components.json').read_text())
fig,ax=plt.subplots(figsize=(12,8),dpi=180);fig.patch.set_facecolor('#f5f7fa');ax.set_facecolor('#f5f7fa')
ax.set_xlim(-4,118);ax.set_ylim(63,-11);ax.set_aspect('equal');ax.axis('off')
ax.add_patch(Rectangle((0,0),90,55,facecolor='#174c43',edgecolor='#102e29',lw=2))
for x,y in [(4,4),(86,4),(4,51),(86,51)]:ax.add_patch(Circle((x,y),1.6,color='#f5f7fa'))
def box(x,y,w,h,txt,color='#b8dcca',size=9):
    ax.add_patch(Rectangle((x,y),w,h,facecolor=color,edgecolor='white',lw=1));ax.text(x+w/2,y+h/2,txt,ha='center',va='center',fontsize=size,color='#102932')
box(37.62,4,18,45,'U1\nNano\nESP32\n\nSocketed',color='#b5d7f0',size=10)
box(15.95,14.45,8.1,13.1,'U4\n7.5 V\nNano VIN',color='#b5d7f0',size=7)
box(57.4,29.4,15.2,15.2,'U3\n6 V coil\nPololu 4013',size=8)
box(58.5,3.5,22.4,7,'J5 · RFID / XH8',color='#f4da9c',size=8)
box(62.05,15.3,17.9,4.5,'J6 · Panel / PH8',color='#f4da9c',size=7)
box(5.5,39.8,28.5,13.5,'USB-C charge only\nU2 charger + U5 input protection\n100 mA · RUN off',color='#d8cbea',size=7)
box(28.7,19.5,7.4,11.5,'A0\nBattery\nsense',color='#ddd8ee',size=6)
box(75,32.5,9,7,'Q1\nCoil FET',color='#f3baad',size=7)
box(56.3,20,14.8,7.5,'Q2 / D2\nBuzzer driver',color='#f3baad',size=7)
ax.add_patch(Circle((82.75,27),4,facecolor='#ddd8ee',edgecolor='white'));ax.text(82.75,27,'C1\n470µF',fontsize=7,ha='center',va='center')
ax.add_patch(Circle((64,50),2.5,facecolor='#ddd8ee',edgecolor='white'));ax.text(64,50,'C8',fontsize=7,ha='center',va='center')
box(81.5,38.5,6.5,7.7,'J4',color='#f4da9c',size=9)
box(73.6,47.2,8.8,3.6,'D1 flyback',color='#f3baad',size=6)
for x,y,label in [(13.5,4,'J1 Battery'),(31.5,6,'J2 RUN switch')]:
    ax.plot([x-2.5,x+2.5],[y,y],'o',mfc='#e5cc86',mec='white',ms=4);ax.text(x,y+3,label,fontsize=7,color='white',ha='center')
ax.text(12,12.8,'F1 fuse',color='white',fontsize=7,ha='center')
ax.add_patch(Rectangle((42,45),12,9,fill=False,edgecolor='#fcbe79',hatch='///'));ax.text(48,51,'RF\nkeepout',fontsize=7,color='white',ha='center')
for x,y,label in [(81,7,'RFID harness'),(80,17,'One panel harness'),(88,43,'Solenoid')]:
    ax.plot([x,94],[y,y],color='#40576a',lw=.8);ax.text(95,y,label,fontsize=8,va='center',color='#40576a')
ax.text(0,-7,'VELOX · compact carrier Rev B',fontsize=19,weight='bold',color='#102932')
ax.text(0,-2,'90 × 55 mm · 30.8% less area than Rev A · top view',fontsize=10,color='#40576a')
ax.text(0,60,'ENGINEERING PROTOTYPE · Battery/coil ratings and enclosure changes remain release gates',fontsize=9,color='#8a3828',weight='bold')
fig.savefig(P/'layout_map.png',bbox_inches='tight',facecolor=fig.get_facecolor());fig.savefig(P/'layout_map.svg',bbox_inches='tight',facecolor=fig.get_facecolor());plt.close(fig)

fig,ax=plt.subplots(figsize=(12,6),dpi=180);ax.set_xlim(0,12);ax.set_ylim(0,6);ax.axis('off');fig.patch.set_facecolor('#f5f7fa')
nodes={'usb':(.3,3.6,2,1,'USB-C 5 V\nNCP361 input protection'),
 'charge':(3,3.6,2.2,1,'MCP73831 charger\n100 mA · RUN off'),
 'bat':(3,.7,2.2,1,'Protected 1S cell\nF1 + RUN switch'),
 'nano':(6,2.1,2.3,1,'7.5 V boost\nNano VIN → 3V3'),
 'coil':(6,.3,2.3,1,'6 V boost\nSolenoid + AO3400A'),
 'panel':(9,2.1,2.6,1,'RC522 / LEDs / buzzer\nWake + cancel buttons')}
for key,(x,y,w,h,label) in nodes.items():
    ax.add_patch(Rectangle((x,y),w,h,facecolor='#bddaca' if key in ['bat','coil'] else '#c5dded',edgecolor='#536f7f',lw=1.2));ax.text(x+w/2,y+h/2,label,ha='center',va='center',fontsize=10)
for a,b in [('usb','charge'),('charge','bat'),('bat','nano'),('bat','coil'),('nano','panel')]:
    x,y,w,h,_=nodes[a];xx,yy,ww,hh,_=nodes[b]
    start=(x+w,y+h/2);end=(xx,yy+hh/2)
    if a=='charge':start=(x+w/2,y);end=(xx+ww/2,yy+hh)
    ax.add_patch(FancyArrowPatch(start,end,arrowstyle='-|>',mutation_scale=15,color='#536f7f',lw=1.5))
ax.text(.3,5.55,'VELOX Rev B · electrical map',fontsize=18,weight='bold',color='#203642')
ax.text(.3,5.1,'Separate coil and Nano regulators share one protected battery. This is not a power-path charger.',fontsize=10,color='#516879')
ax.text(.3,.08,'Native ERC/DRC passed. Confirm real cell/coil ratings, charging thermal behavior and physical installation before fabrication.',fontsize=9,color='#8a3828')
fig.savefig(P/'power_map.png',bbox_inches='tight');plt.close(fig)

selected={'U1':'Arduino ABX00083','U2':'Microchip MCP73831-2ATI/OT','U3':'Pololu4013 U3V40F6','U4':'Pololu4943 U3V16F7','U5':'onsemi NCP361SNT1G',
 'Q1':'AOS AO3400A','Q2':'AOS AO3400A','C1':'Panasonic EEUFR1A471','C8':'Panasonic EEUFR1A101',
 'J3':'GCT USB4125-GF-A','J4':'JST B2B-XH-A','J5':'JST B8B-XH-A','J6':'JST B8B-PH-K-S',
 'D1':'SS34 SMA, qualify manufacturer','D2':'SS14 SMA, qualify manufacturer','F1':'Littelfuse0467003.NR candidate'}
with (R/'BOM_review.csv').open('w',newline='') as f:
    w=csv.writer(f);w.writerow(['Reference','Value','Selected part / candidate','Footprint','Release status','Notes'])
    for c in parts:
        if c['kind'] in ['test','hole']:continue
        status='MPN / operating qualification open' if c['ref'] in ['F1','C2','C3','C4','C5','C6','C9','C10','C11','J1','J2','U1'] else 'Selected interface; physical prototype qualification open'
        w.writerow([c['ref'],c['value'],selected.get(c['ref'],'Select exact tolerance/rating-compatible part'),c['footprint'],status,c['note']])
with (R/'pin_map.csv').open('w',newline='') as f:
    w=csv.writer(f);w.writerow(['Reference','Carrier pin','Function','Net'])
    for c in parts:
        for pn,n in c['pins'].items():w.writerow([c['ref'],pn,c['names'].get(pn,''),n or 'NC'])
if '--views-only' in sys.argv:sys.exit(0)
archive=R/'VELOX_carrier_B_REVIEW_NOT_FOR_FAB.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for f in sorted(R.rglob('*')):
        if f.is_file() and f!=archive and '__pycache__' not in str(f) and f.suffix not in ['.prl','.kicad_prl','.bak']:
            z.write(f,'VELOX_carrier_B/'+str(f.relative_to(R)))
print(archive)
