import type { SceneArtProps } from "../types";
import { WorldArt } from "../WorldArt";
import { craneScene } from "./index";

export function CraneArt(props: SceneArtProps) {
  const outcome = props.showResult ? props.selectedId : undefined;
  return (
    <WorldArt
      {...props}
      scene="crane"
      title={craneScene.title}
      options={craneScene.options(props.context)}
      outcome={outcome}
      giftLocation={outcome && outcome !== "wait" ? "barge" : "quay"}
    />
  );
}
