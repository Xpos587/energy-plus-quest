import { expect, type Page, test } from "@playwright/test";

async function expectCompleteArtwork(page: Page) {
  const image = page.locator("[data-compact-consequence] img");
  await expect
    .poll(() =>
      image.evaluate(
        (node: HTMLImageElement) => node.complete && node.naturalWidth > 0,
      ),
    )
    .toBe(true);
  const geometry = await page
    .locator("[data-compact-consequence]")
    .evaluate((figure) => {
      const image = figure.querySelector("img");
      const caption = figure.querySelector("figcaption");
      if (!image || !caption)
        throw new Error("Missing result illustration or caption");
      const bounds = figure.getBoundingClientRect();
      const imageBounds = image.getBoundingClientRect();
      const captionBounds = caption.getBoundingClientRect();
      return {
        fit: getComputedStyle(image).objectFit,
        contained: [imageBounds, captionBounds].every(
          (rect) =>
            rect.left >= bounds.left - 1 &&
            rect.right <= bounds.right + 1 &&
            rect.top >= bounds.top - 1 &&
            rect.bottom <= bounds.bottom + 1,
        ),
        captionFits: caption.scrollHeight <= caption.clientHeight + 1,
        width: imageBounds.width,
        height: imageBounds.height,
      };
    });
  expect(geometry.fit).toBe("contain");
  expect(geometry.contained).toBe(true);
  expect(geometry.captionFits).toBe(true);
  expect(geometry.width).toBeGreaterThan(100);
  expect(geometry.height).toBeGreaterThan(100);
}

for (const parcel of ["socks", "camera", "boat"] as const) {
  test(`${parcel}: loading preview, cancellation, confirmation and automatic placement`, async ({
    page,
  }) => {
    await page.goto(`/scenes.html?scene=compact&parcel=${parcel}`);
    await page.getByRole("button", { name: "К выбору", exact: true }).click();
    for (const place of [1, 2, 3, 4]) {
      const marker = page.locator(`[data-hotspot="place-${place}"]`);
      // Exercise actual taps/clicks and native keyboard activation.
      if (place === 2) {
        await marker.focus();
        await marker.press("Space");
      } else await marker.click();
      await expect(
        page.locator(`[data-choice-inspection="compact:place-${place}"]`),
      ).toBeVisible();
      await expect(page.locator("[data-compact-consequence]")).toHaveCount(0);
      await expect(marker).toBeEnabled();
      await expect(marker).toHaveAttribute("aria-pressed", "true");
      await page.locator("[data-choice-cancel]").click();
      await expect(marker).toHaveAttribute("aria-pressed", "false");
      await marker.click();
      await page.locator("[data-choice-confirm]").click();
      const next = page.getByRole("button", {
        name: "Следующий фрагмент",
        exact: true,
      });
      while (await next.isEnabled()) {
        await expect(page.locator("[data-compact-consequence]")).toHaveCount(0);
        await next.click();
      }
      const image = page.locator("[data-compact-consequence] img");
      await expect(image).toHaveAttribute(
        "src",
        /^\/compact-art\/outcomes\/.+\.png$/,
      );
      await expect(image).toHaveAttribute("alt", /\S/);
      await expectCompleteArtwork(page);
      await expect(page.locator("[data-compact-consequence] svg")).toHaveCount(
        0,
      );
      await expect(
        page.locator(`[data-compact-consequence="${parcel}-place-${place}"]`),
      ).toBeVisible();
      await expect(
        page.locator(`[data-loading-zone="place-${place}"]`),
      ).toHaveAttribute("data-active", "true");
      await expect(
        page.locator("[data-world-scene='compact'] button:disabled"),
      ).toHaveCount(4);
      await page.getByRole("button", { name: "Назад", exact: true }).click();
      await page.getByRole("button", { name: "К выбору", exact: true }).click();
      await expect(page.locator("[data-compact-consequence]")).toHaveCount(0);
      await expect(
        page.locator('[data-loading-zone][data-active="true"]'),
      ).toHaveCount(0);
    }
    await page.goto(`/scenes.html?scene=compact&parcel=${parcel}`);
    await page.getByRole("button", { name: "К выбору", exact: true }).click();
    await page.locator('[data-choice-id="auto"]').click();
    await expect(
      page.locator('[data-loading-zone][data-active="true"]'),
    ).toHaveCount(0);
    await page.locator("[data-choice-confirm]").click();
    await expect(page.locator('[data-world-scene="compact"]')).toHaveAttribute(
      "data-placement",
      parcel === "boat" ? "4" : "3",
    );
    const automaticPlace = page.locator(
      `[data-hotspot="place-${parcel === "boat" ? 4 : 3}"]`,
    );
    await expect(automaticPlace).toBeInViewport();
    const next = page.getByRole("button", {
      name: "Следующий фрагмент",
      exact: true,
    });
    while (await next.isEnabled()) await next.click();
    await expectCompleteArtwork(page);
    await expect(
      page.locator("[data-compact-consequence] img"),
    ).toHaveAttribute("alt", /\S/);
    await expect(page.locator("[data-diagram]")).toHaveAttribute(
      "data-diagram",
      parcel === "boat" ? "upright" : "compact",
    );
  });
}
