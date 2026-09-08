// Separate touch targets at junctions while leader lines retain the exact truck anchor.
export function mapMarkerPositions(
  anchors: number[][],
  width: number,
  height: number,
) {
  const points = anchors.map(([x, y]) => [
    (x * width) / 100,
    (y * height) / 100,
  ]);
  const clamp = (p: number[]) => {
    p[0] = Math.max(22, Math.min(width - 22, p[0]));
    p[1] = Math.max(22, Math.min(height - 22, p[1]));
  };
  points.forEach(clamp);
  for (let pass = 0; pass < 40; pass++) {
    for (let i = 0; i < points.length; i++) {
      for (let j = 0; j < i; j++) {
        const a = points[i],
          b = points[j];
        const dx = a[0] - b[0],
          dy = a[1] - b[1];
        const distance = Math.hypot(dx, dy);
        if (distance >= 45) continue;
        const shift = (45 - distance) / 2;
        const ux = distance ? dx / distance : 1,
          uy = distance ? dy / distance : 0;
        a[0] += ux * shift;
        a[1] += uy * shift;
        b[0] -= ux * shift;
        b[1] -= uy * shift;
        clamp(a);
        clamp(b);
      }
    }
  }
  return points;
}
