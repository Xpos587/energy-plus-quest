export function interpolateOutcome(
  body: string,
  recipient?: string,
  parcelAccusative?: string,
) {
  return body
    .replaceAll("{recipient}", recipient ?? "получатель")
    .replaceAll("{parcel}", parcelAccusative ?? "подарок");
}
