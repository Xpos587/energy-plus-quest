import { expect, type Page } from "@playwright/test";

/** Follow the real opening before older route tests exercise the preparation screen. */
export async function openPreparation(page: Page): Promise<void> {
  await page.goto("/");
  await page.evaluate(() => {
    localStorage.clear();
    sessionStorage.clear();
  });
  await page.reload();
  await page.locator("[data-intro-enter]").click();
  await page.locator("[data-intro-next]").click();
  await page.locator("[data-intro-start]").click();
  await expect(page.locator('[data-choice="professional"]')).toBeVisible();
}

export async function openCarrier(
  page: Page,
  profile: "student" | "professional" = "professional",
  recipient: "alva" | "khor" | "arseniy" = "alva",
  parcel: "camera" | "socks" | "boat" = "camera",
): Promise<void> {
  await openPreparation(page);
  for (const id of [profile, recipient, parcel]) {
    await page.locator(`[data-choice="${id}"]`).click();
  }
  await expect(
    page.getByRole("heading", { name: "Выбор перевозчика" }),
  ).toBeVisible();
}
