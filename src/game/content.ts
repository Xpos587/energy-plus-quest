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
    title: "Альва",
  },
  {
    id: "khor",
    title: "Хор",
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

export const carrierBriefing =
  "Доставить {parcel} на край света? Для нас нет ничего невозможного. Для начала найдем лучшего перевозчика, который отправит ваш груз в далекий город Лабытнанги.";

export const carrierQuestion =
  "Прежде всего, нам нужно найти лучший транспорт для перевозки подарка. Выберите фуру, которая лучше всего справится с задачей:";

const oldCarrier: CarrierChoice = {
  id: "old",
  eyebrow: "Дальний маршрут",
  title: "Знакомая «Ласточка»",
  description:
    "Проверенная фура с большим пробегом находится дальше от склада.",
  score: { energy: 0, empathy: -3, efficiency: -3 },
  resultTitle: "Маршрут потребовал больше времени",
  resultBody:
    "«Ласточка», которую вы выбрали, видала виды. В связи с неважным техническим состоянием ее задержали на посту – и теперь {recipient} на неделю позже получит {parcel}.",
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
    resultTitle: "Счастье уже близко!",
    resultBody:
      "Ваш перевозчик был рядом с офисом и сразу же завернул в ваш логистический центр.\n\nНо водитель оказался очень неторопливым – он на 3 дня опоздал с доставкой {parcelGenitive}.",
  },
  {
    id: "crew",
    eyebrow: "Два водителя",
    title: "Экипаж из двух водителей",
    description: "Новая фура с двумя водителями — они работают посменно.",
    score: { energy: -3, empathy: 3, efficiency: 4 },
    resultTitle: "Два водителя лучше одного!",
    resultBody:
      "Благодаря посменной работе водителей фура добралась до Лабытнанги без остановок на сон - на три дня раньше срока! Но аренда такого транспорта оказалась очень дорогой – на следующей остановке вам лучше сэкономить.",
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
      "Вы использовали платформу организации грузоперевозок Express и всего за два часа организовали доставку, выбрав перевозчика с высоким рейтингом, двумя водителями в фуре и по выгодной цене.\n\nУ него высокие рейтинги, новая фура сразу с двумя водителями и выгодная стоимость перевозки. Ваш (подарок) доехал до цели без остановок.\n\nТеперь {recipient} получит {parcel} а целости и сохранности на неделю раньше запланированного!",
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
