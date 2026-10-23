import {test,expect} from '@playwright/test';
test('placement cue runs while choosing and respects reduced motion',async({page})=>{
 await page.emulateMedia({reducedMotion:'no-preference'});
 await page.goto('/scenes.html?scene=compact&parcel=boat&recipient=alva');
 const next=page.getByRole('button',{name:/^(Далее|К выбору)$/});
 for(let n=0;n<20&&await next.isVisible();n++) await next.click();
 const zone=page.locator('[data-loading-zone="place-1"]');
 const motion=await zone.evaluate(el=>{const s=getComputedStyle(el);return {name:s.animationName,iterations:s.animationIterationCount,duration:s.animationDuration};});
 expect(motion.name).toContain('placementOutline');
 expect(motion.iterations).toBe('infinite');
 expect(motion.duration).toBe('2.4s');
 const offset=await zone.evaluate(el=>getComputedStyle(el).strokeDashoffset);
 await expect.poll(()=>zone.evaluate(el=>getComputedStyle(el).strokeDashoffset)).not.toBe(offset);
 await page.locator('[data-scene-choice="place-1"]').click();
 await expect(zone).toHaveCSS('animation-name','none');
 await page.getByRole('button',{name:'Изменить выбор',exact:true}).click();
 await expect(zone).not.toHaveCSS('animation-name','none');
 await page.emulateMedia({reducedMotion:'reduce'});
 await expect(zone).toHaveCSS('animation-name','none');
});
test('compact header and introduction form a useful choice screen',async({page},info)=>{
 await page.goto('/scenes.html?scene=compact&parcel=boat&recipient=alva');
 await page.evaluate(()=>document.fonts.ready);
 const progress=page.locator('[aria-label="Этап 2 из 5: Загрузка"]');
 await expect(progress).toBeVisible();
 await expect(progress).toBeInViewport({ratio:1});
 await expect(page.locator('[data-progress-step]')).toHaveCount(0);
 await expect(page.locator('[data-scene-progress]')).toHaveText('Этап 2/5');
 const width=page.viewportSize()!.width;
 const choices=page.locator('[data-scene-choice]');
 if(width>=600) {
  await expect(choices).toHaveCount(5);
  for(const choice of await choices.all()) await expect(choice).toBeInViewport({ratio:1});
  await expect(page.getByRole('button',{name:'К выбору',exact:true})).toHaveCount(0);
  await expect(page.getByText(/Перевозчик найден/)).toBeVisible();
 }
 const next=page.getByRole('button',{name:/^(Далее|К выбору)$/});
 for(let n=0;n<20&&await next.isVisible();n++) await next.click();
 for(const choice of await choices.all()) await expect(choice).toBeInViewport({ratio:1});
 for(const id of ['place-1','place-2','place-3','place-4']) {
  const zone=page.locator(`[data-hotspot="${id}"]`);
  await expect(zone).toBeVisible();
  await zone.click();
  await expect(page.locator('[data-result-reader]')).toBeVisible();
  await page.getByRole('button',{name:'Изменить выбор',exact:true}).click();
 }
 await page.screenshot({path:`.tmp-work/compact-header/${info.project.name}.png`});
 await page.locator('[data-scene-choice="auto"]').click();
 await expect(page.locator('[data-result-reader]')).toBeVisible();
 await page.getByRole('button',{name:'Изменить выбор',exact:true}).click();
 await page.locator('[data-scene-choice="place-4"]').click();
 await expect(page.locator('[data-result-reader]')).toBeVisible();
 await expect(page.getByRole('button',{name:/^(Найти место на складе|Читать дальше)$/})).toBeInViewport({ratio:1});
 await page.screenshot({path:`.tmp-work/compact-header/${info.project.name}-result.png`});
 await page.getByRole('button',{name:'Изменить выбор',exact:true}).click();
 for(const choice of await choices.all()) await expect(choice).toBeInViewport({ratio:1});
});

for (const parcel of ['camera', 'socks']) test(`${parcel} place two uses boxed gift artwork`, async ({page},info) => {
 await page.goto(`/scenes.html?scene=compact&parcel=${parcel}&recipient=alva`);
 const next=page.getByRole('button',{name:/^(Далее|К выбору)$/});
 for(let n=0;n<20&&await next.isVisible();n++) await next.click();
 await page.locator('[data-scene-choice="place-2"]').click();
 await expect(page.locator('[data-cargo-view] > image:not([filter])')).toHaveAttribute('href',new RegExp(`${parcel}-zone2-v`));
 await expect(page.locator('[data-loading-zone="place-2"]')).toHaveAttribute('data-active','true');
 await expect(page.getByRole('button',{name:/^(Найти место на складе|Читать дальше)$/})).toBeInViewport({ratio:1});
 const framing = await page.locator('[data-world-plane]').evaluate(el => {
   const r=el.getBoundingClientRect();
   return {boxedCameraWidth:r.width*132/1368,boxedCameraHeight:r.height*75/1149};
 });
 console.log(`${info.project.name} ${parcel} box: ${JSON.stringify(framing)}`);
 await page.screenshot({path:`.tmp-work/compact-header/${info.project.name}-${parcel}2.png`});
 await page.getByRole('button',{name:'Изменить выбор',exact:true}).click();
 await expect(page.locator('[data-camera-detail]')).toHaveCount(0);
 await expect(page.locator('[data-cargo-view] > image:not([filter])')).not.toHaveAttribute('href',new RegExp(`${parcel}-zone2-v`));
 for (const id of ['place-1','place-2','place-3','place-4'])
   await expect(page.locator(`[data-hotspot="${id}"]`)).toBeInViewport({ratio:1});

});
