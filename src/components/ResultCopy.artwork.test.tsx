import { act } from "react";
import { createRoot } from "react-dom/client";
import { expect, it, vi } from "vitest";
import { ResultCopy } from "./ResultCopy";

it("keeps the consequence illustration beside the full narrative", async () => {
  vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);
  const host = document.createElement("div");
  const root = createRoot(host);
  try {
    await act(async () =>
      root.render(
        <ResultCopy paragraphs={["Груз прибыл целым."]}>
          <figure>
            <img src="/result.webp" alt="Закреплённый груз" />
            <figcaption>Ремень удержал коробку.</figcaption>
          </figure>
        </ResultCopy>,
      ),
    );
    expect(host.querySelector("figure")?.textContent).toBe(
      "Ремень удержал коробку.",
    );
    expect(host.querySelector('[data-testid="result-copy"]')?.textContent).toBe(
      "Груз прибыл целым.",
    );
    expect(host.querySelector("button, nav")).toBeNull();
  } finally {
    await act(async () => root.unmount());
    vi.unstubAllGlobals();
  }
});

it("does not advance the displayed beat while a long authored paragraph still has pages", async () => {
  vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);
  const width = vi
    .spyOn(HTMLElement.prototype, "clientWidth", "get")
    .mockReturnValue(320);
  const height = vi
    .spyOn(HTMLElement.prototype, "clientHeight", "get")
    .mockReturnValue(120);
  const bounds = vi
    .spyOn(HTMLElement.prototype, "getBoundingClientRect")
    .mockImplementation(function (this: HTMLElement) {
      const measuredHeight =
        this instanceof HTMLParagraphElement &&
        this.style.visibility === "hidden"
          ? Math.ceil((this.textContent?.length ?? 0) / 40) * 20
          : 120;
      return {
        x: 0,
        y: 0,
        width: 320,
        height: measuredHeight,
        top: 0,
        right: 320,
        bottom: measuredHeight,
        left: 0,
        toJSON: () => ({}),
      };
    });
  const host = document.createElement("div");
  const root = createRoot(host);
  const displayedBeats: number[] = [];
  const paragraphs = [
    "Первый эпизод продолжается. ".repeat(20),
    "Второй эпизод начинается здесь.",
  ];
  try {
    await act(async () =>
      root.render(
        <ResultCopy
          paragraphs={paragraphs}
          navigation={{
            scores: { energy: 0, empathy: 0, efficiency: 0 },
            onBack: () => {},
            onNext: () => {},
            backLabel: "Изменить выбор",
            nextLabel: "Завершить",
          }}
          onDisplayedBeatChange={(beat: number) => displayedBeats.push(beat)}
        />,
      ),
    );
    expect(displayedBeats.at(-1)).toBe(0);

    let pagesInFirstBeat = 0;
    while (
      !host.querySelector('[data-testid="result-copy"]')?.textContent?.includes(
        paragraphs[1],
      )
    ) {
      expect(displayedBeats.at(-1)).toBe(0);
      const next = host.querySelector<HTMLButtonElement>(
        '[aria-label="Читать дальше"]',
      );
      expect(next).not.toBeNull();
      await act(async () => next?.click());
      pagesInFirstBeat += 1;
      if (pagesInFirstBeat > 20) throw new Error("Second beat was not reached");
    }

    expect(pagesInFirstBeat).toBeGreaterThan(1);
    expect(displayedBeats.at(-1)).toBe(1);
  } finally {
    await act(async () => root.unmount());
    bounds.mockRestore();
    height.mockRestore();
    width.mockRestore();
    vi.unstubAllGlobals();
  }
});
