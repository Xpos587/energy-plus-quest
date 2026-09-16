// Track anchors are trailer-roof centres, not free-floating callout targets.
export function mapMarkerPositions(anchors: number[][], width: number, height: number) {
  return anchors.map(([x, y]) => [x * width / 100, y * height / 100]);
}
