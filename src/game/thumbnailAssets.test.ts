import { expect, it, vi } from "vitest";
vi.mock("virtual:thumbnail-images", () => ({
  default: { "assets/full.webp": "assets/thumb.webp" },
}));
import { thumbnailAsset } from "./imageAssets";
it("uses a small summary thumbnail and preserves unknown editable artwork", () => {
  expect(thumbnailAsset("/assets/full.webp")).toBe("/assets/thumb.webp");
  expect(thumbnailAsset("/brand/custom.webp")).toBe("/brand/custom.webp");
});
