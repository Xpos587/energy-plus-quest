import { expect, test } from "@playwright/test";

const scores: Record<string, number[]> = {
  rush: [-4, -3, 3],
  wait: [0, 3, -4],
  petr: [-2, 4, -3],
  remote: [4, 4, 5],
  rover: [4, 3, 5],
  robot: [-4, 3, -5],
  "pipe-carrier": [-5, 0, -3],
};
for (const scene of ["crane", "lastmile"])
  for (const parcel of ["camera", "socks", "boat"])
    for (const recipient of ["alva", "khor", "arseniy"])
      test(`${scene} ${parcel} ${recipient}: all four confirmed outcomes`, async ({
        page,
      }, info) => {
        const errors: string[] = [];
        page.on("pageerror", (error) => errors.push(error.message));
        await page.goto(
          `/scenes.html?scene=${scene}&parcel=${parcel}&recipient=${recipient}`,
        );
        const choices =
          scene === "crane"
            ? ["rush", "wait", "petr", "remote"]
            : ["helicopter", "rover", "robot", "pipe-carrier"];
        for (const choice of choices) {
          await page
            .getByRole("button", { name: "Закрыть условие", exact: true })
            .click();
          await page.locator(`[data-choice-id="${choice}"]`).click();
          await expect(page.locator("[data-score-key]")).toHaveCount(0);
          await expect(page.locator("[data-choice-confirm]")).toBeInViewport({
            ratio: 1,
          });
          await page.locator("[data-choice-confirm]").click();
          let key = `${scene}-${choice}`;
          if (choice === "helicopter" && recipient !== "arseniy")
            key += "-remote";
          if (choice === "pipe-carrier" && parcel === "boat") key += "-boat";
          const art = page.locator(`[data-scene-consequence="${key}"] > img`);
          await expect
            .poll(() =>
              art.evaluate(
                (image: HTMLImageElement) =>
                  image.complete && image.naturalWidth > 0,
              ),
            )
            .toBe(true);
          expect(
            await art.evaluate((image) => getComputedStyle(image).objectFit),
          ).toBe("contain");
          const text = page.getByTestId("result-copy");
          await expect(text).not.toContainText(
            /\(подарок\)|\(персонаж\)|Ваш вязаные|Теперь он придет.*лод/,
          );
          const expected =
            choice === "helicopter"
              ? [-4, recipient === "arseniy" ? 0 : -2, 4]
              : scores[choice];
          expect(
            await page.locator("[data-score-key] strong").allTextContents(),
          ).toEqual(
            expected.map((value) => (value > 0 ? `+${value}` : `${value}`)),
          );
          const box = await art.boundingBox();
          const card = await page
            .getByRole("region", { name: "Результат выбора" })
            .boundingBox();
          expect(box && card && box.y + box.height <= card.y + 1).toBe(true);
          if (
            recipient === "alva" &&
            (parcel === "boat" || parcel === "camera")
          )
            await page.screenshot({
              path: info.outputPath(`${key}-${parcel}.png`),
            });
          await page
            .getByRole("button", { name: "Изменить выбор", exact: true })
            .click();
          await expect(page.locator("[data-scene-consequence]")).toHaveCount(0);
        }
        expect(errors).toEqual([]);
      });
