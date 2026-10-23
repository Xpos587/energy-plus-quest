import { act } from "react";
import { createRoot } from "react-dom/client";
import { expect, it, vi } from "vitest";
import { JourneyEnding } from "./JourneyEnding";

it.each(["alva", "khor", "arseniy"] as const)(
  "renders all three gift resolutions for %s",
  async (recipient) => {
    vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);
    const host = document.createElement("div");
    const root = createRoot(host);
    try {
      for (const parcel of ["socks", "boat", "camera"] as const) {
        await act(async () =>
          root.render(
            <JourneyEnding
              context={{ profile: "student", recipient, parcel }}
              scores={{ energy: 0, empathy: 0, efficiency: 0 }}
              onRestart={() => {}}
            />,
          ),
        );
        const art = host.querySelector<HTMLImageElement>(
          "[data-resolution-art]",
        );
        expect(art?.getAttribute("src")).toContain(`${recipient}-${parcel}`);
        expect(art?.alt).toBeTruthy();
        expect(host.textContent).toContain("Миссия выполнена");
        expect(host.textContent).not.toContain("(для");
      }
    } finally {
      await act(async () => root.unmount());
      vi.unstubAllGlobals();
    }
  },
);

it("continues the delivered gift to a certificate before restart or home", async () => {
  vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);
  const host = document.createElement("div");
  document.body.append(host);
  const root = createRoot(host);
  const restart = vi.fn();
  const home = vi.fn();
  try {
    await act(async () =>
      root.render(
        <JourneyEnding
          context={{ profile: "student", recipient: "alva", parcel: "boat" }}
          scores={{ energy: 1, empathy: 5, efficiency: 2 }}
          onRestart={restart}
          onHome={home}
        />,
      ),
    );
    expect(host.textContent).toContain(
      "Миссия выполнена: вы успешно доставили подарок! Сюрприз по-настоящему порадовал Майму.",
    );
    expect(host.textContent).toContain(
      "Она теперь сможет путешествовать по реке и рыбачить в удовольствие!",
    );
    expect(host.textContent).not.toContain("(для лодки)");
    expect(host.textContent).not.toContain("Пройти заново");
    await act(async () => host.querySelector("button")!.click());
    expect(restart).not.toHaveBeenCalled();
    expect(host.querySelector("[data-logist-certificate]")).not.toBeNull();
    expect(host.textContent).toContain("Вы — сердце логистики!");
    expect(host.textContent).toContain("Вы не только сделали сюрприз Майме.");
    expect(document.activeElement).toBe(host.querySelector("h1"));
    const restartButton = [...host.querySelectorAll("button")].find(
      (button) => button.getAttribute("aria-label") === "Пройти заново",
    )!;
    const homeButton = [...host.querySelectorAll("button")].find(
      (button) => button.getAttribute("aria-label") === "Вернуться на главную",
    )!;
    await act(async () => homeButton.click());
    expect(home).toHaveBeenCalledOnce();
    await act(async () => restartButton.click());
    expect(restart).toHaveBeenCalledOnce();
    expect(
      host.querySelectorAll('a[href^="https://max.ru/:share"]'),
    ).toHaveLength(1);
  } finally {
    await act(async () => root.unmount());
    host.remove();
    vi.unstubAllGlobals();
  }
});

it.each([
  [
    "student",
    { energy: -1, empathy: -2, efficiency: -3 },
    "Вы — логист будущего.",
  ],
  [
    "professional",
    { energy: -1, empathy: -2, efficiency: -3 },
    "Вы — настоящий мистер Энергия!",
  ],
  [
    "student",
    { energy: 1, empathy: 2, efficiency: 3 },
    "Вы — логистический гик!",
  ],
  [
    "professional",
    { energy: 3, empathy: 3, efficiency: 3 },
    "Вы — настоящий мистер Энергия!",
  ],
] as const)(
  "selects canonical profile for %s with %o",
  async (profile, scores, title) => {
    vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);
    const host = document.createElement("div");
    const root = createRoot(host);
    try {
      await act(async () =>
        root.render(
          <JourneyEnding
            context={{ profile, recipient: "arseniy", parcel: "camera" }}
            scores={scores}
            onRestart={() => {}}
          />,
        ),
      );
      await act(async () => host.querySelector("button")!.click());
      expect(host.querySelector("h1")?.textContent).toBe(title);
      expect(host.textContent).not.toContain("(ссылка сайт/страницу HH)");
    } finally {
      await act(async () => root.unmount());
      vi.unstubAllGlobals();
    }
  },
);
