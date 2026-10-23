import type { SceneArtProps } from "../types";
import { WorldArt } from "../WorldArt";
import { craneScene } from "./index";
import { CraneZones } from "./CraneZones";

export function CraneArt(props: SceneArtProps) {
  const outcome = props.showResult ? props.selectedId : undefined;
  return (
    <WorldArt
      {...props}
      markers={!props.showResult}
      scene="crane"
      title={craneScene.title}
      options={craneScene.options(props.context)}
      markerLabels={{
        rush: "Отправить Ивана на кран",
        wait: "Ждать 3 часа",
        petr: "Попросить Петра",
        remote: "Управлять из офиса",
      }}
      outcome={outcome}
      giftLocation={outcome && outcome !== "wait" ? "barge" : "quay"}
    >
      {!props.showResult && props.onSelect && (composition => <CraneZones
        composition={composition}
        selectedId={props.selectedId}
        onSelect={props.onSelect}
      />)}
    </WorldArt>
  );
}
