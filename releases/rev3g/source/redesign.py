"""Rev3g assembly-access prototype. Dimensions mm; unmodified solenoid.
Source drawings and owner measurements are distinguished in README.
Run from any directory; outputs beside this script. Requires CadQuery.
"""
from pathlib import Path
import importlib.util,json,math
import cadquery as cq
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('base',OUT/'base_rev3f.py');b=importlib.util.module_from_spec(sp);sp.loader.exec_module(b)
box=b.xbox
ZF=38.; TOP=70.; AXIS_Y=-4.; AXIS_Z=52.
BODY_REAR=24.5; BODY_FRONT=54.5; STROKE=10.
def xc(a,c,r):return cq.Workplane('YZ',origin=(a,AXIS_Y,AXIS_Z)).circle(r).extrude(c-a)
def hole(x,y,z,d,h):return cq.Workplane('XY',origin=(x,y,z)).circle(d/2).extrude(h)
def solid(w):return w.val()
# All removable bays are independently lowered from above. Board envelopes retained
# from rev3f; final connector variants still require hardware verification.
bays={
 'battery':(110,160,0,34,40,50.5,[(106,17),(164,17)]),
 'reader':(15,75,46,85,57,61.5,[(11,65.5),(79,65.5)]),
 'nano':(110,155,43,61,40,47.5,[(115,39),(150,39)]),
 'driver':(15,55,15,25.7,40,53.6,[(20,11),(50,11)]),
 'boost':(65,101,20,37,40,47,[(70,17),(96,17)]),
 'charger':(134,163,70,87,40,44.3,[(130,73),(130,84)])}
mounts=[(19,5),(60,5)]
lid_screws=[(6,12),(164,-8),(6,88),(164,60)]
parts={}; refs={}; screws=[]
# Preserve the original attachment/saddle geometry below the new floor.
lower=b.build_top_box().intersect(box(-5,175,-20,100,-100,35.1))
housing=lower.union(box(0,170,-17,94,34.9,38)).union(box(0,170,.3,94,32,35.1))
wall=box(0,170,-17,94,38,TOP).cut(box(3,167,-14,91,37.9,TOP+1))
# Fully open solenoid relief for top-down insertion: 1.5 mm outer wall remains.
wall=wall.cut(box(15,64,-12.5,-10.9,37.9,TOP+1))
housing=housing.union(wall)
housing=housing.cut(box(79.8,100.2,-19,-.7,0,36.5))
# Latch receiver stays coaxial with existing closure screw and cable head.
receiver=hole(90,-4,38,19,TOP-38).cut(hole(90,-4,37.9,11,TOP-37))
receiver=receiver.cut(xc(63,90,6.25))
receiver=receiver.cut(hole(90,-4,58.8,14.3,TOP-58.7))
housing=housing.union(receiver.intersect(box(0,170,-17,94,37,52))).cut(hole(90,-4,0,3.4,38.1))
# Split guide: lower half integral, upper half removable; shaft seat enters vertically.
guide=box(63,84.5,-12.5,10,38,61).cut(xc(62,85,6.25))
baseguide=guide.intersect(box(62,86,-14,11,37,52))
capguide=guide.union(receiver).intersect(box(62,101,-14,11,52,TOP+1))
capguide=capguide.cut(hole(90,-4,58.8,14.3,TOP-58.7))
for x,y in [(66,7),(80,7)]:
 baseguide=baseguide.cut(hole(x,y,46.6,1.6,5.5))
 capguide=capguide.cut(hole(x,y,51.9,2.4,10))
 screws.append(('guide',x,y,61,14))
housing=housing.union(baseguide)
parts['latch_guide_cover']=capguide
# Solenoid rotates 180 degrees in plan and 90 around shaft: frame 14 wide,17 tall.
carrier=box(16,63,-11.8,8,38,40)
for x in [27,48]:carrier=carrier.union(box(x,x+4,-11,3,40,43.5))
for x,y in mounts:
 carrier=carrier.cut(hole(x,y,37.9,2.4,6)); screws.append(('solenoid',x,y,40,5))
# Strap slots accessible before placement, crosswise ties around metal body only.
for x in [32,46]:
 for y in [-10.9,3.8]:carrier=carrier.cut(box(x-1.5,x+1.5,y,y+1.5,37.9,40.1))
parts['solenoid_carrier']=carrier
for name,(x0,x1,y0,y1,z0,z1,axes) in bays.items():
 deck=box(x0-2,x1+2,y0-2,y1+2,z0-2,z0)
 for x,y in axes:
  # Ear joins to plate; elevated reader ears stand on columns, allowing direct driver access.
  deck=deck.union(box(min(x,x0-1),max(x,x1+1),y-2.5,y+2.5,z0-2,z0))
  if z0>40:deck=deck.union(hole(x,y,38,5,z0-38))
  deck=deck.cut(hole(x,y,37.9,2.4,z0-37.8))
  screws.append((name,x,y,z0, int(z0-38+3)))
 # Two retained tie loops: slots outside component edges, underside channels.
 for x in [x0+(x1-x0)*.3,x0+(x1-x0)*.7]:
  for y in [y0-1.6,y1+.3]:deck=deck.cut(box(x-1.5,x+1.5,y,y+1.3,z0-2.1,z0+.1))
  deck=deck.cut(box(x-1.5,x+1.5,y0-2.1,y1+2.1,z0-2.1,z0-1.1))
 parts[name+'_tray']=deck
 refs[name]=box(x0,x1,y0,y1,z0,z1)
for _,x,y,seat,length in screws:
 if seat!=61:housing=housing.cut(hole(x,y,34.6,1.6,3.5))
for x,y in lid_screws:
 housing=housing.union(hole(x,y,38,8,TOP-38)).cut(hole(x,y,62,2.5,9))
# Dedicated charger end port; shaft wiring exits into open central bay.
housing=housing.cut(box(162.9,170.1,73.5,83.5,39.7,44.7))
housing=housing.cut(box(165,170.1,70.8,86.2,37.0,47.4))
for x in b.SCREW_X:
 housing=housing.cut(hole(x,b.CROWN_Y,25,b.TAP3,12))
housing=housing.clean()
parts['A1_top_box']=housing
lid=box(0,170,-17,94,70,75)
for x,y in lid_screws:
 lid=lid.cut(hole(x,y,69.9,3.4,5.2))
 lid=lid.cut(cq.Workplane('XY',origin=(x,y,73.5)).circle(1.7).workplane(offset=1.5).circle(3.2).loft())
lid=lid.cut(hole(90,-4,69.9,14.5,5.2))
# Existing button dimensions, shifted into clear service strip between bays.
for y in [50,78]:lid=lid.cut(hole(90,y,69.9,12.4,5.2));refs['button_'+str(y)]=hole(90,y,55,12,15)
for x in [84,96]:lid=lid.cut(hole(x,36,69.9,3.3,5.2))
lid=lid.cut(hole(115,65,69.9,2.5,5.2));refs['buzzer']=hole(115,65,61,12,9)
# Thin RF region integral to PETG lid (no separate insert); reader below.
lid=lid.cut(box(30,72,48,83,69.9,73.5))
parts['A2_lid']=lid
parts['prototype_bushing']=hole(90,-4,58.8,14,16.2).cut(hole(90,-4,58.7,10.3,16.4))
# Enlarged sleeve guided in the same 12.5 passage as the 11.1125 spring seat.
# Cross-pin location estimate from drawing, to be confirmed with small coupon.
adapter=xc(76.5,83.5,5.9).union(xc(83.5,86.5,4)).cut(xc(76.4,84.5,3.45))
adapter=adapter.cut(cq.Workplane('XZ',origin=(81,5,52)).circle(1.6).extrude(18))
parts['prototype_latch_adapter']=adapter
refs['solenoid_frame']=box(24.5,54.5,-11,3,43.5,60.5)
def moving(t):
 front=xc(54.4,84.5-t,3.25)
 rear=xc(24.5-9.525-t,24.6,3.25)
 # Conservative solid envelope includes spring and washer. Spring OD provisional11.5.
 spring=xc(54.5,75.5-t,5.75)
 washer=xc(74.5-t,75.5-t,11.1125/2)
 return front.union(rear).union(spring).union(washer)
refs['solenoid_moving_rest']=moving(0)
# Access checker uses exact solids sampled at 1mm. Fixtures carried with purchased parts.
def overlap(a,c):
 aa=a.val() if hasattr(a,'val') else a; cc=c.val() if hasattr(c,'val') else c
 ab=aa.BoundingBox();cb=cc.BoundingBox()
 if ab.xmax<=cb.xmin or cb.xmax<=ab.xmin or ab.ymax<=cb.ymin or cb.ymax<=ab.ymin or ab.zmax<=cb.zmin or cb.zmax<=ab.zmin:return 0.
 return aa.intersect(cc).Volume()
def audit():
 errors=[]; report={}
 for n,s in parts.items():
  if not s.val().isValid() or len(s.val().Solids())!=1:errors.append(('invalid',n,len(s.val().Solids())))
 # Actual occupied solids, including separated washer/shaft vs mating adapter intentionally overlap.
 static={**parts,**refs}
 allowed={frozenset(('prototype_latch_adapter','solenoid_moving_rest')),frozenset(('solenoid_frame','solenoid_moving_rest'))}
 for i,(n,s) in enumerate(static.items()):
  for k,t in list(static.items())[i+1:]:
   if frozenset((n,k)) in allowed:continue
   v=overlap(s,t)
   if v>.05:errors.append(('static',n,k,round(v,3)))
 # Solenoid and adapter move together across full factory stroke.
 for t in range(11):
  mov=moving(t).union(adapter.translate((-t,0,0)))
  for n,s in static.items():
   if n in ['prototype_latch_adapter','solenoid_moving_rest','solenoid_frame']:continue
   v=overlap(mov,s)
   if v>.05:errors.append(('stroke',t,n,round(v,3)))
 # Lid/control assemblies removed first. Guide cover and bushing installed last.
 installed={'housing':housing}; groups=[]
 for n in bays:groups.append((n,parts[n+'_tray'].union(refs[n])))
 groups += [('solenoid',carrier.union(refs['solenoid_frame']).union(moving(0)).union(adapter)),('guide',capguide),('bushing',parts['prototype_bushing'])]
 for n,s in groups:
  maximum=0.
  for dz in range(0,71):
   for k,o in installed.items():maximum=max(maximum,overlap(s.translate((0,0,dz)),o))
  report[n+'_vertical_install_max_mm3']=round(maximum,4)
  if maximum>.05:errors.append(('installation',n,maximum))
  installed[n]=s
 # Driver cylinder above each screw, lid absent; its own tray omitted for normal seating.
 for owner,x,y,z,l in screws:
  tool=hole(x,y,z+1.6,5,85-z)
  for n,s in installed.items():
   if n in [owner,'housing']:continue
   v=overlap(tool,s)
   if v>.05:errors.append(('tool',owner,n,round(v,3)))
 # Additional installation path: lid with button bodies/nuts and buzzer.
 lidgroup=lid
 for key in ['button_50','button_78','buzzer']:lidgroup=lidgroup.union(refs[key])
 for y in [50,78]:lidgroup=lidgroup.union(hole(90,y,67,15,3))
 lm=0.
 for dz in range(0,41):
  for o in installed.values():lm=max(lm,overlap(lidgroup.translate((0,0,dz)),o))
 report['lid_vertical_install_max_mm3']=round(lm,4)
 if lm>.05:errors.append(('lid_install',lm))
 # Tools against each owner's component, not just neighboring groups.
 for owner,x,y,z,l in screws:
  tool=hole(x,y,z+1.6,5,85-z)
  owned=refs.get(owner)
  if owner=='solenoid':owned=refs['solenoid_frame'].union(moving(0))
  if owned is not None and overlap(tool,owned)>.05:errors.append(('own_tool',owner))
 # Preserve installation swing of existing C2 and liner with the changed box.
 c2=b.build_c2().union(b.build_closure_block()).union(b.build_hinge_block()).union(b.build_liner(False))
 hm=0.
 for angle in [0,.5]+list(range(1,61)):
  sweep=c2.rotate((0,b.HINGE_Y,b.HINGE_Z),(1,b.HINGE_Y,b.HINGE_Z),angle)
  hm=max(hm,overlap(sweep,housing))
 report['hinge_0_to_60_max_mm3']=round(hm,4)
 if hm>.05:errors.append(('hinge',hm))
 # Reserved harness corridor and Nano USB service plug, lid open.
 corridor=box(103,106,0,87,43,46)
 plug=box(90,110,46,58,40,48)
 for name,volume in [('harness_corridor',corridor),('nano_USB_plug',plug)]:
  for n,s in installed.items():
   v=overlap(volume,s)
   if v>.05:errors.append((name,n,round(v,3)))
 cv=overlap(housing,b.build_c1())
 report['C1_housing_overlap_mm3']=round(cv,4)
 if cv>.05:errors.append(('C1_housing',cv))
 for x in b.SCREW_X:
  if overlap(housing,hole(x,b.CROWN_Y,25,b.TAP3-.01,11.9))>.05:errors.append(('frame_pilot',x))
 report['errors']=errors;report['status']='PASS' if not errors else 'FAIL'
 (OUT/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True)
 return not errors
if __name__=='__main__':
 import sys
 if '--audit' in sys.argv:sys.exit(0 if audit() else 1)
 (OUT/'STEP').mkdir(exist_ok=True);a=cq.Assembly(name='rev3g_access_prototype')
 for n,s in {**parts,**refs}.items():
  a.add(s,name=n);cq.exporters.export(s,str(OUT/'STEP'/(n+'.step')))
 a.save(str(OUT/'rev3g_assembly.step'))
 print('Exported',len(parts),'parts and',len(refs),'reference envelopes',flush=True)
