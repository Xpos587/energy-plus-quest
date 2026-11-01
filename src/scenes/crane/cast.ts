/** Hand-drawn character variants per format (see epq-gen storyboard). */
import type { CraneFormat } from "./artwork";

type Box = { x: number; y: number; w: number; h: number };
type Cast = { window: Box; cab: Box; figs: Record<string, number> };

/** Figures are format-independent (same files in every folder); width/height, feet at the bottom. */
const figs = {
  "ivan-run1": 0.69, "ivan-run2": 0.6, "ivan-climb1": 0.48, "ivan-climb2": 0.45,
  "petr-walk1": 0.51, "petr-walk2": 0.525, "petr-sad": 0.4, "petr-climb": 0.45,
};

/** Office and far-cab variants share their boxes. */
export const craneCast: Partial<Record<CraneFormat, Cast>> = {
  wide: {
    window: { x: 440, y: 394.67, w: 200, h: 130.67 },
    cab: { x: 1426.67, y: 0, w: 360, h: 306.67 },
    figs,
  },
  desk: { window: { x: 230.67, y: 533.33, w: 182.67, h: 140.67 }, cab: { x: 1162.67, y: 84.67, w: 373.33, h: 316 }, figs },
  mid: { window: { x: 180, y: 596, w: 172.67, h: 134 }, cab: { x: 1042, y: 152.67, w: 360, h: 298 }, figs },
  tall: { window: { x: 124.67, y: 998.67, w: 131.33, h: 128 }, cab: { x: 624, y: 347.33, w: 385.33, h: 266.67 }, figs },
};

export const castSrc = (format: CraneFormat, name: string) => `scene-art/barge-v4/${format}/${name}.webp`;
