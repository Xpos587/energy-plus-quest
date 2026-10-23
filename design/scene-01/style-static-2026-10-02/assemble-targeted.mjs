import sharp from 'sharp';
const d=new URL('.',import.meta.url).pathname;
const y=await sharp('/home/michael/.config/codex/generated_images/01a0e88c-a0ab-7560-a60b-d425f4850713/exec-3abdebbd-3f8c-4bf4-aed5-64628e3ea3fe.png').resize(430,145,{fit:'fill'}).png().toBuffer();
await sharp(d+'detail-se.png').composite([{input:y,left:330,top:255}]).png().toFile(d+'detail-se-fixed.png');
const source={nw:[0,0,730,635],ne:[670,0,836,635],se:[670,575,836,470]};
const patches=[['nw',100,105,305,505],['nw',406,303,80,244],['ne',749,492,278,106],['ne',1090,316,103,238],['se',720,680,345,106]];
const layers=[];
for(const [n,x,y,w,h] of patches){
 const [tx,ty,tw,th]=source[n];
 const full=await sharp(d+`detail-${n}${n==='se'?'-fixed':''}.png`).resize(tw*2,th*2,{fit:'fill'}).png().toBuffer();
 const patch=await sharp(full).extract({left:(x-tx)*2,top:(y-ty)*2,width:w*2,height:h*2}).ensureAlpha().raw().toBuffer({resolveWithObject:true});
 const base=await sharp(d+'map-v5-lanes.png').resize(3012,2090,{fit:'fill'}).extract({left:x*2,top:y*2,width:w*2,height:h*2}).ensureAlpha().raw().toBuffer();
 const offsets=[[],[],[]];
 for(let r=2;r<patch.info.height-2;r+=4)for(let c=2;c<patch.info.width-2;c+=4){
  if(Math.min(c,r,patch.info.width-c,patch.info.height-r)>12)continue;
  const i=(r*patch.info.width+c)*4;
  for(let ch=0;ch<3;ch++)offsets[ch].push(base[i+ch]-patch.data[i+ch]);
 }
 const shifts=offsets.map(a=>a.sort((a,b)=>a-b)[Math.floor(a.length/2)]);
 const {data,info}=patch;
 for(let i=0;i<data.length;i+=4)for(let ch=0;ch<3;ch++)data[i+ch]=Math.max(0,Math.min(255,data[i+ch]+shifts[ch]));
 for(let r=0;r<info.height;r++)for(let c=0;c<info.width;c++){
   const edge=Math.min(c,r,info.width-1-c,info.height-1-r);
   data[(r*info.width+c)*4+3]=Math.round(255*Math.min(1,edge/24));
 }
 layers.push({input:await sharp(data,{raw:info}).png().toBuffer(),left:x*2,top:y*2});
}
await sharp(d+'map-v5-lanes.png').resize(3012,2090,{fit:'fill'}).composite(layers).png().toFile(d+'map-v7-detail.png');
for(const [name,left,top,width,height] of [['green',2180,850,210,240],['yellow',1640,1390,460,180],['blue',813,866,160,220],['warehouse',220,220,570,570]])
 await sharp(d+'map-v7-detail.png').extract({left,top,width,height}).png().toFile(d+`v7-${name}-detail.png`);
