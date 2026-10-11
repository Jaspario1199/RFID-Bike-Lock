"""Generate VELOX carrier Rev V, a review prototype, using KiCad 7 pcbnew.
Run with Python 3.12 + pcbnew, numpy. Board dimensions are proposed, not enclosure approval.
"""
from pathlib import Path
import sys, json, uuid, math, re, csv, os
sys.path.append('/usr/lib/python3/dist-packages')
import pcbnew as p

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'design'; OUT.mkdir(exist_ok=True)
PRE=ROOT/'previews'; PRE.mkdir(exist_ok=True)
LIB=Path(os.environ.get('KICAD_FOOTPRINT_DIR','/usr/share/kicad/footprints'))
def uid(s): return str(uuid.uuid5(uuid.NAMESPACE_URL,'velox-pcb-revV/'+s))
def mm(x): return p.FromMM(float(x))
def pt(x,y): return p.VECTOR2I(mm(x),mm(y))
board=p.BOARD(); board.SetCopperLayerCount(2)
board.GetDesignSettings().SetBoardThickness(mm(1.6))
comps=[]; nets={}; footprints={}
def net(n):
    if not n: return None
    if n not in nets:
        v=p.NETINFO_ITEM(board,n); board.Add(v); nets[n]=v
    return nets[n]
def line(parent,x1,y1,x2,y2,layer=p.F_SilkS,width=.15):
    s=p.FP_SHAPE(parent) if isinstance(parent,p.FOOTPRINT) else p.PCB_SHAPE()
    s.SetShape(p.SHAPE_T_SEGMENT); s.SetStart(pt(x1,y1)); s.SetEnd(pt(x2,y2)); s.SetLayer(layer); s.SetWidth(mm(width));
    if isinstance(parent,p.FOOTPRINT): s.SetStart0(pt(x1,y1)); s.SetEnd0(pt(x2,y2))
    parent.Add(s)
def rect(parent,x0,y0,x1,y1,layer=p.F_Fab):
    for a,b in [((x0,y0),(x1,y0)),((x1,y0),(x1,y1)),((x1,y1),(x0,y1)),((x0,y1),(x0,y0))]: line(parent,*a,*b,layer)
def textboard(t,x,y,size=1,layer=p.F_SilkS):
    o=p.PCB_TEXT(board); o.SetText(t); o.SetPosition(pt(x,y)); o.SetTextSize(pt(size,size)); o.SetTextThickness(mm(.15)); o.SetLayer(layer); board.Add(o)
def copperlayers():
    ls=p.LSET(p.F_Cu); ls.AddLayer(p.B_Cu); return ls
def padlayers():
    ls=p.LSET.AllCuMask(); ls.AddLayer(p.F_Mask); ls.AddLayer(p.B_Mask); return ls
def custom(name,pads,body=None):
    f=p.FOOTPRINT(board); f.SetFPID(p.LIB_ID('VELOX',name))
    for num,x,y in pads:
        q=p.PAD(f); q.SetNumber(str(num)); q.SetPosition(pt(x,y)); q.SetPos0(pt(x,y)); q.SetSize(pt(2,2)); q.SetDrillSize(pt(1,1)); q.SetAttribute(p.PAD_ATTRIB_PTH); q.SetShape(p.PAD_SHAPE_RECT if str(num)=='1' else p.PAD_SHAPE_CIRCLE); q.SetLayerSet(padlayers()); f.Add(q)
    if body:
        rect(f,*body,p.F_Fab); rect(f,*body,p.F_SilkS)
        x0,y0,x1,y1=body; rect(f,x0-.5,y0-.5,x1+.5,y1+.5,p.F_CrtYd)
    return f
def add(ref,val,fp,x,y,pin_nets,kind='connector',names=None,angle=0,note=''):
    if isinstance(fp,str):
        lib,name=fp.split(':'); f=p.FootprintLoad(str(LIB/(lib+'.pretty')),name)
        if not f: raise RuntimeError(fp)
        fid=fp
    else: f=fp; fid=str(f.GetFPID().GetLibNickname())+':'+str(f.GetFPID().GetLibItemName())
    f.SetReference(ref); f.SetValue(val); f.SetPosition(pt(x,y)); f.SetOrientationDegrees(angle)
    f.Reference().SetTextSize(pt(.8,.8)); f.Reference().SetTextThickness(mm(.12))
    f.Value().SetVisible(False)
    f.SetPath(p.KIID_PATH('/'+uid('sheet')+'/'+uid(ref)))
    for pad in f.Pads():
        n=pin_nets.get(pad.GetNumber())
        if n: pad.SetNet(net(n))
        elif pad.GetNumber() in pin_nets:
            name=(names or {}).get(pad.GetNumber(),pad.GetNumber())
            pad.SetNet(net(f'unconnected-({ref}-{name}-Pad{pad.GetNumber()})'))
    board.Add(f); footprints[ref]=f
    comps.append(dict(ref=ref,value=val,footprint=fid,pins=pin_nets,kind=kind,names=names or {},x=x,y=y,angle=angle,note=note))
    return f
# Two-sided printed ink. Socket/connector leads enter from the top through large
# copper rivets; front/back ink is connected by copper rivets, with no chemical plating.
R='Resistor_SMD:R_0805_2012Metric_Pad1.20x1.40mm_HandSolder'
C='Capacitor_SMD:C_0805_2012Metric_Pad1.18x1.45mm_HandSolder'
def smd(ref,val,fp,x,y,pins,kind,names=None,note=''):
    f=add(ref,val,fp,x,y,pins,kind,names=names,note=note)
    f.Flip(f.GetPosition(),False)
    return f
def rc(ref,val,x,y,a,b,kind='R'):
    return smd(ref,val,R if kind=='R' else C,x,y,{'1':a,'2':b},kind)
def header(ref,value,x,y,ns,names):
    f=custom('Riveted_'+ref,[(i+1,0,i*2.54) for i in range(len(ns))],(-1.4,-1.4,1.4,(len(ns)-1)*2.54+1.4))
    f=add(ref,value,f,x,y,{str(i+1):n for i,n in enumerate(ns)},names={str(i+1):n for i,n in enumerate(names)},note='2.54 mm vertical header. Large copper rivets: drill1.6 / bore1.0 / flange2.2 mm; qualify stock before fabrication. Header on top, solder ink/rivet on bottom.')
    return f
left=['SPI_SCK','3V3',None,'BAT_ADC',None,None,None,None,None,None,None,None,None,'GND','NANO_7V5']
right=['SPI_MISO','SPI_MOSI','RFID_SS','LED_GREEN_GPIO','LED_RED_GPIO',None,'BUZZ_GPIO','SOL_GPIO','RFID_RST','WAKE_BTN','ADMIN_BTN','GND',None,None,None]
ln=['D13','3V3','B0','A0','A1','A2','A3','A4','A5','A6','A7','VBUS','B1','GND','VIN']
rn=['D12','D11','D10','D9','D8','D7','D6','D5','D4','D3','D2','GND','RESET','D0','D1']
u=custom('Nano_ESP32_Riveted_Sockets',[(i+1,0,i*2.54) for i in range(15)]+[(i+16,15.24,i*2.54) for i in range(15)],(-1.38,-4,16.62,41))
add('U1','Arduino Nano ESP32 ABX00083',u,39,8,{str(i+1):n for i,n in enumerate(left+right)},'nano',{str(i+1):n for i,n in enumerate(ln+rn)},note='2x1x15 sockets, 15.24 row separation. Antenna bottom end; module stack must be physically measured. Mount after inspecting underside solder joints.')
header('J1','EXTERNAL POWER / COIL CONTROL',10,35,['NANO_7V5','GND','BAT_MON','SOL_GATE'],['7V5_IN','GND_STAR','BAT_RUN_MON','COIL_GATE_OUT'])
header('J5','RC522 / 2.54 HEADER',70,6,['RFID_SS','SPI_SCK','SPI_MOSI','SPI_MISO',None,'GND','RFID_RST','3V3'],['SS','SCK','MOSI','MISO','IRQ_NC','GND','RST','3V3'])
header('J6','PANEL / 2.54 HEADER',82,23,['GND','GND','WAKE_BTN','ADMIN_BTN','LED_RED_A','LED_GREEN_A','3V3','BUZZ_N'],['GND1','GND2','WAKE','CANCEL','RED_A','GREEN_A','BUZZ_PLUS','BUZZ_MINUS'])
rc('R1','330',22,38,'SOL_GPIO','SOL_GATE')
rc('R7','100k 1%',20,20,'BAT_MON','BAT_ADC');rc('R8','100k 1%',20,26,'BAT_ADC','GND');rc('C6','100n 16V',28,26,'BAT_ADC','GND','C')
rc('C3','10u 25V X7R',30,43,'NANO_7V5','GND','C')
rc('C4','100n 16V',60,12,'3V3','GND','C');rc('C5','10u 10V X7R',63,15,'3V3','GND','C')
rc('R5','470',75,35,'LED_RED_GPIO','LED_RED_A');rc('R6','470',75,38,'LED_GREEN_GPIO','LED_GREEN_A')
smd('Q2','AO3400A','Package_TO_SOT_SMD:SOT-23',65,25,{'1':'BUZZ_GATE','2':'GND','3':'BUZZ_N'},'mos',{'1':'G','2':'S','3':'D'},'3.3 V active buzzer <=30mA candidate. Genuine AO3400A rated at2.5 V gate drive.')
rc('R3','330',62,29,'BUZZ_GPIO','BUZZ_GATE');rc('R4','100k',67,29,'BUZZ_GATE','GND')
smd('D2','SS14','Diode_SMD:D_SMA',72,32,{'1':'3V3','2':'BUZZ_N'},'diode',{'1':'K','2':'A'},'Flyback for active magnetic buzzer; cathode to3V3. Verify buzzer current.')
for i,(x,y) in enumerate([(4,4),(86,4),(4,51),(86,51)],1):
    f=add('H'+str(i),'1.6 PILOT / HAND FINISH 3.2','MountingHole:MountingHole_3.2mm_M3',x,y,{},'hole',note='FEDC1.6 mm pilot only. After curing, fixture and finish to3.2 mm for M3. Centers unchanged from RevB; board requires new enclosure supports.')
    for d in f.Pads():d.SetDrillSize(pt(1.6,1.6));d.SetSize(pt(1.6,1.6))
    f.Reference().SetVisible(False)
    z=p.ZONE(board);z.SetIsRuleArea(True);z.SetZoneName('M3_CLEAR_'+str(i));z.SetLayerSet(copperlayers());z.SetDoNotAllowTracks(True);z.SetDoNotAllowVias(True);z.SetDoNotAllowCopperPour(True);z.SetDoNotAllowPads(False)
    poly=z.Outline();poly.NewOutline()
    for j in range(64):a=j*math.pi/32;poly.Append(mm(x+3.3*math.cos(a)),mm(y+3.3*math.sin(a)))
    board.Add(z)
# THT land artwork is on both printed sides, with large rivet-compatible pad geometry.
for f in board.GetFootprints():
    for d in f.Pads():
        if d.GetAttribute()==p.PAD_ATTRIB_PTH:
            d.SetSize(pt(2.24,2.24));d.SetDrillSize(pt(1.6,1.6));ls=p.LSET(p.B_Cu);ls.AddLayer(p.F_Cu);ls.AddLayer(p.B_Mask);ls.AddLayer(p.F_Mask);d.SetLayerSet(ls)
    f.Reference().SetTextSize(pt(1,1));f.Reference().SetTextThickness(mm(.15))
# No fabrication silkscreen. Keep component graphics/reference labels on Fab
# layers for assembly documentation instead of claiming FEDC prints markings.
for f in board.GetFootprints():
    for g in f.GraphicalItems():
        if g.GetLayer()==p.F_SilkS:g.SetLayer(p.F_Fab)
        elif g.GetLayer()==p.B_SilkS:g.SetLayer(p.B_Fab)
    f.Reference().SetLayer(p.B_Fab if f.IsFlipped() else p.F_Fab)
# Preserve legacy antenna keepout, both sides, with no ground pours.
z=p.ZONE(board);z.SetIsRuleArea(True);z.SetZoneName('NANO_ANTENNA');z.SetLayerSet(copperlayers());z.SetDoNotAllowTracks(True);z.SetDoNotAllowVias(True);z.SetDoNotAllowCopperPour(True);z.SetDoNotAllowPads(False)
poly=z.Outline();poly.NewOutline()
for x,y in [(42,45),(54,45),(54,54),(42,54)]:poly.Append(mm(x),mm(y))
board.Add(z)
rect(board,0,0,90,55,p.Edge_Cuts)
textboard('VELOX V / FEDC REVIEW',20,46,1,p.F_SilkS)
pretty=OUT/'VELOX.pretty';pretty.mkdir(exist_ok=True)
for f in board.GetFootprints():
    p.FootprintSave(str(pretty),f);name=str(f.GetFPID().GetLibItemName());f.SetFPID(p.LIB_ID('VELOX',name));next(c for c in comps if c['ref']==f.GetReference())['footprint']='VELOX:'+name
(OUT/'fp-lib-table').write_text('(fp_lib_table (lib (name "VELOX")(type "KiCad")(uri "${KIPRJMOD}/VELOX.pretty")(options "")(descr "Rev V local footprints")))\n')
(OUT/'components.json').write_text(json.dumps(comps,indent=2)+'\n')
(OUT/'logical_components.json').write_text(json.dumps(comps,indent=2)+'\n')
p.SaveBoard(str(OUT/'VELOX_carrier_V.kicad_pcb'),board)
print('Created two-sided control carrier',len(comps),'parts')
