import {
  createContext,
  type Dispatch,
  type PropsWithChildren,
  useContext,
  useReducer,
} from "react";
import { gameReducer, initialGameState } from "./gameReducer";
import type { GameAction, GameState } from "./types";

type GameContextValue = {
  state: GameState;
  dispatch: Dispatch<GameAction>;
};

const GameContext = createContext<GameContextValue | undefined>(undefined);

export function GameProvider({ children }: PropsWithChildren) {
  const [state, dispatch] = useReducer(gameReducer, initialGameState);

  return (
    <GameContext.Provider value={{ state, dispatch }}>
      {children}
    </GameContext.Provider>
  );
}

export function useGame() {
  const context = useContext(GameContext);

  if (!context) {
    throw new Error("useGame must be used inside GameProvider");
  }

  return context;
}
