import {
  carrierFacts,
  type MapCarrierId,
  mapCarrierIds,
} from "../game/carrierFacts";
import manifest from "./cityV4Manifest.json";
import { carrierColors, depotPill, rigPin, rr, sparkle } from "./cityPins";

// Scene 1 city v4. One Blender scene is the source of truth: the plates
// (wide for landscape, tall for portrait) are its truck-free renders, the rigs
// are sprites of its truck models in 16 headings, and the routes are its lane
// centre lines in metres. Trucks are simulated in world metres and projected
// through the plate camera, so both plates show the same traffic.

type Pt = [number, number];
// [atlasX, atlasY, w, h, offX, offY, exhaustX, exhaustY]: atlas px are at
// sprites.scale; offsets are plate px from the rig's projected centre.
type Frame = [number, number, number, number, number, number, number, number];
type PlateSpec = {
  res: [number, number];
  mpp: number;
  proj: [number[], number[]];
  keep: number[];
  dock: Pt;
  express: Pt;
  autopick: Pt;
  warehouse: Pt;
  sign: Pt[];
  sprites: {
    scale: number;
    atlas: [number, number];
    trucks: Record<string, Frame[]>;
  };
};
type TruckSprite = MapCarrierId | "express";
/** Rig geometry in metres along the rig axis, from its centre. */
type RigGeometry = {
  front: number;
  frontAxle: number;
  rearAxle: number;
  kingpin: number;
  tractorRear: number;
  trailerFront: number;
  bogie: number;
  trailerRear: number;
  width: number;
};
type Manifest = {
  truckM: number[];
  rig: RigGeometry;
  speedKmh: Record<MapCarrierId, number>;
  routes: Record<MapCarrierId, Pt[]>;
  headings: number;
  plates: Record<PlateName, PlateSpec>;
  /** World boxes [x0, y0, z0, x1, y1, z1] tall enough to hide a lane. */
  occluders: number[][];
};
const M = manifest as unknown as Manifest;

export type PlateName = "wide" | "tall";
export const plates = M.plates;
export const plateAspect = (name: PlateName) =>
  M.plates[name].res[0] / M.plates[name].res[1];
/** Clearly landscape map areas get the wide plate; square and portrait ones
 * the tall plate, whose safe area is its central square. */
export const plateFor = (width: number, height: number): PlateName =>
  width >= height * 1.3 ? "wide" : "tall";

// Full literal paths: the static packager (scripts/stage-static.mjs) ships
// only media whose path appears in the bundle.
const files = {
  wide: {
    plate: "scene1-v4/plate-wide.webp?v=2",
    retina: "scene1-v4/plate-wide@2x.webp?v=2",
    trucks: "scene1-v4/trucks-wide.webp?v=5",
  },
  tall: {
    plate: "scene1-v4/plate-tall.webp?v=2",
    retina: "scene1-v4/plate-tall@2x.webp?v=2",
    trucks: "scene1-v4/trucks-tall.webp?v=5",
  },
} as const;
const url = (path: string) => `${import.meta.env.BASE_URL}${path}`;
export const plateSource = (name: PlateName) => url(files[name].plate);
/** Retina plate: the tile-by-tile AI-restored master (3x3 crops, registered
 * and blended back), 1.5x for the wide plate and 2x for the tall one. */
const RETINA = { wide: 1.5, tall: 2 } as const;
export const plateSrcSet = (name: PlateName) => {
  const [w] = M.plates[name].res;
  return `${plateSource(name)} ${w}w, ${url(files[name].retina)} ${Math.round(w * RETINA[name])}w`;
};

/** World metres -> plate px (orthographic camera, z up). */
export function project(name: PlateName, x: number, y: number, z = 0.4): Pt {
  const [a, b] = M.plates[name].proj;
  return [
    a[0] * x + a[1] * y + a[2] * z + a[3],
    b[0] * x + b[1] * y + b[2] * z + b[3],
  ];
}

// ---------------------------------------------------------------- routes

/** Map seconds run faster than real time: a loop takes 15-25 s on screen. */
export const MPS_PER_KMH = 0.55;
export const truckSpeed = (id: MapCarrierId) =>
  carrierFacts[id].citySpeedKmh * MPS_PER_KMH;

export type Route = {
  id: MapCarrierId;
  pts: Pt[];
  cum: number[];
  length: number;
};
function buildRoute(id: MapCarrierId): Route {
  const pts = M.routes[id];
  const cum = [0];
  for (let k = 1; k <= pts.length; k++) {
    const a = pts[k - 1];
    const b = pts[k % pts.length];
    cum.push(cum[k - 1] + Math.hypot(b[0] - a[0], b[1] - a[1]));
  }
  return { id, pts, cum, length: cum[pts.length] };
}
let cached: Route[] | undefined;
export const cityRoutes = () => (cached ??= mapCarrierIds.map(buildRoute));

const mod = (v: number, m: number) => ((v % m) + m) % m;
function pointAt(r: Route, distance: number): Pt {
  const s = mod(distance, r.length);
  let lo = 0;
  let hi = r.pts.length - 1;
  while (lo < hi) {
    const mid = (lo + hi + 1) >> 1;
    if (r.cum[mid] <= s) lo = mid;
    else hi = mid - 1;
  }
  const a = r.pts[lo];
  const b = r.pts[(lo + 1) % r.pts.length];
  const span = r.cum[lo + 1] - r.cum[lo];
  const t = span > 0 ? (s - r.cum[lo]) / span : 0;
  return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t];
}

/** Rig centre and heading (radians, world frame, counter-clockwise from +x). */
export type Pose = { x: number; y: number; heading: number };

/** An articulated rig: the tractor steers along the lane (both axles on the
 * route), the trailer pivots on the kingpin and its bogie follows the lane
 * behind, so in a corner the trailer swings in and lines up again after. */
export type Rig = {
  kingpin: Pt;
  tractor: number;
  trailer: number;
};
export const RIG = M.rig;
export function rigAt(r: Route, distance: number): Rig {
  const [fx, fy] = pointAt(r, distance + RIG.frontAxle);
  const [rx, ry] = pointAt(r, distance + RIG.rearAxle);
  const tractor = Math.atan2(fy - ry, fx - rx);
  const lead = RIG.kingpin - RIG.rearAxle;
  const kingpin: Pt = [
    rx + Math.cos(tractor) * lead,
    ry + Math.sin(tractor) * lead,
  ];
  const [bx, by] = pointAt(r, distance + RIG.bogie);
  const trailer = Math.atan2(kingpin[1] - by, kingpin[0] - bx);
  return { kingpin, tractor, trailer };
}
const along = (q: Pt, heading: number, d: number): Pt => [
  q[0] + Math.cos(heading) * d,
  q[1] + Math.sin(heading) * d,
];
/** Tractor and trailer as two boxes (centre, heading, half length). */
export function rigBoxes(g: Rig): [Pose, number][] {
  const k = RIG.kingpin;
  const tc = (RIG.front + RIG.tractorRear) / 2 - k;
  const lc = (RIG.trailerFront + RIG.trailerRear) / 2 - k;
  const [tx, ty] = along(g.kingpin, g.tractor, tc);
  const [lx, ly] = along(g.kingpin, g.trailer, lc);
  return [
    [{ x: tx, y: ty, heading: g.tractor }, (RIG.front - RIG.tractorRear) / 2],
    [
      { x: lx, y: ly, heading: g.trailer },
      (RIG.trailerFront - RIG.trailerRear) / 2,
    ],
  ];
}
/** Hit-target pose: the middle of the rig, along the cab-to-tail line. */
export function rigPose(g: Rig): Pose {
  const nose = along(g.kingpin, g.tractor, RIG.front - RIG.kingpin);
  const tail = along(g.kingpin, g.trailer, RIG.trailerRear - RIG.kingpin);
  return {
    x: (nose[0] + tail[0]) / 2,
    y: (nose[1] + tail[1]) / 2,
    heading: Math.atan2(nose[1] - tail[1], nose[0] - tail[0]),
  };
}
export function poseAt(r: Route, distance: number): Pose {
  return rigPose(rigAt(r, distance));
}

// ---------------------------------------------------------------- traffic

// A timetable instead of right-of-way: every rig drives its own loop at a
// constant speed, never brakes, and the start phases keep the bodies apart
// (cityV4.test.ts checks a 1.5 m gap over the whole cycle). Laps are whole
// fractions of the green lap so the pattern repeats exactly; carrierFacts
// speeds are these laps rounded to km/h.
const LAPS: Record<MapCarrierId, number> = { crew: 1, old4: 1, near: 1.5, old: 1 };
const startPhase: Record<MapCarrierId, number> = {
  old4: 0,
  crew: 0.5,
  near: 0.25,
  old: 0,
};
const RIG_W = M.rig.width;

type Box = Pose & { hl: number };
function corners(b: Box, grow: number): Pt[] {
  const c = Math.cos(b.heading);
  const s = Math.sin(b.heading);
  const hl = b.hl + grow;
  const hw = RIG_W / 2 + grow;
  return [
    [1, 1],
    [1, -1],
    [-1, -1],
    [-1, 1],
  ].map(([u, v]) => [
    b.x + c * u * hl - s * v * hw,
    b.y + s * u * hl + c * v * hw,
  ]);
}
/** Separating-axis test for two boxes. */
function boxesTouch(a: Box, b: Box, grow: number) {
  if (Math.hypot(a.x - b.x, a.y - b.y) > a.hl + b.hl + RIG_W + 2 * grow)
    return false;
  const A = corners(a, grow / 2);
  const B = corners(b, grow / 2);
  for (const poly of [A, B])
    for (let i = 0; i < 4; i++) {
      const [x1, y1] = poly[i];
      const [x2, y2] = poly[(i + 1) % 4];
      const nx = y2 - y1;
      const ny = x1 - x2;
      let a0 = Infinity,
        a1 = -Infinity,
        b0 = Infinity,
        b1 = -Infinity;
      for (const [x, y] of A) {
        const d = x * nx + y * ny;
        a0 = Math.min(a0, d);
        a1 = Math.max(a1, d);
      }
      for (const [x, y] of B) {
        const d = x * nx + y * ny;
        b0 = Math.min(b0, d);
        b1 = Math.max(b1, d);
      }
      if (a1 < b0 || b1 < a0) return false;
    }
  return true;
}
const boxes = (g: Rig): Box[] => rigBoxes(g).map(([p, hl]) => ({ ...p, hl }));
/** Do two articulated rigs (tractor and trailer boxes each) touch? */
export function rigsTouch(a: Rig, b: Rig, grow = 0) {
  const A = boxes(a);
  const B = boxes(b);
  return A.some((p) => B.some((q) => boxesTouch(p, q, grow)));
}

/** Seconds per lap of the green loop; every other lap is a multiple. */
const greenLap = () =>
  (cityRoutes().find((r) => r.id === "crew") as Route).length /
  truckSpeed("crew");
/** Timetable speed in m/s (carrierFacts holds it rounded, in km/h). */
export const lapSpeed = (r: Route) => r.length / (greenLap() * LAPS[r.id]);

export type Traffic = { time: number; s: number[] };
export function createTraffic(): Traffic {
  const t: Traffic = { time: 0, s: [] };
  stepTraffic(t, 0);
  return t;
}
export function stepTraffic(t: Traffic, dt: number) {
  t.time += Math.max(0, dt);
  t.s = cityRoutes().map((r) =>
    mod(startPhase[r.id] * r.length + lapSpeed(r) * t.time, r.length),
  );
}
export const trafficRigs = (t: Traffic) =>
  cityRoutes().map((r, i) => rigAt(r, t.s[i]));
export const trafficPoses = (t: Traffic) => trafficRigs(t).map(rigPose);

/** Normalised (0..1) plate positions of the rigs, for hit targets and camera. */
export function trafficFrame(t: Traffic, name: PlateName): Pt[] {
  const [W, H] = M.plates[name].res;
  return trafficPoses(t).map((p) => {
    const [x, y] = project(name, p.x, p.y, 1.6);
    return [x / W, y / H];
  });
}
export const landmark = (
  name: PlateName,
  key: "dock" | "express" | "autopick" | "warehouse",
): Pt => {
  const [W, H] = M.plates[name].res;
  const [x, y] = M.plates[name][key];
  return [x / W, y / H];
};

// ---------------------------------------------------------------- assets

export type CityAssets = Record<PlateName, CanvasImageSource | undefined>;
export function loadTruckAtlas(name: PlateName): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const image = new Image();
    image.decoding = "async";
    image.onload = () => resolve(image);
    image.onerror = reject;
    image.src = url(files[name].trucks);
  });
}

/** Painted smoke puffs (public/scene1-v4/smoke.webp, 4x2 cells of 192 px):
 * loaded lazily on first draw; canvas puffs are the fallback meanwhile. */
let smokeImage: HTMLImageElement | undefined;
function smokeSprite(): HTMLImageElement | undefined {
  if (typeof Image === "undefined") return undefined;
  if (!smokeImage) {
    smokeImage = new Image();
    smokeImage.decoding = "async";
    smokeImage.src = url("scene1-v4/smoke.webp?v=1");
  }
  return smokeImage.complete && smokeImage.naturalWidth
    ? smokeImage
    : undefined;
}

// ---------------------------------------------------------------- drawing

export type DrawOptions = {
  plate: PlateName;
  /** canvas px = plate px * k + offset (device px). */
  k: number;
  ox: number;
  oy: number;
  dpr: number;
  selected?: string;
  expressAge?: number;
  pins: boolean;
  pinScale: number;
  reduced: boolean;
};

/** Two neighbouring heading frames and the blend between them, so a turning
 * rig rotates continuously instead of snapping between sprite angles. */
export function headingFrames(heading: number): [number, number, number] {
  const f = mod((heading / (Math.PI * 2)) * M.headings, M.headings);
  const a = Math.floor(f);
  return [a % M.headings, (a + 1) % M.headings, f - a];
}

function blit(
  c: CanvasRenderingContext2D,
  atlas: CanvasImageSource,
  f: Frame,
  at: Pt,
  unit: number,
  o: DrawOptions,
) {
  c.drawImage(
    atlas,
    f[0],
    f[1],
    f[2],
    f[3],
    o.ox + (at[0] + f[4]) * o.k,
    o.oy + (at[1] + f[5]) * o.k,
    f[2] * unit,
    f[3] * unit,
  );
}

function contactShadow(
  c: CanvasRenderingContext2D,
  at: Pt,
  heading: number,
  half: number,
  o: DrawOptions,
  mpp: number,
) {
  const m = o.k / mpp;
  const [pa, pb] = M.plates[o.plate].proj;
  const ch = Math.cos(heading);
  const shh = Math.sin(heading);
  const dx = pa[0] * ch + pa[1] * shh;
  const dy = pb[0] * ch + pb[1] * shh;
  const len = Math.hypot(dx, dy) * half * o.k + 1.6 * m;
  c.save();
  c.translate(o.ox + at[0] * o.k + 0.6 * m, o.oy + at[1] * o.k + 0.9 * m);
  c.rotate(Math.atan2(dy, dx));
  const sh = c.createRadialGradient(0, 0, 0, 0, 0, len);
  sh.addColorStop(0, "rgba(31,43,60,0.26)");
  sh.addColorStop(0.7, "rgba(31,43,60,0.16)");
  sh.addColorStop(1, "rgba(31,43,60,0)");
  c.fillStyle = sh;
  c.scale(1, (2.2 * m) / len);
  c.beginPath();
  c.arc(0, 0, len, 0, Math.PI * 2);
  c.fill();
  c.restore();
}

// Shadows on the painted plate fall to the left and a little down (screen),
// about half the visible height long. In world metres that is mostly -x:
// solve proj * shift = (-1, 0.25) * 0.5 * |z| per metre of height.
const sunShift = (plate: PlateName): Pt => {
  const [pa, pb] = M.plates[plate].proj;
  const L = 0.75 * Math.abs(pb[2]);
  const [tx, ty] = [-0.85 * L, 0.55 * L];
  const det = pa[0] * pb[1] - pa[1] * pb[0];
  return [(tx * pb[1] - pa[1] * ty) / det, (pa[0] * ty - tx * pb[0]) / det];
};
/** Cast shadow of a box part (cab or trailer): the hull of its footprint and
 * the footprint moved away from the sun by its height, filled flat in the
 * plate's shadow tone so it reads like the buildings' and trees' shadows. */
function shadowHull(
  at: Pt,
  heading: number,
  half: number,
  width: number,
  height: number,
  o: DrawOptions,
) {
  // `at` is the part's ground centre in plate px; offsets go through the
  // linear part of the plate projection (metres -> plate px).
  const [pa, pb] = M.plates[o.plate].proj;
  const ch = Math.cos(heading);
  const sh = Math.sin(heading);
  const w = width / 2;
  const sun = sunShift(o.plate);
  const pts: Pt[] = [];
  for (const lift of [0, height]) {
    for (const [u, v] of [
      [half, w],
      [half, -w],
      [-half, -w],
      [-half, w],
    ]) {
      const x = ch * u - sh * v + sun[0] * lift;
      const y = sh * u + ch * v + sun[1] * lift;
      const px = at[0] + pa[0] * x + pa[1] * y;
      const py = at[1] + pb[0] * x + pb[1] * y;
      pts.push([o.ox + px * o.k, o.oy + py * o.k]);
    }
  }
  pts.sort((a, b) => a[0] - b[0] || a[1] - b[1]);
  const cross = (a: Pt, b: Pt, q: Pt) =>
    (b[0] - a[0]) * (q[1] - a[1]) - (b[1] - a[1]) * (q[0] - a[0]);
  const lower: Pt[] = [];
  for (const q of pts) {
    while (
      lower.length > 1 &&
      cross(lower[lower.length - 2], lower[lower.length - 1], q) <= 0
    )
      lower.pop();
    lower.push(q);
  }
  const upper: Pt[] = [];
  for (let i = pts.length - 1; i >= 0; i--) {
    const q = pts[i];
    while (
      upper.length > 1 &&
      cross(upper[upper.length - 2], upper[upper.length - 1], q) <= 0
    )
      upper.pop();
    upper.push(q);
  }
  return lower.slice(0, -1).concat(upper.slice(0, -1));
}
/** One fill for all hulls of a rig (nonzero union: no darker overlap),
 * in the bluish tone of the plate's painted shadows on asphalt. */
function fillShadows(c: CanvasRenderingContext2D, hulls: Pt[][]) {
  c.save();
  c.fillStyle = "rgba(79,121,162,0.5)";
  c.beginPath();
  for (const hull of hulls)
    hull.forEach((q, i) => (i ? c.lineTo(q[0], q[1]) : c.moveTo(q[0], q[1])));
  c.fill("nonzero");
  c.restore();
}

/** One sprite part at a world heading, cross-faded between neighbour frames.
 * Returns the exhaust anchor of the blended frame. */
function drawPart(
  c: CanvasRenderingContext2D,
  atlas: CanvasImageSource,
  spec: PlateSpec,
  key: string,
  at: Pt,
  heading: number,
  o: DrawOptions,
) {
  const frames = spec.sprites.trucks[key];
  const unit = o.k / spec.sprites.scale;
  const [a, b, t] = headingFrames(heading);
  const alpha = c.globalAlpha;
  // Short cross-fade around the switch point only: most of the time a single
  // crisp frame shows, and the swap is a quick dissolve instead of a pop.
  const [base, top, w] = t < 0.5 ? [a, b, t] : [b, a, 1 - t];
  blit(c, atlas, frames[base], at, unit, o);
  const fade = Math.min(1, Math.max(0, (w - 0.42) / 0.08));
  if (fade > 0.02) {
    c.globalAlpha = alpha * fade;
    blit(c, atlas, frames[top], at, unit, o);
    c.globalAlpha = alpha;
  }
  const f = frames[base];
  const g = frames[top];
  return [
    at[0] + f[6] + (g[6] - f[6]) * w,
    at[1] + f[7] + (g[7] - f[7]) * w,
  ] as Pt;
}

/** The parked express rig: one rigid sprite. */
function drawRig(
  c: CanvasRenderingContext2D,
  atlas: CanvasImageSource,
  spec: PlateSpec,
  id: TruckSprite,
  at: Pt,
  heading: number,
  o: DrawOptions,
) {
  const half = (RIG.front - RIG.trailerRear) / 2;
  fillShadows(c, [
    shadowHull(at, heading, half * 0.96, RIG_W * 0.92, RIG_W * 1.45, o),
  ]);
  contactShadow(c, at, heading, half, o, spec.mpp);
  return drawPart(c, atlas, spec, id, at, heading, o);
}

// ---------------------------------------------------------------- occlusion

/** Unit vector from the scene towards the orthographic camera: the null
 * space of the plate projection, pointing up. */
function towardCamera(plate: PlateName): number[] {
  const [a, b] = M.plates[plate].proj;
  const v = [
    a[1] * b[2] - a[2] * b[1],
    a[2] * b[0] - a[0] * b[2],
    a[0] * b[1] - a[1] * b[0],
  ];
  const n = Math.hypot(v[0], v[1], v[2]) * Math.sign(v[2]);
  return v.map((q) => q / n);
}
/** Does the ground ray from p towards the camera cross the footprint of B?
 * Rig sprites are scaled up and drawn standing, so any rig on the far side
 * of a building is behind it; the clip only bites where they overlap. */
function hidden(p: Pt, B: number[], d: number[]) {
  let t0 = 0;
  let t1 = Infinity;
  for (let i = 0; i < 2; i++) {
    if (Math.abs(d[i]) < 1e-9) {
      if (p[i] < B[i] || p[i] > B[i + 3]) return false;
      continue;
    }
    let u = (B[i] - p[i]) / d[i];
    let v = (B[i + 3] - p[i]) / d[i];
    if (u > v) [u, v] = [v, u];
    t0 = Math.max(t0, u);
    t1 = Math.min(t1, v);
    if (t0 > t1) return false;
  }
  return true;
}
/** Screen silhouettes (plate px) of the buildings standing between the
 * camera and this rig. The painted plate shows them; the rig is clipped. */
export function occludersOf(plate: PlateName, g: Rig): Pt[][] {
  const d = towardCamera(plate);
  const parts = rigBoxes(g);
  return M.occluders
    .filter((B) =>
      parts.some(([p, hl]) =>
        [-0.8, 0, 0.8].some((u) =>
          hidden(
            [
              p.x + Math.cos(p.heading) * u * hl,
              p.y + Math.sin(p.heading) * u * hl,
            ],
            B,
            d,
          ),
        ),
      ),
    )
    .map((B) => {
      const pts: Pt[] = [];
      for (const x of [B[0], B[3]])
        for (const y of [B[1], B[4]])
          for (const z of [B[2], B[5]]) pts.push(project(plate, x, y, z));
      return hull(pts);
    });
}
function hull(points: Pt[]): Pt[] {
  const pts = [...points].sort((a, b) => a[0] - b[0] || a[1] - b[1]);
  const cross = (a: Pt, b: Pt, q: Pt) =>
    (b[0] - a[0]) * (q[1] - a[1]) - (b[1] - a[1]) * (q[0] - a[0]);
  const half = (list: Pt[]) => {
    const out: Pt[] = [];
    for (const q of list) {
      while (
        out.length > 1 &&
        cross(out[out.length - 2], out[out.length - 1], q) <= 0
      )
        out.pop();
      out.push(q);
    }
    return out.slice(0, -1);
  };
  return half(pts).concat(half(pts.reverse()));
}

/** An articulated rig: low tractor frame, then trailer and cab in depth
 * order, each turning on its own heading about the kingpin. */
function drawArticulated(
  c: CanvasRenderingContext2D,
  atlas: CanvasImageSource,
  spec: PlateSpec,
  id: MapCarrierId,
  g: Rig,
  o: DrawOptions,
  jitter: Pt,
) {
  const at = project(o.plate, g.kingpin[0], g.kingpin[1]);
  const kp: Pt = [at[0] + jitter[0], at[1] + jitter[1]];
  const [[tb, th], [lb, lh]] = rigBoxes(g);
  const cabAt = project(o.plate, tb.x, tb.y);
  const trlAt = project(o.plate, lb.x, lb.y);
  fillShadows(c, [
    shadowHull(trlAt, g.trailer, lh, RIG_W * 0.92, RIG_W * 1.45, o),
    shadowHull(cabAt, g.tractor, th, RIG_W * 0.92, RIG_W * 1.3, o),
  ]);
  contactShadow(c, trlAt, g.trailer, lh, o, spec.mpp);
  contactShadow(c, cabAt, g.tractor, th, o, spec.mpp);
  drawPart(c, atlas, spec, `${id}-chassis`, kp, g.tractor, o);
  let exhaust: Pt = kp;
  const cab = () => {
    exhaust = drawPart(c, atlas, spec, `${id}-cab`, kp, g.tractor, o);
  };
  const trailer = () =>
    drawPart(c, atlas, spec, `${id}-trailer`, kp, g.trailer, o);
  // The part nearer the viewer (lower on screen) is drawn last.
  if (cabAt[1] >= trlAt[1]) {
    trailer();
    cab();
  } else {
    cab();
    trailer();
  }
  return exhaust;
}

// Smoke: puffs live in world-anchored plate px and rise in screen space.
type Puff = { x: number; y: number; born: number; dark: boolean; big: boolean };
export type Smoke = {
  puffs: Record<"old" | "old4", Puff[]>;
  last: Record<"old" | "old4", number>;
  plate?: PlateName;
};
export const createSmoke = (): Smoke => ({
  puffs: { old: [], old4: [] },
  last: { old: -1, old4: -1 },
});

/** Yellow rig: short coughs with gaps and a dark backfire every few seconds. */
export function sputter(time: number) {
  const beat = time % 3.4;
  if (beat < 0.16) return { on: true, dark: true, big: true };
  return {
    on: Math.sin(time * 9.5) > 0.2 && beat > 0.7,
    dark: false,
    big: false,
  };
}

function emitSmoke(smoke: Smoke, id: "old" | "old4", at: Pt, time: number) {
  const list = smoke.puffs[id];
  const gap = id === "old" ? 0.24 : 0.1;
  if (time - smoke.last[id] < gap && time >= smoke.last[id]) return;
  smoke.last[id] = time;
  if (id === "old")
    list.push({ x: at[0], y: at[1], born: time, dark: false, big: false });
  else {
    const s = sputter(time);
    if (s.on)
      list.push({ x: at[0], y: at[1], born: time, dark: s.dark, big: s.big });
  }
  const life = id === "old" ? 2.2 : 1.7;
  while (list.length && time - list[0].born > life) list.shift();
  if (list.length > 80) list.splice(0, list.length - 80);
}

function drawSmoke(
  c: CanvasRenderingContext2D,
  smoke: Smoke,
  id: "old" | "old4",
  time: number,
  o: DrawOptions,
  mpp: number,
) {
  const steady = id === "old";
  const life = steady ? 2.2 : 1.7;
  const m = o.k / mpp; // device px per metre
  // Cel-shaded cloud, like the plate: opaque flat puffs merged under one soft
  // darker contour (all contours first, then fills, then highlights). Puffs
  // fade by shrinking, never by stacking translucent discs.
  const puffs: { x: number; y: number; r: number; dark: boolean }[] = [];
  const ages: number[] = [];
  for (const p of smoke.puffs[id]) {
    const age = Math.min(1, Math.max(0, (time - p.born) / life));
    const ease = 1 - (1 - age) ** 2;
    const grow = 0.7 + ease * 2.6;
    const shrink = age < 0.45 ? 1 : 1 - ((age - 0.45) / 0.55) ** 1.4;
    // Readable at overview zoom too: never thinner than a few CSS px.
    const r =
      Math.max(grow, ((1.6 + ease * 4.4) * o.dpr * o.pinScale) / m) *
      (p.big ? 1.5 : 1) *
      shrink *
      m;
    if (r < 0.6 * o.dpr) continue;
    const rise = Math.max(m, 2.4 * o.dpr * o.pinScale);
    const drift = Math.sin(p.born * 7.3 + age * 3) * 0.6;
    ages.push(age);
    puffs.push({
      x: o.ox + p.x * o.k + (ease * 3.2 + drift) * rise,
      y: o.oy + p.y * o.k - ease * 9 * rise,
      r,
      dark: p.dark,
    });
  }
  const sprite = smokeSprite();
  if (sprite) {
    // Painted puffs (same artist as the plate): 4 growth stages x light/dark,
    // drawn oldest first so fresh puffs sit on top at the exhaust.
    const C = 192;
    c.save();
    for (let k = 0; k < puffs.length; k++) {
      const p = puffs[k];
      const age = ages[k];
      const stage = age < 0.12 ? 0 : age < 0.3 ? 1 : age < 0.55 ? 2 : 3;
      const d = p.r * 2.3;
      c.globalAlpha = age > 0.8 ? 1 - (age - 0.8) / 0.2 : 1;
      c.drawImage(
        sprite,
        stage * C,
        p.dark ? C : 0,
        C,
        C,
        p.x - d / 2,
        p.y - d / 2,
        d,
        d,
      );
    }
    c.restore();
    return;
  }
  const tones = (dark: boolean) =>
    dark
      ? ["#3d3f47", "#5a5c64", "#74767e"]
      : steady
        ? ["#a3a8ae", "#d3d5d6", "#e6e8e6"]
        : ["#aeafb2", "#dedcd6", "#eeece6"];
  const edge = Math.max(0.8 * o.dpr, 0.14 * m);
  c.save();
  const alpha0 = c.globalAlpha;
  c.globalAlpha = alpha0 * 0.82;
  for (let pass = 0; pass < 3; pass++)
    for (const p of puffs) {
      c.fillStyle = tones(p.dark)[pass];
      c.beginPath();
      if (pass === 0) c.arc(p.x, p.y + edge * 0.4, p.r + edge, 0, Math.PI * 2);
      else if (pass === 1) c.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      else
        c.arc(p.x - p.r * 0.18, p.y - p.r * 0.22, p.r * 0.62, 0, Math.PI * 2);
      c.fill();
    }
  c.restore();
}

/** The blank sign board over the docks gets the word, mapped onto its face. */
function drawSign(
  c: CanvasRenderingContext2D,
  spec: PlateSpec,
  o: DrawOptions,
) {
  const [tl, tr, , bl] = spec.sign;
  const P = (q: Pt): Pt => [o.ox + q[0] * o.k, o.oy + q[1] * o.k];
  const [x0, y0] = P(tl);
  const [x1, y1] = P(tr);
  const [x3, y3] = P(bl);
  const w = Math.hypot(x1 - x0, y1 - y0);
  const h = Math.hypot(x3 - x0, y3 - y0);
  if (w < 14 || h < 4 || Math.min(h * 0.78, w * 0.24) < 11 * o.dpr) {
    // Overview zoom: drawn later as a tag above the pins (see signAnchor).
    return;
  }
  c.save();
  // unit square (0..1, 0..1) -> board face
  c.setTransform(x1 - x0, y1 - y0, x3 - x0, y3 - y0, x0, y0);
  c.fillStyle = "#ffffff";
  c.fillRect(0.02, 0.06, 0.96, 0.88);
  c.restore();
  c.save();
  c.setTransform(
    (x1 - x0) / w,
    (y1 - y0) / w,
    (x3 - x0) / h,
    (y3 - y0) / h,
    x0,
    y0,
  );
  c.fillStyle = "#0057b8";
  c.textAlign = "center";
  c.textBaseline = "middle";
  const size = Math.min(h * 0.78, w * 0.24);
  c.font = `700 ${size}px "Roboto Condensed", Arial, sans-serif`;
  if ("letterSpacing" in c)
    (c as CanvasRenderingContext2D & { letterSpacing: string }).letterSpacing =
      `${size * 0.08}px`;
  c.fillText("СКЛАД", w / 2, h * 0.54);
  c.restore();
}

export function drawCity(
  c: CanvasRenderingContext2D,
  t: Traffic,
  atlas: CanvasImageSource,
  smoke: Smoke,
  o: DrawOptions,
) {
  const spec = M.plates[o.plate];
  const time = t.time;
  const rigs = trafficRigs(t);
  const poses = rigs.map(rigPose);
  const focus =
    o.selected && o.selected !== "express"
      ? (o.selected as MapCarrierId)
      : undefined;
  const P = (q: Pt): Pt => [o.ox + q[0] * o.k, o.oy + q[1] * o.k];
  const m = o.k / spec.mpp;
  if (smoke.plate !== o.plate) {
    smoke.puffs.old.length = 0;
    smoke.puffs.old4.length = 0;
    smoke.plate = o.plate;
  }

  drawSign(c, spec, o);

  // Pick-up point at the dock doors, where an Express rig appears.
  const [ex, ey] = P(spec.express);

  // Selected loop: dashed route in the truck colour.
  if (focus) {
    const route = cityRoutes()[mapCarrierIds.indexOf(focus)];
    c.save();
    c.strokeStyle = carrierColors[focus];
    c.globalAlpha = 0.75;
    c.lineWidth = Math.max(2, 0.9 * m);
    c.lineCap = "round";
    c.setLineDash([Math.max(6, 2.6 * m), Math.max(5, 2.2 * m)]);
    c.lineDashOffset = -time * 8 * m;
    c.beginPath();
    route.pts.forEach(([x, y], i) => {
      const q = P(project(o.plate, x, y, 0.3));
      if (i) c.lineTo(q[0], q[1]);
      else c.moveTo(q[0], q[1]);
    });
    c.closePath();
    c.stroke();
    c.restore();
  }

  // Trucks, back to front.
  const order = mapCarrierIds
    .map((id, i) => ({
      id,
      i,
      p: poses[i],
      at: project(o.plate, poses[i].x, poses[i].y),
    }))
    .sort((a, b) => a.at[1] - b.at[1]);
  const exhausts: Partial<Record<MapCarrierId, Pt>> = {};
  for (const { id } of order) {
    const dim = !!focus && focus !== id;
    c.globalAlpha = dim ? 0.5 : 1;
    let jitter: Pt = [0, 0];
    if (id === "old4" && !o.reduced) {
      // Worn suspension: the yellow rig shudders a little.
      // Mostly a soft wobble, with a short jolt when the engine misfires.
      const beat = time % 3.4;
      const jolt = 0.35 + 1.2 * Math.max(0, 1 - beat / 0.45);
      jitter = [
        Math.sin(time * 11) * 0.35 * jolt,
        Math.sin(time * 17 + 1) * 0.6 * jolt,
      ];
    }
    const g = rigs[mapCarrierIds.indexOf(id)];
    const cover = occludersOf(o.plate, g);
    c.save();
    if (cover.length) {
      // Everything but the buildings in front: the rig drives behind them.
      c.beginPath();
      c.rect(0, 0, c.canvas.width, c.canvas.height);
      for (const poly of cover)
        poly.forEach((q, i) => {
          const [x, y] = P(q);
          if (i) c.lineTo(x, y);
          else c.moveTo(x, y);
        });
      c.clip("evenodd");
    }
    exhausts[id] = drawArticulated(c, atlas, spec, id, g, o, jitter);
    c.restore();
  }
  c.globalAlpha = 1;
  for (const id of ["old", "old4"] as const) {
    const at = exhausts[id];
    if (at && !o.reduced) emitSmoke(smoke, id, at, time);
    else if (at && smoke.puffs[id].length === 0) {
      // Reduced motion: a still plume behind the stack.
      for (let q = 0; q < 6; q++)
        smoke.puffs[id].push({
          x: at[0],
          y: at[1],
          born: time - q * 0.3,
          dark: false,
          big: false,
        });
    }
    c.globalAlpha = focus && focus !== id ? 0.4 : 1;
    drawSmoke(c, smoke, id, time, o, spec.mpp);
  }
  c.globalAlpha = 1;

  // Express is not a rig on the roads but a call (the DOM pill over the
  // dock). Once confirmed, a ripple spreads from the warehouse and a new
  // rig appears backed up to the doors.
  if (o.expressAge !== undefined) {
    const age = o.expressAge;
    const [W] = spec.res;
    if (age < 1.6) {
      c.strokeStyle = `rgba(0,87,184,${0.55 * (1 - age / 1.6)})`;
      c.lineWidth = Math.max(2, 1.4 * m);
      c.beginPath();
      c.arc(ex, ey, (1 - (1 - age / 1.6) ** 3) * W * 0.6 * o.k, 0, Math.PI * 2);
      c.stroke();
    }
    const glow = age < 0.9 ? Math.sin((age / 0.9) * Math.PI) : 0;
    if (glow > 0) {
      // A brief flash while the new rig arrives; nothing lingers after.
      const R = 18 * m;
      const g = c.createRadialGradient(ex, ey, 0, ex, ey, R);
      g.addColorStop(0, `rgba(255,248,210,${glow})`);
      g.addColorStop(1, "rgba(255,248,210,0)");
      c.fillStyle = g;
      c.beginPath();
      c.arc(ex, ey, R, 0, Math.PI * 2);
      c.fill();
    }
    const appear = Math.min(1, Math.max(0, (age - 0.35) / 0.6));
    if (appear > 0) {
      const sc =
        0.6 + 0.4 * (1 + 2.7 * (appear - 1) ** 3 + 1.7 * (appear - 1) ** 2);
      c.save();
      c.translate(ex, ey);
      c.scale(sc, sc);
      c.translate(-ex, -ey);
      c.globalAlpha = appear;
      // Backed up to the doors: cab faces the yard (south, -y).
      drawRig(c, atlas, spec, "express", spec.express, -Math.PI / 2, o);
      c.restore();
      c.globalAlpha = 1;
    }
    if (age < 2)
      for (let s = 0; s < 14; s++) {
        const a = (s / 14) * Math.PI * 2 + age * 1.8;
        const rad = (4 + (1 - (1 - age / 2) ** 3) * 18) * m;
        const fade = 1 - age / 2;
        if (fade > 0.04)
          sparkle(
            c,
            ex + Math.cos(a) * rad,
            ey + Math.sin(a) * rad * 0.7,
            ((1.1 + (s % 3) * 0.5) * m + 2) * fade,
            s % 2 ? "#ffd27a" : "#ffffff",
          );
      }
  }

  // Screen-space pins: constant size at any zoom.
  c.save();
  c.scale(o.dpr, o.dpr);
  const css = (q: Pt): Pt => [
    (o.ox + q[0] * o.k) / o.dpr,
    (o.oy + q[1] * o.k) / o.dpr,
  ];
  // Express is a call, not a rig: a branded pill under the dock doors whose
  // tail points at the doors where the new rig will appear. The DOM button
  // over it takes the tap; the canvas draws it under the rig pins, so a
  // passing rig stays tappable.
  if (o.pins && !o.selected) {
    const [sx, sy] = css(spec.express);
    expressCall(c, sx, sy, o.pinScale);
  }
  if (o.pins && !o.selected)
    rigs.forEach((g, index) => {
      // Anchored on the cab roof, so the pin rides with the tractor and
      // never floats over the swinging trailer.
      const [[cab]] = rigBoxes(g);
      const [sx, sy] = css(project(o.plate, cab.x, cab.y, 6.5));
      rigPin(c, mapCarrierIds[index], sx, sy - 2 * o.pinScale, o.pinScale);
    });
  // The warehouse is the centre of the map: one pill (cargo + "СКЛАД")
  // over the sign board, drawn above every rig pin. While the cargo waits
  // it bobs gently; after the choice it stays put.
  if (!o.selected || o.selected !== "express") {
    const [tl, tr, , bl] = spec.sign;
    const [x0, y0] = css(tl);
    const [x1, y1] = css(tr);
    const [x3, y3] = css(bl);
    const bob =
      o.selected || o.reduced ? 0 : Math.abs(Math.sin(time * 2.2)) * 2.5;
    depotPill(
      c,
      (x0 + x1) / 2 + (x3 - x0) * 0.2,
      (y0 + y1) / 2 + (y3 - y0) * 0.2,
      o.pinScale,
      bob,
    );
  }
  c.restore();
}

/** The Express call pill: tail tip at (x, y), body below it. */
export function expressCall(
  c: CanvasRenderingContext2D,
  x: number,
  y: number,
  s: number,
) {
  c.save();
  c.translate(Math.round(x), Math.round(y));
  c.scale(s, s);
  const h = 30;
  const top = 6;
  const brand = "Express";
  const action = "подобрать фуру";
  c.font = '800 13px "Roboto Condensed", Arial, sans-serif';
  const bw = c.measureText(brand).width;
  c.font = '500 13px "Roboto Condensed", Arial, sans-serif';
  const aw = c.measureText(action).width;
  const w = 4 + 22 + 6 + bw + 6 + aw + 12;
  const left = -w / 2;
  c.fillStyle = "rgba(10,30,50,0.25)";
  rr(c, left + 1, top + 3, w, h, h / 2);
  c.fill();
  c.fillStyle = "#0057b8";
  c.beginPath();
  c.moveTo(-6, top + 1);
  c.lineTo(0, 0);
  c.lineTo(6, top + 1);
  c.closePath();
  c.fill();
  rr(c, left, top, w, h, h / 2);
  c.fill();
  // orange disc with a white lightning bolt
  const ix = left + 4 + 11;
  const iy = top + h / 2;
  c.fillStyle = "#ff6a13";
  c.beginPath();
  c.arc(ix, iy, 11, 0, Math.PI * 2);
  c.fill();
  c.fillStyle = "#fff";
  c.beginPath();
  c.moveTo(ix + 1.6, iy - 7);
  c.lineTo(ix - 4.2, iy + 1);
  c.lineTo(ix - 0.4, iy + 1);
  c.lineTo(ix - 1.6, iy + 7);
  c.lineTo(ix + 4.2, iy - 1.2);
  c.lineTo(ix + 0.4, iy - 1.2);
  c.closePath();
  c.fill();
  c.textBaseline = "middle";
  c.textAlign = "left";
  c.font = '800 13px "Roboto Condensed", Arial, sans-serif';
  c.fillText(brand, ix + 11 + 6, iy + 0.5);
  c.globalAlpha = 0.92;
  c.font = '500 13px "Roboto Condensed", Arial, sans-serif';
  c.fillText(action, ix + 11 + 6 + bw + 6, iy + 0.5);
  c.restore();
}
