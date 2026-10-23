import { test, expect } from '@playwright/test';
const root = 'docs/reviews/barge-2026-10-17/before';
for (const viewport of [{width:320,height:568},{width:390,height:844},{width:844,height:390},{width:1440,height:900}]) {
 for (const parcel of ['boat','camera','socks']) {
 test(`${viewport.width} ${parcel} all branches`, async ({page}) => {
 await page.setViewportSize(viewport);
 await page.goto(`http://127.0.0.1:4320/scenes.html?scene=crane&parcel=${parcel}&recipient=alva`);
 const settle = async () => {await page.locator('img').evaluateAll(async images=>Promise.all(images.map(i=>(i as HTMLImageElement).decode().catch(()=>{})))); await page.waitForTimeout(800);};
 await settle();
 await page.screenshot({path:`${root}/${viewport.width}-${parcel}-intro.png`});
 const intro=page.getByRole('button',{name:/^(Далее|К выбору|К сцене)$/});
 for(let n=0;n<15 && await intro.isVisible();n++) await intro.click();
 await settle();
 await page.screenshot({path:`${root}/${viewport.width}-${parcel}-choice.png`});
 for(const id of ['remote','rush','wait','petr']) {
 await page.locator(`[data-scene-choice="${id}"]`).click();
 await settle();
 await expect(page.locator('[data-scene-consequence]')).toBeVisible();
 await page.screenshot({path:`${root}/${viewport.width}-${parcel}-${id}.png`});
 const more=page.getByRole('button',{name:'Читать дальше',exact:true});
 for(let n=0;n<10 && await more.isVisible();n++){await more.click();await settle();await page.screenshot({path:`${root}/${viewport.width}-${parcel}-${id}-part${n+2}.png`});}
 const revise=page.getByRole('button',{name:'Изменить выбор',exact:true});
 await expect(revise).toBeVisible(); await revise.click(); await settle();
 }
 });
 }
}
