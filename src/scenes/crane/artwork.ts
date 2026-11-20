/** Barge scene v7: the Blender quay (design/scene-04/blender-v6) painted per format (design/scene-04/stylized-v7), as layers.
 * Crane swap (call 17.11): the empty loading crane stands far right by the barge, Petr waits by his crates next to it. */
import { craneLayers, craneWorld } from "./layers";

// Result stills: live v7 painted quay captured by scripts/capture-barge-outcomes.mjs.
const outcomeBase = "scene-art/barge-v7";

export type Rect = { x: number; y: number; width: number; height: number };
export type CraneFormat = keyof typeof craneLayers;
type Point = readonly [number, number];
export type CraneActor = "ivan" | "ladder" | "far" | "near";

/** Bounding box around points, padded and kept inside the drawing. */
function around(points: readonly Point[], pad: number, width: number, height: number): Rect {
  const xs = points.map((p) => p[0]);
  const ys = points.map((p) => p[1]);
  const x = Math.max(0, Math.min(...xs) - pad);
  const y = Math.max(0, Math.min(...ys) - pad);
  return {
    x, y,
    width: Math.min(width, Math.max(...xs) + pad) - x,
    height: Math.min(height, Math.max(...ys) + pad) - y,
  };
}

function format(name: CraneFormat) {
  const layer = craneLayers[name];
  const a = layer.anchors;
  const { width, height } = layer;
  const project = ([x, y, z]: readonly number[]): Point => {
    const [[ax, ay, az, u], [bx, by, bz, v]] = layer.affine;
    return [ax * x + ay * y + az * z + u, bx * x + by * y + bz * z + v];
  };
  const near: readonly Point[] = [a.nearCabin, a.nearTip, a.quayFootNear, a.ladderTop];
  const corners = (r: { x: number; y: number; w: number; h: number }): Point[] => [[r.x, r.y], [r.x + r.w, r.y + r.h]];
  const sp = layer.sprites;
  // Whole figures, not just their centres: office, both cranes, the barge from bow to stern.
  // The round ПРУ office is about 11 m across; the drawn one bulges half a window left of Ivan.
  const [pu, pv] = project([-10 - 6, 20 - 6, 0]);
  const office: Point = [sp.ivan.x - sp.ivan.w * 0.7, a.pru[1]];
  const story: readonly Point[] = [a.pru, [pu, pv], office, ...corners(sp.ivan), ...corners(sp.gift), ...near, ...corners(sp.ladder),
    ...corners(sp.far), ...corners(sp.barge)];
  const tall = name === "tall";
  // Screen shift of Ivan's sprite from the start to the end of his rush walk.
  const rush = craneWorld.routes.rush;
  const walkEnd = project(rush[rush.length - 1]).map((v, i) => v - project(rush[0])[i]);
  const pad = (r: { x: number; y: number; w: number; h: number }, d: number) => ({ x: r.x - d, y: r.y - d, w: r.w + 2 * d, h: r.h + 2 * d });
  return {
    ...layer,
    project,
    // The strip that must stay in frame: office, gift, near crane, barge, far crane.
    focus: around(story, tall ? 40 : 24, width, height),
    // Air around the story inside focus; the camera may crop into it to fill the screen.
    focusPad: tall ? 40 : 24,
    // Tap targets are the actors themselves: Ivan on the ПРУ porch, the barge crane's ladder, Petr by his crates.
    targets: {
      remote: pad(sp.ivan, 14),
      rush: pad(sp.ladder, 10),
      petr: pad(sp.far, 10),
    } as Record<string, { x: number; y: number; w: number; h: number }>,
    // What each way uses: these layers light up when the way is picked.
    actors: {
      remote: ["ivan", "near"],
      rush: ["ladder", "near"],
      petr: ["far", "near"],
    } as Record<string, readonly CraneActor[]>,
    // Reaction bubbles: the tail tip just over the head of whoever reacts; `ladder` = Ivan after his walk.
    emote: {
      office: [sp.ivan.x + sp.ivan.w * 0.75, sp.ivan.y - 2],
      ladder: [sp.ivan.x + sp.ivan.w * 0.75 + walkEnd[0], sp.ivan.y - 2 + walkEnd[1]],
      far: [sp.far.x + sp.far.w * 0.75, sp.far.y - 2],
    } as const,
    // Card open on a phone: the camera closes in on the chosen way.
    zoom: tall
      ? ({
          remote: around([a.ivan, a.gift, a.nearCabin, a.deckSpot], 120, width, height),
          // Wide enough to read Ivan's walk: the quay leg from mid-quay, the gift and the whole loading crane.
          rush: around([a.ladderFoot, a.ladderTop, a.nearCabin, a.nearTip, a.gift, project([30, 17, 0])], 100, width, height),
          petr: around([a.petr, a.ladderFoot, a.nearCabin, a.deckSpot], 110, width, height),
        } as Partial<Record<string, Rect>>)
      : ({} as Partial<Record<string, Rect>>),
  };
}

export const craneArtwork = {
  wide: format("wide"),
  desk: format("desk"),
  mid: format("mid"),
  tall: format("tall"),
};
export { craneWorld };

/** What each way is about: the card eyebrow. */
export const craneCaptions = {
  remote: "Иван управляет краном из офиса ПРУ",
  rush: "Иван идёт на дальний кран",
  petr: "Пётр рядом — поднимается на кран у баржи",
} as const;

/** Short choice names for the option chips and the pins on the quay (phones fit three in one row). */
export const craneChoiceNames = {
  remote: "Иван — с пульта",
  rush: "Иван — пешком на кран",
  petr: "Попросить Петра",
} as const;

/** Pins on the quay: the two people wear their name (roles as the scenario says: «Крановщик Иван», «оператора Петра»);
 * the ladder pin has no person, only a place. On a narrow stage only the name stays. */
export const cranePins = {
  remote: { name: "Иван", detail: "крановщик" },
  rush: { name: undefined, detail: "Пешком на кран" },
  petr: { name: "Пётр", detail: "оператор" },
} as const;

/** Card facts, as the truck card lists speed and year: who, from where, when. */
export const craneFacts = {
  remote: { who: "Иван", where: "Из офиса ПРУ, с пульта", when: "Сразу", note: "Краном управляют на расстоянии, на кран подниматься не нужно" },
  rush: { who: "Иван", where: "Из кабины крана", when: "После подъёма", note: "Иван пройдёт весь причал до крана у баржи и поднимется по лестнице в кабину" },
  petr: { who: "Пётр", where: "Из кабины крана у баржи", when: "Сразу", note: "У Петра скоро своя погрузка" },
} as const;

export const craneOutcomeImage = (id: string) => `${outcomeBase}/outcome-${id}.webp`;
export const craneChoiceImage = craneArtwork.wide.plate;
