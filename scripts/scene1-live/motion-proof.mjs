import { chromium } from 'playwright';
import { mkdir, writeFile } from 'node:fs/promises';
const [out, url = 'http://localhost:4173/', focus = 'overview', start = '0', duration = '6', format = 'desktop'] = process.argv.slice(2);
if (!out) throw Error('Usage: motion-proof.mjs OUTPUT [URL] [overview|1..4] [START] [SECONDS] [desktop|mobile]');
await mkdir(`${out}/frames`, {recursive:true});
const browser = await chromium.launch();
const page = await browser.newPage({viewport:format === 'mobile' ? {width:390,height:844} : {width:1440,height:1000}});
// Keep the browser/compositor running, but advance the map clock one exact frame
// at a time. This is visual evidence, not a claim about device frame pacing.
await page.addInitScript(() => {
  const native = window.requestAnimationFrame.bind(window);
  let clock = 1000;
  window.requestAnimationFrame = callback => native(() => callback(clock));
  window.advanceMap = async delta => {
    clock += delta;
    await new Promise(resolve => native(() => native(resolve)));
  };
});
const errors=[];page.on('pageerror',e=>errors.push(e.message));
await page.goto(url);
for(const id of ['professional','alva','boat'])await page.locator(`[data-choice="${id}"]`).click();
const surface=page.locator('[data-map-surface][data-motion-state]');await surface.waitFor();
if(focus==='overview') {
  const button=page.getByRole('button',{name:'Показать всю карту',exact:true});if(await button.count())await button.click();
} else await page.getByRole('button',{name:`Показать грузовик №${focus} на карте`,exact:true}).click();
await page.evaluate(()=>window.advanceMap(0));
for(let i=0;i<Math.round(Number(start)*10);i++)await page.evaluate(()=>window.advanceMap(100));
const clip=await surface.boundingBox();
await page.screenshot({path:`${out}/normal-size.png`});
const times=[];
for(let frame=0;frame<Number(duration)*24;frame++) {
  await page.screenshot({path:`${out}/frames/${String(frame).padStart(4,'0')}.png`,clip});
  times.push(Number(await surface.getAttribute('data-motion-time')));
  await page.evaluate(()=>window.advanceMap(1000/24));
}
await writeFile(`${out}/proof.json`,JSON.stringify({url,focus,start,duration,format,clip,fps:24,times,errors},null,2));
await browser.close();
if(errors.length)throw Error(errors.join('\n'));
console.log(`${out}: ${times.length} exact clock frames, ${times[0]}..${times.at(-1)}s`);
