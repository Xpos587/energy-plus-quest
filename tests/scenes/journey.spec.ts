import { expect, test } from "@playwright/test";
import manifest from "../../src/scenes/worldManifest.json" with {
  type: "json",
};

test("complete all remaining scenes without clipping copy or losing scores", async ({
  page,
}, testInfo) => {
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await page.goto("/scenes.html?parcel=boat&recipient=alva");
  await expect(
    page.getByRole("heading", { name: "Погрузка на фуру", exact: true }),
  ).toBeVisible();
  for (const [scene, choice, title] of [
    ["compact", "auto", "Погрузка на фуру"],
    ["inventory", "wms", "Хранение на складе"],
    ["crane", "remote", "Погрузка на баржу"],
    ["lastmile", "pipe-carrier", "Последние препятствия"],
  ]) {
    await expect(
      page.getByRole("heading", { name: title, exact: true }),
    ).toBeVisible();
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= window.innerWidth,
      ),
    ).toBe(true);
    await page.screenshot({
      path: testInfo.outputPath(`${scene}-choice.png`),
      fullPage: true,
    });
    await page.locator(`[data-choice-id="${choice}"]`).click();
    await expect(page.getByTestId("result-copy")).toBeVisible();
    await expect(page.getByTestId("result-copy")).not.toContainText(
      /\(подарок\)|\(персонаж\)|\(название|для подарка «лодка»/,
    );
    expect(
      await page
        .getByTestId("result-copy")
        .evaluate((node) => node.scrollHeight <= node.clientHeight + 1),
    ).toBe(true);
    await page.screenshot({
      path: testInfo.outputPath(`${scene}-result.png`),
      fullPage: true,
    });
    await page
      .getByRole("button", {
        name: scene === "lastmile" ? "Завершить" : "Продолжить",
        exact: true,
      })
      .click();
  }
  await expect(
    page.getByRole("button", { name: "Завершено", exact: true }),
  ).toBeDisabled();
  expect(errors).toEqual([]);
});

test("flat concept art stays static under reduced motion", async ({ page }) => {
  for (const scene of ["inventory", "crane", "lastmile"]) {
    await page.goto(`/scenes.html?scene=${scene}`);
    const illustration = page.locator("[data-concept-art] > svg");
    await expect(illustration).toBeVisible();
    await expect(page.locator("[data-world-plane] img")).toHaveCount(0);
    await page.emulateMedia({ reducedMotion: "reduce" });
    expect(
      await illustration.evaluate(
        (node) => getComputedStyle(node).animationName,
      ),
    ).toBe("none");
  }
});

test("manifest targets align, stay separated and resize with their illustration coordinate system", async ({
  page,
}, testInfo) => {
  for (const scene of ["compact", "inventory"] as const) {
    await page.goto(`/scenes.html?scene=${scene}`);
    const viewport = page.viewportSize()!;
    for (const size of [
      viewport,
      { width: viewport.height, height: viewport.width },
      viewport,
    ]) {
      await page.setViewportSize(size);
      const art = page.locator("[data-world-scene]");
      await expect
        .poll(async () => {
          const format = (await art.getAttribute("data-format")) as
            | "desktop"
            | "mobile";
          const view = manifest.scenes[scene][format];
          const plane = await page.locator("[data-world-plane]").boundingBox();
          const image = await page
            .locator(
              scene === "compact"
                ? "[data-world-plane] img"
                : "[data-concept-art] > svg",
            )
            .evaluate((node) => {
              if (node instanceof HTMLImageElement)
                return { width: node.naturalWidth, height: node.naturalHeight };
              const box = (node as SVGSVGElement).viewBox.baseVal;
              return { width: box.width, height: box.height };
            });
          return (
            !!plane &&
            image.width === view.width &&
            image.height === view.height &&
            Math.abs(plane.width / plane.height - view.width / view.height) <
              0.01
          );
        })
        .toBe(true);
      const format = (await art.getAttribute("data-format")) as
        | "desktop"
        | "mobile";
      const view = manifest.scenes[scene][format];
      const stage = (await art.boundingBox())!;
      const area = (candidate: typeof view) => {
        const scale = Math.min(
          stage.width / candidate.width,
          stage.height / candidate.height,
        );
        return candidate.width * candidate.height * scale * scale;
      };
      expect(format).toBe(
        area(manifest.scenes[scene].mobile) >
          area(manifest.scenes[scene].desktop)
          ? "mobile"
          : "desktop",
      );
      const plane = (await page.locator("[data-world-plane]").boundingBox())!;
      const centers: { x: number; y: number }[] = [];
      for (const point of view.hotspots) {
        const box = (await page
          .locator(`[data-hotspot="${point.id}"]`)
          .boundingBox())!;
        expect(box.width).toBeGreaterThanOrEqual(44);
        expect(box.height).toBeGreaterThanOrEqual(44);
        const center = { x: box.x + box.width / 2, y: box.y + box.height / 2 };
        expect(
          Math.abs(center.x - (plane.x + point.x * plane.width)),
        ).toBeLessThan(1);
        expect(
          Math.abs(center.y - (plane.y + point.y * plane.height)),
        ).toBeLessThan(1);
        for (const other of centers)
          expect(
            Math.hypot(center.x - other.x, center.y - other.y),
          ).toBeGreaterThanOrEqual(44);
        centers.push(center);
      }
      await page.screenshot({
        path: testInfo.outputPath(
          `${scene}-${size.width}x${size.height}-geometry.png`,
        ),
      });
    }
  }
});

test("description numbering is rendered only when the label needs it", async ({
  page,
}, testInfo) => {
  for (const scene of ["compact", "inventory", "crane", "lastmile"]) {
    await page.goto(`/scenes.html?scene=${scene}`);
    if (scene === "compact") {
      await expect(page.getByTestId("scene-intro")).toBeVisible();
      await expect(page.locator("[data-choice-description]")).toHaveCount(0);
      continue;
    }
    await page.locator("[aria-expanded]").click();
    for (const item of await page.locator("[data-choice-description]").all()) {
      const label = (await item.textContent())!.trim();
      const numbered =
        scene === "compact" ||
        /^(?:Место\s*\d|Вариант\s*\d|№\s*\d|\d+[.)])/.test(label);
      expect(
        await item.evaluate((node) => getComputedStyle(node).listStyleType),
      ).toBe(numbered ? "none" : "decimal");
    }
    await page.screenshot({
      path: testInfo.outputPath(`${scene}-descriptions.png`),
    });
    await page
      .locator("[data-choice-description]")
      .last()
      .scrollIntoViewIfNeeded();
    await page.screenshot({
      path: testInfo.outputPath(`${scene}-descriptions-end.png`),
    });
  }
});

test("selected landmarks and concise outcomes are visible above result panels", async ({
  page,
}, testInfo) => {
  for (const [scene, choice, parcel, expected] of [
    ["crane", "wait", "camera", "Подарок остался на причале"],
    ["crane", "remote", "camera", "Подарок на барже"],
    ["crane", "rush", "camera", "Подарок на барже"],
    ["crane", "petr", "camera", "Подарок на барже"],
    ["lastmile", "helicopter", "camera", "Быстро, но дорого"],
    ["lastmile", "robot", "camera", "Тележка завязла в грунте"],
    ["lastmile", "rover", "camera", "Снегоболотоход"],
    ["lastmile", "pipe-carrier", "boat", "Подарок доставил снегоболотоход"],
    ["lastmile", "pipe-carrier", "camera", "Подарок доставил беспилотник"],
    ["lastmile", "pipe-carrier", "socks", "Подарок доставил беспилотник"],
  ]) {
    await page.goto(`/scenes.html?scene=${scene}&parcel=${parcel}`);
    await page.locator(`[data-choice-id="${choice}"]`).click();
    await expect(page.locator("[data-selected-marker]")).toHaveCount(0);
    const illustration = page.locator("[data-concept-art]");
    await expect(illustration).toBeVisible();
    const plane = (await page.locator("[data-world-plane]").boundingBox())!;
    const label = page.locator("[data-world-annotation]");
    await expect(label).toContainText(expected);
    for (const element of [illustration, label]) {
      await expect(element).toBeVisible();
      const bounds = (await element.boundingBox())!;
      expect(bounds.x).toBeGreaterThanOrEqual(plane.x);
      expect(bounds.y).toBeGreaterThanOrEqual(plane.y);
      expect(bounds.x + bounds.width).toBeLessThanOrEqual(
        plane.x + plane.width + 1,
      );
      expect(bounds.y + bounds.height).toBeLessThanOrEqual(
        plane.y + plane.height + 1,
      );
      expect(
        await element.evaluate((node) => {
          const box = node.getBoundingClientRect();
          return [
            [box.left + 2, box.top + 2],
            [box.right - 2, box.bottom - 2],
          ].every(([x, y]) => {
            const panel = document
              .querySelector('[data-result="true"]')!
              .getBoundingClientRect();
            return (
              x >= 0 &&
              y >= 0 &&
              x < innerWidth &&
              y < innerHeight &&
              !(
                x >= panel.left &&
                x <= panel.right &&
                y >= panel.top &&
                y <= panel.bottom
              )
            );
          });
        }),
      ).toBe(true);
    }
    await page.screenshot({
      path: testInfo.outputPath(`${scene}-${choice}-${parcel}-annotation.png`),
    });
  }
});

test("all warehouse choices remain on screen without a hidden horizontal pan", async ({
  page,
}) => {
  await page.goto("/scenes.html?scene=inventory");
  const art = page.locator('section[aria-label^="Иллюстрация:"]');
  await expect(art.getByRole("button")).toHaveCount(4);
  const area = await art.boundingBox();
  if (!area) throw new Error("Missing warehouse bounds");
  for (const button of await art.getByRole("button").all()) {
    const box = await button.boundingBox();
    if (!box) throw new Error("Missing warehouse marker bounds");
    expect(box.x).toBeGreaterThanOrEqual(area.x);
    expect(box.x + box.width).toBeLessThanOrEqual(area.x + area.width);
  }
});

test("a compact map choice opens a manually collapsed panel and focuses its result heading", async ({
  page,
}) => {
  await page.goto("/scenes.html");
  await expect(page.getByTestId("scene-intro")).toBeVisible();
  await page.locator("[aria-expanded]").click();
  await expect(page.locator("[aria-expanded]")).toHaveAttribute(
    "aria-expanded",
    "false",
  );
  await page
    .locator('section[aria-label^="Иллюстрация:"]')
    .getByRole("button")
    .first()
    .press("Enter");
  await expect(page.getByTestId("result-copy")).toBeVisible();
  await expect(page.getByRole("heading", { level: 2 })).toBeFocused();
});

test("panel works from keyboard without changing the source text", async ({
  page,
}) => {
  await page.goto("/scenes.html?scene=crane&parcel=camera&recipient=arseniy");
  await page.locator("[aria-expanded]").click();
  const toggle = page.getByRole("button", {
    name: "Скрыть подробности",
    exact: true,
  });
  const original = await page.getByTestId("scene-intro").textContent();
  await toggle.focus();
  await page.keyboard.press("Enter");
  await expect(page.getByTestId("scene-intro")).toBeHidden();
  await page
    .getByRole("button", { name: "Подробнее о задании", exact: true })
    .press("Enter");
  await expect(page.getByTestId("scene-intro")).toHaveText(original ?? "");
  await page.locator('[data-choice-id="wait"]').focus();
  await page.keyboard.press("Enter");
  await expect(page.getByTestId("result-copy")).toContainText("целые сутки");
  await page
    .getByRole("button", { name: "Изменить выбор", exact: true })
    .click();
  await page.locator("[aria-expanded]").click();
});
