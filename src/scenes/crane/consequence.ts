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

function load(prelude: Step[], busy: CraneBeat["busy"]): Step[] {
  return [
    ...prelude,
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
    { ms: 1150, at: (t) => ({ frame: last, hook: hookUnder(last, high), onDeck: true, sail: t * t }) },
  ];
}

const timelines: Record<string, Step[]> = {
  remote: load([], "ivan"),
  petr: load([], "far"),
  // Ivan first climbs the tall ladder to the cabin.
  rush: load([{ ms: 650, at: () => ({ frame: last, hook: hookUnder(last, high), busy: "ladder" }) }], "ladder"),
  // Nobody is at the crane: the barge leaves on time, the gift stays on the quay.
  wait: [
    { ms: 350, at: () => ({ frame: last, hook: hookUnder(last, high) }) },
    { ms: 1500, at: (t) => ({ frame: last, hook: hookUnder(last, high), sail: t * t }) },
  ],
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
