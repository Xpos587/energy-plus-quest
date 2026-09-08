import tracks from "./mapTracks.json";

const centres = Object.fromEntries(Object.entries(tracks).map(([format, paths]) => [
  format, paths.map(path => [0, 1].map(axis => path.reduce((sum, p) => sum + p[axis], 0) / path.length)),
]));

// Follow the inside of each route, rather than flipping sides at the screen midpoint.
export function mapMarkerPositions(anchors: number[][], width: number, height: number) {
  const trucks = anchors.map(([x, y]) => [x * width / 100, y * height / 100]);
  const clearance = width * 0.065 + 15;
  const targets = centres[width / height < 1 ? "mobile" : "desktop"];
  const placed: number[][] = [];
  for (const [i, [x, y]] of trucks.entries()) {
    const direction = Math.atan2(targets[i][1] * height / 100 - y, targets[i][0] * width / 100 - x);
    let best: number[] = [22, 22];
    let bestScore = Infinity;
    for (let radius = clearance + 2; radius <= clearance + 122; radius += 4) {
      for (let step = 0; step < 48; step++) {
        const angle = direction + step * Math.PI / 24;
        const cx = Math.max(22, Math.min(width - 22, x + Math.cos(angle) * radius));
        const cy = Math.max(22, Math.min(height - 22, y + Math.sin(angle) * radius));
        if (trucks.some(([tx, ty]) => Math.hypot(cx - tx, cy - ty) < clearance)) continue;
        if (placed.some(([px, py]) => Math.hypot(cx - px, cy - py) < 45)) continue;
        const score = Math.hypot(cx - (x + Math.cos(direction) * (clearance + 2)), cy - (y + Math.sin(direction) * (clearance + 2)));
        if (score < bestScore) { bestScore = score; best = [cx, cy]; }
      }
    }
    placed.push(best);
  }
  return placed;
}
