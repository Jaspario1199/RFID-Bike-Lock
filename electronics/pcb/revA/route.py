"""Deterministic two-layer routing for the prototype; KiCad DRC is authoritative.
This is geometry routing, not a substitute for electrical/power or RF validation.
"""
import sys, math, heapq, json
from pathlib import Path
sys.path.append('/usr/lib/python3/dist-packages')
import pcbnew as p
import numpy as np
ROOT=Path(__file__).resolve().parent; FN=ROOT/'design/VELOX_carrier_A.kicad_pcb'
b=p.LoadBoard(str(FN)); U=p.FromMM
def pt(x,y): return p.VECTOR2I(U(x),U(y))
def xy(v): return p.ToMM(v.x),p.ToMM(v.y)
S=.25; NX=441; NY=261
xx,yy=np.meshgrid(np.arange(NX)*S,np.arange(NY)*S,indexing='ij')
pads=[]; tracks=[]; vias=[]
for f in b.GetFootprints():
    for pad in f.Pads():
        x,y=xy(pad.GetPosition()); sx,sy=xy(pad.GetSize()); ang=math.radians(pad.GetOrientationDegrees())
        wx=abs(sx*math.cos(ang))+abs(sy*math.sin(ang)); wy=abs(sx*math.sin(ang))+abs(sy*math.cos(ang))
        pads.append(dict(ref=f.GetReference(),num=pad.GetNumber(),x=x,y=y,wx=wx,wy=wy,net=pad.GetNetname(),layers=[k for k,l in enumerate([p.F_Cu,p.B_Cu]) if pad.IsOnLayer(l)],drill=p.ToMM(pad.GetDrillSize().x)))
def segmentmask(x1,y1,x2,y2,r):
    dx=x2-x1; dy=y2-y1; den=dx*dx+dy*dy
    t=np.clip(((xx-x1)*dx+(yy-y1)*dy)/(den or 1),0,1)
    return (xx-x1-t*dx)**2+(yy-y1-t*dy)**2 < r*r
def blocked(net,w,via=False):
    out=np.zeros((2,NX,NY),dtype=bool); r=(.45 if via else w/2)+.22
    edge=(xx < r+.25)|(xx > 110-r-.25)|(yy < r+.25)|(yy > 65-r-.25)
    antenna=(xx>58-r)&(xx<69+r)&(yy>45-r)&(yy<51+r)
    out[:]=edge|antenna
    for a in pads:
        if a['net']==net and a['net']: continue
        if not a['layers']:
            mask=(xx-a['x'])**2+(yy-a['y'])**2 < (a['drill']/2+r+.25)**2
            out|=mask
        else:
            mask=(abs(xx-a['x'])<a['wx']/2+r)&(abs(yy-a['y'])<a['wy']/2+r)
            for l in a['layers']: out[l]|=mask
    for n,l,x1,y1,x2,y2,tw in tracks:
        if n!=net: out[l]|=segmentmask(x1,y1,x2,y2,r+tw/2)
    for n,x,y,d in vias:
        if n!=net: out|=(xx-x)**2+(yy-y)**2<(r+d/2)**2
    return out
def grid(a): return (round(a['x']/S),round(a['y']/S))
def findpath(a,c,n,w):
    ob=blocked(n,w); vo=blocked(n,w,True); no_via=vo[0]|vo[1]
    sx,sy=grid(a); tx,ty=grid(c)
    starts=[(l,sx,sy) for l in a['layers']]; targets={(l,tx,ty) for l in c['layers']}
    for l,x,y in starts|targets if isinstance(starts,set) else starts+list(targets): ob[l,x,y]=False
    def h(s): return abs(s[1]-tx)+abs(s[2]-ty)+(0 if s[0] in c['layers'] else 10)
    heap=[]; costs={}; prev={}
    for s in starts: costs[s]=0; heapq.heappush(heap,(h(s),0,s))
    found=None
    while heap:
        _,g,s=heapq.heappop(heap)
        if g!=costs[s]: continue
        if s in targets: found=s; break
        l,x,y=s
        for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
            nx=x+dx; ny=y+dy
            if nx<0 or nx>=NX or ny<0 or ny>=NY or ob[l,nx,ny]: continue
            t=(l,nx,ny); ng=g+1
            if ng<costs.get(t,1e30): costs[t]=ng; prev[t]=s; heapq.heappush(heap,(ng+h(t),ng,t))
        if not no_via[x,y] and not ob[1-l,x,y]:
            t=(1-l,x,y); ng=g+16
            if ng<costs.get(t,1e30): costs[t]=ng; prev[t]=s; heapq.heappush(heap,(ng+h(t),ng,t))
    if found is None: return None
    path=[found]
    while path[-1] in prev: path.append(prev[path[-1]])
    return path[::-1]
def track(n,l,x1,y1,x2,y2,w):
    if abs(x1-x2)+abs(y1-y2)<.0001:return
    t=p.PCB_TRACK(b); t.SetStart(pt(x1,y1)); t.SetEnd(pt(x2,y2)); t.SetWidth(U(w)); t.SetLayer([p.F_Cu,p.B_Cu][l]); t.SetNetCode(b.FindNet(n).GetNetCode()); b.Add(t)
    tracks.append((n,l,x1,y1,x2,y2,w))
def addpath(path,a,c,n,w):
    l,x,y=path[0]; track(n,l,a['x'],a['y'],x*S,y*S,min(w,.3) if len(a['layers'])==1 else w)
    start=path[0]; last=path[0]; direction=None
    for cur in path[1:]:
        dl=(cur[0]-last[0],cur[1]-last[1],cur[2]-last[2])
        if dl!=direction or dl[0]:
            track(n,start[0],start[1]*S,start[2]*S,last[1]*S,last[2]*S,w); start=last
        if dl[0]:
            v=p.PCB_VIA(b); v.SetPosition(pt(cur[1]*S,cur[2]*S)); v.SetWidth(U(.9)); v.SetDrill(U(.45)); v.SetViaType(p.VIATYPE_THROUGH); v.SetLayerPair(p.F_Cu,p.B_Cu); v.SetNetCode(b.FindNet(n).GetNetCode()); b.Add(v)
            vias.append((n,cur[1]*S,cur[2]*S,.9)); start=cur
        direction=dl; last=cur
    track(n,start[0],start[1]*S,start[2]*S,last[1]*S,last[2]*S,w)
    l,x,y=path[-1]; track(n,l,x*S,y*S,c['x'],c['y'],min(w,.3) if len(c['layers'])==1 else w)

names=sorted({a['net'] for a in pads if a['net'] and a['net']!='GND'})
priority=['SPI_SCK','COIL_N','CELL_N','CELL_P','PROTECTED_BAT','FUSED_BAT','BAT_RUN','COIL_6V','3V3']
names.sort(key=lambda n:(priority.index(n) if n in priority else 20,n))
failed=[]
for n in names:
    group=[a for a in pads if a['net']==n]; connected=[group[0]]; pending=group[1:]
    width=.8 if n in ['CELL_P','CELL_N','PROTECTED_BAT','FUSED_BAT','BAT_RUN','COIL_6V'] else .6 if n=='COIL_N' else .4 if n=='3V3' else .25
    while pending:
        candidates=sorted(((abs(a['x']-c['x'])+abs(a['y']-c['y']),i,j) for i,a in enumerate(connected) for j,c in enumerate(pending)))
        success=False
        for _,i,j in candidates:
            a=connected[i]; c=pending[j]; path=findpath(a,c,n,width)
            if path:
                addpath(path,a,c,n,width); connected.append(pending.pop(j)); success=True; break
        if not success:
            failed.extend((n,c['ref'],c['num']) for c in pending);break
    print(n,'pending',len(pending),flush=True)

# Both copper layers have ground pours; direct ground vias beside SMD ground pads.
for a in [a for a in pads if a['net']=='GND' and len(a['layers'])==1]:
    ob=blocked('GND',.4,True); placed=False
    for r in [.9,1.2,1.5,2.,2.5,3.]:
        for dx,dy in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,1),(1,-1),(-1,-1)]:
            x=round((a['x']+dx*r)/S);y=round((a['y']+dy*r)/S)
            if not(0<=x<NX and 0<=y<NY) or ob[:,x,y].any():continue
            dest=dict(x=x*S,y=y*S,layers=[1]);path=findpath(a,dest,'GND',.4)
            if path:
                addpath(path,a,dest,'GND',.4);placed=True;break
        if placed:break
    if not placed: failed.append(('GND',a['ref'],a['num']))
for layer in [p.F_Cu,p.B_Cu]:
    z=p.ZONE(b); z.SetLayer(layer); z.SetNetCode(b.FindNet('GND').GetNetCode()); z.SetLocalClearance(U(.25)); z.SetThermalReliefGap(U(.25)); z.SetThermalReliefSpokeWidth(U(.4)); z.SetPadConnection(p.ZONE_CONNECTION_FULL)
    poly=z.Outline();poly.NewOutline()
    for x,y in [(.5,.5),(109.5,.5),(109.5,64.5),(.5,64.5)]:poly.Append(U(x),U(y))
    b.Add(z)
p.ZONE_FILLER(b).Fill(b.Zones())
# Merge the two nearby same-net vias at the BAT_RUN test-point fanout.
# The remaining via connects both copper layers through the shared test pad.
for t in list(b.GetTracks()):
    if isinstance(t,p.PCB_VIA) and abs(p.ToMM(t.GetPosition().x)-45)<.001 and abs(p.ToMM(t.GetPosition().y)-35.5)<.001:
        b.Remove(t)
p.ZONE_FILLER(b).Fill(b.Zones())
p.SaveBoard(str(FN),b)
(ROOT/'routing_report.json').write_text(json.dumps(dict(failed=failed,segments=len(tracks),vias=len(vias),grid_mm=S,signal_width_mm=.25,power_width_mm=.8,clearance_mm=.22),indent=2))
print('DONE',len(tracks),'segments',len(vias),'vias; failed',failed)
p.WriteDRCReport(b,str(ROOT/'drc.txt'),p.EDA_UNITS_MILLIMETRES,True)
