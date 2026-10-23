import { existsSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { sceneChoiceImage, sceneOutcomeImage } from "./artwork";

const deliveries = [
  [
    "boat",
    "alva",
    "revision-2/rover-boat-alva.webp",
    "robot-boat-result-v3.webp",
    "pipecarrier-return-swim-v5.webp",
    "helicopter-ground-boat-final-v5.webp",
  ],
  [
    "boat",
    "khor",
    "revision-2/rover-boat-khor.webp",
    "robot-boat-result-v3.webp",
    "pipecarrier-return-swim-v5.webp",
    "helicopter-ground-khor-boat-v6.webp",
  ],
  [
    "boat",
    "arseniy",
    "revision-2/rover-boat-arseniy.webp",
    "robot-boat-result-v3.webp",
    "pipecarrier-return-swim-v5.webp",
    "revision-2/flight-boat-arseniy.webp",
  ],
  [
    "camera",
    "alva",
    "revision-2/rover-parcel-alva.webp",
    "robot-parcel-result-v1.webp",
    "pipecarrier-return-swim-v5.webp",
    "helicopter-ground-alva-parcel-v6.webp",
  ],
  [
    "camera",
    "khor",
    "revision-2/rover-parcel-khor.webp",
    "robot-parcel-result-v1.webp",
    "pipecarrier-return-swim-v5.webp",
    "helicopter-ground-khor-parcel-v6.webp",
  ],
  [
    "camera",
    "arseniy",
    "revision-2/rover-parcel-arseniy.webp",
    "robot-parcel-result-v1.webp",
    "pipecarrier-return-swim-v5.webp",
    "revision-2/flight-parcel-arseniy.webp",
  ],
  [
    "socks",
    "alva",
    "revision-2/rover-parcel-alva.webp",
    "robot-parcel-result-v1.webp",
    "pipecarrier-return-swim-v5.webp",
    "helicopter-ground-alva-parcel-v6.webp",
  ],
  [
    "socks",
    "khor",
    "revision-2/rover-parcel-khor.webp",
    "robot-parcel-result-v1.webp",
    "pipecarrier-return-swim-v5.webp",
    "helicopter-ground-khor-parcel-v6.webp",
  ],
  [
    "socks",
    "arseniy",
    "revision-2/rover-parcel-arseniy.webp",
    "robot-parcel-result-v1.webp",
    "pipecarrier-return-swim-v5.webp",
    "revision-2/flight-parcel-arseniy.webp",
  ],
] as const;

describe("current artwork for every delivery context", () => {
  for (const [parcel, recipient, ...results] of deliveries) {
    const context = { parcel, recipient, profile: "student" } as const;
    it(`${recipient}/${parcel}: matching lastmile choice and all consequences`, () => {
      const choice = "choice-final-wide-v10.webp";
      expect(sceneChoiceImage("lastmile", context)).toBe(
        `/scene-art/lastmile-family-v1/${choice}`,
      );
      for (const [index, option] of [
        "rover",
        "robot",
        "pipe-carrier",
        "helicopter",
      ].entries()) {
        const file = option === "pipe-carrier" ? `revision-2/pipe-carrier-${recipient}.webp` : results[index];
        const path = `/scene-art/lastmile-family-v1/${file}`;
        expect(sceneOutcomeImage("lastmile", option, context)).toBe(path);
        expect(existsSync(`public${path}`), path).toBe(true);
      }
      expect(existsSync(`public/scene-art/lastmile-family-v1/${choice}`)).toBe(
        true,
      );
    });
    it(`${recipient}/${parcel}: matching warehouse family and crane choice`, () => {
      expect(sceneChoiceImage("crane", context)).toBe(
        "/scene-art/barge-family-v1/choice-neutral-wide-v7.webp",
      );
      for (const option of ["entrance", "keeper", "wms", "alphabet"]) {
        const path = option === "keeper" || option === "entrance"
          ? `/scene-art/warehouse-corrections-2026-10-20/outcomes/${option === "keeper" ? "keeper-v2" : "entrance"}-labels-v1.png`
          : option === "wms"
            ? "/scene-art/warehouse-revision-3-2026-10-18/wms-stylized-v3.png"
            : `/scene-art/warehouse-polish-2026-10-17/${option}.webp`;
        expect(sceneOutcomeImage("inventory", option, context)).toBe(path);
        expect(existsSync(`public${path}`), path).toBe(true);
      }
    });
  }
});
