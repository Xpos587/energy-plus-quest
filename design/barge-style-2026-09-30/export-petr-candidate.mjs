import fs from 'node:fs/promises';
import path from 'node:path';
import {chromium} from '@playwright/test';
const dir=path.dirname(new URL(import.meta.url).pathname);
const uri=async file=>'data:image/png;base64,'+(await fs.readFile(path.join(dir,file))).toString('base64');
const current=await uri('petr-socks-v7-candidate.png');
const before=await uri('petr-socks-v4-rejected.png');
const html=`<!doctype html><meta charset="utf-8"><style>@page{size:A4 landscape;margin:0}*{box-sizing:border-box}body{margin:0;font-family:Arial;color:#173c55}section{width:297mm;height:210mm;padding:9mm;break-after:page;display:flex;flex-direction:column}header,footer{display:flex;justify-content:space-between}h1{font-size:21px;margin:0}small,footer{font-size:11px}.main{flex:1;display:flex;align-items:center;justify-content:center;gap:6mm;min-height:0}img{max-width:100%;max-height:174mm;object-fit:contain}.pair{width:50%;text-align:center}h2{font-size:15px}.crop{position:relative;overflow:hidden;width:260mm;height:140mm}.crop img{position:absolute;max-width:none;max-height:none;width:600mm;height:auto;left:-108mm;top:-20mm}</style>
<section><header><h1>Попросить Петра · Носки</h1><small>V7 · На ревью</small></header><div class="main"><img src="${current}"></div><footer><span>Композиция</span><span>1672 × 941 px</span></footer></section>
<section><header><h1>Персонажи · Деталь</h1><small>V7 · На ревью</small></header><div class="main"><div class="crop"><img src="${current}"></div></div><footer><span>Иван · Пётр</span><span>Увеличенный фрагмент</span></footer></section>
<section><header><h1>Композиция · До / После</h1><small>V7 · На ревью</small></header><div class="main"><div class="pair"><h2>До · V4</h2><img src="${before}"></div><div class="pair"><h2>После · V7</h2><img src="${current}"></div></div><footer><span>Сцена 4 · Погрузка на баржу</span><span>Носки</span></footer></section>`;
const browser=await chromium.launch({headless:true});const page=await browser.newPage();await page.setContent(html);await page.evaluate(async()=>{await document.fonts.ready;await Promise.all([...document.images].map(i=>i.decode()));});await page.pdf({path:path.join(dir,'energy-plus-petr-socks-v7-review.pdf'),printBackground:true,preferCSSPageSize:true});await browser.close();console.log('PDF: 3 pages');
