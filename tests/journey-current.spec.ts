import { expect, type Page, test } from "@playwright/test";

type Journey = {
  name: string;
  profile: "student" | "professional";
  recipient: "alva" | "khor" | "arseniy";
  parcel: "camera" | "socks" | "boat";
  carrier: "near" | "crew" | "express";
  compact: [string, string];
  inventory: string;
  crane: string;
  lastmile: string;
};

const journeys: Journey[] = [
  {
    name: "boat to Alva",
    profile: "professional",
    recipient: "alva",
    parcel: "boat",
    carrier: "crew",
    compact: ["place-1", "place-4"],
    inventory: "alphabet",
    crane: "wait",
    lastmile: "helicopter",
  },
  {
    name: "camera to Khor",
    profile: "student",
    recipient: "khor",
    parcel: "camera",
    carrier: "near",
    compact: ["place-2", "auto"],
    inventory: "wms",
    crane: "remote",
    lastmile: "pipe-carrier",
  },
  {
    name: "socks to Arseniy",
    profile: "professional",
    recipient: "arseniy",
    parcel: "socks",
    carrier: "express",
    compact: ["place-3", "place-1"],
    inventory: "keeper",
    crane: "petr",
    lastmile: "rover",
  },
];

async function expectCurrentViewFits(page: Page) {
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth + 1,
    ),
  ).toBe(true);
  for (const control of await page
    .locator(
      '[data-choice-confirm]:visible, [data-choice-cancel]:visible, [data-result-reader] footer button:visible',
    )
    .all()) {
    await expect(control).toBeInViewport({ ratio: 0.98 });
  }
}

async function readBriefing(page: Page) {
  const forward = page.getByRole("button", {
    name: /^(Далее|К выбору)$/,
  });
  for (let step = 0; step < 20 && (await forward.isVisible()); step += 1) {
    await expectCurrentViewFits(page);
    await forward.click();
  }
  await expect(page.locator('[data-scene-briefing][data-reading="false"]')).toBeVisible();
  await expectCurrentViewFits(page);
}

async function readResult(page: Page) {
  const reader = page.locator("[data-result-reader]");
  await expect(reader).toBeVisible();
  for (const image of await page.locator('[data-outcome-scene] img:visible').all()) {
    await expect(image).toHaveCSS('object-fit', 'cover');
  }
  await expect(reader).not.toContainText(/(?:Страница|Результат)\s*\d+\s*из\s*\d+/i);
  await expect(reader).not.toContainText("Последствия выбора");
  const readFurther = page.getByRole("button", {
    name: "Читать дальше",
    exact: true,
  });
  for (let pageIndex = 0; pageIndex < 40 && (await readFurther.isVisible()); pageIndex += 1) {
    await expect(page.getByTestId("result-copy")).not.toBeEmpty();
    await expectCurrentViewFits(page);
    await readFurther.click();
  }
  await expect(readFurther).toHaveCount(0);
  await expectCurrentViewFits(page);
}

async function chooseSetup(page: Page, journey: Journey) {
  for (const id of [journey.profile, journey.recipient, journey.parcel]) {
    const choice = page.locator(`[data-choice="${id}"]`);
    await expect(choice).toBeVisible();
    await choice.click();
  }
}

async function inspectCarrier(page: Page, id: Journey["carrier"], cancel = false) {
  await page
    .locator(`[data-carrier-choice="${id}"], [data-scene-choice="${id}"]`)
    .first()
    .click();
  await expect(page.locator("[data-choice-inspection]")).toBeVisible();
  await expectCurrentViewFits(page);
  await page.locator(cancel ? "[data-choice-cancel]" : "[data-choice-confirm]").click();
}

async function inspectSceneChoice(page: Page, id: string, viaArtwork = false) {
  const choice = page.locator(`[data-scene-choice="${id}"]`);
  const expectedTitle = (await choice.innerText()).replace(/^\s*\d+\s*/, "").trim();
  if (viaArtwork) {
    const marker = page.locator(`[data-hotspot="${id}"][data-choice-id="${id}"]`);
    await expect(marker).toBeVisible();
    await marker.click();
  } else {
    await choice.click();
  }
  await expect(page.locator("[data-choice-inspection]")).toBeVisible();
  await expect(page.locator("[data-choice-inspection] h3")).toHaveText(expectedTitle);
  await expectCurrentViewFits(page);
  await page.locator("[data-choice-confirm]").click();
  await expect(page.locator("[data-result]")).toBeVisible();
}

async function continueResult(page: Page, label: string) {
  await readResult(page);
  const next = page.getByRole("button", { name: label, exact: true });
  await expect(next).toBeInViewport({ ratio: 0.98 });
  await next.click();
}

for (const journey of journeys) {
  test(`${journey.name}: current full journey survives revision, reload and restart`, async ({
    page,
  }) => {
    const pageErrors: string[] = [];
    page.on("pageerror", (error) => pageErrors.push(error.message));
    await page.goto("/");

    await chooseSetup(page, journey);
    await readBriefing(page);
    await inspectCarrier(page, journey.carrier, true);
    await expect(page.locator("[data-choice-inspection], [data-result-reader]")).toHaveCount(0);
    await inspectCarrier(page, journey.carrier);
    await continueResult(page, "К следующей сцене");

    await expect(page.locator('[data-scene="compact"]')).toBeVisible();
    await readBriefing(page);
    await inspectSceneChoice(page, journey.compact[0]);
    await expect(page.locator('[data-world-scene="compact"]')).toHaveAttribute(
      "data-selected",
      journey.compact[0],
    );
    await page.getByRole("button", { name: "Изменить выбор", exact: true }).click();
    await expect(page.locator(`[data-scene-choice="${journey.compact[0]}"]`)).toBeVisible();
    await inspectSceneChoice(page, journey.compact[1]);
    await expect(page.locator('[data-world-scene="compact"]')).toHaveAttribute(
      "data-selected",
      journey.compact[1],
    );
    await continueResult(page, "Продолжить");

    await expect(page.locator('[data-scene="inventory"]')).toBeVisible();
    await readBriefing(page);
    await inspectSceneChoice(page, journey.inventory, true);
    const inventoryResult = `inventory-${journey.inventory}${
      journey.inventory === "alphabet" ? `-${journey.parcel}` : ""
    }`;
    await expect(page.locator(`[data-scene-consequence="${inventoryResult}"]`)).toBeVisible();
    await page.reload();
    await expect(page.locator('[data-scene="inventory"] [data-result]')).toBeVisible();
    await expect(page.locator(`[data-scene-consequence="${inventoryResult}"]`)).toBeVisible();
    await continueResult(page, "Продолжить");

    await expect(page.locator('[data-scene="crane"]')).toBeVisible();
    await readBriefing(page);
    await inspectSceneChoice(page, journey.crane);
    await continueResult(page, "Продолжить");

    await expect(page.locator('[data-scene="lastmile"]')).toBeVisible();
    await readBriefing(page);
    await inspectSceneChoice(page, journey.lastmile);
    await continueResult(page, "Завершить");
    await expect(page.getByText("Завершено", { exact: true })).toBeVisible();

    const restart = page.getByRole("button", {
      name: "Пройти сцены заново",
      exact: true,
    });
    await expect(restart).toBeInViewport({ ratio: 0.98 });
    await restart.click();
    await expect(
      page.getByRole("heading", { name: "Кто отправится в путь?", exact: true }),
    ).toBeVisible();

    await chooseSetup(page, journey);
    await readBriefing(page);
    await inspectCarrier(page, journey.carrier);
    await continueResult(page, "К следующей сцене");
    await expect(page.locator('[data-scene="compact"] [data-result]')).toHaveCount(0);
    await expect(page.locator('[data-scene="compact"] [data-scene-briefing]')).toBeVisible();
    expect(pageErrors).toEqual([]);
  });
}
