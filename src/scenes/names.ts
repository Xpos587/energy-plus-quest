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
