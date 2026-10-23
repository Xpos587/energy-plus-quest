import {
  createContext,
  type Dispatch,
  type PropsWithChildren,
  useContext,
  useReducer,
  useEffect,
  useRef,
} from "react";
import { gameReducer, initialGameState } from "./gameReducer";
import {
  SAVE_KEY,
  clearSaveScope,
  newSaveScope,
  readStored,
  restoreGame,
  writeStored,
} from "./persistence";
import type { GameAction, GameState } from "./types";

type GameContextValue = {
  state: GameState;
  dispatch: Dispatch<GameAction>;
};

const SaveScopeContext = createContext<string | undefined>(undefined);
export function useOptionalSaveScope() {
  return useContext(SaveScopeContext);
}

const GameContext = createContext<GameContextValue | undefined>(undefined);

export function GameProvider({
  children,
  persist = false,
}: PropsWithChildren<{ persist?: boolean }>) {
  const [saved, send] = useReducer(
    (
      current: { state: GameState; scope: string },
      envelope: { action: GameAction; nextScope: string },
    ) => {
      const { action, nextScope } = envelope;
      const state = gameReducer(current.state, action);
      const scope =
        action.type === "RESET" ||
        (state !== current.state && action.type.startsWith("CHOOSE_"))
          ? nextScope
          : current.scope;
      return { state, scope };
    },
    undefined,
    () =>
      (persist ? restoreGame(readStored(SAVE_KEY)) : undefined) ?? {
        state: initialGameState,
        scope: newSaveScope(),
      },
  );
  const previousScope = useRef(saved.scope);
  const dispatch: Dispatch<GameAction> = (action) =>
    send({ action, nextScope: newSaveScope() });
  useEffect(() => {
    if (persist) {
      writeStored(SAVE_KEY, { version: 1, ...saved });
      if (previousScope.current !== saved.scope)
        clearSaveScope(previousScope.current);
    }
    previousScope.current = saved.scope;
  }, [persist, saved]);
  return (
    <SaveScopeContext.Provider value={persist ? saved.scope : undefined}>
      <GameContext.Provider value={{ state: saved.state, dispatch }}>
        {children}
      </GameContext.Provider>
    </SaveScopeContext.Provider>
  );
}

export function useGame() {
  const context = useContext(GameContext);

  if (!context) {
    throw new Error("useGame must be used inside GameProvider");
  }

  return context;
}
