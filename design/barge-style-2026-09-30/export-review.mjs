import fs from 'node:fs/promises';
import path from 'node:path';
import sharp from 'sharp';
import { chromium } from '@playwright/test';

const dir = path.dirname(new URL(import.meta.url).pathname);
const root = path.resolve(dir, '../..');
const manifest = JSON.parse(await fs.readFile(path.join(dir, 'current.json'), 'utf8'));
const names = { rush: 'Попросить Ивана', wait: 'Ждать кран', petr: 'Попросить Петра', remote: 'Удалённое управление' };
const old = { rush: 'crane-rush-v4-desktop.png', wait: 'crane-wait-v4-desktop.png', petr: 'crane-petr-v7-desktop.png', remote: 'crane-remote-v4-desktop.png' };
let html = `<!doctype html><html lang="ru"><meta charset="utf-8"><style>
@page{size:A4 landscape;margin:0}*{box-sizing:border-box}body{margin:0;font-family:Arial,sans-serif;color:#173c55}section{width:297mm;height:210mm;padding:9mm 11mm;break-after:page;display:flex;flex-direction:column}header,footer{display:flex;justify-content:space-between;align-items:center}h1{font-size:22px;margin:0}small,footer,.dims{font-size:11px}.row{display:flex;flex:1;min-height:0;gap:16px;margin:5mm 0}.panel{display:flex;flex:1;min-width:0;flex-direction:column;align-items:center}h2{font-size:16px;margin:0 0 8px}figure{flex:1;min-height:0;margin:0;display:flex;align-items:center;justify-content:center;width:100%}img{max-width:100%;max-height:161mm;object-fit:contain}.dims{margin-top:6px}
</style>`;
async function panel(title, file) {
  const data = await fs.readFile(file);
  const meta = await sharp(data).metadata();
  return `<div class="panel"><h2>${title}</h2><figure><img src="data:image/png;base64,${data.toString('base64')}"></figure><span class="dims">${meta.width} × ${meta.height} px</span></div>`;
}
async function page(title, panels, footer) {
  html += `<section><header><h1>${title}</h1><small>V1 · На ревью</small></header><div class="row">`;
  for (const p of panels) html += await panel(...p);
  html += `</div><footer><span>Сцена 4 · Погрузка на баржу</span><span>${footer}</span></footer></section>`;
}
await page('Баржа · эталон и текущая сцена', [
  ['Эталон стиля', path.join(root, 'design/style-audit-2026-09-28/reference.png')],
  ['Лодка · V1', path.join(dir, manifest.choice.boat)],
], 'Статичные иллюстрации');
await page('Причал · до / после', [
  ['До', path.join(root, 'public/scene-art/crane-v2.png')],
  ['После · V1', path.join(dir, manifest.choice.boat)],
], 'Лодка');
for (const id of Object.keys(names)) {
  await page(`${names[id]} · до / после`, [
    ['До', path.join(root, 'public/scene-art/outcomes', old[id])],
    ['После', path.join(dir, manifest.outcomes[id].boat)],
  ], 'Лодка');
}
await fs.mkdir(path.join(dir, 'review-screens'), { recursive: true });
for (const id of Object.keys(names)) {
  const panels = [];
  for (const [gift, label] of [['socks', 'Носки'], ['camera', 'Фотоаппарат'], ['boat', 'Лодка']]) {
    const file = `390x844-${gift}-${id}.png`;
    const target = path.join(dir, 'review-screens', file);
    await fs.copyFile(path.resolve(dir, manifest.screenshots, file), target);
    panels.push([label, target]);
  }
  await page(names[id], panels, 'В игре · 390 × 844');
}
await fs.writeFile(path.join(dir, 'review-print.html'), html);
const browser = await chromium.launch({ headless: true });
const tab = await browser.newPage();
await tab.setContent(html);
await tab.evaluate(async () => { await document.fonts.ready; await Promise.all([...document.images].map(i => i.decode())); });
await tab.pdf({ path: path.join(dir, 'energy-plus-barge-style-v1.pdf'), printBackground: true, preferCSSPageSize: true });
await browser.close();
console.log('Exported barge review PDF: 10 pages');
