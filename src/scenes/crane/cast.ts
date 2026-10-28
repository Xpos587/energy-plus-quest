/** Hand-drawn character variants for the formats restyled so far (see epq-gen storyboard). */
import type { CraneFormat } from "./artwork";

type Box = { x: number; y: number; w: number; h: number };
type Cast = { window: Box; cab: Box; figs: Record<string, number> };

/** Office and far-cab variants share their boxes; figures store width/height, feet at the bottom. */
export const craneCast: Partial<Record<CraneFormat, Cast>> = {
  wide: {
    window: { x: 440, y: 394.67, w: 200, h: 130.67 },
    cab: { x: 1426.67, y: 0, w: 360, h: 306.67 },
    figs: {
      "ivan-run1": 0.69, "ivan-run2": 0.6, "ivan-climb1": 0.48, "ivan-climb2": 0.45,
      "petr-walk1": 0.51, "petr-walk2": 0.525, "petr-sad": 0.4, "petr-climb": 0.45,
    },
  },
};

export const castSrc = (format: CraneFormat, name: string) => `scene-art/barge-v4/${format}/${name}.webp`;
