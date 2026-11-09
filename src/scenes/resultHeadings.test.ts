import { expect, it } from "vitest";
import { carriers } from "../game/content";
import { compactScene } from "./compact";
import { craneScene } from "./crane";
import { inventoryScene } from "./inventory";
import { lastmileScene } from "./lastmile";
import { carrierHeadings, resultHeading } from "./ScenesGame";
import type { SceneDefinition } from "./types";

/** R19 (call 05.11): a result heading names what happened, never grades or compares the choice. */
const verdict = /Отлич|Неудач|Можно лучше|Лучше|Хуже|Сильн(ая|ые) сторон|Обходит|Наравне с лучшими|Эффективн|неэффективн|правильн|ошибк/i;
const headings: [string, string][] = [];
for (const carrier of carriers) headings.push([`carrier:${carrier.id}`, carrierHeadings[carrier.id]]);
for (const parcel of ["camera", "socks", "boat"] as const)
  for (const option of compactScene.options({ parcel, recipient: "alva", profile: "student" }))
    headings.push([`compact:${parcel}:${option.id}`, resultHeading("compact", option.id, parcel)!]);
const scenes: SceneDefinition[] = [inventoryScene, craneScene, lastmileScene];
for (const scene of scenes)
  for (const option of scene.options({ parcel: "camera", recipient: "alva", profile: "student" }))
    headings.push([`${scene.id}:${option.id}`, resultHeading(scene.id, option.id, "camera")!]);

it("every result has a heading that describes what happened", () => {
  for (const [where, heading] of headings) {
    expect(heading, where).toBeTruthy();
    expect(heading, where).not.toMatch(verdict);
    expect(heading.length, where).toBeLessThanOrEqual(48);
  }
});

it("the comparison line is gone from scene 1", () => {
  expect(Object.keys(carrierHeadings).sort()).toEqual(carriers.map((carrier) => carrier.id).sort());
  expect(carrierHeadings.near).toBe("Рядом, но на три дня позже");
  expect(carrierHeadings).not.toHaveProperty("pipe-carrier");
});
