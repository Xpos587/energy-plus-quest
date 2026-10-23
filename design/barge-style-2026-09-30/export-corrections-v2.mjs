import fs from 'node:fs/promises';
import path from 'node:path';
import sharp from 'sharp';
import { chromium } from '@playwright/test';

const dir = path.dirname(new URL(import.meta.url).pathname);
const changes = [
  ['Попросить Петра · Фотоаппарат','petr-camera-v2.png','petr-camera-v3.png'],
  ['Попросить Петра · Лодка','petr-boat-v2.png','petr-boat-v3.png'],
  ['Попросить Петра · Носки','petr-socks-v2.png','petr-socks-v3.png'],
  ['Попросить Ивана · Фотоаппарат','rush-camera-v1.png','rush-camera-v2.png'],
  ['Попросить Ивана · Носки','rush-socks-v1.png','rush-socks-v2.png'],
  ['Удалённое управление · Фотоаппарат','remote-camera-v2.png','remote-camera-v3.png'],
  ['Удалённое управление · Носки','remote-socks-v2.png','remote-socks-v3.png'],
];
let html = '<!doctype html><meta charset="utf-8"><style>@page{size:A4 landscape;margin:0}*{box-sizing:border-box}body{margin:0;color:#173c55;font-family:Arial,sans-serif}section{width:297mm;height:210mm;padding:10mm;break-after:page;display:flex;flex-direction:column}header,footer{display:flex;justify-content:space-between;align-items:center}h1{font-size:22px;margin:0}small,footer{font-size:11px}.row{display:flex;gap:6mm;flex:1;align-items:center}.panel{width:50%;text-align:center}h2{font-size:16px}img{width:100%;height:auto}.dims{font-size:11px;margin-top:8px}</style>';
for (const [title,before,after] of changes) {
  html += `<section><header><h1>${title}</h1><small>V2 · На ревью</small></header><div class="row">`;
  for (const [label,file] of [['До',before],['После',after]]) {
    const data = await fs.readFile(path.join(dir,file));
    const {width,height} = await sharp(data).metadata();
    html += `<div class="panel"><h2>${label}</h2><img src="data:image/png;base64,${data.toString('base64')}"><div class="dims">${width} × ${height} px</div></div>`;
  }
  html += '</div><footer><span>Сцена 4 · Погрузка на баржу</span><span>Геометрия и упаковка</span></footer></section>';
}
const browser = await chromium.launch({headless:true});
const page = await browser.newPage();
await page.setContent(html);
await page.evaluate(async()=>{await document.fonts.ready;await Promise.all([...document.images].map(i=>i.decode()));});
await page.pdf({path:path.join(dir,'energy-plus-barge-corrections-v2.pdf'),printBackground:true,preferCSSPageSize:true});
await browser.close();
console.log('Exported correction PDF, 7 pages');
