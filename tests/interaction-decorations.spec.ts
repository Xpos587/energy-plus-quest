import { expect, test } from '@playwright/test';
import { shareCards, sharePage } from '../scripts/share-pages';
import { expectNoInteractionDecorations } from './helpers/interaction-decorations';

test('all seven standalone share pages keep links free of decorations', async ({ page, isMobile }) => {
  for (const card of shareCards) {
    await page.setContent(sharePage(card.id, `https://example.test/r/${card.id}/`).replace('src="card.jpg"', 'src="data:,"'));
    const link = page.getByRole('link', { name: 'Пройти игру' });
    await expectNoInteractionDecorations(page);
    await page.keyboard.press('Tab');
    await expect(link).toBeFocused();
    await expectNoInteractionDecorations(page);
    if (!isMobile) { await link.hover(); await expectNoInteractionDecorations(page); }
  }
});

test('global policy also covers decorated descendants and pseudo-elements', async ({ page }) => {
  await page.goto('/');
  // Deliberately hostile local styles prove the shared policy is not button-only.
  await page.evaluate(() => {
    const probe = document.createElement('div');
    probe.innerHTML = `<style>
      #decoration-probe span { outline: 3px solid blue; text-decoration: underline; }
      #decoration-probe span::after { content: 'label'; outline: 2px solid red; text-decoration: underline; }
    </style><button id="decoration-probe"><span>1</span></button>`;
    document.body.append(probe);
  });
  const probe = page.locator('#decoration-probe');
  await probe.focus();
  await expectNoInteractionDecorations(page);
  await probe.hover();
  await expectNoInteractionDecorations(page);
  await probe.click();
  await expectNoInteractionDecorations(page);
});
