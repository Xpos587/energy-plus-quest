import { expect, test } from "@playwright/test";

test("helicopter rotors move only while selected and respect reduced motion", async ({
  page,
}) => {
  await page.goto("/scenes.html?scene=lastmile&parcel=boat&recipient=alva");
  const reading = page.getByRole("button", { name: /^(Далее|К выбору)$/ });
  for (let step = 0; step < 8 && (await reading.isVisible()); step++)
    await reading.click();
  const rotors = page.locator("[data-helicopter-main-rotor]");
  await expect(rotors).toHaveCount(1);
  const pose = () =>
    rotors.evaluate((element) => getComputedStyle(element).transform);
  const parked = await pose();
  await page.waitForTimeout(180);
  expect(await pose()).toBe(parked);
  await page.locator('[data-choice-id="helicopter"]').click();
  await expect.poll(async () => await pose()).not.toBe(parked);
  const running = await pose();
  await page.waitForTimeout(180);
  expect(await pose()).not.toBe(running);
  await page
    .getByRole("button", { name: "К вариантам", exact: true })
    .click();
  await page.locator('[data-choice-id="rover"]').click();
  const stopped = await pose();
  await page.waitForTimeout(180);
  expect(await pose()).toBe(stopped);
  await page
    .getByRole("button", { name: "К вариантам", exact: true })
    .click();
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.locator('[data-choice-id="helicopter"]').click();
  const reduced = await pose();
  await page.waitForTimeout(180);
  expect(await pose()).toBe(reduced);
});
