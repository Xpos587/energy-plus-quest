import source from "./carrierSourceCopy.json" with { type: "json" };

// Independent DOCX fixture, verified by scripts/check-scene-source.py.
// Only paragraph-edge whitespace, named placeholders and the button direction are normalized.
const paragraph = (id: keyof typeof source.paragraphs) =>
  source.paragraphs[id]
    .trim()
    .replaceAll("%имя получателя%", "{recipient}")
    .replaceAll(
      "%название посылки%",
      id === "p127" ? "{parcelGenitive}" : "{parcel}",
    )
    .replaceAll("%выбранную посылку%", "{parcel}")
    .replace(" Кнопка «Узнать больше об Express»", "");

export const sourceCopy = {
  // Previously approved short UI labels are not replaced by historical onboarding.
  profileHeading: "Кто отправится в путь?",
  profiles: ["Студент", "Профессионал"],
  recipientHeading: "Выберите получателя",
  recipients: ["Альва", "Хор", "Арсений"],
  parcelHeading: "Что будет в посылке?",
  parcels: ["Фотоаппарат", "Вязаные носки", "Лодка"],
  carrierPrompt: paragraph("p109"),
  carrierBriefing: paragraph("p69"),
  carrierAutoSelect: "Подобрать автоматически",
  outcomes: {
    old: {
      heading: "Маршрут потребовал больше времени",
      body: paragraph("p114"),
    },
    near: {
      heading: paragraph("p124"),
      body: [paragraph("p125"), paragraph("p127")].join("\n\n"),
    },
    crew: {
      heading: paragraph("p137"),
      body: paragraph("p138"),
    },
    express: {
      heading: "Перевозчик найден за два часа",
      body: [paragraph("p147"), paragraph("p149"), paragraph("p151")].join(
        "\n\n",
      ),
    },
  },
} as const;
