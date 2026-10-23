import sharp from 'sharp';
import fs from 'node:fs/promises';
const dir = new URL('.', import.meta.url).pathname;
const generated = '/home/michael/.config/codex/generated_images/01a0e88c-a0ab-7560-a60b-d425f4850713/';
const tiles = [
 ['nw',0,0,730,635,'exec-355b43af-36f4-4c3c-a044-207b8d084e08.png'],
 ['ne',670,0,836,635,'exec-66a4da43-d8fb-4139-bc64-829a81b987a0.png'],
 ['sw',0,575,730,470,'exec-a2da268b-b313-416e-ac68-4121bf70cc4a.png'],
 ['se',670,575,836,470,'exec-b2b898f5-b574-4a94-a4d6-4f55e1268003.png'],
];
const layers=[];
for (const [name,x,y,w,h,file] of tiles) {
 await fs.copyFile(generated+file,dir+`detail-${name}.png`);
 const {data,info}=await sharp(dir+`detail-${name}.png`).resize(w*2,h*2,{fit:'fill'}).ensureAlpha().raw().toBuffer({resolveWithObject:true});
 for(let row=0;row<info.height;row++)for(let col=0;col<info.width;col++){
  const a=(x?Math.min(1,col/120):1)*(y?Math.min(1,row/120):1);
  data[(row*info.width+col)*4+3]=Math.round(255*a);
 }
 layers.push({input:await sharp(data,{raw:info}).png().toBuffer(),left:x*2,top:y*2});
}
await sharp({create:{width:3012,height:2090,channels:3,background:'#aecedf'}}).composite(layers).png().toFile(dir+'map-v6-detail.png');
for(const [name,left,top,width,height] of [['green',2150,630,190,460],['yellow',1610,1385,495,200],['warehouse',170,190,620,650]])
 await sharp(dir+'map-v6-detail.png').extract({left,top,width,height}).png().toFile(dir+`v6-${name}-detail.png`);
console.log('Composited 3012 x 2090; generated detail in four tiles.');
