import type { SceneArtProps } from "../types";
import { WorldArt } from "../WorldArt";
import { inventoryScene } from "./index";
import { WarehouseZones } from "./WarehouseZones";

export function InventoryArt(props: SceneArtProps) {
  return (
    <WorldArt
      {...props}
      scene="inventory"
      title={inventoryScene.title}
      options={inventoryScene.options(props.context)}
      markers
      outcome={props.showResult ? props.selectedId : undefined}
    >
      {composition => !props.showResult && props.onSelect ? (
        <WarehouseZones context={props.context} selectedId={props.selectedId} onSelect={props.onSelect} composition={composition} />
      ) : null}
    </WorldArt>
  );
}
