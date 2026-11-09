import { expect, type Page, test } from "@playwright/test";
import { openInventory } from "./inventory-fixture";

async function readResult(page: Page) {
  const copy = page.getByTestId("result-copy");
  let text = await copy.innerText();
  const next = page.getByRole("button", { name: "Читать дальше", exact: true });
  while (await next.isVisible()) {
    await next.click();
    text += ` ${await copy.innerText()}`;
  }
  return text;
}

// Branch IDs and deltas from sourceCopy p355–381, not from implementation data.
const branches = [
  {
    id: "entrance",
    score: [-2, -1, 0],
    copy: "Сотрудникам придется делать лишний крюк",
  },
  {
    id: "alphabet",
    score: [-3, 0, -1],
    copy: "зона отгрузки находится рядом с началом алфавита",
  },
  { id: "keeper", score: [1, 4, -3], copy: "не рассказал" },
  { id: "wms", score: [4, 4, 5], copy: "Система выбрала для подарка место ближе к зоне отгрузки" },
];

for (const width of [320, 390]) {
  for (const [parcel, letter, range] of [
    ["camera", "Ф", "Ф–Э"],
    ["socks", "Н", "Н–У"],
    ["boat", "Л", "Л–М"],
  ]) {
    test(`${width}px ${parcel}: all warehouse results keep scenario copy, image and score on mobile`, async ({
      page,
      isMobile,
    }) => {
      await page.setViewportSize({ width, height: 844 });
      await page.emulateMedia({ reducedMotion: "reduce" });
      const errors: string[] = [];
      page.on("pageerror", (error) => errors.push(error.message));
      for (const branch of branches) {
        await openInventory(page, parcel);
        const main = page.locator("[data-world-plane] > picture img");
        await main.evaluate((img: HTMLImageElement) => img.decode());
        await expect(page.locator("[data-hotspot]")).toHaveCount(4);
        await expect(
          page.getByRole("button", { name: "Рассмотреть склад" }),
        ).toHaveCount(0);
        const marker = page.locator(`[data-hotspot="${branch.id}"]`);
        await expect(marker.locator("span")).toBeVisible(); // scene-1 style numbered pins
        if (isMobile) await marker.tap();
        else await marker.click();
        const preview = page.locator("[data-world-plane]");
        await expect(
          preview.locator(`[data-hotspot="${branch.id}"]`),
        ).toHaveAttribute("aria-pressed", "true");
        await expect(preview.locator('[data-warehouse-zone][data-interactive="true"]')).toHaveCount(1);
        if (branch.id === "alphabet") {
          await expect(marker).toHaveAttribute(
            "aria-label",
            new RegExp(`Стеллаж ${range}, буква ${letter}`),
          );
        }
        if (parcel === "socks")
          await page.screenshot({
            path: `.tmp-work/warehouse-audit-preview-${branch.id}-${width}.png`,
          });
        await page.locator("[data-choice-confirm]").click();
        const key = `inventory-${branch.id}${branch.id === "alphabet" ? `-${parcel}` : ""}`;
        const result = page.locator("[data-scene-consequence]");
        await expect(result).toHaveAttribute("data-scene-consequence", key);
        const image = result.locator("picture > img");
        await image.evaluate((img: HTMLImageElement) => img.decode());
        await expect(image).toHaveAttribute(
          "src",
          new RegExp(`/${key.replace("inventory-", "outcome-")}\\.webp$`),
        );
        const resultText = await readResult(page);
        expect(resultText).toContain(branch.copy);
        if (branch.id === "keeper") {
          expect(resultText).toContain("не рассказал");
          expect(resultText).toContain("задержалась");
        }
        for (const [i, score] of branch.score.entries()) {
          await expect(
            page.locator(
              `[data-score-key="${["energy", "empathy", "efficiency"][i]}"] strong`,
            ),
          ).toHaveText(score > 0 ? `+${score}` : String(score));
        }
        await expect(
          page.getByRole("button", { name: "Продолжить", exact: true }),
        ).toBeInViewport({ ratio: 1 });
        expect(
          await page.evaluate(
            () => document.documentElement.scrollWidth <= innerWidth,
          ),
        ).toBe(true);
        await page.screenshot({
          path: `.tmp-work/warehouse-audit-result-${parcel}-${branch.id}-${width}.png`,
        });
      }
      expect(errors).toEqual([]);
    });
  }
}
