import { craneWorld } from "./layers";

/** What happens on the quay right after a way is confirmed, as world positions over time. */
export type CraneBeat = {
  /** Index of the near crane's slewing top frame (0 = over the gift, last = rest over the barge). */
  frame: number;
  /** Hook block attach point in world metres; undefined while the hook is not drawn. */
  hook?: readonly [number, number, number];
  /** The gift box hangs under the hook. */
  lifted: boolean;
  /** The gift sits on the barge deck. */
  onDeck: boolean;
  /** Barge travel along its course, 0..1. */
  sail: number;
  /** A story actor working right now (pulses). */
  busy?: "ladder" | "ivan" | "far";
  /** Ivan behind the ПРУ window; undefined = at the console as drawn. */
  office?: "joy" | "wave" | "cheer" | "empty";
  /** Petr's far crane cab; undefined = Petr at his controls. */
  cab?: "sad" | "empty";
  /** Who sits in the near crane cab. */
  operator?: "ivan" | "petr";
  /** A figure on the quay: sprite name and feet position in world metres. */
  walker?: { pose: string; at: readonly [number, number, number]; flip?: boolean };
  /** A small reaction drawn over a character. */
  emote?: { kind: "tired" | "question" | "sad"; at: "office" | "near" | "far" };
  /** Remote-control signal from the office to the near crane. */
  signal?: boolean;
  /** Petr's own crates wait for later. */
  later?: boolean;
};

const last = craneWorld.slews.length - 1;
const [gx, gy] = craneWorld.gift;
const high = craneWorld.hookAttach + 7; // hook carried well above the quay
const deckDelta = [craneWorld.deck[0] - gx, craneWorld.deck[1] - gy, craneWorld.deck[2] - craneWorld.gift[2]] as const;
const deckAttach = craneWorld.hookAttach + deckDelta[2];
/** Where the barge goes when it casts off (world metres): downstream, bow first, away from the quay. */
export const craneSail = [-26, -9, 0] as const;
export { deckDelta as craneDeckDelta };

const ease = (t: number) => (t < 0.5 ? 2 * t * t : 1 - (-2 * t + 2) ** 2 / 2);
const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

type Step = { ms: number; at: (t: number) => Partial<CraneBeat> };
const tipAt = (frame: number) => craneWorld.tips[frame];
const hookUnder = (frame: number, z: number) => [tipAt(frame)[0], tipAt(frame)[1], z] as const;

// Quay spots in world metres (feet on the quay, z up).
const door = [-9.8, 14.6, 0] as const; // ПРУ entrance
const ladderFoot = [7.34, 3.87, 0] as const;
const ladderTop = [7.34, 3.87, 10.9] as const;
const farFoot = [41.3, 3.05, 0] as const; // front leg of Petr's crane
const along = (a: readonly number[], b: readonly number[], t: number) => [lerp(a[0], b[0], t), lerp(a[1], b[1], t), lerp(a[2], b[2], t)] as const;
/** Two-frame gait: the frame flips every `beat` ms of a step lasting `ms`. */
const gait = (names: readonly [string, string], t: number, ms: number, beat = 140) => names[Math.floor((t * ms) / beat) % 2];

function walk(ms: number, pose: readonly [string, string], from: readonly number[], to: readonly number[], keep: Partial<CraneBeat> = {}, flip = false): Step {
  return { ms, at: (t) => ({ ...keep, walker: { pose: gait(pose, t, ms), at: along(from, to, t), flip } }) };
}

/** The common loading run; `keep` holds for the whole run, `end` joins it once the gift is released. */
function load(prelude: Step[], busy: CraneBeat["busy"], keep: Partial<CraneBeat> = {}, end: Partial<CraneBeat> = {}): Step[] {
  const steps: Step[] = [
    // the boom swings from the barge to the gift
    { ms: 700, at: (t) => { const f = Math.round(lerp(last, 0, ease(t))); return { frame: f, hook: hookUnder(f, high), busy }; } },
    // hook down to the slings, then up with the gift
    { ms: 320, at: (t) => ({ frame: 0, hook: [gx, gy, lerp(high, craneWorld.hookAttach, ease(t))], busy }) },
    { ms: 380, at: (t) => ({ frame: 0, hook: [gx, gy, lerp(craneWorld.hookAttach, high, ease(t))], lifted: true, busy }) },
    // swing back over the free spot on the deck
    { ms: 760, at: (t) => { const f = Math.round(lerp(0, last, ease(t))); return { frame: f, hook: hookUnder(f, high), lifted: true, busy }; } },
    { ms: 360, at: (t) => ({ frame: last, hook: hookUnder(last, lerp(high, deckAttach, ease(t))), lifted: true, busy }) },
    // release: the hook rises, the gift stays aboard
    { ms: 260, at: (t) => ({ frame: last, hook: hookUnder(last, lerp(deckAttach, high, ease(t))), onDeck: true }) },
    { ms: 1600, at: (t) => ({ frame: last, hook: hookUnder(last, high), onDeck: true, sail: t * t }) },
  ];
  const n = steps.length;
  return [...prelude, ...steps.map((step, i) => ({ ms: step.ms, at: (t: number) => ({ ...keep, ...(i >= n - 2 ? end : {}), ...step.at(t) }) }))];
}

const rest = () => ({ frame: last, hook: hookUnder(last, high) });

const timelines: Record<string, Step[]> = {
  // Ivan takes the joystick; the signal runs to the empty cab; he waves the barge off.
  remote: load(
    [{ ms: 600, at: () => ({ ...rest(), office: "joy", signal: true }) }],
    "ivan", { office: "joy", signal: true }, { office: "wave", signal: false },
  ),
  // Ivan runs out of the office, climbs the tall ladder, loads, and is out of breath.
  rush: load(
    [
      { ms: 250, at: () => ({ ...rest(), office: "empty", walker: { pose: "ivan-run1", at: door } }) },
      walk(1300, ["ivan-run1", "ivan-run2"], door, ladderFoot, { ...rest(), office: "empty" }),
      walk(1100, ["ivan-climb1", "ivan-climb2"], ladderFoot, ladderTop, { ...rest(), office: "empty", busy: "ladder" }),
    ],
    "ladder", { office: "empty", operator: "ivan" }, { emote: { kind: "tired", at: "near" } },
  ),
  // Petr leaves his own crates, walks over, climbs, loads; he is sad, Ivan cheers.
  petr: load(
    [
      { ms: 500, at: () => ({ ...rest(), busy: "far" }) },
      { ms: 250, at: () => ({ ...rest(), cab: "empty", later: true, walker: { pose: "petr-walk1", at: farFoot, flip: true } }) },
      walk(1700, ["petr-walk1", "petr-walk2"], farFoot, ladderFoot, { ...rest(), cab: "empty", later: true }, true),
      walk(1000, ["petr-climb", "petr-climb"], ladderFoot, ladderTop, { ...rest(), cab: "empty", later: true }),
    ],
    "far", { cab: "empty", operator: "petr", later: true }, { office: "cheer", emote: { kind: "sad", at: "near" } },
  ),
};

export const craneRest: CraneBeat = { frame: last, hook: hookUnder(last, high), lifted: false, onDeck: false, sail: 0 };

export function craneDuration(id: string) {
  return (timelines[id] ?? []).reduce((sum, step) => sum + step.ms, 0);
}

/** Quay state `ms` after confirming way `id`. */
export function craneBeat(id: string, ms: number): CraneBeat {
  let start = 0;
  const steps = timelines[id] ?? [];
  for (const step of steps) {
    if (ms < start + step.ms) return { ...craneRest, ...step.at((ms - start) / step.ms) };
    start += step.ms;
  }
  const end = steps.at(-1);
  return end ? { ...craneRest, ...end.at(1) } : craneRest;
}
