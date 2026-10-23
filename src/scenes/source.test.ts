import { describe, expect, it } from "vitest";
import { source } from "./source";
import { implementationText } from "./implementationText";

describe("retained scene implementation text", () => {
  it("preserves current implementation copy and existing proofreading", () => {
    const corrected = new Set([
      "p223",
      "p290",
      "p444",
      "p469",
      "p487",
      "p554",
      "p558",
    ]);
    for (const [id, text] of Object.entries(implementationText)) {
      if (!corrected.has(id))
        expect(source(id)).toBe(text);
    }
    expect(source("p223")).toContain("сломалась, и пришлось");
    expect(source("p290")).toContain("грузами и защитят");
    expect(source("p444")).toContain("– не каждый день");
    expect(source("p469")).toContain("выручил вас, вовремя погрузив подарок");
    expect(source("p487")).toContain("«Газпромнефть-снабжение»");
    expect(source("p554")).toMatch(/\?$/);
    expect(source("p558")).toMatch(/^Результат: Вертолет/);
  });
  it("rejects a missing source instead of displaying empty copy", () => {
    expect(() => source("missing")).toThrow("missing");
  });
});
