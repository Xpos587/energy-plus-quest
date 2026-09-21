import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const api=await import('./fit-map.mjs').catch(()=>null);
assert.ok(api,'Responsive fitting implementation is missing');
const {fitMap,placeTargets}=api;
const data=JSON.parse(readFileSync(new URL('projection.json',import.meta.url)));
let smallest=Infinity,maxDrift=0;
for(const [width,height,name] of [[320,300,'mobile'],[375,400,'mobile'],[390,470,'mobile'],[540,800,'mobile'],[344,300,'desktop'],[600,330,'desktop'],[1056,800,'desktop'],[2176,1300,'desktop']]){
 const view=data.views[name];
 const fit=fitMap(view,width,height);
 let min=Infinity;
 for(const row of view.tracks){
  const anchors=row.map(t=>[fit.x+t.marker[0]*fit.scale,fit.y+t.marker[1]*fit.scale]);
  const targets=placeTargets(anchors,width,height);
  for(let i=0;i<row.length;i++){
   const b=row[i].bounds.map((p,k)=>p*fit.scale+(k%2?fit.y:fit.x));
   assert.ok(b[0]>=7.99&&b[1]>=7.99&&b[2]<=width-7.99&&b[3]<=height-7.99,'Truck clipped');
   const [x,y]=targets[i];assert.ok(x>=22&&y>=22&&x<=width-22&&y<=height-22,`Target clipped: ${width}x${height}: ${x}, ${y}`);
   const drift=Math.hypot(x-anchors[i][0],y-anchors[i][1]);maxDrift=Math.max(drift,maxDrift);
   assert.ok(drift<=6,'Badge detached from roof');
   for(const [xx,yy] of targets.slice(i+1))assert.ok(Math.abs(x-xx)>=44-1e-5||Math.abs(y-yy)>=44-1e-5,'Tap targets overlap');
   min=Math.min(min,Math.max(b[2]-b[0],b[3]-b[1]));
  }
 }
 assert.ok(min>=48,`Truck too small: ${width}x${height} ${name}: ${min}`);
 smallest=Math.min(smallest,min);
 const [x0,y0,x1,y1]=view.warehouse;
 assert.ok(fit.x+x0*fit.scale>=7.99&&fit.y+y0*fit.scale>=7.99&&fit.x+x1*fit.scale<=width-7.99&&fit.y+y1*fit.scale<=height-7.99,'Warehouse clipped');
 console.log(`${width}x${height} ${name}: smallest truck ${min.toFixed(2)} CSS px`);
}
console.log({smallest,maxDrift,checkedFrames:768*8});
