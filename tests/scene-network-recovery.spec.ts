import { expect, type Page, test } from "@playwright/test";

const stages = [
  { id: "compact", choice: "auto", pattern: /compact-environment-v(53|54)/ },
  { id: "inventory", choice: "wms", pattern: /inventory-master-v16/ },
  {
    id: "crane",
    choice: "remote",
    pattern: /barge-v7\/(wide|desk|mid|tall)\/plate/,
  },
  { id: "lastmile", choice: "rover", pattern: /lastmile-family-v1\/revision-30\/choice/ },
] as const;

async function briefing(page: Page) {
  const panel = page.locator("[data-scene-briefing]");
  for (
    let n = 0;
    n < 30 && (await panel.getAttribute("data-reading")) === "true";
    n++
  )
    await panel
      .getByRole("button", { name: /^(Далее|К выбору|К сцене)$/ })
      .click();
  await expect(panel).toHaveAttribute("data-reading", "false");
}

async function checkpoint(page: Page, index: number) {
  await page.goto("/");
  const answers = Object.fromEntries(
    stages.slice(0, index).map((stage) => [stage.id, stage.choice]),
  );
  await page.evaluate(
    ({ index, answers }) => {
      localStorage.clear();
      const scope = "quest-scene-network";
      localStorage.setItem(
        "energy-quest-save-v1",
        JSON.stringify({
          version: 1,
          scope,
          state: {
            step: "outcome",
            profile: "professional",
            recipient: "alva",
            parcel: "camera",
            carrier: "crew",
          },
        }),
      );
      localStorage.setItem(`${scope}:intro-seen`, "true");
      localStorage.setItem(`${scope}:remaining`, "true");
      localStorage.setItem(
        `${scope}:scenes`,
        JSON.stringify({
          progress: {
            sceneIndex: index,
            phase: "choice",
            finished: false,
            answers,
          },
        }),
      );
    },
    { index, answers },
  );
  return answers;
}

for (const [index, scene] of stages.entries()) {
  test(`${scene.id}: failed choice artwork is recoverable and cannot accept invisible choices`, async ({
    page,
  }, info) => {
    test.setTimeout(60000);
    const errors: string[] = [];
    page.on("pageerror", (error) => errors.push(error.message));
    await page.emulateMedia({ reducedMotion: "reduce" });
    const answers = await checkpoint(page, index);
    let failures = 0;
    await page.route(scene.pattern, (route) => {
      failures++;
      return route.abort();
    });
    await page.reload();
    await expect(page.locator(`[data-scene="${scene.id}"]`)).toBeVisible();
    await briefing(page);
    const feedback = page.locator('[data-artwork-status="error"]');
    await expect(feedback).toBeVisible();
    await expect.poll(() => failures).toBeGreaterThan(0);
    await expect(page.locator("[data-carrier-tap-hint]")).toBeHidden();
    if (scene.id !== "crane")
      await expect(page.locator("[data-world-plane]")).toHaveCSS(
        "opacity",
        "0",
      );
    await page.screenshot({ path: info.outputPath(`${scene.id}-failure.png`) });
    const target = page.locator(`[data-hotspot="${scene.choice}"]`);
    await target.focus();
    expect
      .soft(
        await target.evaluate((element) => element === document.activeElement),
        "Unseen scene choices must not receive keyboard focus",
      )
      .toBe(false);
    const retry = feedback.getByRole("button", {
      name: "Повторить",
      exact: true,
    });
    const box = await retry.boundingBox();
    expect
      .soft(
        box?.height ?? 0,
        "Retry must keep its 44px touch target after artwork scaling",
      )
      .toBeGreaterThanOrEqual(44);
    await expect(retry).toBeInViewport();
    const before = failures;
    await retry.click();
    await expect.poll(() => failures).toBeGreaterThan(before);
    await expect(feedback).toBeVisible();
    await page.getByRole("button", { name: /^К этапу/ }).click();
    await expect(page.locator("[data-result-reader]")).toBeVisible();
    await expect(page.locator("[data-artwork-status]")).toHaveCount(0);
    const more = page.getByRole("button", {
      name: "Читать дальше",
      exact: true,
    });
    for (let n = 0; n < 40 && (await more.isVisible()); n++) await more.click();
    await page
      .getByRole("button", {
        name: ["Дальше: погрузка", "Дальше: склад", "Дальше: баржа", "Дальше: последняя миля"][index],
        exact: true,
      })
      .click();
    await briefing(page);
    await expect(feedback).toBeVisible();
    await page.unroute(scene.pattern);
    await retry.click();
    await expect(page.locator("[data-artwork-status]")).toHaveCount(0);
    await expect(page.locator("[data-carrier-tap-hint]")).toBeVisible();
    if (scene.id !== "crane")
      await expect(page.locator("[data-world-plane]")).toHaveCSS(
        "opacity",
        "1",
      );
    await expect(target).toBeVisible();
    if (scene.id === "inventory" || scene.id === "lastmile") {
      await page
        .locator("[data-world-plane] > picture > img")
        .evaluate((image: HTMLImageElement) => image.decode());
    }
    await page.screenshot({
      path: info.outputPath(`${scene.id}-recovered.png`),
    });
    await target.focus();
    await expect(target).toBeFocused();
    await page.keyboard.press("Enter");
    await page.locator("[data-choice-confirm]").click();
    await expect(page.locator("[data-result-reader]")).toBeVisible();
    expect(
      await page.evaluate(
        () =>
          JSON.parse(localStorage.getItem("quest-scene-network:scenes") ?? "{}")
            .progress.answers,
      ),
    ).toEqual({ ...answers, [scene.id]: scene.choice });
    expect(errors).toEqual([]);
  });

  test(`${scene.id}: leaving during a delayed download does not restore a stale scene`, async ({
    page,
  }) => {
    await page.emulateMedia({ reducedMotion: "reduce" });
    const errors: string[] = [];
    page.on("pageerror", (error) => errors.push(error.message));
    await checkpoint(page, index);
    let release!: () => void;
    const gate = new Promise<void>((resolve) => {
      release = resolve;
    });
    let pending = 0;
    await page.route(scene.pattern, async (route) => {
      pending++;
      await gate;
      await route.continue();
      pending--;
    });
    try {
      await page.reload({ waitUntil: "domcontentloaded" });
      await briefing(page);
      await expect.poll(() => pending).toBeGreaterThan(0);
      await expect(
        page.locator('[data-artwork-status="loading"]'),
      ).toBeVisible();
      await expect(page.locator("[data-carrier-tap-hint]")).toBeHidden();
      if (scene.id !== "crane")
        await expect(page.locator("[data-world-plane]")).toHaveCSS(
          "opacity",
          "0",
        );
      const target = page.locator(`[data-hotspot="${scene.choice}"]`);
      await target.focus();
      await expect(target).not.toBeFocused();
      await page.getByRole("button", { name: /^К этапу/ }).click();
      await expect(page.locator("[data-result-reader]")).toBeVisible();
      release();
      await expect.poll(() => pending).toBe(0);
      await page.unroute(scene.pattern);
      await expect(page.locator("[data-artwork-status]")).toHaveCount(0);
      await expect(page.locator(`[data-scene="${scene.id}"]`)).toHaveCount(0);
      const more = page.getByRole("button", {
        name: "Читать дальше",
        exact: true,
      });
      for (let n = 0; n < 40 && (await more.isVisible()); n++)
        await more.click();
      await page
        .getByRole("button", {
          name: ["Дальше: погрузка", "Дальше: склад", "Дальше: баржа", "Дальше: последняя миля"][index],
          exact: true,
        })
        .click();
      await briefing(page);
      await expect(page.locator("[data-artwork-status]")).toHaveCount(0);
      if (scene.id !== "crane")
        await expect(page.locator("[data-world-plane]")).toHaveCSS(
          "opacity",
          "1",
        );
      await expect(target).toBeVisible();
      await target.focus();
      await expect(target).toBeFocused();
      await page.keyboard.press("Enter");
      await expect(
        page.locator("[data-choice-inspection]"),
      ).toBeVisible();
      expect(errors).toEqual([]);
    } finally {
      release();
    }
  });
}
