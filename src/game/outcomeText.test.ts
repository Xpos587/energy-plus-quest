import { describe, expect, it } from "vitest";
import { carriers, parcels } from "./content";
import { interpolateOutcome } from "./outcomeText";

describe("outcome copy", () => {
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
