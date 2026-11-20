import { existsSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { sceneChoiceImage, sceneOutcomeImage } from "./artwork";

import { lastmileChoiceImage } from "./lastmile/artworkFamily";

const deliveries = [
  [
    "boat",
    "alva",
    "revision-22/rover-boat.webp",
    "revision-19/robot-boat.webp",
    "pipecarrier-return-swim-v5.webp",
    "revision-19/ground-boat.webp",
  ],
  [
    "boat",
    "khor",
    "revision-22/rover-boat.webp",
    "revision-19/robot-boat.webp",
    "pipecarrier-return-swim-v5.webp",
    "revision-19/ground-khor-boat.webp",
  ],
  [
    "boat",
    "arseniy",
    "revision-22/rover-boat.webp",
    "revision-19/robot-boat.webp",
    "pipecarrier-return-swim-v5.webp",
    "revision-18/flight-boat-arseniy-tall.webp",
  ],
  [
    "camera",
    "alva",
    "revision-19/rover-parcel.webp",
    "revision-19/robot-parcel.webp",
    "pipecarrier-return-swim-v5.webp",
    "revision-19/ground-alva-parcel.webp",
  ],
  [
    "camera",
    "khor",
    "revision-19/rover-parcel.webp",
    "revision-19/robot-parcel.webp",
    "pipecarrier-return-swim-v5.webp",
    "revision-19/ground-khor-parcel.webp",
  ],
  [
    "camera",
    "arseniy",
    "revision-19/rover-parcel.webp",
    "revision-19/robot-parcel.webp",
    "pipecarrier-return-swim-v5.webp",
    "revision-18/flight-parcel-arseniy-tall.webp",
  ],
  [
    "socks",
    "alva",
    "revision-19/rover-parcel.webp",
    "revision-19/robot-parcel.webp",
    "pipecarrier-return-swim-v5.webp",
    "revision-19/ground-alva-parcel.webp",
  ],
  [
    "socks",
    "khor",
    "revision-19/rover-parcel.webp",
    "revision-19/robot-parcel.webp",
    "pipecarrier-return-swim-v5.webp",
    "revision-19/ground-khor-parcel.webp",
  ],
  [
    "socks",
    "arseniy",
    "revision-19/rover-parcel.webp",
    "revision-19/robot-parcel.webp",
    "pipecarrier-return-swim-v5.webp",
    "revision-18/flight-parcel-arseniy-tall.webp",
  ],
] as const;

describe("current artwork for every delivery context", () => {
  for (const [parcel, recipient, ...results] of deliveries) {
    const context = { parcel, recipient, profile: "student" } as const;
    it(`${recipient}/${parcel}: matching lastmile choice and all consequences`, () => {
      for (const format of ["wide", "tall"] as const) {
        const choice = lastmileChoiceImage(format, recipient);
        expect(choice).toBe(`scene-art/lastmile-family-v1/revision-27/choice-${format}.webp`);
        expect(existsSync(`public/${choice}`)).toBe(true);
      }
      const choice = "revision-15/intro-wide.webp";
      expect(sceneChoiceImage("lastmile")).toBe(
        `/scene-art/lastmile-family-v1/${choice}`,
      );
      for (const [index, option] of [
        "rover",
        "robot",
        "pipe-carrier",
        "helicopter",
      ].entries()) {
        const file = option === "pipe-carrier" ? "revision-21/pipe-carrier-tall.webp" : results[index];
        const path = `/scene-art/lastmile-family-v1/${file}`;
        expect(sceneOutcomeImage("lastmile", option, context)).toBe(path);
        expect(existsSync(`public${path}`), path).toBe(true);
      }
      expect(existsSync(`public/scene-art/lastmile-family-v1/${choice}`)).toBe(
        true,
      );
    });
    it(`${recipient}/${parcel}: matching warehouse family and crane choice`, () => {
      expect(sceneChoiceImage("crane")).toBe(
        "/scene-art/barge-v7/wide/plate.webp",
      );
      for (const option of ["rush", "petr", "remote"]) {
        const path = `/scene-art/barge-v7/outcome-${option}.webp`;
        expect(sceneOutcomeImage("crane", option, context)).toBe(path);
        expect(existsSync(`public${path}`), path).toBe(true);
      }
      for (const option of ["entrance", "keeper", "wms", "alphabet"]) {
        const path = `/scene-art/warehouse-results-v4/outcome-${option === "alphabet" ? `alphabet-${context.parcel}` : option}.webp`;
        expect(sceneOutcomeImage("inventory", option, context)).toBe(path);
        expect(existsSync(`public${path}`), path).toBe(true);
      }
    });
  }
});
