import { act } from "react";
import { createRoot } from "react-dom/client";
import { expect, it, vi } from "vitest";
import { openingSentenceLength, PageText } from "./PageText";
import { useTextPages } from "./useTextPages";

it("uses the rendered opening weight and gap when measuring, then remains stable on resize", async () => {
  vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);
  const source = "Первый смысл. Следующий смысл. Последний смысл.";
  const measuredStyles: string[][] = [];
  vi.spyOn(HTMLElement.prototype, "clientWidth", "get").mockReturnValue(200);
  vi.spyOn(HTMLElement.prototype, "getBoundingClientRect").mockImplementation(function (this: HTMLElement) {
    let height = 30;
    if (this.tagName === "P") {
      const spans = [...this.children] as HTMLElement[];
      measuredStyles.push(spans.map(span => `${span.style.fontWeight}:${span.style.marginTop}`));
      height = spans.length
        ? spans.reduce((sum, span) => sum + Math.ceil((span.textContent?.trim().length ?? 0) / 15) * 10 + (parseFloat(span.style.marginTop) || 0), 0)
        : Math.ceil((this.textContent?.trim().length ?? 0) / 15) * 10;
    }
    return { x: 0, y: 0, top: 0, left: 0, right: 200, bottom: height, width: 200, height, toJSON: () => ({}) };
  });
  function Reader() {
    const leadLength = openingSentenceLength(source);
    const { body, pages } = useTextPages([source], true, true, false, false, false, false, leadLength);
    return <div ref={body} style={{ padding: 0, borderWidth: 0, maxHeight: 30 }}>
      <output>{JSON.stringify(pages)}</output>
      <PageText text={pages[0]} leadLength={leadLength} />
    </div>;
  }
  const host = document.createElement("div");
  const root = createRoot(host);
  try {
    await act(async () => root.render(<Reader />));
    const pages: string[] = JSON.parse(host.querySelector("output")?.textContent ?? "[]");
    expect(pages[0]).toBe("Первый смысл. ");
    expect(pages.join("")).toBe(source);
    expect(measuredStyles).toContainEqual(["600:", "400:8px"]);
    const before = host.innerHTML;
    await act(async () => window.dispatchEvent(new Event("resize")));
    expect(host.innerHTML).toBe(before);
  } finally {
    await act(async () => root.unmount());
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
  }
});
