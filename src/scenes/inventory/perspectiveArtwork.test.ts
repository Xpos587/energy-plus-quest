import sharp from 'sharp';
import { expect, it } from 'vitest';
import manifest from '../worldManifest.json';
import contours from './segmentedContours.json';
import mobileContours from './segmentedContours.mobile.json';

it('registers the final perspective raster, native hit regions and both camera views together', async () => {
  for (const [format, drawing] of [['desktop', contours], ['mobile', mobileContours]] as const) {
    const image = drawing.source;
    const raster = await sharp(`public/${image}`).metadata();
    const view = manifest.scenes.inventory[format];
    expect(view.image).toBe(image);
    expect([view.width, view.height]).toEqual([raster.width, raster.height]);
    expect([drawing.width, drawing.height]).toEqual([raster.width, raster.height]);
  }
});
