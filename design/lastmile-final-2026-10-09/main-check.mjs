import {chromium} from '@playwright/test';
const b=await chromium.launch({args:['--disable-gpu']});
for(const [width,height] of [[393,852],[1440,900]]){
 const p=await b.newPage({viewport:{width,height}});
 await p.addInitScript(()=>{
 const scope='quest-lastmile-final';localStorage.setItem('energy-quest-save-v1',JSON.stringify({version:1,scope,state:{step:'outcome',profile:'professional',recipient:'alva',parcel:'boat',carrier:'crew'}}));
 localStorage.setItem(scope+':intro-seen','true');localStorage.setItem(scope+':remaining','true');
 localStorage.setItem(scope+':scenes',JSON.stringify({progress:{sceneIndex:3,phase:'choice',finished:false,answers:{compact:'auto',inventory:'wms',crane:'remote'}}}));
 });
 await p.goto('http://127.0.0.1:4173/');await p.locator('[data-world-scene="lastmile"]').waitFor();await p.locator('img').evaluateAll(es=>Promise.all(es.map(e=>e.decode().catch(()=>{}))));
 const brief=p.getByRole("button",{name:/^(Далее|К выбору)$/});for(let i=0;i<30&&await brief.isVisible();i++)await brief.click();
 await p.screenshot({path:`design/lastmile-final-2026-10-09/screens/${width}-main-choice.png`});
 const art=await p.locator('[data-world-scene="lastmile"] img').getAttribute('src');if(!art.includes('choice-final-'))throw Error(art);
 await p.locator('[data-scene-choice="rover"]').click();await p.locator('[data-choice-confirm]').click();
 const read=p.getByRole('button',{name:'Читать дальше',exact:true});for(let i=0;i<30&&await read.isVisible();i++)await read.click();
 await p.getByRole('button',{name:'К вручению подарка'}).click();await p.locator('[data-journey-ending]').waitFor();await p.getByRole('button',{name:'Узнать, какой вы логист'}).click();await p.locator('[data-logist-certificate]').waitFor();
 await p.screenshot({path:`design/lastmile-final-2026-10-09/screens/${width}-main-certificate.png`});
 await p.getByRole('button',{name:'Вернуться на главную'}).click();await p.getByRole('heading',{name:/Кем вы хотите быть|професси|роль/i}).waitFor({timeout:3000}).catch(()=>{});
 console.log({width,art,certificateFlow:'pass',reset:await p.locator('[data-journey-ending]').count()===0});await p.close();
}await b.close();
