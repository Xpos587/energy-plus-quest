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
  /** A story actor working right now (pulses). */
  busy?: "ladder" | "ivan" | "far";
  /** Ivan by the ПРУ office; "empty" = he has walked off to the crane. */
  office?: "joy" | "wave" | "cheer" | "empty";
  /** Petr by his crates; "empty" = he has walked off to the crane. */
  cab?: "empty";
  /** Who sits in the barge crane cab. */
  operator?: "ivan" | "petr";
  /** Ivan's walk to the barge crane ladder, 0 = porch, 1 = ladder (rush); he stays there for the loading. */
  walk?: number;
  /** A small reaction over a character: Ivan by the ПРУ office or at the ladder after his walk, or Petr by his crates. */
  emote?: { kind: "tired" | "question" | "sad"; at: "office" | "ladder" | "far" };
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
export { deckDelta as craneDeckDelta };

const ease = (t: number) => (t < 0.5 ? 2 * t * t : 1 - (-2 * t + 2) ** 2 / 2);
const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

type Step = { ms: number; at: (t: number) => Partial<CraneBeat> };
const tipAt = (frame: number) => craneWorld.tips[frame];
const hookUnder = (frame: number, z: number) => [tipAt(frame)[0], tipAt(frame)[1], z] as const;

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
    // hold on the loaded barge (it stays moored), then the result reads
    { ms: 900, at: () => ({ frame: last, hook: hookUnder(last, high), onDeck: true }) },
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
  // Ivan walks the quay to the barge crane ladder, then the crane does the work.
  rush: load([{ ms: 2600, at: (t) => ({ ...rest(), office: "empty", walk: t }) }], "ladder", { office: "empty", walk: 1 },
    { emote: { kind: "tired", at: "ladder" } }),
  petr: load([{ ms: 400, at: () => ({ ...rest(), busy: "far" }) }], "far", { later: true }, { emote: { kind: "sad", at: "far" } }),
};

export const craneRest: CraneBeat = { frame: last, hook: hookUnder(last, high), lifted: false, onDeck: false };

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
