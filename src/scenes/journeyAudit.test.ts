import { expect, it } from "vitest";
import { remainingScenes } from "./ScenesGame";
import { initialProgress, progressReducer, totalScores } from "./progress";
import type { SceneContext } from "./types";

it("every context and option can be revised, completed and traversed backwards without score farming", () => {
  for (const profile of ["student", "professional"] as const)
    for (const recipient of ["alva", "khor", "arseniy"] as const)
      for (const parcel of ["camera", "socks", "boat"] as const) {
        const context: SceneContext = { profile, recipient, parcel };
        const reduce = (state: typeof initialProgress, action: Parameters<typeof progressReducer>[1]) =>
          progressReducer(state, action, remainingScenes, context);
        let state = initialProgress;
        for (const scene of remainingScenes) {
          const before = totalScores(state, remainingScenes, context);
          expect(scene.intro(context).length).toBeGreaterThan(0);
          for (const option of scene.options(context)) {
            expect(option.result.join("").trim().length).toBeGreaterThan(0);
            const selected = reduce(state, { type: "CHOOSE", id: option.id });
            expect(selected.phase).toBe("result");
            expect(totalScores(selected, remainingScenes, context)).toEqual({
              energy: before.energy + option.score.energy,
              empathy: before.empathy + option.score.empathy,
              efficiency: before.efficiency + option.score.efficiency,
            });
            expect(reduce(selected, { type: "CHOOSE", id: option.id })).toEqual(selected);
            expect(reduce(selected, { type: "BACK" })).toEqual(state);
          }
          state = reduce(state, { type: "CHOOSE", id: scene.options(context)[0].id });
          state = reduce(state, { type: "NEXT" });
        }
        expect(state.finished).toBe(true);
        expect(reduce(state, { type: "NEXT" })).toEqual(state);
        for (let index = remainingScenes.length - 1; index >= 0; index--) {
          state = reduce(state, { type: "BACK" });
          expect(state.finished).toBe(false);
          expect(state.phase).toBe("choice");
          expect(state.answers[remainingScenes[index].id]).toBeUndefined();
          if (index > 0) {
            state = reduce(state, { type: "BACK" });
            expect(state.sceneIndex).toBe(index - 1);
            expect(state.phase).toBe("result");
          }
        }
        expect(state).toEqual(initialProgress);
        expect(totalScores(state, remainingScenes, context)).toEqual({ energy: 0, empathy: 0, efficiency: 0 });
      }
});
