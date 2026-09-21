const {chromium}=require('/home/michael/Github/energy-plus-quest/node_modules/playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const crypto=require('node:crypto');
const root=__dirname;
const artifacts='/home/michael/.local/state/energy-plus-quest/production/2026-09-16-geometry-reference/pass-13';
const url='http://localhost:4173/review/map-geometry/pass-13/index.html';
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
(async()=>{
 const browser=await chromium.launch();const results=[];
 fs.mkdirSync(path.join(artifacts,'screenshots'),{recursive:true});
 try {
  for(const [width,height] of [[1440,1000],[390,844],[320,568],[820,1180],[568,320]]){
   const page=await browser.newPage({viewport:{width,height},reducedMotion:'reduce'});const errors=[];
   page.on('pageerror',e=>errors.push(e.message));
   assert.equal((await page.goto(url)).status(),200);
   assert.equal(await page.locator('[data-variant]').count(),2);
   await page.waitForFunction(()=>document.querySelector('[data-smoke]')?.children.length>0);
   assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
   assert.equal(await page.locator('#toggle').getAttribute('aria-pressed'),'false');
   const paused=await page.locator('[data-smoke]').first().innerHTML();await page.waitForTimeout(100);
   assert.equal(await page.locator('[data-smoke]').first().innerHTML(),paused);
   for(const key of ['before','after','before','after']){
    await page.locator(`[data-variant="${key}"]`).click();
    assert.equal(await page.locator(`[data-variant="${key}"]`).getAttribute('aria-pressed'),'true');
    assert.equal(await page.locator('#art').getAttribute('href'),key==='before'?'../pass-12/map-a.jpg':'map.jpg');
    assert.equal(await page.locator('[data-variant][aria-pressed="true"]').count(),1);
   }
   for(const key of ['before','after']){
    await page.locator(`[data-variant="${key}"]`).click();
    for(const id of ['download','crops'])assert.equal((await page.request.get(new URL(await page.locator(`#${id}`).getAttribute('href'),url).href)).status(),200);
   }
   await page.locator('#character').uncheck();
   assert.equal(await page.locator('.character').evaluate(e=>getComputedStyle(e).visibility),'hidden');
   await page.locator('#character').check();
   assert.equal(await page.locator('.character').evaluate(e=>getComputedStyle(e).visibility),'visible');
   await page.locator('#zoom').selectOption('2');
   const zoomWidth=await page.locator('.overview').evaluate(e=>e.getBoundingClientRect().width);
   await page.locator('[data-variant="before"]').click();
   assert.equal(await page.locator('.overview').evaluate(e=>e.getBoundingClientRect().width),zoomWidth);
   assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
   await page.locator('#zoom').selectOption('1');
   await page.locator('[data-variant="after"]').click();
   await page.locator('#toggle').click();await page.waitForTimeout(180);
   assert.notEqual(await page.locator('[data-smoke]').first().innerHTML(),paused);
   await page.locator('#toggle').click();
   for(const button of await page.locator('button').all())assert((await button.boundingBox()).height>=44);
   await page.screenshot({path:path.join(artifacts,'screenshots',`${width}x${height}.png`),fullPage:true});
   assert.deepEqual(errors,[]);results.push({width,height,passed:true,switches:4,states:2,zoomStable:true,reducedMotion:true});
   await page.close();
  }
  const page=await browser.newPage();await page.goto(url);
  const links=await page.evaluate(()=>[...document.querySelectorAll('[src],a[href],image[href],link[href],script[src]')].map(e=>e.getAttribute('src')||e.getAttribute('href')).filter(Boolean));
  links.push(...fs.readdirSync(root).filter(name=>fs.statSync(path.join(root,name)).isFile()));
  for(const link of new Set(links)){
   const target=new URL(link,url);assert.equal(target.origin,new URL(url).origin);
   const response=await page.request.get(target.href);assert.equal(response.status(),200,link);
   const local=path.resolve(root,decodeURIComponent(link));
   if(fs.existsSync(local)&&fs.statSync(local).isFile())assert.equal(sha(await response.body()),sha(fs.readFileSync(local)),`HTTP bytes: ${link}`);
  }
  const preserved=JSON.parse(fs.readFileSync(path.join(artifacts,'preserved-hashes.json')));
  for(const [file,hash]of Object.entries(preserved))assert.equal(sha(fs.readFileSync(path.resolve('/home/michael/Github/energy-plus-quest',file))),hash,`Preserved ${file}`);
  const result={passed:true,results,localAssetsMatchHTTP:true,priorReviewsAndCharacterUnchanged:true};
  fs.writeFileSync(path.join(root,'validation.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result,null,2));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
