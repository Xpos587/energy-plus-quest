import { expect, type Page, test } from "@playwright/test";

async function expectNoPageScroll(page: Page) {
  const dimensions = await page.evaluate(() => ({
    clientHeight: document.documentElement.clientHeight,
    clientWidth: document.documentElement.clientWidth,
    scrollHeight: document.documentElement.scrollHeight,
    scrollWidth: document.documentElement.scrollWidth,
  }));

  expect(dimensions.scrollWidth).toBeLessThanOrEqual(
    dimensions.clientWidth + 1,
  );
  expect(dimensions.scrollHeight).toBeLessThanOrEqual(
    dimensions.clientHeight + 1,
  );
}

async function expectControlsInsideViewport(page: Page) {
  const controls = page.getByRole("button").filter({ visible: true });
  for (let index = 0; index < (await controls.count()); index += 1) {
    await expect(controls.nth(index)).toBeInViewport();
  }
}

async function expectImagesComplete(page: Page) {
  expect(
    await page
      .locator("img")
      .evaluateAll((images) =>
        images.every(
          (image) =>
            (image as HTMLImageElement).complete &&
            (image as HTMLImageElement).naturalWidth > 0,
        ),
      ),
  ).toBe(true);
}

async function expectScreenFits(page: Page) {
  await expectControlsInsideViewport(page);
  await expectNoPageScroll(page);
  await expectImagesComplete(page);
}

async function playReviewPath(page: Page) {
  await page.goto("/");
  await page.getByRole("button", { name: /Начать игру/ }).click();
  await page.getByRole("button", { name: /Профессионал/ }).click();
  await page.getByRole("button", { name: /Альва/ }).click();
  await page.getByRole("button", { name: /Фотоаппарат/ }).click();
  await expect(
    page.getByRole("heading", { name: "Выберите транспорт для подарка" }),
  ).toBeVisible();
}

test("keeps the playable route inside one viewport", async ({ page }) => {
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: /Доставляем радость/ }),
  ).toBeVisible();
  await expectScreenFits(page);

  await page.getByRole("button", { name: /Начать игру/ }).click();
  await expectScreenFits(page);
  await page.getByRole("button", { name: /Профессионал/ }).click();
  await expectScreenFits(page);
  await page.getByRole("button", { name: /Альва/ }).click();
  await expectScreenFits(page);
  await page.getByRole("button", { name: /Фотоаппарат/ }).click();
  await expectScreenFits(page);

  const carrierControls = page.locator(
    "[data-carrier-hotspot], [data-carrier-choice], [data-express-control]",
  );
  for (let index = 0; index < (await carrierControls.count()); index += 1) {
    const box = await carrierControls.nth(index).boundingBox();
    expect(box).not.toBeNull();
    expect(box?.width ?? 0).toBeGreaterThanOrEqual(44);
    expect(box?.height ?? 0).toBeGreaterThanOrEqual(44);
  }

  for (let number = 1; number <= 4; number += 1) {
    const hotspot = page.locator(`[data-truck="truck-${number}"]`);
    const badge = hotspot.locator("[data-truck-number]");
    const [hotspotBox, badgeBox] = await Promise.all([
      hotspot.boundingBox(),
      badge.boundingBox(),
    ]);
    expect(hotspotBox).not.toBeNull();
    expect(badgeBox).not.toBeNull();
    const badgeCenter = {
      x: (badgeBox?.x ?? 0) + (badgeBox?.width ?? 0) / 2,
      y: (badgeBox?.y ?? 0) + (badgeBox?.height ?? 0) / 2,
    };
    expect(badgeCenter.x).toBeGreaterThanOrEqual(hotspotBox?.x ?? 0);
    expect(badgeCenter.x).toBeLessThanOrEqual(
      (hotspotBox?.x ?? 0) + (hotspotBox?.width ?? 0),
    );
    expect(badgeCenter.y).toBeGreaterThanOrEqual(hotspotBox?.y ?? 0);
    expect(badgeCenter.y).toBeLessThanOrEqual(
      (hotspotBox?.y ?? 0) + (hotspotBox?.height ?? 0),
    );
  }

  await page.getByRole("button", { name: "Машина №2", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Близко — не значит быстро" }),
  ).toBeVisible();
  await expectScreenFits(page);

  await page.getByRole("button", { name: "Назад к машинам" }).click();
  await expectScreenFits(page);
  await page.getByRole("button", { name: "Назад", exact: true }).click();
  await expectScreenFits(page);
});

test("shows visible keyboard focus on carrier controls", async ({ page }) => {
  await playReviewPath(page);
  const firstTruck = page.getByRole("button", {
    name: "Машина №1",
    exact: true,
  });
  await firstTruck.focus();
  await expect(firstTruck).toBeFocused();
  expect(
    await firstTruck.evaluate((element) => {
      const style = getComputedStyle(element);
      return style.outlineStyle !== "none" || style.boxShadow !== "none";
    }),
  ).toBe(true);
});
