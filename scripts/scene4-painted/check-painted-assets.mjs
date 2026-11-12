import sharp from 'sharp';
import assert from 'node:assert/strict';
import { readFile, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { createHash } from 'node:crypto';

async function sameGeometry(source,target,name){
 const [a,b]=await Promise.all([sharp(source).ensureAlpha().raw().toBuffer({resolveWithObject:true}),sharp(target).ensureAlpha().raw().toBuffer({resolveWithObject:true})]);
 assert.equal(b.info.width,a.info.width,`${name}: width changed`);
 assert.equal(b.info.height,a.info.height,`${name}: height changed`);
 let changed=0;
 for(let i=3;i<a.data.length;i+=4)if(a.data[i]!==b.data[i])changed++;
 assert.equal(changed,0,`${name}: alpha changed at ${changed} pixels`);
 return {width:a.info.width,height:a.info.height,alphaChangedPixels:changed};
}
async function liveCrop(buffer, receipt, name) {
 assert(receipt, `${name}: missing live-capture receipt`);
 assert.equal(createHash('sha256').update(buffer).digest('hex'), receipt.sha256, `${name}: receipt hash mismatch`);
 const {data,info}=await sharp(buffer).ensureAlpha().raw().toBuffer({resolveWithObject:true});
 const {clip:c,hull:h,inset}=receipt;
 assert.equal(info.width,receipt.width); assert.equal(info.height,receipt.height);
 assert(Math.abs(info.width-c.width*2)<=2 && Math.abs(info.height-c.height*2)<=2, `${name}: not a native 2x crop`);
 assert(c.x>=0 && c.y>=0 && c.x+c.width<=1402.001 && c.y+c.height<=1122.001, `${name}: outside mid camera`);
 assert(Math.abs(c.width/c.height-1.11)<1e-6 && inset===0.0675, `${name}: rail crop contract changed`);
 assert(h.x>=c.x+c.width*inset && h.y>=c.y+c.height*inset && h.x+h.width<=c.x+c.width*(1-inset) && h.y+h.height<=c.y+c.height*(1-inset), `${name}: hull outside safe crop`);
 for(let i=3;i<data.length;i+=4)assert.equal(data[i],255, `${name}: transparent result pixel`);
 return {width:info.width,height:info.height,alphaChangedPixels:0,clip:c};
}
async function restoredPortrait(original, width, height) {
 const png = await sharp(original).resize(width, height, {fit:'fill'}).png().toBuffer();
 return sharp(png).webp({quality:92,alphaQuality:100,effort:5}).toBuffer();
}
const isPortrait = name => /^(wide|desk|mid|tall)\/ivan\.webp$/.test(name);
const isCore = name => /^(wide|desk|mid|tall)\/(plate|barge|far|ladder|gift|box|hook|smoke|top|ivan)\.webp$/.test(name) || /^outcome-(remote|rush|petr)(-rail|-portrait)?\.webp$/.test(name);
if(process.argv[2]==='--self-test'){
 const rgba=Buffer.from([20,30,40,0,50,60,70,128]);
 const image=await sharp(rgba,{raw:{width:2,height:1,channels:4}}).png().toBuffer();
 await sameGeometry(image,image,'identical');
 rgba[3]=1;
 const changed=await sharp(rgba,{raw:{width:2,height:1,channels:4}}).png().toBuffer();
 await assert.rejects(sameGeometry(image,changed,'negative fixture'),/alpha changed at 1 pixels/);
 const resized=await sharp(image).resize(3,1).png().toBuffer();
 await assert.rejects(sameGeometry(image,resized,'negative dimensions'),/width changed/);
 const portrait = await restoredPortrait(image, 4, 2);
 await sameGeometry(portrait, portrait, 'restored identity');
 assert(!portrait.equals(await restoredPortrait(changed, 4, 2)), 'identity encoding must detect altered source');
 assert(isPortrait('wide/ivan.webp') && !isPortrait('wide/ivan-wave.webp') && !isPortrait('wide/barge.webp'));
 const opaque=await sharp({create:{width:200,height:180,channels:4,background:'#123456'}}).png().toBuffer();
 const receipt={width:200,height:180,sha256:createHash('sha256').update(opaque).digest('hex'),clip:{x:10,y:0,width:100,height:100/1.11},hull:{x:30,y:10,width:40,height:40},inset:0.0675};
 await liveCrop(opaque,receipt,'live rail');
 await assert.rejects(liveCrop(opaque,{...receipt,clip:{...receipt.clip,width:110}},'bad size'),/not a native 2x crop/);
 await assert.rejects(liveCrop(opaque,{...receipt,hull:{...receipt.hull,x:0}},'bad hull'),/hull outside safe crop/);
 console.log('PASS: exact alpha, negative alpha/dimensions, exact original portraits, live-crop size and hull bounds');
}else{
 const baseline=process.argv[2]||'.tmp-work/scene4-final-render/blender-assets';
 const target=process.argv[3]||'public/scene-art/barge-v5';
 const files=async root=>Array.fromAsync(new Bun.Glob('**/*.webp').scan({cwd:root})).then(a=>a.sort());
 const names=await files(baseline);
 assert.deepEqual(await files(target),names,'Runtime asset inventory changed');
 const rows=[];
 const crops=JSON.parse(await readFile(process.argv[5]||'.tmp-work/scene4-final-render/outcome-crops.json','utf8'));
 let originalCastFiles=0;
 for(const name of names){
  const [a,b]=await Promise.all([readFile(join(baseline,name)),readFile(join(target,name))]);
  let reference=a, alphaReference='Blender baseline';
  if(isPortrait(name)){
   const {width,height}=await sharp(a).metadata();
   alphaReference=join('public/scene-art/barge-v4',name);
   reference=await restoredPortrait(alphaReference,width,height);
   assert(reference.equals(b),`${name}: must exactly match the original v4 portrait resized to the current box and encoded at quality 92`);
  }
  if(!isCore(name)){
   assert(a.equals(b),`${name}: preserved cast asset changed from baseline`);
   assert(b.equals(await readFile(join('public/scene-art/barge-v4',name))),`${name}: no longer byte-identical to original v4 cast`);
   originalCastFiles++;
  }
  const rail=/^outcome-(remote|rush|petr)-rail\.webp$/.test(name);
  const geometry=rail ? await liveCrop(b,crops.find(row=>row.output.endsWith('/'+name)),name) : await sameGeometry(reference,b,name);
  if(rail)alphaReference='Live 1.11:1 cover-safe crop; opaque alpha (dynamic bounds, not baseline dimensions)';
  rows.push({name,...geometry,alphaReference,unchangedBytes:a.equals(b)});
 }
 assert.equal(rows.length,121,'Expected 49 core assets plus 72 preserved cast assets');
 assert.equal(originalCastFiles,72,'Original cast inventory changed');
 assert.equal(rows.filter(row=>isPortrait(row.name)).length,4,'Expected exactly four restored portraits');
 const receipt={baseline,target,files:rows.length,originalCastFiles,baselineAlphaExceptions:{restoredPortraits:4,liveCrops:3},unchangedFiles:rows.filter(x=>x.unchangedBytes).length,rows};
 const out=process.argv[4]||'.tmp-work/scene4-final-render/alpha-checks.json';
 await writeFile(out,JSON.stringify(receipt,null,2)+'\n');
 console.log(`PASS: 114 baseline alpha masks; 4 exact original-portrait reconstructions; 3 verified live crops; 72 original cast files byte-identical; ${out}`);
}
