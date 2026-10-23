import { expect, type Locator, test } from "@playwright/test";

async function appearance(panel: Locator) {
  return panel.evaluate((node) =>
    [node, ...node.querySelectorAll("*")].map((element) => {
      const style = getComputedStyle(element);
      return Object.fromEntries(
        [
          "display",
          "height",
          "font",
          "padding",
          "margin",
          "gap",
          "grid-template-columns",
          "grid-template-rows",
          "border-radius",
          "background-color",
          "align-items",
          "justify-content",
          "text-align",
          "font-variant-numeric",
          "font-style",
          "white-space",
          ...(element.tagName === "STRONG" ? [] : ["color", "width", "border"]),
        ].map((property) => [property, style.getPropertyValue(property)]),
      );
    }),
  );
}

test("all outcomes use exactly one canonical metrics panel, not cumulative totals", async ({
  page,
}, info) => {
  await page.goto("/");
  for (const id of ["professional", "alva", "boat"])
    await page.locator(`[data-choice="${id}"]`).click();
  await page.locator('[data-carrier-choice="express"]').click();
  await page.evaluate(() => document.fonts.ready);
  const panel = page.getByRole("group", { name: "Изменение показателей" });
  const canonical = await appearance(panel);
  const icons = await panel
    .locator("svg")
    .evaluateAll((nodes) => nodes.map((node) => node.outerHTML));
  await panel.screenshot({ path: info.outputPath("carrier-metrics.png") });
  await page.getByRole("button", { name: "К следующей сцене" }).click();
  for (const [scene, id, values] of [
    ["compact", "auto", ["-4", "+3", "+5"]],
    ["inventory", "wms", ["+4", "+4", "+5"]],
    ["crane", "remote", ["+4", "+4", "+5"]],
    ["lastmile", "pipe-carrier", ["-5", "0", "-3"]],
  ] as const) {
    await expect(panel).toHaveCount(0);
    await expect(page.locator("dl")).toHaveCount(0);
    await page.locator(`[data-choice-id="${id}"]`).press("Enter");
    await expect(panel).toHaveCount(1);
    await expect(panel).toBeInViewport({ ratio: 1 });
    await expect(page.locator("dl")).toHaveCount(0);
    await expect(panel.locator("strong")).toHaveText([...values]);
    await expect(panel.locator("em")).toHaveText([
      "Энергия",
      "Эмпатия",
      "Эффективность",
    ]);
    expect(await appearance(panel)).toEqual(canonical);
    expect(
      await panel
        .locator("svg")
        .evaluateAll((nodes) => nodes.map((node) => node.outerHTML)),
    ).toEqual(icons);
    for (const value of await panel.locator("strong").all()) {
      const number = Number(await value.textContent());
      expect(await value.evaluate((node) => getComputedStyle(node).color)).toBe(
        number > 0
          ? "rgb(130, 185, 255)"
          : number === 0
            ? "rgb(211, 223, 238)"
            : "rgb(255, 155, 103)",
      );
    }
    await panel.screenshot({ path: info.outputPath(`${scene}-metrics.png`) });
    await page.screenshot({ path: info.outputPath(`${scene}-result.png`) });
    await page
      .getByRole("button", {
        name: scene === "lastmile" ? "Завершить" : "Продолжить",
        exact: true,
      })
      .click();
  }
  await expect(panel).toHaveCount(1);
  await expect(page.locator("dl")).toHaveCount(0);
});

test("each choice displays its own source score, including parcel and recipient branches", async ({
  page,
}) => {
  for (const [parcel, recipient] of [
    ["boat", "alva"],
    ["camera", "arseniy"],
    ["socks", "khor"],
  ]) {
    await page.goto(`/scenes.html?parcel=${parcel}&recipient=${recipient}`);
    const scenes = (await page.evaluate(
      async ({ parcel, recipient }) => {
        const path = "/src/scenes/ScenesGame.tsx";
        const { remainingScenes } = await import(path);
        return remainingScenes.map(
          (scene: {
            id: string;
            options: (
              context: object,
            ) => { id: string; score: Record<string, number> }[];
          }) => ({
            id: scene.id,
            options: scene
              .options({ parcel, recipient, profile: "student" })
              .map(({ id, score }) => ({ id, score })),
          }),
        );
      },
      { parcel, recipient },
    )) as {
      id: string;
      options: { id: string; score: Record<string, number> }[];
    }[];
    for (const scene of scenes) {
      await page.goto(
        `/scenes.html?scene=${scene.id}&parcel=${parcel}&recipient=${recipient}`,
      );
      for (const option of scene.options) {
        await page.locator(`[data-choice-id="${option.id}"]`).click();
        const panel = page.getByRole("group", {
          name: "Изменение показателей",
        });
        await expect(panel).toHaveCount(1);
        await expect(panel).toBeInViewport({ ratio: 1 });
        for (const [key, value] of Object.entries(option.score))
          await expect(
            panel.locator(`[data-score-key="${key}"] strong`),
          ).toHaveText(value > 0 ? `+${value}` : String(value));
        await expect(page.locator("dl")).toHaveCount(0);
        await page
          .getByRole("button", { name: "Изменить выбор", exact: true })
          .click();
        await expect(panel).toHaveCount(0);
      }
    }
  }
});
