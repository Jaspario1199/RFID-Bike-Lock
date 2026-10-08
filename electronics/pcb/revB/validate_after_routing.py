"""Native validation for the final routed Rev B. No pass is recorded until this runs.
Run after build_board.py and copper routing. KiCad 7 GUI ERC is a separate release gate.
"""
from pathlib import Path
import sys, json, subprocess, xml.etree.ElementTree as ET, re
sys.path.append('/usr/lib/python3/dist-packages')
import pcbnew as p
ROOT=Path(__file__).resolve().parent;D=ROOT/'design'
fn=D/'VELOX_carrier_B.kicad_pcb'
if not fn.exists(): raise SystemExit('Missing board: run build_board.py, then route it. No DRC has run.')
subprocess.run(['kicad-cli','sch','export','netlist','--format','kicadxml','-o',str(D/'VELOX_carrier_B.xml'),str(D/'VELOX_carrier_B.kicad_sch')],check=True)
b=p.LoadBoard(str(fn));ds=b.GetDesignSettings()
ds.m_MinClearance=p.FromMM(.2);ds.m_CopperEdgeClearance=p.FromMM(.5)
ds.m_TrackMinWidth=p.FromMM(.25);ds.m_ViasMinSize=p.FromMM(.6);ds.m_MinThroughDrill=p.FromMM(.3)
ds.m_HoleClearance=p.FromMM(.25);ds.m_HoleToHoleMin=p.FromMM(.25)
p.WriteDRCReport(b,str(ROOT/'drc.txt'),p.EDA_UNITS_MILLIMETRES,True)
parts=json.loads((ROOT/'design_spec.json').read_text())['parts']
expected={(c['ref'],pn):n for c in parts for pn,n in c['pins'].items() if n}
unused={(c['ref'],pn) for c in parts for pn,n in c['pins'].items() if not n}
xml=ET.parse(D/'VELOX_carrier_B.xml').getroot()
actual={(node.attrib['ref'],node.attrib['pin']):n.attrib['name'].lstrip('/') for n in xml.find('nets') for node in n.findall('node') if not node.attrib['ref'].startswith('#')}
bp={(f.GetReference(),pad.GetNumber()):pad.GetNetname().lstrip('/') for f in b.GetFootprints() for pad in f.Pads() if pad.GetNetname()}
sm=[{'pin':list(k),'expected':n,'actual':actual.get(k)} for k,n in expected.items() if actual.get(k)!=n]
pm=[{'pin':list(k),'expected':n,'actual':bp.get(k)} for k,n in expected.items() if bp.get(k)!=n]
extra=[{'pin':list(k),'net':n} for k,n in bp.items() if k not in expected]
nc_bad=[list(k) for k in unused if k in bp]
# Independently transcribed interface contracts, not generated from the source part list.
contracts={
'U1':{'1':'SPI_SCK','2':'3V3','4':'BAT_ADC','14':'GND','15':'NANO_7V5','16':'SPI_MISO','17':'SPI_MOSI','18':'RFID_SS','19':'LED_GREEN_GPIO','20':'LED_RED_GPIO','22':'BUZZ_GPIO','23':'SOL_GPIO','24':'RFID_RST','25':'WAKE_BTN','26':'ADMIN_BTN','27':'GND'},
'U2':{'1':'CHARGE_STAT','2':'GND','3':'BAT_PROTECTED','4':'USB_5V_SAFE','5':'CHARGE_PROG'},
'U3':{'1':'BAT_RUN','2':'BAT_RUN','3':'GND','4':'GND','5':'COIL_6V','6':'COIL_6V'},
'U4':{'1':'BAT_RUN','2':'GND','3':'NANO_7V5'},
'U5':{'1':'USB_VBUS','2':'GND','3':'GND','5':'USB_5V_SAFE'},
'J3':{'A5':'USB_CC1','B5':'USB_CC2','A9':'USB_VBUS','B9':'USB_VBUS','A12':'GND','B12':'GND','S1':'GND'},
'Q1':{'1':'SOL_GATE','2':'GND','3':'COIL_N'},
'D1':{'1':'COIL_6V','2':'COIL_N'},
'J5':{'1':'RFID_SS','2':'SPI_SCK','3':'SPI_MOSI','4':'SPI_MISO','6':'GND','7':'RFID_RST','8':'3V3'},
'J6':{'1':'GND','2':'GND','3':'WAKE_BTN','4':'ADMIN_BTN','5':'LED_RED_A','6':'LED_GREEN_A','7':'3V3','8':'BUZZ_N'}}
ci=[{'pin':[ref,pn],'expected':n,'actual':bp.get((ref,pn))} for ref,ps in contracts.items() for pn,n in ps.items() if bp.get((ref,pn))!=n]
# Check manufacturer top-view module coordinates independently of the source footprints.
fps={f.GetReference():f for f in b.GetFootprints()}
module_coordinates={
 'U3':[(str(i+1),65-6.33+i*2.54,37+6.33) for i in range(6)],
 'U4':[('1',20-2.53,21+5.28),('2',20+.01,21+5.28),('3',20+2.55,21+5.28)]}
coordinate_errors=[]
for ref,entries in module_coordinates.items():
    pp={pad.GetNumber():pad for pad in fps[ref].Pads()}
    for pin,x,y in entries:
        pad=pp[pin];pos=pad.GetPosition()
        got=[p.ToMM(pos.x),p.ToMM(pos.y)]
        if abs(got[0]-x)>.015 or abs(got[1]-y)>.015:
            coordinate_errors.append({'part':ref,'pin':pin,'expected_xy':[x,y],'actual_xy':got})
        drill=pad.GetDrillSize()
        if abs(p.ToMM(drill.x)-1.2)>.005 or abs(p.ToMM(drill.y)-1.2)>.005:
            coordinate_errors.append({'part':ref,'pin':pin,'expected_drill_mm':1.2,'actual_drill_mm':[p.ToMM(drill.x),p.ToMM(drill.y)]})
report=(ROOT/'drc.txt').read_text()
counts={}
for title in ['DRC violations','unconnected pads','Footprint errors']:
    m=re.search(r'Found (\d+) '+title,report)
    if not m:raise RuntimeError('Could not parse DRC count: '+title)
    counts[title]=int(m.group(1))
ok=not(sm or pm or extra or nc_bad or ci or coordinate_errors or any(counts.values()))
result={'status':'REVIEW_NOT_FOR_FABRICATION','native_geometry_and_net_checks':'PASS' if ok else 'FAIL','connected_pins':len(expected),'schematic_mismatch':sm,'pcb_mismatch':pm,'extra_pcb_pins':extra,'unexpected_NC_connections':nc_bad,'interface_contract_mismatch':ci,'module_coordinate_errors':coordinate_errors,**counts,'full_ERC':'NOT RUN by this script. Run native KiCad GUI ERC or supported newer CLI and retain its report.','remaining':['Exact USB suffix/stakes and Nano sockets','Cell protection, actual coil current/duty, fuse and passive MPNs','Voltage transient, thermal, charger and release-time bench tests','Complete enclosure installation and cable-mating validation','Manufacturer DFM review']}
(ROOT/'validation_after_routing.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
raise SystemExit(0 if ok else 1)
