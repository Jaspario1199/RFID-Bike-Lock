"""Envelope-only enclosure review and nonfunctional PCB fit references.
This deliberately does not produce replacement production enclosure parts.
"""
from pathlib import Path
import sys,json,math
sys.path.append('/usr/lib/python3/dist-packages')
import pcbnew as p
import cadquery as cq
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Circle
R=Path(__file__).resolve().parent;O=R/'mechanical';O.mkdir(exist_ok=True)
b=p.LoadBoard(str(R/'design/VELOX_carrier_B.kicad_pcb'))
parts=json.loads((R/'design/components.json').read_text())
heights={'U1':14,'U2':1.5,'U3':8.1,'U4':5.4,'U5':1.5,'J1':3,'J2':3,'J3':3.2,'J4':18,'J5':18,'J6':18,'C1':13,'C8':12.5}
def cub(v):
    x0,x1,y0,y1,z0,z1=v
    return cq.Workplane('XY').box(x1-x0,y1-y0,z1-z0,centered=(False,False,False)).translate((x0,y0,z0)).val()
def mv(v,dx,dy,dz):return [v[0]+dx,v[1]+dx,v[2]+dy,v[3]+dy,v[4]+dz,v[5]+dz]
def intersection(a,b):
    return math.prod(max(0,min(a[j+1],b[j+1])-max(a[j],b[j])) for j in (0,2,4))
coupon=cq.Workplane('XY').box(90,55,1.6,centered=(False,False,False))
for x,y in [(4,4),(86,4),(4,51),(86,51)]:
    coupon=coupon.cut(cq.Workplane('XY',origin=(x,y,-.1)).circle(1.6).extrude(1.8))
cq.exporters.export(coupon,str(O/'PCB_outline_fit_coupon.step'))
cq.exporters.export(coupon,str(O/'PCB_outline_fit_coupon.stl'))
models={'PCB':[0,90,0,55,0,1.6]};shapes={'PCB':coupon.val()}
for f in b.GetFootprints():
    ref=f.GetReference()
    if ref.startswith(('H','TP')):continue
    bb=f.GetBoundingBox(False,False)
    h=heights.get(ref,2.0 if ref.startswith('D') else 1.5)
    v=[p.ToMM(bb.GetX()),p.ToMM(bb.GetRight()),p.ToMM(bb.GetY()),p.ToMM(bb.GetBottom()),1.6,1.6+h]
    models[ref]=v;shapes[ref]=cub(v)
a=cq.Assembly(name='VELOX_carrier_B_CONSERVATIVE_ENVELOPES')
for ref,s in shapes.items():a.add(s,name=ref,color=cq.Color(.12,.4,.3) if ref=='PCB' else cq.Color(.35,.6,.8))
a.save(str(O/'carrier_envelope.step'))

# Proposal coordinates are in the rev3g assembly coordinate system, mm.
dx,dy,dz=11.,35.5,42.
installed={ref:mv(v,dx,dy,dz) for ref,v in models.items()}
fixed={'battery':[110,160,0,34,40,50.5],
       'solenoid_frame':[24.5,54.5,-11,3,43.5,60.5],
       'latch_guide':[63,101,-14,11,52,70]}
old={'reader':[15,75,46,85,57,61.5],
     'reader_tray_deck':[13,77,44,87,55,57],
     'reader_tray_post_left':[8.5,13.5,63,68,38,57],
     'reader_tray_post_right':[76.5,81.5,63,68,38,57],
     'wake_button':[84,96,44,56,55,70],
     'cancel_button':[84,96,72,84,55,70],
     'buzzer':[109,121,59,71,61,70]}
lid_proposal={'reader':[119,158,30,90,61,65.5],
     'wake_button':[104,116,38,50,55,70],
     'cancel_button':[104,116,64,76,55,70],
     'buzzer':[130,142,12,24,61,70],
     'red_LED':[81.5,86.5,33.5,38.5,64,70],
     'green_LED':[93.5,98.5,33.5,38.5,64,70]}
def collisions(left,right):
    return [{'a':n,'b':m,'aabb_overlap_mm3':round(intersection(v,w),4)}
            for n,v in left.items() for m,w in right.items() if intersection(v,w)>.001]
old_conflicts=collisions(installed,old)
proposed_conflicts=collisions(installed,{**fixed,**lid_proposal})
# M3 fixing coordinates; check a6 mm screwdriver envelope with lid removed.
mounts=[(dx+x,dy+y) for x,y in [(4,4),(86,4),(4,51),(86,51)]]
tools={f'M3_tool_{i+1}':[x-3,x+3,y-3,y+3,dz+1.6,95] for i,(x,y) in enumerate(mounts)}
tool_conflicts=collisions(tools,{n:v for n,v in installed.items() if n!='PCB'})
service={'Nano_USB_plug':[54,65,19.5,40.5,52.5,59],
         'Charge_USB_plug':[18.5,29.5,90.8,112,42.8,49.3]}
service_conflicts=collisions(service,{**fixed,**lid_proposal})
walls={'left_wall':[0,3,-17,94,38,70],'right_wall':[167,170,-17,94,38,70],
       'front_wall':[0,170,-17,-14,38,70],'rear_wall':[0,170,91,94,38,70]}
bosses={f'lid_boss_{i+1}':[x-4,x+4,y-4,y+4,38,70] for i,(x,y) in enumerate([(6,12),(164,-8),(6,88),(164,60)])}
wall_conflicts=collisions(installed,{**walls,**bosses})
# A closed USB aperture permits final placement but blocks vertical insertion.
# Split the rear wall around the cut instead of exempting connector collisions.
original_port=[18,30,90.5,94.1,42.5,49.5]
port=[18,30,90.5,94.1,42.5,70.1]  # top-open notch; revised lid must cap it
def walls_with_port(opening):
    x0,x1,_,_,z0,z1=opening
    result={n:v for n,v in walls.items() if n!='rear_wall'}
    result.update(rear_left=[0,x0,91,94,38,70],rear_right=[x1,170,91,94,38,70],
                  rear_below=[x0,x1,91,94,38,z0])
    if z1<70:result['rear_above']=[x0,x1,91,94,z1,70]
    return result
proposed_walls=walls_with_port(port)
obstacles={**fixed,**proposed_walls,**bosses}
wall_conflicts=collisions(installed,{**proposed_walls,**bosses})
# The union of every Z position in a straight 40 mm translation is this AABB.
# This is continuous for the envelope model, with no gaps between samples.
swept={n:v[:5]+[v[5]+40] for n,v in installed.items()}
original_insertion=collisions(swept,{**fixed,**walls_with_port(original_port),**bosses})
insertion=collisions(swept,obstacles)
tool_conflicts+=collisions(tools,obstacles)
service_conflicts+=collisions(service,{**proposed_walls,**bosses})
lid_sweep={n:v[:5]+[v[5]+40] for n,v in lid_proposal.items()}
lid_conflicts=collisions(lid_sweep,{**installed,**fixed,**proposed_walls,**bosses})
for plug,own in [('Nano_USB_plug','U1'),('Charge_USB_plug','J3')]:
    service_conflicts+=collisions({plug:service[plug]},{n:v for n,v in installed.items() if n not in ['PCB',own]})
report={'status':'PLACEMENT_PROPOSAL_ONLY_NOT_ENCLOSURE_RELEASE',
 'carrier_origin_xyz_mm':[dx,dy,dz],'board_mm':[90,55,1.6],
 'old_rev3g_conflicts':old_conflicts,'proposed_component_conflicts':proposed_conflicts,
 'proposed_fixed_wall_boss_conflicts':wall_conflicts,'pcb_top_down_insertion_conflicts':insertion,
 'lid_removed_M3_tool_conflicts':tool_conflicts,'proposed_USB_service_conflicts':service_conflicts,
 'M3_mount_xy_mm':mounts,
 'closed_aperture_insertion_conflicts':original_insertion,
 'continuous_translation_test_mm':40,
 'new_rear_charge_opening_proposal_mm':port,
 'lid_component_continuous_lowering_conflicts':lid_conflicts,
 'reader_antenna_reservation_assumed_mm':[119,158,50,90,61,70],
 'component_height_reservations_above_PCB_mm':heights,
 'limits':['AABB envelopes include footprint courtyards, not detailed component solids.',
 'Reader antenna end and module sizes come from repository assumptions; inspect the actual RC522.',
 'Nano sockets and mated connector/cable heights are reserved, not measured.',
 'All panel parts and RFID holder require a new lid arrangement; old reader posts/tray must be removed.',
 'Charging port must be a top-open notch for PCB insertion; revised lid cap/sealing and new carrier supports are not production designs.',
 'Cable bends, unplugging under the revised lid, reader attachment tools, real module supports and complete lock hinge motion are not verified.',
 'This does not qualify the existing solenoid mechanism, battery swelling or thermal/RF performance.'],
 'geometry_only_pass':not(proposed_conflicts+wall_conflicts+insertion+tool_conflicts+service_conflicts+lid_conflicts)}
(O/'placement_report.json').write_text(json.dumps(report,indent=2))
(O/'component_envelopes.json').write_text(json.dumps({'local':models,'proposal_global':installed,'fixed':fixed,'proposed_lid_parts':lid_proposal},indent=2))

# Context STEP: simplified housing, not the production enclosure/attachment geometry.
floor=cub([0,170,-17,94,35,38]);shell=cq.Workplane(obj=floor)
for v in walls.values():shell=shell.union(cub(v))
shell=shell.cut(cub(report['new_rear_charge_opening_proposal_mm']))
scene=cq.Assembly(name='VELOX_revB_PLACEMENT_ONLY')
scene.add(shell.val(),name='SIMPLIFIED_HOUSING_CONTEXT_NOT_FOR_PRINT',color=cq.Color(.7,.7,.7,.25))
for ref,s in shapes.items():scene.add(s.translate((dx,dy,dz)),name='carrier_'+ref,color=cq.Color(.1,.4,.3) if ref=='PCB' else cq.Color(.35,.6,.8))
for ref,v in {**fixed,**lid_proposal}.items():scene.add(cub(v),name=ref,color=cq.Color(.8,.6,.2))
scene.save(str(O/'placement_proposal_ENVELOPES_ONLY.step'))

fig,ax=plt.subplots(figsize=(12,8),dpi=180);fig.patch.set_facecolor('#f5f7fa');ax.set_facecolor('#f5f7fa');ax.set_aspect('equal');ax.set_xlim(-10,180);ax.set_ylim(104,-28);ax.axis('off')
ax.add_patch(Rectangle((0,-17),170,111,facecolor='#e1e7eb',edgecolor='#516879',lw=2))
ax.add_patch(Rectangle((3,-14),164,105,facecolor='#f5f7fa',edgecolor='#849aa8'))
def draw(v,label,color):
    x0,x1,y0,y1,_,_=v;ax.add_patch(Rectangle((x0,y0),x1-x0,y1-y0,facecolor=color,edgecolor='white',alpha=.9,lw=1));ax.text((x0+x1)/2,(y0+y1)/2,label,ha='center',va='center',fontsize=8)
draw(installed['PCB'],'90 × 55 mm carrier\nTop-down mounting','#92c5b4')
for ref in ['U1','U3','U4','J5','J6','C1']:draw(installed[ref],ref,'#c4deee')
draw(fixed['battery'],'Battery\nretained','#e9c989');draw(fixed['solenoid_frame'],'Solenoid\nretained','#e9c989');draw(fixed['latch_guide'],'Guide','#d7c1a6')
draw(lid_proposal['reader'],'Reader relocated\nLid holder still required','#c2c1eb')
for ref in ['wake_button','cancel_button','buzzer']:
    v=lid_proposal[ref];x=(v[0]+v[1])/2;y=(v[2]+v[3])/2;ax.add_patch(Circle((x,y),6,facecolor='#ebaa98',edgecolor='white'));ax.text(x,y,ref.replace('_button','').replace('buzzer','buzz'),fontsize=7,ha='center',va='center')
for x,y in mounts:ax.add_patch(Circle((x,y),1.6,facecolor='#f5f7fa',edgecolor='#42686c'))
ax.plot([24,24],[90,102],color='#7a4153',lw=2);ax.text(32,99,'New rear charge opening',fontsize=9,color='#7a4153')
ax.text(0,-24,'VELOX Rev B · proposed enclosure placement',fontsize=16,weight='bold',color='#203642')
ax.text(0,-19,'Reader, panel and charging port need new mounts/openings. Reference envelopes only.',fontsize=9,color='#516879')
fig.savefig(R/'previews/enclosure_proposal.png',bbox_inches='tight');plt.close(fig)
print(json.dumps({'old_conflicts':len(old_conflicts),'geometry_only_pass':report['geometry_only_pass'],'proposed_conflicts':proposed_conflicts,'wall_conflicts':wall_conflicts,'tool_conflicts':tool_conflicts},indent=2))
