import type { CSSProperties } from "react";
import { ArtworkLoading } from "../components/ArtworkLoading";
import { useArtworkLoading } from "../components/useArtworkLoading";
import { ImageSources } from "../components/ImageSources";
import { imageAsset } from "../game/imageAssets";
import { sceneOutcomeImage } from "./artwork";
import { outcomeCloseup, outcomeFocus } from "./outcomeFraming";
import { lastmileFlightImage } from "./lastmile/artworkFamily";
import styles from "./SceneOutcomeArt.module.css";
import type { SceneContext, SceneId } from "./types";

const outcomes: Record<string, string> = {
  "inventory-entrance":
    "Сотрудники забирают подарок у входа и несут его через склад к дальней зоне отгрузки.",
  "inventory-keeper":
    "Подарок рядом с отгрузкой, но сотрудники новой смены ищут его среди коробок.",
  "inventory-wms":
    "Система управления складом помогает сотруднику быстро забрать подарок возле отгрузки.",
  "crane-rush":
    "Уставший, но довольный Иван отдыхает у лестницы крана; баржа с подарком отходит от причала.",
  "crane-wait":
    "Баржа с трубами уходит без подарка; Иван смотрит на часы рядом с оставшимся на причале подарком.",
  "crane-petr":
    "Пётр из кабины ближнего крана опускает подарок на баржу, Иван радуется внизу; ящики Петра ждут у дальнего крана.",
  "crane-remote":
    "Иван в удобном кресле управляет краном джойстиками из офиса и смотрит, как подарок опускается на баржу.",
  "lastmile-helicopter":
    "Вертолёт доставляет подарок и трубы на посадочную площадку месторождения.",
  "lastmile-helicopter-remote":
    "После перелёта на вертолёте работники везут подарок дальше от посадочной площадки на вездеходе.",
  "lastmile-rover":
    "Вездеход на больших шинах проходит болото и плывёт через реку с первым льдом.",
  "lastmile-robot":
    "Тележка с подарком застряла в грунте; специальная техника вытаскивает её.",
  "lastmile-pipe-carrier":
    "Колёсный трубовоз возвращает трубы на причал; снегоболотоход с посылкой плывёт к противоположному берегу.",
  "lastmile-pipe-carrier-boat":
    "Колёсный трубовоз возвращает трубы на причал; снегоболотоход с посылкой плывёт к противоположному берегу.",
};

export function SceneOutcomeArt({
  scene,
  selectedId,
  context,
  displayedBeat = 0,
}: {
  scene: SceneId;
  selectedId: string;
  context: SceneContext;
  displayedBeat?: number;
}) {
  const helicopterSequence =
    scene === "lastmile" &&
    selectedId === "helicopter" &&
    context.recipient !== "arseniy";
  const groundLeg = helicopterSequence && displayedBeat > 0;
  let key = `${scene}-${selectedId}`;
  const alphabetResult = scene === "inventory" && selectedId === "alphabet";
  if (alphabetResult) {
    key += `-${context.parcel}`;
  } else if (
    scene === "lastmile" &&
    selectedId === "pipe-carrier" &&
    context.parcel === "boat"
  ) {
    key += "-boat";
  } else if (
    scene === "lastmile" &&
    selectedId === "helicopter" &&
    context.recipient !== "arseniy"
  ) {
    key += "-remote";
  }
  const alt = alphabetResult
    ? "Подарок в закрытой коробке хранится по алфавиту; сотрудники идут за ним отдельно от основного груза."
    : outcomes[key];
  const artwork = useArtworkLoading(
    helicopterSequence && !groundLeg
      ? imageAsset(
          lastmileFlightImage(context),
        )
      : sceneOutcomeImage(scene, selectedId, context),
  );
  if (!alt) return null;
  return (
    <figure
      className={styles.figure}
      data-scene-consequence={key}
      data-outcome-scene={scene}
      data-delivery-leg={scene === "lastmile" && selectedId === "helicopter" ? (groundLeg ? "ground" : "flight") : undefined}
      data-outcome-beat={helicopterSequence ? displayedBeat : undefined}
      style={
        {
          "--outcome-focus": outcomeFocus[key] ?? "50%",
          "--outcome-height": outcomeCloseup[key] ?? "100%",
        } as CSSProperties
      }
    >
      <picture className={styles.picture}>
        <ImageSources src={artwork.src} />
        <img
          ref={artwork.ref}
          className={styles.image}
          src={artwork.src}
          onLoad={artwork.onLoad}
          onError={artwork.onError}
          alt={helicopterSequence && !groundLeg ? outcomes["lastmile-helicopter"] : alt}
          width={1672}
          height={941}
          decoding="async"
          draggable={false}
        />
      </picture>
      <ArtworkLoading status={artwork.status} onRetry={artwork.retry} />
    </figure>
  );
}
