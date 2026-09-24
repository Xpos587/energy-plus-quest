import type { ComponentType } from "react";
import type { ParcelId, ProfileId, RecipientId, Scores } from "../game/types";

export type SceneId = "compact" | "inventory" | "crane" | "lastmile";
export type SceneContext = {
  parcel: ParcelId;
  recipient: RecipientId;
  profile: ProfileId;
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
