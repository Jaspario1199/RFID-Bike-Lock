// GEOMETRIC OUTLINE ONLY. Not an enclosure or populated-board fit approval.
// Export STL from OpenSCAD for a K1/K1 Max outline fit print.
$fn=64;
difference(){
  cube([90,55,1.6]);
  for(p=[[4,4],[86,4],[4,51],[86,51]])
    translate([p[0],p[1],-0.1]) cylinder(h=1.8,d=3.2);
}
