import fs from 'node:fs/promises';
import path from 'node:path';
import sharp from 'sharp';
import {chromium} from '@playwright/test';
const dir=path.dirname(new URL(import.meta.url).pathname);
const pages=[
 ['Фотоаппарат · иллюстрация',[
  ['До','../../public/compact-art/outcomes/camera-dishes.png'],
  ['После · V36','camera-zone2-v36.png']]],
 ['Носки · тот же принцип',[
  ['390 × 844','socks-zone2-mobile-after-v37.png'],
  ['320 × 568','socks-zone2-small-after-v37.png']]],
 ['Фотоаппарат · экраны V37',[
  ['390 × 844','camera-zone2-mobile-after-v37.png'],
  ['320 × 568','camera-zone2-small-after-v37.png']]],
];
let html='<!doctype html><html lang="ru"><meta charset="utf-8"><style>@page{size:A4 landscape;margin:0}*{box-sizing:border-box}body{margin:0;font-family:Arial;color:#143b55}section{width:297mm;height:210mm;padding:10mm 12mm;break-after:page;display:flex;flex-direction:column}header,footer{display:flex;justify-content:space-between}h1{font-size:23px;margin:0}small,footer{font-size:11px}.row{display:flex;flex:1;min-height:0;gap:24px;margin:5mm 0}.panel{display:flex;flex:1;flex-direction:column;align-items:center;min-width:0}h2{font-size:16px;margin:0 0 10px}figure{flex:1;min-height:0;margin:0;display:flex;justify-content:center}img{max-width:100%;max-height:158mm;object-fit:contain}.dims{font-size:11px;margin-top:8px}</style>';
for(const [title,panels] of pages){html+=`<section><header><h1>${title}</h1><small>Энергия+ · V37 · На ревью</small></header><div class="row">`;for(const [label,file]of panels){const data=await fs.readFile(path.join(dir,file));const m=await sharp(data).metadata();html+=`<div class="panel"><h2>${label}</h2><figure><img src="data:image/png;base64,${data.toString('base64')}"></figure><div class="dims">${m.width} × ${m.height} px</div></div>`;}html+='</div><footer><span>Погрузка · место №2</span><span>Экраны игры</span></footer></section>';}
await fs.writeFile(path.join(dir,'place2-mobile-v37-print.html'),html);
const browser=await chromium.launch({headless:true});const page=await browser.newPage();await page.setContent(html);await page.evaluate(async()=>{await document.fonts.ready;await Promise.all([...document.images].map(i=>i.decode()));});await page.pdf({path:path.join(dir,'energy-plus-place2-mobile-v37.pdf'),printBackground:true,preferCSSPageSize:true});await browser.close();console.log('Exported 3 pages');
