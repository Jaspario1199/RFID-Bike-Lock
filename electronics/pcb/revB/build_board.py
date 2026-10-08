"""Build the UNROUTED Rev B placement in KiCad 7+.
This script has not run after workspace loss. Native ERC/DRC and routing remain required.
Requires pcbnew and official KiCad footprint libraries, including USB4125.
"""
from pathlib import Path
import os, sys, json, uuid
sys.path.append('/usr/lib/python3/dist-packages')
import pcbnew as p
ROOT=Path(__file__).resolve().parent
D=ROOT/'design'; D.mkdir(exist_ok=True)
LOCAL=D/'VELOX.pretty'; LOCAL.mkdir(exist_ok=True)
parts=json.loads((ROOT/'design_spec.json').read_text())['parts']
LIB=Path(os.environ.get('VELOX_KICAD_FOOTPRINT_DIR','/usr/share/kicad/footprints'))
def mm(v): return p.FromMM(float(v))
def pt(x,y): return p.VECTOR2I(mm(x),mm(y))
board=p.BOARD(); board.SetCopperLayerCount(2)
board.GetDesignSettings().SetBoardThickness(mm(1.6))
nets={}
def uid(s):
    a=2166136261;h=[]
    for j in range(4):
        for ch in 'velox-revB-'+str(j)+s:a=((a^ord(ch))*16777619)&0xffffffff
        h.append(format(a,'08x'))
    v=''.join(h)
    return v[:8]+'-'+v[8:12]+'-5'+v[13:16]+'-a'+v[17:20]+'-'+v[20:]
def net(name):
    if name not in nets:
        n=p.NETINFO_ITEM(board,'/'+name);board.Add(n);nets[name]=n
    return nets[name]
def layers():
    v=p.LSET.AllCuMask();v.AddLayer(p.F_Mask);v.AddLayer(p.B_Mask);return v
def fline(f,x0,y0,x1,y1,layer,width):
    s=p.FP_SHAPE(f);s.SetShape(p.SHAPE_T_SEGMENT)
    s.SetStart(pt(x0,y0));s.SetEnd(pt(x1,y1))
    s.SetStart0(pt(x0,y0));s.SetEnd0(pt(x1,y1))
    s.SetLayer(layer);s.SetWidth(mm(width));f.Add(s)
def frect(f,body,layer,width):
    x0,y0,x1,y1=body
    for a,b in [((x0,y0),(x1,y0)),((x1,y0),(x1,y1)),((x1,y1),(x0,y1)),((x0,y1),(x0,y0))]:fline(f,*a,*b,layer,width)
def custom(c):
    f=p.FOOTPRINT(board);s=c['custom']
    f.SetFPID(p.LIB_ID('VELOX',c['footprint_name']))
    for num,x,y in s['pads']:
        pad=p.PAD(f);pad.SetNumber(str(num));pad.SetPosition(pt(x,y));pad.SetPos0(pt(x,y))
        pad.SetSize(pt(s['pad_mm'],s['pad_mm']));pad.SetDrillSize(pt(s['drill_mm'],s['drill_mm']))
        pad.SetAttribute(p.PAD_ATTRIB_PTH)
        pad.SetShape(p.PAD_SHAPE_RECT if str(num)=='1' else p.PAD_SHAPE_CIRCLE)
        pad.SetLayerSet(layers());f.Add(pad)
    if s['body']:
        frect(f,s['body'],p.F_Fab,.1)
        x0,y0,x1,y1=s['body'];frect(f,[x0-.25,y0-.25,x1+.25,y1+.25],p.F_CrtYd,.05)
    return f
for c in parts:
    if c['custom']: f=custom(c)
    else:
        name=c['footprint_name'];local=LOCAL/(name+'.kicad_mod')
        lib=LOCAL if local.exists() else LIB/(c['library']+'.pretty')
        f=p.FootprintLoad(str(lib),name)
        if not f: raise RuntimeError('Missing official footprint: '+str(lib)+'/'+name+'.kicad_mod')
    f.SetFPID(p.LIB_ID(*c['footprint'].split(':',1)))
    f.SetReference(c['ref']);f.SetValue(c['value'])
    f.SetPath(p.KIID_PATH('/'+uid('sheet')+'/'+uid(c['ref'])))
    f.SetPosition(pt(c['x'],c['y']));f.SetOrientationDegrees(c['angle'])
    f.Reference().SetTextSize(pt(.8,.8));f.Reference().SetTextThickness(mm(.12))
    f.Value().SetVisible(False)
    if c['kind']=='hole':f.Reference().SetVisible(False)
    for pad in f.Pads():
        n=c['pins'].get(pad.GetNumber())
        if n:pad.SetNet(net(n))
    board.Add(f)
    p.FootprintSave(str(LOCAL),f)
# Square board corners are a prototype target; fabricator/mechanical review is pending.
for x0,y0,x1,y1 in [(0,0,90,0),(90,0,90,55),(90,55,0,55),(0,55,0,0)]:
    s=p.PCB_SHAPE();s.SetShape(p.SHAPE_T_SEGMENT);s.SetStart(pt(x0,y0));s.SetEnd(pt(x1,y1))
    s.SetLayer(p.Edge_Cuts);s.SetWidth(mm(.05));board.Add(s)
for txt,x,y,size in [('VELOX B / UNROUTED / REVIEW',46,53,1),('USB',46.5,2,.8),('+',11,2,.8),('-',16,2,.8),('RUN OFF TO CHARGE',22,31,.7)]:
    t=p.PCB_TEXT(board);t.SetText(txt);t.SetPosition(pt(x,y));t.SetTextSize(pt(size,size));t.SetTextThickness(mm(.12));t.SetLayer(p.F_SilkS);board.Add(t)
z=p.ZONE(board);z.SetIsRuleArea(True)
ls=p.LSET(p.F_Cu);ls.AddLayer(p.B_Cu);z.SetLayerSet(ls)
z.SetDoNotAllowTracks(True);z.SetDoNotAllowVias(True);z.SetDoNotAllowCopperPour(True)
poly=z.Outline();poly.NewOutline()
for x,y in [(42,45),(54,45),(54,54),(42,54)]:poly.Append(mm(x),mm(y))
board.Add(z)
p.SaveBoard(str(D/'VELOX_carrier_B.kicad_pcb'),board)
print('Created UNROUTED 90 x55 mm proposal:',len(parts),'components;',len(nets),'nets.')
print('Route and resolve ERC/DRC before generating fabrication outputs.')
