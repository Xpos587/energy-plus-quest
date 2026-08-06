import mapMobile from "../../design/scene-01/assets/map-mobile/edited.webp";
import mapDesktop from "../../design/scene-01/assets/map-v2-desktop/edited.webp";
import locatorBlue from "../../design/scene-01/assets/ui/locator-blue.png";
import locatorOrange from "../../design/scene-01/assets/ui/locator-orange.png";
import styles from "../App.module.css";
import { carriers } from "../game/content";
import type { CarrierId } from "../game/types";

type CityMapProps = {
  onSelect?: (carrier: CarrierId) => void;
  selected?: CarrierId;
  mode?: "soft" | "live" | "result" | "express" | "complete";
};

const mapMarkers: Array<{
  carrier: CarrierId;
  label: string;
}> = [
  { carrier: "old", label: "Машины 1 и 4" },
  { carrier: "near", label: "Машина 2" },
  { carrier: "crew", label: "Машина 3" },
  { carrier: "express", label: "Express" },
];

export function CityMap({ onSelect, selected, mode = "soft" }: CityMapProps) {
  return (
    <section
      aria-label={onSelect ? "Карта доступных перевозчиков" : "Карта маршрута"}
      className={styles.cityMap}
      data-mode={mode}
      data-selected={selected}
    >
      <picture className={styles.mapPicture}>
        <source media="(max-width: 760px)" srcSet={mapMobile} />
        <img
          alt=""
          aria-hidden="true"
          className={styles.mapImage}
          height="864"
          src={mapDesktop}
          width="1536"
        />
      </picture>
      <div aria-hidden="true" className={styles.mapShade} />

      {mapMarkers.map((marker) => {
        const carrier = carriers.find((item) => item.id === marker.carrier);
        const markerCode =
          marker.carrier === "express" ? "EX" : marker.label.match(/\d/)?.[0];
        const locatorArtwork =
          marker.carrier === "express" ? locatorOrange : locatorBlue;
        const label =
          marker.carrier === "express"
            ? "Express на карте: цифровой автоподбор"
            : `${marker.label}: ${carrier?.title ?? "перевозчик"}`;

        if (!onSelect) {
          return selected === marker.carrier ? (
            <span
              aria-hidden="true"
              className={styles.mapHotspot}
              data-carrier={marker.carrier}
              data-selected="true"
              key={marker.carrier}
            >
              <span className={styles.locatorBadge}>
                <img alt="" src={locatorArtwork} />
                <b>{markerCode}</b>
              </span>
            </span>
          ) : null;
        }

        return (
          <button
            aria-label={label}
            className={styles.mapHotspot}
            data-carrier={marker.carrier}
            data-selected={selected === marker.carrier}
            key={marker.carrier}
            onClick={() => onSelect(marker.carrier)}
            type="button"
          >
            <span className={styles.locatorBadge}>
              <img alt="" aria-hidden="true" src={locatorArtwork} />
              <b>{markerCode}</b>
            </span>
          </button>
        );
      })}
    </section>
  );
}
