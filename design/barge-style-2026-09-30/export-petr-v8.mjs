import fs from 'node:fs/promises';
import path from 'node:path';
import sharp from 'sharp';
import {chromium} from '@playwright/test';
const dir=path.dirname(new URL(import.meta.url).pathname);
let html='<!doctype html><meta charset="utf-8"><style>@page{size:A4 landscape;margin:0}*{box-sizing:border-box}body{margin:0;font-family:Arial;color:#173c55}section{width:297mm;height:210mm;padding:9mm;break-after:page;display:flex;flex-direction:column}header,footer{display:flex;justify-content:space-between}h1{font-size:21px;margin:0}small,footer,.dims{font-size:11px}.row{flex:1;display:flex;align-items:center;justify-content:center;gap:5mm;min-height:0}.panel{flex:1;min-width:0;text-align:center}img{max-width:100%;max-height:160mm;object-fit:contain}h2{font-size:14px}</style>';
async function page(title,panels){html+=`<section><header><h1>${title}</h1><small>V8 · На ревью</small></header><div class="row">`;for(const[label,file]of panels){const data=await fs.readFile(path.resolve(dir,file));const m=await sharp(data).metadata();html+=`<div class="panel"><h2>${label}</h2><img src="data:image/png;base64,${data.toString('base64')}"><div class="dims">${m.width} × ${m.height} px</div></div>`;}html+='</div><footer><span>Сцена 4 · Попросить Петра</span><span>Статичная иллюстрация</span></footer></section>';}
await page('Эталон и выбранная композиция',[['Эталон стиля','../style-audit-2026-09-28/reference.png'],['Носки · V8','petr-socks-v8.png']]);
for(const[gift,label]of[['socks','Носки'],['camera','Фотоаппарат'],['boat','Лодка']])await page(`${label} · До / После`,[['До · V3',`petr-${gift}-v3.png`],['После · V8',`petr-${gift}-v8.png`]]);
const screenDir='../../.tmp-work/barge-petr-v8-final/';
const screenshots=[];for(const[gift,label]of[['socks','Носки'],['camera','Фотоаппарат'],['boat','Лодка']]){const file=screenDir+`390x844-${gift}-petr.png`;try{await fs.access(path.resolve(dir,file));screenshots.push([label,file]);}catch{}}
if(screenshots.length===3)await page('В игре · 390 × 844',screenshots);
const browser=await chromium.launch({headless:true});const tab=await browser.newPage();await tab.setContent(html);await tab.evaluate(async()=>{await document.fonts.ready;await Promise.all([...document.images].map(i=>i.decode()));});await tab.pdf({path:path.join(dir,'energy-plus-petr-family-v8.pdf'),printBackground:true,preferCSSPageSize:true});await browser.close();console.log('PDF exported; mobile screenshots included: '+screenshots.length);
