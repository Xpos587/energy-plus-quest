import { expect, test, type Locator } from "@playwright/test";

async function centeredIn(feedback: Locator, media: Locator) {
  await expect(feedback).toBeVisible();
  await expect.poll(async () => {
    const [status, area] = await Promise.all([feedback.boundingBox(), media.boundingBox()]);
    if (!status || !area) return Infinity;
    return Math.max(
      Math.abs(status.x + status.width / 2 - area.x - area.width / 2),
      Math.abs(status.y + status.height / 2 - area.y - area.height / 2),
    );
  }).toBeLessThan(1);
}

for (const scene of [
  { id: "compact", pattern: /compact-environment-v(53|54)/ },
  { id: "inventory", pattern: /inventory-master-v16/ },
  { id: "crane", pattern: /barge-v7\/(wide|desk|mid|tall)\/plate/ },
  { id: "lastmile", pattern: /lastmile-family-v1\/revision-28\/choice/ },
]) {
  test(`${scene.id}: loading and retry stay centered in media, including after resize`, async ({ page }, info) => {
    await page.emulateMedia({ reducedMotion: "reduce" });
    let release!: () => void;
    const pending = new Promise<void>(resolve => { release = resolve; });
    await page.route(scene.pattern, async route => { await pending; await route.abort(); });
    try {
      await page.goto(`/scenes.html?scene=${scene.id}&parcel=socks&recipient=khor`, { waitUntil: "domcontentloaded" });
      const condition = page.getByRole("region", { name: "Условие задания", exact: true });
      for (let n = 0; n < 40 && await condition.isVisible(); n++)
        await condition.getByRole("button", { name: /^(Далее|К выбору)$/ }).click();
      await expect(condition).toHaveCount(0);
      const media = page.locator(`[data-world-scene="${scene.id}"]`);
      await centeredIn(page.locator('[data-artwork-status="loading"]'), media);
      release();
      const feedback = page.locator('[data-artwork-status="error"]');
      await centeredIn(feedback, media);
      const retry = feedback.getByRole("button", { name: "Повторить", exact: true });
      expect((await retry.boundingBox())!.height).toBeGreaterThanOrEqual(44);
      await page.screenshot({ path: info.outputPath(`${scene.id}-centered.png`) });
      for (const viewport of [{ width: 320, height: 568 }, { width: 844, height: 390 }, { width: 1440, height: 900 }]) {
        await page.setViewportSize(viewport);
        await centeredIn(feedback, media);
      }
      await page.unroute(scene.pattern);
      await retry.click();
      await expect(page.locator('[data-artwork-status]')).toHaveCount(0);
    } finally { release(); }
  });
}

test("lastmile preview keeps responsive-image retry centered in its media", async ({ page }, info) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.setViewportSize({ width: 390, height: 1000 });
  const pattern = /lastmile-family-v1\/revision-28\/choice-wide/;
  await page.route(pattern, route => route.abort());
  await page.goto("/scenes.html?scene=lastmile&parcel=socks&recipient=khor");
  const condition = page.getByRole("region", { name: "Условие задания", exact: true });
  for (let n = 0; n < 40 && await condition.isVisible(); n++)
    await condition.getByRole("button", { name: /^(Далее|К выбору)$/ }).click();
  const media = page.locator('[data-world-scene="lastmile"]');
  await expect(media).toHaveAttribute("data-artwork-ready", "true");
  await page.locator('[data-hotspot="rover"]').click();
  await expect(page.locator("[data-choice-inspection]")).toBeVisible();
  await expect(media.locator("img").first()).toHaveAttribute("src", /choice-tall/);
  await page.setViewportSize({ width: 1440, height: 900 });
  const feedback = page.locator('[data-artwork-status="error"]');
  await centeredIn(feedback, media);
  await expect(page.locator("[data-choice-inspection]")).toBeVisible();
  await page.screenshot({ path: info.outputPath("lastmile-preview-centered.png") });
  await page.unroute(pattern);
  await feedback.getByRole("button", { name: "Повторить", exact: true }).click();
  await expect(media).toHaveAttribute("data-artwork-ready", "true");
  await expect(page.locator("[data-choice-inspection]")).toBeVisible();
  await expect(page.locator("[data-result-reader]")).toHaveCount(0);
});
