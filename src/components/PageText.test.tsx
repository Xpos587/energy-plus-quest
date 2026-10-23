import { renderToStaticMarkup } from "react-dom/server";
import { expect, it } from "vitest";
import { PageText } from "./PageText";

it("hides page-edge blank lines while preserving the exact source and internal paragraphs", () => {
  const text = "\n\nТеперь Хабт получит подарок.\n\nВ целости и сохранности!\n";
  const host = document.createElement("div");
  host.innerHTML = renderToStaticMarkup(<PageText text={text} />);
  expect(host.textContent).toBe(text);
  host.querySelectorAll("[hidden]").forEach((node) => node.remove());
  expect(host.textContent).toBe(text.trim());
});

it("separates only the opening sentence and preserves every authored character", () => {
  const text = "\n Первый смысл. \n\nОстальная история.\n";
  const host = document.createElement("div");
  host.innerHTML = renderToStaticMarkup(<PageText text={text} leadLength={text.indexOf("Остальная")} />);
  expect(host.textContent).toBe(text);
  const lead = host.querySelector<HTMLElement>("[data-reading-lead]");
  expect(lead?.textContent).toBe("Первый смысл.");
  expect(lead?.style.fontWeight).toBe("600");
  expect(host.querySelector<HTMLElement>("[data-reading-remainder]")?.style.marginTop).toBe("8px");
  expect(host.querySelector<HTMLElement>("[data-reading-remainder]")?.style.fontWeight).toBe("400");
});

it("adds no opening paragraph gap when a page contains only the lead", () => {
  const text = "Первая фраза. \n\n";
  const host = document.createElement("div");
  host.innerHTML = renderToStaticMarkup(<PageText text={text} leadLength={text.length} />);
  expect(host.textContent).toBe(text);
  expect(host.querySelector("[data-reading-remainder]")).toBeNull();
});
