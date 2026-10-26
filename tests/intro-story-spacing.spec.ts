import { expect, test } from "@playwright/test";

test("portrait story keeps the route preview below the reading column", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  await page.locator("[data-intro-enter]").click();
  const story = page.locator('[data-page="0"]');
  const end = await story.locator("p").last().boundingBox();
  const route = await story
    .getByRole("list", { name: "Этапы доставки в игре" })
    .getByRole("listitem")
    .first()
    .boundingBox();
  if (!route || !end) throw new Error("Story and route must be rendered");
  expect(route.y).toBeGreaterThanOrEqual(end.y + end.height + 16);
  await expect(story.getByRole("listitem")).toHaveCount(6);
  await expect(page.locator("[data-intro-next]")).toBeInViewport();
  expect(await page.evaluate(() => document.documentElement.scrollHeight)).toBe(
    844,
  );
});
