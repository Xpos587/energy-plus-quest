import sharp from 'sharp';
import {readFile} from 'node:fs/promises';
const here=new URL('./',import.meta.url).pathname;
const patches=JSON.parse(await readFile(here+'patches.json','utf8'));
const polygons={
 keeper:'38,10 64,10 73,25 79,36 80,55 75,64 65,66 61,75 45,88 29,88 28,81 39,78 39,58 33,54 33,45 19,46 12,42 12,35 24,33 34,35 38,30',
 drone:'8,12 96,12 96,78 8,78',
 forklift:'17,8 26,5 29,0 37,0 39,7 53,8 54,4 66,4 68,38 82,34 97,39 99,88 91,95 80,93 68,87 59,86 52,89 40,83 33,78 23,71 14,76 3,70 2,59 4,44 6,37 11,34 12,19',
 rear:'39,8 69,8 78,19 75,25 88,28 91,38 91,69 81,73 73,82 54,99 36,99 37,91 40,68 38,57 41,52 31,49 23,44 21,40 16,36 15,29 30,27 34,34 40,39 46,32 44,28 42,21 37,20'
};
const layers=[];
for(const p of patches){const w=p.w*3,h=p.h*3;
 const mask=Buffer.from(`<svg width="${w}" height="${h}" viewBox="0 0 100 100" preserveAspectRatio="none"><polygon points="${polygons[p.name]}" fill="white" stroke="white" stroke-width="3"/></svg>`);
 const input=await sharp(p.file).resize(w,h,{fit:'fill'}).composite([{input:await sharp(mask).blur(10).png().toBuffer(),blend:'dest-in'}]).png().toBuffer();
 layers.push({input,left:p.x*3,top:p.y*3});}
await sharp(here+'master-v2.png').resize(5016,2823).composite(layers).png().toFile(here+'warehouse-master-v3.png');
await sharp(here+'warehouse-master-v3.png').webp({quality:96}).toFile(here+'warehouse-master-v3.webp');
