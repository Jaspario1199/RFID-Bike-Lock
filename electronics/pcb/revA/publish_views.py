from pathlib import Path
import json,csv,subprocess,zipfile,sys,re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Circle
import cairosvg
R=Path(__file__).resolve().parent; D=R/'design'; P=R/'previews'
# Recover the standalone project symbol library from the native embedded symbols.
s=(D/'VELOX_carrier_A.kicad_sch').read_text();start=s.index('(lib_symbols'); depth=0; quote=False;escape=False
for i in range(start,len(s)):
    c=s[i]
    if escape:escape=False;continue
    if c=='\\' and quote:escape=True;continue
    if c=='"':quote=not quote
    if not quote:
        if c=='(':depth+=1
        elif c==')':
            depth-=1
            if depth==0: end=i;break
embedded=s[start+len('(lib_symbols'):end].replace('(symbol "VELOX:','(symbol "')
(D/'VELOX.kicad_sym').write_text('(kicad_symbol_lib (version 20220914)(generator kicad_symbol_editor)'+embedded+')')
(D/'sym-lib-table').write_text('(sym_lib_table (lib (name "VELOX")(type "KiCad")(uri "${KIPRJMOD}/VELOX.kicad_sym")(options "")(descr "Project symbols")))\n')
for args in [
 ['sch','export','svg','-o',str(P)+'/',str(D/'VELOX_carrier_A.kicad_sch')],
 ['sch','export','netlist','--format','kicadxml','-o',str(D/'VELOX_carrier_A.xml'),str(D/'VELOX_carrier_A.kicad_sch')],
 ['pcb','export','svg','--layers','F.Cu,F.Silkscreen,Edge.Cuts','--page-size-mode','2','--exclude-drawing-sheet','-o',str(P/'pcb_top.svg'),str(D/'VELOX_carrier_A.kicad_pcb')],
 ['pcb','export','svg','--layers','B.Cu,Edge.Cuts','--page-size-mode','2','--exclude-drawing-sheet','--mirror','-o',str(P/'pcb_bottom.svg'),str(D/'VELOX_carrier_A.kicad_pcb')]]:
    subprocess.run(['kicad-cli']+args,check=True)
for src,dst,w in [('VELOX_carrier_A.svg','schematic.png',2600),('pcb_top.svg','pcb_top.png',1800),('pcb_bottom.svg','pcb_bottom.png',1800)]:
    cairosvg.svg2png(url=str(P/src),write_to=str(P/dst),output_width=w)

fig,ax=plt.subplots(figsize=(13,8),dpi=170);fig.patch.set_facecolor('#f5f7fa');ax.set_facecolor('#f5f7fa')
ax.set_xlim(-4,130);ax.set_ylim(73,-12);ax.set_aspect('equal');ax.axis('off')
ax.add_patch(Rectangle((0,0),110,65,facecolor='#174c43',edgecolor='#102e29',lw=2))
for x,y in [(4,4),(106,4),(4,61),(106,61)]:ax.add_patch(Circle((x,y),1.6,color='#f5f7fa'))
def box(x,y,w,h,txt,color='#b8dcca',size=10):
    ax.add_patch(Rectangle((x,y),w,h,facecolor=color,edgecolor='white',lw=1));ax.text(x+w/2,y+h/2,txt,ha='center',va='center',fontsize=size,color='#102932')
box(6.5,8.5,29,17,'U2 · charger\nUSB on module\nInsulated mount',size=9)
box(4,34.5,36,17,'U3 · boost module\n6 V output to qualify\nInsulated mount',size=9)
box(53.62,4,18,45,'U1\nNano\nESP32\n\nSocketed',color='#b5d7f0',size=10)
ax.text(62.6,2,'USB access',color='white',fontsize=8,ha='center')
box(76.5,4.5,22.4,6.5,'J5 · RFID cable',color='#f4da9c',size=8)
for y,label in [(18,'J6  Wake'),(27,'J7  Cancel'),(36,'J8  Red LED'),(45,'J9  Green LED'),(54,'J10  Buzzer')]:
    box(100.5,y-4.7,7,7,'',color='#f4da9c')
    ax.plot([107.5,112],[y-1.2,y-1.2],color='#40576a',lw=.8)
    ax.text(113,y-1.2,label,fontsize=9,va='center')
box(82,43,11,11,'Q1 / D1\nCoil driver',color='#f3baad',size=7)
box(82,20,18,9,'Q2 / D2\nBuzzer driver',color='#f3baad',size=8)
ax.add_patch(Circle((89.5,36),5,facecolor='#ddd8ee',edgecolor='white'))
ax.text(89.5,36,'C1\nBulk cap',fontsize=8,ha='center',va='center')
box(85.5,55.5,7.4,6,'J4',color='#f4da9c',size=9)
ax.text(89.2,63.5,'Solenoid',ha='center',fontsize=8,color='white')
for x,y,label in [(20.5,4,'J1 Battery'),(48.5,57,'J11 RUN switch')]:
    ax.plot([x-2.5,x+2.5],[y,y],'o',mfc='#e5cc86',mec='white',ms=5)
    ax.text(x,y+4,label,fontsize=8,color='white',ha='center')
box(43,19,9,13,'Battery\nsense',color='#ddd8ee',size=7)
ax.text(44,13,'F1 Fuse',color='white',fontsize=8,ha='center')
ax.add_patch(Rectangle((58,45),11,6,fill=False,edgecolor='#fcbe79',hatch='///'))
ax.text(63.5,53,'Antenna keepout',color='white',fontsize=7,ha='center')
ax.text(0,-8,'VELOX · first carrier PCB layout',fontsize=19,weight='bold',color='#102932')
ax.text(0,-3,'110 × 65 mm · top view · proposed placement, not enclosure fit approval',fontsize=10,color='#40576a')
ax.text(0,69,'REVIEW PROTOTYPE  |  Charging: RUN off  |  Power/module qualification still required',fontsize=10,color='#8a3828',weight='bold')
fig.savefig(P/'layout_map.png',bbox_inches='tight',facecolor=fig.get_facecolor());fig.savefig(P/'layout_map.svg',bbox_inches='tight',facecolor=fig.get_facecolor());plt.close(fig)
parts=json.loads((D/'components.json').read_text())
with (R/'BOM_review.csv').open('w',newline='') as f:
    w=csv.writer(f);w.writerow(['Reference','Value / proposed part','Footprint','Notes'])
    for c in parts:w.writerow([c['ref'],c['value'],c['footprint'],c['note']])
with (R/'pin_map.csv').open('w',newline='') as f:
    w=csv.writer(f);w.writerow(['Reference','Carrier pin','Function','Net'])
    for c in parts:
        for pn,n in c['pins'].items():w.writerow([c['ref'],pn,c['names'].get(pn,''),n or 'NC'])
archive=R/'VELOX_carrier_A_REVIEW_NOT_FOR_FAB.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for f in sorted(R.rglob('*')):
        if f.is_file() and f!=archive and '__pycache__' not in str(f) and f.suffix not in ['.net']:
            z.write(f,'VELOX_carrier_A/'+str(f.relative_to(R)))
print(archive)
