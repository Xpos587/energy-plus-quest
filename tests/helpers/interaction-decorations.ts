import { expect, type Page } from '@playwright/test';

/** Inspect descendants and pseudo-elements too: a focused pin can frame its label. */
export async function expectNoInteractionDecorations(page: Page) {
  const violations = await page.evaluate(() => {
    const found: string[] = [];
    for (const element of document.body.querySelectorAll('*')) {
      if (!(element instanceof HTMLElement || element instanceof SVGElement) || !element.getClientRects().length) continue;
      for (const pseudo of [null, '::before', '::after']) {
        const style = getComputedStyle(element, pseudo);
        if (style.display === 'none' || style.visibility === 'hidden' || (pseudo && ['none', 'normal'].includes(style.content))) continue;
        if (style.textDecorationLine.includes('underline') ||
            (style.outlineStyle !== 'none' && style.outlineStyle !== 'hidden' && parseFloat(style.outlineWidth) > 0)) {
          found.push(`${element.tagName}.${element.getAttribute('class') ?? ''}${pseudo ?? ''}: ${style.textDecorationLine}, outline ${style.outline}`);
        }
      }
    }
    return found;
  });
  expect(violations, 'No underlines or extra outline frames anywhere on the rendered screen').toEqual([]);
}
