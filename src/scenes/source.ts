import { implementationText } from "./implementationText";

const paragraphs = new Map(Object.entries(implementationText));

// Existing implementation corrections; this module is not a scenario authority.
const proofreading: Record<string, [string, string]> = {
  p223: ["Машина сломалась и пришлось", "Машина сломалась, и пришлось"],
  p290: ["соседними грузами защитят", "соседними грузами и защитят"],
  p444: ["–не каждый день", "– не каждый день"],
  p469: [
    "Петр выручил вас вовремя погрузить подарок",
    "Петр выручил вас, вовремя погрузив подарок",
  ],
  p487: ["«Газпромнефть-снабжение.»", "«Газпромнефть-снабжение»"],
  p554: ["(имени персонажа)", "(имени персонажа)?"],
  p558: ["Результат: «Вертолет", "Результат: Вертолет"],
};

export function source(id: string): string {
  const text = paragraphs.get(id);
  if (text === undefined) throw new Error(`Missing scenario paragraph: ${id}`);
  const correction = proofreading[id];
  return correction ? text.replace(...correction) : text;
}
