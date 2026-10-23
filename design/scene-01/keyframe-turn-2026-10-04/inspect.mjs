import sharp from 'sharp';
import { readdir } from 'node:fs/promises';
const dir='design/scene-01/keyframe-turn-2026-10-04';
const files=(await readdir(`${dir}/frames`)).filter(f=>f.endsWith('.png')).sort();
const tiles=[];
for(let i=0;i<files.length;i++){
 const frame=await sharp(`${dir}/frames/${files[i]}`).resize(320,240).toBuffer();
 const label=Buffer.from(`<svg width="320" height="24"><rect width="320" height="24" fill="white"/><text x="8" y="17" font-size="15">${i*0.5} s</text></svg>`);
 tiles.push({input:frame,left:(i%4)*320,top:Math.floor(i/4)*264});
 tiles.push({input:label,left:(i%4)*320,top:Math.floor(i/4)*264+240});
}
await sharp({create:{width:1280,height:Math.ceil(files.length/4)*264,channels:3,background:'white'}}).composite(tiles).png().toFile(`${dir}/contact.png`);
