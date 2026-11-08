import { expect, it } from "vitest";
import { carriers } from "../game/content";
import { compactScene } from "./compact";
import { craneScene } from "./crane";
import { inventoryScene } from "./inventory";
import { lastmileScene } from "./lastmile";
import { compareChoice } from "./ScenesGame";
import type { SceneDefinition } from "./types";

const goals: [string, string, string] = ["A", "B", "C"];
const summaries = (scene: SceneDefinition, parcel: "camera" | "socks" | "boat" = "camera") => {
  const scores = scene.options({ parcel, recipient: "alva", profile: "student" }).map((o) => o.score);
  return scores.map((score) => compareChoice(score, scores, goals).text);
};

it("compares a choice with the others instead of grading it", () => {
  const all = [...summaries(compactScene), ...summaries(compactScene, "boat"), ...summaries(inventoryScene), ...summaries(craneScene), ...summaries(lastmileScene), ...carriers.map((c) => compareChoice(c.score, carriers.map((x) => x.score), goals).text)];
  for (const text of all) expect(text).not.toMatch(/Отлич|Неудач|Можно лучше|Лучше всех|Наравне/);
  expect(summaries(inventoryScene)).toEqual([
    "Обходит два варианта: «C»",
    "Обходит один вариант: «B»",
    "Сильная сторона: «B»",
    "Сильные стороны: «A» и «C»",
  ]);
});
