import { expect, test } from "vitest";
import { mapMarkerPositions } from "./mapMarkerPositions";
import tracks from "./mapTracks.json";

test("all decoded frame targets fit and remain separate at small-phone size", () => {
  for (const [format, width, height] of [
    ["mobile", 171, 243],
    ["desktop", 440, 249],
  ] as const) {
    for (let frame = 0; frame < 1152; frame++) {
      const positions = mapMarkerPositions(
        tracks[format].map((path) => path[frame]),
        width,
        height,
      );
      positions.forEach(([x, y], i) => {
        for (const path of tracks[format]) {
          const [ax, ay] = path[frame];
          expect(Math.hypot(x - ax * width / 100, y - ay * height / 100))
            .toBeGreaterThanOrEqual(width * 0.065 + 15 - 0.01);
        }
        expect(x).toBeGreaterThanOrEqual(22);
        expect(x).toBeLessThanOrEqual(width - 22);
        expect(y).toBeGreaterThanOrEqual(22);
        expect(y).toBeLessThanOrEqual(height - 22);
        for (let j = 0; j < i; j++)
          expect(
            Math.hypot(x - positions[j][0], y - positions[j][1]),
          ).toBeGreaterThan(43.9);
      });
    }
  }
});
