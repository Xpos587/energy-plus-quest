import { strictEqual } from "node:assert";
import { expect, test } from "vitest";
import { mapMarkerPositions } from "./mapMarkerPositions";
import tracks from "./mapTracks.json";

test("every badge stays on its own trailer roof through two loops and resize", () => {
  for (const format of ["mobile", "desktop"] as const) {
    for (const width of [171, 390, 1440, 1920]) {
      const height = width * (format === "mobile" ? 1088 / 720 : 788 / 1280);
      for (let frame = 0; frame < tracks[format][0].length * 2; frame++) {
        const anchors = tracks[format].map((path) => path[frame % path.length]);
        const positions = mapMarkerPositions(anchors, width, height);
        positions.forEach(([x, y], i) => {
          strictEqual(x, (anchors[i][0] * width) / 100);
          strictEqual(y, (anchors[i][1] * height) / 100);
        });
      }
    }
  }
});

test("track sampling metadata agrees with both complete authored loops", () => {
  expect(tracks.fps).toBe(60);
  expect(tracks.durationSeconds).toBe(64);
  for (const format of ["mobile", "desktop"] as const)
    for (const path of tracks[format])
      expect(path).toHaveLength(tracks.fps * tracks.durationSeconds);
});
