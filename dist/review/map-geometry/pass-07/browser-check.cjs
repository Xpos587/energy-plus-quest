const {chromium,webkit}=require('/home/michael/Github/energy-plus-quest/node_modules/playwright');
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const root=__dirname,url=process.env.REVIEW_URL||'http://localhost:4173/review/map-geometry/pass-07/index.html';
const data=JSON.parse(fs.readFileSync(path.join(root,'projection.json')));
const sizes=[[320,568],[375,667],[375,520],[390,844],[390,700],[568,320],[844,390],[820,1180],[1024,768],[1440,900],[2560,1440],[1152,720],[1029,643],[960,600]];
(async()=>{
 const {fitMap,placeTargets}=await import('./fit-map.mjs');
 const browser=await chromium.launch();const results=[];
 fs.mkdirSync(path.join(root,'screenshots'),{recursive:true});
 for(const [width,height] of sizes){
  const page=await browser.newPage({viewport:{width,height},reducedMotion:'reduce',hasTouch:true});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(url);await page.waitForFunction(()=>{const v=document.querySelector('video');return v?.readyState>=2&&!v.hidden;});
  assert(await page.locator('video').evaluate(v=>v.paused),'Reduced motion should start paused');
  const box=await page.locator('.map').evaluate(n=>({x:n.getBoundingClientRect().x,y:n.getBoundingClientRect().y,width:n.clientWidth,height:n.clientHeight}));const format=await page.locator('.map').getAttribute('data-format');const view=data.views[format],fit=fitMap(view,box.width,box.height);
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'Horizontal overflow');
  for(const target of await page.locator('button').all()){const b=await target.boundingBox();assert(b.width>=44&&b.height>=44,'Native target too small');}
  let smallest=Infinity;
  for(const row of view.tracks){
   for(const t of row){const b=t.bounds.map((v,k)=>v*fit.scale+(k%2?fit.y:fit.x));assert(b[0]>=7.99&&b[1]>=7.99&&b[2]<=box.width-7.99&&b[3]<=box.height-7.99);smallest=Math.min(smallest,Math.max(b[2]-b[0],b[3]-b[1]));}
   const targets=placeTargets(row.map(t=>[fit.x+t.marker[0]*fit.scale,fit.y+t.marker[1]*fit.scale]),box.width,box.height);
   targets.forEach(([x,y],i)=>{assert(x>=22&&y>=22&&x<=box.width-22&&y<=box.height-22);for(const [xx,yy] of targets.slice(i+1))assert(Math.abs(xx-x)>=43.999||Math.abs(yy-y)>=43.999);});
  }
  assert(smallest>=48,`Unreadable at ${width}x${height}: ${smallest}`);
  for(const frame of [1,127,384,767]){
   await page.locator('video').evaluate(async(v,t)=>{await new Promise(resolve=>{v.addEventListener('seeked',resolve,{once:true});v.currentTime=t;});},(frame+.25)/24);
   await page.waitForFunction(f=>Number(document.querySelector('.map').dataset.frame)===f,frame,{timeout:5000}).catch(async e=>{console.log({width,height,frame,state:await page.evaluate(()=>({frame:document.querySelector('.map').dataset.frame,time:document.querySelector('video').currentTime,paused:document.querySelector('video').paused}))});throw e;});
   const actualFrame=Number(await page.locator('.map').getAttribute('data-frame'));
   const expected=placeTargets(view.tracks[actualFrame].map(t=>[fit.x+t.marker[0]*fit.scale,fit.y+t.marker[1]*fit.scale]),box.width,box.height);
   const actual=await page.locator('.target').evaluateAll(nodes=>nodes.map(n=>[parseFloat(n.style.left),parseFloat(n.style.top)]));
   actual.forEach((p,i)=>p.forEach((v,k)=>assert(Math.abs(v-expected[i][k])<.1,`Marker out of sync ${width}x${height} f${actualFrame} truck${i} axis${k}: ${v} vs ${expected[i][k]}`)));
  }
  await page.locator('.choice').nth(2).focus();await page.keyboard.press('Enter');assert.equal(await page.locator('.target').nth(2).getAttribute('aria-pressed'),'true');
  await page.locator('.target').nth(1).tap();assert.equal(await page.locator('.choice').nth(1).getAttribute('aria-pressed'),'true');
  await page.screenshot({path:path.join(root,`screenshots/${width}x${height}.png`),fullPage:true});
  assert.deepEqual(errors,[]);results.push({width,height,format,map:box,smallestTruckPx:smallest,allLoopFrames:768,seekSamples:4,keyboard:true,tap:true,overflow:false});await page.close();
 }
 const page=await browser.newPage({viewport:{width:375,height:667}});await page.goto(url);await page.waitForFunction(()=>!document.querySelector('video').paused);
 await page.locator('.motion').click();await page.locator('video').evaluate(async v=>{await new Promise(resolve=>{v.addEventListener('seeked',resolve,{once:true});v.currentTime=12;});});
 await page.setViewportSize({width:1440,height:900});await page.waitForFunction(()=>document.querySelector('.map').dataset.format==='desktop'&&!document.querySelector('video').hidden);
 assert(Math.abs(await page.locator('video').evaluate(v=>v.currentTime)-12)<.1,'Phase lost on camera switch');
 const target=page.locator('.target').nth(0),b=await target.boundingBox();await page.mouse.move(b.x+22,b.y+22);await page.mouse.down();await page.locator('video').evaluate(async v=>{await new Promise(resolve=>{v.addEventListener('seeked',resolve,{once:true});v.currentTime=15;});});await page.mouse.up();assert.equal(await target.getAttribute('aria-pressed'),'true');
 const before=await page.locator('.selection').textContent();const b2=await page.locator('.target').nth(1).boundingBox();await page.mouse.move(b2.x+22,b2.y+22);await page.mouse.down();await page.mouse.move(b2.x+52,b2.y+52);await page.mouse.up();assert.equal(await page.locator('.selection').textContent(),before,'Drag selected truck');
 await page.locator('video').evaluate(async v=>{await new Promise(resolve=>{v.addEventListener('seeked',resolve,{once:true});v.currentTime=31.9;});});await page.locator('.motion').click();await page.waitForFunction(()=>document.querySelector('video').currentTime<2);await page.close();
 const failed=await browser.newPage({viewport:{width:320,height:568}});await failed.route('**/*-motion.mp4',r=>r.abort());await failed.goto(url);await failed.waitForFunction(()=>document.querySelector('.media-status').textContent.includes('недоступно'));assert(await failed.locator('video').evaluate(v=>v.hidden));assert.equal(await failed.locator('.map').getAttribute('data-frame'),'0');await failed.locator('.choice').nth(3).click();assert.equal(await failed.locator('.target').nth(3).getAttribute('aria-pressed'),'true');await failed.unroute('**/*-motion.mp4');await failed.locator('.motion').click();await failed.waitForFunction(()=>!document.querySelector('video').hidden&&!document.querySelector('video').paused);await failed.locator('video').evaluate(v=>v.dispatchEvent(new Event('error')));await failed.locator('.motion').click();await failed.waitForFunction(()=>!document.querySelector('video').hidden&&!document.querySelector('video').paused,{},{timeout:5000});await failed.close();await browser.close();
 let webkitStatus;try{const b=await webkit.launch();await b.close();webkitStatus='launch available; matrix not run';}catch(e){webkitStatus='Unavailable: missing host dependencies (libicu74, libxml2, libflite1). Not Safari verification.';}
 const report={browser:'Playwright Chromium',results,resizePhase:true,movingPointerCapture:true,dragCancelled:true,loop:true,mediaFallback:true,mediaRetry:true,reducedMotion:true,webkit:webkitStatus,zoom:'Last 3 sizes are 125%, 140%, 150% equivalent CSS viewports for 1440x900, not a physical browser-zoom test.',physicalDevices:'No physical iPhone or Telegram WebView access.'};fs.writeFileSync(path.join(root,'browser-check.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));
})().catch(e=>{console.error(e);process.exit(1)});
