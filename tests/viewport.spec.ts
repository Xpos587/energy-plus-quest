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
      '[data-layout="dialog"] > div:last-child, [data-layout="result"] > [data-carrier], div:has(> div > [data-carrier-choice])',
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
      else expect(Math.min(...radii)).toBeGreaterThanOrEqual(24);
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
  const media = await page.locator("[data-map-media]:visible").boundingBox();
  expect(media!.x).toBeGreaterThanOrEqual(map!.x - 1);
  expect(media!.y).toBeGreaterThanOrEqual(map!.y - 1);
  expect(media!.x + media!.width).toBeLessThanOrEqual(map!.x + map!.width + 1);
  expect(media!.y + media!.height).toBeLessThanOrEqual(
    map!.y + map!.height + 1,
  );
  const format = await page
    .locator("[data-map-media]:visible")
    .getAttribute("data-format");
  expect(media!.width / media!.height).toBeCloseTo(
    format === "mobile" ? 720 / 1088 : 1280 / 788,
    3,
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

test("authored carrier media and all moving trucks fit without UI occlusion", async ({
  page,
}) => {
  await page.goto("/");
  for (const name of ["Профессионал", "Хор", "Фотоаппарат"]) {
    await page.getByRole("button", { name, exact: true }).click();
  }
  const video = page.locator("video[data-map-media]");
  await expect
    .poll(() => video.evaluate((node: HTMLVideoElement) => node.videoWidth))
    .toBeGreaterThan(0);
  const geometry = await video.evaluate((node: HTMLVideoElement) => {
    const box = node.getBoundingClientRect();
    const mobile = node.dataset.format === "mobile";
    // Conservative full-cycle swept envelope from the verified r22 render, including mirrors.
    const bounds = mobile ? [76, 37, 630, 1024] : [370, 31, 839, 724];
    const moving = {
      x: box.x + (bounds[0] / node.videoWidth) * box.width,
      y: box.y + (bounds[1] / node.videoHeight) * box.height,
      right: box.x + (bounds[2] / node.videoWidth) * box.width,
      bottom: box.y + (bounds[3] / node.videoHeight) * box.height,
    };
    // Moving inspection targets intentionally follow the trucks; mission controls must not cover them.
    const buttons = [
      ...document.querySelectorAll("button:not([data-truck-inspect])"),
    ].map((button) => button.getBoundingClientRect());
    const pickup = document
      .querySelector("[data-pickup-label]")!
      .getBoundingClientRect();
    return {
      size: [node.videoWidth, node.videoHeight],
      duration: node.duration,
      ratioError: Math.abs(
        box.width / box.height - node.videoWidth / node.videoHeight,
      ),
      clipped:
        moving.x < 0 ||
        moving.y < 0 ||
        moving.right > innerWidth + 1 ||
        moving.bottom > innerHeight + 1,
      obscured: buttons.some(
        (button) =>
          moving.x < button.right &&
          moving.right > button.x &&
          moving.y < button.bottom &&
          moving.bottom > button.y,
      ),
      pickup: [
        Math.abs((pickup.x - box.x) / box.width - (mobile ? 0.486 : 0.489)),
        Math.abs((pickup.y - box.y) / box.height - (mobile ? 0.3066 : 0.2555)),
      ],
    };
  });
  expect([
    [720, 1088],
    [1280, 788],
  ]).toContainEqual(geometry.size);
  expect(geometry.duration).toBeCloseTo(64, 1);
  expect(geometry.ratioError).toBeLessThan(0.001);
  expect(geometry.clipped).toBe(false);
  expect(geometry.obscured).toBe(false);
  expect(Math.max(...geometry.pickup)).toBeLessThan(0.001);
});
