import { expect, test } from "bun:test";
import { rankName, shareCards, sharePage, sharePages } from "./share-pages";
import { resolveConfig } from "vite";

test("compile-check mode never generates share images or starts font tooling", async () => {
  const plugin = sharePages();
  const config = await resolveConfig({ configFile: false, root: "/nonexistent-quest-compile-check", mode: "test" }, "build");
  if (typeof plugin.configResolved !== "function" || typeof plugin.closeBundle !== "function") throw new Error("Missing share hooks");
  await plugin.configResolved.call({} as never, config);
  await plugin.closeBundle.call({} as never);
});

test("share page is the sender's certificate in third person with absolute preview tags", () => {
  expect(rankName("Вы — логистический гик!")).toBe("Логистический гик");
  expect(rankName("Вы — логист будущего.")).toBe("Логист будущего");
  const assets = { art: "data:image/webp;base64,A", brand: "data:image/svg+xml;base64,B", regular: "data:font/woff2;base64,C", bold: "data:font/woff2;base64,D" };
  const html = sharePage("Логистический гик", "https://example.test/game/r/student-energy/", assets);
  expect(html).toContain('<meta property="og:image" content="https://example.test/game/r/student-energy/card.jpg">');
  expect(html).toContain('<meta property="og:title" content="Участник игры «Доставляем радость» получил звание «Логистический гик»">');
  const certificate = html.match(/<article class="certificate">([\s\S]*)<\/article>/)![1];
  expect(certificate).toContain("<h1>Сертификат</h1>");
  expect(certificate).toContain('<p class="lead">Участник игры «Доставляем радость» получил звание</p>');
  expect(certificate).toContain('<p class="rank">Логистический гик</p>');
  expect(certificate).toContain(`src="${assets.art}"`);
  expect(certificate).not.toMatch(/<a\b|<button\b/);
  /* One quiet CTA, outside the certificate. */
  expect(html.match(/<a\b[^>]*>[^<]*<\/a>/g)).toEqual(['<a class="cta" href="../../">Пройти игру самому</a>']);
  expect(html).not.toMatch(/(^|[^а-яё])(Я|какой логист вы)(?![а-яё])/u);
  expect(shareCards.map((card) => card.id)).toEqual([
    "student-future", "student-energy", "student-empathy", "student-efficiency",
    "professional-energy", "professional-empathy", "professional-efficiency",
  ]);
});
