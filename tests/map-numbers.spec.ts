import { expect, type Page, test } from "@playwright/test";

async function openMap(page: Page) {
  await page.goto("/");
  for (const name of [/Профессионал/, /Альва/, /Фотоаппарат/])
    await page.getByRole("button", { name }).click();
}

for (const viewport of [
  { width: 320, height: 568 },
  { width: 390, height: 844 },
  { width: 1440, height: 900 },
]) {
  test(`four fixed carrier buttons remain accessible at ${viewport.width}`, async ({
    page,
  }) => {
    await page.setViewportSize(viewport);
    await openMap(page);
    for (let number = 1; number <= 4; number++) {
      const choice = page.getByRole("button", {
        name: `№${number}`,
        exact: true,
      });
      await expect(choice).toHaveAttribute("type", "button");
      await choice.scrollIntoViewIfNeeded();
      const box = (await choice.boundingBox())!;
      expect(box.width).toBeGreaterThanOrEqual(44);
      expect(box.height).toBeGreaterThanOrEqual(44);
    }
    // The generated video does not follow the former canvas marker trajectories.
    await expect(page.locator("[data-truck-number]")).toHaveCount(0);
    await expect(page.getByRole("dialog")).toHaveCount(0);
  });
}

test("number selection preserves carrier mapping without an invisible map target", async ({
  page,
}) => {
  await openMap(page);
  await page.getByRole("button", { name: "№3", exact: true }).click();
  await expect(
    page.locator('[data-layout="result"][data-carrier="crew"]'),
  ).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "Два водителя лучше одного" }),
  ).toBeVisible();
});

test("carrier choices stay fixed during playback and keyboard-selectable", async ({
  page,
}) => {
  await openMap(page);
  const target = page.getByRole("button", { name: "№2", exact: true });
  await target.scrollIntoViewIfNeeded();
  const first = await target.boundingBox();
  await page.waitForTimeout(300);
  expect(await target.boundingBox()).toEqual(first);
  await target.focus();
  await target.press("Enter");
  await expect(
    page.locator('[data-layout="result"][data-carrier="near"]'),
  ).toBeVisible();
});
