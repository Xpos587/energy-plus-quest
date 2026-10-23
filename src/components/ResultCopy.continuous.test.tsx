import { act } from "react";
import { createRoot } from "react-dom/client";
import { expect, it, vi } from "vitest";
import { ResultCopy } from "./ResultCopy";

it("exposes the whole consequence without a heading, collapse or page controls", async () => {
  vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);
  const host = document.createElement("div");
  const root = createRoot(host);
  const paragraphs = [
    "Опыт кладовщика помог. ".repeat(30),
    "Подарок доехал целым.",
  ];
  try {
    await act(async () => root.render(<ResultCopy paragraphs={paragraphs} />));
    expect(host.querySelector('[data-testid="result-copy"]')?.textContent).toBe(
      paragraphs.join("\n\n"),
    );
    expect(host.textContent).not.toContain("Что произошло");
    expect(host.querySelector("button, nav")).toBeNull();
    expect(
      host
        .querySelector('[aria-label="Текст результата"]')
        ?.getAttribute("tabindex"),
    ).toBe("0");
  } finally {
    await act(async () => root.unmount());
    vi.unstubAllGlobals();
  }
});

it("shows the compact consequence and its narrative together from the start", async () => {
  vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);
  const host = document.createElement("div");
  const root = createRoot(host);
  try {
    await act(async () =>
      root.render(
        <ResultCopy paragraphs={["Лодка не помещается. ".repeat(20)]}>
          <figure>
            <img src="/boat.png" alt="Лодка шире ниши" />
          </figure>
        </ResultCopy>,
      ),
    );
    expect(host.querySelector("figure")).not.toBeNull();
    expect(
      host.querySelector('[data-testid="result-copy"]')?.textContent,
    ).toContain("Лодка не помещается.");
    expect(host.querySelector("nav")).toBeNull();
  } finally {
    await act(async () => root.unmount());
    vi.unstubAllGlobals();
  }
});
