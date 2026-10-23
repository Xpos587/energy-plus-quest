import { expect, test } from "@playwright/test";

test("all certificate profiles fit and expose download and text channels", async ({
  page,
}) => {
  await page.goto("/");
  for (const viewport of [
    { width: 320, height: 568 },
    { width: 390, height: 844 },
    { width: 844, height: 390 },
    { width: 1440, height: 900 },
  ]) {
    await page.setViewportSize(viewport);
    for (const profile of ["student", "professional"])
      for (const type of ["future", "energy", "empathy", "efficiency"]) {
        if (profile === "professional" && type === "future") continue;
        await page.evaluate(
          async ({ profile, type }) => {
            // Load the actual Vite modules to cover every canonical result without changing game scores.
            const load = (url: string) => import(/* @vite-ignore */ url);
            const React = (await load("/node_modules/.vite/deps/react.js"))
              .default;
            const { createRoot } = (
              await load("/node_modules/.vite/deps/react-dom_client.js")
            ).default;
            const { JourneyEnding } = await load(
              "/src/scenes/JourneyEnding.tsx",
            );
            const review = window as unknown as {
              reviewRoot?: { unmount(): void; render(node: unknown): void };
            };
            review.reviewRoot?.unmount();
            const host = document.createElement("div");
            document.body.replaceChildren(host);
            Object.defineProperty(navigator, "canShare", {
              configurable: true,
              value: () => true,
            });
            Object.defineProperty(navigator, "share", {
              configurable: true,
              value: async () => {},
            });
            review.reviewRoot = createRoot(host);
            const scores = { energy: 0, empathy: 0, efficiency: 0 };
            if (type === "future")
              Object.assign(scores, {
                energy: -1,
                empathy: -1,
                efficiency: -1,
              });
            else scores[type as keyof typeof scores] = 5;
            review.reviewRoot!.render(
              React.createElement(JourneyEnding, {
                context: { profile, recipient: "arseniy", parcel: "boat" },
                scores,
                onRestart: () => {},
                onHome: () => {},
              }),
            );
          },
          { profile, type },
        );
        await page
          .getByRole("button", { name: "Узнать, какой вы логист" })
          .click();
        await page
          .getByRole("button", { name: "Поделиться", exact: true })
          .click();
        await expect(
          page.getByRole("button", { name: "Скачать сертификат", exact:true }),
        ).toBeVisible();
        await page
          .getByRole("button", { name: "Закрыть", exact: true })
          .click();
        for (const screen of ["result", "practice"]) {
          if (screen === "practice") {
            const turn = page.getByRole("button", {
              name: "Подробнее о практике",
            });
            if (!(await turn.isVisible())) break;
            await turn.click();
            await expect(page.locator("[data-practice-cta] h2")).toBeFocused();
          }
          const outside = await page.locator("button,a").evaluateAll(
            (els, viewport) =>
              els
                .filter((e) => e.getClientRects().length)
                .filter((e) => {
                  const r = e.getBoundingClientRect();
                  return (
                    r.bottom > viewport.height + 1 ||
                    r.right > viewport.width + 1 ||
                    r.x < 0 ||
                    r.y < 0
                  );
                })
                .map((e) => e.textContent),
            viewport,
          );
          expect(
            outside,
            `${profile}/${type}/${screen} ${viewport.width}`,
          ).toEqual([]);
        }
        await page
          .getByRole("button", { name: "Поделиться", exact: true })
          .click();
        await expect(
          page.getByRole("link", { name: "MAX", exact: true }),
        ).toBeVisible();
      }
  }
});
