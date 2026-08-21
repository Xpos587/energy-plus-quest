import { describe, expect, it } from "vitest";
import { gameReducer, initialGameState } from "./gameReducer";

describe("gameReducer", () => {
  it("moves directly from parcel selection to the carrier map", () => {
    const state = gameReducer(
      {
        ...initialGameState,
        step: "parcel",
        profile: "student",
        recipient: "alva",
      },
      { type: "CHOOSE_PARCEL", value: "camera" },
    );

    expect(state).toMatchObject({
      step: "carrier",
      profile: "student",
      recipient: "alva",
      parcel: "camera",
    });
  });

  it("returns from an outcome to the carrier map and clears its score", () => {
    const outcome = gameReducer(
      {
        ...initialGameState,
        step: "carrier",
        profile: "professional",
        recipient: "arseniy",
        parcel: "boat",
      },
      { type: "CHOOSE_CARRIER", value: "crew" },
    );

    expect(gameReducer(outcome, { type: "BACK" })).toEqual({
      step: "carrier",
      profile: "professional",
      recipient: "arseniy",
      parcel: "boat",
      scores: { energy: 0, empathy: 0, efficiency: 0 },
    });
  });

  it("walks backward through the personalization choices", () => {
    expect(
      gameReducer(
        { ...initialGameState, step: "recipient", profile: "student" },
        { type: "BACK" },
      ).step,
    ).toBe("profile");
    expect(
      gameReducer(
        {
          ...initialGameState,
          step: "parcel",
          profile: "student",
          recipient: "alva",
        },
        { type: "BACK" },
      ).step,
    ).toBe("recipient");
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
