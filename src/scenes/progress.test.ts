import { describe, expect, it } from "vitest";
import { initialProgress, progressReducer, totalScores } from "./progress";
import type { SceneContext, SceneDefinition } from "./types";

const context: SceneContext = {
  parcel: "boat",
  recipient: "alva",
  profile: "student",
};
const scenes = ["compact", "inventory", "crane", "lastmile"].map(
  (id, index) => ({
    id,
    number: index + 2,
    title: id,
    product: id,
    intro: () => [],
    Art: () => null,
    options: () => [
      {
        id: "a",
        label: "a",
        result: [],
        sourceIds: [],
        score: { energy: -4, empathy: 3, efficiency: 5 },
      },
      {
        id: "b",
        label: "b",
        result: [],
        sourceIds: [],
        score: { energy: 1, empathy: -2, efficiency: -3 },
      },
    ],
  }),
) as SceneDefinition[];
const reduce = (
  state: typeof initialProgress,
  action: Parameters<typeof progressReducer>[1],
) => progressReducer(state, action, scenes, context);

describe("remaining scene progression", () => {
  it("requires a valid choice and counts it once, including negative scores", () => {
    expect(reduce(initialProgress, { type: "NEXT" })).toEqual(initialProgress);
    expect(reduce(initialProgress, { type: "CHOOSE", id: "invalid" })).toEqual(
      initialProgress,
    );
    const chosen = reduce(initialProgress, { type: "CHOOSE", id: "a" });
    expect(chosen.phase).toBe("result");
    expect(reduce(chosen, { type: "CHOOSE", id: "b" })).toEqual(chosen);
    expect(
      totalScores(chosen, scenes, context, {
        energy: 2,
        empathy: 2,
        efficiency: 2,
      }),
    ).toEqual({ energy: -2, empathy: 5, efficiency: 7 });
  });
  it("allows a revised answer without farming scores or retaining future choices", () => {
    let state = reduce(initialProgress, { type: "CHOOSE", id: "a" });
    state = reduce(state, { type: "NEXT" });
    expect(state.sceneIndex).toBe(1);
    state = reduce(state, { type: "CHOOSE", id: "b" });
    state = reduce(state, { type: "BACK" });
    expect(state.answers).toEqual({ compact: "a" });
    state = reduce(state, { type: "BACK" });
    expect(state.sceneIndex).toBe(0);
    expect(state.phase).toBe("result");
    state = reduce(state, { type: "BACK" });
    state = reduce(state, { type: "CHOOSE", id: "b" });
    expect(totalScores(state, scenes, context)).toEqual({
      energy: 1,
      empathy: -2,
      efficiency: -3,
    });
  });
  it("does not fabricate earlier answers when revising a direct-entry scene", () => {
    for (const sceneIndex of [1, 2, 3]) {
      let state = { ...initialProgress, sceneIndex };
      state = reduce(state, { type: "CHOOSE", id: "a" });
      state = reduce(state, { type: "BACK" });
      expect(state.answers).toStrictEqual({});
      expect(reduce(state, { type: "BACK" })).toEqual(state);
      expect(reduce(state, { type: "CHOOSE", id: "b" }).phase).toBe("result");
    }
  });
  it("ends after scene 5, preserves its outcome and rejects repeated completion", () => {
    let state = initialProgress;
    for (const _scene of scenes) {
      state = reduce(state, { type: "CHOOSE", id: "a" });
      state = reduce(state, { type: "NEXT" });
    }
    expect(state.finished).toBe(true);
    expect(state.sceneIndex).toBe(3);
    expect(state.phase).toBe("result");
    expect(totalScores(state, scenes, context)).toEqual({
      energy: -16,
      empathy: 12,
      efficiency: 20,
    });
    expect(reduce(state, { type: "NEXT" })).toEqual(state);
    expect(reduce(state, { type: "RESET" })).toEqual(initialProgress);
  });
});
