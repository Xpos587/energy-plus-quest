import type { SceneArtProps } from "../types";
import { WorldArt } from "../WorldArt";
import { lastmileScene } from "./index";

export function LastmileArt(props: SceneArtProps) {
  const outcome = props.showResult ? props.selectedId : undefined;
  return (
    <WorldArt
      {...props}
      scene="lastmile"
      title={lastmileScene.title}
      options={lastmileScene.options(props.context)}
      outcome={outcome}
      rescue={
        outcome === "pipe-carrier"
          ? props.context.parcel === "boat"
            ? "rover"
            : "drone"
          : undefined
      }
    />
  );
}
