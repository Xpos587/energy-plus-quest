import {test, expect} from '@playwright/test';
import {writeFileSync} from 'node:fs';
for (const scene of ['compact','inventory','crane','lastmile']) {
 test(`${scene} fixed choices and result`, async({page}, info)=>{
  await page.goto(`/scenes.html?scene=${scene}&parcel=boat&recipient=alva`);
  const next=page.getByRole('button',{name:/^(Далее|К выбору|К сцене)$/});
  for(let i=0;i<20&&await next.isVisible();i++) await next.click();
  const choices=page.locator('[data-scene-choice]');
  for(const button of await choices.all()) await expect(button).toBeInViewport({ratio:0.99});
  await page.locator('img').evaluateAll(async imgs=>Promise.all(imgs.map(img=>(img as HTMLImageElement).decode().catch(()=>{}))));
  await page.screenshot({path:`.tmp-work/fixed-ux/${info.project.name}-${scene}-choices.png`});
  const artBounds = () => page.locator('[data-world-scene], [data-fixed-choice], [data-fixed-result], [data-outcome-scene]').first().boundingBox();
  const choiceBounds = await artBounds();
  if (scene === 'compact') {
    for (const [index, button] of (await choices.all()).entries()) {
      const label = await button.innerText();
      expect(label.match(/\d+/g) ?? []).toHaveLength(index < 4 ? 1 : 0);
    }
  }
  await choices.first().click();
  await expect(page.locator('[data-choice-inspection] h3')).not.toContainText('Место №');
  await expect(page.locator('[data-choice-confirm]')).toBeInViewport({ratio:0.99});
  await page.locator('[data-choice-confirm]').click();
  const frame=page.locator('[data-layout="result"]');
  await expect(frame).toBeVisible();
  await expect(frame).not.toContainText('Последствия выбора');
  await expect(frame).not.toContainText('Результат ·');
  writeFileSync(`.tmp-work/fixed-ux/${info.project.name}-${scene}-dimensions.json`, JSON.stringify({viewport:info.project.name,scene,choice:choiceBounds,result:await artBounds()},null,2));
  for(let n=0;n<30;n++) {
    await expect(page.getByRole('button',{name:'Изменить выбор',exact:true})).toBeInViewport({ratio:.99});
    const reading=page.locator('[data-result-reading]');
    await expect.poll(()=>reading.evaluate(e=>e.scrollWidth<=e.clientWidth+1&&e.scrollHeight<=e.clientHeight+1)).toBe(true);
    const forward=page.getByRole('button',{name:/^(Читать дальше|Продолжить|Завершить)$/});
    await expect(forward).toBeInViewport({ratio:0.99});
    await expect.poll(()=>frame.evaluate(e=>e.scrollHeight<=e.clientHeight+1)).toBe(true);
    if(n===0) await page.locator('img').evaluateAll(async imgs=>Promise.all(imgs.map(img=>(img as HTMLImageElement).decode())));
    if(n===0) await page.screenshot({path:`.tmp-work/fixed-ux/${info.project.name}-${scene}-result.png`});
    if(await forward.getAttribute('aria-label')!=='Читать дальше') break;
    await forward.click();
  }
 });
}

test('carrier map keeps selection and readable result', async ({page}, info) => {
  await page.goto('/');
  for (const id of ['professional','alva','boat']) await page.locator(`[data-choice="${id}"]`).click();
  const intro=page.getByRole('button',{name:/^(Далее|К выбору|К сцене)$/});
  for(let i=0;i<20&&await intro.isVisible();i++) await intro.click();
  await page.getByRole('button',{name:'Синяя фура',exact:true}).click();
  await expect(page.locator('[data-choice-confirm]')).toBeInViewport({ratio:.99});
  await page.locator('[data-choice-confirm]').click();
  for(let i=0;i<30;i++) {
    const next=page.getByRole('button',{name:/^(Читать дальше|Дальше: погрузка|Продолжить)$/});
    await expect(next).toBeInViewport({ratio:.99});
    const reading=page.locator('[data-result-reading]');
    await expect.poll(()=>reading.evaluate(e=>e.scrollHeight<=e.clientHeight+1)).toBe(true);
    if(i===0) await page.locator('[data-outcome-art]').evaluateAll(async imgs=>Promise.all(imgs.map(img=>(img as HTMLImageElement).decode())));
    if(i===0) await page.screenshot({path:`.tmp-work/fixed-ux/${info.project.name}-carrier-result.png`});
    if(await next.getAttribute('aria-label')!=='Читать дальше') break;
    await next.click();
  }
});
