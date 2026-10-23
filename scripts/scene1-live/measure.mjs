import { chromium } from 'playwright';
import { mkdir, writeFile } from 'node:fs/promises';
const out = process.argv[2];
const recording = process.argv[3] !== "--no-video";
if (!out) throw new Error('Usage: node scripts/scene1-live/measure.mjs /absolute/evidence-directory');
await mkdir(out, {recursive:true});
const browser = await chromium.launch();
const context = await browser.newContext({viewport:{width:1440,height:1000},...(recording ? {recordVideo:{dir:out,size:{width:1440,height:1000}}} : {})});
const page = await context.newPage();
await page.goto('http://localhost:4173/');
for (const choice of ['professional','alva','boat']) await page.locator(`[data-choice="${choice}"]`).click();
await page.locator('[data-map-surface][data-motion-state]').waitFor();
const samples = await page.evaluate(async()=>{
  const surface=document.querySelector('[data-map-surface]');
  const frames=[];
  await new Promise(resolve=>{
    let start;
    function sample(now){start??=now;frames.push({now,time:Number(surface.dataset.motionTime)});if(now-start<12000)requestAnimationFrame(sample);else resolve();}
    requestAnimationFrame(sample);
  });
  return frames;
});
for(let i=0;i<5;i++){await page.screenshot({path:`${out}/motion-${i}.png`});await page.waitForTimeout(1200);}
const intervals=samples.slice(1).map((f,i)=>f.now-samples[i].now).sort((a,b)=>a-b);
const summary={recording,frames:samples.length,p50:intervals[Math.floor(intervals.length*.5)],p95:intervals[Math.floor(intervals.length*.95)],p99:intervals[Math.floor(intervals.length*.99)],over34ms:intervals.filter(x=>x>34).length};
await writeFile(`${out}/frame-pacing.json`,JSON.stringify({summary,samples},null,2));
const video=page.video();await context.close();if(video)await video.saveAs(`${out}/motion.webm`);await browser.close();console.log(summary);
