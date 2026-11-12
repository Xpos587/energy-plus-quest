import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile,writeFile} from 'node:fs/promises';
import sharp from 'sharp';
import {craneLayers,craneWorld} from '../../src/scenes/crane/layers.ts';
const root='.tmp-work/scene4-final-render';
const baseline=JSON.parse(await readFile(`${root}/current/geometry.json`,'utf8'));
assert.deepEqual(craneWorld,baseline.craneWorld);
const formats=[],files=new Set();
for(const [name,f] of Object.entries(craneLayers)){
 const m=JSON.parse(await readFile(`${root}/manifests/${name}.json`,'utf8'));
 assert.equal(m.render.scale,2);assert.equal(m.render.samples,128);assert.equal(m.scene.slews.length,16);
 assert.equal(f.width,baseline.craneLayers[name].width);assert.equal(f.height,baseline.craneLayers[name].height);
 let anchorDelta=0,affineDelta=0;
 for(const [key,point] of Object.entries(f.anchors))point.forEach((n,i)=>anchorDelta=Math.max(anchorDelta,Math.abs(n-baseline.craneLayers[name].anchors[key][i])));
 f.affine.forEach((row,j)=>row.forEach((n,i)=>affineDelta=Math.max(affineDelta,Math.abs(n-baseline.craneLayers[name].affine[j][i]))));
 // Wide's old 809*1.5 height rounded upward to1214; exact2x changes projections by0.1px, not the camera.
 assert.ok(anchorDelta<=0.10001);assert.ok(affineDelta<=0.10001);
 const plate=await sharp(`public/${f.plate}`).metadata();
 assert.equal(plate.width,f.width*2);assert.equal(plate.height,f.height*2);files.add(f.plate);
 for(const [key,s] of Object.entries(f.sprites)){
  const meta=await sharp(`public/${s.src}`).metadata();
  assert.equal(meta.width,s.w*2,`${name}/${key} width`);assert.equal(meta.height,s.h*2,`${name}/${key} height`);
  assert.ok(s.x>=0&&s.y>=0&&s.x+s.w<=f.width+.01&&s.y+s.h<=f.height+.01);
  assert.equal(meta.hasAlpha,true,`${name}/${key} transparency`);
  files.add(s.src);
 }
 const atlas=await sharp(`public/${f.top.src}`).metadata();
 assert.equal(f.top.cols*f.top.rows,16);assert.equal(atlas.width,f.top.w*2*f.top.cols);assert.equal(atlas.height,f.top.h*2*f.top.rows);files.add(f.top.src);
 formats.push({name,width:plate.width,height:plate.height,frames:16,maxAnchorDelta:anchorDelta,maxAffineDelta:affineDelta});
}
for(const id of ['remote','rush','petr'])for(const suffix of ['','-rail','-portrait']){
 const path=`scene-art/barge-v5/outcome-${id}${suffix}.webp`;
 const m=await sharp(`public/${path}`).metadata();
 if(!suffix){assert.equal(m.width,3884);assert.equal(m.height,1618);}
 else if(suffix==='-portrait'){assert.equal(m.width,2048);assert.equal(m.height,3072);}
 else{assert.ok(m.width>2000&&m.height>2000&&m.width<=2804&&m.height<=2244);assert.ok(Math.abs(m.width/m.height-1.11)<.001);}
 files.add(path);
}
const media=[];
for(const path of files){const data=await readFile(`public/${path}`);const m=await sharp(data).metadata();media.push({path,bytes:data.length,width:m.width,height:m.height,sha256:createHash('sha256').update(data).digest('hex')});}
assert.equal(media.length,49);
await writeFile(`${root}/export-checks.json`,JSON.stringify({worldIdentical:true,formats,media},null,2)+'\n');
console.log('PASS:4 formats,64 atlas frames,32 sprites,4 plates,9 outcomes;49 files inventoried;world unchanged;projection drift<=0.1px');
