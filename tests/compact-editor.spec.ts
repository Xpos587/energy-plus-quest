import { expect, test } from "@playwright/test";
import { readFile } from "node:fs/promises";
const saved = "compact-layout-v1",
  draft = "compact-layout-draft-v1";
test("edit numbers independently, drag, undo, save, reload and import coordinates", async ({
  page,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.goto("/compact-editor.html");
  const frame = page.frameLocator("iframe");
  await expect(frame.locator('[data-layout-badge="place-1"]')).toBeVisible();
  const zone = frame.locator('[data-loading-zone="place-1"]');
  const number = frame.locator('[data-layout-badge="place-1"]');
  const originalZone = await zone.getAttribute("x");
  const originalNumber = await number.boundingBox();
  const originalX = Number(
    await page.getByLabel("X", { exact: true }).inputValue(),
  );
  await page.getByLabel("X", { exact: true }).fill(String(originalX + 30));
  await expect
    .poll(
      async () =>
        ((await number.boundingBox())?.x ?? 0) - (originalNumber?.x ?? 0),
    )
    .toBeGreaterThan(5);
  expect(await zone.getAttribute("x")).toBe(originalZone);
  await page.getByRole("button", { name: "Отменить", exact: true }).click();
  await expect(page.getByLabel("X", { exact: true })).toHaveValue(
    String(originalX),
  );
  const handle = page.locator(
    '[data-editor-target="badge:place-1"] .editor-drag',
  );
  await expect
    .poll(async () =>
      Math.abs(
        ((
          await page
            .locator('[data-editor-target="badge:place-1"]')
            .boundingBox()
        )?.x ?? 0) - ((await number.boundingBox())?.x ?? 0),
      ),
    )
    .toBeLessThan(1);
  const box = (await handle.boundingBox())!;
  await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
  await page.mouse.down();
  await page.mouse.move(
    box.x + box.width / 2 + 35,
    box.y + box.height / 2 + 15,
    { steps: 8 },
  );
  await page.mouse.up();
  await expect
    .poll(async () =>
      Number(await page.getByLabel("X", { exact: true }).inputValue()),
    )
    .toBeGreaterThan(originalX + 20);
  const newX = await page.getByLabel("X", { exact: true }).inputValue();
  await page
    .getByRole("button", { name: "Сохранить для игры", exact: true })
    .click();
  await page.reload();
  await expect(frame.locator('[data-layout-badge="place-1"]')).toBeVisible();
  await expect(page.getByLabel("X", { exact: true })).toHaveValue(newX);
  await page.getByRole("button", { name: "Зоны", exact: true }).click();
  await page.getByLabel("Ширина", { exact: true }).fill("200");
  await expect(zone).toHaveAttribute("width", "200");
  await page.getByRole("button", { name: "Номера", exact: true }).click();
  await expect(page.getByLabel("X", { exact: true })).toHaveValue(newX);
  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: "Экспорт JSON", exact: true }).click();
  const download = await downloadPromise;
  expect(download.suggestedFilename()).toBe("compact-layout-v1.json");
  const exported = await readFile((await download.path())!, "utf8");
  await page.getByRole("button", { name: "Сбросить всё", exact: true }).click();
  await expect(page.getByLabel("X", { exact: true })).toHaveValue(
    String(originalX),
  );
  await page
    .getByRole("button", { name: "Импорт / JSON", exact: true })
    .click();
  await page.getByLabel("JSON координат").fill("{");
  await page
    .getByRole("button", { name: "Импортировать", exact: true })
    .click();
  await expect(page.locator("dialog [role=alert]")).toBeVisible();
  await page.getByLabel("Файл координат").setInputFiles({
    name: "compact-layout-v1.json",
    mimeType: "application/json",
    buffer: Buffer.from(exported),
  });
  await expect(page.getByLabel("X", { exact: true })).toHaveValue(newX);
  expect(
    await page.evaluate((key) => JSON.parse(localStorage.getItem(key)!), draft),
  ).toEqual(JSON.parse(exported));
  await page.getByRole("button", { name: "Логотипы", exact: true }).click();
  await page.getByLabel("Сдвиг Y").fill("6");
  await expect(frame.locator('img[alt="Энергия+"]:visible')).toHaveCSS(
    "translate",
    "0px 6px",
  );
  await page
    .getByRole("button", { name: "Сохранить для игры", exact: true })
    .click();
  await page.screenshot({
    path: "docs/reviews/compact-editor-2026-10-18/editor-mobile.png",
  });
  await page.getByLabel("Размер окна").selectOption("1440×900");
  await expect(frame.locator('[data-layout-profile="wide"]')).toBeVisible();
  await expect(page.getByLabel("Сдвиг Y")).toHaveValue("0");
  await page.getByLabel("Сдвиг Y").fill("4");
  await page.getByRole("button", { name: "Номера", exact: true }).click();
  await page.getByLabel("X", { exact: true }).fill("100");
  await page
    .getByRole("button", { name: "Сохранить для игры", exact: true })
    .click();
  await page.screenshot({
    path: "docs/reviews/compact-editor-2026-10-18/editor-desktop.png",
  });
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto(
    "/scenes.html?scene=compact&parcel=boat&recipient=alva&carrier=near",
  );
  const next = page.getByRole("button", { name: /^(К выбору|Далее)$/ });
  for (let n = 0; n < 10 && (await next.isVisible()); n++) await next.click();
  await expect(page.locator('[data-layout-badge="place-1"]')).toBeVisible();
  await expect(page.locator('img[alt="Энергия+"]:visible')).toHaveCSS(
    "translate",
    "0px 4px",
  );
  await expect
    .poll(async () => {
      const plane = (await page.locator("[data-world-plane]").boundingBox())!;
      const badge = (await page
        .locator('[data-layout-badge="place-1"]')
        .boundingBox())!;
      return Math.abs(badge.x - (plane.x + (100 / 1040) * plane.width));
    })
    .toBeLessThan(1);
  expect(
    await page.evaluate(
      ([key]) =>
        JSON.parse(localStorage.getItem(key)!).profiles.portrait[0].badge.x,
      [saved, draft],
    ),
  ).toBe(Number(newX));
  expect(errors).toEqual([]);
});

test("drag zones, resize and move the visible logos; saved normal game uses exactly that geometry", async ({
  page,
}) => {
  await page.goto("/compact-editor.html");
  const frame = page.frameLocator("iframe");
  const badge = frame.locator('[data-layout-badge="place-1"]');
  await expect(badge).toBeVisible();
  const originalBadge = (await badge.boundingBox())!;
  const drag = async (selector: string, dx: number, dy: number) => {
    const handle = page.locator(selector);
    await expect(handle).toBeVisible();
    await handle.hover();
    const rect = (await handle.boundingBox())!;
    await page.mouse.move(rect.x + rect.width / 2, rect.y + rect.height / 2);
    await page.mouse.down();
    await page.mouse.move(
      rect.x + rect.width / 2 + dx,
      rect.y + rect.height / 2 + dy,
      { steps: 10 },
    );
    await page.mouse.up();
  };
  await page.getByRole("button", { name: "Зоны", exact: true }).click();
  await drag('[data-editor-target="zone:place-1"] .editor-drag', 20, 10);
  await expect
    .poll(async () =>
      Number(await page.getByLabel("X", { exact: true }).inputValue()),
    )
    .toBeGreaterThan(100);
  expect(
    Math.abs((await badge.boundingBox())!.x - originalBadge.x),
  ).toBeLessThan(1);
  const zoneX = await page.getByLabel("X", { exact: true }).inputValue();
  await drag('[data-editor-target="zone:place-1"] .editor-resize', 12, 8);
  await expect
    .poll(async () =>
      Number(await page.getByLabel("Ширина", { exact: true }).inputValue()),
    )
    .toBeGreaterThan(170);
  await page.getByRole("button", { name: "Номера", exact: true }).click();
  await drag('[data-editor-target="badge:place-1"] .editor-resize', 14, 0);
  await expect
    .poll(async () =>
      Number(await page.getByLabel("Размер номера").inputValue()),
    )
    .toBeGreaterThan(30);
  const size = await page.getByLabel("Размер номера").inputValue();
  await page.getByRole("button", { name: "Логотипы", exact: true }).click();
  const logo = frame.locator('img[alt="Энергия+"]:visible');
  const initialLogo = (await logo.boundingBox())!;
  await drag('[data-editor-target="logo:energy"] .editor-drag', 12, 7);
  await expect
    .poll(async () => Number(await page.getByLabel("Сдвиг X").inputValue()))
    .toBeGreaterThan(10);
  expect((await logo.boundingBox())!.y).toBeGreaterThan(initialLogo.y + 4);
  await drag('[data-editor-target="logo:energy"] .editor-resize', 12, 0);
  await expect
    .poll(async () => Number(await page.getByLabel("Масштаб").inputValue()))
    .toBeGreaterThan(1);
  await page
    .getByRole("button", { name: "Сохранить для игры", exact: true })
    .click();
  const savedDoc = await page.evaluate(
    (key) => JSON.parse(localStorage.getItem(key)!),
    saved,
  );
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(
    "/scenes.html?scene=compact&parcel=boat&recipient=alva&carrier=near",
  );
  const next = page.getByRole("button", { name: /^(К выбору|Далее)$/ });
  for (let n = 0; n < 10 && (await next.isVisible()); n++) await next.click();
  await expect(page.locator('[data-loading-zone="place-1"]')).toHaveAttribute(
    "x",
    zoneX,
  );
  expect(
    Math.abs(
      (await page
        .locator('[data-layout-badge="place-1"]')
        .evaluate((e) => parseFloat(getComputedStyle(e).width))) - Number(size),
    ),
  ).toBeLessThan(0.02);
  const adjustment = savedDoc.logos.mobile.energy;
  await expect(page.locator('img[alt="Энергия+"]:visible')).toHaveCSS(
    "translate",
    `${adjustment.dx}px ${adjustment.dy}px`,
  );
  await expect(page.locator('img[alt="Энергия+"]:visible')).toHaveCSS(
    "scale",
    String(adjustment.scale),
  );
  await page.reload();
  for (let n = 0; n < 10 && (await next.isVisible()); n++) await next.click();
  await expect(page.locator('[data-loading-zone="place-1"]')).toHaveAttribute(
    "x",
    zoneX,
  );
  await page.screenshot({
    path: "docs/reviews/compact-editor-2026-10-18/saved-normal-mobile.png",
  });
  await page.goto("/scenes.html?scene=inventory&parcel=boat&recipient=alva");
  for (const logo of await page.locator('img[alt="Энергия+"]').all())
    expect(await logo.evaluate((e) => (e as HTMLElement).style.translate)).toBe(
      "",
    );
});
