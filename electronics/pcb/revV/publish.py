"""Export native design views, assembly map, fit references and review archives."""
from pathlib import Path
import json,subprocess,csv,zipfile,hashlib,math
import pcbnew as p
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Circle
import cadquery as cq
import cairosvg
R=Path(__file__).resolve().parent;D=R/'design';P=R/'previews';M=R/'manufacturing_REVIEW_ONLY';O=R/'mechanical'
for x in [P,M,O]:x.mkdir(exist_ok=True)
v=json.loads((R/'validation.json').read_text());assert v['digital_checks']=='PASS'
fn=D/'VELOX_carrier_V.kicad_pcb';b=p.LoadBoard(str(fn));parts=json.loads((D/'components.json').read_text());links=json.loads((R/'jumpers.json').read_text())
assert hashlib.sha256(fn.read_bytes()).hexdigest()==v['source_sha256']['design/VELOX_carrier_V.kicad_pcb']
subprocess.run(['kicad-cli','sch','export','svg','-o',str(P)+'/',str(D/'VELOX_carrier_V.kicad_sch')],check=True)
cairosvg.svg2png(url=str(P/'VELOX_carrier_V.svg'),write_to=str(P/'schematic.png'),output_width=6000,background_color='white')
for name,layers in [('ink_top','F.Cu,Edge.Cuts'),('ink_bottom','B.Cu,Edge.Cuts'),('assembly_bottom','B.Cu,B.Fab,B.Silkscreen,Edge.Cuts'),('assembly_top','F.Fab,F.Silkscreen,Edge.Cuts')]:
 subprocess.run(['kicad-cli','pcb','export','svg','--mode-single','--page-size-mode','2','--exclude-drawing-sheet','--black-and-white',*(['--mirror'] if name.endswith('bottom') else []),'--layers',layers,'-o',str(P/(name+'.svg')),str(fn)],check=True)
 cairosvg.svg2png(url=str(P/(name+'.svg')),write_to=str(P/(name+'.png')),output_width=1800,background_color='white')
subprocess.run(['kicad-cli','pcb','export','gerbers','--layers','F.Cu,B.Cu,Edge.Cuts','-o',str(M)+'/',str(fn)],check=True)
subprocess.run(['kicad-cli','pcb','export','drill','--excellon-units','mm','--excellon-oval-format','route','--generate-report','--report-path',str(M/'drill_report.txt'),'-o',str(M)+'/',str(fn)],check=True)
# FEDC requests .GKO outline. Keep separate from ink layer.
outline=M/'VELOX_carrier_V-Edge_Cuts.gm1';outline.rename(M/'VELOX_carrier_V-outline.gko')
job=M/'VELOX_carrier_V-job.gbrjob'
if job.exists():job.write_text(job.read_text().replace('VELOX_carrier_V-Edge_Cuts.gm1','VELOX_carrier_V-outline.gko'))
# No production plating: explicitly tell technician the combined file is mechanical holes only.
(M/'READ_ME_FIRST.md').write_text('FEDC V-One REVIEW ONLY. Top ink .gtl + bottom ink .gbl + separate outline .gko + mechanical drill .drl. Copper rivets connect layers; no chemical plating, solder mask or printed silkscreen. Drill diameters0.7mm for small rivets and1.6mm for header rivets/mount pilots. Mount holes are pilots; hand finish four centers to3.2mm. Header holes accept stock large copper rivets, not chemical plating. See README.md and SYSTEM_WIRING.md in the full package; qualify coupon, stock rivet fit, ink/solder process and external power first. Do not mirror the GBL manually: Voltera handles bottom-file mirroring.\n')
with (R/'rivet_map.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['ID','Type','x mm','y mm','Drill mm','Land diameter mm','Net'])
 for i,t in enumerate([t for t in b.GetTracks() if isinstance(t,p.PCB_VIA)],1):
  q=t.GetPosition();w.writerow(['V'+str(i),'small copper rivet',p.ToMM(q.x),p.ToMM(q.y),p.ToMM(t.GetDrill()),p.ToMM(t.GetWidth()),t.GetNetname()])
 for fp in b.GetFootprints():
  for d in fp.Pads():
   if d.GetAttribute()==p.PAD_ATTRIB_PTH:
    q=d.GetPosition();w.writerow([fp.GetReference()+'.'+d.GetNumber(),'large copper rivet',p.ToMM(q.x),p.ToMM(q.y),1.6,2.24,d.GetNetname()])
# No change in mounting centers; fit-gauge holes are final hand-finished diameter.
board=cq.Workplane('XY').box(90,55,1.6,centered=(False,False,False))
for x,y in [(4,4),(86,4),(4,51),(86,51)]:board=board.cut(cq.Workplane('XY',origin=(x,y,-.1)).circle(1.6).extrude(1.8))
cq.exporters.export(board,str(O/'PCB_FINAL_HOLE_fit_gauge.step'));cq.exporters.export(board,str(O/'PCB_FINAL_HOLE_fit_gauge.stl'))
a=cq.Assembly(name='REV_V_ENVELOPES_ONLY');a.add(board.val(),name='board',color=cq.Color(.1,.5,.3))
envelopes={'board':[0,90,0,55,0,1.6],'underside_reserved':[0,90,0,55,-3,0]}
for ref,c in [(c['ref'],c) for c in parts if c['kind'] not in ['hole','jumper']]:
 f=next(f for f in b.GetFootprints() if f.GetReference()==ref);q=f.GetBoundingBox(False,False)
 if ref=='U1':bbox=[37.62,55.62,4,49,1.6,15.6]
 elif ref.startswith('J'):
  bbox=[c['x']-2,c['x']+2,c['y']-1.5,c['y']+(len(c['pins'])-1)*2.54+1.5,1.6,11.6]
 else:bbox=[p.ToMM(q.GetX()),p.ToMM(q.GetRight()),p.ToMM(q.GetY()),p.ToMM(q.GetBottom()),-2.6 if ref=='D2' else -1.5,0]
 envelopes[ref]=bbox;x0,x1,y0,y1,z0,z1=bbox
 solid=cq.Workplane('XY').box(x1-x0,y1-y0,z1-z0,centered=(False,False,False)).translate((x0,y0,z0)).val();a.add(solid,name=ref,color=cq.Color(.3,.5,.7))
a.save(str(O/'carrier_ENVELOPES_ONLY.step'))
(O/'envelope_review.json').write_text(json.dumps({'status':'ENVELOPES_ONLY_NO_INSTALLATION_APPROVAL','envelopes_mm':envelopes,'underside_gap_proposal_mm':4,'underside_reserved_mm':3,'global_board_origin_from_RevB_proposal_mm':[11,35.5,42],'mount_centers_mm':[[4,4],[86,4],[4,51],[86,51]],'final_M3_hole_mm':3.2,'drill_pilot_mm':1.6,'outstanding':'Socket/header heights, wire-crossing stack and bend radius, external driver/regulator/charger retention and full installation must be physically checked.'},indent=2)+'\n')
# Top-view assembly coordinates with underside wires seen through the board.
fig,ax=plt.subplots(figsize=(14,8),dpi=180);ax.set_aspect('equal');ax.set_xlim(-3,94);ax.set_ylim(62,-4);ax.axis('off');fig.patch.set_facecolor('#f6f8fa');ax.add_patch(Rectangle((0,0),90,55,fc='#e3efe8',ec='#314c41',lw=1.5))
for x,y in [(4,4),(86,4),(4,51),(86,51)]:ax.add_patch(Circle((x,y),1.6,fc='white',ec='#314c41'))
for c in parts:
 if c['kind'] in ['hole','jumper']:continue
 f=next(f for f in b.GetFootprints() if f.GetReference()==c['ref'])
 for pad in f.Pads():
  z=pad.GetPosition();ax.add_patch(Circle((p.ToMM(z.x),p.ToMM(z.y)),.6,fc='#536e60'))
 ax.text(c['x'],c['y']-2,c['ref'],fontsize=8,color='#263c31',ha='center')
colors=plt.get_cmap('tab20')
for i,j in enumerate(links):
 x,y=j['from_xy_mm'];xx,yy=j['to_xy_mm'];col=colors(i%20);ax.plot([x,xx],[y,yy],lw=1.5,color=col,alpha=.8);ax.text((x+xx)/2+2,(y+yy)/2-1,j['ref'],fontsize=7,color=col,bbox={'facecolor':'white','edgecolor':'none','pad':1})
ax.text(0,-2,'Rev V: component positions · TOP VIEW',fontsize=12,weight='bold');ax.text(0,58,'Riveted two-sided prototype; install the one short insulated JP1 link between C5.2 and C4.2. Confirm 4 mm underside gap with the real assembly.',fontsize=9)
fig.savefig(P/'wire_map.png',bbox_inches='tight');plt.close(fig)
with (R/'jumpers.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['Wire','Functional net','From existing land','To existing land','Starting cut length mm','Routing note'])
 for j in links:w.writerow([j['ref'],j['functional_net'],j['from'],j['to'],j['suggested_cut_length_mm'],'Insulated wire on underside; trim after routing; secure against solder-joint loading'])
with (R/'pin_map.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['Reference','Pin','Function','Board segment net'])
 for c in parts:
  for pn,n in c['pins'].items():w.writerow([c['ref'],pn,c['names'].get(pn,''),n or 'NC'])
with (R/'BOM_review.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['Reference','Value','Footprint','Qualification'])
 for c in parts:
  if c['kind']=='hole':continue
  w.writerow([c['ref'],c['value'],c['footprint'],'Exact MPN/rating and solder process to qualify; wire cut lengths and header/socket stack to verify' if c['ref']!='U1' else 'ABX00083 only; socket stack to measure'])
# Resistance/adhesion coupon: 3 isolated 20 mm center-to-center traces and pads.
cb=p.BOARD();cb.SetCopperLayerCount(2)
for i,width in enumerate([.35,.6,1.0]):
 y=5+i*6;t=p.PCB_TRACK(cb);t.SetStart(p.VECTOR2I(p.FromMM(5),p.FromMM(y)));t.SetEnd(p.VECTOR2I(p.FromMM(25),p.FromMM(y)));t.SetWidth(p.FromMM(width));t.SetLayer(p.B_Cu);cb.Add(t)
 for x in [5,25]:
  f=p.FOOTPRINT(cb);d=p.PAD(f);d.SetNumber('1');d.SetSize(p.VECTOR2I(p.FromMM(3),p.FromMM(3)));d.SetShape(p.PAD_SHAPE_CIRCLE);d.SetAttribute(p.PAD_ATTRIB_SMD);d.SetLayerSet(p.LSET(p.B_Cu));d.SetPosition(p.VECTOR2I(p.FromMM(x),p.FromMM(y)));f.Add(d);cb.Add(f)
for x,y,xx,yy in [(0,0,30,0),(30,0,30,30),(30,30,0,30),(0,30,0,0)]:
 s=p.PCB_SHAPE();s.SetShape(p.SHAPE_T_SEGMENT);s.SetStart(p.VECTOR2I(p.FromMM(x),p.FromMM(y)));s.SetEnd(p.VECTOR2I(p.FromMM(xx),p.FromMM(yy)));s.SetWidth(p.FromMM(.05));s.SetLayer(p.Edge_Cuts);cb.Add(s)
# Actual stock fit coupon: three large-rivet lands at 2.54 pitch,
# plus two small-rivet lands; no connections between adjacent lands.
for i,(x,drill,diam) in enumerate([(5,1.6,2.24),(7.54,1.6,2.24),(10.08,1.6,2.24),(20,.7,1.3),(25,.7,1.3)]):
 f=p.FOOTPRINT(cb);f.SetPosition(p.VECTOR2I(p.FromMM(x),p.FromMM(25)))
 d=p.PAD(f);d.SetNumber('1');d.SetSize(p.VECTOR2I(p.FromMM(diam),p.FromMM(diam)));d.SetDrillSize(p.VECTOR2I(p.FromMM(drill),p.FromMM(drill)));d.SetShape(p.PAD_SHAPE_CIRCLE);d.SetAttribute(p.PAD_ATTRIB_PTH);d.SetLayerSet(p.LSET.AllCuMask());d.SetPosition(f.GetPosition());d.SetPos0(p.VECTOR2I(0,0));f.Add(d);cb.Add(f)
p.SaveBoard(str(M/'process_coupon.kicad_pcb'),cb)
subprocess.run(['kicad-cli','pcb','export','gerbers','--layers','F.Cu,B.Cu,Edge.Cuts','-o',str(M)+'/',str(M/'process_coupon.kicad_pcb')],check=True)
subprocess.run(['kicad-cli','pcb','export','drill','--excellon-units','mm','-o',str(M)+'/',str(M/'process_coupon.kicad_pcb')],check=True)
(M/'COUPON.md').write_text('Print coupon FIRST, separate from carrier. 30x30mm, five mechanical holes (three1.6mm, two0.7mm). At y25, three large-rivet lands at x5/7.54/10.08 qualify header pitch; two small-rivet lands at x20/25 qualify interlayer riveting. Top-view y5:0.35mm; y11:0.60mm; y17:1.00mm width. Each trace has20mm pad-center distance and3mm terminal pads. Measure with compensated leads or four-wire measurement; pad resistance makes this a process comparison, not an exact sheet-resistance metrology structure. Inspect spacing, continuity, solder wetting and adhesion with the actual ink/cure/solder settings. Also qualify a sample large rivet/header joint on the real substrate thickness before committing the carrier. Document actual measured resistance/current temperature rise; no guaranteed current rating is inferred from the coupon.\n')
exports={str(f.relative_to(R)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(M.iterdir()) if f.is_file()}
(R/'export_manifest.json').write_text(json.dumps(exports,indent=2)+'\n')
with zipfile.ZipFile(R/'FEDC_REVIEW_ONLY.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in sorted(M.iterdir()):
  if f.is_file():z.write(f,'manufacturing_REVIEW_ONLY/'+f.name)
 for name in ['README.md','SYSTEM_WIRING.md','validation.json','jumpers.csv','rivet_map.csv','previews/wire_map.png']:z.write(R/name,name)
assert (R/'FEDC_REVIEW_ONLY.zip').stat().st_size<5_000_000
archive=R/'VELOX_RevV_Voltera_REVIEW.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for f in sorted(R.rglob('*')):
  if f.is_file() and f!=archive and '__pycache__' not in str(f) and f.suffix not in ['.kicad_prl','.prl','.bak']:z.write(f,'VELOX_RevV/'+str(f.relative_to(R)))
print('Published',archive)
