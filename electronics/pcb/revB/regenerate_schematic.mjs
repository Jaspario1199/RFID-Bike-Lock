import fs from "node:fs";
import path from "node:path";
import {fileURLToPath} from "node:url";
const root=path.dirname(fileURLToPath(import.meta.url));
function nativeSchematic(spec) {
 const qs=s=>JSON.stringify(String(s));
 function uid(s){let a=2166136261;const h=[];for(let j=0;j<4;j++){for(const c of "velox-revB-"+j+s){a^=c.charCodeAt(0);a=Math.imul(a,16777619);}h.push((a>>>0).toString(16).padStart(8,"0"));}const v=h.join("");return `${v.slice(0,8)}-${v.slice(8,12)}-5${v.slice(13,16)}-a${v.slice(17,20)}-${v.slice(20)}`;}
 const ef=(sz=1,extra="")=>`(effects (font (size ${sz} ${sz})) ${extra})`;
 const symbols=[],instances=[],wires=[],labels=[],nc=[];
 const places={U1:[85,92],U2:[220,143],U3:[405,108],U4:[405,160],U5:[220,205],J1:[405,45],F1:[480,48],J2:[480,76],J3:[220,48],J4:[540,240],J5:[85,259],J6:[535,321],Q1:[405,224],Q2:[405,312],R1:[350,214],R2:[350,240],R3:[350,302],R4:[350,331],R5:[480,347],R6:[480,370],R7:[85,323],R8:[85,347],R9:[195,95],R10:[195,117],R11:[285,168],R12:[285,194],C1:[480,199],C2:[480,260],C3:[480,149],C4:[85,166],C5:[85,190],C6:[195,347],C8:[480,110],C9:[195,250],C10:[195,276],C11:[195,313],D1:[480,230],D2:[480,310],D3:[285,223]};
 let t=0;
 for(const c of spec.parts) {
  if(c.kind==="hole")continue;
  if(c.kind==="test")places[c.ref]=[270+(t++)*45,378];
  const name="Part_"+c.ref, pins=Object.keys(c.pins),layout={},graphics=[],pinDefs=[];
  if(c.kind==="nano") {
   for(let i=0;i<15;i++){layout[String(i+1)]=[-30,35-i*5,0];layout[String(i+16)]=[30,35-i*5,180];}
   graphics.push("(rectangle (start -25 40)(end 25 -40)(stroke (width .254)(type default))(fill (type background)))");
  }else if(["R","C","CP","diode"].includes(c.kind)){
   layout["1"]=[-10,0,0];layout["2"]=[10,0,180];
   if(c.kind==="R") graphics.push("(rectangle (start -4 1.5)(end 4 -1.5)(stroke (width .254)(type default))(fill (type none)))");
   else if(c.kind==="C"||c.kind==="CP"){
    [-1,1].forEach(x=>graphics.push(`(polyline (pts (xy ${x} -3)(xy ${x} 3))(stroke (width .254)(type default))(fill (type none)))`));
    if(c.kind==="CP")graphics.push(`(text "+" (at -4 3 0) ${ef()})`);
   }else{
    graphics.push("(polyline (pts (xy 3 -3)(xy -3 0)(xy 3 3)(xy 3 -3))(stroke (width .254)(type default))(fill (type none)))");
    graphics.push("(polyline (pts (xy -4 -3)(xy -3 -3)(xy -3 3)(xy -2 3))(stroke (width .254)(type default))(fill (type none)))");
   }
  }else if(c.kind==="mos"){
   layout["1"]=[-15,0,0];layout["2"]=[15,-5,180];layout["3"]=[15,5,180];
   graphics.push("(rectangle (start -10 9)(end 10 -9)(stroke (width .254)(type default))(fill (type background)))",`(text "N-MOS" (at 0 0 0) ${ef()})`);
  }else if(c.kind==="test"){
   layout["1"]=[-5,0,0];graphics.push("(circle (center 0 0)(radius 1)(stroke (width .254)(type default))(fill (type none)))");
  }else{
   pins.forEach((pn,i)=>layout[pn]=[-20,(pins.length-1)*2.5-i*5,0]);
   const h=Math.max(5,pins.length*2.5+1);
   graphics.push(`(rectangle (start -15 ${h})(end 15 ${-h})(stroke (width .254)(type default))(fill (type background)))`);
  }
  for(const [pn,[x,y,a]] of Object.entries(layout)){
   const label=c.names[pn]||(["R","C","CP"].includes(c.kind)?"~":pn);
   const len=c.kind==="R"?6:["C","CP"].includes(c.kind)?9:c.kind==="diode"?7:c.kind==="test"?4:5;
   pinDefs.push(`(pin ${c.pin_types[pn]||"passive"} line (at ${x} ${y} ${a})(length ${len})(name ${qs(label)} ${ef(.9)})(number ${qs(pn)} ${ef(.9)}))`);
  }
  symbols.push(`(symbol "VELOX:${name}" (pin_names (offset .5))(in_bom yes)(on_board yes)(property "Reference" ${qs(c.ref)} (at 0 0 0) ${ef()})(property "Value" ${qs(c.value)} (at 0 0 0) ${ef()})(symbol "${name}_0_1" ${graphics.join("")})(symbol "${name}_1_1" ${pinDefs.join("")}))`);
  const [x,y]=places[c.ref],off=c.kind==="nano"?-44:c.kind==="mos"?-14:c.kind==="test"?-7:["R","C","CP","diode"].includes(c.kind)?-7:-(Math.max(5,pins.length*2.5+1)+6);
  let ins=`(symbol (lib_id "VELOX:${name}")(at ${x} ${y} 0)(unit 1)(in_bom yes)(on_board yes)(dnp no)(uuid ${uid(c.ref)})(property "Reference" ${qs(c.ref)} (at ${x} ${y+off} 0) ${ef(1.2)})(property "Value" ${qs(c.value)} (at ${x} ${y+off+3} 0) ${ef(1)})(property "Footprint" ${qs(c.footprint)} (at ${x} ${y} 0) ${ef(1,"hide")})`;
  for(const [pn,[px,py,a]] of Object.entries(layout)){
   const xx=x+px, yy=y-py,n=c.pins[pn];
   ins+=`(pin ${qs(pn)} (uuid ${uid(c.ref+"pin"+pn)}))`;
   if(n){
    const ex=xx+(a===0?-7.5:7.5), justification=a===0?"right bottom":"left bottom";
    wires.push(`(wire (pts (xy ${xx} ${yy})(xy ${ex} ${yy}))(stroke (width 0)(type default))(uuid ${uid(c.ref+pn+"wire")}))`);
    labels.push(`(label ${qs(n)} (at ${ex} ${yy} 0) ${ef(.95,`(justify ${justification})`)}(uuid ${uid(c.ref+pn+"label")}))`);
   }else nc.push(`(no_connect (at ${xx} ${yy})(uuid ${uid(c.ref+pn+"NC")}))`);
  }
  ins+=`(instances (project "VELOX_carrier_B" (path "/${uid("sheet")}" (reference ${qs(c.ref)})(unit 1)))))`;
  instances.push(ins);
 }
 // Power flags describe the external supplies at their actual connection points.
 symbols.push(`(symbol "VELOX:PWR_FLAG" (pin_names (offset 0))(in_bom no)(on_board no)(property "Reference" "#FLG" (at 0 3 0) ${ef()})(property "Value" "PWR_FLAG" (at 0 5 0) ${ef()})(symbol "PWR_FLAG_0_1" (polyline (pts (xy 0 0)(xy 0 2)(xy -2 3)(xy 0 4)(xy 2 3)(xy 0 2))(stroke (width .254)(type default))(fill (type none))))(symbol "PWR_FLAG_1_1" (pin power_out line (at 0 0 90)(length 0)(name "pwr" ${ef(.9,"hide")})(number "1" ${ef(.9,"hide")}))))`);
 ["GND","USB_VBUS","BAT_RUN"].forEach((n,i)=>{
  const ref="#FLG010"+(i+1),x=300+i*65,y=35;
  instances.push(`(symbol (lib_id "VELOX:PWR_FLAG")(at ${x} ${y} 0)(unit 1)(in_bom no)(on_board no)(dnp no)(uuid ${uid(ref)})(property "Reference" "${ref}" (at ${x} ${y-5} 0) ${ef(1,"hide")})(property "Value" "PWR_FLAG" (at ${x} ${y-7} 0) ${ef(1)})(pin "1" (uuid ${uid(ref+"pin1")}))(instances (project "VELOX_carrier_B" (path "/${uid("sheet")}" (reference "${ref}")(unit 1)))))`);
  labels.push(`(label "${n}" (at ${x} ${y} 0) ${ef(.95,"(justify left bottom)")}(uuid ${uid(ref+"label")}))`);
 });
 const notes=[
 [15,13,"VELOX REV B | SCHEMATIC + PLACEMENT REVIEW | NOT FOR FABRICATION",2],
 [15,21,"90 x 55 mm target. Copper routing and native ERC/DRC are unfinished. No manufacturing approval.",1.25],
 [15,34,"Nano ESP32 / 3.3V logic",1.3],[160,75,"USB-C / OVP / 100mA charger",1.3],
 [335,185,"6V coil driver",1.3],[335,278,"3.3V active buzzer / panel",1.3],
 [15,214,"RC522: remote, always powered",1.3],[15,302,"Battery monitor / calibrate ADC",1.3],
 [15,397,"Same net labels connect. NC crosses are intentional. Charge with RUN OFF and Nano USB unplugged.",1.1],
 [15,404,"Use a protected 1S cell. No onboard BMS, load sharing or temperature-qualified charging.",1.1],
 [15,411,"Power flags declare external supplies; they do not verify wiring. Polarity, coil load and enclosure fit require testing.",1.1]
 ];
 let sch=`(kicad_sch (version 20230121)(generator eeschema)(uuid ${uid("sheet")})(paper "A2")(lib_symbols ${symbols.join("\n")})\n${instances.concat(wires,labels,nc).join("\n")}\n`;
 notes.forEach(([x,y,str,sz],i)=>sch+=`(text ${qs(str)} (at ${x} ${y} 0) ${ef(sz,"(justify left)")}(uuid ${uid("text"+i)}))\n`);
 sch+='(sheet_instances (path "/" (page "1"))))\n';
 return {sch,sym:'(kicad_symbol_lib (version 20220914)(generator kicad_symbol_editor)\n'+symbols.map(x=>x.replace('(symbol "VELOX:','(symbol "')).join("\n")+'\n)\n'};
}
const spec=JSON.parse(fs.readFileSync(path.join(root,"design_spec.json"),"utf8"));
const out=nativeSchematic(spec);
fs.mkdirSync(path.join(root,"design"),{recursive:true});
fs.writeFileSync(path.join(root,"design","VELOX_carrier_B.kicad_sch"),out.sch);
fs.writeFileSync(path.join(root,"design","VELOX.kicad_sym"),out.sym);
fs.writeFileSync(path.join(root,"design","components.json"),JSON.stringify(spec.parts,null,2)+"\n");
console.log("Wrote Rev B schematic and component map.");
