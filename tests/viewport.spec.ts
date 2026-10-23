import { expect, test } from "@playwright/test";

test("every scene fits the viewport without hiding content", async ({
  page,
}) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
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
      await button.scrollIntoViewIfNeeded();
      const box = await button.boundingBox();
      expect(box?.height).toBeGreaterThanOrEqual(44);
      expect(
        box?.y,
        (await button.getAttribute("aria-label")) ??
          (await button.textContent()) ??
          "button",
      ).toBeGreaterThanOrEqual(-1);
      expect((box?.y ?? 0) + (box?.height ?? 0)).toBeLessThanOrEqual(
        dimensions.height + 1,
      );
    }
    await page.getByRole("button", { name: action, exact: true }).click();
  }
  await expect(
    page.getByRole("button", { name: "К следующей сцене", exact: true }),
  ).toBeEnabled();
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

test("selection cards stay rounded and portrait results are edge-to-edge", async ({
  page,
}) => {
  await page.goto("/");
  for (const action of [
    "Профессионал",
    "Хор",
    "Лодка",
    "№1",
    "Назад к машинам",
  ]) {
    const panels = page.locator(
      '[data-layout="dialog"] > div:last-child, [data-layout="result"] > [data-carrier], [data-carrier-panel]',
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
      const portraitResult =
        action === "Назад к машинам" &&
        page.viewportSize()!.width <= 900 &&
        page.viewportSize()!.height > page.viewportSize()!.width;
      if (portraitResult) expect(radii).toEqual([0, 0, 0, 0]);
      else if ((await panel.getAttribute("data-carrier-panel")) !== null) {
        expect(Math.min(...radii)).toBeGreaterThanOrEqual(16);
      } else expect(Math.min(...radii)).toBeGreaterThanOrEqual(24);
    }
    await page.getByRole("button", { name: action, exact: true }).click();
  }
});

test("media fills its surface once and progress numerals stay light", async ({
  page,
}) => {
  await page.goto("/");
  const mobileHeader = page.viewportSize()!.width <= 600;
  for (const circle of await page.locator("[data-progress-step] i").all()) {
    if (mobileHeader) {
      await expect(circle).toBeHidden();
      continue;
    }
    await expect(circle).toHaveCSS("line-height", "18px");
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
  const media = await page.locator("[data-city-video]").boundingBox();
  expect(media!.x).toBeGreaterThanOrEqual(map!.x - 1);
  expect(media!.y).toBeGreaterThanOrEqual(map!.y - 1);
  expect(media!.x + media!.width).toBeGreaterThanOrEqual(
    map!.x + map!.width - 1,
  );
  expect(media!.y + media!.height).toBeGreaterThanOrEqual(
    map!.y + map!.height - 1,
  );
  expect(media!.width / media!.height).toBeCloseTo(1440 / 1000, 2);
  await expect(page.locator("[data-city-video]")).toHaveCSS(
    "object-fit",
    "contain",
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

test("edge-to-edge outcomes stay filled when switching phone and desktop", async ({
  page,
}, info) => {
  test.skip(
    info.project.name !== "desktop-chromium",
    "one resize sequence covers the breakpoint transition",
  );
  await page.setViewportSize({ width: 440, height: 956 });
  await page.goto("/");
  for (const name of ["Профессионал", "Хор", "Вязаные носки", "№3"]) {
    await page.getByRole("button", { name, exact: true }).click();
  }
  for (const [width, height] of [
    [440, 956],
    [1725, 998],
    [440, 956],
    [1265, 730],
    [1440, 900],
  ]) {
    await page.setViewportSize({ width, height });
    const scene = page.locator('[data-layout="result"]');
    await expect(scene).toHaveCSS("border-radius", "0px");
    const image = page.locator("[data-outcome-art]:visible");
    await image.evaluate((el: HTMLImageElement) => el.decode());
    await expect(image.locator("..")).toHaveCSS("border-radius", "0px");
    const art = (await image.boundingBox())!;
    const bounds = (await scene.boundingBox())!;
    expect(art.x).toBe(0);
    expect(art.width).toBe(width);
    expect(art.y).toBe(bounds.y);
    expect(bounds.y + bounds.height).toBe(height);
    if (width > 900) expect(art.y + art.height).toBe(height);
    else {
      const panel = scene.locator(":scope > [data-carrier]");
      await expect(panel).toHaveCSS("border-radius", "0px");
      const box = (await panel.boundingBox())!;
      expect(Math.abs(art.y + art.height - box.y)).toBeLessThan(1);
      expect(box.y + box.height).toBe(height);
    }
  }
});

test("mission controls stay outside the city overview", async ({ page }) => {
  await page.goto("/");
  for (const name of ["Профессионал", "Хор", "Фотоаппарат"])
    await page.getByRole("button", { name, exact: true }).click();
  await expect(page.locator("[data-city-video]")).toBeVisible();
  await expect(page.locator("[data-truck-number]")).toHaveCount(0);
  for (const choice of await page.locator("[data-carrier-choice]").all()) {
    await choice.scrollIntoViewIfNeeded();
    const map = (await page.locator("[data-map-surface]").boundingBox())!;
    const control = (await choice.boundingBox())!;
    expect(
      map.x < control.x + control.width &&
        map.x + map.width > control.x &&
        map.y < control.y + control.height &&
        map.y + map.height > control.y,
    ).toBe(false);
    await expect(choice).toBeInViewport();
  }
  await page
    .getByRole("button", { name: "Рассмотреть карту", exact: true })
    .click();
  await expect(page.locator("[data-carrier-panel]")).toBeHidden();
  await page
    .getByRole("button", { name: "Вернуться к выбору", exact: true })
    .click();
  await expect(page.locator("[data-carrier-panel]")).toBeVisible();
});
