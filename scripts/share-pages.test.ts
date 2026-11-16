import { expect, test } from "bun:test";
import { shareCards, sharePage, sharePages } from "./share-pages";
import { resolveConfig } from "vite";

test("compile-check mode never generates share images or starts font tooling", async () => {
  const plugin = sharePages();
  const config = await resolveConfig({ configFile: false, root: "/nonexistent-quest-compile-check", mode: "test" }, "build");
  if (typeof plugin.configResolved !== "function" || typeof plugin.closeBundle !== "function") throw new Error("Missing share hooks");
  await plugin.configResolved.call({} as never, config);
  await plugin.closeBundle.call({} as never);
});

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
