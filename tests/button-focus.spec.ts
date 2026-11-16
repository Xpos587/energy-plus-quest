import { expect, test } from '@playwright/test';

for (const scene of ['carrier', 'inventory', 'crane', 'lastmile']) {
  test(`${scene}: task button has no pointer ring, but keeps keyboard focus`, async ({ page, isMobile }, info) => {
    await page.addInitScript(scene => {
      const scope = 'quest-button-focus';
      const scenes = ['compact', 'inventory', 'crane', 'lastmile'];
      localStorage.clear(); sessionStorage.clear();
      localStorage.setItem('energy-quest-save-v1', JSON.stringify({ version: 1, scope, state: {
        step: scene === 'carrier' ? 'carrier' : 'outcome', profile: 'professional', recipient: 'khor', parcel: 'socks',
        ...(scene === 'carrier' ? {} : { carrier: 'express' }),
      } }));
      localStorage.setItem(`${scope}:intro-seen`, 'true');
      if (scene !== 'carrier') {
        localStorage.setItem(`${scope}:remaining`, 'true');
        const sceneIndex = scenes.indexOf(scene);
        localStorage.setItem(`${scope}:scenes`, JSON.stringify({ progress: {
          sceneIndex, phase: 'choice', finished: false,
          answers: Object.fromEntries(Object.entries({ compact: 'auto', inventory: 'wms', crane: 'remote' }).filter(([id]) => scenes.indexOf(id) < sceneIndex)),
        }, briefed: scenes }));
      }
    }, scene);
    await page.goto('/');
    const briefing = page.locator('[data-scene-briefing]');
    const task = briefing.getByRole('button', { name: 'Задание', exact: true });
    const pointer = async (button: typeof task) => isMobile ? button.tap() : button.click();
    const close = async (keyboard = false) => {
      for (let n = 0; n < 30 && await briefing.getAttribute('data-reading') === 'true'; n++) {
        const next = briefing.getByRole('button', { name: /^(Далее|К выбору|К сцене)$/ });
        if (keyboard) {
          for (let tab = 0; tab < 15 && !await next.evaluate(el => el === document.activeElement); tab++) await page.keyboard.press('Tab');
          await expect(next).toBeFocused();
          await page.keyboard.press('Enter');
        } else await pointer(next);
      }
    };
    await close();
    await pointer(task);
    await close();
    await page.mouse.move(0, 0);
    await task.screenshot({ path: info.outputPath('task-after-pointer.png') });
    await expect(task).toHaveCSS('outline-style', 'none');
    // Real Tab navigation must still work, without decorative text or focus frames.
    for (let tab = 0; tab < 30 && !await task.evaluate(el => el === document.activeElement && el.matches(':focus-visible')); tab++) await page.keyboard.press('Tab');
    await expect(task).toBeFocused();
    await expect(task).toHaveCSS('outline-style', 'none');
    await expect(task).toHaveCSS('text-decoration-line', 'none');
    await page.keyboard.press('Enter');
    await close(true);
    await expect(task).toBeFocused();
    await expect(task).toHaveCSS('outline-style', 'none');
    await expect(task).toHaveCSS('text-decoration-line', 'none');
    await task.screenshot({ path: info.outputPath('task-keyboard-no-ring.png') });
    await pointer(task);
    await close();
    await expect(task).toHaveCSS('outline-style', 'none');
    await expect(task).toHaveCSS('text-decoration-line', 'none');
    if (!isMobile) {
      await task.hover();
      await expect(task).toHaveCSS('text-decoration-line', 'none');
    }
    if (scene === 'inventory') {
      const marker = page.locator('[data-hotspot="entrance"]');
      for (let tab = 0; tab < 30 && !await marker.evaluate(el => el === document.activeElement); tab++) await page.keyboard.press('Tab');
      await expect(marker).toBeFocused();
      await expect(marker).toHaveCSS('text-decoration-line', 'none');
      await marker.screenshot({ path: info.outputPath('inventory-marker-no-underline.png') });
    }
  });
}
