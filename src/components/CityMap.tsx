import crewArtwork from "../../design/scene-01/assets/feedback-v8/production/carrier-crew.webp";
import mapDesktop from "../../design/scene-01/assets/feedback-v8/production/carrier-desktop.webp";
import expressArtwork from "../../design/scene-01/assets/feedback-v8/production/carrier-express.webp";
import mapMobile from "../../design/scene-01/assets/feedback-v8/production/carrier-mobile.webp";
import nearArtwork from "../../design/scene-01/assets/feedback-v8/production/carrier-near.webp";
import oldArtwork from "../../design/scene-01/assets/feedback-v8/production/carrier-old.webp";
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
  artwork: string;
  kicker: string;
  label: string;
}> = [
  {
    carrier: "old",
    ariaLabel: "Старая машина далеко от склада",
    artwork: oldArtwork,
    kicker: "Старая машина",
    label: "Далеко от склада",
  },
  {
    carrier: "near",
    ariaLabel: "Машина у ворот едет медленно",
    artwork: nearArtwork,
    kicker: "У ворот",
    label: "Едет медленно",
  },
  {
    carrier: "crew",
    ariaLabel: "Два водителя едут без остановок",
    artwork: crewArtwork,
    kicker: "Два водителя",
    label: "Без остановок",
  },
  {
    carrier: "express",
    ariaLabel: "Автоподбор Express уже в пути",
    artwork: expressArtwork,
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
          data-art-version="feedback-v8"
          height="864"
          src={mapDesktop}
          width="1536"
        />
      </picture>
      <div aria-hidden="true" className={styles.mapShade} />

      {onSelect && (
        <>
          <svg
            aria-hidden="true"
            className={`${styles.routeNetwork} ${styles.routeNetworkDesktop}`}
            viewBox="0 0 1536 864"
          >
            <path
              className={styles.routeOld}
              d="M 120 315 C 270 280 430 350 665 432"
              pathLength="100"
            />
            <path
              className={styles.routeNear}
              d="M 635 425 C 700 460 770 450 835 485"
              pathLength="100"
            />
            <path
              className={styles.routeCrew}
              d="M 250 730 C 430 650 650 605 930 640"
              pathLength="100"
            />
            <path
              className={styles.routeExpress}
              d="M 1420 650 C 1240 620 1070 565 815 490"
              pathLength="100"
            />
          </svg>
          <svg
            aria-hidden="true"
            className={`${styles.routeNetwork} ${styles.routeNetworkMobile}`}
            viewBox="0 0 944 1792"
          >
            <path
              className={styles.routeOld}
              d="M 150 330 C 290 300 390 370 470 455"
              pathLength="100"
            />
            <path
              className={styles.routeNear}
              d="M 430 560 C 560 610 660 585 760 660"
              pathLength="100"
            />
            <path
              className={styles.routeCrew}
              d="M 90 1390 C 280 1260 480 1180 690 1160"
              pathLength="100"
            />
            <path
              className={styles.routeExpress}
              d="M 910 1030 C 770 980 680 900 555 790"
              pathLength="100"
            />
          </svg>
          {mapMarkers.map((marker) => {
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
                <span aria-hidden="true" className={styles.vehicleTrail} />
                <img
                  alt=""
                  aria-hidden="true"
                  className={styles.vehicleSprite}
                  src={marker.artwork}
                />
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
        </>
      )}
    </section>
  );
}
