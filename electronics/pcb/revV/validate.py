"""Native checks plus independent functional connectivity through installed wires."""
from pathlib import Path
import pcbnew as p
import subprocess,json,hashlib,xml.etree.ElementTree as ET,math,sys
R=Path(__file__).resolve().parent;D=R/'design';fn=D/'VELOX_carrier_V.kicad_pcb'
for args in [ ['sch','erc','--format','json','--severity-all','-o',str(R/'erc.json'),str(D/'VELOX_carrier_V.kicad_sch')],
['pcb','drc','--format','json','--severity-all','--all-track-errors','--schematic-parity','-o',str(R/'drc.json'),str(fn)]]:
 subprocess.run(['kicad-cli']+args,check=True)
b=p.LoadBoard(str(fn));parts=json.loads((D/'components.json').read_text());logical=json.loads((D/'logical_components.json').read_text());jumpers=json.loads((R/'jumpers.json').read_text())
actual={(f.GetReference(),d.GetNumber()):d.GetNetname().lstrip('/') for f in b.GetFootprints() for d in f.Pads()};errors=[]
xml=ET.parse(D/'VELOX_carrier_V.xml').getroot();sch={(a.attrib['ref'],a.attrib['pin']):n.attrib['name'].lstrip('/') for n in xml.find('nets') for a in n.findall('node')}
for c in parts:
 for pin,n in c['pins'].items():
  expected=n or f'unconnected-({c["ref"]}-{c["names"].get(pin,pin)}-Pad{pin})'
  if actual.get((c['ref'],pin))!=expected or sch.get((c['ref'],pin))!=expected:errors.append(['pin/parity',c['ref'],pin,expected,actual.get((c['ref'],pin)),sch.get((c['ref'],pin))])
parent={}
def find(n):
 parent.setdefault(n,n)
 if parent[n]!=n:parent[n]=find(parent[n])
 return parent[n]
def union(a,c):parent[find(a)]=find(c)
for j in jumpers:union(*j['net_segments'])
net_groups={}
for c in logical:
 for pin,n in c['pins'].items():
  if n:
   net_groups.setdefault(n,set()).add(find(actual[(c['ref'],pin)]))
for n,groups in net_groups.items():
 if len(groups)!=1:errors.append(['functional disconnect',n,list(groups)])
if len({next(iter(s)) for s in net_groups.values()})!=len(net_groups):errors.append(['functional short between originally distinct nets'])
# Retain the independently recorded Nano pin/interface map from Rev B.
oldnano=json.loads((D/'reference_nano_pinmap.json').read_text());nano=next(c for c in logical if c['ref']=='U1')
if oldnano['pins']!=nano['pins'] or oldnano['names']!=nano['names']:errors.append(['Nano interface changed'])
# Fabrication invariants: small copper rivets connect the two printed sides.
tracks=list(b.GetTracks());via_count=sum(isinstance(t,p.PCB_VIA) for t in tracks)
# Rivet count is reported for assembly planning, not an invented process limit.
if any(t.GetLayer() not in [p.F_Cu,p.B_Cu] for t in tracks):errors.append(['invalid track layer'])
if any(t.GetWidth()<p.FromMM(.3) for t in tracks):errors.append(['track width'])
if any(not z.GetIsRuleArea() for z in b.Zones()):errors.append(['printed filled zone'])
for f in b.GetFootprints():
 for pad in f.Pads():
  if pad.GetDrillSize().x and abs(p.ToMM(pad.GetDrillSize().x)-1.6)>.0001:errors.append(['unsupported drill',f.GetReference(),pad.GetNumber()])
  if pad.GetAttribute()==p.PAD_ATTRIB_PTH:
   if min(p.ToMM(pad.GetSize().x),p.ToMM(pad.GetSize().y))<2.24-.0001:errors.append(['rivet land too small'])
  if pad.GetAttribute()==p.PAD_ATTRIB_SMD and pad.GetLayerSet().Contains(p.F_Cu):errors.append(['SMD mounted on wrong side',f.GetReference()])
for t in tracks:
 if isinstance(t,p.PCB_VIA) and (abs(p.ToMM(t.GetDrill())-.7)>.001 or p.ToMM(t.GetWidth())<1.3-.001):errors.append(['small rivet geometry'])
# Wire land overlays must exactly coincide with documented existing solder pads.
fs={f.GetReference():f for f in b.GetFootprints()}
for j in jumpers:
 for pn,end in [('1','from'),('2','to')]:
  ref,num=j[end].split('.');target=next(d for d in fs[ref].Pads() if d.GetNumber()==num);wire=next(d for d in fs[j['ref']].Pads() if d.GetNumber()==pn)
  if target.GetPosition()!=wire.GetPosition() or target.GetNetCode()!=wire.GetNetCode():errors.append(['wire endpoint mismatch',j['ref'],pn])
  if target.GetSize().x<p.FromMM(.8) or target.GetSize().y<p.FromMM(.8):errors.append(['wire pad coverage'])
drc=json.loads((R/'drc.json').read_text());erc=json.loads((R/'erc.json').read_text());erc_issues=[v for s in erc['sheets'] for v in s['violations']]
counts={'ERC_violations':len(erc_issues),'DRC_violations':len(drc['violations']),'unconnected_items':len(drc['unconnected_items']),'schematic_parity_issues':len(drc['schematic_parity'])}
report={'status':'REVIEW_PROTOTYPE_NOT_FEDC_ACCEPTED','digital_checks':'PASS' if not errors and not any(counts.values()) else 'FAIL',**counts,'independent_errors':errors,'logical_connected_pins':sum(bool(n) for c in logical for n in c['pins'].values()),'functional_nets':len(net_groups),'installed_wire_count':len(jumpers),'via_count':via_count,'copper_sides':['F.Cu','B.Cu'],'board_mm':[90,55,1.6],'min_track_mm':min(p.ToMM(t.GetWidth()) for t in tracks),'native_checker':drc['kicad_version'],'drc_exclusions':[],
'ignored_rule_note':'Solder-mask bridges ignored because the prototype has no solder mask. Other original project severity categories are retained; inspect .kicad_pro.',
'source_sha256':{str(f.relative_to(R)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(D.rglob('*')) if f.is_file() and f.suffix in ['.kicad_pcb','.kicad_sch','.kicad_pro','.kicad_mod','.kicad_sym','.kicad_dru','.json']},
'physical_qualification':'Not performed. Rivet/header fit, ink coupon resistance/adhesion, solder process, external power and enclosure/harness installation require qualification.'}
(R/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='source_sha256'},indent=2));sys.exit(0 if report['digital_checks']=='PASS' else 1)
