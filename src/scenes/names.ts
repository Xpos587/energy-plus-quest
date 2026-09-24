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
  alva: { nominative: "Альва", genitive: "Альвы", dative: "Альве" },
  khor: { nominative: "Хор", genitive: "Хора", dative: "Хору" },
  arseniy: { nominative: "Арсений", genitive: "Арсения", dative: "Арсению" },
} as const;
