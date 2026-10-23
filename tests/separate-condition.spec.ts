import { expect, type Page, test } from "@playwright/test";

const scenes = ["compact", "inventory", "crane", "lastmile"];
const answers = {
  compact: "place-1",
  inventory: "wms",
  crane: "remote",
  lastmile: "rover",
};
async function fits(page: Page) {
  expect(
    await page.evaluate(
      () =>
        document.documentElement.scrollHeight <= innerHeight &&
        document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  const next = page.locator('[aria-label="Условие задания"] button').last();
  if (await next.isVisible()) await expect(next).toBeInViewport({ ratio: 1 });
}
async function read(page: Page) {
  const seen = [];
  for (
    let n = 0;
    n < 50 &&
    (await page
      .locator('[data-scene-briefing][data-reading="true"]')
      .isVisible());
    n++
  ) {
    await fits(page);
    const body = page.getByTestId("scene-intro");
    await expect(body).toBeFocused();
    seen.push(await body.innerText());
    await page.getByRole("button", { name: /^(Далее|К выбору)$/ }).click();
  }
  return seen.join(" ").replace(/\s+/g, " ").trim();
}
for (const [width, height] of [
  [320, 568],
  [390, 844],
  [844, 390],
  [1440, 900],
])
  for (const [sceneIndex, scene] of scenes.entries())
    test(`${scene}: separate condition, replay, reload and result return ${width}x${height}`, async ({
      page,
    }) => {
      await page.setViewportSize({ width, height });
      await page.goto("/");
      await page.evaluate(
        ({ sceneIndex, scenes, answers }) => {
          localStorage.clear();
          const scope = "quest-r2-condition";
          localStorage.setItem(
            "energy-quest-save-v1",
            JSON.stringify({
              version: 1,
              scope,
              state: {
                step: "outcome",
                profile: "student",
                recipient: "khor",
                parcel: "boat",
                carrier: "old",
              },
            }),
          );
          localStorage.setItem(scope + ":remaining", "true");
          localStorage.setItem(
            scope + ":scenes",
            JSON.stringify({
              progress: {
                sceneIndex,
                phase: "choice",
                answers: Object.fromEntries(
                  scenes
                    .slice(0, sceneIndex)
                    .map((id) => [id, answers[id as keyof typeof answers]]),
                ),
                finished: false,
              },
            }),
          );
        },
        { sceneIndex, scenes, answers },
      );
      await page.reload();
      await expect(page.locator("[data-scene-briefing]")).toHaveAttribute(
        "data-reading",
        "true",
      );
      const expected = await page.evaluate(
        async ({ sceneIndex, scene }) => {
          const load = (url: string) => import(/* @vite-ignore */ url);
          const { remainingScenes } = await load("/src/scenes/ScenesGame.tsx");
          const all = remainingScenes[sceneIndex].intro({
            profile: "student",
            recipient: "khor",
            parcel: "boat",
          });
          return (
            scene === "compact" || scene === "lastmile" ? all.slice(0, -1) : all
          )
            .join(" ")
            .replace(/\s+/g, " ")
            .trim();
        },
        { sceneIndex, scene },
      );
      expect(await read(page)).toBe(expected);
      await fits(page);
      await expect(page.locator("[data-scene-briefing]")).toHaveAttribute(
        "data-reading",
        "false",
      );
      expect(
        await page.getByTestId("scene-question").innerText(),
      ).not.toContain(expected);
      const about = page.getByRole("button", { name: "О задаче", exact: true });
      await expect(about).toBeFocused();
      await about.click();
      expect(await read(page)).toBe(expected);
      await page
        .locator(
          `[data-scene-choice="${answers[scene as keyof typeof answers]}"]`,
        )
        .click();
      await expect(page.locator("[data-result]")).toBeVisible();
      await page
        .getByRole("button", { name: "Изменить выбор", exact: true })
        .click();
      await expect(page.locator("[data-scene-briefing]")).toHaveAttribute(
        "data-reading",
        "false",
      );
      await fits(page);
      await expect(
        page.locator(
          `[data-scene-choice="${answers[scene as keyof typeof answers]}"]`,
        ),
      ).toBeFocused();
      await page.reload();
      await expect(page.locator("[data-scene-briefing]")).toHaveAttribute(
        "data-reading",
        "false",
      );
      await about.click();
      expect(await read(page)).toBe(expected);
    });
