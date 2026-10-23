import { act } from "react";
import { createRoot } from "react-dom/client";
import { expect, it, vi } from "vitest";
import { ResultCopy } from "./ResultCopy";

it("shows consequence beside the first narrative without an extra illustration page", async () => {
  vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);
  const host = document.createElement("div");
  const root = createRoot(host);
  try {
    await act(async () => root.render(
      <ResultCopy paragraphs={["Лодка не помещается."]} artworkMode="alongside">
        <img src="/boat.png" alt="Лодка шире ниши" />
      </ResultCopy>,
    ));
    expect(host.querySelector("img")?.alt).toBe("Лодка шире ниши");
    expect(host.querySelector('[data-testid="result-copy"]')?.textContent).toBe("Лодка не помещается.");
    expect(host.querySelector('[aria-label="Следующий фрагмент"]')).toBeNull();
  } finally {
    await act(async () => root.unmount());
    vi.unstubAllGlobals();
  }
});
