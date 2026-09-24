import type { CarrierId } from "./types";

export const MAP_LOOP = 96;
export const VEHICLE_UNIT = 14;
// Couple cargo over the tractor fifth wheel, leaving turning clearance behind the cab.
const HITCH_OFFSET = 2.1;
const TAU = Math.PI * 2;
const FPS = 60;
const N = MAP_LOOP * FPS;

type Route = {
  left: number;
  right: number;
  top: number;
  bottom: number;
  radius: number;
  width: number;
  length: number;
};
function route(
  left: number,
  right: number,
  top: number,
  bottom: number,
  radius: number,
): Route {
  return {
    left,
    right,
    top,
    bottom,
    radius,
    width: right - left,
    length: 2 * (right - left + bottom - top - 4 * radius) + TAU * radius,
  };
}
const routes = [
  route(287, 738, 85, 1030, 120),
  route(388, 608, 520, 850, 110),
  route(268, 1204, 130, 990, 130),
  route(697, 1158, 700, 1050, 140),
];
const trucks = (routes: Route[]) =>
  routes.map((r, index) => ({
    id: (["old", "near", "crew", "old4"] as const)[index] as Exclude<
      CarrierId,
      "express"
    >,
    route: r,
    laps: index === 0 ? 2 : 1,
    phase: [0.15, 0.4, 0.28, 0][index],
    speed: (r.length * (index === 0 ? 2 : 1)) / MAP_LOOP,
  }));
export const MAP_TRUCKS = trucks(routes);

function at(r: Route, distance: number) {
  let d = ((distance % r.length) + r.length) % r.length;
  const { left: l, right, top: t, bottom: b, radius: k } = r;
  const segments = [
    [l + k, t, 0, right - l - 2 * k, 0],
    [right - k, t + k, -Math.PI / 2, (k * Math.PI) / 2, 1],
    [right, t + k, Math.PI / 2, b - t - 2 * k, 0],
    [right - k, b - k, 0, (k * Math.PI) / 2, 1],
    [right - k, b, Math.PI, right - l - 2 * k, 0],
    [l + k, b - k, Math.PI / 2, (k * Math.PI) / 2, 1],
    [l, b - k, -Math.PI / 2, b - t - 2 * k, 0],
    [l + k, t + k, Math.PI, (k * Math.PI) / 2, 1],
  ];
  for (const [x, y, a, length, arc] of segments) {
    if (d <= length) {
      const angle = a + (arc ? d / k : 0);
      return arc
        ? {
            x: x + k * Math.cos(angle),
            y: y + k * Math.sin(angle),
            angle: angle + Math.PI / 2,
          }
        : { x: x + d * Math.cos(a), y: y + d * Math.sin(a), angle: a };
    }
    d -= length;
  }
  throw new Error("Invalid route distance");
}

export type TruckPose = {
  x: number;
  y: number;
  angle: number;
  steering: number;
  hitchX: number;
  hitchY: number;
  trailerAngle: number;
  markerX: number;
  markerY: number;
};
const buildTracks = (definitions: typeof MAP_TRUCKS) =>
  definitions.map((truck) => {
    const states: TruckPose[] = [];
    let trailerAngle = at(truck.route, truck.phase * truck.route.length).angle;
    let cabAngle = trailerAngle;
    let previousCab: { x: number; y: number } | undefined;
    let previous: { x: number; y: number } | undefined;
    // Settle the no-side-slip trailer before storing one periodic loop.
    for (let frame = -N * 4; frame <= N; frame++) {
      const routePose = at(
        truck.route,
        truck.route.length * (truck.phase + (frame / N) * truck.laps),
      );
      // Integrate the rear axle's no-side-slip constraint. Aligning the cab to
      // the path tangent makes its rear tires skid and steering snap at bends.
      if (previousCab) {
        const dx = routePose.x - previousCab.x, dy = routePose.y - previousCab.y;
        const turn = (angle: number) =>
          (dy * Math.cos(angle) - dx * Math.sin(angle)) / (2.1 * VEHICLE_UNIT);
        cabAngle += turn(cabAngle + turn(cabAngle) / 2);
      }
      previousCab = routePose;
      const slip = routePose.angle - cabAngle;
      const pose = { ...routePose, angle: cabAngle,
        steering: Math.atan2(2.87 * Math.sin(slip), 2.1 * Math.cos(slip)) };
      const hitchX =
        pose.x - Math.cos(pose.angle) * HITCH_OFFSET * VEHICLE_UNIT;
      const hitchY =
        pose.y - Math.sin(pose.angle) * HITCH_OFFSET * VEHICLE_UNIT;
      if (previous)
        trailerAngle +=
          ((hitchY - previous.y) * Math.cos(trailerAngle) -
            (hitchX - previous.x) * Math.sin(trailerAngle)) /
          (5.35 * VEHICLE_UNIT);
      previous = { x: hitchX, y: hitchY };
      if (frame >= 0)
        states.push({
          ...pose,
          hitchX,
          hitchY,
          trailerAngle,
          markerX: hitchX - Math.cos(trailerAngle) * 3.05 * VEHICLE_UNIT,
          markerY: hitchY - Math.sin(trailerAngle) * 3.05 * VEHICLE_UNIT,
        });
    }
    return states;
  });
const desktopTracks = buildTracks(MAP_TRUCKS);
const mixAngle = (a: number, b: number, t: number) =>
  a + Math.atan2(Math.sin(b - a), Math.cos(b - a)) * t;
export function mapFrame(seconds: number): TruckPose[] {
  const tracks = desktopTracks;
  const frame = (((seconds % MAP_LOOP) + MAP_LOOP) % MAP_LOOP) * FPS;
  const index = Math.floor(frame),
    t = frame - index;
  return tracks.map((track) => {
    const a = track[index],
      b = track[index + 1];
    const angle = mixAngle(a.angle, b.angle, t),
      trailerAngle = mixAngle(a.trailerAngle, b.trailerAngle, t);
    const x = a.x + (b.x - a.x) * t,
      y = a.y + (b.y - a.y) * t;
    const hitchX = x - Math.cos(angle) * HITCH_OFFSET * VEHICLE_UNIT,
      hitchY = y - Math.sin(angle) * HITCH_OFFSET * VEHICLE_UNIT;
    return {
      x,
      y,
      angle,
      steering: a.steering + (b.steering - a.steering) * t,
      hitchX,
      hitchY,
      trailerAngle,
      markerX: hitchX - Math.cos(trailerAngle) * 3.05 * VEHICLE_UNIT,
      markerY: hitchY - Math.sin(trailerAngle) * 3.05 * VEHICLE_UNIT,
    };
  });
}
export function exhaustPoint(pose: TruckPose) {
  const c = Math.cos(pose.angle), s = Math.sin(pose.angle);
  return { x: pose.x + (-.85 * c + .69 * s) * VEHICLE_UNIT,
    y: pose.y + (-.85 * s - .69 * c) * VEHICLE_UNIT };
}

// Pass08's bounded warm ink puffs, anchored to real birth poses instead of a
// four-second hand-tracked shot. The emission interval divides the loop exactly.
export function exhaustFrame(seconds: number, index: number) {
  if (index !== 0 && index !== 3) return [];
  const interval = .48, life = 1.35, offset = index * .12;
  const latest = Math.floor((seconds - offset) / interval);
  return [0, 1, 2].flatMap((i) => {
    const birth = (latest - i) * interval + offset, age = seconds - birth;
    if (age < 0 || age >= life) return [];
    const emitter = exhaustPoint(mapFrame(birth)[index]);
    return [{ birth, age, x: emitter.x + age * 18,
      y: emitter.y - age * 7, z: 3.1 + age * 1.3,
      radius: 3.8 + age * 6.5, alpha: .82 * (1 - age / life) }];
  });
}
// Same orthographic basis as the source camera (8,-100,120); y is southwards.
export function project(x: number, y: number, z = 0): [number, number] {
  return [
    0.996815 * x - 0.079745 * y,
    0.061174 * x + 0.764675 * y - 0.641439 * z * VEHICLE_UNIT,
  ];
}
function rectangle(
  x: number,
  y: number,
  angle: number,
  front: number,
  rear: number,
  halfWidth: number,
): [number, number][] {
  return [
    [front, halfWidth],
    [front, -halfWidth],
    [-rear, -halfWidth],
    [-rear, halfWidth],
  ].map(([u, v]) => [
    x + VEHICLE_UNIT * (u * Math.cos(angle) - v * Math.sin(angle)),
    y + VEHICLE_UNIT * (u * Math.sin(angle) + v * Math.cos(angle)),
  ]);
}
export function vehicleFootprints(pose: TruckPose) {
  return [
    rectangle(pose.x, pose.y, pose.angle, 1.65, 2.65, 1.13),
    rectangle(pose.hitchX, pose.hitchY, pose.trailerAngle, 0.75, 6.95, 0.94),
  ];
}
function trackBounds(tracks: TruckPose[][]) {
  const allPoints = tracks.flatMap((track) =>
    track
      .filter((_, i) => i % 6 === 0)
      .flatMap((pose) => [
        project(pose.markerX, pose.markerY, 3.3),
        ...vehicleFootprints(pose)
          .flat()
          .map(([x, y]) => project(x, y)),
      ]),
  );
  return [
    Math.min(...allPoints.map((p) => p[0])) - 4,
    Math.min(...allPoints.map((p) => p[1])) - 4,
    Math.max(...allPoints.map((p) => p[0])) + 4,
    Math.max(...allPoints.map((p) => p[1])) + 4,
  ];
}
const desktopBounds = trackBounds(desktopTracks);
export function mapFit(width: number, height: number) {
  const bounds = desktopBounds;
  const scale = Math.min(
    Math.max(1, width - 48) / (bounds[2] - bounds[0]),
    Math.max(1, height - 48) / (bounds[3] - bounds[1]),
  );
  return {
    scale,
    x: (width - (bounds[0] + bounds[2]) * scale) / 2,
    y: (height - (bounds[1] + bounds[3]) * scale) / 2,
  };
}
export function atlasHeading(angle: number) {
  return ((((-angle / TAU) * 72) % 72) + 72) % 72;
}
