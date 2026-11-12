import { expect, test } from '@playwright/test';
import { writeFile } from 'node:fs/promises';
import { openInventory } from './inventory-fixture';
import wide from '../src/scenes/inventory/segmentedContours.json' with { type: 'json' };
import tall from '../src/scenes/inventory/segmentedContours.mobile.json' with { type: 'json' };

for (const [width, height] of [[1440, 900], [1280, 800], [390, 844], [320, 568], [430, 932], [844, 390], [1180, 820], [2560, 1440], [390, 700], [375, 667], [1152, 720], [1024, 643], [820, 1180]]) {
  test(`Warehouse pins stay separate, with 4 beside the computer at ${width}×${height}`, async ({ page }, info) => {
    await page.setViewportSize({ width, height });
    for (const parcel of ['boat', 'camera', 'socks']) {
      await openInventory(page, parcel);
      await page.mouse.move(0, 0);
      const image = page.locator('[data-world-plane] picture img');
      const drawing = (await image.getAttribute('src'))!.includes('-tall') ? tall : wide;
      const pins = await page.locator('[data-hotspot]').evaluateAll(nodes => nodes.map(node => ({
        id: (node as HTMLElement).dataset.hotspot!,
        rect: node.getBoundingClientRect().toJSON(),
      })));
      const plane = (await image.boundingBox())!;
      if (process.env.CAPTURE_INVENTORY_PINS) {
        await page.screenshot({ path: info.outputPath(`${parcel}-overview.png`), scale: 'css' });
        await writeFile(info.outputPath(`${parcel}-overview.json`), JSON.stringify({ width, height, parcel, plane, pins, source: drawing.source }));
      }
      expect(pins).toHaveLength(4);
      for (const { id, rect } of pins) {
        expect(rect.width, id).toBe(44);
        expect(rect.height, id).toBe(44);
        expect(rect.left, id).toBeGreaterThanOrEqual(0);
        expect(rect.right, id).toBeLessThanOrEqual(width);
        expect(rect.top, id).toBeGreaterThanOrEqual(0);
        expect(rect.bottom, id).toBeLessThanOrEqual(height);
      }
      for (let i = 0; i < pins.length; i++) for (let j = i + 1; j < pins.length; j++) {
        const a = pins[i].rect, b = pins[j].rect;
        expect(a.right <= b.left || b.right <= a.left || a.bottom <= b.top || b.bottom <= a.top,
          `${pins[i].id} and ${pins[j].id} hit targets must not overlap`).toBe(true);
      }
      const pin = page.locator('[data-hotspot="wms"]');
      const assertSide = async () => {
        const { rect, art, src } = await pin.evaluate(node => {
          const image = document.querySelector<HTMLImageElement>('[data-world-plane] picture img')!;
          return { rect: node.getBoundingClientRect().toJSON(), art: image.getBoundingClientRect().toJSON(), src: image.getAttribute('src')! };
        });
        const target = (src.includes('-tall') ? tall : wide).regions.wms.anchor;
        expect(Math.abs(rect.x + rect.width - (art.x + art.width * target.x) - 1), 'right-pointing tip touches computer').toBeLessThan(1);
        expect(Math.abs(rect.y + rect.height / 2 - (art.y + art.height * target.y)), 'pin 4 is level with its computer anchor').toBeLessThan(1);
        const style = await pin.evaluate(node => {
          const css = getComputedStyle(node), disc = getComputedStyle(node, '::before'), tail = getComputedStyle(node, '::after');
          return { color: css.color, fill: disc.backgroundColor, rim: disc.borderLeftColor, tail: tail.borderLeftColor, tailWidth: tail.borderLeftWidth, tailRight: tail.borderRightWidth };
        });
        expect(style.fill).toBe('rgb(255, 255, 255)');
        expect(style.rim).toBe(style.color);
        expect(style.tail).toBe(style.color);
        expect(style.tailWidth).toBe('9px');
        expect(style.tailRight).toBe('0px');
        return style.color;
      };
      const idle = await assertSide();
      if (parcel === 'boat') {
        await pin.hover();
        const active = await assertSide();
        expect(active).not.toBe(idle);
        await pin.focus();
        await expect(pin).toBeFocused();
        await page.keyboard.press('Enter');
        await page.mouse.move(0, 0);
        await expect(pin).toHaveAttribute('aria-pressed', 'true');
        await expect(page.locator('[data-choice-confirm]')).toBeVisible();
        expect(await assertSide()).toBe(active);
        if (process.env.CAPTURE_INVENTORY_PINS) {
          await page.screenshot({ path: info.outputPath('boat-selected.png'), scale: 'css' });
          await writeFile(info.outputPath('boat-selected.json'), JSON.stringify({ width, height, plane: await image.boundingBox(), pins: [{ id: 'wms', rect: await pin.boundingBox() }] }));
        }
      }
    }
  });
}
