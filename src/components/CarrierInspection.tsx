import { CalendarDays, Gauge, Users } from "lucide-react";
import { carrierFacts, type MapCarrierId } from "../game/carrierFacts";
import type { CarrierId } from "../game/types";
import { PagedDescription } from "./PagedDescription";
import styles from "./CarrierInspection.module.css";
import { imageAsset } from "../game/imageAssets";
import { CarrierSpeedometer } from "./CarrierSpeedometer";

const truckImage = (id: MapCarrierId) =>
  imageAsset(`review/carrier-art-2026-09-27/closer-${id}.png`);

/** Content only: the shared choice UI owns heading, confirmation and return. */
export function CarrierInspection({
  carrierId,
  showPreview = true,
}: {
  carrierId: CarrierId;
  showPreview?: boolean;
}) {
  if (carrierId === "express") {
    return (
      <PagedDescription
        paragraphs={["Поручить поиск перевозчика платформе Express."]}
      />
    );
  }
  const facts = carrierFacts[carrierId];
  const instruments = !showPreview;
  return (
    <div
      className={styles.inspection}
      data-carrier-inspection={carrierId}
      data-map-inspection={!showPreview || undefined}
      data-carrier-instruments={instruments || undefined}
    >
      {showPreview && (
        <img
          className={styles.photo}
          src={truckImage(carrierId)}
          width={1672}
          height={941}
          decoding="async"
          alt={facts.imageAlt}
        />
      )}
      <dl className={styles.facts}>
        <div>
          <dt>{instruments ? "Темп движения" : "Максимальная скорость"}</dt>
          <dd className={instruments ? styles.speedReadout : undefined}>
            {instruments ? (
              <CarrierSpeedometer key={carrierId} carrierId={carrierId} />
            ) : (
              !showPreview && <Gauge aria-hidden="true" />
            )}
            {!instruments && <span>{facts.citySpeedKmh} км/ч</span>}
          </dd>
        </div>
        <div>
          <dt>Год выпуска</dt>
          <dd>
            {!showPreview && <CalendarDays aria-hidden="true" />}
            <span>{facts.buildYear}</span>
          </dd>
        </div>
        {carrierId === "crew" && (
          <div>
            <dt>Экипаж</dt>
            <dd>
              {!showPreview && <Users aria-hidden="true" />}
              <span>Два водителя</span>
            </dd>
          </div>
        )}
      </dl>
    </div>
  );
}
