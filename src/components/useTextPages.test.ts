import { expect, it } from "vitest";
import { paginateTextBlocks, splitReadingParagraphs, splitTextPages } from "./useTextPages";

it("keeps authored paragraph whitespace available while compact paragraphs fit together", () => {
  const text = "Перевозчик был рядом.\n\nНо доставка опоздала.\n \n\nПоследствие.";
  const parts = splitReadingParagraphs(text);
  expect(parts).toEqual(["Перевозчик был рядом.", "\n\n", "Но доставка опоздала.", "\n \n\n", "Последствие."]);
  expect(parts.join("")).toBe(text);
  const pages = splitTextPages(text, 260, candidate => {
    const paragraphs = splitReadingParagraphs(candidate.trim()).filter((_, index) => index % 2 === 0);
    return paragraphs.length * 40 + (paragraphs.length - 1) * 8 <= 100;
  }, true);
  expect(pages).toEqual(["Перевозчик был рядом.\n\nНо доставка опоздала.\n \n\n", "Последствие."]);
  expect(pages.join("")).toBe(text);
});

it("keeps authored beats on separate pages by default", () => {
  const beats = [
    "Подарок прибыл на причал. ",
    "Его нужно погрузить на баржу.",
    "Кран освободится через три часа. ",
    "Иван ждёт распоряжений.",
  ];
  const pages = paginateTextBlocks(beats, (text) => text.length <= 60);
  expect(pages).toEqual(beats);
  expect(pages.join("")).toBe(beats.join(""));
});

it("combines short briefing blocks only when merging is requested", () => {
  const beats = [
    "Подарок прибыл на причал. ",
    "Его нужно погрузить на баржу.",
    "Кран освободится через три часа. ",
    "Иван ждёт распоряжений.",
  ];
  const pages = paginateTextBlocks(beats, (text) => text.length <= 60, true);
  expect(pages).toEqual([
    "Подарок прибыл на причал. \n\nЕго нужно погрузить на баржу.\n\n",
    "Кран освободится через три часа. \n\nИван ждёт распоряжений.",
  ]);
  expect(pages.join("")).toBe(beats.join("\n\n"));
});

it("splits an oversized beat while preserving its order and wording", () => {
  const beats = ["Первое предложение. Второе предложение.", "Новый смысл."];
  const pages = paginateTextBlocks(beats, (text) => text.length <= 23, true);
  expect(pages).toEqual([
    "Первое предложение. ",
    "Второе предложение.\n\n",
    "Новый смысл.",
  ]);
  expect(pages.join("")).toBe(beats.join("\n\n"));
});

it("measures page zero with its opening presentation during splits and rebalancing", () => {
  const source = "Первый смысл. Следующий смысл. Последний смысл.";
  const fits = (text: string, pageIndex = -1) => text.trim().length <= (pageIndex === 0 ? 14 : 36);
  const pages = splitTextPages(source, 260, fits);
  expect(pages.join("")).toBe(source);
  expect(pages[0].trim()).toBe("Первый смысл.");
  expect(pages.every((text, index) => fits(text, index))).toBe(true);
});
