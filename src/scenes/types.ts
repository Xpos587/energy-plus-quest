import type { ComponentType } from "react";
import type { CarrierId, ParcelId, ProfileId, RecipientId, Scores } from "../game/types";

export type SceneId = "compact" | "inventory" | "crane" | "lastmile";
export type SceneContext = {
  parcel: ParcelId;
  recipient: RecipientId;
  profile: ProfileId;
  carrier?: CarrierId;
};
export type SceneOption = {
  id: string;
  label: string;
  accessibleDescription?: string;
  result: string[];
  score: Scores;
  sourceIds: string[];
};
export type SceneArtProps = {
  context: SceneContext;
  selectedId?: string;
  onSelect?: (id: string) => void;
  showResult: boolean;
  initialPan?: number;
  onPanChange?: (position: number) => void;
  /** Lets the choice list and the artwork highlight the same option. */
  focusedId?: string;
  onFocusChange?: (id: string | undefined) => void;
  /** A confirmed choice whose consequence plays in the drawing before the result. */
  playing?: string;
  onPlayed?: () => void;
};
export type SceneDefinition = {
  id: SceneId;
  number: 2 | 3 | 4 | 5;
  title: string;
  product: string;
  intro: (context: SceneContext) => string[];
  options: (context: SceneContext) => SceneOption[];
  Art: ComponentType<SceneArtProps>;
};
