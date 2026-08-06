import { describe, expect, it } from "vitest";
import { gameReducer, initialGameState } from "./gameReducer";

describe("gameReducer", () => {
  it("walks through onboarding and keeps the selected cargo context", () => {
    const started = gameReducer(initialGameState, { type: "START" });
    const withProfile = gameReducer(started, {
      type: "CHOOSE_PROFILE",
      value: "student",
    });
    const withRecipient = gameReducer(withProfile, {
      type: "CHOOSE_RECIPIENT",
      value: "alva",
    });
    const withParcel = gameReducer(withRecipient, {
      type: "CHOOSE_PARCEL",
      value: "camera",
    });

    expect(withParcel).toMatchObject({
      step: "briefing",
      profile: "student",
      recipient: "alva",
      parcel: "camera",
    });
  });

  it("applies the chosen carrier score and opens the consequence", () => {
    const outcome = gameReducer(initialGameState, {
      type: "CHOOSE_CARRIER",
      value: "crew",
    });

    expect(outcome.step).toBe("outcome");
    expect(outcome.carrier).toBe("crew");
    expect(outcome.scores).toEqual({
      energy: -3,
      empathy: 3,
      efficiency: 4,
    });
  });

  it("gives Express the values from the first-scene draft", () => {
    const outcome = gameReducer(initialGameState, {
      type: "CHOOSE_CARRIER",
      value: "express",
    });

    expect(outcome.scores).toEqual({
      energy: -1,
      empathy: 5,
      efficiency: 5,
    });
  });

  it("resets the entire route", () => {
    const changed = gameReducer(initialGameState, {
      type: "CHOOSE_CARRIER",
      value: "near",
    });

    expect(gameReducer(changed, { type: "RESET" })).toEqual(initialGameState);
  });
});
