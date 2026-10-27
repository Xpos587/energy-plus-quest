import { expect, test } from '@playwright/test';

const choices: Record<string, string[]> = {
  carrier: ['old', 'near', 'crew', 'old4', 'express'],
  compact: ['place-1', 'place-2', 'place-3', 'place-4', 'auto'],
  inventory: ['entrance', 'keeper', 'alphabet', 'wms'],
  crane: ['rush', 'wait', 'petr', 'remote'],
  lastmile: ['helicopter', 'rover', 'robot', 'pipe-carrier'],
};

for (const [scene, ids] of Object.entries(choices)) {
  test(`${scene}: every answer is discoverable without moving the picture`, async ({ page }, info) => {
    await page.goto(scene === 'carrier' ? '/' : `/scenes.html?scene=${scene}&parcel=boat&recipient=khor`);
    if (scene === 'carrier') {
      for (const name of [/^Далее/, /^Начать/]) {
        const intro = page.getByRole('button', { name });
        if (await intro.isVisible()) await intro.click();
      }
      for (const id of ['professional', 'khor', 'boat']) await page.locator(`[data-choice="${id}"]`).click();
    }
    const condition = page.getByRole('region', { name: 'Условие задания', exact: true });
    for (let i = 0; i < 30 && await condition.isVisible(); i++) {
      await condition.getByRole('button', { name: /^(Далее|К выбору|К сцене)$/ }).click();
    }
    const attr = scene === 'crane' ? 'data-hotspot' : 'data-scene-choice';
    const answers = page.locator(`[${attr}]`);
    await expect(answers).toHaveCount(ids.length);
    await page.mouse.move(0, 0);
    await page.screenshot({ path: `.tmp-work/choice-buttons/${scene}-${info.project.name}-initial.png` });
    for (const id of ids) {
      const answer = page.locator(`[${attr}="${id}"]`);
      await expect(answer).toBeVisible();
      await expect(answer).toBeInViewport({ ratio: 1 });
      const bounds = await answer.boundingBox();
      expect(bounds!.height).toBeGreaterThanOrEqual(44);
      await answer.click();
      await expect(page.locator('[data-choice-confirm]')).toBeVisible();
      await expect(page.locator('[data-result-reader]')).toHaveCount(0);
      await page.locator('[data-choice-cancel]').click();
      await expect(answer).toBeFocused();
    }
    await page.screenshot({ path: `.tmp-work/choice-buttons/${scene}-${info.project.name}.png` });
    await page.locator(`[${attr}="${ids.at(-1)}"]`).click();
    await page.locator('[data-choice-confirm]').click();
    await expect(page.locator('[data-result-reader]')).toBeVisible();
    await page.getByRole('button', { name: /Изменить выбор|К машинам|Назад к машинам/ }).click();
    await expect(condition).not.toBeVisible();
    await expect(answers).toHaveCount(ids.length);
    for (const answer of await answers.all()) await expect(answer).toBeInViewport({ ratio: 1 });
  });
}
