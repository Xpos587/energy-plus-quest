import { expect, test } from "@playwright/test";

for (const viewport of [
  { width: 320, height: 568 },
  { width: 390, height: 844 },
  { width: 1440, height: 900 },
]) {
  test(`map has noninteractive numbers, no connectors or model at ${viewport.width}`, async ({
    page,
  }) => {
    await page.setViewportSize(viewport);
    await page.goto("/");
    for (const name of [/Профессионал/, /Альва/, /Фотоаппарат/])
      await page.getByRole("button", { name }).click();
    await expect(page.locator("[data-truck-number]")).toHaveCount(4);
    await expect(page.locator("[data-truck-number]").first()).toHaveCSS(
      "font-size",
      "13px",
    );
    await expect(
      page.locator("[aria-label='Карта доступных перевозчиков'] svg line"),
    ).toHaveCount(0);
    await expect(page.getByRole("dialog")).toHaveCount(0);
    await expect(page.getByRole("button", { name: /Рассмотреть/ })).toHaveCount(
      0,
    );
    const box = await page.locator("[data-truck-number]").first().boundingBox();
    await page.mouse.click(box!.x + box!.width / 2, box!.y + box!.height / 2);
    await expect(page.getByRole("dialog")).toHaveCount(0);
    await expect(
      page.getByRole("button", {
        name: "Подобрать автоматически",
        exact: true,
      }),
    ).toBeVisible();
  });
}

test("paused trailer badges do not drift after a seek", async ({ page }) => {
  await page.goto("/");
  for (const name of [/Профессионал/, /Альва/, /Фотоаппарат/])
    await page.getByRole("button", { name }).click();
  await page.locator("video").evaluate(async (video: HTMLVideoElement) => {
    video.pause();
    await new Promise<void>(resolve => {
      video.addEventListener("seeked", () => resolve(), { once: true });
      video.currentTime = 31.5;
    });
  });
  // The scenario intentionally retries autoplay on canplay after a seek.
  await page.waitForTimeout(200);
  await page.locator("video").evaluate((video: HTMLVideoElement) => video.pause());
  await page.waitForTimeout(100);
  const positions = () => page.locator("[data-truck-number]").evaluateAll(nodes =>
    nodes.map(node => [(node as HTMLElement).style.left, (node as HTMLElement).style.top]));
  const first = await positions();
  await page.waitForTimeout(500);
  expect(await positions()).toEqual(first);
});
