import { recipientNames } from "../scenes/names";
import { parcels } from "./content";

export function interpolateOutcome(
  body: string,
  recipient?: string,
  parcelAccusative?: string,
) {
  return body
    .replaceAll("(подарок)", "подарок")
    .replaceAll("{recipientDative}", Object.values(recipientNames).find(name => name.nominative === recipient)?.dative ?? "получателю")
    .replaceAll("{recipient}", recipient ?? "получатель")
    .replaceAll("{parcel}", parcelAccusative ?? "подарок")
    .replaceAll(
      "{parcelGenitive}",
      parcels.find((parcel) => parcel.accusativeTitle === parcelAccusative)
        ?.genitiveTitle ?? "подарка",
    );
}
