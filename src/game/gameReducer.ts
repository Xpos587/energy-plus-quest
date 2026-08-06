import { findCarrier } from "./content";
import type { GameAction, GameState } from "./types";

export const initialGameState: GameState = {
  step: "intro",
  scores: { energy: 0, empathy: 0, efficiency: 0 },
};

export function gameReducer(state: GameState, action: GameAction): GameState {
  switch (action.type) {
    case "START":
      return { ...state, step: "profile" };
    case "CHOOSE_PROFILE":
      return { ...state, profile: action.value, step: "recipient" };
    case "CHOOSE_RECIPIENT":
      return { ...state, recipient: action.value, step: "parcel" };
    case "CHOOSE_PARCEL":
      return { ...state, parcel: action.value, step: "briefing" };
    case "OPEN_CARRIER_MAP":
      return { ...state, step: "carrier" };
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
    case "SHOW_EXPRESS":
      return { ...state, step: "express" };
    case "COMPLETE_SCENE":
      return { ...state, step: "complete" };
    case "RESET":
      return initialGameState;
  }
}
