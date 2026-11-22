/** Barge scene v7: the Blender quay (design/scene-04/blender-v6) painted per format (design/scene-04/stylized-v7), as layers.
 * Crane swap (call 17.11): the empty loading crane stands far right by the barge, Petr waits by his crates next to it. */
import { craneLayers, craneWorld as quayWorld } from "./layers";
// Step cycles, cab occupants, painted-out patches and depth masks: design/scene-04/walk-v1 (boxes in format px).
import walkArt from "./walkArt.json";

export type Rect = { x: number; y: number; width: number; height: number };
export type CraneFormat = keyof typeof craneLayers;
type Point = readonly [number, number];
export type CraneActor = "ivan" | "far" | "near";
type Sprite = { src: string; x: number; y: number; w: number; h: number };
/** A frame grid (cols × rows) in one image, frames left to right, top to bottom. */
export type CraneSheet = Sprite & { cols: number; rows: number };
type Walker = "Ivan" | "Petr";

/** Call 21.11: Petr waits just right of his crane's right legs, between the rails (not on the quay edge under his boom),
 * and walks straight along the rails to the barge crane ladder. The plate still has him at the old spot: the `post`
 * patch covers it and his cut-out and step sheets are shifted by the world move (a pure screen shift for this camera).
 * ponytail: depth masks for this lane are the old ones; re-render walk-v1 if something must pass in front of him. */
const petrFrom = quayWorld.routes.petr[0];
// Owner 22.11: he stood on the right leg's bogie by the quay edge; now clear of it, inland of the sea rail and
// seaward of his crates (x ≥ 29.5, y 6.8…11.8), so the straight lane passes in front of them.
const petrRoute = [[23.5, 5.9, 0], [57, 5.9, 0], quayWorld.routes.petr[2]] as const;
const petrMove = petrRoute[0].map((v, i) => v - petrFrom[i]);
/** Remote (call 21.11, owner 22.11): Ivan steps from the porch straight inland up the steps into the ПРУ door, then
 * radios the crane. 5 m inland is the dark doorway on the desk plate (3.4 m stopped him on the bottom step). */
const officeRoute = [quayWorld.routes.rush[0], [quayWorld.routes.rush[0][0], quayWorld.routes.rush[0][1] + 5, 0]] as const;
const craneWorld = { ...quayWorld, routes: { ...quayWorld.routes, petr: petrRoute, office: officeRoute } };
/** Walk art not every format has yet (being made in .tmp-work/crane-anim); each piece is drawn only when present.
 * post: the quay with Petr painted out while he walks (as porch for Ivan).
 * cab<Walker>: the person seen in the loading crane cab, one sheet frame per `top` slew frame.
 * walk<Walker><Dir> / climb<Walker>: step cycles, boxed at the route start / ladder foot like the walker sprite.
 * walkOccluder… / turnOccluder… / climbOccluder: scenery nearer the camera than the walk, drawn over the walker. */
export type CraneOptionalSprites = Partial<
  Record<"post" | "walkOccluder" | "walkOccluderPetr" | "turnOccluderIvan" | "turnOccluderPetr" | "climbOccluder", Sprite>
  & Record<`walk${Walker}${"East" | "Inland" | "Seaward"}` | `climb${Walker}` | `cab${Walker}`, CraneSheet>
>;

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
  const [[ax, ay, az], [bx, by, bz]] = layer.affine;
  const [mx, my, mz] = petrMove;
  const shift = <T extends { x: number; y: number }>(r: T): T => ({ ...r, x: r.x + ax * mx + ay * my + az * mz, y: r.y + bx * mx + by * my + bz * mz });
  const art = walkArt.formats[name] as CraneOptionalSprites;
  const sp = {
    ...layer.sprites, ...art,
    far: shift(layer.sprites.far),
    ...Object.fromEntries((["walkPetrEast", "walkPetrInland", "walkPetrSeaward"] as const).filter((k) => art[k]).map((k) => [k, shift(art[k]!)])),
  } as typeof layer.sprites & CraneOptionalSprites;
  const petr = shift({ x: a.petr[0], y: a.petr[1] });
  const anchors = { ...a, petr: [petr.x, petr.y] as const };
  // Whole figures, not just their centres: office, both cranes, the barge from bow to stern.
  // The round ПРУ office is about 11 m across; the drawn one bulges half a window left of Ivan.
  const [pu, pv] = project([-10 - 6, 20 - 6, 0]);
  const office: Point = [sp.ivan.x - sp.ivan.w * 0.7, a.pru[1]];
  const story: readonly Point[] = [a.pru, [pu, pv], office, ...corners(sp.ivan), ...corners(sp.gift), ...near, ...corners(sp.ladder),
    ...corners(sp.far), ...corners(sp.barge)];
  const tall = name === "tall";
  const metre = Math.hypot(layer.affine[0][0], layer.affine[1][0]);
  const pad = (r: { x: number; y: number; w: number; h: number }, d: number) => ({ x: r.x - d, y: r.y - d, w: r.w + 2 * d, h: r.h + 2 * d });
  return {
    ...layer,
    anchors,
    sprites: sp,
    project,
    // The strip that must stay in frame: office, gift, near crane, barge, far crane.
    focus: around(story, tall ? 40 : 24, width, height),
    // Air around the story inside focus; the camera may crop into it to fill the screen.
    focusPad: tall ? 40 : 24,
    // Tap targets are the actors themselves: Ivan on the ПРУ porch, the barge crane's cab, Petr by his crates.
    // Owner 22.11: pin 2 on the ladder read as nothing; it marks the cab (about 5 × 7 m on screen around nearCabin).
    targets: {
      remote: pad(sp.ivan, 14),
      rush: pad({ x: a.nearCabin[0] - 2.5 * metre, y: a.nearCabin[1] - 3.5 * metre, w: 5 * metre, h: 7 * metre }, 12),
      petr: pad(sp.far, 10),
    } as Record<string, { x: number; y: number; w: number; h: number }>,
    // What each way uses: these layers light up when the way is picked.
    actors: {
      remote: ["ivan", "near"],
      // No glow on the ladder (owner 20.11: the lit ladder looked awful); Ivan is the one who walks.
      rush: ["ivan", "near"],
      petr: ["far", "near"],
    } as Record<string, readonly CraneActor[]>,
    // Reaction bubbles: the tail tip over Ivan's head at the office, or over the loading crane cab once someone climbed in.
    emote: {
      office: [sp.ivan.x + sp.ivan.w * 0.75, sp.ivan.y - 2],
      cab: [a.nearCabin[0], a.nearCabin[1] - 2.4 * metre],
    } as const,
  };
}

export const craneArtwork = {
  wide: format("wide"),
  desk: format("desk"),
  mid: format("mid"),
  tall: format("tall"),
};
export { craneWorld };
/** World metres per 8-phase step cycle of the walk sheets. */
export const craneWalkCycle = walkArt.walkCycleMetres;

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

/** Card facts, as the truck card lists speed and year: who, from where, when. */
export const craneFacts = {
  remote: { who: "Иван", where: "Из офиса ПРУ, с пульта", when: "Сразу", note: "Краном управляют на расстоянии, на кран подниматься не нужно" },
  rush: { who: "Иван", where: "Из кабины крана", when: "После подъёма", note: "Иван пройдёт весь причал до крана у баржи и поднимется по лестнице в кабину" },
  petr: { who: "Пётр", where: "Из кабины крана у баржи", when: "Сразу", note: "У Петра скоро своя погрузка" },
} as const;

export const craneChoiceImage = craneArtwork.wide.plate;
