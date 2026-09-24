import { describe, expect, it } from "vitest";
import {
  carrierBriefing,
  carrierQuestion,
  carriers,
  parcels,
  profiles,
  recipients,
} from "./content";
import { interpolateOutcome } from "./outcomeText";
import { sourceCopy } from "./sourceCopyBaseline";

describe("full September scenario copy and approved onboarding labels", () => {
  it("preserves the original briefing and inflects the delivery placeholder", () => {
    expect(carrierBriefing).toBe(sourceCopy.carrierBriefing);
    expect(carrierQuestion).toBe(sourceCopy.carrierPrompt);
    for (const [gift, expected] of [
      ["фотоаппарат", "фотоаппарата"],
      ["вязаные носки", "вязаных носков"],
      ["лодку", "лодки"],
    ])
      expect(
        interpolateOutcome("с доставкой {parcelGenitive}", "Альва", gift),
      ).toBe(`с доставкой ${expected}`);
  });
  it("keeps short recipient names and approved choice labels", () => {
    expect(profiles.map(({ title }) => title)).toEqual(sourceCopy.profiles);
    expect(recipients.map(({ title }) => title)).toEqual([
      "Альва",
      "Хор",
      "Арсений",
    ]);
    expect(parcels.map(({ title }) => title)).toEqual(sourceCopy.parcels);
  });

  it("preserves restored titles, bodies and all 45 personalized outcomes", () => {
    expect(carriers).toHaveLength(5);
    let combinations = 0;
    for (const carrier of carriers) {
      const expected =
        sourceCopy.outcomes[carrier.id === "old4" ? "old" : carrier.id];
      expect(carrier.resultTitle).toBe(expected.heading);
      expect(carrier.resultBody).toBe(expected.body);
      for (const recipient of recipients) {
        for (const parcel of parcels) {
          const result = interpolateOutcome(
            carrier.resultBody,
            recipient.title,
            parcel.accusativeTitle,
          );
          expect(result).toBe(
            expected.body
              .replaceAll("{recipient}", recipient.title)
              .replaceAll("{parcel}", parcel.accusativeTitle)
              .replaceAll("{parcelGenitive}", parcel.genitiveTitle),
          );
          expect(result).not.toMatch(/[{}]|undefined/);
          combinations += 1;
        }
      }
    }
    expect(combinations).toBe(45);
  });

  it("keeps safe fallback text", () => {
    expect(interpolateOutcome("{recipient} получит {parcel}")).toBe(
      "получатель получит подарок",
    );
  });
});
