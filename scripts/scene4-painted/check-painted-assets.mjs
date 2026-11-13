// Current Scene 4 contracts. No dependency on an expiring scratch Blender export.
// Usage: bun scripts/scene4-painted/check-painted-assets.mjs [runtimeDir] [receiptOut] [captureReceipt]
import sharp from 'sharp';
import assert from 'node:assert/strict';
import { readFile, writeFile } from 'node:fs/promises';
import { join, resolve } from 'node:path';
import { createHash } from 'node:crypto';
import { craneOperatorBoxes } from '../../src/scenes/crane/cast';

const root=resolve(import.meta.dirname,'../..');
const painted=join(root,'design/scene-04/blender-v4/painted');
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const json=async path=>JSON.parse(await readFile(path,'utf8'));
async function alpha(image){
 return sharp(image).ensureAlpha().extractChannel(3).raw().toBuffer({resolveWithObject:true});
}
async function geometry(image,reference,name){
 const {data,info}=await alpha(image);
 assert.equal(info.width,reference.width,`${name}: width changed`);
 assert.equal(info.height,reference.height,`${name}: height changed`);
 assert.equal(hash(data),reference.alphaSha256,`${name}: alpha changed`);
 return {width:info.width,height:info.height,alphaExact:true};
}
async function originalPortrait(source,width,height){
 const png=await sharp(source).resize(width,height,{fit:'fill'}).png().toBuffer();
 return sharp(png).webp({quality:92,alphaQuality:100,effort:5}).toBuffer();
}
async function liveCrop(buffer,receipt,name){
 assert(receipt,`${name}: missing live-capture receipt`);
 assert.equal(hash(buffer),receipt.sha256,`${name}: capture hash mismatch`);
 const {data,info}=await alpha(buffer),{clip:c,hull:h,inset}=receipt;
 assert.equal(info.width,receipt.width);assert.equal(info.height,receipt.height);
 assert(Math.abs(info.width-c.width*2)<=2&&Math.abs(info.height-c.height*2)<=2,`${name}: not a native 2x crop`);
 const [w,ht]=receipt.format==='wide'?[1942,809]:receipt.format==='tall'?[1024,1536]:[1402,1122];
 assert(c.x>=0&&c.y>=0&&c.x+c.width<=w+.001&&c.y+c.height<=ht+.001,`${name}: outside camera`);
 if(receipt.format==='mid')assert(Math.abs(c.width/c.height-1.11)<1e-6&&inset===.0675,`${name}: rail contract changed`);
 else assert(c.x===0&&c.y===0&&c.width===w&&c.height===ht&&inset===0,`${name}: full-camera contract changed`);
 assert(h.x>=c.x+c.width*inset&&h.y>=c.y+c.height*inset&&h.x+h.width<=c.x+c.width*(1-inset)&&h.y+h.height<=c.y+c.height*(1-inset),`${name}: hull outside safe crop`);
 assert(data.every(a=>a===255),`${name}: transparent result pixel`);
 return {width:info.width,height:info.height,opaque:true,clip:c};
}
async function operator(buffer,format,actor,visibility){
 const {data,info}=await alpha(buffer),box=craneOperatorBoxes[format];
 assert.equal(info.width,box.w*16,`${format}/${actor}: atlas width/placement mismatch`);
 assert.equal(info.height,box.h*16,`${format}/${actor}: atlas height/placement mismatch`);
 const cw=info.width/4,ch=info.height/4,frames=Array(16).fill(0);
 for(let y=0;y<info.height;y++)for(let x=0;x<info.width;x++)if(data[y*info.width+x])frames[Math.floor(y/ch)*4+Math.floor(x/cw)]++;
 for(let frame=0;frame<16;frame++){
  const proof=visibility.find(r=>r.format===format&&r.actor===actor&&r.frame===frame);
  assert(proof,`${format}/${actor}/${frame}: missing visibility proof`);
  assert.equal(proof.shown,proof.headRetained>=.9&&proof.headConnected>=.88);
  assert.equal(frames[frame]>0,proof.shown,`${format}/${actor}/${frame}: occlusion contract changed`);
 }
 return {width:info.width,height:info.height,framesWithOperator:frames.filter(Boolean).length};
}
const core=name=>/^(wide|desk|mid|tall)\/(plate|barge|far|ladder|gift|box|hook|smoke|top|ivan)\.webp$/.test(name);
if(process.argv[2]==='--self-test'){
 const rgba=Buffer.from([20,30,40,0,50,60,70,128]);
 const image=await sharp(rgba,{raw:{width:2,height:1,channels:4}}).png().toBuffer();
 const ref={width:2,height:1,alphaSha256:hash(Buffer.from([0,128]))};
 await geometry(image,ref,'same');rgba[3]=1;
 const changed=await sharp(rgba,{raw:{width:2,height:1,channels:4}}).png().toBuffer();
 await assert.rejects(geometry(changed,ref,'bad alpha'),/alpha changed/);
 await assert.rejects(geometry(image,{...ref,width:3},'bad width'),/width changed/);
 assert.notEqual(hash(image),hash(changed));
 const opaque=await sharp({create:{width:200,height:180,channels:4,background:'#123456'}}).png().toBuffer();
 const receipt={format:'mid',width:200,height:180,sha256:hash(opaque),clip:{x:10,y:0,width:100,height:100/1.11},hull:{x:30,y:10,width:40,height:40},inset:.0675};
 await liveCrop(opaque,receipt,'rail');
 await assert.rejects(liveCrop(opaque,{...receipt,sha256:'bad'},'bad hash'),/hash mismatch/);
 await assert.rejects(liveCrop(opaque,{...receipt,hull:{...receipt.hull,x:0}},'bad hull'),/hull outside/);
 await assert.rejects(liveCrop(opaque,{...receipt,clip:{...receipt.clip,width:110}},'bad density'),/native 2x/);
 console.log('PASS: exact-alpha, dimensions, content-hash, live-crop density and hull negative checks');
}else{
 const target=process.argv[2]||join(root,'public/scene-art/barge-v5');
 const out=process.argv[3]||join(painted,'receipts/alpha-checks.json');
 const crops=await json(process.argv[4]||join(painted,'receipts/outcome-crops.json'));
 const base=(await json(join(painted,'receipts/geometry-baseline.json'))).rows;
 const heads=(await json(join(painted,'receipts/office-alpha-reference.json'))).rows;
 const visibility=await json(join(painted,'receipts/operator-visibility.json'));
 const media=(await json(join(painted,'receipts/media-files.json'))).rows;
 const files=async dir=>(await Array.fromAsync(new Bun.Glob('**/*.webp').scan({cwd:dir}))).sort();
 const original=join(root,'public/scene-art/barge-v4'),names=await files(target);
 const preservedNames=(await files(original)).filter(name=>!core(name)&&!name.startsWith('outcome-')&&!name.endsWith('/ivan-watch.webp'));
 const expected=[...new Set([...Object.keys(base),...preservedNames])].sort();
 assert.deepEqual(names,expected,'Runtime inventory changed');assert.equal(names.length,121);
 const rows=[];let preserved=0;
 for(const name of names){
  const bytes=await readFile(join(target,name));
  const approved=media.find(r=>r.path===`public/scene-art/barge-v5/${name}`);
  assert(approved,`${name}: missing accepted media hash`);
  assert.equal(hash(bytes),approved.sha256,`${name}: differs from accepted media`);
  let check,contract;
  const [format,file]=name.split('/');
  if(name.startsWith('outcome-')){
   const capture=crops.find(r=>r.output.endsWith('/'+name));
   assert.equal(capture?.format,name.includes('-rail.')?'mid':name.includes('-portrait.')?'tall':'wide');
   check=await liveCrop(bytes,capture,name);contract='live 2x capture';
  }else if(heads[name]){
   assert.equal(hash(await readFile(join(painted,'face-inputs',name))),heads[name].sourceSha256,`${name}: office input changed`);
   check=await geometry(bytes,heads[name],name);contract='original alpha resampled 2x (Pillow LANCZOS)';
  }else if(/^top-(ivan|petr)\.webp$/.test(file)){
   check=await operator(bytes,format,file.slice(4,-5),visibility);contract='compact 4x operator, 16 synchronized frames';
  }else if(file==='far-empty.webp'){
   check=await geometry(bytes,base[`${format}/far.webp`],name);contract='far base geometry, not legacy cab box';
  }else if(file==='ivan.webp'){
   const ref=base[name];assert(bytes.equals(await originalPortrait(join(original,name),ref.width,ref.height)),`${name}: legacy portrait changed`);
   check={width:ref.width,height:ref.height};contract='unchanged reconstructed legacy portrait; unused at runtime';
  }else if(core(name)){
   check=await geometry(bytes,base[name],name);contract='exact original Blender alpha and dimensions';
  }else{
   assert(bytes.equals(await readFile(join(original,name))),`${name}: preserved original cast changed`);preserved++;
   check={unchangedBytes:true};contract='byte-identical v4 cast';
  }
  rows.push({name,...check,contract});
 }
 assert.equal(preserved,44);
 await writeFile(out,JSON.stringify({files:121,originalCastFiles:preserved,mechanicalAlpha:36,legacyPortraits:4,officeAlpha:16,compactOperators:8,farEmptyAlpha:4,liveCrops:9,rows},null,2)+'\n');
 console.log(`PASS: all121 accepted hashes;36 exact mechanical masks;44 original cast;4 unused portraits;16 office masks;8 operators;4 far-empty masks;9 live crops. ${out}`);
}
