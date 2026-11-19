import { expect, test } from "@playwright/test";

const scores: Record<string, number[]> = {
  rush: [-4, -3, 3],
  petr: [-2, 4, -3],
  remote: [4, 4, 5],
  rover: [4, 3, 5],
  robot: [-4, 3, -5],
  "pipe-carrier": [-5, 0, -3],
};

async function finishBriefing(page: import("@playwright/test").Page) {
  const briefing = page.locator("[data-scene-briefing]");
  for (let step = 0; step < 30 && await briefing.getAttribute("data-reading") === "true"; step++) {
    const next = briefing.getByRole("button", { name: /^(Далее|К выбору|К сцене)$/ });
    await expect(next).toBeVisible();
    await next.click();
  }
  await expect(briefing).toHaveAttribute("data-reading", "false");
}

async function checkOutcome(page: import("@playwright/test").Page, key: string, expectedScores: number[]) {
  await expect(page.locator("[data-result-reader]")).toBeVisible({ timeout: 15_000 });
  const figure = page.locator(`[data-scene-consequence="${key}"]`);
  const image = figure.locator("img");
  await expect(figure).toBeVisible();
  await expect.poll(() => image.evaluate((node: HTMLImageElement) => node.complete && node.naturalWidth > 0)).toBe(true);
  await image.evaluate((node: HTMLImageElement) => node.decode());
  const alt = await image.getAttribute("alt");
  expect(alt?.trim().length ?? 0).toBeGreaterThan(0);
  const imageBox = await image.boundingBox();
  const figureBox = await figure.boundingBox();
  const panelBox = await page.getByRole("region", { name: "Результат выбора" }).boundingBox();
  expect(imageBox).not.toBeNull();
  expect(figureBox).not.toBeNull();
  expect(panelBox).not.toBeNull();
  expect(imageBox!.width).toBeGreaterThan(0);
  expect(imageBox!.height).toBeGreaterThan(0);
  const overlap = Math.max(0, Math.min(figureBox!.x + figureBox!.width, panelBox!.x + panelBox!.width) - Math.max(figureBox!.x, panelBox!.x)) *
    Math.max(0, Math.min(figureBox!.y + figureBox!.height, panelBox!.y + panelBox!.height) - Math.max(figureBox!.y, panelBox!.y));
  expect(overlap, "outcome illustration and reading panel occupy separate regions").toBeLessThan(2);
  expect(await page.locator("[data-score-key] strong").allTextContents()).toEqual(
    expectedScores.map(value => value > 0 ? `+${value}` : `${value}`),
  );
  const text = page.getByTestId("result-copy");
  await expect(text).toBeVisible();
  await expect(text).not.toContainText(/\(подарок\)|\(персонаж\)|Ваш вязаные|Теперь он придет.*лод/);
}

for (const scene of ["crane", "lastmile"] as const)
  for (const parcel of ["camera", "socks", "boat"] as const)
    for (const recipient of ["alva", "khor", "arseniy"] as const)
      test(`${scene} ${parcel} ${recipient}: all available outcomes`, async ({ page }) => {
        const errors: string[] = [];
        page.on("pageerror", error => errors.push(error.message));
        await page.goto(`/scenes.html?scene=${scene}&parcel=${parcel}&recipient=${recipient}`);
        await finishBriefing(page);
        const choices = scene === "crane"
          ? ["rush", "petr", "remote"]
          : ["helicopter", "rover", "robot", "pipe-carrier"];
        for (const choice of choices) {
          const hotspot = page.locator(`[data-hotspot="${choice}"]`);
          await expect(hotspot).toBeVisible();
          await hotspot.click();
          await expect(page.locator("[data-choice-inspection]")).toBeVisible();
          await expect(page.locator("[data-score-key]")).toHaveCount(0);
          const confirm = page.locator("[data-choice-confirm]");
          await expect(confirm).toBeInViewport({ ratio: 0.98 });
          await confirm.click();
          const key = choice === "helicopter" && recipient !== "arseniy"
            ? "lastmile-helicopter-remote"
            : choice === "pipe-carrier" && parcel === "boat"
              ? "lastmile-pipe-carrier-boat"
              : `${scene}-${choice}`;
          const expected = choice === "helicopter"
            ? [-4, recipient === "arseniy" ? 0 : -2, 4]
            : scores[choice];
          await checkOutcome(page, key, expected);
          await page.getByRole("button", { name: "Изменить выбор", exact: true }).click();
          await expect(page.locator("[data-scene-consequence]")).toHaveCount(0);
          await expect(page.locator("[data-scene-briefing]")).toHaveAttribute("data-reading", "false");
        }
        expect(errors).toEqual([]);
      });
