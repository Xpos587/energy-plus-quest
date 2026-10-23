import { act } from "react";
import { createRoot } from "react-dom/client";
import { expect, it, vi } from "vitest";
import { ResultCopy, splitResultNarrative } from "./ResultCopy";

it("renders compact paragraphs without changing their source text", async () => {
  vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);
  const host = document.createElement("div");
  const root = createRoot(host);
  const text = "Первое предложение.\n\nВторой абзац.\n \n\nПоследний.";
  try {
    await act(async () => root.render(<ResultCopy paragraphs={[text]} />));
    const copy = host.querySelector('[data-testid="result-copy"]')!;
    expect(copy.textContent).toBe(text);
    expect([...copy.querySelectorAll('span:not([hidden])')].map(node => node.textContent)).toEqual([
      "Первое предложение.", "Второй абзац.", "Последний.",
    ]);
    expect([...copy.querySelectorAll('[hidden]')].map(node => node.textContent)).toEqual(["\n\n", "\n \n\n"]);
  } finally {
    await act(async () => root.unmount());
    vi.unstubAllGlobals();
  }
});

it("balances a tiny trailing page without changing the scenario", () => {
  const text = `${"Слово ".repeat(18)}конец.`;
  const pages = splitResultNarrative(text, 260, (part) => part.length <= 110);
  expect(pages.join("")).toBe(text);
  expect(pages).toHaveLength(2);
  expect(Math.min(...pages.map((part) => part.length))).toBeGreaterThan(40);
  expect(pages.every((part) => part.length <= 110)).toBe(true);
});

it("moves a complete sentence to avoid an isolated short outcome tail", () => {
  const sentences = [
    "Конечно, такой тяжелый груз, как лодка, не мог не повредить посуду при тряске. ",
    "Хрупкие тарелки были просто раздавлены, и к вахтовикам в общежитие доехали осколки. ",
    "Теперь им придется ждать новую поставку.",
  ];
  const text = sentences.join("");
  const pages = splitResultNarrative(text, 260, part => part.length <= 160);
  expect(pages).toEqual([sentences[0], sentences.slice(1).join("")]);
  expect(pages.join("")).toBe(text);
});

it("keeps a short final paragraph on the same page when it fits", () => {
  const text = "Подробности доставки.\n\nВсё получилось.";
  expect(splitResultNarrative(text, 260, (part) => part.length <= 100)).toEqual(
    [text],
  );
});

it("fits long sentences into pages without dropping words or whitespace", () => {
  const text =
    "Очень длинное предложение, которое должно полностью сохраниться при разбиении на небольшие фрагменты без прокрутки.\n\nИтог.";
  const pages = splitResultNarrative(text, 260, (part) => part.length <= 45);
  expect(pages.every((part) => part.length <= 45)).toBe(true);
  expect(pages.join("")).toBe(text);
});

it("preserves every character and splits only between complete sentences", () => {
  const text =
    "Первое предложение с подробным описанием. Второе предложение с последствием!\n\nПоследний абзац без точки";
  const pages = splitResultNarrative(text, 55);
  expect(pages.length).toBeGreaterThan(1);
  expect(pages.join("")).toBe(text);
  expect(pages[0].trim()).toBe("Первое предложение с подробным описанием.");
  expect(splitResultNarrative("Одна фраза.")).toEqual(["Одна фраза."]);
});

it("keeps punctuation attached to its word when filling a result page", () => {
  const text = "Дорога закончилась. На воде он поплыл.";
  const limit = "Дорога закончилась".length;
  const pages = splitResultNarrative(text, 260, part => part.trim().length <= limit, true);
  expect(pages.join("")).toBe(text);
  expect(pages.every(page => !/^[.,!?;:]/u.test(page.trim()))).toBe(true);
});
