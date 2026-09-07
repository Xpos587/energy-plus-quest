import { expect, type Page, test } from "@playwright/test";

async function expectResponsive(page: Page) {
  await page.evaluate(() => document.fonts.ready);
  await page.waitForFunction(() =>
    [...document.images]
      .filter((image) => image.getClientRects().length > 0)
      .every((image) => image.complete && image.naturalWidth > 0),
  );
  const failures = await page.evaluate(() => {
    const issues: string[] = [];
    if (document.documentElement.scrollHeight > innerHeight + 1)
      issues.push("vertical page overflow");
    if (document.documentElement.scrollWidth > innerWidth + 1)
      issues.push("horizontal page overflow");
    for (const element of document.querySelectorAll<HTMLElement>(
      'button, h1, h2, p, nav span, [data-role-part="title"]',
    )) {
      if (!element.getClientRects().length) continue;
      const box = element.getBoundingClientRect();
      if (box.left < -1 || box.right > innerWidth + 1)
        issues.push(`horizontal clipping: ${element.textContent}`);
      if (
        element.scrollWidth > element.clientWidth + 1 ||
        element.scrollHeight > element.clientHeight + 1
      )
        issues.push(`text overflow: ${element.textContent}`);
      for (
        let parent = element.parentElement;
        parent;
        parent = parent.parentElement
      ) {
        const style = getComputedStyle(parent);
        if (["hidden", "clip"].includes(style.overflowY)) {
          const bounds = parent.getBoundingClientRect();
          if (box.bottom > bounds.bottom + 1 || box.top < bounds.top - 1)
            issues.push(`vertical clipping: ${element.textContent}`);
        }
      }
    }
    for (const element of document.querySelectorAll<HTMLElement>(
      '[data-layout="result"] > div, [data-layout="dialog"] > div',
    )) {
      if (
        getComputedStyle(element).overflowY === "auto" &&
        element.scrollHeight > element.clientHeight + 1
      )
        issues.push("inner panel scrolling");
    }
    return issues;
  });
  expect(failures).toEqual([]);
  for (const button of await page.getByRole("button").all()) {
    await button.evaluate((element) =>
      element.scrollIntoView({ block: "center", inline: "nearest" }),
    );
    await expect(button).toBeInViewport({ ratio: 0.99 });
    const box = await button.boundingBox();
    expect(box?.height).toBeGreaterThanOrEqual(44);
  }
}

async function startRoute(page: Page, recipient = "alva", parcel = "camera") {
  await page.goto("/");
  await page.locator('[data-choice="professional"]').click();
  await page.locator(`[data-choice="${recipient}"]`).click();
  await page.locator(`[data-choice="${parcel}"]`).click();
}

test("responsive route keeps artwork complete and controls reachable", async ({
  page,
}) => {
  await page.goto("/");
  await expectResponsive(page);
  for (const choice of ["professional", "khor", "camera"]) {
    await expectResponsive(page);
    for (const image of await page.locator("[data-choice] img").all()) {
      await expect(image).toHaveCSS("object-fit", "contain");
      await expect(image).toHaveCSS("transform", "none");
    }
    await page.locator(`[data-choice="${choice}"]`).click();
  }
  await expectResponsive(page);
  for (const badge of await page.locator("[data-truck-number]").all()) {
    await badge.scrollIntoViewIfNeeded();
    await expect(badge).toBeInViewport({ ratio: 0.99 });
  }
  await page.getByRole("button", { name: "Назад", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Что будет в посылке?" }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Лодка", exact: true }).click();
  for (const control of ["№1", "№2", "№3", "№4", "Подобрать автоматически"]) {
    await page.getByRole("button", { name: control, exact: true }).click();
    await expectResponsive(page);
    const image = page.locator("[data-outcome-art]:visible");
    await expect(image).toHaveCSS("object-fit", "cover");
    await expect(image).toHaveCSS("transform", "none");
    const box = await image.boundingBox();
    expect(box?.width).toBeGreaterThanOrEqual(
      Math.min(280, (page.viewportSize()?.width ?? 0) - 32),
    );
    expect(box?.height).toBeGreaterThan(100);
    const scoreTops = await page
      .locator("[data-score-key] strong")
      .evaluateAll((nodes) =>
        nodes.map((node) => node.getBoundingClientRect().top),
      );
    expect(Math.max(...scoreTops) - Math.min(...scoreTops)).toBeLessThanOrEqual(
      1,
    );
    await expect(page.getByText(/Хор получит лодку/)).toBeVisible();
    await page.getByRole("button", { name: "Назад к машинам" }).click();
  }
});

test("all personalization combinations remain readable on a short phone", async ({
  page,
}, info) => {
  test.skip(
    info.project.name !== "iphone-se-chromium",
    "Exhaustive combinations on short phone",
  );
  test.setTimeout(180_000);
  for (const recipient of ["alva", "khor", "arseniy"]) {
    for (const parcel of ["camera", "socks", "boat"]) {
      await startRoute(page, recipient, parcel);
      for (const control of ["№1", "№2", "№3", "Подобрать автоматически"]) {
        await page.getByRole("button", { name: control, exact: true }).click();
        await expectResponsive(page);
        const body = page
          .locator('[data-layout="result"] p')
          .filter({ hasText: "получит" });
        expect(
          parseFloat(
            await body.evaluate(
              (element) => getComputedStyle(element).fontSize,
            ),
          ),
        ).toBeGreaterThanOrEqual(16);
        await page.getByRole("button", { name: "Назад к машинам" }).click();
      }
    }
  }
});

test("meeting cleanup and readable type survive responsive layouts", async ({
  page,
}) => {
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: "Кто отправится в путь?" }),
  ).toBeVisible();
  await expect(page.getByRole("button", { name: "Начать игру" })).toHaveCount(
    0,
  );
  for (const [action, current] of [
    ["Профессионал", "Перевозчик"],
    ["Хор", "Перевозчик"],
    ["Фотоаппарат", "Перевозчик"],
    ["№2", "Перевозчик"],
  ]) {
    const sizes = await page
      .locator("p")
      .filter({
        hasText: /У логистов|Сегодня вам|Выберите одну|Перевозчик выбран/,
      })
      .evaluateAll((elements) =>
        elements.map((element) =>
          parseFloat(getComputedStyle(element).fontSize),
        ),
      );
    expect(sizes.every((size) => size >= 16)).toBe(true);
    await page.getByRole("button", { name: action, exact: true }).click();
    const nav = page.getByRole("navigation", { name: "Этапы доставки" });
    await expect(nav.locator("[data-progress-step]")).toHaveCount(5);
    await expect(nav.locator('[aria-current="step"] > span')).toHaveText(
      current,
    );
    expect(
      await nav
        .locator("span")
        .evaluateAll((elements) =>
          elements.every(
            (element) => parseFloat(getComputedStyle(element).fontSize) >= 12,
          ),
        ),
    ).toBe(true);
    await expect(
      page.locator('[data-choice] b, [data-choice] [data-role-part="action"]'),
    ).toHaveCount(0);
    await expect(
      page.getByText(/Северный олень Хор|с языка хантов|самец оленя/),
    ).toHaveCount(0);
  }
  for (const button of await page.getByRole("button").all())
    expect(
      parseFloat(
        await button.evaluate((element) => getComputedStyle(element).fontSize),
      ),
    ).toBeGreaterThanOrEqual(16);
  for (const label of ["Энергия", "Эмпатия", "Эффективность"])
    expect(
      parseFloat(
        await page
          .getByText(label, { exact: true })
          .evaluate((element) => getComputedStyle(element).fontSize),
      ),
    ).toBeGreaterThanOrEqual(14);
});

test("keyboard focus reaches carrier controls including Back", async ({
  page,
}) => {
  await startRoute(page);
  await page.keyboard.press("Tab");
  await expect(
    page.getByRole("button", { name: "Назад", exact: true }),
  ).toBeFocused();
  await page.keyboard.press("Tab");
  const first = page.getByRole("button", { name: "№1", exact: true });
  await expect(first).toBeFocused();
  expect(
    await first.evaluate((element) => getComputedStyle(element).outlineStyle),
  ).not.toBe("none");
});

test("media meets card edges and desktop map fills its scene", async ({
  page,
}) => {
  await page.goto("/");
  const scene = await page.locator('[data-layout="dialog"]').boundingBox();
  expect(scene!.y + scene!.height).toBeGreaterThanOrEqual(
    page.viewportSize()!.height - 1,
  );
  const gaps = await page.locator("[data-choice]").evaluateAll((cards) =>
    cards.map((card) => {
      const c = card.getBoundingClientRect();
      const image = card.querySelector("img")!.getBoundingClientRect();
      return {
        left: image.left - c.left,
        top: image.top - c.top,
        ratio: image.width / image.height,
      };
    }),
  );
  for (const gap of gaps) {
    expect(gap.left).toBeLessThanOrEqual(2);
    expect(gap.top).toBeLessThanOrEqual(2);
    expect(gap.ratio).toBeCloseTo(0.8, 2);
  }
  await page.getByRole("button", { name: "Профессионал", exact: true }).click();
  if (page.viewportSize()!.width >= 780) {
    const tops = await page
      .locator("[data-choice]")
      .evaluateAll((nodes) =>
        nodes.map((node) => node.getBoundingClientRect().top),
      );
    expect(Math.max(...tops) - Math.min(...tops)).toBeLessThanOrEqual(1);
  }
  await page.getByRole("button", { name: "Хор", exact: true }).click();
  await page.getByRole("button", { name: "Лодка", exact: true }).click();
  const map = await page.locator('[data-mode="live"]').boundingBox();
  expect(map!.width).toBeGreaterThan(150);
  expect(map!.height).toBeLessThanOrEqual(page.viewportSize()!.height);
});

test("desktop composition stays compact rather than becoming a poster gallery", async ({
  page,
}) => {
  test.skip((page.viewportSize()?.width ?? 0) < 901, "Desktop composition");
  await page.goto("/");
  const cards = await page.locator("[data-choice]").evaluateAll((elements) =>
    elements.map((element) => {
      const card = element.getBoundingClientRect();
      const image = element.querySelector("img")!.getBoundingClientRect();
      const title = element.querySelector("strong")!.getBoundingClientRect();
      return {
        width: card.width,
        height: card.height,
        imageRight: image.right,
        titleLeft: title.left,
      };
    }),
  );
  for (const card of cards) {
    expect(card.height).toBeLessThan(400);
    expect(card.titleLeft).toBeGreaterThanOrEqual(card.imageRight);
  }
  expect(
    await page.evaluate(() => document.documentElement.scrollHeight),
  ).toBeLessThanOrEqual(page.viewportSize()!.height + 1);
  await page.getByRole("button", { name: "Профессионал", exact: true }).click();
  await page.getByRole("button", { name: "Хор", exact: true }).click();
  await page.getByRole("button", { name: "Лодка", exact: true }).click();
  for (const name of ["№2", "№1", "№3", "Подобрать автоматически"]) {
    await page.getByRole("button", { name, exact: true }).click();
    const picture = await page
      .locator("[data-outcome-art]:visible")
      .boundingBox();
    const panel = await page
      .locator('[data-layout="result"] > [data-carrier]')
      .boundingBox();
    expect(picture!.x).toBeLessThanOrEqual(1);
    expect(picture!.width).toBeGreaterThanOrEqual(
      page.viewportSize()!.width - 1,
    );
    expect(panel!.x).toBeGreaterThanOrEqual(picture!.x + picture!.width * 0.6);
    await page.getByRole("button", { name: "Назад к машинам" }).click();
  }
});

test("header restores numbered progress and rounded media", async ({
  page,
}) => {
  await page.goto("/");
  const nav = page.getByRole("navigation", { name: "Этапы доставки" });
  await expect(nav.locator("i")).toHaveText(["1", "2", "3", "4", "5"]);
  await expect(nav.locator("[data-progress-step] > span")).toHaveText([
    "Перевозчик",
    "Загрузка",
    "Склад",
    "Баржа",
    "Последняя миля",
  ]);
  const initialHeight = (await page.locator("header").boundingBox())!.height;
  for (const image of await page.locator("[data-choice] img").all()) {
    expect(
      await image.evaluate((el) =>
        parseFloat(getComputedStyle(el).borderTopRightRadius),
      ),
    ).toBeGreaterThan(0);
    expect(
      await image.evaluate((el) =>
        parseFloat(getComputedStyle(el).borderBottomRightRadius),
      ),
    ).toBeGreaterThan(0);
  }
  for (const [action, current] of [
    ["Профессионал", "Перевозчик"],
    ["Хор", "Перевозчик"],
    ["Лодка", "Перевозчик"],
    ["Назад", "Перевозчик"],
  ]) {
    await page.getByRole("button", { name: action, exact: true }).click();
    await expect(nav.locator('[aria-current="step"] > span')).toHaveText(
      current,
    );
    expect((await page.locator("header").boundingBox())!.height).toBeCloseTo(
      initialHeight,
      0,
    );
    for (const image of await page
      .locator("header [data-selection-context] img")
      .all()) {
      expect(
        await image.evaluate((el) =>
          parseFloat(getComputedStyle(el).borderRadius),
        ),
      ).toBeGreaterThan(0);
    }
    await expectResponsive(page);
  }
  const geometry = await nav
    .locator("[data-progress-step]")
    .evaluateAll((nodes) =>
      nodes.map((node) => {
        const circle = node.querySelector("i")!.getBoundingClientRect();
        const label = node.querySelector("span")!;
        return {
          width: circle.width,
          height: circle.height,
          textFits: label.scrollWidth <= label.clientWidth + 1,
          line: getComputedStyle(node, "::after").width,
        };
      }),
    );
  for (const item of geometry) {
    expect(item.width).toBe(item.height);
    expect(item.width).toBeGreaterThanOrEqual(24);
    expect(item.textFits).toBe(true);
  }
  expect(geometry.slice(0, 3).every((item) => parseFloat(item.line) > 0)).toBe(
    true,
  );
});

test("profile-first entry and mobile delivery hierarchy follow the review", async ({
  page,
}) => {
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: "Кто отправится в путь?" }),
  ).toBeVisible();
  await expect(page.getByRole("button", { name: "Начать игру" })).toHaveCount(
    0,
  );
  await expect(
    page.getByRole("button", { name: "Назад", exact: true }),
  ).toHaveCount(0);
  await expect(page.locator('[data-layout="intro"]')).toHaveCount(0);
  await expectResponsive(page);
  await page.getByRole("button", { name: "Профессионал", exact: true }).click();
  await page.getByRole("button", { name: "Хор", exact: true }).click();
  await page.getByRole("button", { name: "Лодка", exact: true }).click();
  if (
    page.viewportSize()!.width <= 900 &&
    page.viewportSize()!.height > page.viewportSize()!.width
  ) {
    const map = await page.locator('[data-mode="live"]').boundingBox();
    const back = await page
      .getByRole("button", { name: "Назад", exact: true })
      .boundingBox();
    expect(back!.y).toBeGreaterThanOrEqual(map!.y + map!.height);
  }
  await page.getByRole("button", { name: "№2", exact: true }).click();
  await expect(
    page.getByText("К чему приведёт выбор", { exact: true }),
  ).toHaveCount(0);
  await expect(
    page.getByRole("button", { name: "К следующей сцене" }),
  ).toBeDisabled();
  await expect(
    page.getByText("Продолжение пока недоступно", { exact: true }),
  ).toHaveCount(0);
  const pairs = await page.locator("[data-score-key]").evaluateAll((nodes) =>
    nodes.map((node) => ({
      value: node.querySelector("strong")!.getBoundingClientRect().bottom,
      label: node.querySelector("em")!.getBoundingClientRect().top,
    })),
  );
  expect(pairs.every((pair) => pair.value <= pair.label)).toBe(true);
  await expect(page.locator('[data-score-key="empathy"] strong')).toHaveCSS(
    "color",
    "rgb(211, 223, 238)",
  );
  await expectResponsive(page);
});
