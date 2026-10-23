import { expect, test } from "@playwright/test";

test("returning through every Back button leaves both profile cards clickable", async ({
  page,
  isMobile,
}) => {
  await page.goto("/");
  for (let round = 0; round < 6; round += 1) {
    const profile = round % 2 ? "student" : "professional";
    for (const choice of [profile, "alva", "camera"]) {
      const button = page.locator(`[data-choice="${choice}"]`);
      await button.scrollIntoViewIfNeeded();
      if (isMobile) await button.tap();
      else await button.click();
    }
    const carrier = page.getByRole("button", {
      name: "№3",
      exact: true,
    });
    if (isMobile) await carrier.tap();
    else await carrier.click();
    await page
      .getByRole("button", { name: "Назад к машинам", exact: true })
      .click();
    for (let step = 0; step < 3; step += 1) {
      await page.getByRole("button", { name: "Назад", exact: true }).click();
    }
    await expect(
      page.getByRole("heading", {
        name: "Кто отправится в путь?",
        exact: true,
      }),
    ).toBeVisible();
    await expect(page.locator("[data-truck-number]")).toHaveCount(0);
    await expect(page.locator("video")).toHaveCount(0);
    for (const choice of ["student", "professional"]) {
      const button = page.locator(`[data-choice="${choice}"]`);
      await button.scrollIntoViewIfNeeded();
      expect(
        await button.evaluate((element) => {
          const box = element.getBoundingClientRect();
          const target = document.elementFromPoint(
            box.x + box.width / 2,
            box.y + box.height / 2,
          );
          return target !== null && element.contains(target);
        }),
      ).toBe(true);
    }
  }
  await page.locator('[data-choice="student"]').click();
  await expect(
    page.getByRole("heading", { name: "Выберите получателя", exact: true }),
  ).toBeVisible();
});
