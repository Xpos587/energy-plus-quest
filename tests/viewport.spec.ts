import { expect, test } from "@playwright/test";

test("every scene fits the viewport without hiding content", async ({
  page,
}) => {
  await page.goto("/");
  for (const action of [
    "Профессионал",
    "Хор",
    "Лодка",
    "№1",
    "Назад к машинам",
    "№2",
    "Назад к машинам",
    "№3",
    "Назад к машинам",
    "Подобрать автоматически",
  ]) {
    await page.evaluate(() => document.fonts.ready);
    const dimensions = await page.evaluate(() => ({
      width: innerWidth,
      height: innerHeight,
      scrollWidth: document.documentElement.scrollWidth,
      scrollHeight: document.documentElement.scrollHeight,
    }));
    expect(dimensions.scrollWidth).toBeLessThanOrEqual(dimensions.width + 1);
    expect(dimensions.scrollHeight).toBeLessThanOrEqual(dimensions.height + 1);
    for (const button of await page.getByRole("button").all()) {
      const box = await button.boundingBox();
      expect(box?.height).toBeGreaterThanOrEqual(44);
      expect(box?.y).toBeGreaterThanOrEqual(-1);
      expect((box?.y ?? 0) + (box?.height ?? 0)).toBeLessThanOrEqual(
        dimensions.height + 1,
      );
    }
    await page.getByRole("button", { name: action, exact: true }).click();
  }
  await expect(
    page.getByRole("button", { name: "К следующей сцене", exact: true }),
  ).toBeDisabled();
  await expect(
    page.getByText("Продолжение пока недоступно", { exact: true }),
  ).toHaveCount(0);
  await expect(page.locator('[aria-current="step"] > span')).toHaveText(
    "Перевозчик",
  );
  await expect(page.locator('[aria-current="step"] i')).toHaveCSS(
    "color",
    "rgb(255, 255, 255)",
  );
});

test("scene panels retain their rounded corners", async ({ page }) => {
  await page.goto("/");
  for (const action of [
    "Профессионал",
    "Хор",
    "Лодка",
    "№1",
    "Назад к машинам",
  ]) {
    const panels = page.locator(
      '[data-layout="dialog"] > div:last-child, [data-layout="result"], div:has(> div > [data-carrier-choice])',
    );
    await expect(panels).toHaveCount(1);
    for (const panel of await panels.all()) {
      const radii = await panel.evaluate((el) => {
        const s = getComputedStyle(el);
        return [
          s.borderTopLeftRadius,
          s.borderTopRightRadius,
          s.borderBottomLeftRadius,
          s.borderBottomRightRadius,
        ].map(parseFloat);
      });
      expect(Math.min(...radii)).toBeGreaterThanOrEqual(24);
    }
    await page.getByRole("button", { name: action, exact: true }).click();
  }
});

test("media fills its surface once and progress numerals stay light", async ({
  page,
}) => {
  await page.goto("/");
  const numeral = page.locator('[aria-current="step"] i');
  await expect(numeral).toHaveCSS("font-weight", "400");
  await expect(numeral).toHaveCSS("line-height", "18px");
  for (const circle of await page.locator("[data-progress-step] i").all()) {
    await expect(circle).toHaveCSS("width", "28px");
    await expect(circle).toHaveCSS("height", "28px");
    await expect(circle).toHaveCSS("font-size", "18px");
    await expect(circle).toHaveCSS("font-weight", "400");
    const centered = await circle.evaluate((el) => {
      const box = el.getBoundingClientRect();
      const glyph = el.firstElementChild!.getBoundingClientRect();
      return [
        Math.abs(glyph.x + glyph.width / 2 - box.x - box.width / 2),
        Math.abs(glyph.y + glyph.height / 2 - box.y - box.height / 2),
      ];
    });
    expect(Math.max(...centered)).toBeLessThanOrEqual(1);
  }
  for (const action of ["Профессионал", "Хор", "Лодка"]) {
    await page.getByRole("button", { name: action, exact: true }).click();
  }
  const map = await page.locator('[data-mode="live"]').boundingBox();
  for (const marker of await page.locator("[data-truck-number]").all()) {
    const box = (await marker.boundingBox())!;
    expect(box.x).toBeGreaterThanOrEqual(map!.x);
    expect(box.y).toBeGreaterThanOrEqual(map!.y);
    expect(box.x + box.width).toBeLessThanOrEqual(map!.x + map!.width);
    expect(box.y + box.height).toBeLessThanOrEqual(map!.y + map!.height);
  }
  const media = await page.locator("[data-map-media]:visible").boundingBox();
  expect(media!.x).toBeLessThanOrEqual(map!.x + 1);
  expect(media!.x + media!.width).toBeGreaterThanOrEqual(
    map!.x + map!.width - 1,
  );
  await page.getByRole("button", { name: "№1", exact: true }).click();
  await expect(page.locator('[data-layout="result"]')).toHaveCSS(
    "background-image",
    "none",
  );
  const image = page.locator("[data-outcome-art]:visible");
  await expect(image).toHaveCount(1);
  await expect(image).toHaveCSS("object-fit", "cover");
  const background = await image.evaluate(
    (el) => getComputedStyle(el.parentElement!, "::before").content,
  );
  expect(background).toBe("none");
});
