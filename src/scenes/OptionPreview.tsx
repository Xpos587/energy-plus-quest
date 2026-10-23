import type { CSSProperties } from "react";
import { CargoBay, cargoSpaces } from "./compact/CargoBay";
import { inventoryAlphabet } from "./inventory/alphabet";
import { WarehouseZones } from "./inventory/WarehouseZones";
import styles from "./OptionPreview.module.css";
import type { SceneContext, SceneId } from "./types";
import manifest from "./worldManifest.json";
import { imageAsset } from "../game/imageAssets";
import { ImageSources } from "../components/ImageSources";

export function OptionPreview({
  scene,
  optionId,
  context,
}: {
  scene: SceneId;
  optionId: string;
  context: SceneContext;
}) {
  const view = manifest.scenes[scene].desktop;
  const space = cargoSpaces.find((item) => item.id === optionId);
  const point =
    scene === "compact"
      ? space && { x: space.markerX / 1040, y: space.markerY / 550 }
      : scene === "inventory" && optionId === "alphabet"
        ? inventoryAlphabet[context.parcel]
        : view.hotspots.find((item) => item.id === optionId);

  if (!point) return null;

  const cropStyle = {
    "--preview-x": `${point.x * 100}%`,
    "--preview-y": `${point.y * 100}%`,
    "--preview-ratio":
      scene === "compact" ? "1040 / 550" : `${view.width} / ${view.height}`,
  } as CSSProperties;

  return (
    <div
      className={styles.preview}
      data-option-preview={optionId}
      aria-hidden="true"
    >
      <div className={styles.crop} style={cropStyle}>
        {scene === "compact" ? (
          <CargoBay placement={space?.number} focused={optionId} />
        ) : (
          <>
            <picture><ImageSources src={imageAsset(view.image)} /><img src={imageAsset(view.image)} alt="" /></picture>
            {scene === "inventory" && (
              <WarehouseZones context={context} selectedId={optionId} />
            )}
          </>
        )}
      </div>
    </div>
  );
}
