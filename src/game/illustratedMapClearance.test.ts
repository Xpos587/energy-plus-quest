import { expect, it } from "vitest";
import {
  MAP_LOOP,
  mapFrame,
  project,
  VEHICLE_UNIT,
  vehicleFootprints,
} from "./illustratedMapMotion";

type Point = [number, number];
function overlap(a: Point[], b: Point[]) {
  for (const polygon of [a, b])
    for (let i = 0; i < polygon.length; i++) {
      const p = polygon[i],
        q = polygon[(i + 1) % polygon.length];
      const axis = [q[1] - p[1], p[0] - q[0]];
      const pa = a.map((v) => v[0] * axis[0] + v[1] * axis[1]),
        pb = b.map((v) => v[0] * axis[0] + v[1] * axis[1]);
      if (
        Math.max(...pa) <= Math.min(...pb) ||
        Math.max(...pb) <= Math.min(...pa)
      )
        return false;
    }
  return true;
}
// Ground footprints, not roof outlines: the latter are intentionally foreground occluders.
const buildings: Point[][] = [
  [
    [350, 220],
    [625, 239],
    [620, 332],
    [594, 379],
    [329, 355],
  ],
  [
    [751, 235],
    [854, 251],
    [852, 402],
    [735, 402],
  ],
  [
    [939, 280],
    [1059, 289],
    [1051, 397],
    [1025, 433],
    [921, 411],
  ],
  [
    [739, 466],
    [1027, 478],
    [1025, 519],
    [746, 506],
    [726, 496],
  ],
  [
    [721, 707],
    [999, 729],
    [994, 773],
    [974, 800],
    [714, 776],
    [702, 737],
  ],
];
const periphery: Point[][] = [
  [
    [0, 0],
    [218, 0],
    [173, 119],
    [154, 283],
    [151, 336],
    [116, 410],
    [0, 405],
  ],
  [
    [0, 405],
    [118, 415],
    [108, 565],
    [83, 744],
    [0, 775],
  ],
  [
    [1218, 180],
    [1400, 185],
    [1400, 933],
    [1184, 822],
    [1192, 562],
    [1195, 367],
  ],
];
const fences: Point[][] = [
  [
    [302, 335],
    [306, 335],
    [280, 678],
    [275, 678],
  ],
  [
    [275, 678],
    [280, 678],
    [278, 728],
    [273, 729],
  ],
  [
    [274, 728],
    [279, 725],
    [309, 747],
    [306, 752],
  ],
  [
    [307, 746],
    [550, 768],
    [549, 774],
    [306, 752],
  ],
  [
    [550, 768],
    [546, 765],
    [573, 718],
    [578, 720],
  ],
  [
    [573, 721],
    [578, 721],
    [581, 625],
    [575, 625],
  ],
  [
    [606, 548],
    [612, 549],
    [624, 362],
    [619, 362],
  ],
];

it("keeps cab/cargo, fences, building ground footprints and four trucks separate over the whole loop", () => {
  const failures: string[] = [];
  {
    const portrait = false;
    const obstacles = [...buildings, ...fences, ...periphery];
    for (let time = 0; time < MAP_LOOP; time += 1 / 12) {
      const poses = mapFrame(time);
      const bodies = poses.map(vehicleFootprints);
      for (let i = 0; i < 4; i++) {
        // Chassis overlaps the hitch by design; only the forward cab shell is a collision body.
        const [cab, cargo] = bodies[i];
        const pose = poses[i];
        const shell: Point[] = [
          [1.65, 1.13],
          [1.65, -1.13],
          [-0.88, -1.13],
          [-0.88, 1.13],
        ].map(([x, y]) => [
          pose.x +
            VEHICLE_UNIT *
              (x * Math.cos(pose.angle) - y * Math.sin(pose.angle)),
          pose.y +
            VEHICLE_UNIT *
              (x * Math.sin(pose.angle) + y * Math.cos(pose.angle)),
        ]);
        if (overlap(shell, cargo))
          failures.push(
            `${portrait ? "portrait" : "landscape"} t=${time.toFixed(2)} self=${i + 1}`,
          );
        for (const body of [cab, cargo]) {
          const projected = body.map(([x, y]) => project(x, y));
          for (let j = 0; j < obstacles.length; j++)
            if (overlap(projected, obstacles[j]))
              failures.push(
                `${portrait ? "portrait" : "landscape"} t=${time.toFixed(2)} truck=${i + 1} obstacle=${j}`,
              );
          for (let j = i + 1; j < 4; j++)
            for (const other of bodies[j])
              if (overlap(body, other))
                failures.push(
                  `${portrait ? "portrait" : "landscape"} t=${time.toFixed(2)} trucks=${i + 1}/${j + 1}`,
                );
        }
      }
    }
  }
  expect(failures.slice(0, 25), `${failures.length} collisions`).toEqual([]);
});
