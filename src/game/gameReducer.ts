import { findCarrier } from "./content";
import type { GameAction, GameState } from "./types";

const emptyScores = { energy: 0, empathy: 0, efficiency: 0 };

export const initialGameState: GameState = {
  step: "intro",
  scores: emptyScores,
};

function goBack(state: GameState): GameState {
  switch (state.step) {
    case "profile":
      return { ...state, step: "intro" };
    case "recipient":
      return { ...state, step: "profile", recipient: undefined };
    case "parcel":
      return { ...state, step: "recipient", parcel: undefined };
    case "carrier":
      return {
        ...state,
        step: "parcel",
        carrier: undefined,
        scores: emptyScores,
      };
    case "outcome":
      return {
        ...state,
        step: "carrier",
        carrier: undefined,
        scores: emptyScores,
      };
    case "intro":
      return state;
  }
}

export function gameReducer(state: GameState, action: GameAction): GameState {
  switch (action.type) {
    case "START":
      return { ...state, step: "profile" };
    case "CHOOSE_PROFILE":
      return { ...state, profile: action.value, step: "recipient" };
    case "CHOOSE_RECIPIENT":
      return { ...state, recipient: action.value, step: "parcel" };
    case "CHOOSE_PARCEL":
      return { ...state, parcel: action.value, step: "carrier" };
    case "CHOOSE_CARRIER": {
      const carrier = findCarrier(action.value);

      if (!carrier) {
        return state;
      }

      return {
        ...state,
        carrier: action.value,
        scores: carrier.score,
        step: "outcome",
      };
    }
    case "BACK":
      return goBack(state);
    case "RESET":
      return initialGameState;
  }
}
