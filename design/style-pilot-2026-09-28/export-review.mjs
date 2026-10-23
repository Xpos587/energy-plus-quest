import fs from 'node:fs/promises';
import path from 'node:path';
import sharp from 'sharp';
import { chromium } from '@playwright/test';

const dir = path.dirname(new URL(import.meta.url).pathname);
const gcd = (a,b) => b ? gcd(b,a%b) : a;
async function figure(file, label) {
 const data = await fs.readFile(path.resolve(dir,file));
 const {width,height} = await sharp(data).metadata();
 const d=gcd(width,height);
 return `<figure><img src="data:image/png;base64,${data.toString('base64')}"><figcaption><b>${label}</b><span>${width} × ${height} px · ${width/d}:${height/d}</span></figcaption></figure>`;
}
const pages=[];
async function page(title,items,cls='') {
 const content=await Promise.all(items.map(([file,label])=>figure(file,label)));
 pages.push(`<section><header><div><small>ЭНЕРГИЯ+ · СКЛАД</small><h1>${title}</h1></div><div class="status">На ревью<br><small>28.09.2026 · пакет 01</small></div></header><main class="${cls}">${content.join('')}</main><footer><span>Визуальная целостность</span><span>${String(pages.length+1).padStart(2,'0')}</span></footer></section>`);
}
await page('Эталон',[['../style-audit-2026-09-28/reference.png','Референс стилистики']]);
await page('Склад · сравнение версий',[['warehouse-master-v1.png','V1'],['warehouse-master-v2.png','V2']],'pair');
await page('Склад',[['warehouse-master-v2.png','V2']]);
await page('Последствие · сравнение версий',[['outcome-v1.png','V1'],['outcome-v2.png','V2']],'pair');
await page('Последствие',[['outcome-v2.png','V2']]);
await page('Экран · компьютер',[['desktop-outcome.png','V2 · 1440 × 900']]);
await page('Экраны · телефон',[['mobile-outcome.png','V2 · 390 × 844'],['small-outcome.png','V2 · 320 × 568']],'pair phones');
const html=`<!doctype html><html lang="ru"><meta charset="utf-8"><title>Энергия+ · Склад · Ревью 01</title><style>
@page{size:A4 landscape;margin:0}*{box-sizing:border-box}body{margin:0;font-family:Arial,sans-serif;color:#253747;background:#fff}section{width:297mm;height:210mm;padding:10mm 12mm 7mm;break-after:page;display:flex;flex-direction:column}section:last-child{break-after:auto}header{display:flex;justify-content:space-between;align-items:start;height:23mm;flex-shrink:0}small{font-size:9px;letter-spacing:1px;color:#627381}h1{font-size:22px;margin:4px 0;font-weight:600}.status{text-align:right;font-size:12px;line-height:1.7}main{display:flex;flex:1;min-height:0;justify-content:center;gap:7mm}figure{display:flex;flex:1;min-width:0;min-height:0;flex-direction:column;margin:0;align-items:center;justify-content:center}img{display:block;max-width:100%;max-height:151mm;object-fit:contain;min-height:0}.pair img{max-height:132mm}.phones img{height:149mm;max-height:149mm;width:auto;max-width:100%}figcaption{font-size:10px;width:100%;display:flex;justify-content:space-between;gap:10px;margin-top:3mm;color:#526675;flex-shrink:0}figcaption b{color:#253747;font-weight:600}footer{display:flex;justify-content:space-between;font-size:9px;color:#7b8790;margin-top:4mm;flex-shrink:0}.phones figure{flex:0 1 95mm}.phones figcaption{justify-content:center;flex-wrap:wrap}
</style>${pages.join('')}</html>`;
await fs.writeFile(path.join(dir,'review-print.html'),html);
const browser=await chromium.launch({headless:true});
const tab=await browser.newPage();
await tab.setContent(html,{waitUntil:'load'});
await tab.evaluate(async()=>{await document.fonts.ready;await Promise.all([...document.images].map(i=>i.decode()));});
await tab.pdf({path:path.join(dir,'energy-plus-warehouse-review-01.pdf'),printBackground:true,preferCSSPageSize:true});
await browser.close();
console.log(`Exported ${pages.length} pages.`);
