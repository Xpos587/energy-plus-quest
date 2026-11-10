/** Hand-drawn character variants per format (see epq-gen storyboard). */
import type { CraneFormat } from "./artwork";
import { craneLayers } from "./layers";

type Box = { x: number; y: number; w: number; h: number };
type Cast = { window: Box; cab: Box; office: Box; figs: Record<string, number> };

/** Figures are format-independent (same files in every folder); width/height, feet at the bottom. */
const figs = {
  "ivan-run1": 0.567, "ivan-run2": 0.583, "ivan-climb1": 0.483, "ivan-climb2": 0.483,
  "petr-walk1": 0.525, "petr-walk2": 0.567, "petr-sad": 0.375, "petr-climb": 0.458,
};

/** Office and far-cab variants share their boxes; `office` is the whole ПРУ building cut from the plate, so it can glow. */
const authoredCast: Record<CraneFormat, Cast> = {
  wide: {
    window: { x: 463.6, y: 393.8, w: 184.5, h: 139.1 },
    cab: { x: 1434.2, y: 0.3, w: 357.1, h: 303.2 },
    office: { x: 442.5, y: 318.0, w: 224.0, h: 255.8 },
    figs,
  },
  desk: { window: { x: 230.7, y: 528.0, w: 182.7, h: 140.7 },
    cab: { x: 1162.7, y: 79.4, w: 373.3, h: 316.0 },
    office: { x: 142.7, y: 451.4, w: 280.7, h: 256.0 }, figs },
  mid: { window: { x: 180.0, y: 590.7, w: 172.7, h: 134.0 },
    cab: { x: 1042.0, y: 147.2, w: 360.0, h: 298.1 },
    office: { x: 98.7, y: 518.7, w: 260.7, h: 243.4 }, figs },
  tall: { window: { x: 125.0, y: 992.5, w: 131.8, h: 128.4 },
    cab: { x: 626.0, y: 339.0, w: 386.6, h: 267.6 },
    office: { x: 74.1, y: 923.6, w: 171.2, h: 212.0 }, figs },
};

// Calibration of the existing patches: office anchor x/y and far-cab x.
// Camera zoom/translation can change; a new viewing angle needs new artwork.
type Calibration = readonly [number, number, number];
const authoredCamera: Record<CraneFormat, Calibration> = {
  wide: [554.8, 372.4, 1561], desk: [315.9, 507.3, 1298.4],
  mid: [258.4, 571.1, 1174.8], tall: [160.6, 983, 780.1],
};
export function reframeCastBox(box: Box, from: Calibration, to: Calibration): Box {
  const scale = (to[2] - to[0]) / (from[2] - from[0]);
  return { x: to[0] + (box.x - from[0]) * scale, y: to[1] + (box.y - from[1]) * scale,
    w: box.w * scale, h: box.h * scale };
}
export const craneCast = Object.fromEntries(Object.entries(authoredCast).map(([name, cast]) => {
  const format = name as CraneFormat;
  const { pru, farCabin } = craneLayers[format].anchors;
  const place = (box: Box) => reframeCastBox(box, authoredCamera[format], [pru[0], pru[1], farCabin[0]]);
  return [format, { ...cast, window: place(cast.window), cab: place(cast.cab), office: place(cast.office) }];
})) as Record<CraneFormat, Cast>;

export const castSrc = (format: CraneFormat, name: string) => `scene-art/barge-v5/${format}/${name}.webp`;
