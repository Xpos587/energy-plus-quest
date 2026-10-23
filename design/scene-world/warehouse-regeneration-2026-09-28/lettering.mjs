import { spawnSync } from 'node:child_process';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

// Corners measured on a 2048 px preview: TL, TR, BL, BR.
// Only transparent lettering is composited; the original plaques stay intact.
const labels = [
  ['Ю–Я', [[488,409],[537,420],[488,465],[537,477]]],
  ['Ф–Э', [[566,428],[615,440],[566,483],[615,495]]],
  ['Н–У', [[874,506],[922,517],[874,562],[922,573]]],
  ['Л–М', [[953,524],[1003,536],[953,580],[1003,591]]],
  ['В–К', [[1270,592],[1320,605],[1270,648],[1320,660]]],
  ['А–Б', [[1353,612],[1403,625],[1353,668],[1403,680]]],
  ['ПРИЁМКА', [[162,244],[282,154],[162,280],[282,188]]],
  ['ОТГРУЗКА', [[1818,663],[1897,563],[1818,698],[1897,600]]],
];
const font = '/usr/share/fonts/TTF/DejaVuSans-Bold.ttf';
const work = mkdtempSync(join(tmpdir(), 'warehouse-lettering-'));
const run = (...args) => {
  const result = spawnSync('magick', args, { encoding: 'utf8' });
  if (result.status !== 0) throw new Error(result.stderr);
};
try {
  let base = 'public/scene-art/inventory-barge-style-v5.webp';
  for (const [index, [text, corners]] of labels.entries()) {
    const door = index >= 6;
    const width = 500, height = door ? 140 : 500;
    const label = join(work, `label-${index}.png`);
    run('-size', `${width}x${height}`, 'xc:none', '-font', font,
      '-pointsize', door ? '65' : '155', '-fill', '#173b60',
      '-gravity', 'center', '-annotate', '+0+0', text, label);
    const source = [[0,0],[width-1,0],[0,height-1],[width-1,height-1]];
    const mapping = source.map((p,i) => [...p, ...corners[i].map(v=>v*2752/2048)].join(',')).join(' ');
    const warped = join(work, `warped-${index}.png`);
    run(label, '-background', 'none', '-mattecolor', 'none', '-virtual-pixel', 'transparent', '-define',
      'distort:viewport=2752x1536+0+0', '-distort', 'Perspective', mapping, '+repage', warped);
    const next = join(work, `composite-${index}.png`);
    run(base, warped, '-compose', 'Over', '-composite', next);
    base = next;
  }
  run(base, '-quality', '94', 'public/scene-art/inventory-barge-style-v6.webp');
} finally {
  rmSync(work, { recursive: true, force: true });
}
