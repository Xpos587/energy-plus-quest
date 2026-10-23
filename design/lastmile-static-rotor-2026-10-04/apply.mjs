import sharp from 'sharp';
const root='design/lastmile-static-rotor-2026-10-04';
const generated='/home/michael/.config/codex/generated_images/01a0e88c-a0ab-7560-a60b-d425f4850713';
const rows=[['lastmile-choice-wide-v2','exec-baec8fee-657c-4e77-bede-d5cecad606f4'],['lastmile-choice-tall-v2','exec-2f824af1-07bc-4788-80cd-0d22118fb086'],['choice-neutral-wide-v1','exec-4fc993a9-44ac-4c72-aa1a-246c3ff7c24e'],['choice-neutral-tall-v2','exec-6a58908f-10a1-49bc-a7c2-b72d1a607dd4']];
for(const [name,id] of rows){
 const original=`${root}/before/${name}.webp`;const meta=await sharp(original).metadata();
 const rect=name.includes('wide')?{left:690,top:23,width:269,height:159}:{left:222,top:484,width:173,height:112};
 const patch=await sharp(`${generated}/${id}.png`).resize(meta.width,meta.height,{fit:'fill'}).extract(rect).toBuffer();
 await sharp(original).composite([{input:patch,left:rect.left,top:rect.top}]).png().toFile(`${root}/${name}-static.png`);
 await sharp(`${root}/${name}-static.png`).webp({quality:97}).toFile(`public/scene-art/lastmile-family-v1/${name}.webp`);
}
