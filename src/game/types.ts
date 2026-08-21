export type GameStep =
  | "intro"
  | "profile"
  | "recipient"
  | "parcel"
  | "carrier"
  | "outcome";

export type ProfileId = "student" | "professional";
export type RecipientId = "alva" | "khor" | "arseniy";
export type ParcelId = "camera" | "socks" | "boat";
export type CarrierId = "old" | "near" | "crew" | "express";

export type Scores = {
  energy: number;
  empathy: number;
  efficiency: number;
};

export type GameState = {
  step: GameStep;
  profile?: ProfileId;
  recipient?: RecipientId;
  parcel?: ParcelId;
  carrier?: CarrierId;
  scores: Scores;
};

export type GameAction =
  | { type: "START" }
  | { type: "CHOOSE_PROFILE"; value: ProfileId }
  | { type: "CHOOSE_RECIPIENT"; value: RecipientId }
  | { type: "CHOOSE_PARCEL"; value: ParcelId }
  | { type: "CHOOSE_CARRIER"; value: CarrierId }
  | { type: "BACK" }
  | { type: "RESET" };

export type ChoiceItem<T extends string> = {
  id: T;
  title: string;
  eyebrow: string;
  description?: string;
  symbol: string;
};

export type ParcelChoice = ChoiceItem<ParcelId> & {
  accusativeTitle: string;
};

export type CarrierChoice = ChoiceItem<CarrierId> & {
  mapLabel: string;
  score: Scores;
  resultTitle: string;
  resultBody: string;
  delivery: string;
  condition: string;
  crew: string;
  cost: string;
};
