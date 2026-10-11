"""Deterministic two-sided rivet-compatible routing for the V-One prototype; KiCad DRC is authoritative.
This is geometry routing, not a substitute for electrical/power or RF validation.
"""
import sys, math, heapq, json
from pathlib import Path
sys.path.append('/usr/lib/python3/dist-packages')
import pcbnew as p
import numpy as np
ROOT=Path(__file__).resolve().parent; FN=ROOT/'design/VELOX_carrier_V.kicad_pcb'
b=p.LoadBoard(str(FN)); U=p.FromMM
def pt(x,y): return p.VECTOR2I(U(float(x)),U(float(y)))
def xy(v): return p.ToMM(v.x),p.ToMM(v.y)
S=.25; NX=361; NY=221
xx,yy=np.meshgrid(np.arange(NX)*S,np.arange(NY)*S,indexing='ij')
pads=[]; tracks=[]; vias=[];trackobjects=[]
for f in b.GetFootprints():
    for pad in f.Pads():
        x,y=xy(pad.GetPosition()); sx,sy=xy(pad.GetSize()); ang=math.radians(pad.GetOrientationDegrees())
        wx=abs(sx*math.cos(ang))+abs(sy*math.sin(ang)); wy=abs(sx*math.sin(ang))+abs(sy*math.cos(ang))
        fx,fy=xy(f.GetPosition())
        pads.append(dict(fx=fx,fy=fy,ref=f.GetReference(),num=pad.GetNumber(),x=x,y=y,wx=wx,wy=wy,net=pad.GetNetname(),layers=[k for k,l in enumerate([p.F_Cu,p.B_Cu]) if pad.IsOnLayer(l)],drill=p.ToMM(pad.GetDrillSize().x)))
def segmentmask(x1,y1,x2,y2,r):
    dx=x2-x1; dy=y2-y1; den=dx*dx+dy*dy
    t=np.clip(((xx-x1)*dx+(yy-y1)*dy)/(den or 1),0,1)
    return (xx-x1-t*dx)**2+(yy-y1-t*dy)**2 < r*r
def blocked(net,w,via=False):
    out=np.zeros((2,NX,NY),dtype=bool); r=(.65 if via else w/2)+.31
    edge=(xx < r+.25)|(xx > 90-r-.25)|(yy < r+.25)|(yy > 55-r-.25)
    antenna=(xx>42-r)&(xx<54+r)&(yy>45-r)&(yy<54+r)
    mounts=np.zeros((NX,NY),dtype=bool)
    for hx,hy in [(4,4),(86,4),(4,51),(86,51)]:mounts|=(xx-hx)**2+(yy-hy)**2<(3.3+r)**2
    out[:]=edge|antenna|mounts
    for a in pads:
        if a['net']==net and a['net']:
            if via and a['drill']:
                out|=(xx-a['x'])**2+(yy-a['y'])**2 < (a['drill']/2+.5+.25)**2
            continue
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
        elif via:
            m=(xx-x)**2+(yy-y)**2<1.15**2
            m[round(x/S),round(y/S)]=False
            out|=m
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
    tracks.append((n,l,x1,y1,x2,y2,w));trackobjects.append(t)
def addpath(path,a,c,n,w):
    l,x,y=path[0]; track(n,l,a['x'],a['y'],x*S,y*S,min(w,.35) if len(a['layers'])==1 else w)
    start=path[0]; last=path[0]; direction=None
    for cur in path[1:]:
        dl=(cur[0]-last[0],cur[1]-last[1],cur[2]-last[2])
        if dl!=direction or dl[0]:
            track(n,start[0],start[1]*S,start[2]*S,last[1]*S,last[2]*S,w); start=last
        if dl[0]:
            if any(vn==n and abs(vx-cur[1]*S)<1e-6 and abs(vy-cur[2]*S)<1e-6 for vn,vx,vy,_ in vias):
                start=cur;direction=dl;last=cur;continue
            v=p.PCB_VIA(b); v.SetPosition(pt(cur[1]*S,cur[2]*S)); v.SetWidth(U(1.3)); v.SetDrill(U(.7)); v.SetViaType(p.VIATYPE_THROUGH); v.SetLayerPair(p.F_Cu,p.B_Cu); v.SetNetCode(b.FindNet(n).GetNetCode()); b.Add(v)
            vias.append((n,cur[1]*S,cur[2]*S,1.3)); start=cur
        direction=dl; last=cur
    track(n,start[0],start[1]*S,start[2]*S,last[1]*S,last[2]*S,w)
    l,x,y=path[-1]; track(n,l,x*S,y*S,c['x'],c['y'],min(w,.35) if len(c['layers'])==1 else w)


# Route both printed sides with rivets. Native connectivity is authoritative;
# finish.py installs the reviewed short JP1 link.
comps=json.loads((ROOT/'design/components.json').read_text());logical=json.loads((ROOT/'design/logical_components.json').read_text())
links=[]
def newnet(n):
    net=p.NETINFO_ITEM(b,n);b.Add(net);return net
priority=['BUZZ_GATE','BUZZ_N','LED_RED_A','LED_GREEN_A','BAT_ADC','SOL_GATE','SPI_SCK','SPI_MISO','SPI_MOSI','RFID_SS','RFID_RST','WAKE_BTN','ADMIN_BTN','LED_RED_GPIO','LED_GREEN_GPIO','BUZZ_GPIO','SOL_GPIO','NANO_7V5','BAT_MON','3V3','GND']
names=sorted({a['net'] for a in pads if a['net'] and not a['net'].startswith('unconnected-')},key=lambda n:(priority.index(n) if n in priority else 99,n))
# Reserve outward 0.35 mm necks for bottom SMT power/ground pads before
# signal routing fences them in; main rails are0.6mm. This is not coil routing.
escaped={}
for a in pads:
    if a['net'] not in ['GND','3V3','NANO_7V5'] or a['layers']!=[1]:continue
    dx=a['x']-a['fx'];dy=a['y']-a['fy']
    if abs(dx)>=abs(dy):ex=a['x']+math.copysign(a['wx']/2+.9,dx);ey=a['y']
    else:ex=a['x'];ey=a['y']+math.copysign(a['wy']/2+.9,dy)
    dest=dict(a,x=round(ex/S)*S,y=round(ey/S)*S)
    path=findpath(a,dest,a['net'],.35)
    if path:addpath(path,a,dest,a['net'],.35);escaped[(a['ref'],a['num'])]=dest
    else:
        for ox,oy in [(0,1.75),(0,-1.75),(1.75,0),(-1.75,0)]:
            dest=dict(a,x=round((a['x']+ox)/S)*S,y=round((a['y']+oy)/S)*S)
            path=findpath(a,dest,a['net'],.35)
            if path:addpath(path,a,dest,a['net'],.35);escaped[(a['ref'],a['num'])]=dest;break
        else:raise RuntimeError('Cannot escape SMT rail pad '+a['ref']+'.'+a['num'])
failed=[]
for n in names:
    group=[escaped.get((a['ref'],a['num']),a) for a in pads if a['net']==n];roots=list(range(len(group)));w=.6 if n in ['3V3','GND','NANO_7V5'] else .35
    def root(i):
        if roots[i]!=i:roots[i]=root(roots[i])
        return roots[i]
    candidates=sorted((abs(a['x']-c['x'])+abs(a['y']-c['y']),i,j) for i,a in enumerate(group) for j,c in enumerate(group) if j>i)
    for width in [w]+([.35] if w>.35 else []):
        for _,i,j in candidates:
            if root(i)==root(j):continue
            a,c=group[i],group[j];path=findpath(a,c,n,width)
            if path:addpath(path,a,c,n,width);roots[root(j)]=root(i)
    if len({root(i) for i in range(len(group))})>1:failed.append(n)
    print('Routed',n,'vias',len(vias),flush=True)
if failed:print('Router tree accounting needs native connectivity check:',failed,flush=True)
for f in b.GetFootprints():p.FootprintSave(str(ROOT/'design/VELOX.pretty'),f)
p.SaveBoard(str(FN),b)
(ROOT/'design/components.json').write_text(json.dumps(comps,indent=2)+'\n')
(ROOT/'jumpers.json').write_text(json.dumps(links,indent=2)+'\n')
(ROOT/'routing_report.json').write_text(json.dumps({'copper_sides':['F.Cu','B.Cu'],'segments':len(tracks),'vias':len(vias),'installed_wire_count':len(links),'min_trace_mm':.35,'signal_clearance_target_mm':.3,'power_trace_mm':.6,'router_tree_nets_for_native_review':failed,'note':'SMT rail necks are0.35mm; main logic rails0.6mm. Small rivets drill0.7 / land1.3mm connect printed layers. Wire components intentionally overlay existing solder lands; they add no holes. No printed front copper or solid ground plane.'},indent=2)+'\n')
