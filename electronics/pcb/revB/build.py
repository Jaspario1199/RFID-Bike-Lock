"""Generate VELOX carrier Rev B, a review prototype, using KiCad 7 pcbnew.
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
def uid(s): return str(uuid.uuid5(uuid.NAMESPACE_URL,'velox-pcb-revB/'+s))
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
R='Resistor_SMD:R_0805_2012Metric_Pad1.20x1.40mm_HandSolder'
C='Capacitor_SMD:C_0805_2012Metric_Pad1.18x1.45mm_HandSolder'
Q='Package_TO_SOT_SMD:SOT-23'
D='Diode_SMD:D_SMA'
def rc(ref,val,x,y,a,b,kind='R',angle=0): return add(ref,val,R if kind=='R' else C,x,y,{'1':a,'2':b},kind,angle=angle)

# Fixed-output modules: positions and header order come from Pololu top views.
# U3 top view: six holes along bottom edge. Bottom-view labels are mirrored.
# Top-view left to right: EN / VIN / GND / GND / VOUT / VOUT.
u3=custom('Pololu_U3V40F6_4013',[(i+1,-6.33+i*2.54,6.33) for i in range(6)],(-7.6,-7.6,7.6,7.6))
for pa in u3.Pads():pa.SetDrillSize(pt(1.2,1.2))
add('U3','Pololu U3V40F6 / 6V',u3,65,37,
    {'1':'BAT_RUN','2':'BAT_RUN','3':'GND','4':'GND','5':'COIL_6V','6':'COIL_6V'},'module',
    {'1':'EN','2':'VIN','3':'GND1','4':'GND2','5':'VOUT1','6':'VOUT2'},
    note='Pololu 4013 only. Two output and two ground pins used. EN tied to VIN. 2.5 mm insulating header gap and support under free edge; coil performance requires bench qualification.')
# U4: top-view left-to-right VIN/GND/VOUT. Bottom drawing is mirrored.
u4=custom('Pololu_U3V16F7_4943',[(1,-2.53,5.28),(2,.01,5.28),(3,2.55,5.28)],(-4.05,-6.55,4.05,6.55))
for pa in u4.Pads():pa.SetDrillSize(pt(1.2,1.2))
add('U4','Pololu U3V16F7 / 7.5V',u4,20,21,{'1':'BAT_RUN','2':'GND','3':'NANO_7V5'},'module',
    {'1':'VIN','2':'GND','3':'VOUT'},note='Pololu 4943 only. Dedicated 7.5 V nominal Nano VIN rail, +/-4%. 2.5 mm insulating header gap. This is not a reader power gate.')
add('J1','PROTECTED 1S BATTERY',custom('Battery_WirePads',[(1,0,0),(2,5,0)]),11,4,
    {'1':'BAT_PROTECTED','2':'GND'},names={'1':'+','2':'-'},note='Existing protected 1S 4.2 V LiPo only. Independent BMS discharge capability and pigtail current must be confirmed; do not connect a bare cell.')
add('F1','3A / 0467003.NR candidate','Fuse:Fuse_1206_3216Metric_Pad1.42x1.75mm_HandSolder',12,10,
    {'1':'BAT_PROTECTED','2':'BAT_FUSED'},'R',note='Candidate fuse, not released: coordinate with cell BMS, harness, operating pulse and measured inrush. Charger and load are both downstream of fuse.')
add('J2','RUN SWITCH / OFF TO CHARGE',custom('RunSwitch_WirePads',[(1,0,0),(2,5,0)]),29,6,
    {'1':'BAT_FUSED','2':'BAT_RUN'},names={'1':'FUSED+','2':'RUN+'},note='External latching SPST >=3 A DC, subject to measured input current. Open to charge. No load sharing; Nano USB disconnected while charging.')

usb='Connector_USB:USB_C_Receptacle_GCT_USB4125-xx-x_6P_TopMnt_Horizontal'
add('J3','USB4125-GF-A / CHARGE ONLY',usb,13,52,
    {'A5':'CC1','B5':'CC2','A9':'USB_VBUS','B9':'USB_VBUS','A12':'GND','B12':'GND','S1':'GND'},
    names={'A5':'CC1','B5':'CC2','A9':'VBUS','B9':'VBUS','A12':'GND','B12':'GND','S1':'SHIELD'},
    note='GCT USB4125-GF-A, 1 mm stake variant. Both CC pins have independent 5.1k Rd. 5 V charging only, no data or PD. Connector overhang needs a new enclosure port.')
rc('R9','5.1k 1%',8,44,'CC1','GND',angle=90)
rc('R10','5.1k 1%',13,44,'CC2','GND',angle=90)
small5='Package_TO_SOT_SMD:SOT-23-5_HandSoldering'
add('U5','NCP361SNT1G',small5,22,49,
    {'1':'USB_VBUS','2':'GND','3':'GND','4':None,'5':'USB_5V_SAFE'},'ic',
    {'1':'IN','2':'GND','3':'EN_LOW','4':'FLAG_NC','5':'OUT'},
    note='TSOP-5 pinout 1 IN / 2 GND / 3 EN / 4 FLAG / 5 OUT. EN grounded. OVP threshold max5.9 V, fast disconnect; verify real hot-plug waveform below MCP73831 absolute7 V. Not battery protection.')
add('U2','MCP73831-2ATI/OT',small5,26,41,
    {'1':'CHG_STAT','2':'GND','3':'BAT_FUSED','4':'USB_5V_SAFE','5':'CHG_PROG'},'ic',
    {'1':'STAT','2':'VSS','3':'VBAT','4':'VDD','5':'PROG'},
    note='4.2 V 1S charger; default RPROG10k ~100 mA to reduce enclosure heating. No cell-temperature sensor, no power path, no BMS. Charge within verified cell temperature limits and with RUN open.')
rc('R11','10k 1% / 100mA',32,38,'CHG_PROG','GND')
rc('R12','2.2k',26,45,'USB_5V_SAFE','CHG_LED_A')
add('D3','CHARGE LED / red','LED_SMD:LED_0805_2012Metric',31,46,{'1':'CHG_STAT','2':'CHG_LED_A'},'diode',{'1':'K','2':'A'},note='On while charger reports charging; off can also mean no USB, no cell or fault, not proof of a full battery.')
# Larger 1206 ceramics leave room for specified effective capacitance at bias.
cbig='Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder'
add('C9','4.7u 50V X7R',cbig,20,44,{'1':'USB_VBUS','2':'GND'},'C',note='Select exact MPN with >=1u effective at20 V, input ESD condition from NCP361 datasheet. Charge source remains5 V USB.')
add('C10','10u 25V X7R',cbig,26,52,{'1':'USB_5V_SAFE','2':'GND'},'C',note='Select exact MPN with >=4.7u effective at5.9 V for charger stability; also NCP361 output bypass.')
add('C11','10u 25V X7R',cbig,27,35,{'1':'BAT_FUSED','2':'GND'},'C',note='Select exact MPN with >=4.7u effective at4.2 V. Charger output bypass close to VBAT.')

left=['SPI_SCK','3V3',None,'BAT_ADC',None,None,None,None,None,None,None,None,None,'GND','NANO_7V5']
right=['SPI_MISO','SPI_MOSI','RFID_SS','LED_GREEN_GPIO','LED_RED_GPIO',None,'BUZZ_GPIO','SOL_GPIO','RFID_RST','WAKE_BTN','ADMIN_BTN','GND',None,None,None]
ln=['D13','3V3','B0','A0','A1','A2','A3','A4','A5','A6','A7','VBUS','B1','GND','VIN']
rn=['D12','D11','D10','D9','D8','D7','D6','D5','D4','D3','D2','GND','RESET','D0','D1']
npads=[(i+1,0,i*2.54) for i in range(15)]+[(i+16,15.24,i*2.54) for i in range(15)]
nano=custom('Nano_ESP32_ABX00083_Sockets',npads,(-1.38,-4,16.62,41))
for pa in nano.Pads(): pa.SetSize(pt(1.7,1.7))
add('U1','Arduino Nano ESP32 ABX00083',nano,39,8,{str(i+1):v for i,v in enumerate(left+right)},'nano',
    {str(i+1):v for i,v in enumerate(ln+rn)},note='Two 1x15 female sockets 2.54 pitch /15.24 row spacing. Nano ESP32 only. VBUS unconnected; 7.5 V to VIN. Reserve14 mm above carrier for socketed module; antenna keepout below.')
add('J5','RC522 / XH8 HARNESS','Connector_JST:JST_XH_B8B-XH-A_1x08_P2.50mm_Vertical',61,7,
    {'1':'RFID_SS','2':'SPI_SCK','3':'SPI_MOSI','4':'SPI_MISO','5':None,'6':'GND','7':'RFID_RST','8':'3V3'},
    names={'1':'SS','2':'SCK','3':'MOSI','4':'MISO','5':'IRQ_NC','6':'GND','7':'RST','8':'3V3'},
    note='JST B8B-XH-A, housing XHP-8. Match RC522 labels individually. RC522 antenna remains separate, with no carrier/battery/metal behind it; enclosure reader mounting must change.')
add('J6','PANEL / PH8 HARNESS','Connector_JST:JST_PH_B8B-PH-K_1x08_P2.00mm_Vertical',64,17,
    {'1':'GND','2':'GND','3':'WAKE_BTN','4':'ADMIN_BTN','5':'LED_RED_A','6':'LED_GREEN_A','7':'3V3','8':'BUZZ_N'},
    names={'1':'GND1','2':'GND2','3':'WAKE','4':'CANCEL','5':'RED_A','6':'GREEN_A','7':'BUZZ+','8':'BUZZ-'},
    note='JST B8B-PH-K-S, housing PHR-8. Distinct pitch from RFID. Normally-open buttons to shared ground, LED cathodes to ground, 3.3 V active buzzer <=30 mA. Label both ends; validate current and polarity.')
add('J4','COIL / XH2 / 6V VERIFY','Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical',85,44,
    {'1':'COIL_6V','2':'COIL_N'},names={'1':'+','2':'SWITCHED-'},angle=90,
    note='JST B2B-XH-A and XHP-2. 6 V ~1 A is an assumption from bench notes. Actual coil rating, resistance, duty and release behavior must be measured.')
add('Q1','AO3400A',Q,81,36,{'1':'SOL_GATE','2':'GND','3':'COIL_N'},'mos',{'1':'G','2':'S','3':'D'},
    note='AOS genuine AO3400A: Rds(on) specified at2.5 V, not an IRF520. Pin1 G/2 S/3 D. Check pulse thermal and drain transient.')
rc('R1','330',77,34,'SOL_GPIO','SOL_GATE'); rc('R2','100k',77,38,'SOL_GATE','GND')
add('D1','SS34',D,78,49,{'1':'COIL_6V','2':'COIL_N'},'diode',{'1':'K','2':'A'},
    note='Flyback cathode/band to6 V. SMA SS34. Simple diode gives slow current decay: check latch release time physically.')
add('C1','470u 10V / EEUFR1A471','Capacitor_THT:CP_Radial_D8.0mm_P3.50mm',81,27,
    {'1':'COIL_6V','2':'GND'},'CP',note='Panasonic EEUFR1A471 exact: D8/H11.5/P3.5 mm. Bulk is transient support, not the source for the whole coil pulse.')
rc('C2','1u 25V',76,26,'COIL_6V','GND','C')
rc('C3','10u 25V',32,15,'NANO_7V5','GND','C')
rc('C4','100n 16V',59,13.2,'3V3','GND','C')
rc('C5','10u 10V',66,13.2,'3V3','GND','C')
add('C8','100u 10V / EEUFR1A101','Capacitor_THT:CP_Radial_D5.0mm_P2.00mm',63,50,
    {'1':'BAT_RUN','2':'GND'},'CP',note='Panasonic EEUFR1A101 exact: D5/H11/P2 mm. Battery/boost input damping near U3; retain short adequately rated battery wiring.')
add('Q2','AO3400A',Q,59,22,{'1':'BUZZ_GATE','2':'GND','3':'BUZZ_N'},'mos',{'1':'G','2':'S','3':'D'})
rc('R3','330',60,26,'BUZZ_GPIO','BUZZ_GATE'); rc('R4','100k',65,26,'BUZZ_GATE','GND')
add('D2','SS14',D,69,23,{'1':'3V3','2':'BUZZ_N'},'diode',{'1':'K','2':'A'},note='Populate flyback for magnetic active buzzer. Buzzer supply3.3 V; qualify module current <=30 mA.')
rc('R5','470',84,14,'LED_RED_GPIO','LED_RED_A'); rc('R6','470',84,18,'LED_GREEN_GPIO','LED_GREEN_A')
rc('R7','100k 1%',31,22,'BAT_RUN','BAT_ADC',angle=90)
rc('R8','100k 1%',31,29,'BAT_ADC','GND',angle=90)
rc('C6','100n 16V',35,29,'BAT_ADC','GND','C',angle=90)
for i,(n,x,y) in enumerate([('BAT_RUN',33,35),('COIL_6V',77,43),('NANO_7V5',35,40),('3V3',59,17),('GND',80,53.25),('BAT_ADC',35,22)],1):
    add('TP'+str(i),n,'TestPoint:TestPoint_Pad_D2.0mm',x,y,{'1':n},'test')
for i,(x,y) in enumerate([(4,4),(86,4),(4,51),(86,51)],1):
    add('H'+str(i),'M3 NPTH','MountingHole:MountingHole_3.2mm_M3',x,y,{},'hole',note='Carrier fixing locations only. New enclosure supports required; mounts must permit top-down installation and connector access.')
rect(board,0,0,90,55,p.Edge_Cuts)
textboard('VELOX B - REVIEW',19,29,.85)
textboard('+',11,2,.8);textboard('-',16,2,.8)
textboard('100mA / RUN OFF',15,38,.8)
textboard('RC522',72,2,.8)
textboard('COIL',86,35,.8);textboard('7V5 VIN',20,16,.8)
# NORA antenna is at the Nano end opposite USB; tracks/pours prohibited.
zone=p.ZONE(board); zone.SetIsRuleArea(True); zone.SetLayerSet(copperlayers()); zone.SetDoNotAllowTracks(True); zone.SetDoNotAllowVias(True); zone.SetDoNotAllowCopperPour(True)
poly=zone.Outline(); poly.NewOutline()
for x,y in [(42,45),(54,45),(54,54),(42,54)]: poly.Append(mm(x),mm(y))
board.Add(zone);rect(board,42,45,54,54,p.Dwgs_User)
textboard('ANTENNA',48,51,.75,p.Dwgs_User)
for f in footprints.values():
    if f.GetReference().startswith('H'): f.Reference().SetVisible(False)

for ref,x,y in [('U1',46.5,5),('J1',13.5,6.6),('J2',31.5,3.8),('R11',32,40.1),('R4',65,28)]:
    footprints[ref].Reference().SetPosition(pt(x,y))

# Save local footprints and preserve exact reference/schematic pin identity.
pretty=OUT/'VELOX.pretty';pretty.mkdir(exist_ok=True)
for ref,f in footprints.items():
    name=str(f.GetFPID().GetLibItemName());p.FootprintSave(str(pretty),f)
    f.SetFPID(p.LIB_ID('VELOX',name))
    next(c for c in comps if c['ref']==ref)['footprint']='VELOX:'+name
(OUT/'fp-lib-table').write_text('(fp_lib_table (lib (name "VELOX")(type "KiCad")(uri "${KIPRJMOD}/VELOX.pretty")(options "")(descr "Rev B local footprints")))\n')
if '--schematic-only' not in sys.argv:
    p.SaveBoard(str(OUT/'VELOX_carrier_B.kicad_pcb'),board)
(OUT/'components.json').write_text(json.dumps(comps,indent=2))


# Native schematic, with individually labeled wires and embedded symbols.
# Generic module/connector blocks expose every connection; discrete parts use IEC symbols.
def q(s): return json.dumps(str(s))
def effects(sz=1.0,extra=''): return f'(effects (font (size {sz} {sz})) {extra})'
symdefs=[]; instances=[]; wires=[]; labels=[]; nc=[]
def symbol(c):
    ref=c['ref']; kind=c['kind']; nm='Part_'+ref; pinlist=list(c['pins']); layout={}; graphics=[]; pins=[]
    if kind=='nano':
        for i in range(15): layout[str(i+1)]=(-30,35-i*5,0)
        for i in range(15): layout[str(i+16)]=(30,35-i*5,180)
        graphics.append('(rectangle (start -25 40)(end 25 -40)(stroke (width .254)(type default))(fill (type background)))')
    elif kind in ['R','C','CP','diode']:
        layout={'1':(-10,0,0),'2':(10,0,180)}
        if kind=='R': graphics.append('(rectangle (start -4 1.5)(end 4 -1.5)(stroke (width .254)(type default))(fill (type none)))')
        elif kind in ['C','CP']:
            for x in [-1,1]: graphics.append(f'(polyline (pts (xy {x} -3)(xy {x} 3))(stroke (width .254)(type default))(fill (type none)))')
            if kind=='CP': graphics.append(f'(text "+" (at -4 3 0) {effects()})')
        else:
            graphics.append('(polyline (pts (xy 3 -3)(xy -3 0)(xy 3 3)(xy 3 -3))(stroke (width .254)(type default))(fill (type none)))')
            graphics.append('(polyline (pts (xy -4 -3)(xy -3 -3)(xy -3 3)(xy -2 3))(stroke (width .254)(type default))(fill (type none)))')
    elif kind=='test':
        layout={'1':(-5,0,0)}
        graphics.append('(circle (center 0 0)(radius 1.5)(stroke (width .254)(type default))(fill (type none)))')
    elif kind=='ic':
        if ref=='U2': layout={'4':(-20,5,0),'5':(-20,-5,0),'3':(20,5,180),'1':(20,-5,180),'2':(20,-15,180)}
        else: layout={'1':(-20,5,0),'3':(-20,-5,0),'2':(-20,-15,0),'5':(20,5,180),'4':(20,-10,180)}
        graphics.append('(rectangle (start -15 20)(end 15 -20)(stroke (width .254)(type default))(fill (type background)))')
    elif kind=='mos':
        layout={'1':(-15,0,0),'2':(15,-5,180),'3':(15,5,180)}
        graphics.append('(rectangle (start -10 9)(end 10 -9)(stroke (width .254)(type default))(fill (type background)))')
        graphics.append(f'(text "N-MOS" (at 0 0 0) {effects()})')
    else:
        for i,pn in enumerate(pinlist): layout[pn]=(-20,(len(pinlist)-1)*2.5-i*5,0)
        h=max(5,len(pinlist)*2.5+1)
        graphics.append(f'(rectangle (start -15 {h})(end 15 {-h})(stroke (width .254)(type default))(fill (type background)))')
    for pn,(x,y,a) in layout.items():
        name=c['names'].get(pn, pn if kind not in ['R','C','CP'] else '~')
        typ='passive'
        if kind=='nano':
            nam=c['names'][pn]; typ='power_in' if nam in ['VIN','GND'] else 'power_out' if nam=='3V3' else 'bidirectional'
        if kind=='ic':
            name=c['names'][pn]
            typ='power_in' if name in ['IN','GND','VSS','VDD'] else 'power_out' if name in ['VBAT','OUT'] else 'tri_state' if name=='STAT' else 'open_collector' if name.startswith('FLAG') else 'passive'
        if kind=='module':
            typ='power_in' if name.startswith('GND') or name=='VIN' else 'power_out' if name in ['VOUT','VOUT1'] else 'input' if name=='EN' else 'passive'
        if kind=='mos' and pn=='1':typ='input'
        length=5
        if kind=='R': length=6
        elif kind in ['C','CP']: length=9
        elif kind=='diode': length=7
        pins.append(f'(pin {typ} line (at {x} {y} {a})(length {length})(name {q(name)} {effects(.9)})(number {q(pn)} {effects(.9)}))')
    bom='no' if kind in ['test','hole'] else 'yes'
    symdefs.append(f'(symbol "VELOX:{nm}" (pin_names (offset .5))(in_bom {bom})(on_board yes)(property "Reference" "{ref}" (at 0 0 0) {effects()})(property "Value" {q(c["value"])} (at 0 0 0) {effects()})(symbol "{nm}_0_1" {"".join(graphics)})(symbol "{nm}_1_1" {"".join(pins)}))')
    return nm,layout

# A2 landscape: readable functional groups, no anonymous global connections.
places={'U1':(65,100),'J5':(65,217),'R7':(70,310),'R8':(70,335),'C6':(70,360),'C4':(70,255),'C5':(70,280),
 'J1':(180,50),'F1':(245,50),'J2':(325,50),
 'J3':(180,135),'U5':(290,125),'U2':(390,125),'R9':(175,183),'R10':(175,207),
 'C9':(250,182),'C10':(478,105),'C11':(478,137),'R11':(340,183),'R12':(400,183),'D3':(470,183),
 'U4':(300,234),'C3':(300,207),'U3':(460,237),'C8':(367,237),
 'J6':(190,298),'R5':(272,272),'R6':(272,296),'Q2':(360,302),'R3':(310,320),'R4':(310,349),'D2':(370,349),
 'Q1':(470,289),'R1':(417,284),'R2':(417,317),'J4':(535,283),'D1':(535,320),'C1':(535,226),'C2':(535,249)}
texts=[(25,15,'VELOX CARRIER REV B | COMPACT ENGINEERING PROTOTYPE',2),
 (25,24,'90 x 55 mm / two layers. Not fabrication-released: battery, coil and enclosure must be qualified.',1.2),
 (25,42,'CONTROLLER / 3.3 V LOGIC',1.4),(160,86,'USB-C CHARGER / 100 mA / RUN OFF',1.4),
 (25,294,'BATTERY MONITOR',1.2),(160,255,'PANEL / LEDS / BUZZER',1.3),
 (400,211,'6 V COIL / SEPARATE FROM NANO VIN',1.2),
 (158,385,'Pololu modules use published top-view hole positions; no MT3608 or TP4056 clone interfaces.',1.1),
 (25,392,'Matching labels connect. Nano ESP32 only; VBUS/B0/B1/D7 unused. Reader always powered: READER_POWER_GATED=0.',1.1),
 (25,400,'Charging: RUN switch open, Nano USB unplugged, verified cell temperature. No concurrent-use power path or cell-temperature cutoff.',1.1),
 (25,33,'Battery must have independent protection. Flyback diode release delay and boost/battery pulse capability require real hardware tests.',1.1)]
ti=0
for c in comps:
    if c['kind']=='hole':places[c['ref']]=(450+(int(c['ref'][1:])-1)*30,340)
    if c['ref'].startswith('TP'):
        places[c['ref']]=(160+ti*53,366); ti+=1
    nm,lay=symbol(c); x,y=(round(v/1.25)*1.25 for v in places[c['ref']])
    off=-44 if c['kind']=='nano' else -(max(5,len(c['pins'])*2.5+1)+6) if c['kind'] not in ['R','C','CP','diode','mos','ic'] else -25 if c['kind']=='ic' else -14 if c['kind']=='mos' else -7
    bom='no' if c['kind'] in ['test','hole'] else 'yes'
    ins=f'(symbol (lib_id "VELOX:{nm}")(at {x} {y} 0)(unit 1)(in_bom {bom})(on_board yes)(dnp no)(uuid {uid(c["ref"])})'
    ins+=f'(property "Reference" {q(c["ref"])} (at {x} {y+off} 0) {effects(1.2)})(property "Value" {q(c["value"])} (at {x} {y+off+3} 0) {effects(1.0)})'
    ins+=f'(property "Footprint" {q(c["footprint"])} (at {x} {y} 0) {effects(1,"hide")})'
    for pn,(px,py,a) in lay.items():
        xx=x+px; yy=y-py; n=c['pins'].get(pn)
        ins+=f'(pin {q(pn)} (uuid {uid(c["ref"]+"pin"+pn)}))'
        if n:
            ex=xx-7.5 if a==0 else xx+7.5
            wires.append(f'(wire (pts (xy {xx} {yy})(xy {ex} {yy}))(stroke (width 0)(type default))(uuid {uid(c["ref"]+pn+"wire")}))')
            labels.append(f'(label {q(n)} (at {ex} {yy} 0) {effects(.95,"(justify right bottom)" if a==0 else "(justify left bottom)")}(uuid {uid(c["ref"]+pn+"label")}))')
        else: nc.append(f'(no_connect (at {xx} {yy})(uuid {uid(c["ref"]+pn+"nc")}))')
    ins+=f'(instances (project "VELOX_carrier_B" (path "/{uid("sheet")}" (reference {q(c["ref"])})(unit 1)))))'
    instances.append(ins)
# Explicit external supplies. BAT_RUN is powered with the external RUN switch
# closed; BAT_PROTECTED is the protected cell connector, not an onboard BMS.
symdefs.append('(symbol "VELOX:PWR_FLAG" (power) (pin_names (offset 0))(in_bom no)(on_board no)'
 '(property "Reference" "#FLG" (at 0 0 0)(effects (font (size 1 1)) hide))'
 '(property "Value" "PWR_FLAG" (at 0 3 0)(effects (font (size 1 1))))'
 '(symbol "PWR_FLAG_0_1" (polyline (pts (xy 0 0)(xy 0 1)(xy -1 2)(xy 0 3)(xy 1 2)(xy 0 1))(stroke (width .254)(type default))(fill (type none))))'
 '(symbol "PWR_FLAG_1_1" (pin power_out line (at 0 0 90)(length 0)(name "pwr" (effects (font (size 1 1))))(number "1" (effects (font (size 1 1)))))))')
for i,n in enumerate(['GND','USB_VBUS','BAT_PROTECTED','BAT_RUN'],1):
    x=145+i*65;y=375;ref=f'#FLG010{i}'
    instances.append(f'(symbol (lib_id "VELOX:PWR_FLAG")(at {x} {y} 0)(unit 1)(in_bom no)(on_board no)(uuid {uid(ref)})'
      f'(property "Reference" "{ref}" (at {x} {y} 0){effects(1,"hide")})'
      f'(property "Value" "PWR_FLAG" (at {x} {y-4} 0){effects(.8)})'
      f'(pin "1" (uuid {uid(ref+"pin1")}))'
      f'(instances (project "VELOX_carrier_B" (path "/{uid("sheet")}" (reference "{ref}")(unit 1)))))')
    labels.append(f'(label "{n}" (at {x} {y} 0){effects(.8,"(justify left bottom)")}(uuid {uid(ref+"label")}))')
sch=f'(kicad_sch (version 20230121)(generator eeschema)(uuid {uid("sheet")})(paper "A2") (lib_symbols {"".join(symdefs)})'
sch+=''.join(instances+wires+labels+nc)
for i,(x,y,t,sz) in enumerate(texts): sch+=f'(text {q(t)} (at {x} {y} 0) {effects(sz,"(justify left)")}(uuid {uid("text"+str(i))}))'
sch+='(sheet_instances (path "/" (page "1"))))'
def schematic_grid(s):
    # 1.25 mm drawing units -> the standard 1.27 mm / 50 mil connection grid.
    # Move symbols and their wires together; never suppress off-grid ERC rules.
    number=r'(-?(?:\d+(?:\.\d*)?|\.\d+))'
    s=re.sub(r'\((at|xy|start|end|center) '+number+' '+number,
        lambda m:f'({m[1]} {float(m[2])*1.016:.6f} {float(m[3])*1.016:.6f}',s)
    return re.sub(r'\((length|radius) '+number,
        lambda m:f'({m[1]} {float(m[2])*1.016:.6f}',s)
(OUT/'VELOX_carrier_B.kicad_sch').write_text(schematic_grid(sch))
(OUT/'VELOX.kicad_sym').write_text(schematic_grid('(kicad_symbol_lib (version 20220914)(generator kicad_symbol_editor)'+''.join(s.replace('(symbol "VELOX:', '(symbol "',1) for s in symdefs)+')'))
(OUT/'sym-lib-table').write_text('(sym_lib_table (lib (name "VELOX")(type "KiCad")(uri "${KIPRJMOD}/VELOX.kicad_sym")(options "")(descr "Embedded project symbols")))\n')
print('Generated',len(comps),'components,',len(nets),'nets')
