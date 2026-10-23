/** Explicit conventional interpolation, without native reconstruction claims. Preview only. */
import {readFile,writeFile,mkdir,readdir,link,copyFile} from 'node:fs/promises';
import path from 'node:path';import sharp from 'sharp';import{patchMedia}from'./media_patch';
const[label,source,widthArg,stageArg]=process.argv.slice(2),width=Number(widthArg),root=process.cwd();
if(!/^[-a-zA-Z0-9]+$/.test(label??'')||!source?.startsWith('public/')||source.includes('..')||!Number.isInteger(width)||width<1||width>8192||!stageArg)throw Error('label public/source width stage required');
const live=path.join(root,'.tmp-work/grisha-demo-2026-10-19-stage'),stage=path.resolve(stageArg);
if(!stage.startsWith(root+'/.tmp-work/')||stage===live)throw Error('Isolated stage required');
const metadata=await sharp(source).metadata();if(!metadata.width||!metadata.height||width<=metadata.width)throw Error('Measured enlargement required');
const html=await readFile(path.join(live,'index.html'),'utf8'),entry=html.match(/<script\b[^>]*src=["']([^"']+)["'][^>]*>/)?.[1];if(!entry)throw Error('Entry missing');
const oldJs=await readFile(path.join(live,entry),'utf8'),key=source.slice(7);
// Refuse an absent/ambiguous published source before encoding any derivatives.
patchMedia(oldJs,{[key]:{fallback:'pending',responsive:{}}});
async function clone(from:string,to:string){await mkdir(to);for(const f of await readdir(from,{withFileTypes:true})){const a=path.join(from,f.name),b=path.join(to,f.name);if(f.isDirectory())await clone(a,b);else if(f.name==='index.html')await copyFile(a,b);else await link(a,b);}}
await clone(live,stage);sharp.concurrency(1);
const variants:{width:number,avif:string,webp:string}[]=[];
for(const size of[...new Set([1280,1600,width].filter(n=>n<=width))]){
 const prefix=`assets/conventional-${label}-${size}`,avif=prefix+'.avif',webp=prefix+'.webp';
 for(const url of[avif,webp])try{await readFile(path.join(stage,url));throw Error('Derivative exists');}catch(e:any){if(e.code!=='ENOENT')throw e;}
 const pipeline=()=>sharp(source).resize({width:size,kernel:'lanczos3'});
 await pipeline().avif({quality:60,effort:4}).toFile(path.join(stage,avif));
 await pipeline().webp({quality:88,alphaQuality:100,effort:4}).toFile(path.join(stage,webp));
 variants.push({width:size,avif,webp});
}
const full=variants.at(-1)!,dimensions=await sharp(path.join(stage,full.webp)).metadata();
const responsive={avif:full.avif,avifSrcSet:variants.map(v=>`${v.avif} ${v.width}w`).join(', '),webpSrcSet:variants.map(v=>`${v.webp} ${v.width}w`).join(', '),width:dimensions.width,height:dimensions.height};
const patched=patchMedia(oldJs,{[key]:{fallback:full.webp,responsive}}),newEntry=`assets/index-conventional-${label}.js`;
try{await readFile(path.join(stage,newEntry));throw Error('Entry exists');}catch(e:any){if(e.code!=='ENOENT')throw e;}
await writeFile(path.join(stage,newEntry),patched.code);await writeFile(path.join(stage,'index.html'),html.replaceAll(entry,'./'+newEntry));
const receipt={label,source,sourceDimensions:[metadata.width,metadata.height],runtimeDimensions:[dimensions.width,dimensions.height],processingMode:'conventional_interpolation',method:'Lanczos3; AVIF60/WebP88 runtime derivatives; originals preserved',detailRecovery:false,nativeGenerationCalls:0,stage:path.relative(root,stage),oldEntry:entry,newEntry,newAssets:variants.flatMap(v=>[v.avif,v.webp]),patches:patched.patches,nonMediaBytesPreserved:true,published:false,runtimeVerified:false};
const directory=path.join(root,'docs/reviews/conventional-media-2026-10-22',label);await mkdir(directory,{recursive:true});await writeFile(path.join(directory,'overlay.json'),JSON.stringify(receipt,null,2)+'\n');console.log(JSON.stringify({label,stage:receipt.stage,runtimeDimensions:receipt.runtimeDimensions,detailRecovery:false}));
