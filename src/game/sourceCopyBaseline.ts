import { scenarioParagraph } from "./scenarioDocument";
// Canonical Markdown player copy; visual and mechanic blocks are rejected.
// Only grammatical placeholders and paragraph edges change.
const paragraph = (id: string) => scenarioParagraph(id).trim()
  .replaceAll("%имя получателя%", "{recipient}")
  .replaceAll("%название посылки%", id === "512D2AEE" ? "{parcelGenitive}" : "{parcel}")
  .replaceAll("%выбранную посылку%", "{parcel}")
  .replaceAll("%Посылку%", "{parcel}")
  .replaceAll("№герой%", "{recipientDative}");
const intro = paragraph("2A80D000");
const prompt = intro.slice(intro.lastIndexOf(". ") + 2);
const near = paragraph("512D2AEE");
const nearHeading = near.slice(0, near.indexOf("!") + 1);
export const sourceCopy = {
  profileHeading: "Кто отправится в путь?", profiles: ["Студент", "Профессионал"],
  recipientHeading: "Выберите получателя", recipients: ["Майма", "Хабт", "Арсений"],
  parcelHeading: "Что будет в посылке?", parcels: ["Фотоаппарат", "Вязаные носки", "Лодка"],
  carrierPrompt: prompt, carrierBriefing: intro.slice(0, -prompt.length).trim(),
  carrierAutoSelect: scenarioParagraph("3B38D1EB", "mixed").replace(/^Кнопка «|»$/g, ""),
  outcomes: {
    old: { heading: "", body: paragraph("6656C720") },
    near: { heading: nearHeading, body: near.slice(nearHeading.length).trim() },
    crew: { heading: paragraph("4264BB8C"), body: paragraph("67C929B0") },
    express: { heading: "", body: [paragraph("7E9315CC"), paragraph("46FE90C1")].join("\n\n") },
  },
} as const;
