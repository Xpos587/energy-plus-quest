import { afterEach, describe, expect, it, vi } from "vitest";
import { registerGameCache } from "./offlineCache";

afterEach(() => {
  vi.unstubAllEnvs();
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
  delete (navigator as unknown as { serviceWorker?: unknown }).serviceWorker;
});

describe("optional offline registration", () => {
  it("registers a nested production scope without reusing the browser's SW cache", () => {
    vi.stubEnv("PROD", true);
    vi.stubEnv("BASE_URL", "/specprojects/game/");
    const register = vi.fn().mockResolvedValue({});
    vi.stubGlobal("isSecureContext", true);
    vi.spyOn(document, "readyState", "get").mockReturnValue("complete");
    Object.defineProperty(navigator, "serviceWorker", {
      configurable: true,
      value: { register },
    });
    registerGameCache();
    expect(register).toHaveBeenCalledWith(
      new URL("/specprojects/game/quest-cache.js", document.baseURI).href,
      {
        scope: new URL("/specprojects/game/", document.baseURI).href,
        updateViaCache: "none",
      },
    );
  });
});
