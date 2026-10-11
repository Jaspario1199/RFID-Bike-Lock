from pathlib import Path
import json,uuid,re
ROOT=Path(__file__).resolve().parent; OUT=ROOT/"design"
def uid(s):return str(uuid.uuid5(uuid.NAMESPACE_URL,"velox-pcb-revV/"+s))
comps=json.loads((OUT/"components.json").read_text())
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
    elif kind in ['R','C','CP','diode','jumper']:
        layout={'1':(-10,0,0),'2':(10,0,180)}
        if kind in ['R','jumper']: graphics.append('(rectangle (start -4 1.5)(end 4 -1.5)(stroke (width .254)(type default))(fill (type none)))')
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
places={'U1':(65,100),'J1':(180,70),'J5':(300,75),'J6':(460,75),
'R1':(175,165),'R7':(290,165),'R8':(290,190),'C6':(290,215),'C3':(175,195),
'C4':(175,230),'C5':(175,255),'R5':(450,165),'R6':(450,190),'Q2':(450,260),'R3':(345,260),'R4':(345,290),'D2':(535,260)}
texts=[(20,15,'VELOX REV V | FEDC V-ONE CONTROL CARRIER',2),
(20,24,'Two printed ink layers, connected by copper rivets. No coil current is routed through this carrier.',1.2),
(20,33,'J1: external regulated 7.5V / common ground / switched protected battery monitor / solenoid gate.',1.2),
(20,405,'Coil power, battery fuse/switch, charger and regulators remain external. See SYSTEM_WIRING.md.',1.2)]
ti=0
for c in comps:
    if c['kind']=='hole':places[c['ref']]=(430+(int(c['ref'][1:])-1)*35,365)
    if c['kind']=='jumper':places[c['ref']]=(35+(int(c['ref'][2:])-1)%7*80,345+((int(c['ref'][2:])-1)//7)*25)
    if c['ref'].startswith('TP'):
        places[c['ref']]=(160+ti*53,366); ti+=1
    nm,lay=symbol(c); x,y=(round(v/1.25)*1.25 for v in places[c['ref']])
    off=-44 if c['kind']=='nano' else -(max(5,len(c['pins'])*2.5+1)+6) if c['kind'] not in ['R','C','CP','diode','jumper','mos','ic'] else -25 if c['kind']=='ic' else -14 if c['kind']=='mos' else -7
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
    ins+=f'(instances (project "VELOX_carrier_V" (path "/{uid("sheet")}" (reference {q(c["ref"])})(unit 1)))))'
    instances.append(ins)
# Explicit external supplies. BAT_RUN is powered with the external RUN switch
# closed; BAT_PROTECTED is the protected cell connector, not an onboard BMS.
symdefs.append('(symbol "VELOX:PWR_FLAG" (power) (pin_names (offset 0))(in_bom no)(on_board no)'
 '(property "Reference" "#FLG" (at 0 0 0)(effects (font (size 1 1)) hide))'
 '(property "Value" "PWR_FLAG" (at 0 3 0)(effects (font (size 1 1))))'
 '(symbol "PWR_FLAG_0_1" (polyline (pts (xy 0 0)(xy 0 1)(xy -1 2)(xy 0 3)(xy 1 2)(xy 0 1))(stroke (width .254)(type default))(fill (type none))))'
 '(symbol "PWR_FLAG_1_1" (pin power_out line (at 0 0 90)(length 0)(name "pwr" (effects (font (size 1 1))))(number "1" (effects (font (size 1 1)))))))')
for i,n in enumerate(['GND','NANO_7V5','BAT_MON'],1):
    x=145+i*65;y=375;ref=f'#FLG010{i}'
    instances.append(f'(symbol (lib_id "VELOX:PWR_FLAG")(at {x} {y} 0)(unit 1)(in_bom no)(on_board no)(uuid {uid(ref)})'
      f'(property "Reference" "{ref}" (at {x} {y} 0){effects(1,"hide")})'
      f'(property "Value" "PWR_FLAG" (at {x} {y-4} 0){effects(.8)})'
      f'(pin "1" (uuid {uid(ref+"pin1")}))'
      f'(instances (project "VELOX_carrier_V" (path "/{uid("sheet")}" (reference "{ref}")(unit 1)))))')
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
(OUT/'VELOX_carrier_V.kicad_sch').write_text(schematic_grid(sch))
(OUT/'VELOX.kicad_sym').write_text(schematic_grid('(kicad_symbol_lib (version 20220914)(generator kicad_symbol_editor)'+''.join(s.replace('(symbol "VELOX:', '(symbol "',1) for s in symdefs)+')'))
(OUT/'sym-lib-table').write_text('(sym_lib_table (lib (name "VELOX")(type "KiCad")(uri "${KIPRJMOD}/VELOX.kicad_sym")(options "")(descr "Embedded project symbols")))\n')
print('Generated native schematic',len(comps),'components')
