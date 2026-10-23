import { expect, test } from "@playwright/test";

for (const carrier of ["old", "old4", "crew", "express"]) {
  for (const [width, height] of [[1440, 900], [390, 844]]) {
    test(`Compact preserves glazing while painting ${carrier} at ${width}`, async ({ page }) => {
      await page.setViewportSize({ width, height });
      await page.goto(`/scenes.html?scene=compact&parcel=boat&recipient=khor&carrier=${carrier}`);
      const svg = page.locator('svg[data-cargo-view="side-2d"]');
      await expect(svg).toBeVisible();
      await expect(svg.locator('image[filter][mask]')).toHaveCount(1);
      const pixels = await svg.evaluate(async (element) => {
        const source = element as SVGSVGElement;
        const base = source.querySelector('image:not(defs image):not([filter])') as SVGImageElement;
        const y = Number(base.getAttribute('y'));
        const portrait = Number(base.getAttribute('height')) === 874;
        const delta = y + (portrait ? 234 : 0);
        const images = [...source.querySelectorAll('image')];
        const urls = new Map<string, string>();
        for (const image of images) {
          const href = image.getAttribute('href')!;
          if (urls.has(href)) continue;
          const blob = await (await fetch(href)).blob();
          const data = await new Promise<string>((resolve) => { const r = new FileReader(); r.onload = () => resolve(String(r.result)); r.readAsDataURL(blob); });
          urls.set(href, data);
        }
        async function render(overlay: boolean) {
          const clone = source.cloneNode(true) as SVGSVGElement;
          clone.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
          clone.setAttribute('width', '1040');
          clone.setAttribute('height', String(source.viewBox.baseVal.height));
          clone.querySelectorAll('foreignObject,rect[data-loading-zone]').forEach(n => n.remove());
          if (!overlay) clone.querySelectorAll('image[filter][mask]').forEach(n => n.remove());
          clone.querySelectorAll('image').forEach(n => n.setAttribute('href', urls.get(n.getAttribute('href')!)!));
          const img = new Image();
          img.src = URL.createObjectURL(new Blob([new XMLSerializer().serializeToString(clone)], { type: 'image/svg+xml' }));
          await img.decode();
          const canvas = document.createElement('canvas'); canvas.width = 1040; canvas.height = Math.ceil(source.viewBox.baseVal.height);
          const ctx = canvas.getContext('2d')!; ctx.drawImage(img, 0, 0); URL.revokeObjectURL(img.src);
          return ctx.getImageData(0, 0, canvas.width, canvas.height).data;
        }
        const original = await render(false), painted = await render(true);
        const changed = (x1: number, y1: number, x2: number, y2: number) => {
          let count = 0;
          for (let y = Math.ceil(y1 + delta); y < y2 + delta; y++) for (let x = x1; x < x2; x++) {
            const i = (y * 1040 + x) * 4;
            if ([0, 1, 2].some(c => Math.abs(original[i + c] - painted[i + c]) > 2)) count++;
          }
          return count;
        };
        return {
          sideGlass: changed(927, 187, 964, 229),
          windshield: changed(1006, 204, 1011, 223),
          mirror: changed(977, 195, 984, 215),
          vent: changed(867, 128, 875, 132),
          tire: changed(900, 355, 923, 385),
          paint: changed(853, 180, 890, 230),
          paintColor: [...painted.slice(((Math.round(205 + delta) * 1040 + 867) * 4), ((Math.round(205 + delta) * 1040 + 867) * 4) + 3)],
        };
      });
      expect(pixels.sideGlass).toBe(0);
      expect(pixels.windshield).toBe(0);
      expect(pixels.mirror).toBe(0);
      expect(pixels.vent).toBe(0);
      expect(pixels.tire).toBe(0);
      expect(pixels.paint).toBeGreaterThan(100);
      if (carrier === "old4") {
        expect(pixels.paintColor[0]).toBeGreaterThan(210);
        expect(pixels.paintColor[1]).toBeGreaterThan(165);
        expect(pixels.paintColor[2]).toBeLessThan(110);
      }
    });
  }
}
