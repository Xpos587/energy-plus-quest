import { chromium } from '@playwright/test';
import { mkdir, writeFile } from 'node:fs/promises';
const [baseURL, phase] = process.argv.slice(2);
const root = `docs/reviews/feedback-2026-10-22/carrier/${phase}`;
await mkdir(root, {recursive:true});
const browser = await chromium.launch();
const rows = [];
for (const [width,height] of [[320,568],[390,844],[844,390],[1440,900],[1920,1080]]) {
 const page = await browser.newPage({baseURL,viewport:{width,height},hasTouch:width<900});
 await page.goto('/');
 for(const selector of ['[data-intro-enter]','[data-intro-next]','[data-intro-start]','[data-choice="professional"]','[data-choice="arseniy"]','[data-choice="boat"]']) await page.locator(selector).click();
 await page.locator('[data-city-video]').evaluate(v=>{v.pause();v.currentTime=8;});
 await page.waitForTimeout(500);
 await page.screenshot({path:`${root}/${width}-choices.png`});
 await page.locator('[data-scene-choice="near"]').click();
 await page.waitForTimeout(1200);
 const target = page.locator('[data-carrier-choice="near"]');
 const styles = await target.evaluate(e=>{const s=getComputedStyle(e);return {background:s.backgroundColor,border:s.borderWidth,outline:s.outline,shadow:s.boxShadow,selected:e.getAttribute('aria-pressed')};});
 await page.screenshot({path:`${root}/${width}-inspection.png`});
 await page.locator('[data-choice-cancel]').click();
 await target.focus();await page.keyboard.press('Tab');await page.keyboard.press('Shift+Tab');
 await page.screenshot({path:`${root}/${width}-keyboard.png`});
 rows.push({width,height,baseURL,styles,keyboard:await target.evaluate(e=>({focused:e===document.activeElement,background:getComputedStyle(e).backgroundColor,outline:getComputedStyle(e).outline}))});
 await page.close();
}
await writeFile(`${root}/runtime.json`,JSON.stringify(rows,null,2));
await browser.close();
