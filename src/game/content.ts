import { sourceCopy } from "./sourceCopyBaseline";
import type {
  CarrierChoice,
  ChoiceItem,
  ParcelChoice,
  ParcelId,
  ProfileId,
  RecipientId,
} from "./types";

export const profiles: ChoiceItem<ProfileId>[] = [
  {
    id: "student",
    title: "Студент",
  },
  {
    id: "professional",
    title: "Профессионал",
  },
];

export const recipients: ChoiceItem<RecipientId>[] = [
  {
    id: "alva",
    title: "Майма",
  },
  {
    id: "khor",
    title: "Хабт",
  },
  {
    id: "arseniy",
    title: "Арсений",
  },
];

export const parcels: ParcelChoice[] = [
  {
    id: "camera",
    accusativeTitle: "фотоаппарат",
    genitiveTitle: "фотоаппарата",
    title: "Фотоаппарат",
  },
  {
    id: "socks",
    accusativeTitle: "вязаные носки",
    genitiveTitle: "вязаных носков",
    title: "Вязаные носки",
  },
  {
    id: "boat",
    accusativeTitle: "лодку",
    genitiveTitle: "лодки",
    title: "Лодка",
  },
];

export const carrierBriefing = sourceCopy.carrierBriefing;

export const carrierQuestion = sourceCopy.carrierPrompt;

const oldCarrier: CarrierChoice = {
  id: "old",
  eyebrow: "Дальний маршрут",
  title: "Знакомая «Ласточка»",
  description:
    "Проверенная фура с большим пробегом находится дальше от склада.",
  score: { energy: 0, empathy: -3, efficiency: -3 },
  resultTitle: sourceCopy.outcomes.old.heading,
  resultBody: sourceCopy.outcomes.old.body,
};

export const carriers: CarrierChoice[] = [
  oldCarrier,
  { ...oldCarrier, id: "old4" },
  {
    id: "near",
    eyebrow: "У ворот склада",
    title: "Ближайшая к центру",
    description: "Исправная фура, которая очень медленно ездит рядом с офисом.",
    score: { energy: 1, empathy: 0, efficiency: -2 },
    resultTitle: sourceCopy.outcomes.near.heading,
    resultBody: sourceCopy.outcomes.near.body,
  },
  {
    id: "crew",
    eyebrow: "Два водителя",
    title: "Экипаж из двух водителей",
    description: "Новая фура с двумя водителями — они работают посменно.",
    score: { energy: -3, empathy: 3, efficiency: 4 },
    resultTitle: sourceCopy.outcomes.crew.heading,
    resultBody: sourceCopy.outcomes.crew.body,
  },
  {
    id: "express",
    eyebrow: "Автоподбор",
    title: "Автоподбор Express",
    description:
      "Подберёт перевозчика по состоянию техники, экипажу и стоимости.",
    score: { energy: -1, empathy: 5, efficiency: 5 },
    resultTitle: sourceCopy.outcomes.express.heading,
    resultBody: sourceCopy.outcomes.express.body,
  },
];

export const findProfile = (id?: ProfileId) =>
  profiles.find((item) => item.id === id);

export const findRecipient = (id?: RecipientId) =>
  recipients.find((item) => item.id === id);

export const findParcel = (id?: ParcelId) =>
  parcels.find((item) => item.id === id);

export const findCarrier = (id?: string) =>
  carriers.find((item) => item.id === id);
