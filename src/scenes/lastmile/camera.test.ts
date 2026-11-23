import { expect, it } from "vitest";
import { contourBox, lastmileCamera, lastmileTopInset } from "./camera";
import contours from "./segmentedContours.json";
import { lastmileChoiceArtwork as art } from "./expandedArtwork";

it("camera always covers the stage, never exposing the background", () => {
  for (let width = 320; width <= 2560; width += 10)
    for (let height = 300; height <= 1600; height += 10) {
      const view = lastmileCamera({ width, height });
      expect(view.left, `${width}x${height}`).toBeLessThanOrEqual(1e-6);
      expect(view.top, `${width}x${height}`).toBeLessThanOrEqual(1e-6);
      expect(view.left + view.width, `${width}x${height}`).toBeGreaterThanOrEqual(width - 1e-6);
      expect(view.top + view.height, `${width}x${height}`).toBeGreaterThanOrEqual(height - 1e-6);
    }
});

// Choice and the taller second briefing sheet on the same 360×780, 390×844 and 412×915 phones.
it.each([[360, 436.84375], [390, 525.84375], [412, 596.84375], [360, 510.734375], [390, 574.734375], [412, 645.734375]])(
  "%ix%i keeps both crane extremities, all four vehicles and the far-bank landmarks inside the phone",
  (width, height) => {
    const view = lastmileCamera({ width, height });
    const scale = view.width / art.width;
    const boxes = [...Object.values(art.landmarks), art.motion.rotor, ...Object.values(contours.regions).map(({ path }) => contourBox(path))];
    for (const { x, y, w, h } of boxes) {
      expect(view.left + x * scale).toBeGreaterThan(5);
      expect(width - view.left - (x + w) * scale).toBeGreaterThan(5);
      expect(view.top + y * scale).toBeGreaterThan(lastmileTopInset(width));
      expect(height - view.top - (y + h) * scale).toBeGreaterThan(5);
    }
  },
);

// Measured map stages (390x844 → 390x526 above the sheet, desktop → stage beside the side panel).
it.each([[390, 526], [412, 597], [768, 751], [704, 704], [896, 736], [1040, 836], [1520, 1016], [2160, 1016]])(
  "%ix%i keeps the quay, the gift and every recipient's destination (chums, АБК) under the hint",
  (width, height) => {
    const view = lastmileCamera({ width, height });
    const k = view.width / art.width;
    const l = art.landmarks;
    // 21:9 shows 1130 of 1800 plate px in height: the chum tips may be trimmed, the camp itself (with reindeer) stays.
    const camp = { x: l.chums.x, y: l.reindeer.y, w: l.chums.w, h: l.chums.y + l.chums.h - l.reindeer.y };
    for (const [name, box] of Object.entries({ camp, abk: l.abk, helipad: l.helipad, gift: l.gift, rotor: art.motion.rotor, "pipe-carrier": art.motion["pipe-carrier"] })) {
      expect(view.left + box.x * k, name).toBeGreaterThanOrEqual(0);
      expect(view.left + (box.x + box.w) * k, name).toBeLessThanOrEqual(width);
      // The «Нажмите на транспорт» chip is centred: side landmarks may run under its band, central ones not.
      const central = box.x * k + view.left < width / 2 + 160 && (box.x + box.w) * k + view.left > width / 2 - 160;
      expect(view.top + box.y * k, name).toBeGreaterThanOrEqual(central ? lastmileTopInset(width) : 0);
      expect(view.top + (box.y + box.h) * k, name).toBeLessThanOrEqual(height);
    }
    // The distant rig fits with margin on both phones; ultra-wide cover can trim distant terrain vertically.
    if (height > width) {
      expect(view.left + l.industry.x * k).toBeGreaterThan(8);
      expect(view.left + (l.industry.x + l.industry.w) * k).toBeLessThan(width - 8);
      expect(view.top + l.industry.y * k).toBeGreaterThan(lastmileTopInset(width));
    }
  },
);
