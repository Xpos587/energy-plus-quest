import type { ParcelId } from "../game/types";
import type { SceneId } from "./types";
import { lastmileHeadings } from "./lastmile/LastmileFacts";

/** Result headings (R18 draft for Teo): what happened, taken from the result text; no score verdict. */
const resultHeadings: Partial<Record<SceneId, Record<string, string>>> = {
  inventory: {
    entrance: "Лишний крюк до отгрузки",
    alphabet: "Подарок в середине алфавита, груз — в начале",
    keeper: "Место знал один кладовщик",
    wms: "Система выбрала место у отгрузки",
  },
  crane: {
    remote: "Кран из офиса, без подъёма",
    rush: "Подъём в кабину — много сил",
    wait: "Баржа ушла без подарка",
    petr: "Пётр выручил, свой груз отложил",
  },
  lastmile: lastmileHeadings,
};
/** Scene 1 result headings (R19, call 05.11): what happened to the parcel, no verdict. */
export const carrierHeadings: Record<string, string> = {
  old: "Сервис — подарок на неделю позже",
  old4: "Сервис — подарок на неделю позже",
  near: "Рядом, но на три дня позже",
  crew: "За рулём двое — на три дня раньше",
  express: "Платформа выбрала — на неделю раньше",
};
// The truck outcome depends on the parcel.
const compactHeadings: Record<ParcelId, Record<string, string>> = {
  socks: {
    "place-1": "Коробка развалилась, носки разлетелись",
    "place-2": "Носки под крышей — больше ничего не влезет",
    "place-3": "Носки в нише, место осталось",
    "place-4": "Носки заняли место трёх ящиков",
    auto: "Система Compact выбрала место 3",
  },
  camera: {
    "place-1": "Фотоаппарат разбил посуду",
    "place-2": "Место над фотоаппаратом пустует",
    "place-3": "Фотоаппарат в нише — до него тянуться",
    "place-4": "К фотоаппарату долго пробирались",
    auto: "Система Compact выбрала место 3",
  },
  boat: {
    "place-1": "Перегруз сломал фуру",
    "place-2": "Лодка разбила посуду",
    "place-3": "Лодка не поместилась в нишу",
    "place-4": "Лодку закрепили стоя",
    auto: "Система Compact выбрала место 4",
  },
};
export const resultHeading = (scene: SceneId, id: string, parcel: ParcelId = "socks") =>
  (scene === "compact" ? compactHeadings[parcel] : resultHeadings[scene])?.[id];
