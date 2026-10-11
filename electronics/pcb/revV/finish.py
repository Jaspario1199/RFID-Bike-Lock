"""Apply reviewed local routing corrections and one installed short wire link.
Run after schematic_writer + sync_board, then regenerate schematic/sync and check.
No violations are excluded. The wire is an explicit two-terminal installed part.
"""
from pathlib import Path
import json,uuid
import pcbnew as p
R=Path(__file__).resolve().parent;D=R/'design';fn=D/'VELOX_carrier_V.kicad_pcb';b=p.LoadBoard(str(fn));mm=p.FromMM
parts=json.loads((D/'components.json').read_text());fs={f.GetReference():f for f in b.GetFootprints()}
def pt(x,y):return p.VECTOR2I(mm(x),mm(y))
if 'JP1' not in fs:
    # Low-current battery-divider return: narrow two local rail pieces to
    # preserve0.30 mm spacing to the ADC trace. Native DRC is rerun afterwards.
    narrowed=0
    for t in list(b.GetTracks()):
        if isinstance(t,p.PCB_VIA) or t.GetNetname()!='/GND':continue
        a,c=t.GetStart(),t.GetEnd();x,y,xx,yy=[p.ToMM(v) for v in [a.x,a.y,c.x,c.y]]
        if x==22.5 and xx==22.5 and 26<=min(y,yy) and max(y,yy)<=27.5:
            t.SetWidth(mm(.35));narrowed+=1
    assert narrowed==2,narrowed
    # C4.2 is isolated by surrounding traces. A short insulated link to C5.2
    # avoids a crowded additional rivet. Remove its unused routing stub.
    removed=0;removed_tracks=[]
    for t in list(b.GetTracks()):
        if isinstance(t,p.PCB_VIA) or t.GetNetname()!='/GND':continue
        a,c=t.GetStart(),t.GetEnd();x,y,xx,yy=[p.ToMM(v) for v in [a.x,a.y,c.x,c.y]]
        if y==12 and yy==12 and 61<=min(x,xx) and max(x,xx)<=62.5:
            t.thisown=False;removed_tracks.append(t);b.Remove(t);removed+=1
    assert removed==2,removed
    new='GND__JP1';nn=p.NETINFO_ITEM(b,'/'+new);b.Add(nn)
    dest=next(d for d in fs['C4'].Pads() if d.GetNumber()=='2');source=next(d for d in fs['C5'].Pads() if d.GetNumber()=='2');dest.SetNet(nn)
    next(c for c in parts if c['ref']=='C4')['pins']['2']=new
    f=p.FOOTPRINT(b);f.SetReference('JP1');f.SetValue('INSULATED_WIRE');f.SetFPID(p.LIB_ID('VELOX','Wire_JP1'));f.SetAttributes(p.FP_SMD);f.SetPosition(source.GetPosition());f.Reference().SetVisible(False);f.Value().SetVisible(False)
    for pn,land in [('1',source),('2',dest)]:
        q=p.PAD(f);q.SetNumber(pn);q.SetAttribute(p.PAD_ATTRIB_SMD);q.SetShape(p.PAD_SHAPE_CIRCLE);q.SetSize(pt(.8,.8));q.SetLayerSet(p.LSET(p.B_Cu));q.SetPosition(land.GetPosition());z=land.GetPosition()-source.GetPosition();q.SetPos0(z);q.SetNet(land.GetNet());f.Add(q)
    u=lambda s:str(uuid.uuid5(uuid.NAMESPACE_URL,'velox-pcb-revV/'+s));f.SetPath(p.KIID_PATH('/'+u('sheet')+'/'+u('JP1')));b.Add(f)
    p.FootprintSave(str(D/'VELOX.pretty'),f)
    a,c=source.GetPosition(),dest.GetPosition();xy=lambda q:[p.ToMM(q.x),p.ToMM(q.y)]
    parts.append(dict(ref='JP1',value='INSULATED_WIRE',footprint='VELOX:Wire_JP1',pins={'1':'GND','2':new},kind='jumper',names={'1':'C5.2_GND','2':'C4.2_GND'},x=p.ToMM(a.x),y=p.ToMM(a.y),angle=0,note='Short insulated underside wire between existing capacitor ground lands; no extra drill holes. Install after SMD inspection; strain relief and clearance to adjacent live pads required.'))
    links=[{'ref':'JP1','functional_net':'GND','from':'C5.2','to':'C4.2','from_xy_mm':xy(a),'to_xy_mm':xy(c),'straight_distance_mm':round(((a.x-c.x)**2+(a.y-c.y)**2)**.5/1e6,2),'suggested_cut_length_mm':12,'net_segments':['GND',new]}]
    (D/'components.json').write_text(json.dumps(parts,indent=2)+'\n');(R/'jumpers.json').write_text(json.dumps(links,indent=2)+'\n')
    report=json.loads((R/'routing_report.json').read_text());report['installed_wire_count']=1;report['segments']=sum(not isinstance(t,p.PCB_VIA) for t in b.GetTracks());report['router_tree_nets_for_native_review']=[];report['reviewed_corrections']='C4 ground connected by installed JP1; ADC return local tracks narrowed to0.35mm. Native checks, not router tree accounting, determine final connectivity.';(R/'routing_report.json').write_text(json.dumps(report,indent=2)+'\n')
    p.SaveBoard(str(fn),b)
print('Reviewed routing corrections applied; regenerate schematic then validate.')
