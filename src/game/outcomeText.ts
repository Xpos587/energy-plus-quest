import { parcels } from "./content";

export function interpolateOutcome(
  body: string,
  recipient?: string,
  parcelAccusative?: string,
) {
  return body
    .replaceAll("{recipient}", recipient ?? "получатель")
    .replaceAll("{parcel}", parcelAccusative ?? "подарок")
    .replaceAll(
      "{parcelGenitive}",
      parcels.find((parcel) => parcel.accusativeTitle === parcelAccusative)
        ?.genitiveTitle ?? "подарка",
    );
}
