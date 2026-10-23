import { expect, test, type Page } from "@playwright/test";

const viewports = [
  { width: 320, height: 568 },
  { width: 390, height: 844 },
  { width: 844, height: 390 },
  { width: 1440, height: 900 },
];

async function expectWholePageInView(page: Page, label: string) {
  await page.evaluate(() => document.fonts.ready);
  const geometry = await page.evaluate(() => {
    const view = { width: innerWidth, height: innerHeight };
    const controls = [...document.querySelectorAll<HTMLButtonElement | HTMLAnchorElement>("main button, main a")]
      .filter((element) => element.getClientRects().length > 0)
      .map((element) => {
        const rect = element.getBoundingClientRect();
        return { name: element.textContent?.trim(), top: rect.top, bottom: rect.bottom, height: rect.height };
      });
    return {
      view,
      scrollHeight: document.documentElement.scrollHeight,
      scrollWidth: document.documentElement.scrollWidth,
      internalScrolls: [...document.querySelectorAll<HTMLElement>("main *")]
        .filter((element) => {
          const style = getComputedStyle(element);
          return /auto|scroll/.test(style.overflowY) && element.scrollHeight > element.clientHeight + 1;
        })
        .map((element) => element.tagName.toLowerCase()),
      controls,
    };
  });
  expect(geometry.scrollHeight, `${label}: document height`).toBeLessThanOrEqual(geometry.view.height + 1);
  expect(geometry.scrollWidth, `${label}: document width`).toBeLessThanOrEqual(geometry.view.width + 1);
  expect(geometry.internalScrolls, `${label}: internal scroll areas`).toEqual([]);
  for (const control of geometry.controls) {
    expect(control.top, `${label}: ${control.name} top`).toBeGreaterThanOrEqual(-1);
    expect(control.bottom, `${label}: ${control.name} bottom`).toBeLessThanOrEqual(geometry.view.height + 1);
    expect(control.height, `${label}: ${control.name} target`).toBeGreaterThanOrEqual(44);
  }
}

async function openEnding(page: Page, options: { profile?: "student" | "professional"; recipient?: "alva" | "khor" | "arseniy"; parcel?: "socks" | "boat" | "camera" } = {}) {
  await page.goto("/");
  await page.evaluate(({ profile, recipient, parcel }) => {
    localStorage.clear();
    const scope = "quest-opening-end-fit";
    localStorage.setItem("energy-quest-save-v1", JSON.stringify({
      version: 1, scope,
      state: { step: "outcome", profile, recipient, parcel, carrier: "old", scores: { energy: 0, empathy: 0, efficiency: 0 } },
    }));
    for (const key of ["remaining", "intro-seen"])
      localStorage.setItem(`${scope}:${key}`, "true");
    localStorage.setItem(`${scope}:scenes`, JSON.stringify({
      progress: { sceneIndex: 3, phase: "result", finished: true, answers: { compact: "place-1", inventory: "entrance", crane: "rush", lastmile: "helicopter" } },
    }));
  }, { profile: options.profile ?? "student", recipient: options.recipient ?? "alva", parcel: options.parcel ?? "socks" });
  await page.reload();
  await expect(page.locator("[data-journey-ending]")).toBeVisible();
}

for (const context of [
  { profile: "student", recipient: "khor", parcel: "boat" },
  { profile: "professional", recipient: "arseniy", parcel: "camera" },
] as const) {
  test(`short-phone certificate fits ${context.profile}/${context.recipient}/${context.parcel}`, async ({ page }) => {
    await page.setViewportSize({ width: 320, height: 568 });
    await openEnding(page, context);
    await page.getByRole("button", { name: "Узнать, какой вы логист" }).click();
    await expectWholePageInView(page, `${context.profile} result`);
    await page.screenshot({ path: `.tmp-work/opening-end-fit/certificate-${context.profile}-${context.recipient}-${context.parcel}-320x568.png` });
    if (context.profile === "student") {
      await page.getByRole("button", { name: "Подробнее о практике" }).click();
      await expectWholePageInView(page, `${context.profile} practice`);
      await page.screenshot({ path: `.tmp-work/opening-end-fit/certificate-practice-${context.profile}-${context.recipient}-${context.parcel}-320x568.png` });
    } else {
      await expect(page.locator("[data-practice-cta]")).toHaveCount(0);
      await expect(page.getByRole("button", { name: "Подробнее о практике" })).toHaveCount(0);
    }
  });
}
for (const viewport of viewports) {
  test(`opening and ending pages fit ${viewport.width}x${viewport.height}`, async ({ page }) => {
    await page.setViewportSize(viewport);
    await page.emulateMedia({ reducedMotion: "reduce" });
    await page.goto("/");
    await expectWholePageInView(page, "cover");
    await page.screenshot({ path: `.tmp-work/opening-end-fit/cover-${viewport.width}x${viewport.height}.png` });
    await page.locator("[data-intro-enter]").click();
    await expectWholePageInView(page, "briefing");
    await page.screenshot({ path: `.tmp-work/opening-end-fit/briefing-${viewport.width}x${viewport.height}.png` });
    await page.locator("[data-intro-next]").click();
    await expectWholePageInView(page, "scoring");
    await page.screenshot({ path: `.tmp-work/opening-end-fit/scoring-${viewport.width}x${viewport.height}.png` });
    await openEnding(page);
    await expectWholePageInView(page, "ending");
    await page.screenshot({ path: `.tmp-work/opening-end-fit/ending-${viewport.width}x${viewport.height}.png` });
    await page.getByRole("button", { name: "Узнать, какой вы логист" }).click();
    await expectWholePageInView(page, "certificate");
    await page.screenshot({ path: `.tmp-work/opening-end-fit/certificate-${viewport.width}x${viewport.height}.png` });
    if (viewport.width === 320) {
      await page.getByRole("button", { name: "Подробнее о практике" }).click();
      await expect(page.locator("[data-practice-cta] h2")).toBeFocused();
      await expectWholePageInView(page, "certificate practice");
      await page.screenshot({ path: `.tmp-work/opening-end-fit/certificate-practice-${viewport.width}x${viewport.height}.png` });
      await page.getByRole("button", { name: "Назад к результату" }).click();
      await expect(page.locator("[data-logist-certificate] h1")).toBeFocused();
    }
  });
}

