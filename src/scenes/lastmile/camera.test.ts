import { expect, it } from "vitest";
import { lastmileCamera, lastmileTopInset } from "./camera";
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
    // Tablets and desktops keep the rig too.
    if (width >= 700) expect(view.left + (l.industry.x + l.industry.w) * k).toBeLessThanOrEqual(width);
  },
);
