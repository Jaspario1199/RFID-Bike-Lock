"""Deterministic two-layer routing for the prototype; KiCad DRC is authoritative.
This is geometry routing, not a substitute for electrical/power or RF validation.
"""
import sys, math, heapq, json
from pathlib import Path
sys.path.append('/usr/lib/python3/dist-packages')
import pcbnew as p
import numpy as np
ROOT=Path(__file__).resolve().parent; FN=ROOT/'design/VELOX_carrier_B.kicad_pcb'
b=p.LoadBoard(str(FN)); U=p.FromMM
def pt(x,y): return p.VECTOR2I(U(float(x)),U(float(y)))
def xy(v): return p.ToMM(v.x),p.ToMM(v.y)
S=.125; NX=721; NY=441
xx,yy=np.meshgrid(np.arange(NX)*S,np.arange(NY)*S,indexing='ij')
pads=[]; tracks=[]; vias=[]
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
    out=np.zeros((2,NX,NY),dtype=bool); r=(.45 if via else w/2)+.22
    edge=(xx < r+.25)|(xx > 90-r-.25)|(yy < r+.25)|(yy > 55-r-.25)
    antenna=(xx>42-r)&(xx<54+r)&(yy>45-r)&(yy<54+r)
    out[:]=edge|antenna
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
            m=(xx-x)**2+(yy-y)**2<.8**2
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
    tracks.append((n,l,x1,y1,x2,y2,w))
def addpath(path,a,c,n,w):
    l,x,y=path[0]; track(n,l,a['x'],a['y'],x*S,y*S,min(w,.3) if len(a['layers'])==1 else w)
    start=path[0]; last=path[0]; direction=None
    for cur in path[1:]:
        dl=(cur[0]-last[0],cur[1]-last[1],cur[2]-last[2])
        if dl!=direction or dl[0]:
            track(n,start[0],start[1]*S,start[2]*S,last[1]*S,last[2]*S,w); start=last
        if dl[0]:
            if any(vn==n and abs(vx-cur[1]*S)<1e-6 and abs(vy-cur[2]*S)<1e-6 for vn,vx,vy,_ in vias):
                start=cur;direction=dl;last=cur;continue
            v=p.PCB_VIA(b); v.SetPosition(pt(cur[1]*S,cur[2]*S)); v.SetWidth(U(.9)); v.SetDrill(U(.45)); v.SetViaType(p.VIATYPE_THROUGH); v.SetLayerPair(p.F_Cu,p.B_Cu); v.SetNetCode(b.FindNet(n).GetNetCode()); b.Add(v)
            vias.append((n,cur[1]*S,cur[2]*S,.9)); start=cur
        direction=dl; last=cur
    track(n,start[0],start[1]*S,start[2]*S,last[1]*S,last[2]*S,w)
    l,x,y=path[-1]; track(n,l,x*S,y*S,c['x'],c['y'],min(w,.3) if len(c['layers'])==1 else w)

# Reserve Nano signal escapes before power tracks can fence in header pads.
escaped={}
def escape_via(n,x,y):
    v=p.PCB_VIA(b);v.SetPosition(pt(x,y));v.SetWidth(U(.9));v.SetDrill(U(.45));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNetCode(b.FindNet(n).GetNetCode());b.Add(v)
    vias.append((n,x,y,.9))
for a in pads:
    if a['ref']!='U1' or not a['net']:continue
    ex=56.25 if int(a['num'])>=16 else 36.75
    ey=round(a['y']/S)*S
    track(a['net'],0,a['x'],a['y'],ex,ey,.4 if a['net'] in ['GND','3V3','NANO_7V5'] else .25)
    escape_via(a['net'],ex,ey)
    escaped[(a['ref'],a['num'])]=dict(x=ex,y=ey,layers=[0,1])

# Reserve connector and LED-resistor exits before routing the shared corridors.
for a in pads:
    ex=ey=layer=None
    if a['ref']=='J5' and a['num'] in ['1','2','3','4','7']:
        ex=a['x'];ey=3.0;layer=1
    elif a['ref']=='J6' and a['num'] in ['3','4','5','6','8']:
        ex=a['x'];ey=20.5;layer=0
    elif a['ref'] in ['R5','R6'] and a['num']=='1':
        ex=81;ey=a['y'];layer=0
    if ex is not None:
        track(a['net'],layer,a['x'],a['y'],ex,ey,.25)
        escape_via(a['net'],ex,ey)
        escaped[(a['ref'],a['num'])]=dict(x=ex,y=ey,layers=[0,1])

# Escape both crowded buzzer FET pins before nearby signal routing.
for number,ex,ey,nw in [('3',61.5,22,.25),('2',58.125,24.25,.4)]:
    a=next(a for a in pads if a['ref']=='Q2' and a['num']==number)
    track(a['net'],0,a['x'],a['y'],ex,ey,nw)
    escape_via(a['net'],ex,ey)
    escaped[('Q2',number)]=dict(x=ex,y=ey,layers=[0,1])

# The two3V3 bypass-ground pads escape their dense header corridor directly.
for ref,ex in [('C4',60),('C5',67)]:
    a=next(a for a in pads if a['ref']==ref and a['num']=='2')
    ey=14.5;track('GND',0,a['x'],a['y'],ex,ey,.4);escape_via('GND',ex,ey)
    escaped[(ref,'2')]=dict(x=ex,y=ey,layers=[0,1])

names=sorted({a['net'] for a in pads if a['net']})
priority=['BAT_PROTECTED','BAT_FUSED','BAT_RUN','COIL_6V','COIL_N','NANO_7V5','USB_VBUS','USB_5V_SAFE','3V3','LED_RED_GPIO','LED_GREEN_GPIO','RFID_SS','SPI_MISO','SPI_MOSI','SPI_SCK','RFID_RST','WAKE_BTN','SOL_GPIO']
names.sort(key=lambda n:(priority.index(n) if n in priority else 99 if n=='GND' else 20,n))
failed=[]
for n in names:
    if n=='RFID_SS':
        def getpad(ref,num):return next(a for a in pads if a['ref']==ref and a['num']==str(num))
        source=getpad('Q1',2);target=getpad('U3',3)
        escape=dict(x=78.125,y=37,layers=[0])
        path=findpath(source,escape,'GND',.45)
        if path:
            addpath(path,source,escape,'GND',.45)
            path=findpath(escape,target,'GND',1.0)
            if path:addpath(path,escape,target,'GND',1.0)
            else:failed.append(('GND','Q1','2','coil return'))
        else:failed.append(('GND','Q1','2','source fanout'))
    group=[a for a in pads if a['net']==n]; connected=[group[0]]; pending=group[1:]
    width=1.5 if n in ['BAT_PROTECTED','BAT_FUSED','BAT_RUN'] else 1.0 if n in ['COIL_6V','COIL_N'] else .8 if n=='NANO_7V5' else .5 if n in ['USB_VBUS','USB_5V_SAFE'] else .4 if n in ['3V3','GND'] else .25
    # Fine-pitch SMD power pins escape at a narrower width before the main route.
    group=[dict(a) for a in group]
    for a in group:
        if (a['ref'],a['num']) in escaped:a.update(escaped[(a['ref'],a['num'])])
    if width>=.8:
        for a in group:
            if len(a['layers'])!=1 or a['ref'].startswith('TP'):continue
            dx=a['x']-a['fx'];dy=a['y']-a['fy']
            if abs(dx)+abs(dy)<.1:continue
            if abs(dx)>=abs(dy): ex=a['x']+math.copysign(a['wx']/2+width/2+.4,dx);ey=a['y']
            else: ex=a['x'];ey=a['y']+math.copysign(a['wy']/2+width/2+.4,dy)
            dest=dict(x=round(ex/S)*S,y=round(ey/S)*S,layers=a['layers'])
            neck=.3 if a['ref']!='Q1' else .45
            path=findpath(a,dest,n,neck)
            if path:
                addpath(path,a,dest,n,neck);a.update(dest)
            else:failed.append((n,a['ref'],a['num'],'power fanout'))
    connected=[group[0]];pending=group[1:]
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

# Remove reserved escape vias when a completed route used only one layer.
# No non-ground pour exists; absence of any same-net copper on a layer makes
# that via unnecessary. Native DRC checks that removal does not break a net.
def distance_to_segment(x,y,x1,y1,x2,y2):
    dx=x2-x1;dy=y2-y1;den=dx*dx+dy*dy
    t=max(0,min(1,((x-x1)*dx+(y-y1)*dy)/(den or 1)))
    return math.hypot(x-x1-t*dx,y-y1-t*dy)
removed=0
for v in list(b.GetTracks()):
    if not isinstance(v,p.PCB_VIA) or v.GetNetname()=='GND':continue
    x,y=xy(v.GetPosition());n=v.GetNetname();touch=set()
    for tn,l,x1,y1,x2,y2,tw in tracks:
        if tn==n and distance_to_segment(x,y,x1,y1,x2,y2)<=(tw+.9)/2+1e-5:touch.add(l)
    for a in pads:
        if a['net']!=n:continue
        d=math.hypot(max(0,abs(x-a['x'])-a['wx']/2),max(0,abs(y-a['y'])-a['wy']/2))
        if d<=.45+1e-5:touch.update(a['layers'])
    if len(touch)<2:b.Remove(v);removed+=1
b.BuildConnectivity()
for layer in [p.F_Cu,p.B_Cu]:
    z=p.ZONE(b); z.SetLayer(layer); z.SetNetCode(b.FindNet('GND').GetNetCode()); z.SetLocalClearance(U(.25)); z.SetThermalReliefGap(U(.25)); z.SetThermalReliefSpokeWidth(U(.4)); z.SetPadConnection(p.ZONE_CONNECTION_FULL); z.SetIslandRemovalMode(p.ISLAND_REMOVAL_MODE_ALWAYS)
    poly=z.Outline();poly.NewOutline()
    for x,y in [(.5,.5),(89.5,.5),(89.5,54.5),(.5,54.5)]:poly.Append(U(x),U(y))
    b.Add(z)
p.ZONE_FILLER(b).Fill(b.Zones())
p.SaveBoard(str(FN),b)
(ROOT/'routing_report.json').write_text(json.dumps(dict(failed=failed,segments=len(tracks),vias=sum(isinstance(t,p.PCB_VIA) for t in b.GetTracks()),unused_escape_vias_removed=removed,grid_mm=S,signal_width_mm=.25,power_width_mm=1.5,clearance_mm=.22),indent=2))
print('DONE',len(tracks),'segments',len(vias),'vias; failed',failed)
p.WriteDRCReport(b,str(ROOT/'drc.txt'),p.EDA_UNITS_MILLIMETRES,True)
