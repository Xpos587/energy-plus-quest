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
    symbol: "01",
  },
  {
    id: "professional",
    title: "Профессионал",
    symbol: "02",
  },
];

export const recipients: ChoiceItem<RecipientId>[] = [
  {
    id: "alva",
    title: "Девочка Альва",
    symbol: "А",
  },
  {
    id: "khor",
    title: "Северный олень Хор",
    description: "«Хор» с языка хантов — самец оленя.",
    symbol: "Х",
  },
  {
    id: "arseniy",
    title: "Вахтовик Арсений",
    symbol: "АР",
  },
];

export const parcels: ParcelChoice[] = [
  {
    id: "camera",
    accusativeTitle: "фотоаппарат",
    title: "Фотоаппарат",
    symbol: "ФОТО",
  },
  {
    id: "socks",
    accusativeTitle: "вязаные носки",
    title: "Вязаные носки",
    symbol: "ТЕПЛО",
  },
  {
    id: "boat",
    accusativeTitle: "лодку",
    title: "Лодка",
    symbol: "ЛОДКА",
  },
];

export const carriers: CarrierChoice[] = [
  {
    id: "old",
    eyebrow: "Машина 1",
    title: "Знакомая «Ласточка»",
    description:
      "Проверенная фура с большим пробегом находится дальше от склада.",
    symbol: "1",
    mapLabel: "1",
    score: { energy: 0, empathy: -3, efficiency: -3 },
    resultTitle: "Маршрут потребовал больше времени",
    resultBody:
      "Дальняя машина прошла дополнительную техническую проверку по пути. Подарок в безопасности, но {recipient} получит {parcel} на неделю позже.",
    delivery: "+7 дней",
    condition: "Большой пробег",
    crew: "Один водитель",
    cost: "Низкая",
  },
  {
    id: "near",
    eyebrow: "Машина 2",
    title: "Ближайшая к центру",
    description: "Исправная фура, которая очень медленно ездит рядом с офисом.",
    symbol: "2",
    mapLabel: "2",
    score: { energy: 1, empathy: 0, efficiency: -2 },
    resultTitle: "Близко — не значит быстро",
    resultBody:
      "Машина была рядом, но водитель ехал очень неторопливо. {recipient} получит {parcel} на три дня позже.",
    delivery: "+3 дня",
    condition: "Исправная техника",
    crew: "Один водитель",
    cost: "Средняя",
  },
  {
    id: "crew",
    eyebrow: "Машина 3",
    title: "Экипаж из двух водителей",
    description: "Новая фура с двумя водителями — они работают посменно.",
    symbol: "3",
    mapLabel: "3",
    score: { energy: -3, empathy: 3, efficiency: 4 },
    resultTitle: "Два водителя лучше одного",
    resultBody:
      "Водители сменяли друг друга и добрались до Лабытнанги без остановок на сон. {recipient} получит {parcel} на три дня раньше, но на следующем участке придётся сэкономить.",
    delivery: "−3 дня",
    condition: "Новая техника",
    crew: "Два водителя",
    cost: "Высокая",
  },
  {
    id: "express",
    eyebrow: "Автоподбор",
    title: "Автоподбор Express",
    description:
      "Подберёт перевозчика по состоянию техники, экипажу и стоимости.",
    symbol: "EX",
    mapLabel: "EX",
    score: { energy: -1, empathy: 5, efficiency: 5 },
    resultTitle: "Перевозчик найден за два часа",
    resultBody:
      "За два часа Express нашёл новую фуру с двумя водителями. {recipient} получит {parcel} в целости и сохранности — на неделю раньше плана!",
    delivery: "−7 дней",
    condition: "Новая техника",
    crew: "Два водителя",
    cost: "Выгодная",
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
