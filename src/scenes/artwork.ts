import { imageAsset } from "../game/imageAssets";
import craneFraming from "./crane/outcomeFraming.json";
import { craneFamilyImage } from "./crane/artworkFamily";
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
  if (scene === "crane" && context) {
    const family = craneFamilyImage("choice", context.parcel);
    if (family) return imageAsset(family);
  }
  return imageAsset(manifest.scenes[scene].desktop.image);
}

export function sceneOutcomeImage(
  scene: SceneId,
  selectedId: string,
  context: SceneContext,
): string {
  if (scene === "inventory") {
    if (selectedId === "entrance" || selectedId === "keeper") {
      return imageAsset(`scene-art/warehouse-corrections-2026-10-20/outcomes/${selectedId === "keeper" ? "keeper-v2" : "entrance"}-labels-v1.png`);
    }
    if (selectedId === "wms") {
      return imageAsset("scene-art/warehouse-revision-3-2026-10-18/wms-stylized-v3.png");
    }
    if (["entrance", "alphabet", "wms"].includes(selectedId)) {
      return imageAsset(`scene-art/warehouse-polish-2026-10-17/${selectedId}.webp`);
    }
    return imageAsset(
      `scene-art/warehouse-restored-2026-10-11/${selectedId}${selectedId === "keeper" ? "-v2" : ""}.webp`,
    );
  }
  if (scene === "crane") {
    const family = craneFamilyImage(selectedId, context.parcel);
    if (family) return imageAsset(family);
    const frame = craneFraming[selectedId as keyof typeof craneFraming];
    return imageAsset(`scene-art/outcomes/${frame.file}`);
  }
  if (scene === "lastmile") {
    const file = lastmileOutcomeImage(selectedId, context);
    if (file) return imageAsset(file);
  }
  return imageAsset(`scene-art/outcomes/${scene}-${selectedId}-v4.webp`);
}
