import { expect, test } from "@playwright/test";

test("embedded browser chrome resize keeps the header and all actions reachable", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 700 });
  await page.goto("/");
  expect(
    (await page.locator("header").boundingBox())!.height,
  ).toBeLessThanOrEqual(76);
  await expect(page.locator("[data-progress-caption]")).toHaveText(
    "Перевозчик",
  );
  await expect(page.locator("[data-progress-count]")).toHaveText("1 / 5");
  const segments = page.locator("[data-progress-step]");
  await expect(segments).toHaveCount(5);
  for (const segment of await segments.all()) {
    await expect(segment).toHaveCSS("height", "4px");
    await expect(segment.locator("i")).toBeHidden();
  }
  await expect(
    page.locator('[data-progress-step][aria-current="step"]'),
  ).toHaveCSS("background-color", "rgb(255, 85, 0)");
  for (const height of [560, 700, 480, 844]) {
    await page.setViewportSize({ width: 390, height });
    const bounds = await page.locator("#root > div").boundingBox();
    expect(bounds?.height).toBe(height);
    await expect(
      page.getByRole("button", { name: "Профессионал", exact: true }),
    ).toBeInViewport();
  }
  await page.getByRole("button", { name: "Профессионал", exact: true }).click();
  await page.getByRole("button", { name: "Альва", exact: true }).click();
  await page.getByRole("button", { name: "Фотоаппарат", exact: true }).click();
  for (const [width, height] of [
    [390, 560],
    [320, 480],
    [700, 390],
    [390, 700],
  ]) {
    await page.setViewportSize({ width, height });
    const map = await page.locator('[data-mode="live"]').boundingBox();
    expect(map?.height).toBeGreaterThanOrEqual(160);
    for (const name of [
      "Назад",
      "№1",
      "№2",
      "№3",
      "№4",
      "Подобрать автоматически",
    ]) {
      const button = page.getByRole("button", { name, exact: true });
      await button.scrollIntoViewIfNeeded();
      await expect(button).toBeInViewport({ ratio: 0.99 });
    }
    expect(
      await page.evaluate(() => document.documentElement.scrollWidth),
    ).toBeLessThanOrEqual(width);
    expect(
      await page.evaluate(() => document.documentElement.scrollHeight),
    ).toBeLessThanOrEqual(height);
  }
  await page
    .getByRole("button", { name: "Подобрать автоматически", exact: true })
    .click();
  await page.setViewportSize({ width: 320, height: 480 });
  const back = page.getByRole("button", {
    name: "Назад к машинам",
    exact: true,
  });
  await back.scrollIntoViewIfNeeded();
  await expect(back).toBeInViewport({ ratio: 0.99 });
  await back.click();
  await expect(
    page.getByRole("button", { name: "№1", exact: true }),
  ).toBeVisible();
});

test("simulated safe-area insets keep logos and controls clear of cutouts", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 700 });
  await page.goto("/");
  await page.evaluate(() => {
    document.documentElement.style.setProperty("--safe-area-top", "24px");
    document.documentElement.style.setProperty("--safe-area-bottom", "34px");
  });
  const header = await page.locator("header").boundingBox();
  expect(header?.y).toBeGreaterThanOrEqual(24);
  for (const choice of ["professional", "alva", "camera"]) {
    await page.locator(`[data-choice="${choice}"]`).click();
  }
  const auto = page.getByRole("button", {
    name: "Подобрать автоматически",
    exact: true,
  });
  await auto.scrollIntoViewIfNeeded();
  const box = await auto.boundingBox();
  expect(box!.y + box!.height).toBeLessThanOrEqual(700 - 34);
});

test("mobile card labels do not stick to artwork or screen headings", async ({
  page,
}) => {
  for (const width of [320, 390]) {
    await page.setViewportSize({ width, height: 560 });
    await page.goto("/");
    for (const choice of ["professional", "alva", "camera"]) {
      const spacing = await page.evaluate(() => {
        const heading = document.querySelector("h2")!.getBoundingClientRect();
        const cards = [...document.querySelectorAll("[data-choice]")];
        return {
          heading: cards[0].getBoundingClientRect().top - heading.bottom,
          labels: cards.map((card) => {
            const image = card.querySelector("img")!.getBoundingClientRect();
            const text = card
              .querySelector("[data-role-part=title]")!
              .getBoundingClientRect();
            return text.left - image.right;
          }),
        };
      });
      expect(spacing.heading).toBeGreaterThanOrEqual(16);
      expect(spacing.labels.every((gap) => gap >= 14)).toBe(true);
      await page.locator(`[data-choice="${choice}"]`).click();
    }
  }
});

test("warehouse remains described in the video without interactive overlays", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 700 });
  await page.goto("/");
  for (const choice of ["professional", "alva", "camera"]) {
    await page.locator(`[data-choice="${choice}"]`).click();
  }
  const video = page.locator("[data-city-video]");
  await expect(video).toHaveAccessibleName(
    "Город, склад и четыре движущихся грузовика",
  );
  await expect(page.locator('[data-mode="live"]')).toBeInViewport({ ratio: 1 });
  expect((await video.boundingBox())!.width).toBeGreaterThanOrEqual(390);
  await expect(page.locator("[data-pickup-label]")).toHaveCount(0);
  await expect(
    page.getByRole("button", { name: "Склад", exact: true }),
  ).toHaveCount(0);
});
