/** Run under flowers-global-assembly.lock. Produces an isolated preview, never publishes. */
import {build} from 'vite';
import {readFile,writeFile,mkdir,readdir,link,copyFile} from 'node:fs/promises';
import path from 'node:path';
import {optimizedImages} from '../optimized-images';
import {patchMedia} from './media_patch';
const [label,stageArg,...ids]=process.argv.slice(2);
if(!label||!stageArg||!ids.length||!/^[-a-zA-Z0-9]+$/.test(label))throw Error('label stageDir Fxxxx... required');
const root=process.cwd(),live=path.join(root,'.tmp-work/grisha-demo-2026-10-19-stage'),stage=path.resolve(stageArg),work=path.join(root,'.tmp-work/media-registry-'+label);
if(!stage.startsWith(root+'/.tmp-work/')||stage===live)throw Error('isolated stage required');
const aliases=JSON.parse(await readFile('src/media/flowers-masters.json','utf8'));
const selected=Object.entries(aliases).filter(([,row]:any)=>ids.includes(row.id)) as [string,any][];
if(selected.length!==new Set(ids).size)throw Error('Every requested ID must have one reviewed alias');
for(const[source,row]of selected){
 if(!source.startsWith('public/'))throw Error('Public sources only');
 const review=JSON.parse(await readFile(row.reviewReceipt,'utf8'));
 if(review.decision!=='accepted_for_runtime'||row.passes!==2)throw Error('Accepted two-pass review required');
}
const html=await readFile(path.join(live,'index.html'),'utf8'),match=html.match(/<script\b[^>]*src=["']([^"']+)["'][^>]*>/);
if(!match)throw Error('Published entry missing');
const oldEntry=match[1],oldJs=await readFile(path.join(live,oldEntry),'utf8');
await mkdir(work);
const entry=path.join(work,'entry.ts');
await writeFile(entry,'import fallback from "virtual:optimized-images";import responsive from "virtual:responsive-images";export {fallback,responsive};\n');
await build({configFile:false,root,base:'./',plugins:[optimizedImages()],logLevel:'warn',build:{outDir:path.join(work,'build'),copyPublicDir:false,lib:{entry,formats:['es'],fileName:()=> 'media-registry.mjs'},rollupOptions:{output:{assetFileNames:'assets/[name]-[hash][extname]'}}}});
const registry=await import(path.join(work,'build/media-registry.mjs'));
const replacements:Record<string,any>={};
for(const[source]of selected){const key=source.slice('public/'.length);if(!registry.fallback[key]||!registry.responsive[key])throw Error('Source absent from generated runtime registry: '+key);replacements[key]={fallback:registry.fallback[key],responsive:registry.responsive[key]};}
const patched=patchMedia(oldJs,replacements);
async function clone(from:string,to:string){await mkdir(to);for(const f of await readdir(from,{withFileTypes:true})){const a=path.join(from,f.name),b=path.join(to,f.name);if(f.isDirectory())await clone(a,b);else if(f.name==='index.html')await copyFile(a,b);else await link(a,b);}}
await clone(live,stage);
const urls=new Set<string>();
function collect(value:any){if(typeof value==='string'){for(const match of value.matchAll(/(?:\.\/)?assets\/[^\s,]+/g))urls.add(match[0].replace(/^\.\//,''));}else if(value&&typeof value==='object')Object.values(value).forEach(collect);}
collect(replacements);
for(const url of urls){const input=path.join(work,'build',url),output=path.join(stage,url);let existing:Buffer|undefined;try{existing=await readFile(output);}catch(e:any){if(e.code!=='ENOENT')throw e;}const data=await readFile(input);if(existing){if(!existing.equals(data))throw Error('Asset collision: '+url);}else await writeFile(output,data);}
const newEntry='assets/index-media-'+label+'.js';
try{await readFile(path.join(stage,newEntry));throw Error('Entry already exists');}catch(e:any){if(e.code!=='ENOENT')throw e;}
await writeFile(path.join(stage,newEntry),patched.code);
await writeFile(path.join(stage,'index.html'),html.replaceAll(oldEntry,'./'+newEntry));
const receipt={ids,stage:path.relative(root,stage),oldEntry,newEntry,newAssets:[...urls],replacements,patches:patched.patches,nonMediaBytesPreserved:patched.nonMediaBytesPreserved,nativeGenerationCalls:0,published:false,runtimeVerification:'pending'};
await writeFile(path.join(work,'overlay.json'),JSON.stringify(receipt,null,2)+'\n');
console.log(JSON.stringify({ids,stage:receipt.stage,newEntry,nonMediaBytesPreserved:true,receipt:path.relative(root,path.join(work,'overlay.json'))}));
