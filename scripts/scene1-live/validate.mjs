import { chromium } from "playwright";
import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";

const destination = process.argv[2];
if (!destination) throw new Error("Usage: node scripts/scene1-live/validate.mjs /absolute/evidence-directory [URL]");
const url = process.argv[3] ?? "http://localhost:4173/";
await mkdir(destination, { recursive: true });
const browser = await chromium.launch({ headless: true });
const checks = [];
for (const [width, height] of [[320,568],[390,844],[820,1180],[1440,1000],[844,390]]) {
  const context = await browser.newContext({ viewport: { width, height },
    ...([390,1440].includes(width) ? { recordVideo: { dir: destination, size: { width, height } } } : {}),
  });
  const page = await context.newPage();
  const errors = [];
  page.on("pageerror", error => errors.push(error.message));
  await page.goto(url);
  for (const choice of ["professional","alva","boat"]) await page.locator(`[data-choice="${choice}"]`).click();
  await page.locator('[data-map-surface][data-motion-state]').waitFor();
  await page.waitForTimeout(400);
  if([320,390].includes(width)){
    for(const index of [1,2,3,4]){await page.getByRole('button',{name:`Показать грузовик №${index} на карте`,exact:true}).click();await page.waitForTimeout(300);await page.screenshot({path:path.join(destination,`focus-${index}-${width}x${height}.png`)});}
    await page.getByRole('button',{name:'Показать грузовик №2 на карте',exact:true}).click();
  }
  const composition = await page.locator('[data-map-surface]').getAttribute('data-composition');
  await page.screenshot({ path: path.join(destination,`map-${width}x${height}.png`) });
  if ([390,1440].includes(width)) await page.waitForTimeout(9000);
  if (width===320) {
    await page.locator('[data-carrier-choice="express"]').scrollIntoViewIfNeeded();
    await page.screenshot({path:path.join(destination,'controls-320x568.png')});
  }
  for (const choice of ["old","near","crew","old4","express"]) {
    await page.locator(`[data-carrier-choice="${choice}"]`).click();
    const image = page.locator(`[data-outcome-art="${choice}"]:visible`);
    await image.evaluate(image => image.decode());
    if(width===390 || (width===1440 && choice==='express')) await page.screenshot({path:path.join(destination,`${choice}-${width}x${height}.png`)});
    await page.getByRole('button',{name:'К следующей сцене',exact:true}).click();
    await page.locator('[data-scene="compact"]').waitFor();
    await page.getByRole('button',{name:'Назад',exact:true}).click();
  }
  const overflow = await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth);
  checks.push({width,height,composition,allFiveResultsAndContinue:true,horizontalOverflow:overflow,errors});
  if(overflow||errors.length)throw new Error(JSON.stringify(checks.at(-1)));
  const video=page.video();
  await context.close();
  if(video)await video.saveAs(path.join(destination,`motion-${width}x${height}.webm`));
}
await browser.close();
await writeFile(path.join(destination,'browser-evidence.json'),JSON.stringify({url,engine:'Chromium emulation; not physical Safari',checks},null,2)+'\n');
console.log(JSON.stringify(checks));
