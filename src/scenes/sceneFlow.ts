import { resetBriefingReadingState } from "../components/briefingReadingState";
import { compactScene } from "./compact";
import { inventoryScene } from "./inventory";
import { craneScene } from "./crane";
import { lastmileScene } from "./lastmile";
import type { SceneContext, SceneId } from "./types";

export const remainingScenes = [
  compactScene,
  inventoryScene,
  craneScene,
  lastmileScene,
];
export function briefingParagraphs(scene: SceneId, intro: string[]) {
  // Scene 2 (R19, phone): the cargo line already says where the truck goes, so
  // the choice screen keeps only the question, the goals and the picture.
  if (scene === "compact") return [];
  return scene === "lastmile" ? intro.slice(0, -1) : intro;
}

/** Explicit forward navigation starts the target condition; reloads retain their reading state. */
export function restartSceneCondition(
  id: SceneId,
  context: SceneContext,
  scope: string | undefined,
) {
  const scene = remainingScenes.find((scene) => scene.id === id);
  if (!scene) return;
  resetBriefingReadingState(
    scope,
    scene.title.replace(/^Сцена \d+\.\s*/, ""),
    briefingParagraphs(id, scene.intro(context)),
  );
}
