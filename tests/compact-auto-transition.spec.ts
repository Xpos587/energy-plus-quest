import { test, expect } from '@playwright/test';
for (const parcel of ['boat','camera','socks']) {
 test(`Compact automatic placement stays stable and waits for decoded ${parcel} artwork`, async ({page}) => {
  await page.route(/compact-art\/(boat-zone4-v29|camera-zone3-packed-v40|socks-zone3-secured-v43)\.png/,async route=>{await new Promise(resolve=>setTimeout(resolve,450));await route.continue();});
  await page.goto('/');await page.evaluate(parcel=>{localStorage.clear();const scope='quest-auto-transition';localStorage.setItem('energy-quest-save-v1',JSON.stringify({version:1,scope,state:{step:'outcome',profile:'student',recipient:'arseniy',parcel,carrier:'express',scores:{energy:0,empathy:0,efficiency:0}}}));localStorage.setItem(`${scope}:remaining`,'true');localStorage.setItem(`${scope}:intro-seen`,'true');localStorage.setItem(`${scope}:scenes`,JSON.stringify({progress:{sceneIndex:0,phase:'choice',finished:false,answers:{}}}));},parcel);await page.reload();
  while(await page.locator('[data-scene-briefing][data-reading="true"]').count()) await page.getByRole('button',{name:/^(Далее|К выбору)$/}).click();
  const art=page.locator('[data-world-scene="compact"]');await expect(art.locator('image').last()).toBeVisible();await expect(page.getByText('Загружаем иллюстрацию',{exact:false})).toHaveCount(0);
  const original=await art.boundingBox();await page.locator('[data-scene-choice="auto"]').click();await expect(art).toHaveAttribute('data-inspection-camera','true');
  expect(await art.boundingBox()).toEqual(original);
  expect(await art.evaluate(e=>Number((e as HTMLElement).style.getPropertyValue('--inspection-scale')))).toBeGreaterThan(1);
  await page.evaluate(()=>{(window as any).illustrationFlash=false;new MutationObserver(()=>{if([...document.querySelectorAll('[role="status"]')].some(e=>e.textContent?.includes('иллюстрацию')))(window as any).illustrationFlash=true;}).observe(document.body,{subtree:true,childList:true});});
  await page.locator('[data-choice-confirm]').click();await expect(page.locator('[data-layout="result"]')).toBeVisible();expect(await art.boundingBox()).toEqual(original);
  await expect(art.locator('image').last()).toHaveAttribute('href',new RegExp(`${parcel}-zone[34]`));
  await page.waitForTimeout(500);expect(await page.evaluate(()=>(window as any).illustrationFlash)).toBe(false);
  await page.getByRole('button',{name:'Изменить выбор',exact:true}).click();await expect(page.locator('[data-scene-choice="auto"]')).toBeVisible();expect(await art.boundingBox()).toEqual(original);
 });
}
