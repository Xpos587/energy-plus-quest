import { expect, it } from "vitest";
import { lastmileScene } from "./index";
import { scenarioParagraph } from "../../game/scenarioDocument";
it("uses the October scenario and snow rover rescue for every gift", () => {
 for (const parcel of ["boat", "camera", "socks"] as const) {
  const context = {profile:"professional" as const, recipient:"alva" as const, parcel};
  expect(lastmileScene.intro(context)[0]).toBe(scenarioParagraph("6B6E0ADA").replace("(имя персонажа)", "Майме"));
  expect(lastmileScene.intro(context)[1]).toBe(scenarioParagraph("4A484891"));
  const result = lastmileScene.options(context).find(o=>o.id === "pipe-carrier")!;
  expect(result.result).toEqual([scenarioParagraph("4E705130"),scenarioParagraph("7F6FF7ED")]);
  expect(result.result.join(" ")).not.toContain("беспилотник");
 }
});
