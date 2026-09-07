import { expect, test } from "@playwright/test";

test("every scene fits the viewport without hiding content", async ({
  page,
}) => {
  await page.goto("/");
  for (const action of [
    "Начать игру",
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
  await expect(page.locator('[aria-current="step"] span')).toHaveText(
    "Перевозчик",
  );
  await expect(page.locator('[aria-current="step"] i')).toHaveCSS(
    "color",
    "rgb(255, 255, 255)",
  );
});
