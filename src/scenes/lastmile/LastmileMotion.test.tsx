import { renderToStaticMarkup } from "react-dom/server";
import { expect, it, vi } from "vitest";

vi.mock("./expandedArtwork", () => ({
  lastmileChoiceArtwork: {
    wide: { width: 2056, height: 1841 },
    tall: { width: 1664, height: 1952 },
  },
}));

import { LastmileMotion } from "./LastmileMotion";

it.each(["wide", "tall"] as const)("keeps the static map usable without optional %s motion layers", composition => {
  expect(renderToStaticMarkup(<LastmileMotion composition={composition} />)).toBe("");
});
