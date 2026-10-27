import { expect, test, type Locator } from '@playwright/test';

for (const [width, height] of [[320,568],[390,844],[620,768],[624,794],[835,974],[1440,900],[844,390]]) {
 for (const scene of ['compact', 'inventory', 'crane', 'lastmile']) {
 test(`${scene} shares panel and action geometry across states ${width}x${height}`, async ({page}, info) => {
  await page.setViewportSize({width,height});
  const tops:number[]=[];
  const bottoms:number[]=[];
  const sampleActions = async (buttons: Locator) => {
   for (const button of await buttons.all()) {
    await expect(button).toBeInViewport({ratio:1});
    const rect = await button.boundingBox();
    expect(rect!.height).toBe(48);
    bottoms.push(rect!.y + rect!.height);
   }
  };
  const sceneChoices: Record<string, string[]> = { compact: ['place-2', 'auto'], inventory: ['entrance', 'wms'], crane: ['rush', 'remote'], lastmile: ['helicopter', 'rover'] };
  for (const choice of sceneChoices[scene]) {
   await page.goto(`/scenes.html?scene=${scene}&parcel=boat&recipient=alva`);
   await page.evaluate(()=>document.fonts.ready);
   const next=page.getByRole('button',{name:/^(Далее|К выбору|К сцене)$/});
   const briefing=page.locator('[aria-label="Условие задания"]');
   if(height>500) tops.push((await briefing.boundingBox())!.y);
   for(let i=0;i<30&&await next.isVisible();i++) {
    await sampleActions(briefing.locator('button'));
    const intro = page.getByTestId('scene-intro');
    expect(await intro.evaluate(el=>el.firstElementChild!.getBoundingClientRect().height-el.clientHeight)).toBeLessThanOrEqual(1);
    await next.click();
   }
   const question = page.getByTestId('scene-question');
   if(height>500) tops.push((await question.boundingBox())!.y);
   await sampleActions(question.getByRole('button', {name:/К этапу|К выбору подарка|О задаче/}));
   await page.screenshot({path:info.outputPath(`${choice}-choices.png`)});
   const choices = page.locator('[data-scene-choice]');
   for(const button of await choices.all()) await expect(button).toBeInViewport({ratio:1});
   await page.locator(scene === 'compact' ? `[data-scene-choice="${choice}"]` : scene === 'inventory' || scene === 'crane' ? `[data-hotspot="${choice}"]` : `[data-choice-id="${choice}"]`).click();
   const inspection = page.locator('[data-choice-inspection]');
   if(height>500) tops.push((await inspection.boundingBox())!.y);
   await sampleActions(page.locator('[data-choice-confirm], [data-choice-cancel]'));
   await page.locator('[data-choice-confirm]').click();
   const reading=page.locator('[data-result-reading]');
   await expect(reading).toBeVisible();
   for(let i=0;i<30;i++) {
    await page.waitForTimeout(80);
    const measurements=await reading.evaluate(el=>({top:el.closest('[data-sheet-panel]')!.getBoundingClientRect().top, overflow:el.firstElementChild!.getBoundingClientRect().height-el.getBoundingClientRect().height}));
    tops.push(measurements.top);
    expect(measurements.overflow).toBeLessThanOrEqual(1);
    await sampleActions(page.locator('[data-result-reader] footer button'));
    const readMore=page.getByRole('button',{name:'Читать дальше',exact:true});
    if(!await readMore.isVisible())break;
    await readMore.click();
   }
   await page.screenshot({path:info.outputPath(`${choice}.png`)});
  }
  expect(Math.max(...tops)-Math.min(...tops)).toBeLessThanOrEqual(1);
  expect(Math.max(...bottoms)-Math.min(...bottoms)).toBeLessThanOrEqual(1);
 });
 }
}
