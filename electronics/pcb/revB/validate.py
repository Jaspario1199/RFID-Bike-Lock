"""Native KiCad 9 ERC/DRC/parity and independent interface checks.
Does not change CAD files. Physical hardware testing remains separate.
"""
from pathlib import Path
import sys,json,xml.etree.ElementTree as ET,re,subprocess,math,hashlib
sys.path.append('/usr/lib/python3/dist-packages')
import pcbnew as p
R=Path(__file__).resolve().parent;D=R/'design';fn=D/'VELOX_carrier_B.kicad_pcb'
subprocess.run(['kicad-cli','sch','export','netlist','--format','kicadxml','-o',str(D/'VELOX_carrier_B.xml'),str(D/'VELOX_carrier_B.kicad_sch')],check=True)
b=p.LoadBoard(str(fn))
for args in [
 ['sch','erc','--format','json','--severity-all','--exit-code-violations','-o',str(R/'erc.json'),str(D/'VELOX_carrier_B.kicad_sch')],
 ['pcb','drc','--format','json','--severity-all','--all-track-errors','--schematic-parity','--exit-code-violations','-o',str(R/'drc.json'),str(fn)]]:
    result=subprocess.run(['kicad-cli']+args)
    if result.returncode not in [0,5]:raise RuntimeError('KiCad checker did not complete')
parts=json.loads((D/'components.json').read_text());expected={}
for c in parts:
    for pin,n in c['pins'].items():
        if n:expected[(c['ref'],pin)]=n
root=ET.parse(D/'VELOX_carrier_B.xml').getroot();actual={}
for n in root.find('nets'):
    for pin in n.findall('node'):actual[(pin.attrib['ref'],pin.attrib['pin'])]=n.attrib['name'].lstrip('/')
sch_mismatch=[(k,n,actual.get(k)) for k,n in expected.items() if actual.get(k)!=n]
bp={(f.GetReference(),d.GetNumber()):d.GetNetname().lstrip('/') for f in b.GetFootprints() for d in f.Pads()}
pcb_mismatch=[(k,n,bp.get(k)) for k,n in expected.items() if bp.get(k)!=n]
nc_expected={(c['ref'],pin):f'unconnected-({c["ref"]}-{c["names"].get(pin,pin)}-Pad{pin})' for c in parts for pin,n in c['pins'].items() if not n}
extra=[(k,v) for k,v in bp.items() if v and k not in expected and k not in nc_expected]
nc_errors=[(k,n,bp.get(k),actual.get(k)) for k,n in nc_expected.items() if bp.get(k)!=n or actual.get(k)!=n]
for k,n in nc_expected.items():
    if list(bp.values()).count(n)!=1 or any(t.GetNetname()==n for t in b.GetTracks()):
        nc_errors.append((k,'NC net must have exactly one pad and no copper routes'))

# Manufacturer interfaces independently recorded from primary documents.
critical={
 'U2':{'1':'CHG_STAT','2':'GND','3':'BAT_FUSED','4':'USB_5V_SAFE','5':'CHG_PROG'},
 'U5':{'1':'USB_VBUS','2':'GND','3':'GND','4':'','5':'USB_5V_SAFE'},
 'U3':{'1':'BAT_RUN','2':'BAT_RUN','3':'GND','4':'GND','5':'COIL_6V','6':'COIL_6V'},
 'U4':{'1':'BAT_RUN','2':'GND','3':'NANO_7V5'},
 'Q1':{'1':'SOL_GATE','2':'GND','3':'COIL_N'},
 'Q2':{'1':'BUZZ_GATE','2':'GND','3':'BUZZ_N'},
 'D1':{'1':'COIL_6V','2':'COIL_N'},'D2':{'1':'3V3','2':'BUZZ_N'},
 'U1':{'1':'SPI_SCK','2':'3V3','3':'','4':'BAT_ADC','12':'','13':'','14':'GND','15':'NANO_7V5',
       '16':'SPI_MISO','17':'SPI_MOSI','18':'RFID_SS','19':'LED_GREEN_GPIO','20':'LED_RED_GPIO',
       '21':'','22':'BUZZ_GPIO','23':'SOL_GPIO','24':'RFID_RST','25':'WAKE_BTN','26':'ADMIN_BTN','27':'GND'},
 'J3':{'A5':'CC1','B5':'CC2','A9':'USB_VBUS','B9':'USB_VBUS','A12':'GND','B12':'GND','S1':'GND'}}
interface_errors=[(ref,pin,n,bp.get((ref,pin))) for ref,pins in critical.items() for pin,n in pins.items() if bp.get((ref,pin))!=(n or nc_expected.get((ref,pin)))]
fs={f.GetReference():f for f in b.GetFootprints()}
geometry_errors=[];interfaces=json.loads((R/'interfaces.json').read_text())
for ref,w,h in [('U3',15.2,15.2),('U4',8.1,13.1)]:
    f=fs[ref];origin=f.GetPosition();spec=interfaces[ref+'_top_view']
    for i,expected_xy in enumerate(spec['hole_xy_from_top_left_mm'],1):
        pad=next(a for a in f.Pads() if a.GetNumber()==str(i));pos=pad.GetPosition()
        measured=[p.ToMM(pos.x-origin.x)+w/2,p.ToMM(pos.y-origin.y)+h/2]
        if math.dist(measured,expected_xy)>.005:geometry_errors.append((ref,i,expected_xy,measured))
        if abs(p.ToMM(pad.GetDrillSize().x)-spec['carrier_plated_drill_mm'])>.001:
            geometry_errors.append((ref,i,'carrier drill mismatch'))

drc=json.loads((R/'drc.json').read_text());erc=json.loads((R/'erc.json').read_text())
erc_issues=[v for sheet in erc['sheets'] for v in sheet['violations']]
counts={'DRC violations':len(drc['violations']),'unconnected pads':len(drc['unconnected_items']),
        'schematic parity issues':len(drc['schematic_parity']),'ERC violations':len(erc_issues)}
errors=sch_mismatch+pcb_mismatch+extra+nc_errors+interface_errors+geometry_errors
value_errors=[(c['ref'],c['value'],fs[c['ref']].GetValue()) for c in parts if c['value']!=fs[c['ref']].GetValue()]
errors+=value_errors
passed=not errors and not any(counts.values())
result=dict(status='REVIEW_PROTOTYPE_NOT_FOR_FABRICATION',digital_geometry_checks='PASS' if passed else 'FAIL',
 pins_checked=len(expected),isolated_NC_pins_checked=len(nc_expected),functional_nets=len(set(expected.values())),schematic_mismatch=sch_mismatch,pcb_mismatch=pcb_mismatch,
 extra_pcb_nets=extra,nc_errors=nc_errors,manufacturer_interface_errors=interface_errors,
 manufacturer_hole_geometry_errors=geometry_errors,component_value_errors=value_errors,**counts,
 clearance_mm=.2,minimum_track_mm=.25,copper_edge_clearance_mm=.5,board_mm=[90,55,1.6],
 area_reduction_vs_revA_percent=round(100*(1-(90*55)/(110*65)),2),
 erc='Native KiCad '+erc['kicad_version']+' ERC, all severities; no exclusions.',
 drc='Native KiCad '+drc['kicad_version']+' DRC, all severities, all track errors, schematic parity; no exclusions.',
 source_sha256={str(f.relative_to(R)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(D.rglob('*')) if f.is_file() and f.suffix in ['.kicad_pcb','.kicad_sch','.kicad_sym','.kicad_mod','.kicad_pro']},
 physical_validation='Not performed. See mechanical/placement_report.json for envelope-only review.',
 outstanding=interfaces['release_inputs_missing']+['Fabrication-capability review','Loaded rail/transient/thermal/charging/RFID/installation prototype tests'])
(R/'validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
(R/'drc.txt').write_text('Summary of native KiCad JSON reports; see drc.json and erc.json for original reports.\n'+''.join(f'{k}: {v}\n' for k,v in counts.items()))
sys.exit(0 if passed else 1)
