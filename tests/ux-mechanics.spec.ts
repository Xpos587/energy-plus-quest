import { expect, type Page, test } from "@playwright/test";

async function readCondition(page: Page) {
  const card = page.getByRole("region", {
    name: "Условие задания",
    exact: true,
  });
  await expect(card).toBeVisible();
  for (let i = 0; i < 30 && (await card.isVisible()); i++) {
    await card
      .getByRole("button", { name: /^(Далее|К выбору|К сцене)$/ })
      .click();
  }
  await expect(card).toBeHidden();
}
async function reviseResult(page: Page) {
  for (let i = 0; i < 60 && await page.getByRole("button", { name: "Назад по рассказу", exact: true }).count(); i++)
    await page.getByRole("button", { name: "Назад по рассказу", exact: true }).click();
  await page.getByRole("button", { name: /^(Изменить выбор|Назад к машинам)$/ }).click();
}
async function checkResult(page: Page, expected?: string) {
  await page.evaluate(() => document.fonts.ready);
  const reader = page.locator("[data-result-reading]");
  await expect(reader).toBeVisible();
  const artwork = page.locator('[data-result-art], [data-scene-consequence]');
  for (const frame of await artwork.all()) {
    await expect(frame).not.toHaveAttribute('data-pan-viewport');
    expect(await frame.evaluate(el => {
      el.scrollLeft = 100;
      return el.scrollWidth <= el.clientWidth + 1 && el.scrollLeft === 0;
    })).toBe(true);
  }
  await expect(page.getByText("Что произошло", { exact: true })).toHaveCount(0);
  const parts: string[] = [];
  for (let beat = 0; beat < 60; beat++) {
    parts.push((await page.getByTestId("result-copy").textContent()) ?? "");
    expect(await reader.evaluate(el => el.scrollHeight <= el.clientHeight + 2)).toBe(true);
    await expect(page.locator("[data-score-key]")).toHaveCount(3);
    for (const action of await page.locator("[data-sheet-panel] button").all()) {
      if (await action.isVisible()) await expect(action).toBeInViewport({ ratio: 1 });
    }
    const nextBeat = page.getByRole("button", { name: "Читать дальше", exact: true });
    if (!(await nextBeat.count())) break;
    const before = await page.getByTestId("result-copy").textContent();
    await nextBeat.click();
    await expect(page.getByTestId("result-copy")).not.toHaveText(before ?? "");
  }
  const narrative = parts.join("");
  if (expected) expect(narrative).toBe(expected);
  expect(narrative).not.toMatch(/\(подарок\)|\(персонаж\)/);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1)).toBe(true);
  await expect(page.getByRole("button", { name: "Читать дальше", exact: true })).toHaveCount(0);
  return narrative;
}

for (const scene of ["compact", "inventory", "crane", "lastmile"]) {
  test(`${scene}: all context-dependent options have complete reachable consequences`, async ({
    page,
  }, info) => {
    const errors: string[] = [];
    page.on("pageerror", (e) => errors.push(e.message));
    for (const [parcel, recipient] of [
      ["camera", "alva"],
      ["socks", "khor"],
      ["boat", "arseniy"],
    ]) {
      await page.goto(
        `/scenes.html?scene=${scene}&parcel=${parcel}&recipient=${recipient}`,
      );
      await readCondition(page);
      const options = (await page.evaluate(
        async ({ scene, parcel, recipient }) => {
          const moduleUrl = "/src/scenes/ScenesGame.tsx";
          const { remainingScenes } = await import(moduleUrl);
          return remainingScenes
            .find((s: { id: string }) => s.id === scene)
            .options({ parcel, recipient, profile: "professional" })
            .map(
              (o: {
                id: string;
                result: string[];
                score: Record<string, number>;
              }) => ({ id: o.id, result: o.result, score: o.score }),
            );
        },
        { scene, parcel, recipient },
      )) as { id: string; result: string[]; score: Record<string, number> }[];
      for (const option of options) {
        const choice = page.locator(
          `[data-choice-id="${option.id}"]:not([data-callout-target])`,
        );
        await choice.click();
        await expect(page.locator("[data-score-key]")).toHaveCount(0);
        await expect(page.locator("[data-choice-confirm]")).toBeInViewport({
          ratio: 1,
        });
        await page.locator("[data-choice-cancel]").click();
        await expect(choice).toBeFocused();
        await choice.click();
        await page.locator("[data-choice-confirm]").click();
        const expected = option.result
          .map((paragraph) =>
            scene === "inventory"
              ? paragraph
              : paragraph.replace(
                  /^\s*Результат:\s*«?(.)?/iu,
                  (_prefix, first = "") => first.toLocaleUpperCase("ru-RU"),
                ),
          )
          .join("\n\n")
          .replace(
            /\s*Узнать больше(?: об Express| о WMS Inventory\.)?\s*$/u,
            "",
          );
        const image = page.locator(
          scene === "compact"
            ? "[data-compact-consequence] img"
            : "[data-scene-consequence] img",
        );
        await image.evaluate((el: HTMLImageElement) => el.decode());
        await checkResult(page, expected);
        const delta = await page
          .locator("[data-score-key] strong")
          .allTextContents();
        expect(delta).toEqual(
          ["energy", "empathy", "efficiency"].map((k) =>
            option.score[k] > 0
              ? `+${option.score[k]}`
              : String(option.score[k]),
          ),
        );
        if (scene === "compact")
          await expect(
            page.locator("[data-compact-consequence] img"),
          ).toBeVisible();
        if (parcel === "camera")
          await page.screenshot({
            path: info.outputPath(`${scene}-${option.id}.png`),
          });
        await reviseResult(page);
        await expect(page.locator("[data-score-key]")).toHaveCount(0);
        if (
          await page
            .getByRole("region", { name: "Условие задания", exact: true })
            .isVisible()
        )
          await readCondition(page);
      }
    }
    expect(errors).toEqual([]);
  });
}

test("the player can reach the whole condition button beside the task", async ({
  page,
}) => {
  await page.goto("/");
  for (const id of ["professional", "alva", "camera"])
    await page.locator(`[data-choice="${id}"]`).click();
  await readCondition(page);
  const condition = page.getByRole("button", { name: "Условие", exact: true });
  const bounds = await condition.boundingBox();
  expect(bounds).not.toBeNull();
  expect(bounds!.x).toBeGreaterThanOrEqual(0);
  expect(bounds!.x + bounds!.width).toBeLessThanOrEqual(
    page.viewportSize()!.width,
  );
  expect(bounds!.y + bounds!.height).toBeLessThanOrEqual(
    page.viewportSize()!.height,
  );
  await condition.click();
  await expect(
    page.getByRole("region", { name: "Условие задания", exact: true }),
  ).toBeVisible();
});

test("five-scene journey supports rereading, cancellation, revising and reloading before finishing", async ({
  page,
}, info) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.goto("/");
  for (const id of ["professional", "alva", "camera"])
    await page.locator(`[data-choice="${id}"]`).click();
  for (const [scene, id] of [
    ["carrier", "crew"],
    ["compact", "auto"],
    ["inventory", "wms"],
    ["crane", "remote"],
    ["lastmile", "rover"],
  ]) {
    await readCondition(page);
    await page.getByRole("button", { name: "Условие", exact: true }).click();
    await readCondition(page);
    const choice = page.locator(
      scene === "carrier"
        ? `[data-carrier-choice="${id}"]`
        : `[data-choice-id="${id}"]:not([data-callout-target])`,
    );
    await choice.click();
    await expect(page.locator("[data-score-key]")).toHaveCount(0);
    await page.locator("[data-choice-cancel]").click();
    await expect(choice).toBeFocused();
    await choice.click();
    await page.locator("[data-choice-confirm]").click();
    const text = await checkResult(page);
    const scores = await page
      .locator("[data-score-key] strong")
      .allTextContents();
    await page.reload();
    if (!text) throw new Error("Missing result narrative after confirmation");
    await checkResult(page, text);
    expect(
      await page.locator("[data-score-key] strong").allTextContents(),
    ).toEqual(scores);
    if (scene === "carrier") {
      await reviseResult(page);
      await expect(page.locator("[data-score-key]")).toHaveCount(0);
      if (
        await page
          .getByRole("region", { name: "Условие задания", exact: true })
          .isVisible()
      )
        await readCondition(page);
      await choice.click();
      await page.locator("[data-choice-confirm]").click();
      await checkResult(page);
      expect(
        await page.locator("[data-score-key] strong").allTextContents(),
      ).toEqual(scores);
    }
    if (scene !== "compact") {
      await page
        .locator(
          scene === "carrier"
            ? "[data-result-art] img"
            : "[data-scene-consequence] img",
        )
        .evaluate((el: HTMLImageElement) => el.decode());
    }
    await page.screenshot({ path: info.outputPath(`journey-${scene}.png`) });
    await page
      .getByRole("button", {
        name:
          scene === "carrier"
            ? "К следующей сцене"
            : scene === "lastmile"
              ? "Завершить"
              : "Продолжить",
        exact: true,
      })
      .click();
  }
  await expect(
    page.getByRole("status").filter({ hasText: "Завершено" }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Завершено", exact: true }),
  ).toHaveCount(0);
  await page.reload();
  await expect(
    page.getByRole("status").filter({ hasText: "Завершено" }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Пройти сцены заново", exact: true })
    .click();
  await expect(page.locator('[data-choice="professional"]')).toBeVisible();
  expect(errors).toEqual([]);
});

test("carrier: every truck produces its own complete result after confirmation", async ({
  page,
}, info) => {
  await page.goto("/");
  for (const id of ["professional", "alva", "camera"])
    await page.locator(`[data-choice="${id}"]`).click();
  await readCondition(page);
  const ids = await page
    .locator("[data-carrier-choice]")
    .evaluateAll((els) =>
      els.map((el) => el.getAttribute("data-carrier-choice")),
    );
  for (const id of ids) {
    await page.locator(`[data-carrier-choice="${id}"]`).click();
    await expect(page.locator("[data-score-key]")).toHaveCount(0);
    await page.locator("[data-choice-confirm]").click();
    const expected = await page.evaluate(async (id) => {
      const contentUrl = "/src/game/content.ts";
      const outcomeUrl = "/src/game/outcomeText.ts";
      const { findCarrier, findRecipient, findParcel } = await import(
        contentUrl
      );
      const { interpolateOutcome } = await import(outcomeUrl);
      return interpolateOutcome(
        findCarrier(id).resultBody,
        findRecipient("alva").title,
        findParcel("camera").accusativeTitle,
      ).replace(/\s*Узнать больше(?: об Express)?\s*$/u, "");
    }, id);
    await page
      .locator("[data-result-art] img")
      .evaluate((el: HTMLImageElement) => el.decode());
    await checkResult(page, expected);
    await page.screenshot({ path: info.outputPath(`carrier-${id}.png`) });
    await reviseResult(page);
    await expect(
      page.getByRole("region", { name: "Условие задания", exact: true }),
    ).toBeHidden();
    await page.reload();
    await expect(
      page.getByRole("region", { name: "Условие задания", exact: true }),
    ).toBeHidden();
    await page.getByRole("button", { name: "Условие", exact: true }).click();
    await readCondition(page);
  }
});

test("touch: reading a long consequence keeps the scene still and actions reachable", async ({
  browser,
  page,
}, info) => {
  test.skip(page.viewportSize()?.width !== 320);
  const phone = await browser.newPage({
    viewport: { width: 320, height: 568 },
    isMobile: true,
    hasTouch: true,
    reducedMotion: "reduce",
  });
  try {
    await phone.goto("/scenes.html?scene=inventory&parcel=socks");
    await readCondition(phone);
    await phone
      .locator('[data-choice-id="keeper"]:not([data-callout-target])')
      .click();
    await phone.locator("[data-choice-confirm]").click();
    await phone.evaluate(() => document.fonts.ready);
    await phone
      .locator("[data-scene-consequence] img")
      .evaluate((el: HTMLImageElement) => el.decode());
    await checkResult(phone);
    await expect(phone.locator('[data-scene-panning="true"]')).toHaveCount(0);
    await expect(phone.getByRole("button", { name: "Продолжить", exact: true })).toBeInViewport({ ratio: 1 });
    await phone.screenshot({ path: info.outputPath("touch-reader.png") });
  } finally {
    await phone.close();
  }
});

test("back arrow returns to the previous scene from both reading and choosing", async ({
  page,
}) => {
  await page.goto("/");
  for (const id of ["professional", "alva", "camera"])
    await page.locator(`[data-choice="${id}"]`).click();
  await readCondition(page);
  await page.locator('[data-carrier-choice="crew"]').click();
  await page.locator("[data-choice-confirm]").click();
  await checkResult(page);
  await page
    .getByRole("button", { name: "К следующей сцене", exact: true })
    .click();
  await readCondition(page);
  await page
    .locator('[data-choice-id="auto"]:not([data-callout-target])')
    .click();
  await page.locator("[data-choice-confirm]").click();
  const result = await checkResult(page);
  const scores = await page
    .locator("[data-score-key] strong")
    .allTextContents();
  for (const phase of ["reading", "choosing"]) {
    await page.getByRole("button", { name: "Продолжить", exact: true }).click();
    await expect(
      page.getByRole("region", { name: "Условие задания", exact: true }),
    ).toBeVisible();
    if (phase === "choosing") await readCondition(page);
    await page.getByRole("button", { name: "Назад", exact: true }).click();
    await checkResult(page, result);
    expect(
      await page.locator("[data-score-key] strong").allTextContents(),
    ).toEqual(scores);
    await page.reload();
    await checkResult(page, result);
  }
});

test("pan hints keep the question readable until the player actually drags", async ({
  page,
}) => {
  test.skip(
    (page.viewportSize()?.width ?? 0) > 600,
    "Pan hint is a narrow-screen interaction",
  );
  for (const scene of ["compact", "inventory"]) {
    await page.goto(`/scenes.html?scene=${scene}&parcel=camera`);
    await readCondition(page);
    const question = page.getByTestId("scene-question");
    await expect(
      page.getByRole("status").filter({ hasText: "Листайте сцену" }),
    ).toBeVisible();
    await expect(question).toHaveCSS("opacity", "1");
    const viewport = page.locator("[data-pan-viewport]");
    const rect = await viewport.boundingBox();
    if (!rect) throw new Error("Missing pan viewport");
    const x = rect.x + rect.width * 0.7;
    const y = 220;
    await page.mouse.move(x, y);
    await page.mouse.down();
    await page.mouse.move(x - 70, y, { steps: 10 });
    await expect(page.locator('[data-scene-panning="true"]')).toHaveCount(1);
    await expect(question).toHaveCSS("opacity", "0.28");
    await page.mouse.up();
    await expect(question).toHaveCSS("opacity", "1");
  }
});

test("pan guidance does not cover the snow rover choice", async ({
  page,
}, info) => {
  await page.goto("/scenes.html?scene=lastmile&parcel=camera");
  await readCondition(page);
  const hint = page.getByRole("status").filter({ hasText: "Листайте сцену" });
  const rover = page.locator('[data-choice-id="rover"]');
  const canPan = await page
    .locator("[data-pan-viewport]")
    .evaluate((el) => el.scrollWidth - el.clientWidth > 8);
  if (!canPan) {
    await expect(hint).toHaveCount(0);
    await expect(rover).toBeInViewport();
    await rover.click();
    await expect(page.locator("[data-choice-confirm]")).toBeInViewport({
      ratio: 1,
    });
    return;
  }
  await expect(hint).toBeVisible();
  await expect(rover).toBeInViewport();
  const hintRect = await hint.boundingBox();
  const roverRect = await rover.boundingBox();
  if (!hintRect || !roverRect) throw new Error("Missing hint or snow rover");
  const overlap =
    Math.max(
      0,
      Math.min(hintRect.x + hintRect.width, roverRect.x + roverRect.width) -
        Math.max(hintRect.x, roverRect.x),
    ) *
    Math.max(
      0,
      Math.min(hintRect.y + hintRect.height, roverRect.y + roverRect.height) -
        Math.max(hintRect.y, roverRect.y),
    );
  await page.screenshot({ path: info.outputPath("lastmile-hint.png") });
  expect(overlap).toBe(0);
  await rover.click();
  await expect(page.locator("[data-choice-confirm]")).toBeInViewport({
    ratio: 1,
  });
});

test("warehouse result keeps the illustration clear of its compact header", async ({ page }, info) => {
  test.skip(info.project.name !== "320x568" && info.project.name !== "375x667" && info.project.name !== "780x992");
  await page.goto('/scenes.html?scene=inventory&parcel=boat&recipient=khor');
  await readCondition(page);
  await page.locator('[data-choice-id="alphabet"]:not([data-callout-target])').click();
  await page.locator('[data-choice-confirm]').click();
  await page.locator('[data-scene-consequence] img').evaluate((el: HTMLImageElement) => el.decode());
  await page.screenshot({ path: info.outputPath('warehouse-before-reading.png') });
  await expect(page.locator('header[data-header-result] button')).toHaveCount(0);
  const header = await page.locator('header[data-header-result]').boundingBox();
  expect(header!.height).toBeLessThanOrEqual(60);
  const art = await page.locator('[data-scene-consequence]').boundingBox();
  const panel = await page.locator('[data-result]').boundingBox();
  expect(art!.y).toBeGreaterThanOrEqual(header!.y + header!.height);
  expect(art!.y + art!.height).toBeLessThanOrEqual(panel!.y);
  expect(art!.y - header!.y - header!.height).toBeLessThanOrEqual(12);
  expect(panel!.y - art!.y - art!.height).toBeLessThanOrEqual(12);
  await checkResult(page);
  await page.screenshot({ path: info.outputPath('warehouse-after-reading.png') });
  await reviseResult(page);
  await expect(page.getByRole("region", { name: "Условие задания", exact: true })).toBeHidden();
  await expect(page.locator('[data-choice-id="alphabet"]:not([data-callout-target])')).toBeVisible();
});

test("barge and last mile results keep the picture, title and actions separate", async ({ page }, info) => {
  test.skip(!["320x568", "375x667", "780x992"].includes(info.project.name));
  for (const [scene, choice] of [["crane", "remote"], ["lastmile", "rover"]]) {
    await page.goto(`/scenes.html?scene=${scene}&parcel=boat&recipient=khor`);
    await readCondition(page);
    await page.locator(`[data-choice-id="${choice}"]:not([data-callout-target])`).click();
    await page.locator('[data-choice-confirm]').click();
    await page.locator('[data-scene-consequence] img').evaluate((el: HTMLImageElement) => el.decode());
    const header = (await page.locator('header[data-header-result]').boundingBox())!;
    const art = (await page.locator('[data-scene-consequence]').boundingBox())!;
    const panel = (await page.locator('[data-result]').boundingBox())!;
    const title = (await page.locator('[data-result] h2').boundingBox())!;
    expect(title.height).toBeGreaterThan(15);
    expect(art.y).toBeGreaterThanOrEqual(header.y + header.height);
    expect(art.y - header.y - header.height).toBeLessThanOrEqual(12);
    expect(panel.y).toBeGreaterThanOrEqual(art.y + art.height);
    expect(panel.y - art.y - art.height).toBeLessThanOrEqual(12);
    await page.screenshot({ path: info.outputPath(`${scene}-first.png`) });
    await checkResult(page);
    await page.screenshot({ path: info.outputPath(`${scene}-last.png`) });
  }
});

test("barge revision returns to the same visible choices", async ({ page }, info) => {
  test.skip((page.viewportSize()?.width ?? 0) > 600);
  await page.goto('/scenes.html?scene=crane&parcel=boat&recipient=khor');
  await readCondition(page);
  const map = page.locator('[data-world-scene="crane"]');
  await page.evaluate(() => document.fonts.ready);
  await map.locator('img').evaluate((el: HTMLImageElement) => el.decode());
  await expect.poll(() => map.evaluate(el => el.scrollWidth - el.clientWidth)).toBeGreaterThan(50);
  await page.locator('[data-choice-id="wait"]').scrollIntoViewIfNeeded();
  await page.locator('[data-choice-id="wait"]').click();
  // Compare with the view at the decision, after native focus/scroll has settled.
  const position = await map.evaluate(el => el.scrollLeft);
  expect(position).toBeGreaterThan(50);
  await page.locator('[data-choice-confirm]').click();
  await checkResult(page);
  await reviseResult(page);
  await expect(page.getByRole('region', {name:'Условие задания', exact:true})).toBeHidden();
  await expect.poll(() => map.evaluate(el => el.scrollLeft)).toBeCloseTo(position, 0);
  await expect(page.locator('[data-choice-id="wait"]')).toBeInViewport({ratio:1});
  await page.screenshot({path:info.outputPath('barge-revised-choice.png')});
});
