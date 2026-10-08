"""Generate VELOX carrier Rev A, a review prototype, using KiCad 7 pcbnew.
Run with Python 3.12 + pcbnew, numpy. Board dimensions are proposed, not enclosure approval.
"""
from pathlib import Path
import sys, json, uuid, math, re, csv
sys.path.append('/usr/lib/python3/dist-packages')
import pcbnew as p

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'design'; OUT.mkdir(exist_ok=True)
PRE=ROOT/'previews'; PRE.mkdir(exist_ok=True)
LIB=Path('/usr/share/kicad/footprints')
def uid(s): return str(uuid.uuid5(uuid.NAMESPACE_URL,'velox-pcb-revA/'+s))
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
        q=p.PAD(f); q.SetNumber(str(num)); q.SetPosition(pt(x,y)); q.SetPos0(pt(x,y)); q.SetSize(pt(2,2)); q.SetDrillSize(pt(1,1)); q.SetAttribute(p.PAD_ATTRIB_PTH); q.SetShape(p.PAD_SHAPE_CIRCLE); q.SetLayerSet(padlayers()); f.Add(q)
    if body: rect(f,*body,p.F_Fab); rect(f,*body,p.F_SilkS)
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
    board.Add(f); footprints[ref]=f
    comps.append(dict(ref=ref,value=val,footprint=fid,pins=pin_nets,kind=kind,names=names or {},x=x,y=y,angle=angle,note=note))
    return f
R='Resistor_SMD:R_0805_2012Metric_Pad1.20x1.40mm_HandSolder'
C='Capacitor_SMD:C_0805_2012Metric_Pad1.18x1.45mm_HandSolder'
Q='Package_TO_SOT_SMD:SOT-23'
D='Diode_SMD:D_SMA'
def rc(ref,val,x,y,a,b,kind='R',angle=0): return add(ref,val,R if kind=='R' else C,x,y,{'1':a,'2':b},kind,angle=angle)

# Module pin numbers are OUR wire-pad interface; not a claim about clone pad locations.
add('U2','Protected TP4056 MODULE',custom('TP4056_WireMounted',[(1,-17,-5),(2,-17,5),(3,17,-5),(4,17,5)],(-14.5,-8.5,14.5,8.5)),21,17,
    {'1':'CELL_P','2':'CELL_N','3':'PROTECTED_BAT','4':'GND'},'module',{'1':'B+','2':'B-','3':'OUT+','4':'OUT-'},note='USB-C on module. Insulated mount + four short wires. Charge only with RUN switch OFF; verify module and cell.')
add('U3','MT3608 MODULE / QUALIFY',custom('MT3608_WireMounted',[(1,-18,-13),(2,-10,-13),(3,10,12),(4,18,12)],(-18,-8.5,18,8.5)),22,43,
    {'1':'BAT_RUN','2':'GND','3':'COIL_6V','4':'GND'},'module',{'1':'IN+','2':'IN-','3':'OUT+','4':'OUT-'},note='Set unloaded before connecting. 6.0 V target; actual loaded capacity and Nano VIN minimum are release blockers.')
add('J1','BATTERY 1S / POLARITY',custom('Battery_WirePads',[(1,0,0),(2,5,0)]),18,4,{'1':'CELL_P','2':'CELL_N'},names={'1':'+','2':'-'},note='Protected 1S 4.2 V maximum cell; retain its existing pigtail, verify polarity/current.')
add('F1','3 A provisional', 'Fuse:Fuse_1206_3216Metric_Pad1.42x1.75mm_HandSolder',43,11,{'1':'PROTECTED_BAT','2':'FUSED_BAT'},'R',note='Select exact fuse after pulse/inrush and battery qualification. Not a substitute for battery protection.')
add('J11','RUN SWITCH / OFF TO CHARGE',custom('RunSwitch_WirePads',[(1,0,0),(2,5,0)]),46,57,{'1':'FUSED_BAT','2':'BAT_RUN'},names={'1':'FUSED','2':'RUN'},note='External latching SPST rated >=3 A DC. Disconnect Nano USB when charging.')

left=['SPI_SCK','3V3',None,'BAT_ADC',None,None,None,None,None,None,None,None,None,'GND','COIL_6V']
right=['SPI_MISO','SPI_MOSI','RFID_SS','LED_GREEN_GPIO','LED_RED_GPIO',None,'BUZZ_GPIO','SOL_GPIO','RFID_RST','WAKE_BTN','ADMIN_BTN','GND',None,None,None]
ln=['D13','3V3','B0','A0','A1','A2','A3','A4','A5','A6','A7','VBUS','B1','GND','VIN']
rn=['D12','D11','D10','D9','D8','D7','D6','D5','D4','D3','D2','GND','RESET','D0','D1']
npads=[(i+1,0,i*2.54) for i in range(15)]+[(i+16,15.24,i*2.54) for i in range(15)]
nano=custom('Nano_ESP32_ABX00083_Sockets',npads,(-1.38,-4,16.62,41))
for pa in nano.Pads(): pa.SetSize(pt(1.7,1.7))
add('U1','Arduino Nano ESP32 ABX00083',nano,55,8,{str(i+1):v for i,v in enumerate(left+right)},'nano',{str(i+1):v for i,v in enumerate(ln+rn)},note='Two 1x15 female sockets, 2.54 pitch, 15.24 row spacing. USB at top. Nano ESP32 only; VBUS/B0/B1 unused.')

add('J5','RC522 / CUSTOM HARNESS','Connector_JST:JST_XH_B8B-XH-A_1x08_P2.50mm_Vertical',79,8,
    {'1':'RFID_SS','2':'SPI_SCK','3':'SPI_MOSI','4':'SPI_MISO','5':None,'6':'GND','7':'RFID_RST','8':'3V3'},names={'1':'SS','2':'SCK','3':'MOSI','4':'MISO','5':'IRQ_NC','6':'GND','7':'RST','8':'3V3'},note='Map by RC522 silkscreen, not cable colors. Reader mounted separately near plastic lid. No copper behind antenna.')
for ref,val,y,ns in [('J6','WAKE / GREEN',18,['WAKE_BTN','GND']),('J7','CANCEL / RED',27,['ADMIN_BTN','GND']),('J8','RED LED',36,['LED_RED_A','GND']),('J9','GREEN LED',45,['LED_GREEN_A','GND']),('J10','BUZZER / 3.3 V ACTIVE',54,['3V3','BUZZ_N'])]:
    add(ref,val,'Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical',104,y,{'1':ns[0],'2':ns[1]},angle=90,note='Verify external component voltage/polarity; momentary buttons normally open to ground.' if ref in ['J6','J7'] else 'Verify external part current, polarity and voltage.')
add('J4','SOLENOID 6 V / VERIFY','Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical',88,59,{'1':'COIL_6V','2':'COIL_N'},names={'1':'+','2':'SWITCHED-'},note='Actual coil voltage/current and pulse rating must be verified. Assumed 6 V ~1 A from BENCH_BUILD, not BOM 300 mA.')
add('Q1','AO3400A',Q,87,47,{'1':'SOL_GATE','2':'GND','3':'COIL_N'},'mos',{'1':'G','2':'S','3':'D'},note='AOS AO3400A specified Rds(on) at 2.5 V. Pin 1 G, 2 S, 3 D. Check pulse thermal and voltage transient.')
rc('R1','100',80,45,'SOL_GPIO','SOL_GATE'); rc('R2','100k',80,49,'SOL_GATE','GND')
add('D1','SS34',D,88,52,{'1':'COIL_6V','2':'COIL_N'},'diode',{'1':'K','2':'A'},note='Flyback cathode/band to COIL_6V. SMA package. Validate release time with real spring/latch.')
add('C1','1000u / 16V', 'Capacitor_THT:CP_Radial_D10.0mm_P5.00mm',87,36,{'1':'COIL_6V','2':'GND'},'CP',note='Provisional radial D10 P5, maximum height 20 mm; exact capacitor required before order.')
rc('C2','1u / 25V',81,40,'COIL_6V','GND','C')
rc('C3','10u / 25V',49,44,'COIL_6V','GND','C')
rc('C4','100n / 16V',75,13,'3V3','GND','C',angle=90)
rc('C5','10u / 10V',80,13,'3V3','GND','C')
add('Q2','AO3400A',Q,91,24,{'1':'BUZZ_GATE','2':'GND','3':'BUZZ_N'},'mos',{'1':'G','2':'S','3':'D'})
rc('R3','100',85,21,'BUZZ_GPIO','BUZZ_GATE'); rc('R4','100k',85,27,'BUZZ_GATE','GND')
add('D2','SS14',D,97,25,{'1':'3V3','2':'BUZZ_N'},'diode',{'1':'K','2':'A'})
rc('R5','220',94,16,'LED_RED_GPIO','LED_RED_A')
rc('R6','220',94,19,'LED_GREEN_GPIO','LED_GREEN_A')
rc('R7','100k 1%',47,22,'BAT_RUN','BAT_ADC',angle=90)
rc('R8','100k 1%',47,29,'BAT_ADC','GND',angle=90)
rc('C6','100n / 16V',51,29,'BAT_ADC','GND','C',angle=90)
for i,(n,x,y) in enumerate([('BAT_RUN',45,36),('COIL_6V',76,58),('3V3',76,19),('GND',98,59),('BAT_ADC',51,22)],1):
    add('TP'+str(i),n,'TestPoint:TestPoint_Pad_D2.0mm',x,y,{'1':n},'test')
for i,(x,y) in enumerate([(4,4),(106,4),(4,61),(106,61)],1):
    add('H'+str(i),'M3 NPTH','MountingHole:MountingHole_3.2mm_M3',x,y,{},'hole',note='Proposed board mounts; enclosure mounting not yet redesigned.')
rect(board,0,0,110,65,p.Edge_Cuts)
textboard('VELOX CARRIER A - REVIEW ONLY',56,62,1)
textboard('USB',63,2.5,.85)
textboard('OFF TO CHARGE',24,28,.85)
textboard('6V VERIFY',28,58,.85)

# Keep copper away from the Nano antenna region; generous preliminary keepout.
zone=p.ZONE(board); zone.SetIsRuleArea(True); zone.SetLayerSet(copperlayers()); zone.SetDoNotAllowTracks(True); zone.SetDoNotAllowVias(True); zone.SetDoNotAllowCopperPour(True)
poly=zone.Outline(); poly.NewOutline()
for x,y in [(58,45),(69,45),(69,51),(58,51)]: poly.Append(mm(x),mm(y))
board.Add(zone); rect(board,58,45,69,51,p.Dwgs_User)
textboard('ANTENNA',63.5,48,.75,p.Dwgs_User)
for h in ['H1','H2','H3','H4']: footprints[h].Reference().SetVisible(False)
for ref,x,y in [('U1',63,6),('J1',20.5,6.5),('J11',48.5,54.5),('J7',100,28.5),('C5',83,14.5)]:
    footprints[ref].Reference().SetPosition(pt(x,y))
for ref in ['U2','U3']: textboard(ref+' INSULATED MODULE',comps[[c['ref'] for c in comps].index(ref)]['x'],17 if ref=='U2' else 43,.8,p.Dwgs_User)

# Save project-local copies so no external footprint library is required to edit.
pretty=OUT/'VELOX.pretty'; pretty.mkdir(exist_ok=True)
for ref,f in footprints.items():
    name=str(f.GetFPID().GetLibItemName()); p.FootprintSave(str(pretty),f)
    f.SetFPID(p.LIB_ID('VELOX',name))
    next(c for c in comps if c['ref']==ref)['footprint']='VELOX:'+name
(OUT/'fp-lib-table').write_text('(fp_lib_table (lib (name "VELOX")(type "KiCad")(uri "${KIPRJMOD}/VELOX.pretty")(options "")(descr "Local project footprints")))\n')
p.SaveBoard(str(OUT/'VELOX_carrier_A.kicad_pcb'),board)
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
        length=5
        if kind=='R': length=6
        elif kind in ['C','CP']: length=9
        elif kind=='diode': length=7
        pins.append(f'(pin {typ} line (at {x} {y} {a})(length {length})(name {q(name)} {effects(.9)})(number {q(pn)} {effects(.9)}))')
    symdefs.append(f'(symbol "VELOX:{nm}" (pin_names (offset .5))(in_bom yes)(on_board yes)(property "Reference" "{ref}" (at 0 0 0) {effects()})(property "Value" {q(c["value"])} (at 0 0 0) {effects()})(symbol "{nm}_0_1" {"".join(graphics)})(symbol "{nm}_1_1" {"".join(pins)}))')
    return nm,layout

# A2 landscape: readable functional groups, no anonymous global connections.
places={'U1':(78,105),'U2':(210,57),'U3':(320,57),'J1':(210,25),'F1':(260,43),'J11':(260,88),
 'J5':(80,205),'J6':(180,157),'J7':(180,185),'J8':(286,158),'J9':(286,185),'J10':(446,220),'J4':(446,68),
 'Q1':(395,90),'R1':(347,85),'R2':(350,114),'D1':(445,112),'C1':(495,60),'C2':(495,87),'C3':(495,114),
 'Q2':(395,204),'R3':(347,199),'R4':(350,228),'D2':(445,250),'R5':(240,145),'R6':(240,174),
 'R7':(210,255),'R8':(210,278),'C6':(210,301),'C4':(78,247),'C5':(78,274)}
texts=[(25,15,'VELOX CARRIER REV A | ENGINEERING REVIEW - NOT FOR FABRICATION',2),
 (25,30,'Nano ESP32 + RC522; existing firmware pin names retained. All GND labels are protected OUT-.',1.2),
 (160,115,'U2 / U3: wire-mounted modules. Pin numbers refer to carrier pads, NOT clone pad geometry.',1.1),
 (160,121,'Charge with RUN switch OFF and Nano USB disconnected. No simultaneous-use power path.',1.1),
 (330,135,'6 V coil assumed from bench notes. Verify current, boost capacity, Nano VIN and release time.',1.1),
 (25,310,'Matching labels are electrically connected. NC crosses mark intentionally unused pins.',1.1),
 (25,317,'RC522 is always powered in Rev A; READER_POWER_GATED=0. D7 reserved.',1.1),
 (25,324,'Do not substitute a classic Nano. B0/B1 are boot pins, not AVR AREF/RESET.',1.1),
 (25,331,'Connector pin 1 is identified on the PCB. External LEDs: anode on pin 1. Buttons: normally open.',1.1)]
ti=0
for c in comps:
    if c['kind']=='hole': continue
    if c['ref'].startswith('TP'):
        places[c['ref']]=(330+ti*43,294); ti+=1
    nm,lay=symbol(c); x,y=places[c['ref']]
    off=-44 if c['kind']=='nano' else -(max(5,len(c['pins'])*2.5+1)+6) if c['kind'] not in ['R','C','CP','diode','mos'] else -14 if c['kind']=='mos' else -7
    ins=f'(symbol (lib_id "VELOX:{nm}")(at {x} {y} 0)(unit 1)(in_bom yes)(on_board yes)(dnp no)(uuid {uid(c["ref"])})'
    ins+=f'(property "Reference" {q(c["ref"])} (at {x} {y+off} 0) {effects(1.2)})(property "Value" {q(c["value"])} (at {x} {y+off+3} 0) {effects(1.0)})'
    ins+=f'(property "Footprint" {q(c["footprint"])} (at {x} {y} 0) {effects(1,"hide")})'
    for pn,(px,py,a) in lay.items():
        xx=x+px; yy=y-py; n=c['pins'].get(pn)
        ins+=f'(pin {q(pn)} (uuid {uid(c["ref"]+"pin"+pn)}))'
        if n:
            ex=xx-7.5 if a==0 else xx+7.5
            wires.append(f'(wire (pts (xy {xx} {yy})(xy {ex} {yy}))(stroke (width 0)(type default))(uuid {uid(c["ref"]+pn+"wire")}))')
            labels.append(f'(label {q(n)} (at {ex} {yy} 0) {effects(.95,"(justify left bottom)")}(uuid {uid(c["ref"]+pn+"label")}))')
        else: nc.append(f'(no_connect (at {xx} {yy})(uuid {uid(c["ref"]+pn+"nc")}))')
    ins+=f'(instances (project "VELOX_carrier_A" (path "/{uid("sheet")}" (reference {q(c["ref"])})(unit 1)))))'
    instances.append(ins)
sch=f'(kicad_sch (version 20230121)(generator eeschema)(uuid {uid("sheet")})(paper "A2") (lib_symbols {"".join(symdefs)})'
sch+=''.join(instances+wires+labels+nc)
for i,(x,y,t,sz) in enumerate(texts): sch+=f'(text {q(t)} (at {x} {y} 0) {effects(sz,"(justify left)")}(uuid {uid("text"+str(i))}))'
sch+='(sheet_instances (path "/" (page "1"))))'
(OUT/'VELOX_carrier_A.kicad_sch').write_text(sch)
(OUT/'VELOX.kicad_sym').write_text('(kicad_symbol_lib (version 20220914)(generator kicad_symbol_editor)'+''.join(s.replace('(symbol "VELOX:', '(symbol "',1) for s in symdefs)+')')
(OUT/'sym-lib-table').write_text('(sym_lib_table (lib (name "VELOX")(type "KiCad")(uri "${KIPRJMOD}/VELOX.kicad_sym")(options "")(descr "Embedded project symbols")))\n')
print('Generated',len(comps),'components,',len(nets),'nets')
