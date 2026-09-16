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
    title: "Девочка Альва",
  },
  {
    id: "khor",
    title: "Хор",
  },
  {
    id: "arseniy",
    title: "Вахтовик Арсений",
  },
];

export const parcels: ParcelChoice[] = [
  {
    id: "camera",
    accusativeTitle: "фотоаппарат",
    title: "Фотоаппарат",
  },
  {
    id: "socks",
    accusativeTitle: "вязаные носки",
    title: "Вязаные носки",
  },
  {
    id: "boat",
    accusativeTitle: "лодку",
    title: "Лодка",
  },
];

const oldCarrier: CarrierChoice = {
  id: "old",
  eyebrow: "Дальний маршрут",
  title: "Знакомая «Ласточка»",
  description:
    "Проверенная фура с большим пробегом находится дальше от склада.",
  score: { energy: 0, empathy: -3, efficiency: -3 },
  resultTitle: "Маршрут потребовал больше времени",
  resultBody:
    "«Ласточка», которую вы выбрали, видала виды. В связи с неважным техническим состоянием её задержали на посту — и теперь {recipient} получит {parcel} на неделю позже.",
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
    resultTitle: "Близко — не значит быстро",
    resultBody:
      "Вы отлично сокращаете дистанцию! Ваш перевозчик был рядом со складом и сразу же завернул в ваш логистический центр. Но водитель оказался очень неторопливым: {recipient} получит {parcel} на три дня позже.",
  },
  {
    id: "crew",
    eyebrow: "Два водителя",
    title: "Экипаж из двух водителей",
    description: "Новая фура с двумя водителями — они работают посменно.",
    score: { energy: -3, empathy: 3, efficiency: 4 },
    resultTitle: "Два водителя лучше одного",
    resultBody:
      "Благодаря посменной работе водителей фура добралась до Лабытнанги без остановок на сон. {recipient} получит {parcel} на три дня раньше срока! Но аренда оказалась очень дорогой — на следующей остановке вам лучше сэкономить.",
  },
  {
    id: "express",
    eyebrow: "Автоподбор",
    title: "Автоподбор Express",
    description:
      "Подберёт перевозчика по состоянию техники, экипажу и стоимости.",
    score: { energy: -1, empathy: 5, efficiency: 5 },
    resultTitle: "Перевозчик найден за два часа",
    resultBody:
      "Платформа Express помогла за 2 часа организовать доставку с лучшим доступным перевозчиком: высокие рейтинги, новая фура, два водителя и выгодная цена. Фура доедет без остановок. {recipient} получит {parcel} в целости и сохранности на неделю раньше!",
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
