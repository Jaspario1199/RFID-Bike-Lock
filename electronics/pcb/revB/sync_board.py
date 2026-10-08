"""Synchronize exported KiCad net identities after routing; keep copper intact.

Run after build.py + route.py and before validate.py. NC nets remain isolated.
The validator independently checks the resulting identities and all routing.
"""
from pathlib import Path
import subprocess, xml.etree.ElementTree as ET, sys
sys.path.append('/usr/lib/python3/dist-packages')
import pcbnew as p

D=Path(__file__).resolve().parent/'design'
subprocess.run(['kicad-cli','sch','export','netlist','--format','kicadxml',
    '-o',str(D/'VELOX_carrier_B.xml'),str(D/'VELOX_carrier_B.kicad_sch')],check=True)
fn=D/'VELOX_carrier_B.kicad_pcb'; b=p.LoadBoard(str(fn))
for code,n in b.GetNetsByNetcode().items():
    name=n.GetNetname()
    if code and not name.startswith(('/', 'unconnected-')):n.SetNetname('/'+name)
nets={n.GetNetname():n for n in b.GetNetsByNetcode().values()}
footprints={f.GetReference():f for f in b.GetFootprints()}
for net in ET.parse(D/'VELOX_carrier_B.xml').getroot().find('nets'):
    name=net.attrib['name']
    if not name.startswith('unconnected-'):continue
    if name not in nets:
        nets[name]=p.NETINFO_ITEM(b,name);b.Add(nets[name])
    for node in net.findall('node'):
        pad=next(a for a in footprints[node.attrib['ref']].Pads() if a.GetNumber()==node.attrib['pin'])
        pad.SetNet(nets[name])
p.SaveBoard(str(fn),b)
print('Synchronized KiCad net identities; copper preserved.')
