import assert from "node:assert/strict";
import { chromium } from "playwright";

const target = process.argv[2];

if (!target) {
  throw new Error("Static archive URL is required");
}

const profiles = [
  { name: "small-phone", viewport: { width: 320, height: 568 } },
  { name: "phone-landscape", viewport: { width: 844, height: 390 } },
  { name: "tablet-landscape", viewport: { width: 1180, height: 820 } },
  { name: "wide-monitor", viewport: { width: 2560, height: 1440 } },
  { name: "desktop", viewport: { width: 1440, height: 900 } },
  { name: "windows-125", viewport: { width: 1152, height: 720 } },
  { name: "windows-140", viewport: { width: 1024, height: 643 } },
  { name: "tablet", viewport: { width: 820, height: 1180 } },
  { name: "mobile", viewport: { width: 390, height: 844 } },
  { name: "mobile-toolbar", viewport: { width: 390, height: 700 } },
  { name: "iphone-se", viewport: { width: 375, height: 667 } },
];

const browser = await chromium.launch({ headless: true });

try {
  for (const profile of profiles) {
    const page = await browser.newPage({ viewport: profile.viewport });
    const externalRequests = [];
    const localFailures = [];
    const pageErrors = [];

    await page.route("**/*", async (route) => {
      const requestUrl = new URL(route.request().url());

      if (
        requestUrl.protocol === "data:" ||
        requestUrl.hostname === "127.0.0.1"
      ) {
        await route.continue();
        return;
      }

      externalRequests.push(route.request().url());
      await route.abort("blockedbyclient");
    });

    page.on("requestfailed", (request) => {
      const requestUrl = new URL(request.url());

      if (requestUrl.hostname === "127.0.0.1") {
        localFailures.push(request.url());
      }
    });
    page.on("pageerror", (error) => pageErrors.push(error.message));

    await page.goto(target, { waitUntil: "networkidle" });
    assert.equal(await page.getByText("Начало игры", { exact: true }).count(), 0);
    for (const name of ["Студент", "Хор", "Фотоаппарат"]) {
      await page.getByRole("button", { name, exact: true }).click();
      assert.equal(await page.locator('[data-choice] b, [data-choice] [data-role-part="action"]').count(), 0);
      assert.equal(await page.getByRole("navigation", { name: "Этапы доставки" }).locator('[data-progress-step]').count(), 5);
    }
    await page.getByRole("button", { name: "Назад", exact: true }).click();
    await page.getByRole("button", { name: "Лодка", exact: true }).click();
    await page
      .getByRole("button", { name: "Подобрать автоматически", exact: true })
      .click();
    await page
      .getByRole("heading", { name: "Перевозчик найден за два часа" })
      .waitFor();
    assert.equal(await page.getByText('К чему приведёт выбор', { exact: true }).count(), 0);
    assert.equal(await page.getByRole('button', { name: 'Едем дальше', exact: true }).count(), 0);
    assert.equal(await page.getByRole('button', { name: 'К следующей сцене', exact: true }).isDisabled(), true);
    await page.evaluate(() => document.fonts.ready);
    await page.waitForFunction(
      () =>
        [...document.images].every(
          (image) => image.complete && image.naturalWidth > 0,
        ),
      undefined,
      { timeout: 10_000 },
    );

    const state = await page.evaluate(() => ({
      clientHeight: document.documentElement.clientHeight,
      clientWidth: document.documentElement.clientWidth,
      labelsFit: [...document.querySelectorAll('nav span')].every(element => {
        const box = element.getBoundingClientRect();
        return box.left >= 0 && box.right <= innerWidth;
      }),
      imagesLoaded: [...document.images].every(
        (image) => image.complete && image.naturalWidth > 0,
      ),
      incompleteImages: [...document.images]
        .filter((image) => !image.complete || image.naturalWidth === 0)
        .map((image) => image.currentSrc || image.src),
      scrollHeight: document.documentElement.scrollHeight,
      scrollWidth: document.documentElement.scrollWidth,
    }));

    if (
      externalRequests.length > 0 ||
      localFailures.length > 0 ||
      pageErrors.length > 0 ||
      !state.imagesLoaded ||
      !state.labelsFit ||
      state.scrollWidth > state.clientWidth + 1
    ) {
      throw new Error(
        JSON.stringify({
          externalRequests,
          localFailures,
          pageErrors,
          profile: profile.name,
          state,
        }),
      );
    }

    console.log(
      `${profile.name}: responsive route and carrier Back passed; all resources local; no horizontal overflow`,
    );
    await page.close();
  }
} finally {
  await browser.close();
}
