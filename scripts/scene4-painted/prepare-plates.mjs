// Recreate native input crops from the reviewed four-format tile manifests.
// This preserves their explicit registration/identity-review annotations.
import sharp from 'sharp';
import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
const p='.tmp-work/scene4-final-render/gpt';
await mkdir(p,{recursive:true});
for(const format of process.argv.slice(2)){
 assert(['wide','desk','mid','tall'].includes(format),'Use wide|desk|mid|tall');
 const text=await readFile(`design/scene-04/blender-v4/painted/manifests/v4-plate-${format}-tiles.json`,'utf8');
 const manifest=JSON.parse(text),src=`.tmp-work/scene4-final-render/blender-assets/${format}/plate.webp`;
 const metadata=await sharp(src).metadata();
 assert.equal(metadata.width,manifest.width);assert.equal(metadata.height,manifest.height);
 for(const {name,left,top,width,height} of manifest.tiles)await sharp(src).extract({left,top,width,height}).png().toFile(`${p}/${name}-input.png`);
 await writeFile(`${p}/v4-plate-${format}-tiles.json`,text);
 console.log(format,manifest.width,manifest.height,manifest.tiles.length);
}
