import { act } from "react";
import { createRoot } from "react-dom/client";
import { afterEach, expect, it, vi } from "vitest";
import { GameIntro } from "./GameIntro";

vi.mock("../scenes/artwork", () => ({
  sceneChoiceImage: () => "assets/intro-relative.webp",
}));
let dispose: (() => void) | undefined;
afterEach(async () => {
  if (dispose) await act(dispose);
  vi.unstubAllGlobals();
});
async function mount() {
  vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);
  window.scrollTo = vi.fn();
  const host = document.createElement("div");
  document.body.append(host);
  const root = createRoot(host);
  dispose = () => {
    root.unmount();
    host.remove();
  };
  await act(async () => root.render(<GameIntro onStart={() => {}} />));
  return host;
}
it("names each metric, then its scenario action and a plain gloss", async () => {
  const host = await mount();
  for (const selector of ["[data-intro-enter]", "[data-intro-next]"])
    await act(async () =>
      host.querySelector<HTMLButtonElement>(selector)?.click(),
    );
  expect(
    [...host.querySelectorAll("li")].map((e) =>
      e.textContent?.replace(/\s+/g, " ").trim(),
    ),
  ).toEqual([
    "Энергия За то, что экономите ресурсы. Время, силы, топливо и деньги.",
    "Эмпатия За то, что проявляете заботу. О подарке, получателе и людях рядом.",
    "Эффективность За то, что принимаете наиболее эффективные решения. Вовремя и самым подходящим способом.",
  ]);
});
it("makes the CSS background URL independent of the production stylesheet directory", async () => {
  const host = await mount();
  const css = host
    .querySelector<HTMLElement>("[data-intro-page]")
    ?.style.getPropertyValue("--intro-world");
  expect(css).toBe(
    `url("${new URL("assets/intro-relative.webp", document.baseURI).href}")`,
  );
});
