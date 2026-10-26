import { expect, test } from "@playwright/test";
import { openCarrier, pickCarrier } from "./helpers/open-preparation";

test("map teaches zoom once, previews a truck, and returns to the overview", async ({
  page,
}, info) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await openCarrier(page, "professional", "alva", "boat");
  const condition = page.getByRole("region", {
    name: "Условие задания",
    exact: true,
  });
  for (let n = 0; n < 30 && (await condition.isVisible()); n++)
    await condition
      .getByRole("button", { name: /^(Далее|К выбору|К сцене)$/ })
      .click();

  const map = page.locator("[data-map-viewport]");
  const hint = page.locator("[data-map-zoom-hint]");
  if (info.project.use.hasTouch) {
    await expect(hint).toBeHidden();
  } else {
    await expect(hint).toBeVisible();
    await expect(hint).toBeInViewport({ ratio: 1 });
  }
  await expect(hint).toContainText(
    info.project.use.hasTouch
      ? "Раздвиньте пальцы, чтобы приблизить"
      : "Прокрутите колёсико, чтобы приблизить",
  );
  await page.screenshot({ path: info.outputPath("zoom-hint.png") });

  const truck = page.locator('[data-carrier-choice="near"]');
  // Keyboard focus makes even a cropped poster truck reachable before a tap.
  await truck.focus();
  if (info.project.use.hasTouch) await truck.tap();
  else await truck.click();
  await expect(hint).toHaveCount(0);
  const card = page.locator('[data-carrier-inspection="near"]');
  await expect(card).toBeVisible();
  await expect(card).toContainText("17 км/ч");
  await expect(card).toContainText("2021");
  await expect(page.locator('[data-layout="result"]')).toHaveCount(0);
  const reset = page.getByRole("button", {
    name: "Вернуть карту",
    exact: true,
  });
  await expect(reset).toBeInViewport({ ratio: 1 });
  await page.screenshot({
    path: info.outputPath("truck-preview-with-reset.png"),
  });
  if (info.project.use.hasTouch) await reset.tap();
  else await reset.click();
  await expect(map).toHaveAttribute("data-map-scale", "1");
  await expect(card).toHaveCount(0);
  await expect(hint).toHaveCount(0);
  await page.screenshot({ path: info.outputPath("overview-restored.png") });
  await pickCarrier(page, "near");
  await expect(card).toBeVisible();
  await page.locator("[data-choice-confirm]").click();
  await expect(
    page.locator('[data-layout="result"][data-carrier="near"]'),
  ).toBeVisible();
});
