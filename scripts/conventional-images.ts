import{readFile}from'node:fs/promises';import path from'node:path';import sharp from'sharp';
export async function loadConventionalImages(root:string):Promise<Map<string,number>>{
 const images=new Map<string,number>();let rows:Record<string,{width:number,reviewReceipt:string}>;
 try{rows=JSON.parse(await readFile(path.join(root,'src/media/conventional-enlargements.json'),'utf8'));}catch(e:any){if(e.code==='ENOENT')return images;throw e;}
 for(const[source,row]of Object.entries(rows)){
  if(!source.startsWith('public/')||source.includes('..')||!Number.isInteger(row.width)||row.width<1||row.width>8192||row.reviewReceipt.includes('..'))throw Error('Invalid conventional interpolation mapping');
  const review=JSON.parse(await readFile(path.join(root,row.reviewReceipt),'utf8'));
  if(review.decision!=='accepted_for_runtime'||review.processingMode!=='conventional_interpolation'||review.detailRecovery!==false)throw Error('Conventional source requires explicit accepted review without detail recovery claim');
  const file=path.join(root,source),metadata=await sharp(file).metadata();if(!metadata.width||row.width<=metadata.width)throw Error('Conventional target must exceed original width');images.set(file,row.width);
 }
 return images;
}
export function interpolateConventional(original:Buffer,width:number){return sharp(original).resize({width,kernel:'lanczos3'}).png().toBuffer();}
