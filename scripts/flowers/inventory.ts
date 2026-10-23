import { readFile, writeFile, mkdir } from 'node:fs/promises';
import path from 'node:path';
import { parseSync } from 'rolldown/utils';
import sharp from 'sharp';
export type Asset={id:string;source:string;uses:string[];owner:string;processingStatus:string;freezeStatus:string;[key:string]:unknown};
function owner(source:string){if(source.includes('compact-art'))return'compact';if(/warehouse|inventory/.test(source))return'inventory';if(/barge|outcomes\/crane/.test(source))return'barge';if(/certificates|resolution/.test(source))return'ending';if(/lastmile/.test(source)&&!source.includes('choice-final-wide-v10'))return'lastmile';if(/carrier|scene1-live/.test(source))return'carrier';if(source.startsWith('design/')||source.includes('/opening/')||source.includes('choice-final-wide-v10'))return'intro';return'general';}
export function makeInventory({sources,excluded,previous}:{sources:{source:string;uses:string[]}[];excluded:string[];previous:Asset[]}){
 const old=new Map(previous.map(a=>[a.source,a]));let sequence=Math.max(0,...previous.map(a=>Number(a.id.slice(1))||0));const grouped=new Map<string,Set<string>>();
 for(const row of sources){if(excluded.includes(row.source))continue;const uses=grouped.get(row.source)??new Set<string>();for(const use of row.uses)uses.add(use);grouped.set(row.source,uses);}
 const assets:Asset[]=[...grouped].sort(([a],[b])=>a.localeCompare(b)).map(([source,uses])=>({...old.get(source),id:old.get(source)?.id??`F${String(++sequence).padStart(4,'0')}`,source,uses:[...uses].sort(),owner:owner(source),processingStatus:old.get(source)?.processingStatus??'not_started',freezeStatus:old.get(source)?.freezeStatus??'awaiting_owner_freeze'}));
 return{assets,excluded};
}
const legacy=['scene-art/crane-v2.png',...['petr-v7','remote-v4','rush-v4','wait-v4'].map(s=>`scene-art/outcomes/crane-${s}-desktop.png`),'scene-art/lastmile-fifth-scene-v9.png','scene-art/lastmile-family-v1/choice-final-tall-v10.webp'].map(s=>'public/'+s);
if(import.meta.main){const root=process.cwd(),D='docs/reviews/flowers-all-2026-10-20',output=D+'/manifest.json';await mkdir(D,{recursive:true});let oldManifest:any={assets:[]};try{oldManifest=JSON.parse(await readFile(output,'utf8'));}catch(e:any){if(e.code!=='ENOENT')throw e;}const sourceRegistry=process.argv[2]??oldManifest.sourceRegistry??'.tmp-work/grisha-demo-2026-10-20-facts-build/static-image-replacements.json';const replacements=JSON.parse(await readFile(sourceRegistry,'utf8'));const sources=Object.keys(replacements).map(source=>({source:'public/'+source,uses:['current production raster registry']}));
 const file='src/game/artwork.ts',ast=parseSync(file,await readFile(file,'utf8'));if(ast.errors.length)throw Error('source parse failed');
 for(const node of ast.program.body as any[])if(node.type==='ImportDeclaration'&&typeof node.source.value==='string'&&node.source.value.includes('/design/'))sources.push({source:path.relative(root,path.resolve(path.dirname(file),node.source.value)),uses:['preparation/cards/selected thumbnails; src/game/artwork.ts']});
 sources.push({source:'public/opening/parcel-heart-v2.webp',uses:['GameIntro parcel drawing']});
 const previous:Asset[]=oldManifest.assets;
 const audits=JSON.parse(await readFile(D+'/audits.json','utf8'));
 for(const[ownerName,receiptPath]of Object.entries(audits.ownerSourceOverrides??{})as[string,string][]){
  const frozen=JSON.parse(await readFile(receiptPath,'utf8'));
  if(frozen.decision!=='semantic_sources_frozen')throw Error('Owner source override lacks semantic freeze: '+receiptPath);
  const entries=(frozen.assets??frozen.sources) as {source:string}[];
  if(!Array.isArray(entries))throw Error('Owner source override has no asset/source list: '+receiptPath);
  if(entries.some(a=>owner(a.source)!==ownerName))throw Error('Owner source override crosses ownership: '+receiptPath);
  for(let i=sources.length-1;i>=0;i--)if(owner(sources[i].source)===ownerName)sources.splice(i,1);
  sources.push(...entries.map(a=>({source:a.source,uses:['owner-frozen active source; '+receiptPath]})));
 }
 const manifest=makeInventory({sources,excluded:[...legacy,...audits.excluded.map((a:any)=>a.source)],previous});
 const lastmile=JSON.parse(await readFile('docs/reviews/lastmile-2026-10-20-flowers/active-sources.json','utf8'));
 for(const a of manifest.assets){const info=await sharp(a.source).metadata();a.sourceDimensions={width:info.width,height:info.height};a.passes=2;a.exportLongestEdge=8192;a.outputRoot=`.tmp-work/flowers-all-2026-10-20/${a.id}`;a.runtimeFallback=replacements[a.source.replace(/^public\//,'')]??null;
 if(a.owner==='lastmile'){const peer=lastmile.rows.find((r:any)=>r.source===a.source);if(!peer)throw Error('Lastmile source missing in frozen lane: '+a.source);a.peerId=peer.id;a.peerReceipt='docs/reviews/lastmile-2026-10-20-flowers';a.freezeStatus='owner_frozen';a.uses=peer.uses.map((u:any)=>JSON.stringify(u));}
 if(a.owner==='ending'){a.freezeStatus='owner_frozen';a.peerReceipt='docs/reviews/ending-2026-10-20/active-upscale-sources.json';}
 if(a.source.includes('choice-final-wide-v10'))a.uses=['GameIntro cover/background via sceneChoiceImage(lastmile), NOT active Lastmile choice'];
 a.activityStatus=audits.confirmedOwners[a.owner]?'owner_confirmed':'candidate_pending_owner_audit';
 if(audits.confirmedOwners[a.owner]){a.freezeStatus='owner_frozen';a.freezeReceipt=audits.confirmedOwners[a.owner];}
 const confirmed=audits.confirmedSources?.find((c:any)=>c.source===a.source);if(confirmed){a.activityStatus='owner_confirmed';a.freezeStatus='owner_frozen';a.freezeReceipt=confirmed.receipt;}
 const hold=audits.heldSources?.find((h:any)=>h.source===a.source);
 if(hold){a.freezeStatus='hold_semantic_correction';a.holdReason=hold.reason;}
 a.presentInSourceRegistry=!!replacements[a.source.replace(/^public\//,'')];
 }
 const retiredSources=[...(oldManifest.retiredSources??[]),...previous.filter(a=>!manifest.assets.some(b=>a.source===b.source)&&!manifest.excluded.includes(a.source)).map(a=>({id:a.id,source:a.source,reason:'source version replaced in newer active build; prior processing is not attributed to replacement'}))];
 const result={schemaVersion:1,updatedAt:new Date().toISOString(),sourceRegistry,retiredSources,authority:'Two passes,8192 longest edge; active canonical originals only. Path deduplication; no file hashes/sizes.',status:'owner_audit_and_native_generation_in_progress',passes:2,exportLongestEdge:8192,...manifest,nonPhotoAssets:[{type:'SVG',source:'public/brand/quest-brand-lockup.svg',status:'preserve_vector_no_photo_upscale'},{type:'video',source:'public/scene1-live/separated-routes/city-motion-{mobile,tablet,desktop}.mp4',status:'separate_video_workflow'},{type:'raster UI derivatives',source:'public/brand/{favicon-32,icon-192,apple-touch-icon}.png',status:'preserve_vector_derived_UI_no_photo_reconstruction'}]};
 await writeFile(output,JSON.stringify(result,null,2)+'\n');
 await mkdir(D+'/packages',{recursive:true});
 for(const owner of new Set(manifest.assets.map(a=>a.owner)))await writeFile(`${D}/packages/${owner}.json`,JSON.stringify({canonicalManifest:'../manifest.json',owner,passes:2,exportLongestEdge:8192,assets:manifest.assets.filter(a=>a.owner===owner).map(a=>({id:a.id,source:a.source,uses:a.uses,sourceDimensions:a.sourceDimensions,outputRoot:a.outputRoot,activityStatus:a.activityStatus,freezeStatus:a.freezeStatus}))},null,2)+'\n');
 console.log(JSON.stringify({assets:manifest.assets.length,byOwner:Object.fromEntries([...new Set(manifest.assets.map(a=>a.owner))].map(o=>[o,manifest.assets.filter(a=>a.owner===o).length])),excluded:manifest.excluded.length},null,2));}
