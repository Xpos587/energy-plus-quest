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
      "scene-art/lastmile-family-v1/choice-final-wide-v10.webp",
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
    if (selectedId === "wms") {
      return imageAsset("scene-art/warehouse-revision-3-2026-10-18/wms-stylized-v3.png");
    }
    // Plaques read from dispatch (А–Б) back to receiving (Ю–Я), as the scenario says.
    const variant = selectedId === "alphabet" ? `alphabet-${context.parcel}` : selectedId;
    return imageAsset(`scene-art/warehouse-logic-2026-10-28/outcome-${variant}.webp`);
  }
  if (scene === "crane") return imageAsset(craneOutcomeImage(selectedId));
  if (scene === "lastmile") {
    const file = lastmileOutcomeImage(selectedId, context);
    if (file) return imageAsset(file);
  }
  return imageAsset(`scene-art/outcomes/${scene}-${selectedId}-v4.webp`);
}
