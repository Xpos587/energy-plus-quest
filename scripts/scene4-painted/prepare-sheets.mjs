import sharp from 'sharp';
import {writeFile} from 'node:fs/promises';
const format=process.argv[2]||'wide';
const p='.tmp-work/scene4-final-render/gpt', src=`.tmp-work/scene4-final-render/blender-assets/${format}`;
// Bounded shelf layout: barge first, remaining six props beneath it, at native pixels.
const names=['barge','far','ladder','gift','box','hook','smoke'];
const metadata=await Promise.all(names.map(async name=>({name,...await sharp(`${src}/${name}.webp`).metadata()})));
const width=Math.ceil(Math.max(metadata[0].width+32,metadata.slice(1).reduce((n,m)=>n+m.width+16,16))/16)*16;
const secondY=metadata[0].height+32;
const height=Math.ceil((secondY+Math.max(...metadata.slice(1).map(m=>m.height))+16)/16)*16;
let x=16;const sprites=metadata.map((m,i)=>{const rect={name:m.name,left:i?x:16,top:i?secondY:16,width:m.width,height:m.height};if(i)x+=m.width+16;return rect;});
await sharp({create:{width,height,channels:3,background:'#f8f5ef'}}).composite(sprites.map(s=>({input:`${src}/${s.name}.webp`,left:s.left,top:s.top}))).png().toFile(`${p}/v4-sprites-${format}-input.png`);
await writeFile(`${p}/v4-sprites-${format}.json`,JSON.stringify({width,height,sprites},null,2)+'\n');
console.log(`sprites ${format}: ${width}x${height}`);
const atlas=`${src}/top.webp`, m=await sharp(atlas).metadata(), fw=m.width/4,fh=m.height/4;
for(let group=0;group<4;group++){
 const width=Math.ceil((fw*2+48)/16)*16,height=Math.ceil((fh*2+48)/16)*16, frames=[];
 for(let k=0;k<4;k++)frames.push({frame:group*4+k,left:16+(k%2)*(fw+16),top:16+Math.floor(k/2)*(fh+16),width:fw,height:fh});
 const layers=await Promise.all(frames.map(async f=>({input:await sharp(atlas).extract({left:(f.frame%4)*fw,top:Math.floor(f.frame/4)*fh,width:fw,height:fh}).png().toBuffer(),left:f.left,top:f.top})));
 await sharp({create:{width,height,channels:3,background:'#f8f5ef'}}).composite(layers).png().toFile(`${p}/v4-top-${format}-${group}-input.png`);
 await writeFile(`${p}/v4-top-${format}-${group}.json`,JSON.stringify({width,height,frames},null,2)+'\n');
 console.log(`top ${format} group${group}: ${width}x${height}`);
}
