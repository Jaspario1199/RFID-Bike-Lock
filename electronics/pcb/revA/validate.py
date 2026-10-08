from pathlib import Path
import sys,json,xml.etree.ElementTree as ET,re
sys.path.append('/usr/lib/python3/dist-packages')
import pcbnew as p
R=Path(__file__).resolve().parent;D=R/'design'; fn=D/'VELOX_carrier_A.kicad_pcb'
b=p.LoadBoard(str(fn)); ds=b.GetDesignSettings()
ds.m_MinClearance=p.FromMM(.2);ds.m_CopperEdgeClearance=p.FromMM(.5)
ds.m_TrackMinWidth=p.FromMM(.25);ds.m_ViasMinSize=p.FromMM(.6);ds.m_MinThroughDrill=p.FromMM(.3)
ds.m_HoleClearance=p.FromMM(.25);ds.m_HoleToHoleMin=p.FromMM(.25)
# Match KiCad's root-sheet local-label net names.
for code,n in b.GetNetsByNetcode().items():
    if code and not n.GetNetname().startswith('/'):n.SetNetname('/'+n.GetNetname())
p.SaveBoard(str(fn),b)
p.WriteDRCReport(b,str(R/'drc.txt'),p.EDA_UNITS_MILLIMETRES,True)
parts=json.loads((D/'components.json').read_text());expected={}
for c in parts:
    for pin,n in c['pins'].items():
        if n:expected[(c['ref'],pin)]=n
root=ET.parse(D/'VELOX_carrier_A.xml').getroot(); actual={}
for n in root.find('nets'):
    for pin in n.findall('node'):actual[(pin.attrib['ref'],pin.attrib['pin'])]=n.attrib['name'].lstrip('/')
sch_mismatch=[(k,n,actual.get(k)) for k,n in expected.items() if actual.get(k)!=n]
bp={(f.GetReference(),d.GetNumber()):d.GetNetname().lstrip('/') for f in b.GetFootprints() for d in f.Pads() if d.GetNetname()}
pcb_mismatch=[(k,n,bp.get(k)) for k,n in expected.items() if bp.get(k)!=n]
extra=[(k,v) for k,v in bp.items() if k not in expected]
report=(R/'drc.txt').read_text()
counts={n:int(re.search(r'Found (\d+) '+n,report).group(1)) for n in ['DRC violations','unconnected pads','Footprint errors']}
result=dict(status='ENGINEERING_REVIEW_NOT_FOR_FABRICATION',pins_checked=len(expected),schematic_mismatch=sch_mismatch,pcb_mismatch=pcb_mismatch,extra_pcb_nets=extra,**counts,
    clearance_mm=.2,minimum_track_mm=.25,board_mm=[110,65,1.6],
    erc='Full KiCad electrical-rule check not executed: available KiCad 7 CLI lacks ERC. Netlist/pin checks are not ERC.',
    outstanding=['Verify exact solenoid winding/current/duty and boost pulse performance','Verify protected cell discharge rating and charger charge current','Select exact fuse, capacitor and buzzer; verify module mechanical interfaces','Enclosure board mounting, antenna placement and complete installation check','Physical prototype and thermal/transient/charging tests'])
(R/'validation.json').write_text(json.dumps(result,indent=2)); print(json.dumps(result,indent=2))
project={'meta':{'filename':'VELOX_carrier_A.kicad_pro','version':1},'board':{'design_settings':{'rules':{'min_clearance':.2,'min_track_width':.25,'min_via_diameter':.6,'min_through_hole_diameter':.3,'min_copper_edge_clearance':.5,'min_hole_clearance':.25,'min_hole_to_hole':.25}}},
 'net_settings':{'classes':[{'name':'Default','clearance':.2,'track_width':.25,'via_diameter':.9,'via_drill':.45,'microvia_diameter':.3,'microvia_drill':.1,'diff_pair_width':.25,'diff_pair_gap':.25,'diff_pair_via_gap':.25}],'meta':{'version':3}}}
(D/'VELOX_carrier_A.kicad_pro').write_text(json.dumps(project,indent=2))
