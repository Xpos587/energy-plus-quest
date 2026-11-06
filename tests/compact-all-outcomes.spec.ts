import { test, expect } from '@playwright/test';
for (const parcel of ['socks', 'camera', 'boat'] as const) {
 for (const id of ['place-1','place-2','place-3','place-4','auto']) {
  test(`${parcel} ${id}: inspect, revise, read and continue`, async ({page},info) => {
   await page.goto(`/scenes.html?scene=compact&parcel=${parcel}&recipient=alva`);
   const intro = page.getByRole('button',{name:/^(Далее|К выбору)$/});
   for(let n=0;n<20&&await intro.isVisible();n++) await intro.click();
   const choice=page.locator(`[data-hotspot="${id}"]`);
   await choice.click();await page.locator('[data-choice-confirm]').click();
   await expect(page.locator('[data-result-reader]')).toBeVisible();
   // Result keeps only the chosen place marked, and it no longer accepts input.
   const placed=id==='auto'?(parcel==='boat'?'place-4':'place-3'):id;
   // Boat in place 3 does not fit: its result is a separate picture without a marker.
   const marker=page.locator(`[data-hotspot="${placed}"]`);
   if(await marker.count()) await expect(marker).toBeDisabled();
   for (const overlay of await page.locator(`[data-hotspot]:not([data-hotspot="${placed}"])`).all())
    await expect(overlay).toBeHidden();
   await page.screenshot({path:`.tmp-work/compact-complete/${info.project.name}-${parcel}-${id}.png`});
   await page.getByRole('button',{name:'Изменить выбор',exact:true}).click();
   await expect(page.locator('[data-result-reader]')).toHaveCount(0);
   for (const overlay of await page.locator('[data-loading-zone], [data-hotspot]').all())
    await expect(overlay).toBeVisible();
   await choice.click();await page.locator('[data-choice-confirm]').click();
   await expect(page.locator('[data-result-reader]')).toBeVisible();
   const pages:string[]=[];
   for(let n=0;n<30;n++) {
    pages.push(await page.getByTestId('result-copy').innerText());
    const more=page.getByRole('button',{name:'Читать дальше',exact:true});
    if(!await more.isVisible()) break;
    await expect(more).toBeInViewport({ratio:1});
    await more.click();
   }
   const normalize=(text:string)=>text.replace(/\s+/g,' ').trim();
   expect(normalize(pages.join(' ')).length).toBeGreaterThan(40);
   const proceed=page.getByRole('button',{name:'Продолжить',exact:true});
   await expect(proceed).toBeInViewport({ratio:1});
   await proceed.click();
   await expect(page.locator('[data-scene="inventory"]')).toBeVisible();
  });
 }
}
