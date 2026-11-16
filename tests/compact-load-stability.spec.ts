import { expect, test } from "@playwright/test";

for (const viewport of [{ width: 1440, height: 900 }, { width: 752, height: 877 }, { width: 390, height: 844 }]) {
  test(`compact CSS and geometry stay intact at ${viewport.width}px with normal motion`, async ({ page }, info) => {
    await page.setViewportSize(viewport);
    await page.emulateMedia({ reducedMotion: "no-preference" });
    const errors: string[] = [];
    page.on("pageerror", error => errors.push(error.message));
    await page.goto("/");
    await page.evaluate(() => {
      const scope = "quest-compact-stability";
      localStorage.clear();
      localStorage.setItem("energy-quest-save-v1", JSON.stringify({ version: 1, scope, state: {
        step: "outcome", profile: "professional", recipient: "khor", parcel: "socks", carrier: "express",
      } }));
      localStorage.setItem(`${scope}:intro-seen`, "true");
      localStorage.setItem(`${scope}:remaining`, "true");
    });
    await page.reload();
    const figure = page.locator('[data-world-scene="compact"]');
    await expect(figure.locator("[data-cargo-view]")).toHaveAttribute("data-artwork-ready", "true");
    await expect(figure).toHaveAttribute("class", /\S+/);
    const geometry = await figure.evaluate(async element => {
      const heights: number[] = [];
      for (let frame = 0; frame < 120; frame++) {
        await new Promise(requestAnimationFrame);
        heights.push(element.getBoundingClientRect().height);
      }
      return {
        heights,
        fills: [...element.querySelectorAll("[data-loading-zone]")].map(zone => getComputedStyle(zone).fill),
      };
    });
    expect(Math.min(...geometry.heights)).toBeGreaterThan(100);
    expect(Math.max(...geometry.heights)).toBeLessThanOrEqual(viewport.height);
    expect(Math.max(...geometry.heights) - Math.min(...geometry.heights)).toBeLessThan(2);
    expect(geometry.fills).toHaveLength(5);
    expect(geometry.fills).not.toContain("rgb(0, 0, 0)");
    expect(errors).toEqual([]);
    await page.screenshot({ path: info.outputPath("compact-stable.png") });

    await page.locator('[data-hotspot="place-3"]').click();
    await page.locator("[data-choice-confirm]").click();
    await expect(figure).toHaveAttribute("data-fixed-result", "true");
    await expect(figure).toHaveAttribute("data-camera-detail", "true");
    const plane = figure.locator("[data-world-plane]");
    // Result framing is immediate even when the player has not requested reduced motion.
    await expect(plane).toHaveCSS("transition-duration", "0s");
    expect(await plane.evaluate(element => element.getAnimations().length)).toBe(0);
    await expect(figure.locator("[data-cargo-view]")).toHaveAttribute("data-artwork-ready", "true");
    await page.screenshot({ path: info.outputPath("compact-result-still.png") });
  });
}

test("React Refresh accepts new module instances for the whole scene boundary chain", async ({ page }) => {
  await page.goto("/");
  // Use Vite's actual browser runtime, not a naming/regex approximation of its contract.
  const results = await page.evaluate(async () => {
    const runtime = await import(/* @vite-ignore */ "/@react-refresh");
    const modules = ["components/StageIndicator", "components/QuestShell", "components/SceneBriefing", "scenes/ScenesGame"];
    const results = [];
    for (const name of modules) {
      const before = await import(/* @vite-ignore */ `/src/${name}.tsx?refresh-check=before`);
      const after = await import(/* @vite-ignore */ `/src/${name}.tsx?refresh-check=after`);
      results.push({ name, incompatible: runtime.validateRefreshBoundaryAndEnqueueUpdate(name, before, after) ?? null });
    }
    return results;
  });
  expect(results.every(result => result.incompatible === null), JSON.stringify(results)).toBe(true);
});
