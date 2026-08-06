import type {
  CarrierChoice,
  ChoiceItem,
  ParcelId,
  ProfileId,
  RecipientId,
} from "./types";

export const profiles: ChoiceItem<ProfileId>[] = [
  {
    id: "student",
    eyebrow: "Начинаю маршрут",
    title: "Студент",
    description: "Проверю себя в реальной логистической цепочке.",
    symbol: "01",
  },
  {
    id: "professional",
    eyebrow: "Знаю отрасль",
    title: "Профессионал",
    description: "Сравню своё решение с цифровыми инструментами.",
    symbol: "02",
  },
];

export const recipients: ChoiceItem<RecipientId>[] = [
  {
    id: "alva",
    eyebrow: "Посёлок на Севере",
    title: "Альва",
    description: "Маленькая жительница Севера ждёт свою большую радость.",
    symbol: "А",
  },
  {
    id: "khor",
    eyebrow: "Тундровый маршрут",
    title: "Олень Хор",
    description: "Хор поможет доставке пройти последний участок пути.",
    symbol: "Х",
  },
  {
    id: "arseniy",
    eyebrow: "Вахтовый посёлок",
    title: "Арсений",
    description: "Вахтовик ждёт посылку вдали от больших городов.",
    symbol: "АР",
  },
];

export const parcels: ChoiceItem<ParcelId>[] = [
  {
    id: "camera",
    eyebrow: "Хрупкий груз",
    title: "Фотоаппарат",
    description: "Нужны бережная перевозка и точный срок.",
    symbol: "ФОТО",
  },
  {
    id: "socks",
    eyebrow: "Тёплая посылка",
    title: "Вязаные носки",
    description: "Небольшой груз, который особенно важен получателю.",
    symbol: "ТЕПЛО",
  },
  {
    id: "boat",
    eyebrow: "Негабаритный груз",
    title: "Лодка",
    description: "Потребует места и внимательной организации маршрута.",
    symbol: "ЛОДКА",
  },
];

export const carriers: CarrierChoice[] = [
  {
    id: "old",
    eyebrow: "Машины 1 и 4",
    title: "Знакомая «Ласточка»",
    description: "Низкая цена и знакомый водитель, но техника изношена.",
    symbol: "1/4",
    mapLabel: "1/4",
    score: { energy: 0, empathy: -3, efficiency: -3 },
    resultTitle: "Возраст берёт своё",
    resultBody:
      "Фуру задержали на проверке из-за технического состояния. Посылка придёт на неделю позже.",
    delivery: "+7 дней",
    condition: "Изношенная техника",
    crew: "Один водитель",
    cost: "Низкая",
  },
  {
    id: "near",
    eyebrow: "Машина 2",
    title: "Ближайшая к центру",
    description: "Короткая подача и исправная фура, но водитель один.",
    symbol: "2",
    mapLabel: "2",
    score: { energy: 1, empathy: 0, efficiency: -2 },
    resultTitle: "Близко — не значит быстро",
    resultBody:
      "Фура сразу приехала на погрузку, но неторопливый водитель задержал доставку на три дня.",
    delivery: "+3 дня",
    condition: "Исправная техника",
    crew: "Один водитель",
    cost: "Средняя",
  },
  {
    id: "crew",
    eyebrow: "Машина 3",
    title: "Экипаж из двух водителей",
    description: "Новая фура и сменный экипаж, но стоимость высокая.",
    symbol: "3",
    mapLabel: "3",
    score: { energy: -3, empathy: 3, efficiency: 4 },
    resultTitle: "Быстро, но дорого",
    resultBody:
      "Сменный экипаж привёз груз на три дня раньше срока. Бюджет следующего этапа стал заметно меньше.",
    delivery: "−3 дня",
    condition: "Новая техника",
    crew: "Два водителя",
    cost: "Высокая",
  },
  {
    id: "express",
    eyebrow: "Цифровой автоподбор",
    title: "Запустить Express",
    description: "Сервис сравнит цену, рейтинг, технику и график экипажа.",
    symbol: "EX",
    mapLabel: "EX",
    score: { energy: -1, empathy: 5, efficiency: 5 },
    resultTitle: "Перевозчик найден за два часа",
    resultBody:
      "Express выбрал новую фуру, высокий рейтинг, двух водителей и выгодную стоимость. Груз прибудет на неделю раньше плана.",
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
