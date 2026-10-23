import { expect, test } from "@playwright/test";

test.beforeEach(async ({ page }) => {
  await page.goto("/");
  await page.evaluate(() => {
    localStorage.clear();
    const scope = "quest-ending-actions";
    localStorage.setItem(
      "energy-quest-save-v1",
      JSON.stringify({
        version: 1,
        scope,
        state: {
          step: "outcome",
          profile: "student",
          recipient: "alva",
          parcel: "socks",
          carrier: "old",
          scores: { energy: 0, empathy: 0, efficiency: 0 },
        },
      }),
    );
    for (const k of ["remaining", "intro-seen", "ending-profile"])
      localStorage.setItem(`${scope}:${k}`, "true");
    localStorage.setItem(
      `${scope}:scenes`,
      JSON.stringify({
        progress: {
          sceneIndex: 3,
          phase: "result",
          finished: true,
          answers: {
            compact: "place-1",
            inventory: "entrance",
            crane: "rush",
            lastmile: "helicopter",
          },
        },
      }),
    );
  });
});
test("share popup contains labelled download and social links, traps focus and closes", async ({
  page,
}) => {
  await page.reload();
  await expect(
    page.getByRole("link", { name: "MAX", exact: true }),
  ).not.toBeVisible();
  const trigger = page.getByRole("button", { name: "Поделиться", exact: true });
  await trigger.click();
  const dialog = page.getByRole("dialog", { name: "Поделиться результатом" });
  await expect(dialog).toBeVisible();
  await expect(dialog.getByRole("button", { name: "Закрыть" })).toBeFocused();
  for (const name of ["MAX", "Telegram", "ВКонтакте"])
    await expect(dialog.getByRole("link", { name, exact: true })).toBeVisible();
  const download = dialog.getByRole("button", {
    name: "Скачать сертификат",
    exact: true,
  });
  await expect(download).toHaveText("Скачать сертификат");
  const pending = page.waitForEvent("download");
  await download.click();
  expect((await pending).suggestedFilename()).toMatch(/\.png$/);
  await dialog.getByRole("button", { name: "Закрыть" }).focus();
  await page.keyboard.press("Shift+Tab");
  await expect(download).toBeFocused();
  await page.keyboard.press("Tab");
  await expect(dialog.getByRole("button", { name: "Закрыть" })).toBeFocused();
  await page.keyboard.press("Escape");
  await expect(dialog).not.toBeVisible();
  await expect(trigger).toBeFocused();
  await trigger.click();
  await dialog.getByRole("button", { name: "Закрыть" }).click();
  await expect(trigger).toBeFocused();
});
