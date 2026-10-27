import {expect,test, type Page} from '@playwright/test';

async function checkLayout(page:Page, state:string, name:string) {
  const app=page.locator('[data-scene]').last();
  const header=app.locator(':scope > header');
  const h=(await header.boundingBox())!;
  const viewport=page.viewportSize()!;
  expect(h.x,`${state} header left`).toBeLessThan(1);
  expect(h.y,`${state} header top`).toBeLessThan(1);
  expect(Math.abs(h.width-viewport.width),`${state} header width`).toBeLessThan(1);
  const art=app.locator('[data-result-art],[class*="carrierMap_"]');
  const panel=state==='result'?app.locator('[data-sheet-panel]'):state==='condition'?page.getByRole('region',{name:'Условие задания',exact:true}):state==='inspection'?app.locator('[data-choice-inspection]'):app.getByTestId('scene-question');
  const p=(await panel.boundingBox())!;
  if(viewport.height>500 || viewport.width<viewport.height) expect(p.x,`${state} panel left`).toBeLessThan(1);
  // Short landscape may place the panel beside the scene.
  if(viewport.height>500 || viewport.width<viewport.height) expect(Math.abs(p.width-viewport.width)).toBeLessThan(1);
  if(await art.count()===1) {
    const a=(await art.boundingBox())!;
    const overlap=Math.max(0,Math.min(a.x+a.width,p.x+p.width)-Math.max(a.x,p.x))*Math.max(0,Math.min(a.y+a.height,p.y+p.height)-Math.max(a.y,p.y));
    expect(overlap,`${state} art not covered`).toBeLessThan(2);
    expect(Math.abs(a.y-h.y-h.height),`${state} image meets header`).toBeLessThan(2);
    if(viewport.height>500 || viewport.width<viewport.height) expect(Math.abs(a.y+a.height-p.y),`${state} image meets panel`).toBeLessThan(2);
  }
  await app.locator('img').evaluateAll(async images=>Promise.all(images.map(async image=>{if(image.getAttribute('src')) await (image as HTMLImageElement).decode();})));
  await page.screenshot({path:`.tmp-work/edge-layout/${name}-${state}.png`});
}

test('all five stages stay contiguous through the complete delivery path',async({page},info)=>{
  await page.goto('/');
  for(const id of ['professional','khor','boat']) await page.locator(`[data-choice="${id}"]`).click();
  for(const [scene,choice] of [['carrier','express'],['compact','auto'],['inventory','wms'],['crane','remote'],['lastmile','rover']]) {
    await expect(page.locator(`[data-scene="${scene}"]`)).toBeVisible();
    const condition=page.getByRole('region',{name:'Условие задания',exact:true});
    const combined=page.locator('[data-briefing-inline="true"]');
    await expect(condition.or(combined)).toBeVisible();
    if(await condition.isVisible()) await checkLayout(page,'condition',`${scene}-${info.project.name}`);
    if(scene==='compact') {
      const field=page.locator('[data-world-scene="compact"]');
      const plane=field.locator('[data-world-plane]');
      await expect.poll(async()=>{
        const f=(await field.boundingBox())!,p=(await plane.boundingBox())!;
        return Math.max(f.x-p.x,f.y-p.y,p.x+p.width-f.x-f.width,p.y+p.height-f.y-f.height);
      }).toBeLessThan(2);
      for(const number of await field.locator('[data-hotspot] > span').all()) await expect(number).toBeVisible();
    }
    for(let n=0;n<30&&await condition.isVisible();n++) await condition.getByRole('button',{name:/^(Далее|К выбору|К сцене)$/}).click();
    await checkLayout(page,'choice',`${scene}-${info.project.name}`);
    await page.locator(`[${scene==='crane'?'data-hotspot':'data-scene-choice'}="${choice}"]`).click();
    await expect(page.locator('[data-choice-confirm]')).toBeInViewport({ratio:1});
    await checkLayout(page,'inspection',`${scene}-${info.project.name}`);
    await page.locator('[data-choice-confirm]').click();
    await checkLayout(page,'result',`${scene}-${info.project.name}`);
    for(let n=0;n<30&&await page.getByRole('button',{name:'Читать дальше',exact:true}).isVisible();n++) await page.getByRole('button',{name:'Читать дальше',exact:true}).click();
    if(scene!=='lastmile') await page.locator('[data-result-reader] footer button').last().click();
  }
});
