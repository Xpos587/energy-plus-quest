import { expect, test } from "@playwright/test";

// Exercise the map independently of the concurrently edited shared shell.
for (const [width, height] of [
  [320, 568],
  [390, 844],
  [844, 390],
  [768, 1024],
  [1440, 900],
]) {
  test(`moving roof targets and native pan ${width}x${height}`, async ({
    page,
  }, info) => {
    test.skip(Boolean(info.project.use.hasTouch) && width === 1440,
      "The mobile profile cannot decode the desktop 3600p video; desktop 1440x900 is covered separately.");
    await page.setViewportSize({ width, height });
    await page.route("**/carrier-map-harness", (route) =>
      route.fulfill({
        contentType: "text/html",
        body: `
      <html><head><meta name="viewport" content="width=device-width, initial-scale=1"><style>html,body,#root{margin:0;width:100%;height:100%;overflow:hidden}</style></head><body><div id="root"></div>
      <script type="module">
      import RefreshRuntime from '/@react-refresh';
      RefreshRuntime.injectIntoGlobalHook(window);
      window.$RefreshReg$ = () => {}; window.$RefreshSig$ = () => type => type;
      window.__vite_plugin_react_preamble_installed__ = true;
      const {default: React} = await import('/node_modules/.vite/deps/react.js');
      const {default: {createRoot}} = await import('/node_modules/.vite/deps/react-dom_client.js');
      const {IllustratedCityMap} = await import('/src/components/IllustratedCityMap.tsx');
      const root = createRoot(document.getElementById('root'));
      function render(selectedId) {
        root.render(React.createElement(React.Fragment, null,
          React.createElement(IllustratedCityMap, { selectedId, onSelect: id => { document.body.dataset.selected=id; render(id); } }),
          React.createElement('button', { 'data-cancel-inspection': true, style: {position:'fixed',bottom:0,left:0,zIndex:10}, onClick: () => render(undefined) }, 'Back')));
      }
      render();
      </script></body></html>`,
      }),
    );
    await page.goto("/carrier-map-harness");
    const video = page.locator("[data-city-video]");
    await expect(video).toHaveJSProperty("readyState", 4);
    await expect(page.locator("[data-map-controls]")).toHaveCount(0);
    await video.evaluate((element: HTMLVideoElement) => {
      element.pause();
      element.currentTime = 12;
    });
    await expect
      .poll(() =>
        video.evaluate((element: HTMLVideoElement) => element.seeking),
      )
      .toBe(false);
    const target = page.locator('[data-carrier-choice="crew"]');
    await target.evaluate((element: HTMLButtonElement) => element.focus({ preventScroll: true }));
    await target.evaluate((element: HTMLButtonElement) => element.blur());
    const box = await target.boundingBox();
    expect(Math.min(box?.width ?? 0, box?.height ?? 0)).toBeGreaterThanOrEqual(
      44,
    );
    expect(Math.max(box?.width ?? 0, box?.height ?? 0)).toBeGreaterThanOrEqual(
      85,
    );
    await expect(target).toBeEmpty();
    await expect(target).toHaveCSS("background-color", "rgba(0, 0, 0, 0)");
    const plane = await page.locator("[data-map-surface]").boundingBox();
    expect(plane?.height).toBeGreaterThanOrEqual(height);
    if (width < height) expect(plane?.width).toBeGreaterThan(width);
    const surface = page.locator("[data-map-surface]");
    const originalView = await surface.evaluate(element => (element as HTMLElement).style.transform);
    await target.click();
    await expect(page.locator("body")).toHaveAttribute("data-selected", "crew");
    await expect(page.locator("[data-map-viewport]")).toHaveAttribute("data-map-scale", "2.4");
    const selectedView = await surface.evaluate(element => (element as HTMLElement).style.transform);
    await video.evaluate((element: HTMLVideoElement) => { element.currentTime = 15; });
    await expect.poll(() => surface.evaluate(element => (element as HTMLElement).style.transform)).not.toBe(selectedView);
    const closeup = await target.boundingBox();
    expect((closeup?.x ?? -10000) + (closeup?.width ?? 0) / 2).toBeGreaterThan(0);
    expect((closeup?.x ?? 10000) + (closeup?.width ?? 0) / 2).toBeLessThan(width);
    expect((closeup?.y ?? -10000) + (closeup?.height ?? 0) / 2).toBeGreaterThan(0);
    expect((closeup?.y ?? 10000) + (closeup?.height ?? 0) / 2).toBeLessThan(height);
    if (width === 390 || width === 1440) {
      // A 24fps source must not make the camera freeze between decoded frames.
      const cadence = await page.evaluate(async () => {
        const media = document.querySelector("video")!;
        const surface = document.querySelector<HTMLElement>("[data-map-surface]")!;
        await media.play();
        const samples: string[] = [];
        const start = performance.now();
        await new Promise<void>(resolve => {
          const sample = () => {
            samples.push(surface.style.transform);
            if (performance.now() - start < 400) requestAnimationFrame(sample);
            else resolve();
          };
          requestAnimationFrame(sample);
        });
        media.pause();
        return { frames: samples.length - 1, changes: samples.slice(1).filter((value, index) => value !== samples[index]).length };
      });
      expect(cadence.frames).toBeGreaterThan(10);
      expect(cadence.changes / cadence.frames).toBeGreaterThan(.7);
    }
    await page.mouse.move(width / 2, height / 2);
    await page.mouse.wheel(0, -100);
    await expect.poll(async () => Number(await page.locator("[data-map-viewport]").getAttribute("data-map-scale"))).toBeGreaterThan(2.4);
    await page.locator("[data-cancel-inspection]").click();
    await expect.poll(() => surface.evaluate(element => (element as HTMLElement).style.transform)).toBe(originalView);
    await page.screenshot({ path: `/tmp/carrier-tracking-${width}.png` });
  });
}
