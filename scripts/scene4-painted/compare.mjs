import sharp from 'sharp';
import { mkdir } from 'node:fs/promises';
const root='.tmp-work/scene4-final-render',out=`${root}/blender-vs-final`;
await mkdir(out,{recursive:true});
const label=(width,text='')=>Buffer.from(`<svg width="${width*2}" height="42"><rect width="100%" height="100%" fill="white"/><g font-family="sans-serif" font-size="18" fill="#17354b"><text x="12" y="28">BLENDER ${text}</text><text x="${width+12}" y="28">FINAL ${text}</text></g></svg>`);
async function pair(file,name,width){
 const buffers=await Promise.all(['blender','final'].map(s=>sharp(`${root}/${s}/${file}`).resize({width}).png().toBuffer()));
 const heights=await Promise.all(buffers.map(async b=>(await sharp(b).metadata()).height));
 // Rail crops depend on live departure bounds; preserve each image's actual ratio.
 const height=Math.max(...heights);
 await sharp({create:{width:width*2,height:height+42,channels:3,background:'white'}}).composite([{input:label(width),left:0,top:0},...buffers.map((input,i)=>({input,left:i*width,top:42}))]).png().toFile(`${out}/${name}.png`);
}
for(const format of ['wide','desk','mid','tall'])await pair(`art-${format}.png`,format,format==='tall'?600:1000);
for(const way of ['remote','rush','petr'])for(const suffix of ['','-rail','-portrait'])await pair(`outcome-${way}${suffix}.webp`,`outcome-${way}${suffix}`,suffix==='-portrait'?500:800);
// Native pixels, no upscaling: original portrait, gift, crane cab and barge materials.
const boxes=[{left:1072,top:784,width:220,height:139},{left:1512,top:713,width:146,height:155},{left:1510,top:0,width:788,height:776},{left:1365,top:871,width:800,height:400}];
let y=42;const layers=[{input:label(820,'— 100% native pixels'),left:0,top:0}];
for(const b of boxes){for(const [i,s] of ['blender','final'].entries())layers.push({input:await sharp(`${root}/${s}/art-wide.png`).extract(b).png().toBuffer(),left:i*820,top:y});y+=b.height+20;}
await sharp({create:{width:1640,height:y,channels:3,background:'white'}}).composite(layers).png().toFile(`${out}/detail-crops-100.png`);
console.log('Four native formats, nine live outcomes and unscaled native detail comparisons');
