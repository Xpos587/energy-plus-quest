import mapDesktop from "../../design/scene-01/assets/feedback-v9/production/carrier-desktop.webp";
import mapMobile from "../../design/scene-01/assets/feedback-v9/production/carrier-mobile.webp";
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
    ariaLabel: "Старая машина далеко от склада",
    kicker: "Старая машина",
    label: "Далеко от склада",
  },
  {
    carrier: "near",
    ariaLabel: "Машина у ворот едет медленно",
    kicker: "У ворот",
    label: "Едет медленно",
  },
  {
    carrier: "crew",
    ariaLabel: "Два водителя едут без остановок",
    kicker: "Два водителя",
    label: "Без остановок",
  },
  {
    carrier: "express",
    ariaLabel: "Автоподбор Express уже в пути",
    kicker: "Express",
    label: "Уже в пути",
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
          data-art-version="feedback-v9"
          height="864"
          src={mapDesktop}
          width="1536"
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
              <span
                className={styles.mapVehicleLabel}
                data-map-label={marker.carrier}
              >
                <small>{marker.kicker}</small>
                <strong>{marker.label}</strong>
              </span>
            </button>
          );
        })}
    </section>
  );
}
