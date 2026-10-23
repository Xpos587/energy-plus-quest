import { writeFileSync } from "node:fs";
import { expect, it } from "vitest";
import { findCarrier } from "../game/content";
import { logistType } from "./endingCopy";
import { totalScores } from "./progress";
import { remainingScenes } from "./ScenesGame";

it("reaches all seven certificate variants using actual authored routes", () => {
  const fixtures = [];
  for (const profile of ["student", "professional"] as const) {
    const context = { profile, recipient: "alva", parcel: "socks" } as const;
    const found = new Set<string>();
    for (const carrier of ["old", "old4", "near", "crew", "express"] as const) {
      for (const compact of remainingScenes[0].options(context))
        for (const inventory of remainingScenes[1].options(context))
          for (const crane of remainingScenes[2].options(context))
            for (const lastmile of remainingScenes[3].options(context)) {
              const progress = {
                sceneIndex: 3,
                phase: "result" as const,
                finished: true,
                answers: {
                  compact: compact.id,
                  inventory: inventory.id,
                  crane: crane.id,
                  lastmile: lastmile.id,
                },
              };
              const scores = totalScores(
                progress,
                remainingScenes,
                context,
                findCarrier(carrier)!.score,
              );
              const type = logistType(profile, scores);
              if (found.has(type)) continue;
              found.add(type);
              fixtures.push({ profile, type, carrier, progress });
            }
    }
    expect([...found].sort()).toEqual(
      profile === "student"
        ? ["efficiency", "empathy", "energy", "future"]
        : ["efficiency", "empathy", "energy"],
    );
  }
  if (process.env.CERTIFICATE_FIXTURES)
    writeFileSync(
      process.env.CERTIFICATE_FIXTURES,
      JSON.stringify(fixtures, null, 2),
    );
});
