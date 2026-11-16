import { expect, test } from '@playwright/test';
import { openCarrier, pickCarrier } from './helpers/open-preparation';

// Real browser measurements: no lost copy, clipped lines, or tiny trailing pages.
for (const [width, height] of [[1440, 900], [1280, 720], [390, 844], [320, 568]]) {
  test(`result reading capacity and source preservation at ${width}x${height}`, async ({ page }) => {
    test.setTimeout(180000);
    await page.setViewportSize({ width, height });
    await page.emulateMedia({ reducedMotion: 'reduce' });
    const inspect = async (key: string, expected: string) => {
      const reading = page.locator('[data-result-reading]');
      await expect(reading, key).toBeVisible({ timeout: 15000 });
      await page.evaluate(() => document.fonts.ready);
      const parts: string[] = [];
      const continuous = await page.locator('[data-continuous=true]').count();
      for (let i = 0; i < 20; i++) {
        if (!continuous) await expect.poll(() => reading.evaluate(n => n.scrollHeight - n.clientHeight), { message: key }).toBeLessThanOrEqual(1);
        await expect(page.locator('[data-result-reader] footer'), key).toBeInViewport({ ratio: .99 });
        parts.push((await page.getByTestId('result-copy').textContent())!.trim());
        const next = page.getByRole('button', { name: 'Читать дальше', exact: true });
        if (!await next.count()) break;
        await next.click();
      }
      const normalize = (s: string) => s.replace(/\s+/gu, ' ').trim();
      expect(normalize(parts.join(' ')), key).toBe(normalize(expected));
      expect(parts.every(part => part.split(/\s+/u).length >= 4), `${key}: ${JSON.stringify(parts)}`).toBe(true);
      console.log(JSON.stringify({ key, width, pages: parts.length, words: parts.map(part => part.split(/\s+/u).length) }));
      expect(parts.length, key).toBeLessThanOrEqual(width <= 320 ? 4 : 3);
    };
    await openCarrier(page, 'professional', 'khor', 'socks');
    for (const choice of ['old4', 'near', 'crew', 'express'] as const) {
      await pickCarrier(page, choice);
      await page.locator('[data-choice-confirm]').click();
      const expected = await page.evaluate(async choice => {
        const contentURL = '/src/game/content.ts';
        const outcomeURL = '/src/game/outcomeText.ts';
        const { carriers } = await import(contentURL);
        const { interpolateOutcome } = await import(outcomeURL);
        const carrier = carriers.find((c: { id: string }) => c.id === choice);
        return interpolateOutcome([carrier.resultTitle, carrier.resultBody].filter(Boolean).join(' '), 'Хабт', 'вязаные носки');
      }, choice);
      await inspect(`carrier:${choice}`, expected);
      await page.getByRole('button', { name: 'Изменить выбор', exact: true }).click();
    }
    for (const scene of ['compact', 'inventory', 'crane', 'lastmile']) {
      await page.goto(`/scenes.html?scene=${scene}&parcel=boat&recipient=khor`);
      const condition = page.getByRole('region', { name: 'Условие задания', exact: true });
      for (let i = 0; i < 30 && await condition.isVisible(); i++) await condition.getByRole('button', { name: /^(Далее|К выбору)$/ }).click();
      const options: { id: string; expected: string }[] = await page.evaluate(async scene => {
        const scenesURL = '/src/scenes/sceneFlow.ts';
        const linksURL = '/src/components/ScenarioLink.tsx';
        const { remainingScenes } = await import(scenesURL);
        const { separateScenarioLink } = await import(linksURL);
        const definition = remainingScenes.find((s: { id: string }) => s.id === scene);
        return definition.options({ parcel: 'boat', recipient: 'khor', profile: 'student' }).map((option: { id: string; result: string[] }) => ({
          id: option.id,
          expected: separateScenarioLink(option.result.map(p => scene === 'inventory' ? p : p.replace(/^\s*Результат:\s*«?(.)?/iu, (_prefix, first = '') => first.toLocaleUpperCase('ru-RU')))).text,
        }));
      }, scene);
      for (const { id, expected } of options) {
        await page.locator(`[data-hotspot="${id}"]`).click();
        await page.locator('[data-choice-confirm]').click();
        await inspect(`${scene}:${id}`, expected);
        await page.getByRole('button', { name: 'Изменить выбор', exact: true }).click();
      }
    }
  });
}
