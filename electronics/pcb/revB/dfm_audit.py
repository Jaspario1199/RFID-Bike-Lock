"""Conservative pad-mask spacing audit and manufacturing review export (pcbnew 7)."""
from pathlib import Path
import pcbnew as p
import math,json,hashlib,subprocess
R=Path(__file__).resolve().parent;fn=R/'design/VELOX_carrier_B.kicad_pcb';b=p.LoadBoard(str(fn))
v=json.loads((R/'validation.json').read_text())
assert v['digital_geometry_checks']=='PASS','Native validation must pass before export'
assert v['source_sha256']['design/VELOX_carrier_B.kicad_pcb']==hashlib.sha256(fn.read_bytes()).hexdigest()
def distance(a,c):return math.hypot(max(a[0]-c[2],c[0]-a[2],0),max(a[1]-c[3],c[1]-a[3],0))
mask={}
for layer,name in [(p.F_Mask,'front'),(p.B_Mask,'back')]:
    pads=[]
    for f in b.GetFootprints():
        for d in f.Pads():
            if d.GetLayerSet().Contains(layer):
                q=d.GetBoundingBox();m=p.ToMM(d.GetSolderMaskExpansion())
                pads.append((f.GetReference()+'.'+d.GetNumber(),(p.ToMM(q.GetX())-m,p.ToMM(q.GetY())-m,p.ToMM(q.GetRight())+m,p.ToMM(q.GetBottom())+m)))
    dist,a,c=min((distance(a[1],c[1]),a[0],c[0]) for i,a in enumerate(pads) for c in pads[i+1:])
    assert dist>=.1
    mask[name]={'minimum_pad_opening_gap_lower_bound_mm':round(dist,6),'pair':[a,c]}
ring=[];thermals=[];solid=[]
for f in b.GetFootprints():
    for d in f.Pads():
        if d.GetAttribute()==p.PAD_ATTRIB_PTH:
            s=d.GetSize();h=d.GetDrillSize();ring.append(((min(s.x-h.x,s.y-h.y))/2/1e6,f.GetReference()+'.'+d.GetNumber()))
            if d.GetNetname()=='/GND':(thermals if d.GetZoneConnection()==p.ZONE_CONNECTION_THERMAL else solid).append(f.GetReference()+'.'+d.GetNumber())
assert min(ring)[0]>=.25-1e-6
report={'status':'DFM_REVIEW_NOT_ORDER_RELEASE','board_sha256':hashlib.sha256(fn.read_bytes()).hexdigest(),
'manufacturing_target':'2-layer FR4, 1.6 mm nominal, 1 oz copper, green solder mask; finish to confirm',
'pad_mask_audit':mask,'mask_method':'Axis-aligned copper-pad bounding boxes expanded by effective mask margin; conservative lower bound. Via tenting and full mask-to-copper geometry also require CAM review.',
'minimum_pth_nominal_annular_ring_mm':round(min(ring)[0],6),'limiting_pth_pad':min(ring)[1],
'pth_ground_thermal_pads':thermals,'pth_ground_solid_pads':solid,
'copper_track_count':sum(not isinstance(t,p.PCB_VIA) for t in b.GetTracks()),'via_count':sum(isinstance(t,p.PCB_VIA) for t in b.GetTracks()),
'notes':['Nominal annular ring is not a worst-case drill-registration calculation.','Finished-hole tolerances and actual header fit remain release gates.','No impedance-control or automated-assembly qualification claimed.']}
M=R/'manufacturing_REVIEW_ONLY';M.mkdir(exist_ok=True)
for args in [ ['gerbers','--layers','F.Cu,B.Cu,F.Mask,B.Mask,F.Silkscreen,B.Silkscreen,Edge.Cuts,F.Paste','--subtract-soldermask'],
 ['drill','--excellon-separate-th','--excellon-oval-format','route','--generate-report','--report-path',str(M/'drill_report.txt')]]:
    subprocess.run(['kicad-cli','pcb','export']+args+['-o',str(M)+'/',str(fn)],check=True)
assert len(list(M.glob('*.drl')))==2
report['export_sha256']={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(M.iterdir()) if f.is_file() and f.suffix!='.md'}
(R/'dfm_report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
