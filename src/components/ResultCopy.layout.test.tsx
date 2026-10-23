import { act } from "react";
import { createRoot } from "react-dom/client";
import { expect, it, vi } from "vitest";
import { ResultCopy } from "./ResultCopy";

const navigation = {
  scores: { energy: 0, empathy: 0, efficiency: 0 },
  onBack: () => {},
  onNext: () => {},
  backLabel: "Изменить выбор",
  nextLabel: "Продолжить",
};

it("keeps the result title outside measured prose and preserves navigation callbacks", async () => {
  vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);
  const host = document.createElement("div");
  const root = createRoot(host);
  const onBack = vi.fn();
  const onNext = vi.fn();
  try {
    await act(async () => root.render(
      <ResultCopy
        title={<><span>Груз</span> прибыл</>}
        titleTabIndex={-1}
        paragraphs={["Подарок прибыл вовремя."]}
        navigation={{ ...navigation, onBack, onNext }}
      />,
    ));
    const title = host.querySelector("[data-result-narrative] > h2");
    const reading = host.querySelector("[data-result-reading]");
    expect(title?.textContent).toBe("Груз прибыл");
    expect(title?.getAttribute("tabindex")).toBe("-1");
    expect(title?.nextElementSibling).toBe(reading);
    expect(reading?.querySelector("h2")).toBeNull();
    expect(reading?.textContent).toBe("Подарок прибыл вовремя.");
    await act(async () => host.querySelector<HTMLButtonElement>('button[aria-label="Изменить выбор"]')?.click());
    await act(async () => host.querySelector<HTMLButtonElement>('button[aria-label="Продолжить"]')?.click());
    expect(onBack).toHaveBeenCalledOnce();
    expect(onNext).toHaveBeenCalledOnce();
  } finally {
    await act(async () => root.unmount());
    vi.unstubAllGlobals();
  }
});

it("marks a one-page result as compact", async () => {
  vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);
  const host = document.createElement("div");
  const root = createRoot(host);
  try {
    await act(async () =>
      root.render(
        <ResultCopy
          paragraphs={["Подарок прибыл вовремя."]}
          navigation={navigation}
        />,
      ),
    );
    expect(
      host.querySelector("[data-result-reader]")?.getAttribute(
        "data-result-density",
      ),
    ).toBe("compact");
  } finally {
    await act(async () => root.unmount());
    vi.unstubAllGlobals();
  }
});

it("keeps a multi-page result paged with its reading action", async () => {
  vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);
  const host = document.createElement("div");
  const root = createRoot(host);
  try {
    await act(async () =>
      root.render(
        <ResultCopy
          paragraphs={["Длинное последствие выбора. ".repeat(30)]}
          navigation={navigation}
        />,
      ),
    );
    expect(
      host.querySelector("[data-result-reader]")?.getAttribute(
        "data-result-density",
      ),
    ).toBe("paged");
    expect(
      host.querySelector('button[aria-label="Читать дальше"]'),
    ).not.toBeNull();
  } finally {
    await act(async () => root.unmount());
    vi.unstubAllGlobals();
  }
});
