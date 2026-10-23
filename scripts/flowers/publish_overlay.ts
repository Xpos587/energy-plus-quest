/** Publish reviewed media to local4344 only; preserve subsequent unrelated media/CSS. */
import{readFile,writeFile,copyFile,rename}from'node:fs/promises';import path from'node:path';import{patchMedia}from'./media_patch';
const[receiptArg,reviewArg,label]=process.argv.slice(2),root=process.cwd(),live=path.join(root,'.tmp-work/grisha-demo-2026-10-19-stage');
if(!receiptArg?.startsWith('docs/reviews/')||!reviewArg?.startsWith('docs/reviews/')||receiptArg.includes('..')||reviewArg.includes('..')||!/^[-a-zA-Z0-9]+$/.test(label??''))throw Error('review receipt, accepted review, unique label required');
const receipt=JSON.parse(await readFile(receiptArg,'utf8')),review=JSON.parse(await readFile(reviewArg,'utf8'));
if(review.decision!=='accepted_for_runtime'||receipt.published)throw Error('Fresh accepted overlay required');
const stage=path.resolve(receipt.stage);if(!stage.startsWith(root+'/.tmp-work/')||stage===live)throw Error('Isolated preview stage required');
const html=await readFile(path.join(live,'index.html'),'utf8'),entry=html.match(/<script\b[^>]*src=["']([^"']+)["'][^>]*>/)?.[1];if(!entry)throw Error('Published entry missing');
const code=await readFile(path.join(live,entry),'utf8'),replacements:Record<string,any>={};
for(const p of receipt.patches){const row=replacements[p.source]??={};const value=JSON.parse(p.after);if(typeof value==='string')row.fallback=value;else row.responsive=value;}
const patched=patchMedia(code,replacements);
for(const p of patched.patches){const old=receipt.patches.find((o:any)=>o.source===p.source&&typeof JSON.parse(o.after)===typeof JSON.parse(p.after));if(!old||old.before!==p.before)throw Error('Target media changed after preview: '+p.source);}
const newEntry=receipt.newEntry;if(!/^assets\/[-a-zA-Z0-9]+\.js$/.test(newEntry))throw Error('Versioned entry required');
try{await readFile(path.join(live,newEntry));throw Error('Entry already exists');}catch(e:any){if(e.code!=='ENOENT')throw e;}
const backup=path.join(root,'.tmp-work',`4344-before-${label}-index.html`);try{await readFile(backup);throw Error('Backup already exists');}catch(e:any){if(e.code!=='ENOENT')throw e;}
for(const url of receipt.newAssets){if(!/^assets\/[-a-zA-Z0-9_.]+$/.test(url))throw Error('Invalid asset URL');const data=await readFile(path.join(stage,url));let existing:Buffer|undefined;try{existing=await readFile(path.join(live,url));}catch(e:any){if(e.code!=='ENOENT')throw e;}if(existing){if(!existing.equals(data))throw Error('Asset collision');}else await writeFile(path.join(live,url),data);}
await copyFile(path.join(live,'index.html'),backup);await writeFile(path.join(live,newEntry),patched.code);const next=path.join(live,`index-${label}.next.html`);await writeFile(next,html.replaceAll(entry,'./'+newEntry));await rename(next,path.join(live,'index.html'));
Object.assign(receipt,{published:true,publicationTarget:'http://127.0.0.1:4344/',indexBackup:path.relative(root,backup),rebasedFromEntry:entry,acceptedReview:reviewArg,publicationPatches:patched.patches,nonMediaBytesPreserved:true});await writeFile(receiptArg,JSON.stringify(receipt,null,2)+'\n');console.log('Published local media overlay',label);
