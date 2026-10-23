import { expect, type Locator, type Page, test } from "@playwright/test";

type SceneId = "compact" | "inventory" | "crane" | "lastmile";
type Rect = { x: number; y: number; width: number; height: number };
type ArtState = { page: number; rect: Rect; sources: string[] };

const scenes: Record<SceneId, string[]> = {
  compact: ["place-1", "place-2", "place-3", "place-4", "auto"],
  inventory: ["entrance", "alphabet", "keeper", "wms"],
  crane: ["remote", "rush", "wait", "petr"],
  lastmile: ["helicopter", "rover", "robot", "pipe-carrier"],
};
const parcels = ["camera", "socks", "boat"] as const;
const recipients = ["alva", "khor", "arseniy"] as const;

function rounded(rect: Rect): Rect {
  return Object.fromEntries(
    Object.entries(rect).map(([key, value]) => [key, Math.round(value * 10) / 10]),
  ) as unknown as Rect;
}

async function artState(container: Locator, pageIndex: number): Promise<ArtState> {
  await expect(container).toBeVisible();
  const box = await container.boundingBox();
  expect(box).not.toBeNull();
  // Short phones may scroll to the controls; compare document geometry so that
  // normal page scrolling is not mistaken for a changing illustration frame.
  const scroll = await container.evaluate(() => ({ x: window.scrollX, y: window.scrollY }));
  const sources = await container.locator("img").evaluateAll(async (images) => {
    await Promise.all(
      images.map((image) => (image as HTMLImageElement).decode().catch(() => undefined)),
    );
    return images
      .filter((image) => (image as HTMLImageElement).currentSrc)
      .map((image) => new URL((image as HTMLImageElement).currentSrc).pathname);
  });
  return { page: pageIndex, rect: rounded({ ...box!, x: box!.x + scroll.x, y: box!.y + scroll.y }), sources };
}

function rectChanged(a: Rect, b: Rect, tolerance = 1.1) {
  return (Object.keys(a) as (keyof Rect)[]).some(
    (key) => Math.abs(a[key] - b[key]) > tolerance,
  );
}

async function visibleControlDefects(page: Page, scope: Locator, prefix: string) {
  return scope.locator("button:visible").evaluateAll((buttons, label) => {
    const defects: string[] = [];
    for (const [index, button] of buttons.entries()) {
      // Narrow landscape rails intentionally scroll independently of the page.
      // Verify each control can be revealed, rather than treating below-fold
      // controls in an accessible scroll surface as clipped by the viewport.
      button.scrollIntoView({ block: "nearest", inline: "nearest" });
      const rect = button.getBoundingClientRect();
      if (
        rect.left < -1 ||
        (document.documentElement.scrollHeight <= innerHeight + 1 && rect.top < -1) ||
        rect.right > innerWidth + 1 ||
        (document.documentElement.scrollHeight <= innerHeight + 1 && rect.bottom > innerHeight + 1)
      )
        defects.push(`${label}:button-${index}-viewport-clipped`);
      if (button.scrollWidth > button.clientWidth + 1 || button.scrollHeight > button.clientHeight + 1)
        defects.push(`${label}:button-${index}-text-clipped`);
      const hit = document.elementFromPoint(
        Math.min(innerWidth - 1, Math.max(0, rect.left + rect.width / 2)),
        Math.min(innerHeight - 1, Math.max(0, rect.top + rect.height / 2)),
      );
      if (!hit || !button.contains(hit)) defects.push(`${label}:button-${index}-occluded`);
    }
    return defects;
  }, prefix);
}

async function readIntro(page: Page, scene: SceneId, defects: string[]) {
  const briefing = page.locator("[data-scene-briefing]");
  const art = page.locator(`[data-world-scene="${scene}"]`);
  const states: ArtState[] = [];
  for (let index = 0; index < 30; index += 1) {
    states.push(await artState(art, index));
    defects.push(...(await visibleControlDefects(page, briefing, `intro-${index}`)));
    const forward = briefing.getByRole("button", { name: /^(Далее|К выбору)$/ });
    if (!(await forward.isVisible())) break;
    await forward.click();
    if ((await briefing.getAttribute("data-reading")) === "false") break;
  }
  const baseline = states[0]?.rect;
  const baselineSources = states[0]?.sources.join("|");
  for (const state of states.slice(1)) {
    if (baseline && rectChanged(baseline, state.rect))
      defects.push(`intro-art-rect-changed:p0-p${state.page}`);
    if (baselineSources !== state.sources.join("|"))
      defects.push(`intro-art-source-changed:p0-p${state.page}`);
  }
  return states;
}

async function resultStates(page: Page, scene: SceneId, defects: string[]) {
  const result = page.locator("[data-result-reader]");
  const art = page.locator(
    scene === "compact"
      ? '[data-world-scene="compact"]'
      : `[data-scene-consequence][data-outcome-scene="${scene}"]`,
  );
  const states: ArtState[] = [];
  for (let index = 0; index < 60; index += 1) {
    states.push(await artState(art, index));
    defects.push(...(await visibleControlDefects(page, result, `result-${index}`)));
    const reading = page.locator("[data-result-reading]");
    if (
      !(await reading.evaluate(
        (element) =>
          element.scrollWidth <= element.clientWidth + 1 &&
          element.scrollHeight <= element.clientHeight + 1,
      ))
    )
      defects.push(`result-${index}:text-clipped`);
    const forward = result.getByRole("button", { name: "Читать дальше", exact: true });
    if (!(await forward.isVisible())) break;
    const before = await page.getByTestId("result-copy").textContent();
    await forward.click();
    await expect(page.getByTestId("result-copy")).not.toHaveText(before ?? "");
  }
  const firstBySource = new Map<string, ArtState>();
  for (const state of states) {
    const sourceKey = state.sources.join("|");
    const previous = firstBySource.get(sourceKey);
    if (previous && rectChanged(previous.rect, state.rect))
      defects.push(`result-art-rect-changed:${sourceKey || "no-image"}:p${previous.page}-p${state.page}`);
    else if (!previous) firstBySource.set(sourceKey, state);
  }
  return states;
}

async function desktopChoiceAudit(page: Page, scene: SceneId) {
  if (scene !== "compact" || (page.viewportSize()?.width ?? 0) < 1200)
    return { defects: [] as string[], observations: [] as string[] };
  return page.locator('[data-scene-choice]:visible').evaluateAll((buttons) => {
    const rows = new Set(buttons.map((button) => Math.round(button.getBoundingClientRect().y / 4)));
    const wrapped = buttons.some((button) => {
      const label = button.querySelector("span:last-child");
      if (!label) return false;
      const range = document.createRange();
      range.selectNodeContents(label);
      return range.getClientRects().length > 1;
    });
    return {
      defects: rows.size > 1 ? [`desktop-compact-options:${rows.size}-rows`] : [],
      observations: wrapped ? ["desktop-compact-option-label-wrapped"] : [],
    };
  });
}

test.describe.configure({ mode: "parallel" });

for (const scene of Object.keys(scenes) as SceneId[]) {
  for (const parcel of parcels) {
    for (const recipient of recipients) {
      test(`${scene} · ${parcel} · ${recipient}`, async ({ page }, testInfo) => {
        test.setTimeout(150_000);
        const pageErrors: string[] = [];
        page.on("pageerror", (error) => pageErrors.push(error.message));
        await page.goto(
          `/scenes.html?scene=${scene}&parcel=${parcel}&recipient=${recipient}&profile=professional`,
        );
        await page.evaluate(() => document.fonts.ready);

        const introDefects: string[] = [];
        const intro = await readIntro(page, scene, introDefects);
        const desktopChoices = await desktopChoiceAudit(page, scene);
        introDefects.push(
          ...(await visibleControlDefects(page, page.locator('[data-scene-briefing]'), "choices")),
          ...desktopChoices.defects,
        );
        const available = await page.locator("[data-scene-choice]").evaluateAll((buttons) =>
          buttons.map((button) => button.getAttribute("data-scene-choice")),
        );
        expect(available).toEqual(scenes[scene]);

        const rows: unknown[] = [];
        for (const [optionIndex, option] of scenes[scene].entries()) {
          const defects = [...introDefects];
          const choice = page.locator(`[data-scene-choice="${option}"]`);
          await choice.click();
          await expect(page.locator("[data-result-reader]")).toBeVisible();
          const result = await resultStates(page, scene, defects);

          if (
            optionIndex === 0 &&
            parcel === "camera" &&
            recipient === "alva"
          ) {
            await page.screenshot({
              path: testInfo.outputPath(`representative-${scene}.png`),
              fullPage: false,
            });
          }

          rows.push({
            viewport: testInfo.project.name,
            scene,
            parcel,
            recipient,
            option,
            intro,
            result,
            defects,
            observations: desktopChoices.observations,
          });
          await page.getByRole("button", { name: "Изменить выбор", exact: true }).click();
          await expect(page.locator(`[data-scene-choice="${option}"]`)).toBeVisible();
        }

        testInfo.annotations.push({
          type: "coverage-rows",
          description: JSON.stringify(rows),
        });
        expect(pageErrors, "uncaught page errors").toEqual([]);
        expect(
          [...new Set(rows.flatMap((row) => (row as { defects: string[] }).defects))],
          "measured UX defects; see coverage-rows annotation",
        ).toEqual([]);
      });
    }
  }
}
