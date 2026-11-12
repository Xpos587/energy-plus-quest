// Promote reviewed native paint only; never touch the original cast or geometry table.
import sharp from 'sharp';
import assert from 'node:assert/strict';
import { writeFile } from 'node:fs/promises';
const root='.tmp-work/scene4-final-render';
const names=['plate','barge','far','ladder','gift','box','hook','smoke','top','ivan'];
const formats=process.argv.slice(2);
assert(formats.length && formats.every(f=>['wide','desk','mid','tall'].includes(f)));
const rows=[];
for(const f of formats){
 const prepared=[];
 for(const name of names){
  const baseline=`${root}/blender-assets/${f}/${name}.webp`;
  const {width,height}=await sharp(baseline).metadata();
  const src=name==='plate'?`${root}/gpt/v4-plate-${f}.png`:name==='ivan'?`public/scene-art/barge-v4/${f}/ivan.webp`:`${root}/painted-assets/${f}/${name}.png`;
  const image=sharp(src);
  if(name==='ivan') image.resize(width,height,{fit:'fill'});
  const png=await image.png().toBuffer();
  const m=await sharp(png).metadata();
  assert.equal(m.width,width,`${f}/${name} width`);assert.equal(m.height,height,`${f}/${name} height`);
  const bytes=await sharp(png).webp({quality:92,alphaQuality:100,effort:5}).toBuffer();
  const reference=name==='ivan'?png:baseline;
  const a=await sharp(reference).ensureAlpha().extractChannel(3).raw().toBuffer();
  const b=await sharp(bytes).ensureAlpha().extractChannel(3).raw().toBuffer();
  assert(a.equals(b),`${f}/${name} alpha differs from ${reference}`);
  prepared.push({file:`public/scene-art/barge-v5/${f}/${name}.webp`,bytes});
  rows.push({format:f,name,source:src,width,height,alphaReference:name==='ivan'?'original v4 portrait resized to current box':'Blender baseline',alphaChangedPixels:0,bytes:bytes.length});
 }
 // Verify the whole format before replacing any runtime files.
 for(const {file,bytes} of prepared)await writeFile(file,bytes);
 console.log(`Promoted ${f}: ten reviewed assets, mechanical alpha exact; original v4 Ivan restored.`);
}
await writeFile(`${root}/promotion-${formats.join('-')}.json`,JSON.stringify(rows,null,2)+'\n');
