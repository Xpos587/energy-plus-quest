import { expect, test } from "@playwright/test";

test("portrait story keeps the parcel separate from the reading column", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  await page.locator("[data-intro-enter]").click();
  const story = page.locator('[data-page="0"]');
  const paragraphs = story.locator("p");
  const art = story.locator("img");
  const end = await paragraphs.last().boundingBox();
  const image = await art.boundingBox();
  if (!image || !end) throw new Error("Story and parcel must be rendered");
  expect(image.y).toBeGreaterThanOrEqual(end.y + end.height + 16);
  await expect(page.locator("[data-intro-next]")).toBeInViewport();
  expect(await page.evaluate(() => document.documentElement.scrollHeight)).toBe(
    844,
  );
});
