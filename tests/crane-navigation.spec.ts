import { expect, test } from '@playwright/test';
import { mkdir, writeFile } from 'node:fs/promises';
const sizes=[{width:320,height:568},{width:390,height:844},{width:844,height:390},{width:1440,height:900}];
for(const viewport of sizes) for(const parcel of ['boat','camera','socks']) test(`${viewport.width} ${parcel}: controls, images, lastmile`,async({page})=>{
 await page.setViewportSize(viewport);
 const receipt:unknown[]=[];
 for(const id of ['remote','rush','wait','petr']){
 await page.goto(`/scenes.html?scene=crane&parcel=${parcel}&recipient=alva`);
 const intro=page.getByRole('button',{name:/^(Далее|К выбору|К сцене)$/});
 for(let n=0;n<15 && await intro.isVisible();n++) await intro.click();
 await expect(page.locator(`[data-hotspot="${id}"]`)).toBeInViewport({ratio:1});
 await page.locator(`[data-hotspot="${id}"]`).click();
 await page.locator('[data-choice-confirm]').click();
 await expect(page.locator('[data-scene-consequence]')).toBeVisible();
 await page.waitForTimeout(700);
 const images=await page.locator('img:visible').evaluateAll(async imgs=>Promise.all(imgs.map(async i=>{const x=i as HTMLImageElement;await x.decode();return {src:x.currentSrc,source:[x.naturalWidth,x.naturalHeight],display:[x.clientWidth,x.clientHeight]};})));
 receipt.push({id,images});
 await expect(page.getByRole('button',{name:'Изменить выбор',exact:true})).toBeInViewport({ratio:1});
 const more=page.getByRole('button',{name:'Читать дальше',exact:true});
 for(let n=0;n<15 && await more.isVisible();n++){await expect(more).toBeInViewport({ratio:1});await more.click();}
 const proceed=page.getByRole('button',{name:'Продолжить',exact:true});
 await expect(proceed).toBeInViewport({ratio:1});
 expect(await page.evaluate(()=>({x:document.documentElement.scrollWidth<=innerWidth,y:document.documentElement.scrollHeight<=innerHeight}))).toEqual({x:true,y:true});
 await proceed.click();
 await expect(page.locator('[data-scene="lastmile"]')).toBeVisible();
 }
 await mkdir('docs/reviews/barge-2026-10-17/metrics',{recursive:true});
 await writeFile(`docs/reviews/barge-2026-10-17/metrics/${viewport.width}-${parcel}.json`,JSON.stringify(receipt,null,2));
});
