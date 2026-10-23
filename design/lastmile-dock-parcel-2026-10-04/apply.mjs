import sharp from 'sharp';
const d='design/lastmile-dock-parcel-2026-10-04';const g='/home/michael/.config/codex/generated_images/01a0e88c-a0ab-7560-a60b-d425f4850713';
for(const format of ['wide','tall']){
 const neutral=`choice-neutral-${format}-${format==='wide'?'v1':'v2'}`;
 const id=format==='wide'?'exec-c95f924d-7ca4-43fc-93a8-a9bba3eb6866':'exec-4ba19296-f395-4adc-8475-71b26f26b319';
 const rect=format==='wide'?{left:585,top:415,width:85,height:76}:{left:145,top:924,width:67,height:62};
 const pos=format==='wide'?{left:585,top:415}:{left:100,top:733};
 const patch=await sharp(`${g}/${id}.png`).extract(rect).toBuffer();
 for(const name of [neutral,`lastmile-choice-${format}-v2`]){
  const layers=[];
  if(name.startsWith('lastmile')){
   const r=format==='wide'?{left:230,top:357,width:189,height:114}:{left:0,top:688,width:96,height:100};
   layers.push({input:await sharp(`${d}/before/${neutral}.webp`).extract(r).toBuffer(),left:r.left,top:r.top});
  }
  layers.push({input:patch,...pos});
  await sharp(`${d}/before/${name}.webp`).composite(layers).png().toFile(`${d}/${name}-dock.png`);
  await sharp(`${d}/${name}-dock.png`).webp({quality:97}).toFile(`public/scene-art/lastmile-family-v1/${name}.webp`);
 }
}
