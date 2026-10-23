import{test,expect}from'bun:test';import{mkdtemp,mkdir,writeFile,readFile,rm}from'node:fs/promises';import{tmpdir}from'node:os';import path from'node:path';import sharp from'sharp';import{loadConventionalImages,interpolateConventional}from'./conventional-images';
test('reviewed conventional width preserves source and alpha; never implies Flowers',async()=>{
 const root=await mkdtemp(path.join(tmpdir(),'conventional-'));try{
  await mkdir(path.join(root,'src/media'),{recursive:true});await mkdir(path.join(root,'public'));
  const source=path.join(root,'public/source.png');await sharp({create:{width:12,height:8,channels:4,background:{r:20,g:40,b:60,alpha:.5}}}).png().toFile(source);const original=await readFile(source);
  await writeFile(path.join(root,'review.json'),JSON.stringify({decision:'accepted_for_runtime',processingMode:'conventional_interpolation',detailRecovery:false}));
  await writeFile(path.join(root,'src/media/conventional-enlargements.json'),JSON.stringify({'public/source.png':{width:24,reviewReceipt:'review.json'}}));
  const rows=await loadConventionalImages(root);expect(rows.get(source)).toBe(24);const output=await interpolateConventional(original,24);const metadata=await sharp(output).metadata();expect([metadata.width,metadata.height,metadata.hasAlpha]).toEqual([24,16,true]);expect((await readFile(source)).equals(original)).toBe(true);
  await writeFile(path.join(root,'review.json'),JSON.stringify({decision:'rejected'}));await expect(loadConventionalImages(root)).rejects.toThrow();
 }finally{await rm(root,{recursive:true,force:true});}
});
