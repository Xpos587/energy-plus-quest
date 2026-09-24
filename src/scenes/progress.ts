import type { Scores } from "../game/types";
import type { SceneContext, SceneDefinition } from "./types";

export type Progress = {
  sceneIndex: number;
  phase: "choice" | "result";
  answers: Record<string, string>;
  finished: boolean;
};
export type ProgressAction =
  | { type: "CHOOSE"; id: string }
  | { type: "NEXT" | "BACK" | "RESET" };
export const initialProgress: Progress = {
  sceneIndex: 0,
  phase: "choice",
  answers: {},
  finished: false,
};

export function progressReducer(
  state: Progress,
  action: ProgressAction,
  scenes: SceneDefinition[],
  context: SceneContext,
): Progress {
  if (action.type === "RESET") return initialProgress;
  if (state.finished) return state;
  const scene = scenes[state.sceneIndex];
  switch (action.type) {
    case "CHOOSE":
      if (
        state.phase !== "choice" ||
        !scene.options(context).some((option) => option.id === action.id)
      )
        return state;
      return {
        ...state,
        phase: "result",
        answers: { ...state.answers, [scene.id]: action.id },
      };
    case "NEXT":
      if (state.phase !== "result") return state;
      return state.sceneIndex === scenes.length - 1
        ? { ...state, finished: true }
        : { ...state, sceneIndex: state.sceneIndex + 1, phase: "choice" };
    case "BACK": {
      if (state.phase === "choice") {
        return state.sceneIndex === 0 ||
          !state.answers[scenes[state.sceneIndex - 1].id]
          ? state
          : { ...state, sceneIndex: state.sceneIndex - 1, phase: "result" };
      }
      // Revising a choice invalidates it and all downstream answers, not just the displayed total.
      const answers = Object.fromEntries(
        scenes
          .slice(0, state.sceneIndex)
          .filter(({ id }) => state.answers[id] !== undefined)
          .map(({ id }) => [id, state.answers[id]]),
      );
      return { ...state, answers, phase: "choice" };
    }
  }
}

export function totalScores(
  state: Progress,
  scenes: SceneDefinition[],
  context: SceneContext,
  initial: Scores = { energy: 0, empathy: 0, efficiency: 0 },
): Scores {
  return scenes.reduce(
    (total, scene) => {
      const answer = scene
        .options(context)
        .find(({ id }) => id === state.answers[scene.id]);
      if (!answer) return total;
      return {
        energy: total.energy + answer.score.energy,
        empathy: total.empathy + answer.score.empathy,
        efficiency: total.efficiency + answer.score.efficiency,
      };
    },
    { ...initial },
  );
}
