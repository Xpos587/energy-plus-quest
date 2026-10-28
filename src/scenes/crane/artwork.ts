/** Barge scene v4: one Blender quay rendered as layers per screen format (see design/scene-04/blender-v4). */
import { craneLayers, craneWorld } from "./layers";

const base = "scene-art/barge-v4";

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
  const ladderMid: Point = [a.ladderFoot[0], (a.ladderFoot[1] + a.ladderTop[1]) / 2];
  const near: readonly Point[] = [a.nearCabin, a.nearTip, a.quayFootNear, a.ladderTop];
  const corners = (r: { x: number; y: number; w: number; h: number }): Point[] => [[r.x, r.y], [r.x + r.w, r.y + r.h]];
  const sp = layer.sprites;
  // Whole figures, not just their centres: office, both cranes, the barge from bow to stern.
  // The round ПРУ office is about 11 m across.
  const [pu, pv] = project([-10 - 6, 20 - 6, 0]);
  const story: readonly Point[] = [a.pru, [pu, pv], ...corners(sp.ivan), ...corners(sp.gift), ...near, ...corners(sp.ladder),
    ...corners(sp.far), ...corners(sp.barge)];
  const tall = name === "tall";
  return {
    ...layer,
    project,
    // The strip that must stay in frame: office, gift, near crane, barge, far crane.
    focus: around(story, tall ? 40 : 24, width, height),
    hotspots: {
      remote: { x: a.ivan[0], y: a.ivan[1], side: "right" },
      rush: { x: ladderMid[0], y: ladderMid[1], side: "left" },
      wait: { x: a.nearCabin[0], y: a.nearCabin[1], side: "right" },
      petr: { x: a.petr[0], y: a.petr[1], side: "left" },
    } as Record<string, { x: number; y: number; side: "left" | "right" }>,
    chips: {
      gift: { x: a.gift[0], y: a.gift[1] + (tall ? 46 : 52) },
      barge: { x: a.bargeMid[0], y: a.bargeMid[1] + (tall ? 70 : 64) },
    },
    // What each way uses: these layers light up when the way is picked.
    actors: {
      remote: ["ivan", "near"],
      rush: ["ladder", "near"],
      wait: ["near"],
      petr: ["far", "near"],
    } as Record<string, readonly CraneActor[]>,
    // Card open on a phone: the camera closes in on the chosen way.
    zoom: tall
      ? ({
          remote: around([a.ivan, a.gift, a.nearCabin, a.deckSpot], 120, width, height),
          rush: around([a.ladderFoot, a.ladderTop, a.nearCabin, a.gift], 140, width, height),
          wait: around([a.nearCabin, a.gift, a.deckSpot, a.ladderFoot], 120, width, height),
          petr: around([a.petr, a.farCabin, a.nearCabin, a.deckSpot], 110, width, height),
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

/** What each pin points at in the drawing. */
export const craneCaptions = {
  remote: "Иван в офисе",
  rush: "Подъём в кабину",
  wait: "Кран свободен через 3 ч",
  petr: "Пётр на дальнем кране",
} as const;

/** Card facts, as the truck card lists speed and year: who, from where, when. */
export const craneFacts = {
  remote: { who: "Иван", where: "Из офиса, с пульта", when: "Сразу", note: "Кран управляется дистанционно" },
  rush: { who: "Иван", where: "Из кабины", when: "После подъёма", note: "Подъём по лестнице на высоту крана" },
  wait: { who: "По графику", where: "Из кабины", when: "Через 3 ч", note: "Баржа готова к отходу уже сейчас" },
  petr: { who: "Пётр", where: "Из ближнего крана", when: "Сразу", note: "У Петра скоро своя погрузка" },
} as const;

export const craneOutcomeImage = (id: string) => `${base}/outcome-${id}.webp`;
export const craneChoiceImage = craneArtwork.wide.plate;
