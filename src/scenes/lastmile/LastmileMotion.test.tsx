import { renderToStaticMarkup } from "react-dom/server";
import { expect, it, vi } from "vitest";

vi.mock("./expandedArtwork", () => ({
  lastmileChoiceArtwork: { width: 2400, height: 1800 },
}));

import { LastmileMotion } from "./LastmileMotion";

it("keeps the static map usable without optional motion layers", () => {
  expect(renderToStaticMarkup(<LastmileMotion />)).toBe("");
});
