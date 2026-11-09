import { expect, it } from "vitest";
import { resultHeading } from "./ScenesGame";

it("names the pipe carriers' limit in the heading (Teo, 05.11)", () => {
  expect(resultHeading("lastmile", "pipe-carrier", "camera")).toMatch(/до берега — да, через речку — нет/i);
});
