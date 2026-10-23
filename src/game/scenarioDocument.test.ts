import { describe, expect, it } from "vitest";
import { scenarioParagraph } from "./scenarioDocument";

describe("canonical scenario column boundaries", () => {
  it("allows the exact approved player result", () => {
    expect(scenarioParagraph("4264BB8C")).toBe("Два водителя лучше одного!");
  });
  it("rejects visualization and score blocks as player text", () => {
    expect(() => scenarioParagraph("63530BEA")).toThrow("is visual, not text");
    expect(() => scenarioParagraph("78319BED")).toThrow("is scores, not text");
  });
  it("rejects missing blocks", () => {
    expect(() => scenarioParagraph("missing")).toThrow("Missing canonical scenario block");
  });
});
