export const parcelNames = {
  camera: {
    nominative: "фотоаппарат",
    accusative: "фотоаппарат",
    genitive: "фотоаппарата",
    prepositional: "фотоаппарате",
    pronoun: "он",
    arrived: "доехал",
  },
  socks: {
    nominative: "вязаные носки",
    accusative: "вязаные носки",
    genitive: "вязаных носков",
    prepositional: "вязаных носках",
    pronoun: "они",
    arrived: "доехали",
  },
  boat: {
    nominative: "лодка",
    accusative: "лодку",
    genitive: "лодки",
    prepositional: "лодке",
    pronoun: "она",
    arrived: "доехала",
  },
} as const;

export const recipientNames = {
  alva: { nominative: "Майма", genitive: "Маймы", dative: "Майме" },
  khor: { nominative: "Хабт", genitive: "Хабта", dative: "Хабту" },
  arseniy: { nominative: "Арсений", genitive: "Арсения", dative: "Арсению" },
} as const;

/** «Вязаные носки для Маймы»: what is carried and to whom, for the task reminder. */
export function deliveryLine(parcel: keyof typeof parcelNames, recipient: keyof typeof recipientNames) {
  const what = parcelNames[parcel].nominative;
  return `${what[0].toUpperCase()}${what.slice(1)} для ${recipientNames[recipient].genitive}`;
}
