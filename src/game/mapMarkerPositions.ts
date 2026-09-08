// Keep the complete truck clear; callouts prefer the interior side of the map.
export function mapMarkerPositions(anchors: number[][], width: number, height: number) {
  const trucks = anchors.map(([x, y]) => [x * width / 100, y * height / 100]);
  const clearance = width * 0.065 + 15;
  const placed: number[][] = [];
  for (const [x, y] of trucks) {
    const side = x < width / 2 ? 1 : -1;
    let best: number[] = [22, 22];
    let bestScore = Infinity;
    for (let radius = clearance; radius <= clearance + 120; radius += 8) {
      for (let angle = 0; angle < 24; angle++) {
        const radians = angle * Math.PI / 12;
        const cx = Math.max(22, Math.min(width - 22, x + side * Math.cos(radians) * radius));
        const cy = Math.max(22, Math.min(height - 22, y + Math.sin(radians) * radius));
        if (trucks.some(([tx, ty]) => Math.hypot(cx - tx, cy - ty) < clearance)) continue;
        if (placed.some(([px, py]) => Math.hypot(cx - px, cy - py) < 45)) continue;
        const score = Math.hypot(cx - (x + side * clearance), cy - y);
        if (score < bestScore) { bestScore = score; best = [cx, cy]; }
      }
    }
    placed.push(best);
  }
  return placed;
}
