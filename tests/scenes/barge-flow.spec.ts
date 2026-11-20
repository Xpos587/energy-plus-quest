import { expect, test } from "@playwright/test";
import { scenarioParagraph } from "../helpers/scenario-copy";

const source = ["53B56B9E", "62451EC9", "6F7BE91B"].map((id) =>
  scenarioParagraph(id),
);

for (const viewport of [
  { width: 320, height: 568 },
  { width: 390, height: 844 },
  { width: 1440, height: 900 },
]) {
  test(`barge story and on-image choices at ${viewport.width}px`, async ({
    page,
  }, info) => {
    await page.setViewportSize(viewport);
    await page.goto("/scenes.html?scene=crane&parcel=camera&recipient=alva");

    expect(source.join(" ")).toMatch(
      /беспилотном тягаче[\s\S]*кран[\s\S]*Иван/,
    );
    await expect(page.getByTestId("scene-question")).toContainText(
      "Как погрузить подарок на баржу?",
    );
    // One screen (call 17.11): the story and the quay choice together, no «К выбору» step.
    await expect(page.getByRole("button", { name: /^(Далее|К выбору)$/ })).toHaveCount(0);
    await expect(page.locator('[data-scene-briefing][data-reading="true"]')).toHaveCount(0);
    // The first paragraph names the parcel in place of «(название сюрприза)».
    await expect(page.getByTestId("scene-question")).toContainText("Ваш фотоаппарат уже на причале");
    for (const text of source.slice(1)) await expect(page.getByTestId("scene-question")).toContainText(text);
    // Owner 20.11: one choice UI — the pins on the quay, no option buttons under the picture.
    await expect(page.locator('[data-scene-choice]')).toHaveCount(0);

    for (const id of ["remote", "rush", "petr"]) {
      const marker = page.locator(`[data-hotspot="${id}"]`);
      await marker.scrollIntoViewIfNeeded();
      await expect(marker).toBeInViewport();
      await expect(marker).toBeVisible();
      await expect(marker).toBeEnabled();
      await expect(page.locator("[data-score-key]")).toHaveCount(0);
    }
    await page.locator('[data-hotspot="remote"]').click();
    await expect(page.locator("[data-score-key]")).toHaveCount(0);
    await page.locator("[data-choice-confirm]").click();
    // The quay plays the consequence first, then the result reads.
    await expect(page.locator("[data-playing]")).toHaveCount(1);
    await expect(page.locator("[data-score-key]")).toHaveCount(3, { timeout: 15_000 });
    const resultImage = page.locator(
      '[data-scene-consequence="crane-remote"] img',
    );
    await expect(resultImage).toHaveAttribute(
      "src",
      /\/scene-art\/barge-v7\/outcome-remote\.webp/,
    );
    await resultImage.evaluate(async (image: HTMLImageElement) =>
      image.decode(),
    );
    if (viewport.width !== 320) {
      await page.screenshot({ path: info.outputPath("crane-remote-result.png") });
    }
    expect(
      await resultImage.evaluate(
        (image: HTMLImageElement) => new URL(image.currentSrc).pathname,
      ),
    ).toBe(
      // The desktop rail (≥1001×701) and the tall phone result row both take the near-square cut
      // (SceneOutcomeArt: the tall still lost the crane above the copy).
      (viewport.width > 1000 && viewport.height > 700) ||
        (viewport.width <= 1000 && viewport.height >= 701 && viewport.height > viewport.width)
        ? "/scene-art/barge-v7/outcome-remote-rail.webp"
        : "/scene-art/barge-v7/outcome-remote.webp",
    );
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    ).toBe(true);
    await expect(
      page.locator('dialog[data-outcome-preview="crane"]'),
    ).toHaveCount(0);
  });
}
