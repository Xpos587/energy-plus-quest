import { expect, test } from '@playwright/test';

for (const [width, height] of [[320,568],[390,844],[844,390],[1440,900]]) {
  for (const recipient of ['alva','khor','arseniy']) for (const parcel of ['boat','camera','socks']) {
    test(`${width}x${height} ${recipient}/${parcel}: four deliveries fit and return`, async ({ page }) => {
      await page.setViewportSize({width,height});
      await page.goto(`/scenes.html?scene=lastmile&recipient=${recipient}&parcel=${parcel}`);
      await page.waitForTimeout(200);
      const briefing=page.getByRole('button',{name:/^(Далее|К выбору)$/});
      for(let n=0;n<12&&await briefing.isVisible();n++){await briefing.click();await page.waitForTimeout(100);}
      for (const option of ['helicopter','rover','robot','pipe-carrier']) {
        await expect(page.locator('[data-hotspot]')).toHaveCount(4);
        await page.locator(`[data-choice-id="${option}"]:not([data-callout-target])`).click();
        for(let n=0;n<12;n++) {
          const image=page.locator('[data-scene-consequence] img');
          await image.evaluate(async(i:HTMLImageElement)=>{await i.decode();await document.fonts.ready;});
          await page.waitForTimeout(200);
          for(const button of await page.locator('[data-result] button').all()) {
            const box=await button.boundingBox();
            expect(box,`${option} ${await button.innerText()}`).not.toBeNull();
            expect(box!.y+box!.height,`${option}: ${await button.innerText()} below viewport`).toBeLessThanOrEqual(height+1);
            expect(box!.x+box!.width).toBeLessThanOrEqual(width+1);
            expect(box!.y).toBeGreaterThanOrEqual(0);
          }
          expect(await page.locator('body').innerText()).not.toMatch(/\bХор\b|\bkhor\b/);
          const read=page.getByRole('button',{name:'Читать дальше',exact:true});
          if(!await read.isVisible())break;
          await read.click();
        }
        await expect(page.getByRole('button',{name:'К вручению подарка',exact:true})).toBeVisible();
        await page.getByRole('button',{name:'Изменить выбор',exact:true}).click();
      }
    });
  }
}
