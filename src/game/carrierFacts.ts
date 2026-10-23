import type { CarrierId } from "./types";

export type MapCarrierId = Exclude<CarrierId, "express">;
export const mapCarrierIds: MapCarrierId[] = ["old", "near", "crew", "old4"];

// Visual descriptions are for image alternatives, not repeated as card copy.
// Card numbers are fictional prototype details, not sourced fleet records.
// City speeds stay below 60 km/h and preserve the measured animation order:
// #3 > #1 > #4 > #2. Results and scores remain in content.ts.
export const carrierFacts: Record<
  MapCarrierId,
  {
    label: string;
    imageAlt: string;
    citySpeedKmh: number;
    buildYear: number;
  }
> = {
  old: {
    label: "Красная фура",
    imageAlt: "Красный тягач с полуприцепом на городской дороге",
    citySpeedKmh: 36,
    buildYear: 2011,
  },
  near: {
    label: "Синяя фура",
    imageAlt: "Синий тягач с полуприцепом на городской дороге",
    citySpeedKmh: 17,
    buildYear: 2021,
  },
  crew: {
    label: "Зелёная фура",
    imageAlt: "Зелёный тягач с полуприцепом на городской дороге",
    citySpeedKmh: 48,
    buildYear: 2024,
  },
  old4: {
    label: "Жёлтая фура",
    imageAlt: "Жёлтый тягач с полуприцепом на городской дороге",
    citySpeedKmh: 27,
    buildYear: 2013,
  },
};
