import sharp from 'sharp';import fs from 'node:fs/promises';import path from 'node:path';
const root=process.cwd(),dir=path.join(root,'design/style-audit-2026-09-28');
const manifest=JSON.parse(await fs.readFile('src/scenes/worldManifest.json'));
const families={reference:['/home/michael/.cache/tmp/codex-clipboard-a54b2bbd-1ed8-4dca-a4f3-4b1e058bf345.png'],choices:['student','professional','alva','khor','arseniy','camera','socks','boat'].map(x=>`design/scene-01/assets/current/choices/${x}.webp`),scenes:['public/scene1-live/separated-routes/city-poster.webp',...Object.values(manifest.scenes).map(s=>'public/'+s.desktop.image)],carrier:['old','old4','near','crew','express'].flatMap(x=>['desktop','mobile'].map(d=>`public/scene1-live/${x}-${d}.webp`)),inspection:['old','old4','near','crew'].map(x=>`public/review/carrier-art-2026-09-27/closer-${x}.png`),compact:['socks-scatter','socks-dishes','socks-niche','socks-space','camera-dishes-broken','camera-dishes','camera-unload-three','camera-space','camera-niche','boat-axle','boat-dishes','boat-no-fit','boat-reload','boat-upright'].map(x=>`public/compact-art/outcomes/${x}.png`),inventory:['entrance','keeper','wms','alphabet-camera','alphabet-socks','alphabet-boat'].map(x=>`public/scene-art/outcomes/inventory-${x}-v8.webp`),crane:Object.values(JSON.parse(await fs.readFile('src/scenes/crane/outcomeFraming.json'))).map(x=>'public/scene-art/outcomes/'+x.file),lastmile:['helicopter','helicopter-remote','rover','robot','pipe-carrier','pipe-carrier-boat'].map(x=>`public/scene-art/outcomes/lastmile-${x}-v3.png`)};
await fs.copyFile(families.reference[0],path.join(dir,'reference.png'));families.reference=['design/style-audit-2026-09-28/reference.png'];
await fs.writeFile(path.join(dir,'art-inventory.json'),JSON.stringify(families,null,2));
for(const [name,files] of Object.entries(families)){
 const cols=name==='scenes'?2:3,w=500,h=330,composites=[];
 for(const [i,file] of files.entries()){
  const thumb=await sharp(path.resolve(root,file)).resize(w,h-35,{fit:'contain',background:'#eeede7'}).png().toBuffer();
  const label=Buffer.from(`<svg width="${w}" height="35"><rect width="100%" height="100%" fill="#ffffff"/><text x="10" y="23" font-family="sans-serif" font-size="13">${path.basename(file)}</text></svg>`);
  composites.push({input:thumb,left:i%cols*w,top:Math.floor(i/cols)*h},{input:label,left:i%cols*w,top:Math.floor(i/cols)*h+h-35});
 }
 await sharp({create:{width:cols*w,height:Math.ceil(files.length/cols)*h,channels:3,background:'#eeede7'}}).composite(composites).png().toFile(path.join(dir,`${name}-board.png`));
}
console.log(Object.fromEntries(Object.entries(families).map(([k,v])=>[k,v.length])));
