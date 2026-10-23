import { expect, it, vi, afterEach } from "vitest";
import { observedSlowTransfer } from "./network";
afterEach(() => vi.unstubAllGlobals());
it("uses actual slow transfers when connection hints are unavailable, ignoring cached resources", () => {
  vi.stubGlobal("performance", {
    getEntriesByType: () => [
      { encodedBodySize: 69000, transferSize: 69300, duration: 4000 },
    ],
  });
  expect(observedSlowTransfer()).toBe(true);
  vi.stubGlobal("performance", {
    getEntriesByType: () => [
      { encodedBodySize: 69000, transferSize: 0, duration: 4000 },
    ],
  });
  expect(observedSlowTransfer()).toBe(false);
});
