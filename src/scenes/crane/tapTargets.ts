/** A tap target in stage pixels. */
export type TargetRect = { x: number; y: number; w: number; h: number };

/**
 * Keeps the quay tap targets usable on any screen (R19 round 2): every target is
 * at least 44×44 px and neighbours keep an 8 px gap, so the ladder and the empty
 * cab of the near crane never share a finger. Targets only grow or move; the
 * actor they belong to stays inside them because they grow from their centre.
 */
export function fitTapTargets(
  rects: TargetRect[],
  stage: { width: number; height: number },
  { min = 44, gap = 8, frame }: { min?: number; gap?: number; frame?: TargetRect } = {},
): TargetRect[] {
  // The plane is bigger than the screen window; without a frame the targets are clamped to the drawing.
  const area = frame ?? { x: 0, y: 0, w: stage.width, h: stage.height };
  const grown = rects.map((rect) => {
    const w = Math.min(Math.max(rect.w, min), area.w);
    const h = Math.min(Math.max(rect.h, min), area.h);
    return { x: rect.x + rect.w / 2 - w / 2, y: rect.y + rect.h / 2 - h / 2, w, h };
  });
  // Two or three passes settle the quay's four overlapping pairs; more passes never move them again.
  for (let pass = 0; pass < 4; pass++) {
    let moved = false;
    for (let i = 0; i < grown.length; i++) {
      for (let j = i + 1; j < grown.length; j++) {
        const a = grown[i];
        const b = grown[j];
        const overlapX = Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x);
        const overlapY = Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y);
        if (overlapX <= -gap || overlapY <= -gap) continue;
        // Push along the axis where they overlap least: that is the shortest way out.
        const vertical = overlapY < overlapX;
        const push = ((vertical ? overlapY : overlapX) + gap) / 2 + 0.5;
        const sign = vertical
          ? (a.y + a.h / 2 < b.y + b.h / 2 ? -1 : 1)
          : (a.x + a.w / 2 < b.x + b.w / 2 ? -1 : 1);
        moved = true;
        if (vertical) {
          a.y += sign * push;
          b.y -= sign * push;
        } else {
          a.x += sign * push;
          b.x -= sign * push;
        }
      }
    }
    // Keep everything on the picture after a push.
    for (const rect of grown) {
      rect.x = Math.max(area.x, Math.min(area.x + area.w - rect.w, rect.x));
      rect.y = Math.max(area.y, Math.min(area.y + area.h - rect.h, rect.y));
    }
    if (!moved) break;
  }
  return grown;
}
