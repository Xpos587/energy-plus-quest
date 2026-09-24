import type { SceneArtProps } from "../types";
import { WorldArt } from "../WorldArt";
import { inventoryScene } from "./index";

export function InventoryArt(props: SceneArtProps) {
  return (
    <WorldArt
      {...props}
      scene="inventory"
      title={inventoryScene.title}
      options={inventoryScene.options(props.context)}
      markers
      outcome={props.showResult ? props.selectedId : undefined}
    />
  );
}
