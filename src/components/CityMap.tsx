import mapDesktop from "../../design/scene-01/assets/feedback-v4/production/carrier-desktop.webp";
import crewBadge from "../../design/scene-01/assets/feedback-v4/production/choices/crew-badge.webp";
import mapMobile from "../../design/scene-01/assets/feedback-v5/production/carrier-mobile.webp";
import styles from "../App.module.css";
import { carriers } from "../game/content";
import type { CarrierId } from "../game/types";

type CityMapProps = {
  onSelect?: (carrier: CarrierId) => void;
  selected?: CarrierId;
  mode?: "soft" | "live" | "result";
};

const mapMarkers: Array<{
  carrier: CarrierId;
  ariaLabel: string;
  kicker: string;
  label: string;
}> = [
  {
    carrier: "old",
    ariaLabel: "Машина 1: дальний маршрут от склада",
    kicker: "Машина 1",
    label: "Дальше от склада",
  },
  {
    carrier: "near",
    ariaLabel: "Машина 2: короткий маршрут рядом со складом",
    kicker: "Машина 2",
    label: "У ворот склада",
  },
  {
    carrier: "crew",
    ariaLabel: "Машина 3: экипаж из двух водителей",
    kicker: "Машина 3",
    label: "Два водителя",
  },
  {
    carrier: "express",
    ariaLabel: "Express",
    kicker: "Автоподбор",
    label: "Express",
  },
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
          data-art-version="feedback-v4"
          height="800"
          src={mapDesktop}
          width="1328"
        />
      </picture>
      <div aria-hidden="true" className={styles.mapShade} />

      {onSelect &&
        mapMarkers.map((marker) => {
          const carrier = carriers.find((item) => item.id === marker.carrier);

          return (
            <button
              aria-label={`${marker.ariaLabel}: ${carrier?.title ?? "перевозчик"}`}
              className={styles.mapVehicle}
              data-carrier={marker.carrier}
              key={marker.carrier}
              onClick={() => onSelect(marker.carrier)}
              type="button"
            >
              {marker.carrier === "crew" && (
                <img
                  alt=""
                  aria-hidden="true"
                  className={styles.crewMarkerBadge}
                  src={crewBadge}
                />
              )}
              <span data-map-label={marker.carrier}>
                <small>{marker.kicker}</small>
                <strong>{marker.label}</strong>
              </span>
            </button>
          );
        })}
    </section>
  );
}
