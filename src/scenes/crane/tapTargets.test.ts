import { describe, expect, it } from "vitest";
import { fitTapTargets, type TargetRect } from "./tapTargets";

/** Hotspot boxes measured in stage pixels on the real quay screens (src/scenes/crane/artwork.ts targets). */
const measured: Record<string, { stage: { width: number; height: number }; rects: TargetRect[] }> = {
  "320x568": {
    stage: { width: 320, height: 568 },
    rects: [
      { x: 27.7, y: 289.1, w: 36.6, h: 32 },
      { x: 135.7, y: 236.8, w: 23.9, h: 59.8 },
      { x: 140.5, y: 222.1, w: 22.1, h: 22.1 },
      { x: 228, y: 124.3, w: 22.1, h: 22.1 },
    ],
  },
  "390x844": {
    stage: { width: 390, height: 844 },
    rects: [
      { x: 33.8, y: 430, w: 44.6, h: 39 },
      { x: 165.4, y: 366.3, w: 29.1, h: 72.9 },
      { x: 171.3, y: 348.4, w: 26.9, h: 26.9 },
      { x: 277.8, y: 229.2, w: 26.9, h: 26.9 },
    ],
  },
  "1440x900": {
    stage: { width: 1440, height: 900 },
    rects: [
      { x: 73.4, y: 523.7, w: 116.3, h: 84.1 },
      { x: 425.8, y: 477, w: 79.6, h: 181 },
      { x: 450.1, y: 422.5, w: 77.8, h: 77.8 },
      { x: 851.4, y: 280.8, w: 77.8, h: 77.8 },
    ],
  },
};

const gaps = (rects: TargetRect[]) => {
  const out: number[] = [];
  for (let i = 0; i < rects.length; i++) {
    for (let j = i + 1; j < rects.length; j++) {
      const a = rects[i];
      const b = rects[j];
      out.push(Math.max(a.x - (b.x + b.w), b.x - (a.x + a.w), a.y - (b.y + b.h), b.y - (a.y + a.h)));
    }
  }
  return out;
};

describe("fitTapTargets", () => {
  for (const [name, { stage, rects }] of Object.entries(measured)) {
    it(`gives every quay target a 44px target and an 8px gap at ${name}`, () => {
      const fitted = fitTapTargets(rects, stage);
      expect(fitted).toHaveLength(rects.length);
      for (const [i, rect] of fitted.entries()) {
        expect(rect.w, `width of target ${i}`).toBeGreaterThanOrEqual(43.9);
        expect(rect.h, `height of target ${i}`).toBeGreaterThanOrEqual(43.9);
        expect(rect.x).toBeGreaterThanOrEqual(-0.01);
        expect(rect.y).toBeGreaterThanOrEqual(-0.01);
        expect(rect.x + rect.w).toBeLessThanOrEqual(stage.width + 0.01);
        expect(rect.y + rect.h).toBeLessThanOrEqual(stage.height + 0.01);
      }
      for (const [k, gap] of gaps(fitted).entries()) {
        expect(gap, `gap ${k}`).toBeGreaterThanOrEqual(7.9);
      }
    });

    it(`keeps each target over its own actor at ${name}`, () => {
      const fitted = fitTapTargets(rects, stage);
      for (const [i, rect] of rects.entries()) {
        const centreX = rect.x + rect.w / 2;
        const centreY = rect.y + rect.h / 2;
        expect(Math.abs(centreX - (fitted[i].x + fitted[i].w / 2))).toBeLessThan(rect.w / 2 + 24);
        expect(Math.abs(centreY - (fitted[i].y + fitted[i].h / 2))).toBeLessThan(rect.h / 2 + 24);
      }
    });
  }
});
