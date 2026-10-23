import {chromium,expect} from '@playwright/test';
import {writeFile} from 'node:fs/promises';
const root='docs/reviews/barge-2026-10-17/revision-3',browser=await chromium.launch(),receipt=[];
for(const viewport of [{width:320,height:568},{width:390,height:844},{width:844,height:390},{width:1440,height:900}]){
const page=await browser.newPage({viewport});
for(const v of ['a','b','c'])for(const parcel of ['boat','camera','socks']){
await page.goto('file://'+process.cwd()+`/${root}/prototype.html?v=${v}&parcel=${parcel}`);
await expect(page.locator('.condition')).toBeVisible();let fullIntro=[];while(await page.locator('.condition').count()){fullIntro.push(await page.locator('.intro-copy').innerText());await page.locator('.condition button').click();}
await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));expect(fullIntro.join(' ')).toContain('три часа');await expect(page.locator('.option.preview')).toHaveCount(0);await expect(page.locator('.context p:last-child')).toBeVisible();await expect(page.locator('.context p:last-child')).toContainText('своя погрузка');
const actions=[];
for(const id of ['remote','rush','wait','petr']){
await page.locator(`[data-option=${id}]`).click();await expect(page.locator('main')).toHaveAttribute('data-state',id);await page.locator('[data-revise]').click();
await page.locator(`[data-option=${id}]`).focus();await expect(page.locator(`[data-option=${id}]`)).toBeFocused();expect(await page.evaluate(()=>window.PROTOTYPE.active)).toBe(id);await page.locator(`[data-option=${id}]`).press('Enter');await expect(page.locator('main')).toHaveAttribute('data-state',id);
await page.locator('.outcome-sheet').evaluate(i=>i.decode());
let shown=await page.locator('.reading').innerText();const paged=(await page.locator('[data-next]').innerText()).includes('Читать дальше');if(paged){await page.locator('[data-next]').click();shown+=' '+await page.locator('.reading').innerText();}
const expected=await page.evaluate(id=>window.COPY.results[id].map(s=>s.replaceAll('(подарок)',{boat:'лодку',camera:'фотоаппарат',socks:'вязаные носки'}[window.PROTOTYPE.parcel]).replaceAll('(персонажу)','Майме').replace('Теперь он придет',`Теперь ${window.PROTOTYPE.parcel==='boat'?'она придет':window.PROTOTYPE.parcel==='socks'?'они придут':'он придет'}`)).join(' '),id);
expect(shown.replace(/\s+/g,' ').trim()).toBe(expected.replace(/\s+/g,' ').trim());
await expect(page.locator('[data-revise]')).toBeInViewport({ratio:1});await expect(page.locator('[data-next]')).toBeInViewport({ratio:1});
if(id==='petr')await expect(page.locator('.reading')).toContainText('Петр выручил');
actions.push({id,paged,font:await page.locator('.reading').evaluate(e=>getComputedStyle(e).fontSize)});
await page.locator('[data-revise]').click();await expect(page.locator('.condition')).toHaveCount(0);await expect(page.locator('main')).toHaveAttribute('data-state','choice');
}
receipt.push({viewport,v,parcel,neutralFirstEntry:true,petryAvailabilityVisible:true,exactSourceCopy:true,actions});
}await page.close();}
await writeFile(`${root}/interaction-checks.json`,JSON.stringify(receipt,null,2));console.log(JSON.stringify({passed:receipt.length,keyboardSelections:receipt.length*4,sourceCopyMatches:receipt.length*4,mouseSelections:receipt.length*4,neutralFirstEntry:receipt.length}));await browser.close();
