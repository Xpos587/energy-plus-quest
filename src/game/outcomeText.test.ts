import { describe, expect, it } from "vitest";
import { carriers, parcels, recipients } from "./content";
import { interpolateOutcome } from "./outcomeText";

describe("outcome copy", () => {
  it("uses the scenario consequence for all nine recipient/parcel combinations", () => {
    const near = carriers.find((carrier) => carrier.id === "near");
    expect(near?.resultBody).toBe(
      "Вы отлично сокращаете дистанцию! Ваш перевозчик был рядом со складом и сразу же завернул в ваш логистический центр. Но водитель оказался очень неторопливым: {recipient} получит {parcel} на три дня позже.",
    );
    for (const recipient of recipients) {
      for (const parcel of parcels) {
        const text = interpolateOutcome(
          near?.resultBody ?? "",
          recipient.title,
          parcel.accusativeTitle,
        );
        expect(text).toContain(
          `${recipient.title} получит ${parcel.accusativeTitle} на три дня позже.`,
        );
        expect(text).not.toMatch(/[{}]/);
      }
    }
  });
  it.each(parcels)("uses the accusative form for $title", (parcel) => {
    for (const carrier of carriers) {
      const result = interpolateOutcome(
        carrier.resultBody,
        "Вахтовик Арсений",
        parcel.accusativeTitle,
      );

      expect(result).toContain(
        `Вахтовик Арсений получит ${parcel.accusativeTitle}`,
      );
    }
  });

  it("declines лодка as лодку", () => {
    const result = interpolateOutcome(
      carriers[0].resultBody,
      "Вахтовик Арсений",
      parcels.find((parcel) => parcel.id === "boat")?.accusativeTitle,
    );

    expect(result).toContain("Вахтовик Арсений получит лодку");
    expect(result).not.toContain("получит лодка");
  });
});

it("preserves the scenario facts instead of a conditional delivery forecast", () => {
  const old = carriers.find((c) => c.id === "old")!;
  const near = carriers.find((c) => c.id === "near")!;
  const crew = carriers.find((c) => c.id === "crew")!;
  const express = carriers.find((c) => c.id === "express")!;
  expect(old.resultBody).toContain("задержали на посту");
  expect(near.resultBody).toContain("завернул в ваш логистический центр");
  expect(near.resultBody).not.toMatch(/Если|ждёт загрузки/);
  expect(crew.resultBody).toContain("посменной работе");
  expect(crew.resultBody).toContain("аренда оказалась очень дорогой");
  for (const fact of [
    "Платформа Express",
    "2 часа",
    "лучшим доступным перевозчиком",
    "высокие рейтинги",
    "новая фура",
    "два водителя",
    "выгодная цена",
    "без остановок",
    "в целости и сохранности",
    "на неделю раньше",
  ])
    expect(express.resultBody).toContain(fact);
});
