import { expect, test } from "@playwright/test";

test("helicopter artwork follows the authored flight and ground narrative beats", async ({
  page,
}) => {
  await page.goto("/scenes.html?scene=lastmile&parcel=boat&recipient=alva");
  const briefing = page.getByRole("button", { name: /^(Далее|К выбору)$/ });
  for (let step = 0; step < 10 && (await briefing.isVisible()); step += 1)
    await briefing.click();

  await page
    .locator('[data-choice-id="helicopter"]:not([data-callout-target])')
    .click();

  const art = page.locator('[data-scene-consequence="lastmile-helicopter-remote"]');
  const image = art.locator("img");
  const copy = page.getByTestId("result-copy");
  await expect(page.getByRole("navigation", { name: "Эпизоды доставки" })).toHaveCount(0);
  await expect(art).toHaveAttribute("data-outcome-beat", "0");
  await expect(image).toHaveAttribute("src", /revision-2\/flight-boat\.webp/);
  await expect(copy).toContainText("Он быстро преодолел леса и болота");

  const readFurther = page.getByRole("button", {
    name: "Читать дальше",
    exact: true,
  });
  let flightPages = 0;
  while ((await art.getAttribute("data-outcome-beat")) === "0") {
    await expect(image).toHaveAttribute("src", /revision-2\/flight-boat\.webp/);
    await expect(copy).not.toContainText(/от посадочной площадки/i);
    await expect(readFurther).toBeVisible();
    await readFurther.click();
    flightPages += 1;
    if (flightPages > 10) throw new Error("Ground narrative beat was not reached");
  }

  expect(flightPages).toBeGreaterThan(0);
  await expect(art).toHaveAttribute("data-outcome-beat", "1");
  await expect(copy).toContainText(/от посадочной площадки/i);
  await expect(image).toHaveAttribute("src", /helicopter-ground-boat-final-v5/);
});
