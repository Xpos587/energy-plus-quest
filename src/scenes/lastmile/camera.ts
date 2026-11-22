import { lastmileChoiceArtwork as art } from "./expandedArtwork";
import contours from "./segmentedContours.json";

type Box = { x: number; y: number; w: number; h: number };

/** Bounding box of a contour (paths are absolute M/L/Z polygons in plate px). */
export function contourBox(path: string): Box {
  const n = path.match(/-?\d+(\.\d+)?/g)!.map(Number);
  const xs = n.filter((_, i) => i % 2 === 0), ys = n.filter((_, i) => i % 2 === 1);
  const [x0, y0] = [Math.min(...xs), Math.min(...ys)];
  return { x: x0, y: y0, w: Math.max(...xs) - x0, h: Math.max(...ys) - y0 };
}

// Story tiers, widest first. Every recipient's destination is in `places`: Майма's chum, Хабт's reindeer by the
// chums, Арсений's АБК (scenario: «Конечные точки — АБК, чум Маймы»). The rig only receives the helicopter's pipes,
// so a phone loses it first; the transport row and the gift on the quay are never cut.
const pad = 12;
const { landmarks: l } = art;
const choice = [...Object.values(contours.regions).map(({ path }) => contourBox(path)), art.motion.rotor, l.gift];
const places = [...choice, l.chums, l.reindeer, l.abk, l.helipad];
const story = [...places, l.industry];
const span = (boxes: Box[], axis: "x" | "y") => {
  const size = axis === "x" ? "w" : "h";
  return [Math.min(...boxes.map((b) => b[axis])) - pad, Math.max(...boxes.map((b) => b[axis] + b[size])) + pad] as const;
};
/** The «Нажмите на транспорт» chip covers the top of the stage (smaller below 420 px). */
export const lastmileTopInset = (width: number) => (width <= 420 ? 56 : 64);

/** Owner 22.11 (as scene 4): one drawing on every screen. The camera only scales it to cover the stage, centres the
 * story and keeps the widest story tier that fits; it never moves for a selection, so choice and preview match. */
export function lastmileCamera(stage: { width: number; height: number }) {
  // Always cover: an empty band reads as a broken picture.
  const scale = Math.max(stage.width / art.width, stage.height / art.height);
  const place = (stageSize: number, size: number, axis: "x" | "y", inset: number) => {
    const cover = (offset: number) => Math.max(stageSize - size * scale, Math.min(0, offset));
    const [from, to] = span(story, axis);
    const offset = cover((stageSize + inset) / 2 - ((from + to) / 2) * scale);
    // The hint is a short centred chip and the destinations sit at the sides: a tier may run under it before it is dropped.
    for (const [keepFrom, keepTo] of [story, places, choice].map((tier) => span(tier, axis)))
      for (const top of [inset, 0])
        if ((keepTo - keepFrom) * scale <= stageSize - top)
          return cover(Math.max(top - keepFrom * scale, Math.min(stageSize - keepTo * scale, offset)));
    // Narrower than the quay row itself (a 704×1302 tablet stage beside the side panel): centre the four tap points,
    // so each vehicle's hotspot stays on screen while the row's outer ends are trimmed.
    const taps = art.hotspots.map((point) => point[axis] * size);
    return cover((stageSize + inset) / 2 - ((Math.min(...taps) + Math.max(...taps)) / 2) * scale);
  };
  return {
    width: art.width * scale,
    height: art.height * scale,
    left: place(stage.width, art.width, "x", 0),
    top: place(stage.height, art.height, "y", lastmileTopInset(stage.width)),
  };
}
