import {chromium} from '@playwright/test';
import sharp from 'sharp';
import {mkdir,writeFile} from 'node:fs/promises';
const root='design/media-audit-2026-10-05/compact-framing';
const viewports=[[320,568],[393,852],[820,1180],[1440,900],[844,390]];
const cases=[];
const add=(scene,choice,parcel='boat',recipient='alva')=>cases.push({scene,choice,parcel,recipient});
for(const parcel of ['camera','socks','boat'])for(const choice of ['place-1','place-2','place-3','place-4'])add('compact',choice,parcel);
for(const choice of ['entrance','alphabet','keeper','wms'])add('inventory',choice);
for(const parcel of ['camera','socks','boat'])for(const choice of ['rush','wait','petr','remote'])add('crane',choice,parcel);
for(const parcel of ['camera','boat'])for(const choice of ['rover','robot','pipe-carrier','helicopter'])add('lastmile',choice,parcel);
add('lastmile','helicopter','boat','arseniy');
for(const choice of ['old','old4','near','crew'])add('carrier',choice);
cases.splice(0,cases.length,...cases.filter(c=>c.scene==='compact'));
await mkdir(`${root}/results`,{recursive:true});
const browser=await chromium.launch({args:['--disable-gpu']});
const records=[];
async function run(viewport){
const [width,height]=viewport;
for(const c of cases){
 const id=`${width}x${height}-${c.scene}-${c.parcel}-${c.recipient}-${c.choice}`;
 const record={id,viewport:{width,height},...c,captures:[]};records.push(record);
 const p=await browser.newPage({viewport:{width,height},reducedMotion:'reduce'});p.setDefaultTimeout(12000);
 try{
 if(c.scene==='carrier'){
 await p.addInitScript(id=>localStorage.setItem('energy-quest-save-v1',JSON.stringify({version:1,scope:'quest-media-audit',state:{step:'outcome',profile:'professional',recipient:'alva',parcel:'boat',carrier:id}})),c.choice);
 await p.goto('http://127.0.0.1:4173/');
 }else{
 await p.goto(`http://127.0.0.1:4173/scenes.html?scene=${c.scene}&parcel=${c.parcel}&recipient=${c.recipient}`);
 const next=p.getByRole('button',{name:/^(Далее|К выбору)$/});
 for(let i=0;i<40&&await next.isVisible();i++)await next.click();
 await p.locator(`[data-scene-choice="${c.choice}"]`).click();await p.locator('[data-choice-confirm]').click();
 }
 await p.locator('[data-result-reader]').waitFor();
 let previous='';
 for(let page=0;page<45;page++){
 await p.locator('img').evaluateAll(es=>Promise.all(es.map(e=>e.decode().catch(()=>{}))));
 const state=await p.evaluate(()=>{
 const box=e=>{if(!e)return null;const r=e.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height}};
 const art=document.querySelector('[data-result-art],[data-outcome-scene],[data-world-scene="compact"]');
 return {text:document.querySelector('[data-result-reader]')?.textContent,beat:art?.getAttribute('data-outcome-beat'),art:box(art),panel:box(document.querySelector('[data-sheet-panel]')),images:[...(art?.querySelectorAll('img,image')??[])].map(e=>({src:e.currentSrc||e.getAttribute('href')||e.getAttribute('src'),box:box(e),fit:getComputedStyle(e).objectFit,position:getComputedStyle(e).objectPosition,naturalWidth:e.naturalWidth,naturalHeight:e.naturalHeight})),overflow:document.documentElement.scrollWidth>innerWidth};
 });
 const more=p.getByRole('button',{name:'Читать дальше',exact:true});const last=!(await more.isVisible());
 const signature=JSON.stringify(state.images.map(i=>i.src))+state.beat;
 if(page===0||last||signature!==previous){const file=`${root}/results/${id}-page${page}.png`;await p.screenshot({path:file});record.captures.push({page,last,...state,file});}
 previous=signature;
 if(last){record.pages=page+1;break;}await more.click();
 if(page===44)throw new Error('Reader exceeded 45 pages');
 }
 console.log('OK',id,record.captures.length);
 }catch(error){record.error=String(error);console.log('FAIL',id,record.error);}finally{await p.close();}
}
}
// Two concurrent viewports keep image decoding responsive while bounding memory.
for(let i=0;i<viewports.length;i+=2)await Promise.all(viewports.slice(i,i+2).map(run));
await browser.close();
await writeFile(`${root}/results.json`,JSON.stringify(records,null,2));
const sheets=[];
for(const [w,h] of viewports)for(const scene of ['carrier','compact','inventory','crane','lastmile']){
 const captures=records.filter(r=>r.viewport.width===w&&r.scene===scene).flatMap(r=>r.captures.map(c=>({...c,label:`${r.parcel}/${r.recipient} ${r.choice} p${c.page}${c.last?' last':''}`})));
 if(!captures.length)continue;
 const cellW=300,cellH=250,cols=4,rows=Math.ceil(captures.length/cols);const layers=[];
 for(let i=0;i<captures.length;i++){
 const c=captures[i];const x=(i%cols)*cellW,y=Math.floor(i/cols)*cellH;
 const thumb=await sharp(c.file).resize(296,222,{fit:'contain',background:'#dde3e9'}).png().toBuffer();layers.push({input:thumb,left:x+2,top:y+26});
 const label=c.label.replaceAll('&','&amp;').replaceAll('<','&lt;');
 layers.push({input:Buffer.from(`<svg width="300" height="26"><rect width="300" height="26" fill="white"/><text x="4" y="18" font-size="12" font-family="sans-serif">${label}</text></svg>`),left:x,top:y});
 }
 const file=`${root}/results-${w}x${h}-${scene}.jpg`;await sharp({create:{width:cols*cellW,height:rows*cellH,channels:3,background:'white'}}).composite(layers).jpeg({quality:85}).toFile(file);sheets.push(file);
}
await writeFile(`${root}/results-summary.json`,JSON.stringify({cases:records.length,failed:records.filter(r=>r.error),captures:records.reduce((n,r)=>n+r.captures.length,0),sheets},null,2));
console.log('DONE',records.length,'cases',records.filter(r=>r.error).length,'failed');
