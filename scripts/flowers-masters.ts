import { readFile } from 'node:fs/promises';
import path from 'node:path';
import sharp from 'sharp';
export type FlowersAliases=Map<string,string>;
export async function loadFlowersMasters(root:string):Promise<FlowersAliases>{
 const aliases:FlowersAliases=new Map();let entries:Record<string,{master:string;passes:number;reviewReceipt:string}>;
 try{entries=JSON.parse(await readFile(path.join(root,'src/media/flowers-masters.json'),'utf8'));}catch(error:any){if(error.code==='ENOENT')return aliases;throw error;}
 for(const[source,row]of Object.entries(entries)){
  if(row.passes!==2||!row.master.startsWith('public/flowers-2pass-')||row.master.includes('..')||source.includes('..'))throw Error('Invalid Flowers source/master mapping: '+source);
  const review=JSON.parse(await readFile(path.resolve(root,row.reviewReceipt),'utf8'));
  if(review.decision!=='accepted_for_runtime'||review.passes!==2)throw Error('Flowers master lacks explicit accepted runtime review: '+source);
  const original=path.resolve(root,source),master=path.resolve(root,row.master);
  const[a,b]=await Promise.all([sharp(original).metadata(),sharp(master).metadata()]);
  if(!a.width||!a.height||!b.width||!b.height||Math.abs(b.width/b.height*a.height-a.width)>1)throw Error('Flowers master changes canonical artwork aspect ratio: '+source);
  if(a.hasAlpha&&!b.hasAlpha)throw Error('Flowers master drops original alpha: '+source);
  aliases.set(original,master);
 }
 return aliases;
}
