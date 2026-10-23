import { expect, test } from "vitest";
import { splitTextPages } from "./useTextPages";

test("portrait fill uses remaining words without losing authored whitespace", () => {
  const source = "Первая фраза.\n\nВторая фраза заметно длиннее первой. Последняя.";
  const fits = (text: string) => text.trim().length <= 32;
  const pages = splitTextPages(source, 260, fits, true, true);
  expect(pages.join("")).toBe(source);
  expect(pages[0].trim()).toBe("Первая фраза.\n\nВторая фраза");
  expect(pages.every(fits)).toBe(true);
});
