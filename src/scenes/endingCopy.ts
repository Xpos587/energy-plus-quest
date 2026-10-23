import { scenarioParagraph } from "../game/scenarioDocument";
import type { ParcelId, ProfileId, RecipientId, Scores } from "../game/types";

const recipientAccusative: Record<RecipientId, string> = {
  alva: "Майму",
  khor: "Хабта",
  arseniy: "Арсения",
};
const recipientDative: Record<RecipientId, string> = {
  alva: "Майме",
  khor: "Хабту",
  arseniy: "Арсению",
};
export function endingHeading(recipient: RecipientId) {
  return scenarioParagraph("3742D966").replace(
    "%Персонаж%",
    recipientAccusative[recipient],
  );
}
export function endingGiftCopy(parcel: ParcelId, recipient: RecipientId) {
  const ids = { socks: "4624DDDD", camera: "0F6040AE", boat: "7A9DFB12" };
  return scenarioParagraph(ids[parcel], "mixed")
    .replace(/^- /, "")
    .replace(/ \(для [^)]+\)/, "")
    .replace("ему/ей", recipient === "alva" ? "ей" : "ему")
    .replace("Он/она", recipient === "alva" ? "Она" : "Он");
}
export const endingRestartLabel = scenarioParagraph("15010E9F");
export const endingHomeLabel = scenarioParagraph("5D77C15C");
type LogistType = "future" | "energy" | "empathy" | "efficiency";
export function logistType(profile: ProfileId, scores: Scores): LogistType {
  if (
    profile === "student" &&
    Object.values(scores).every((score) => score < 0)
  )
    return "future";
  // The canonical document does not specify ties; retain a stable order.
  if (scores.energy >= scores.empathy && scores.energy >= scores.efficiency)
    return "energy";
  return scores.empathy >= scores.efficiency ? "empathy" : "efficiency";
}
const titles = {
  future: "3AC343FF",
  energy: "70146CB8",
  empathy: "5A9BBBF0",
  efficiency: "2385D203",
};
const student = {
  future: ["4FA05EB1", "2911242F"],
  energy: ["11A5E583", "238AC3A8", "70686CBD"],
  empathy: ["712078FB", "42D17C78", "2DE95A7F"],
  efficiency: ["6C417900", "761265AC", "5B05AAE4"],
};
const professional = {
  future: ["02ACB54C"],
  energy: ["0F179FD6", "1C98BC56", "66F9DC62"],
  empathy: ["1A889B6F", "04524769", "50272F08"],
  efficiency: ["0A442C30", "1CEB26B1", "766699C1"],
};
export function logistProfileCopy(
  profile: ProfileId,
  recipient: RecipientId,
  scores: Scores,
) {
  const type = logistType(profile, scores);
  const paragraphs = (profile === "student" ? student : professional)[type].map(
    (id) =>
      scenarioParagraph(id)
        .replace("(название персонажа)", recipientDative[recipient])
        .replace(" (ссылка сайт/страницу HH)", ""),
  );
  return {
    type,
    title: scenarioParagraph(titles[type]),
    paragraphs: paragraphs.slice(0, -1),
    callToAction: paragraphs.at(-1)!,
  };
}
