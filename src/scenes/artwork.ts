import { imageAsset } from "../game/imageAssets";
import { craneChoiceImage, craneOutcomeImage } from "./crane/artwork";
import { lastmileOutcomeImage } from "./lastmile/artworkFamily";
import type { SceneContext, SceneId } from "./types";
import manifest from "./worldManifest.json";

export function sceneChoiceImage(
  scene: SceneId,
  context?: SceneContext,
): string {
  if (scene === "lastmile") {
    return imageAsset(
      "scene-art/lastmile-family-v1/revision-5/intro-wide.webp",
    );
  }
  if (scene === "crane") return imageAsset(craneChoiceImage);
  return imageAsset(manifest.scenes[scene].desktop.image);
}

export function sceneOutcomeImage(
  scene: SceneId,
  selectedId: string,
  context: SceneContext,
): string {
  if (scene === "inventory") {
    // Plaques read left to right: receiving (А–Б) to dispatch (Ю–Я).
    const variant = selectedId === "alphabet" ? `alphabet-${context.parcel}` : selectedId;
    return imageAsset(`scene-art/warehouse-v10/outcome-${variant}.webp`);
  }
  if (scene === "crane") return imageAsset(craneOutcomeImage(selectedId));
  if (scene === "lastmile") {
    const file = lastmileOutcomeImage(selectedId, context);
    if (file) return imageAsset(file);
  }
  return imageAsset(`scene-art/outcomes/${scene}-${selectedId}-v4.webp`);
}
