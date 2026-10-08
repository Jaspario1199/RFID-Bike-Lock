"""Apply Rev B commercial-fabrication / hand-assembly refinements.
Run on an already routed board, then validate.py. Uses pcbnew 7.
"""
from pathlib import Path
import sys, math, json
sys.path.append('/usr/lib/python3/dist-packages')
import pcbnew as p
R=Path(__file__).resolve().parent; D=R/'design'; fn=D/'VELOX_carrier_B.kicad_pcb'
b=p.LoadBoard(str(fn)); mm=p.FromMM
def pt(x,y):return p.VECTOR2I(mm(x),mm(y))
fs={f.GetReference():f for f in b.GetFootprints()}
# More copper around the PH connector holes, retaining JST library hole sizes.
for pad in fs['J6'].Pads():pad.SetSize(pt(1.35,1.8))
# PTH ground joints get reliefs; SMT devices and vias retain solid connections.
for f in b.GetFootprints():
    for pad in f.Pads():
        if pad.GetAttribute()==p.PAD_ATTRIB_PTH and pad.GetNetname()=='/GND':
            pad.SetZoneConnection(p.ZONE_CONNECTION_THERMAL)
            pad.SetThermalGap(mm(.25));pad.SetThermalSpokeWidth(mm(.4))
            pad.SetThermalSpokeAngle(p.EDA_ANGLE(45,p.DEGREES_T))
# These two pads have obstructed front-layer thermal spokes; retain robust solid
# ground connections rather than accepting starved reliefs. Preheat for soldering.
for ref,pn in [('J6','1'),('U4','2')]:
    next(d for d in fs[ref].Pads() if d.GetNumber()==pn).SetZoneConnection(p.ZONE_CONNECTION_FULL)
# Keep all copper out of a 6.6 mm diameter conductive screw/washer envelope.
existing_zones={z.GetZoneName() for z in b.Zones()}
for ref in ['H1','H2','H3','H4']:
    if 'DFM_M3_'+ref in existing_zones:continue
    c=fs[ref].GetPosition();cx=p.ToMM(c.x);cy=p.ToMM(c.y)
    z=p.ZONE(b);z.SetIsRuleArea(True);z.SetZoneName('DFM_M3_'+ref)
    layers=p.LSET(p.F_Cu);layers.AddLayer(p.B_Cu);z.SetLayerSet(layers)
    z.SetDoNotAllowTracks(True);z.SetDoNotAllowVias(True);z.SetDoNotAllowCopperPour(True);z.SetDoNotAllowPads(False)
    poly=z.Outline();poly.NewOutline()
    for i in range(64):
        a=i*2*math.pi/64;poly.Append(mm(cx+3.3*math.cos(a)),mm(cy+3.3*math.sin(a)))
    b.Add(z)
# Fabricator-recommended minimum silkscreen line width.
for f in b.GetFootprints():
    for g in f.GraphicalItems():
        if not isinstance(g,p.FP_TEXT) and g.GetLayer() in [p.F_SilkS,p.B_SilkS]:g.SetWidth(max(g.GetWidth(),mm(.15)))
# Standard 1 mm / 0.15 mm text. Place references without covering pad openings.
texts=[]
for f in b.GetFootprints():
    if f.Reference().IsVisible():texts.append(f.Reference())
    for g in f.GraphicalItems():
        if isinstance(g,p.FP_TEXT) and g.IsVisible() and g.GetLayer() in [p.F_SilkS,p.B_SilkS]:texts.append(g)
for g in b.GetDrawings():
    if isinstance(g,p.PCB_TEXT) and g.GetLayer() in [p.F_SilkS,p.B_SilkS]:texts.append(g)
def bbox(obj,extra=0):
    v=obj.GetBoundingBox();return (p.ToMM(v.GetX())-extra,p.ToMM(v.GetY())-extra,p.ToMM(v.GetRight())+extra,p.ToMM(v.GetBottom())+extra)
def overlap(a,c):return a[0]<c[2] and a[2]>c[0] and a[1]<c[3] and a[3]>c[1]
padboxes=[bbox(d,.2) for f in b.GetFootprints() for d in f.Pads()]
graphics=[bbox(g,.17) for f in b.GetFootprints() for g in f.GraphicalItems() if not isinstance(g,p.FP_TEXT) and g.GetLayer()==p.F_SilkS]
anchors_file=R/'dfm_text_anchors.json'
anchors=json.loads(anchors_file.read_text()) if anchors_file.exists() else {}
placed=[];moves=[]
for t in sorted(texts,key=lambda t:(not isinstance(t,p.PCB_TEXT),-len(t.GetText()))):
    old=t.GetPosition();key=str(t.m_Uuid.AsString());ox,oy=anchors.setdefault(key,[p.ToMM(old.x),p.ToMM(old.y)])
    t.SetTextSize(pt(1,1));t.SetTextThickness(mm(.15));t.SetTextAngle(p.EDA_ANGLE(0,p.DEGREES_T))
    offsets=[(0,0)]+sorted([(x*.5,y*.5) for x in range(-16,17) for y in range(-16,17) if x or y],key=lambda xy:xy[0]**2+xy[1]**2)
    for dx,dy in offsets:
        t.SetPosition(pt(ox+dx,oy+dy));bb=bbox(t,.12)
        if bb[0]<.5 or bb[1]<.5 or bb[2]>89.5 or bb[3]>54.5:continue
        if any(overlap(bb,x) for x in padboxes+placed+graphics):continue
        placed.append(bb);moves.append({'text':t.GetText(),'xy_mm':[ox+dx,oy+dy]});break
    else:raise RuntimeError('No clear text position for '+t.GetText())
# Keep library pad/thermal geometry synchronized; field positions are board-specific.
for f in b.GetFootprints():p.FootprintSave(str(D/'VELOX.pretty'),f)
b.GetDesignSettings().m_HoleClearance=mm(.28)
b.GetDesignSettings().m_SolderMaskExpansion=0
b.GetDesignSettings().m_SolderMaskMinWidth=mm(.1)
p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(fn),b)
anchors_file.write_text(json.dumps(anchors,indent=2)+'\n')
(R/'dfm_text_positions.json').write_text(json.dumps(moves,indent=2)+'\n')
print('Applied DFM pad/thermal/mounting/text changes; run native checks next.')
