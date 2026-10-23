import {chromium} from '@playwright/test';
import {writeFile,readFile} from 'node:fs/promises';
const source=await readFile('docs/scenario.md','utf8');
const options=Object.entries({rush:'0023E31A',wait:'553650B7',petr:'0C6EC2FC',remote:'5EDD1701'}).map(([id,key])=>{const block=source.split('<!-- scenario-block id="'+key+'"')[1].split('<!-- /scenario-block -->')[0];return {id,label:block.split('\n').filter(l=>l.startsWith('> ')).map(l=>l.slice(2)).join('\n')};});
const browser=await chromium.launch({args:['--disable-gpu']});
const records=[];
for(const [width,height] of [[320,568],[393,650],[393,852],[820,1180],[1440,900]]){
 const page=await browser.newPage({viewport:{width,height},reducedMotion:'reduce'});
 await page.addInitScript(()=>{const scope='quest-barge-final';localStorage.setItem('energy-quest-save-v1',JSON.stringify({version:1,scope,state:{step:'outcome',profile:'professional',recipient:'alva',parcel:'boat',carrier:'crew'}}));localStorage.setItem(scope+':intro-seen','true');localStorage.setItem(scope+':remaining','true');localStorage.setItem(scope+':scenes',JSON.stringify({progress:{sceneIndex:2,phase:'choice',finished:false,answers:{compact:'auto',inventory:'wms'}}}));});
 await page.goto('http://127.0.0.1:4173/'); await page.locator('[data-world-scene="crane"]').waitFor();
 const next=page.getByRole('button',{name:/^(Далее|К выбору)$/});
 for(let i=0;i<30&&await next.isVisible();i++)await next.click();
 if(height<=700){
  await page.mouse.wheel(0,400);
  await page.waitForFunction(()=>scrollY>0);
  await page.evaluate(()=>scrollTo(0,0));
 }
 for(const option of options){
  const card=page.locator(`[data-scene-choice="${option.id}"]`);
  const bounds=await card.boundingBox();
  if(!bounds)throw Error(`Missing card ${width}/${option.id}`);
  if(height>700&&bounds.y+bounds.height>height+1)throw Error(`Hidden card ${width}/${option.id}`);
  await card.scrollIntoViewIfNeeded();
  const visibleBounds=await card.boundingBox();
  if(!visibleBounds||visibleBounds.y+visibleBounds.height>height+1)throw Error(`Unreachable card ${width}/${option.id}`);
  const marker=page.locator(`button[data-hotspot="${option.id}"]`);
  const hit=await marker.boundingBox();if(!hit||hit.width<44||hit.height<44)throw Error('Small marker');
  await marker.click();
  await page.locator('[data-inspecting="true"]').waitFor();
  const routeShown=await page.locator('[data-crane-annotations] svg > path').first().evaluate(e=>getComputedStyle(e).display!=='none');
  if(routeShown!==(option.id==='rush'))throw Error(`Misleading walking route for ${option.id}`);
  const body=await page.locator('body').innerText();
  const label=option.label.replace(/^№\d+\.\s*/,'');
  if(!body.includes(label))throw Error(`Missing canonical text ${option.id}: ${label}`);
  if(width===393)await page.screenshot({path:`design/barge-choice-2026-10-10/screens/inspection-${option.id}-393.png`});
  await page.getByRole('button',{name:'К вариантам',exact:true}).click();
  records.push({width,height,id:option.id,cardVisible:true,markerHit:hit,canonicalText:true});
 }
 await page.locator('[data-scene-choice="remote"]').click();
 await page.getByRole('button',{name:'Подтвердить выбор',exact:true}).click();
 await page.locator('[data-result-reader]').waitFor();
 records.push({width,confirmed:'remote',outcomeShown:true});
 await page.close();
}
await browser.close();await writeFile('design/barge-choice-2026-10-10/interaction-receipt.json',JSON.stringify(records,null,2));console.log(`${records.length} runtime checks passed`);
