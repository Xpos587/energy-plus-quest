import {chromium} from '@playwright/test';
import assert from 'node:assert/strict';
const b=await chromium.launch();
try{const p=await b.newPage();const errors=[];p.on('pageerror',e=>errors.push(e.message));
await p.goto('http://127.0.0.1:4173/review/scene-concepts-2026-09-23/compact-style/placement-demo.html');
assert.equal(await p.getByRole('button',{name:'Подобрать с Compact',exact:true}).count(),1,'Compact automatic choice must be available');
for(const width of [1440,390,320]){await p.setViewportSize({width,height:1000});await p.reload();
for(const [parcel,zone] of [['camera','3'],['socks','3'],['boat','4']]){await p.getByLabel('Подарок',{exact:true}).selectOption(parcel);await p.getByRole('button',{name:'Подобрать с Compact',exact:true}).click();assert.equal(await p.locator('#stage').getAttribute('data-selected'),zone);assert.equal(await p.locator('[data-gift]').count(),1);}
await p.getByRole('button',{name:/3 · Узкая ниша/}).click();assert.equal(await p.locator('#stage').getAttribute('data-blocked'),'true');assert.match(await p.locator('#result').innerText(),/не помещается/);
await p.getByLabel('Подарок',{exact:true}).selectOption('camera');await p.getByRole('button',{name:/2 · Над посудой/}).click();assert.match(await p.locator('#result').innerText(),/свободн|пуст|неиспольз/);
await p.getByRole('button',{name:'Подушки и крепления',exact:true}).click();assert(await p.getByText('Подушки в закрытых коробках',{exact:true}).isVisible());
assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await p.screenshot({path:`design/scene-world/compact-style-2026-09-23/zones-${width}.png`,fullPage:true});}
assert.deepEqual(errors,[]);console.log('PASS: Compact camera/socks→3, boat→4; boat cannot fit 3; single gift; empty volume in 2; pillow explanation; 1440/390/320 without overflow or JS errors.');}finally{await b.close()}
