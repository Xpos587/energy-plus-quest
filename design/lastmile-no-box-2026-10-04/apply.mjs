import sharp from 'sharp';
const dir='design/lastmile-no-box-2026-10-04';const gen='/home/michael/.config/codex/generated_images/01a0e88c-a0ab-7560-a60b-d425f4850713';
const wide=await sharp(`${gen}/exec-27f21cae-840c-4c22-b70f-01a98786a58f.png`).resize(260,180).extract({left:73,top:42,width:92,height:79}).toBuffer();
const tall=await sharp(`${gen}/exec-5c48262e-95c6-4922-8d75-1a1d78697be1.png`).resize(948,1659).extract({left:9,top:707,width:74,height:63}).toBuffer();
for(const [n,patch,left,top] of [['choice-neutral-wide-v1',wide,263,382],['choice-neutral-tall-v2',tall,9,707]]){
 await sharp(`${dir}/before/${n}.webp`).composite([{input:patch,left,top}]).png().toFile(`${dir}/${n}-no-box.png`);
 await sharp(`${dir}/${n}-no-box.png`).webp({quality:97}).toFile(`public/scene-art/lastmile-family-v1/${n}.webp`);
}
