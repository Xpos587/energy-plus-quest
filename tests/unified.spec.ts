import { expect, type Page, test } from "@playwright/test";

async function fits(page: Page) {
  expect(
    await page.evaluate(() => ({
      horizontal: document.documentElement.scrollWidth > innerWidth,
      vertical: document.documentElement.scrollHeight > innerHeight,
    })),
  ).toEqual({ horizontal: false, vertical: false });
  for (const button of await page
    .locator("[data-choice-id], [data-carrier-choice]")
    .all()) {
    await expect(button).toBeInViewport({ ratio: 1 });
    const box = (await button.boundingBox())!;
    // DOM transforms can report 43.99997 for a 44px target.
    expect(box.height).toBeGreaterThanOrEqual(44 - 0.01);
    expect(box.width).toBeGreaterThanOrEqual(44 - 0.01);
    const panel = await button.locator("../..").boundingBox();
    expect(box.y + box.height).toBeLessThanOrEqual(panel!.y + panel!.height);
  }
}

test("remaining stages share geometry, full copy and scores", async ({
  page,
}, info) => {
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await page.goto("/");
  for (const id of ["professional", "alva", "boat"])
    await page.locator(`[data-choice="${id}"]`).click();
  await page.evaluate(() => document.fonts.ready);
  await fits(page);
  await page.screenshot({ path: info.outputPath("carrier.png") });
  await page.locator('[data-carrier-choice="express"]').click();
  await expect(
    page.getByRole("button", { name: "К следующей сцене" }),
  ).toBeInViewport({ ratio: 1 });
  await page.getByRole("button", { name: "К следующей сцене" }).click();
  const header = await page.locator("header").boundingBox();
  const logos = await page.locator("header img").evaluateAll((nodes) =>
    nodes.map((node) => {
      const box = node.getBoundingClientRect();
      return [box.x, box.y, box.width, box.height];
    }),
  );
  for (const [index, id] of [
    "auto",
    "wms",
    "remote",
    "pipe-carrier",
  ].entries()) {
    await expect(page.getByRole("heading")).toBeFocused();
    await expect(page.locator("header")).toHaveCount(1);
    expect(await page.locator("header").boundingBox()).toEqual(header);
    expect(
      await page.locator("header img").evaluateAll((nodes) =>
        nodes.map((node) => {
          const box = node.getBoundingClientRect();
          return [box.x, box.y, box.width, box.height];
        }),
      ),
    ).toEqual(logos);
    await expect(page.locator('[aria-current="step"] > span')).toHaveText(
      ["Загрузка", "Склад", "Баржа", "Последняя миля"][index],
    );
    await expect(page.getByRole("heading")).not.toContainText(/Сцена \d/);
    const toggle = page.locator("[aria-expanded]");
    if ((await toggle.getAttribute("aria-expanded")) === "true")
      await toggle.press("Enter");
    await expect(toggle).toHaveAttribute("aria-expanded", "false");
    await fits(page);
    await page.screenshot({ path: info.outputPath(`${index}-collapsed.png`) });
    await toggle.press("Enter");
    await expect(toggle).toHaveAttribute("aria-expanded", "true");
    const intro = await page.getByTestId("scene-intro").textContent();
    expect(intro!.length).toBeGreaterThan(80);
    const descriptions = await page
      .locator("[data-choice-description]")
      .allTextContents();
    const choices = page.locator("[data-choice-id]");
    for (const [i, description] of descriptions.entries())
      await expect(choices.nth(i)).toHaveAccessibleName(description);
    await fits(page);
    await page.screenshot({ path: info.outputPath(`${index}-expanded.png`) });
    await toggle.press("Escape");
    await expect(toggle).toBeFocused();
    await expect(toggle).toHaveAttribute("aria-expanded", "false");
    await page.locator(`[data-choice-id="${id}"]`).click();
    await expect(page.getByRole("heading")).toBeFocused();
    await expect(page.getByTestId("result-copy")).toBeVisible();
    const copy = page.getByTestId("result-copy").locator("..");
    await copy.focus();
    await copy.press("End");
    await expect
      .poll(() =>
        copy.evaluate(
          (node) => node.scrollTop + node.clientHeight >= node.scrollHeight - 1,
        ),
      )
      .toBe(true);
    await copy.press("Home");
    await expect.poll(() => copy.evaluate((node) => node.scrollTop)).toBe(0);
    await expect(page.locator("[data-score-key]")).toHaveCount(3);
    await fits(page);
    const next = page.getByRole("button", {
      name: index === 3 ? "Завершить" : "Продолжить",
      exact: true,
    });
    await expect(next).toBeInViewport({ ratio: 1 });
    await expect(
      page.getByRole("button", { name: "Изменить выбор" }),
    ).toBeInViewport({ ratio: 1 });
    await page.screenshot({ path: info.outputPath(`${index}-result.png`) });
    await next.click();
  }
  await expect(
    page.getByRole("button", { name: "Завершено", exact: true }),
  ).toBeDisabled();
  expect(errors).toEqual([]);
});

test("back navigation and orientation keep context and choices reachable", async ({
  page,
}) => {
  await page.goto("/");
  for (const id of ["student", "khor", "camera"])
    await page.locator(`[data-choice="${id}"]`).click();
  await page.locator('[data-carrier-choice="near"]').click();
  await expect(
    page.getByRole("button", { name: "К следующей сцене" }),
  ).toBeInViewport({ ratio: 1 });
  await page.getByRole("button", { name: "К следующей сцене" }).click();
  await page.getByRole("button", { name: "Назад", exact: true }).click();
  await expect(page.locator('[data-carrier-choice="near"]')).toBeVisible();
  await expect(page.locator("header [data-selection-context]")).toHaveCount(3);
  await page.locator('[data-carrier-choice="near"]').click();
  await expect(
    page.getByRole("button", { name: "К следующей сцене" }),
  ).toBeInViewport({ ratio: 1 });
  await page.getByRole("button", { name: "К следующей сцене" }).click();
  await page.locator('[data-choice-id="place-1"]').click();
  await page.getByRole("button", { name: "Продолжить", exact: true }).click();
  await page.getByRole("button", { name: "Назад", exact: true }).click();
  await expect(page.locator('[data-scene="compact"]')).toBeVisible();
  await page.getByRole("button", { name: "Изменить выбор" }).click();
  await page.locator("[aria-expanded]").click();
  for (const [width, height] of [
    [844, 390],
    [320, 568],
    [1440, 900],
    [375, 667],
  ]) {
    await page.setViewportSize({ width, height });
    await fits(page);
  }
});
