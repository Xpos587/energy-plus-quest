import { expect, test } from "bun:test";
import { shareCards, sharePage } from "./share-pages";

test("share page carries absolute preview tags and every result has a card", () => {
  const html = sharePage("Я — «гик»!", "https://example.test/game/r/student-energy/");
  expect(html).toContain('<meta property="og:image" content="https://example.test/game/r/student-energy/card.jpg">');
  expect(html).toContain('<meta property="og:title" content="Я — «гик»!">');
  expect(html).toContain('href="../../"');
  expect(shareCards.map((card) => card.id)).toEqual([
    "student-future", "student-energy", "student-empathy", "student-efficiency",
    "professional-energy", "professional-empathy", "professional-efficiency",
  ]);
});
