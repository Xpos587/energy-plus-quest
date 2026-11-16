import { expect, test } from "@playwright/test";
import { openCarrier, pickCarrier } from "./helpers/open-preparation";

for (const asset of ["trucks", "plate"] as const) {
  test(`carrier map recovers after ${asset} download failures without restarting`, async ({
    page,
  }, info) => {
    await page.emulateMedia({ reducedMotion: "reduce" });
    const errors: string[] = [];
    page.on("pageerror", (error) => errors.push(error.message));
    const pattern =
      asset === "trucks"
        ? /scene1-v4\/trucks-(wide|tall)\.webp/
        : /scene1-v4\/plate-(wide|tall)-v18/;
    let failures = 0;
    await page.route(pattern, (route) => {
      failures++;
      return route.abort();
    });
    await openCarrier(page, "professional", "khor", "socks");
    await expect.poll(() => failures).toBeGreaterThan(0);
    const feedback = page.locator('[data-artwork-status="error"]');
    await expect(feedback).toBeVisible();
    await expect(page.locator("[data-carrier-tap-hint]")).toBeHidden();
    if (asset === "plate")
      await expect(page.locator("[data-city-plate]")).toBeHidden();
    await expect(page.locator("[data-map-viewport]")).toHaveAttribute(
      "inert",
      "",
    );
    const unavailable = page.locator('[data-carrier-choice="crew"]');
    await unavailable.focus();
    await expect(unavailable).not.toBeFocused();
    await page.screenshot({ path: info.outputPath(`${asset}-failure.png`) });
    const count = failures;
    await feedback
      .getByRole("button", { name: "Повторить", exact: true })
      .click();
    await expect.poll(() => failures).toBeGreaterThan(count);
    await expect(feedback).toBeVisible();
    await page.unroute(pattern);
    await feedback
      .getByRole("button", { name: "Повторить", exact: true })
      .click();
    await expect(page.locator("[data-artwork-status]")).toHaveCount(0);
    await expect(page.locator("[data-map-surface]")).toHaveAttribute(
      "data-motion-reason",
      "reduced-motion",
    );
    await page
      .locator("[data-city-plate]")
      .evaluate((image: HTMLImageElement) => image.decode());
    await expect(
      page.locator("[data-choice-inspection], [data-layout='result']"),
    ).toHaveCount(0);
    await expect(page.locator("[data-carrier-tap-hint]")).toBeVisible();
    await expect(page.locator("[data-map-viewport]")).not.toHaveAttribute(
      "inert",
    );
    await page.screenshot({
      path: info.outputPath(`${asset}-map-recovered.png`),
    });
    await pickCarrier(page, "crew");
    await page.locator("[data-choice-confirm]").click();
    await expect(
      page.locator('[data-layout="result"][data-carrier="crew"]'),
    ).toBeVisible();
    await page.screenshot({ path: info.outputPath(`${asset}-recovered.png`) });
    expect(errors).toEqual([]);
  });
}

test("rotating away from a failed map loads the matching artwork and can rotate back", async ({
  page,
}) => {
  await page.emulateMedia({ reducedMotion: "no-preference" });
  await page.setViewportSize({ width: 1440, height: 900 });
  const pattern = /scene1-v4\/(trucks-wide\.webp|plate-wide-v18)/;
  await page.route(pattern, (route) => route.abort());
  await openCarrier(page);
  const feedback = page.locator('[data-artwork-status="error"]');
  const surface = page.locator("[data-map-surface]");
  await expect(feedback).toBeVisible();
  await page.setViewportSize({ width: 390, height: 844 });
  await expect(page.locator("[data-city-plate]")).toHaveAttribute(
    "data-city-plate",
    "tall",
  );
  await expect(page.locator("[data-artwork-status]")).toHaveCount(0);
  await expect(surface).toHaveAttribute("data-motion-state", "playing");
  await page.setViewportSize({ width: 1440, height: 900 });
  await expect(feedback).toBeVisible();
  await expect(surface).toHaveAttribute("data-motion-state", "paused");
  await page.unroute(pattern);
  await feedback
    .getByRole("button", { name: "Повторить", exact: true })
    .click();
  await expect(page.locator("[data-artwork-status]")).toHaveCount(0);
  await expect(page.locator("[data-city-plate]")).toHaveAttribute(
    "data-city-plate",
    "wide",
  );
  await expect(surface).toHaveAttribute("data-motion-state", "playing");
  await pickCarrier(page, "express");
  await expect(
    page.locator('[data-choice-inspection="express"]'),
  ).toBeVisible();
});
