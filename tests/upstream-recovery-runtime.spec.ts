import { expect, type Page, test } from "@playwright/test";
import { openCarrier, pickCarrier } from "./helpers/open-preparation";

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

async function proceed(page: Page, label: string) {
  const reader = page.locator("[data-result-reader]");
  const more = reader.getByRole("button", {
    name: "Читать дальше",
    exact: true,
  });
  for (let n = 0; n < 40 && (await more.isVisible()); n++) await more.click();
  await reader.getByRole("button", { name: label, exact: true }).click();
}

async function saved(page: Page) {
  return page.evaluate(() => {
    const game = JSON.parse(
      localStorage.getItem("energy-quest-save-v1") ?? "null",
    );
    const scenes = JSON.parse(
      localStorage.getItem(`${game.scope}:scenes`) ?? "null",
    );
    return {
      scope: game.scope as string,
      state: game.state,
      answers: scenes?.progress.answers ?? {},
    };
  });
}

async function inspect(page: Page, id: string) {
  const target = page.locator(`[data-hotspot="${id}"]`);
  await expect(target).toBeVisible();
  await expect(target).toBeEnabled();
  await target.focus();
  await expect(target).toBeFocused();
  await page.keyboard.press("Enter");
}

const stages = ["compact", "inventory", "crane", "lastmile"] as const;

test("reload checkpoints and an upstream gift change never retain discarded decisions", async ({
  page,
}, info) => {
  test.setTimeout(180000);
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await page.emulateMedia({ reducedMotion: "reduce" });
  await openCarrier(page, "professional", "alva", "camera");
  await page.evaluate(() =>
    localStorage.setItem("walkthrough-unrelated", "keep"),
  );
  await pickCarrier(page, "crew");
  await page.reload();
  await expect(page.locator('[data-carrier-inspection="crew"]')).toBeVisible();
  await expect(page.locator('[data-layout="result"]')).toHaveCount(0);
  expect((await saved(page)).state).toMatchObject({
    step: "carrier",
    scores: { energy: 0, empathy: 0, efficiency: 0 },
  });
  await page.locator("[data-choice-confirm]").click();
  await proceed(page, "Дальше: погрузка");

  const answers: Record<string, string> = {};
  for (const [index, choice] of ["auto", "wms", "remote", "robot"].entries()) {
    const scene = stages[index];
    await expect(page.locator(`[data-scene="${scene}"]`)).toBeVisible();
    await briefing(page);
    if (scene !== "lastmile") {
      await inspect(page, choice);
      await expect(page.locator("[data-choice-inspection]")).toBeVisible();
      // An inspection must not become a confirmed choice after a reload.
      await expect
        .poll(async () => (await saved(page)).answers)
        .toEqual(answers);
      await page.reload();
      await expect(page.locator(`[data-scene="${scene}"]`)).toBeVisible();
      await expect(page.locator("[data-result-reader]")).toHaveCount(0);
      await expect
        .poll(async () => (await saved(page)).answers)
        .toEqual(answers);
      await briefing(page);
    }
    await inspect(page, choice);
    if (scene !== "lastmile")
      await page.locator("[data-choice-confirm]").click();
    await expect(page.locator("[data-result-reader]")).toBeVisible();
    answers[scene] = choice;
    await expect.poll(async () => (await saved(page)).answers).toEqual(answers);
    await page.reload();
    await expect(
      page.locator(`[data-scene="${scene}"] [data-result-reader]`),
    ).toBeVisible();
    await expect.poll(async () => (await saved(page)).answers).toEqual(answers);
    if (scene !== "lastmile") await proceed(page, scene === "compact" ? "Дальше: склад" : scene === "inventory" ? "Дальше: баржа" : "Дальше: последняя миля");
  }

  const oldScope = (await saved(page)).scope;
  for (const scene of [...stages].reverse()) {
    await expect(
      page.locator(`[data-scene="${scene}"] [data-result-reader]`),
    ).toBeVisible();
    await page
      .getByRole("button", { name: "Изменить выбор", exact: true })
      .click();
    delete answers[scene];
    await expect.poll(async () => (await saved(page)).answers).toEqual(answers);
    await page.reload();
    await expect(page.locator(`[data-scene="${scene}"]`)).toBeVisible();
    await expect(page.locator("[data-result-reader]")).toHaveCount(0);
    await briefing(page);
    await page.getByRole("button", { name: /^К этапу/ }).click();
  }
  await expect(
    page.locator('[data-layout="result"][data-carrier="crew"]'),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Назад к машинам", exact: true })
    .click();
  await page
    .getByRole("button", { name: "К выбору подарка", exact: true })
    .click();
  await expect(page.locator('[data-preparation-step="parcel"]')).toBeVisible();
  await page.locator('[data-choice="socks"]').click();
  await expect(page.locator("[data-map-viewport]")).toBeVisible();
  await expect.poll(async () => (await saved(page)).scope).not.toBe(oldScope);
  expect(
    await page.evaluate(
      (scope) =>
        Object.keys(localStorage).filter((key) => {
          if (key.startsWith(`${scope}:`)) return true;
          return (
            key.startsWith("quest-reading-v1:") &&
            JSON.parse(key.slice("quest-reading-v1:".length))[0] === scope
          );
        }),
      oldScope,
    ),
  ).toEqual([]);
  expect(
    await page.evaluate(() => localStorage.getItem("walkthrough-unrelated")),
  ).toBe("keep");
  await page.reload();
  await expect(
    page.locator("[data-choice-inspection], [data-result-reader]"),
  ).toHaveCount(0);
  expect((await saved(page)).state).toMatchObject({
    parcel: "socks",
    scores: { energy: 0, empathy: 0, efficiency: 0 },
  });
  await pickCarrier(page, "express");
  await page.locator("[data-choice-confirm]").click();
  await proceed(page, "Дальше: погрузка");
  await expect.poll(async () => (await saved(page)).answers).toEqual({});

  for (const [index, choice] of ["auto", "wms", "remote", "rover"].entries()) {
    const scene = stages[index];
    await expect(page.locator(`[data-scene="${scene}"]`)).toBeVisible();
    await briefing(page);
    await inspect(page, choice);
    if (scene !== "lastmile")
      await page.locator("[data-choice-confirm]").click();
    await expect(page.locator("[data-result-reader]")).toBeVisible();
    await proceed(
      page,
      scene === "compact" ? "Дальше: склад" : scene === "inventory" ? "Дальше: баржа" : scene === "crane" ? "Дальше: последняя миля" : "К вручению подарка",
    );
  }
  await page.getByRole("button", { name: "Узнать, какой вы логист" }).click();
  // Express + socks/auto + WMS + remote + rover: raw 13/19/24, final 8/9/10.
  await expect(page.locator("[data-certificate-totals] strong")).toHaveText([
    "8",
    "9",
    "10",
  ]);
  await page.reload();
  await expect(page.locator("[data-certificate-totals] strong")).toHaveText([
    "8",
    "9",
    "10",
  ]);
  await page.screenshot({ path: info.outputPath("new-gift-certificate.png") });
  const context = page.context();
  await page.close();
  const reopened = await context.newPage();
  try {
    reopened.on("pageerror", (error) => errors.push(error.message));
    await reopened.goto("/");
    await expect(
      reopened.locator("[data-certificate-totals] strong"),
    ).toHaveText(["8", "9", "10"]);
    await reopened.getByRole("button", { name: /заново/i }).click();
    await expect(reopened.locator("[data-intro-enter]")).toBeVisible();
    await reopened.reload();
    await expect(reopened.locator("[data-intro-enter]")).toBeVisible();
    expect(
      await reopened.evaluate(() =>
        localStorage.getItem("walkthrough-unrelated"),
      ),
    ).toBe("keep");
    expect(errors).toEqual([]);
  } finally {
    await reopened.close();
  }
});
