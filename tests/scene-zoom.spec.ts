import { expect, test } from '@playwright/test';
for (const scene of ['carrier','compact','inventory','crane','lastmile']) {
 test(`${scene}: fullscreen zoom, two-axis movement, opaque UI and touch pinch`, async ({page}, info)=>{
  await page.goto(scene==='carrier' ? '/' : `/scenes.html?scene=${scene}&parcel=boat&recipient=khor`);
  if(scene==='carrier') for(const id of ['professional','khor','boat']) await page.locator(`[data-choice="${id}"]`).click();
  const condition=page.getByRole('region',{name:'Условие задания',exact:true});
  await expect(condition).toBeVisible();
  for(let i=0;i<30&&await condition.isVisible();i++) await condition.getByRole('button',{name:/^(Далее|К выбору|К сцене)$/}).click();
  const map=page.locator('[data-map-viewport]');
  const plane=map.locator('[data-map-surface]');
  await expect(map).toHaveCount(1);
  await expect(map).toHaveAttribute('data-map-scale','1');
  const bounds=await map.boundingBox(); const vp=page.viewportSize()!;
  expect(bounds!.width).toBeGreaterThanOrEqual(vp.width-1);
  expect(bounds!.height).toBeGreaterThanOrEqual(vp.height-1);
  expect(await map.evaluate(e=>{ e.scrollLeft=100; e.scrollTop=100; return e.scrollLeft===0&&e.scrollTop===0; })).toBe(true);
  await page.mouse.move(vp.width*.5,vp.height*.55);
  await page.mouse.wheel(0,-600);
  await expect.poll(async()=>Number(await map.getAttribute('data-map-scale'))).toBeGreaterThan(1.5);
  const before=await plane.boundingBox();
  await page.mouse.down();await page.mouse.move(vp.width*.5+40,vp.height*.55+35,{steps:8});
  const during=await plane.boundingBox();
  expect(Math.abs(during!.x-before!.x)).toBeGreaterThan(10);
  expect(Math.abs(during!.y-before!.y)).toBeGreaterThan(10);
  expect(await page.locator('header').evaluate(e=>getComputedStyle(e).opacity)).toBe('1');
  await page.mouse.up();
  await expect(page.locator('[data-choice-confirm]')).toHaveCount(0);
  await map.focus();await page.keyboard.press('Home');
  await expect(map).toHaveAttribute('data-map-scale','1');
  const cdp=await page.context().newCDPSession(page);
  const cy=vp.height*.55, cx=vp.width*.5;
  await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:cx-25,y:cy,id:1},{x:cx+25,y:cy,id:2}]});
  await cdp.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:cx-60,y:cy-10,id:1},{x:cx+60,y:cy+10,id:2}]});
  await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
  await expect.poll(async()=>Number(await map.getAttribute('data-map-scale'))).toBeGreaterThan(1.5);
  await expect(page.locator('[data-choice-confirm]')).toHaveCount(0);
  await map.focus();await page.keyboard.press('Home');
  await page.evaluate(()=>document.fonts.ready);
  await page.screenshot({path:`.tmp-work/scene-zoom/${scene}-${info.project.name}.png`});
  if(scene!=='carrier') {
    await map.focus();await page.keyboard.press('+');await page.keyboard.press('+');
    for(const target of await map.locator('button[data-choice-id]:not([data-callout-target])').all()) {
      await target.focus();
      await expect(target).toBeInViewport({ratio:0.999});
      await target.click();
      await expect(page.locator('[data-choice-confirm]')).toBeVisible();
      await page.locator('[data-choice-cancel]').click();
    }
  }
  const choice=map.locator('button[data-choice-id],button[data-carrier-choice]').first();
  await choice.focus();
  await choice.press('Enter');
  await expect(page.locator('[data-choice-confirm]')).toBeVisible();
  await page.locator('[data-choice-confirm]').click();
  await expect(page.locator('[data-result-reader]')).toBeVisible();
  await expect(page.locator('[data-map-viewport]')).toHaveCount(0);
  if(vp.width<=600 && vp.height>vp.width) {
    const header=await page.locator('header').boundingBox();
    const art=await page.locator('[data-result-art], [data-outcome-scene], [data-fixed-result]').boundingBox();
    const panel=await page.locator('[data-sheet-panel]').boundingBox();
    expect(header!.x).toBe(0);expect(header!.width).toBe(vp.width);
    expect(panel!.x).toBe(0);expect(panel!.width).toBe(vp.width);
    expect(Math.abs(art!.y-header!.y-header!.height)).toBeLessThan(2);
    expect(Math.abs(panel!.y-art!.y-art!.height)).toBeLessThan(2);
  }
  await page.evaluate(()=>document.fonts.ready);
  await page.locator('[data-result-art] img, [data-outcome-scene] img, [data-fixed-result] img').evaluateAll(async images=>Promise.all(images.map(image=>(image as HTMLImageElement).decode())));
  await page.screenshot({path:`.tmp-work/scene-zoom/result-${scene}-${info.project.name}.png`});
  for(let i=0;i<40;i++) {
    expect(await page.locator('[data-result-reading]').evaluate(e=>e.scrollHeight<=e.clientHeight+2)).toBe(true);
    for(const button of await page.locator('[data-result-reader] footer button').all()) await expect(button).toBeInViewport({ratio:0.999});
    const more=page.getByRole('button',{name:'Читать дальше',exact:true});
    if(!await more.count()) break;
    await more.click();
  }
  await expect(page.getByRole('button',{name:'Читать дальше',exact:true})).toHaveCount(0);
 });
}
