import { describe, expect, it } from "vitest";
import { carriers, parcels, recipients } from "./content";
import { interpolateOutcome } from "./outcomeText";

describe("outcome copy", () => {
  it("forecasts near before loading for all nine recipient/parcel combinations", () => {
    const near = carriers.find((carrier) => carrier.id === "near");
    expect(near?.resultBody).toBe(
      "Перевозчик выбран; груз ещё ждёт загрузки. Машина рядом, но водитель едет неторопливо. Если темп сохранится, {recipient} получит {parcel} на три дня позже.",
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
