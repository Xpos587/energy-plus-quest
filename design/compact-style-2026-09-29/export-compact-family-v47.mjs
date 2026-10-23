import fs from 'node:fs/promises';
import path from 'node:path';
import sharp from 'sharp';
import {chromium} from '@playwright/test';
const dir=path.dirname(new URL(import.meta.url).pathname);
const evidence=path.join(dir,'family-v47-screens');
await fs.mkdir(evidence,{recursive:true});
const ids=['place-1','place-2','place-3','place-4','auto'];
const gifts=[['socks','Носки'],['camera','Фотоаппарат'],['boat','Лодка']];
const uri=async(file)=>`data:image/png;base64,${(await fs.readFile(file)).toString('base64')}`;
let html='<!doctype html><html lang="ru"><meta charset="utf-8"><style>@page{size:A4 landscape;margin:0}*{box-sizing:border-box}body{margin:0;font-family:Arial;color:#163b55}section{width:297mm;height:210mm;padding:9mm 11mm;break-after:page;display:flex;flex-direction:column}header,footer{display:flex;justify-content:space-between;align-items:center}h1{font-size:22px;margin:0}small,footer{font-size:11px}.row{display:flex;flex:1;min-height:0;gap:14px;margin:5mm 0}.panel{display:flex;flex:1;min-width:0;flex-direction:column;align-items:center}h2{font-size:16px;margin:0 0 8px}figure{flex:1;min-height:0;margin:0;display:flex;align-items:center;justify-content:center;width:100%}img{max-width:100%;max-height:161mm;object-fit:contain}.dims{font-size:11px;margin-top:6px}</style>';
async function panel(label,file){const data=await fs.readFile(file);const m=await sharp(data).metadata();return `<div class="panel"><h2>${label}</h2><figure><img src="data:image/png;base64,${data.toString('base64')}"></figure><span class="dims">${m.width} × ${m.height} px</span></div>`;}
html+='<section><header><h1>Погрузка · единое семейство</h1><small>V47 · На ревью</small></header><div class="row">';
html+=await panel('Эталон стиля',path.join(dir,'../style-audit-2026-09-28/reference.png'));
html+=await panel('Актуальная сцена · V26',path.join(dir,'compact-environment-v26-portrait-v2.png'));
html+='</div><footer><span>Сцена 2</span><span>Статичные результаты</span></footer></section>';
html+='<section><header><h1>Иллюстрация · до / после</h1><small>V47 · На ревью</small></header><div class="row">';
html+=await panel('До',path.join(dir,'../../public/compact-art/outcomes/camera-dishes.png'));
html+=await panel('После · V36',path.join(dir,'camera-zone2-v36.png'));
html+='</div><footer><span>Фотоаппарат · место №2</span><span>Упаковка и крепления</span></footer></section>';
for(const id of ids){html+=`<section><header><h1>${id==='auto'?'Размещение Compact':`Место №${id.at(-1)}`}</h1><small>V47 · На ревью</small></header><div class="row">`;for(const[gift,label]of gifts){const name=`390x844-${gift}-${id}.png`;const source=path.resolve(dir,'../../.tmp-work/compact-final-2026-09-30',name);await fs.copyFile(source,path.join(evidence,name));html+=await panel(label,path.join(evidence,name));}html+='</div><footer><span>Результаты в игре</span><span>390 × 844 · мобильный экран</span></footer></section>';}
await fs.writeFile(path.join(dir,'compact-family-v47-print.html'),html);
const browser=await chromium.launch({headless:true});const page=await browser.newPage();await page.setContent(html);await page.evaluate(async()=>{await document.fonts.ready;await Promise.all([...document.images].map(i=>i.decode()));});await page.pdf({path:path.join(dir,'energy-plus-compact-family-v47.pdf'),printBackground:true,preferCSSPageSize:true});await browser.close();console.log('Exported 7 pages');
