import { chromium } from "playwright";

const target = process.argv[2];

if (!target) {
  throw new Error("Static archive URL is required");
}

const profiles = [
  { name: "desktop", viewport: { width: 1440, height: 900 } },
  { name: "windows-125", viewport: { width: 1152, height: 720 } },
  { name: "windows-140", viewport: { width: 1024, height: 643 } },
  { name: "tablet", viewport: { width: 820, height: 1180 } },
  { name: "mobile", viewport: { width: 390, height: 844 } },
  { name: "mobile-toolbar", viewport: { width: 390, height: 700 } },
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
    await page.getByRole("button", { name: /Начать маршрут/ }).click();
    await page.getByRole("button", { name: /Студент/ }).click();
    await page.getByRole("button", { name: /Альва/ }).click();
    await page.getByRole("button", { name: /Фотоаппарат/ }).click();
    await page.getByRole("button", { name: /Открыть карту/ }).click();
    await page.getByRole("button", { name: /Запустить Express/ }).click();
    await page
      .getByRole("button", { name: /Разобрать подбор Express/ })
      .click();
    await page
      .getByRole("button", { name: /Зафиксировать результат/ })
      .click();
    await page
      .getByRole("heading", { name: "Первый участок пройден" })
      .waitFor();
    await page.evaluate(() => document.fonts.ready);

    const state = await page.evaluate(() => ({
      clientHeight: document.documentElement.clientHeight,
      clientWidth: document.documentElement.clientWidth,
      imagesLoaded: [...document.images].every(
        (image) => image.complete && image.naturalWidth > 0,
      ),
      scrollHeight: document.documentElement.scrollHeight,
      scrollWidth: document.documentElement.scrollWidth,
    }));

    if (
      externalRequests.length > 0 ||
      localFailures.length > 0 ||
      pageErrors.length > 0 ||
      !state.imagesLoaded ||
      state.scrollHeight > state.clientHeight + 1 ||
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
      `${profile.name}: complete route passed; all resources local; no page scroll`,
    );
    await page.close();
  }
} finally {
  await browser.close();
}
