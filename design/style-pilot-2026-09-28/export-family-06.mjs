import fs from 'node:fs/promises';
import path from 'node:path';
import sharp from 'sharp';
import {chromium} from '@playwright/test';
const dir=path.dirname(new URL(import.meta.url).pathname);
const pages=[];
async function page(title,items,kind='') {
 const figures=await Promise.all(items.map(async([file,label])=>{
  const data=await fs.readFile(path.resolve(dir,file));
  const {width,height,format}=await sharp(data).metadata();
  const ratio=Math.abs(width/height-16/9)<.01?'≈16:9':width===height?'1:1':`${(width/height).toFixed(2)}:1`;
  return `<figure><img src="data:image/${format};base64,${data.toString('base64')}"><figcaption><b>${label}</b><span>${width} × ${height} px · ${ratio}</span></figcaption></figure>`;
 }));
 pages.push(`<section><header><div><small>ЭНЕРГИЯ+ · СКЛАД · ЛОДКА</small><h1>${title}</h1></div><aside>На ревью<small>29.09.2026 · пакет 06</small></aside></header><main class="${kind}">${figures.join('')}</main><footer><span>Визуальная целостность</span><span>${String(pages.length+1).padStart(2,'0')}</span></footer></section>`);
}
await page("Эталон",[["../style-audit-2026-09-28/reference.png","Референс стилистики"]]);
await page("Цвет и фактура · до / после",[["natural-faces/wms-v9.png","До · V9"],["clean-colors/wms-v10.png","После · V10"]]);
const items=[["Склад","baseline/warehouse.webp","clean-colors/warehouse-v4.png","V4"],["У приёмки","family-boat/baseline/inventory-entrance-v8.webp","clean-colors/entrance-v3.png","V3"],["По алфавиту","baseline/outcome.webp","clean-colors/alphabet-v5.png","V5"],["У кладовщика","family-boat/baseline/inventory-keeper-v8.webp","clean-colors/keeper-v6.png","V6"],["WMS","family-boat/baseline/inventory-wms-v8.webp","clean-colors/wms-v10.png","V10"]];
for(const [title,before,after,version] of items){await page(title+" · до / после",[[before,"До · исходная сцена"],[after,"После · "+version]]);await page(title,[[after,version]]);}
const html=`<!doctype html><html lang="ru"><meta charset="utf-8"><title>Энергия+ · Склад · 04</title><style>
@page{size:A4 landscape;margin:0}*{box-sizing:border-box}body{margin:0;font-family:Arial,sans-serif;color:#253747}section{width:297mm;height:210mm;padding:10mm 12mm 7mm;break-after:page;display:flex;flex-direction:column}section:last-child{break-after:auto}header{height:23mm;flex-shrink:0;display:flex;justify-content:space-between}small{font-size:9px;letter-spacing:1px;color:#627381}h1{font-size:22px;margin:4px 0;font-weight:600}aside{font-size:12px;text-align:right}aside small{display:block;margin-top:5px}main{display:flex;flex:1;min-height:0;justify-content:center;gap:7mm}figure{display:flex;flex:1;min-width:0;min-height:0;flex-direction:column;align-items:center;justify-content:center;margin:0}img{display:block;max-width:100%;max-height:149mm;object-fit:contain;min-height:0}figcaption{width:100%;font-size:11px;display:flex;justify-content:space-between;gap:8px;margin-top:3mm;color:#526675;flex-shrink:0}figcaption b{color:#253747}footer{display:flex;justify-content:space-between;font-size:9px;color:#7b8790;margin-top:4mm;flex-shrink:0}.phones figure{flex:0 1 95mm}.phones img{height:149mm}.phones figcaption{justify-content:center;flex-wrap:wrap}.details img{width:100%;height:90mm;image-rendering:auto}.details figcaption{flex-wrap:wrap}
</style>${pages.join('')}</html>`;
await fs.writeFile(path.join(dir,'family-review-print-06.html'),html);
const browser=await chromium.launch({headless:true});const tab=await browser.newPage();
await tab.setContent(html,{waitUntil:'load'});await tab.evaluate(async()=>{await document.fonts.ready;await Promise.all([...document.images].map(i=>i.decode()));});
await tab.pdf({path:path.join(dir,'energy-plus-warehouse-family-review-06.pdf'),printBackground:true,preferCSSPageSize:true});
await browser.close();console.log(`Exported ${pages.length} pages.`);
