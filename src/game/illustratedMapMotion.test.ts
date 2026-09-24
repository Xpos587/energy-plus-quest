import { describe, expect, it } from "vitest";
import {
  atlasHeading,
  exhaustFrame,
  exhaustPoint,
  VEHICLE_UNIT,
  MAP_LOOP,
  MAP_TRUCKS,
  mapFit,
  mapFrame,
  project,
  vehicleFootprints,
} from "./illustratedMapMotion";

describe("illustrated scene1 motion", () => {
  it("samples headings continuously across adjacent views and the wrap", () => {
    expect(atlasHeading(-Math.PI / 72)).toBeCloseTo(0.5);
    expect(atlasHeading(Math.PI / 72)).toBeCloseTo(71.5);
    for (let angle = -8; angle < 8; angle += 0.01) {
      const delta = atlasHeading(angle + 0.001) - atlasHeading(angle);
      expect(Math.abs(((delta + 108) % 72) - 36)).toBeCloseTo(
        (0.001 * 72) / (2 * Math.PI),
        8,
      );
    }
  });
  it("keeps four identities, different old speeds, near slowest and crew on the outer route", () => {
    expect(MAP_TRUCKS.map((truck) => truck.id)).toEqual([
      "old",
      "near",
      "crew",
      "old4",
    ]);
    const speeds = MAP_TRUCKS.map((truck) => truck.speed);
    expect(speeds[1]).toBeLessThan(Math.min(speeds[0], speeds[2], speeds[3]));
    expect(speeds[0]).toBeGreaterThan(speeds[3]);
    expect(MAP_TRUCKS[2].route.width).toBeGreaterThan(
      MAP_TRUCKS[0].route.width,
    );
  });
  it("rolls rear tractor and trailer axles without lateral skidding and steers continuously", () => {
    for (let time = 0; time < MAP_LOOP; time += .1) {
      const a = mapFrame(time), b = mapFrame(time + .005);
      for (let i = 0; i < 4; i++) {
        for (const [offset, trailer] of [[2.1, false], [5.35, true]] as const) {
          const axle = (pose: typeof a[number]) => {
            const angle = trailer ? pose.trailerAngle : pose.angle;
            return { angle, x: (trailer ? pose.hitchX : pose.x) - Math.cos(angle) * offset * VEHICLE_UNIT,
              y: (trailer ? pose.hitchY : pose.y) - Math.sin(angle) * offset * VEHICLE_UNIT };
          };
          const p = axle(a[i]), q = axle(b[i]);
          const lateral = -(q.x - p.x) * Math.sin(p.angle) + (q.y - p.y) * Math.cos(p.angle);
          expect(Math.abs(lateral) / .005).toBeLessThan(.25);
        }
        const front = (pose: typeof a[number]) => ({
          x: pose.x + Math.cos(pose.angle) * .77 * VEHICLE_UNIT,
          y: pose.y + Math.sin(pose.angle) * .77 * VEHICLE_UNIT,
        });
        const p = front(a[i]), q = front(b[i]);
        const wheelAngle = a[i].angle + a[i].steering;
        expect(Math.abs(-(q.x-p.x)*Math.sin(wheelAngle)+(q.y-p.y)*Math.cos(wheelAngle))/.005).toBeLessThan(.3);
        expect(Math.abs(a[i].steering)).toBeLessThan(.5);
        expect(Math.abs(b[i].steering - a[i].steering)).toBeLessThan(.01);
      }
    }
  });
  it("emits visible bounded smoke from old cab birth positions, never from clean trucks", () => {
    for (let time = 0; time < MAP_LOOP; time += .13) {
      for (const index of [0, 3]) {
        const puffs = exhaustFrame(time, index);
        expect(puffs.length).toBeGreaterThanOrEqual(2);
        expect(puffs.length).toBeLessThanOrEqual(3);
        expect(Math.max(...puffs.map(puff => puff.alpha))).toBeGreaterThan(.5);
        for (const puff of puffs) {
          const birth = exhaustPoint(mapFrame(puff.birth)[index]);
          expect(puff.x).toBeCloseTo(birth.x + puff.age * 18);
          expect(puff.y).toBeCloseTo(birth.y - puff.age * 7);
          expect(puff.radius).toBeLessThan(13);
        }
      }
      expect(exhaustFrame(time, 1)).toEqual([]);
      expect(exhaustFrame(time, 2)).toEqual([]);
    }
    for (const index of [0, 3]) {
      const start = exhaustFrame(0, index), end = exhaustFrame(MAP_LOOP, index);
      start.forEach((puff, i) => {
        expect(end[i].x).toBeCloseTo(puff.x, 6);
        expect(end[i].y).toBeCloseTo(puff.y, 6);
        expect(end[i].alpha).toBeCloseTo(puff.alpha, 6);
      });
    }
  });
  it("closes every cab and articulated trailer without a loop jump", () => {
    for (let i = 0; i < 4; i++) {
      const start = mapFrame(0)[i];
      const end = mapFrame(MAP_LOOP - 0.0001)[i];
      expect(Math.hypot(start.x - end.x, start.y - end.y)).toBeLessThan(0.02);
      expect(Math.sin(start.trailerAngle - end.trailerAngle)).toBeCloseTo(0, 3);
    }
  });
  it("fits full vehicle envelopes and moving 44px pick positions for every composition", () => {
    for (const [width, height] of [
      [320, 380],
      [390, 520],
      [820, 870],
      [1080, 850],
      [650, 245],
    ]) {
      const fit = mapFit(width, height);
      for (let t = 0; t < MAP_LOOP; t += 0.25) {
        for (const truck of mapFrame(t)) {
          const [px, py] = project(truck.markerX, truck.markerY, 3.3);
          expect(px * fit.scale + fit.x).toBeGreaterThanOrEqual(22);
          expect(px * fit.scale + fit.x).toBeLessThanOrEqual(width - 22);
          expect(py * fit.scale + fit.y).toBeGreaterThanOrEqual(22);
          expect(py * fit.scale + fit.y).toBeLessThanOrEqual(height - 22);
          for (const polygon of vehicleFootprints(truck))
            for (const [x, y] of polygon) {
              const [sx, sy] = project(x, y);
              expect(sx * fit.scale + fit.x).toBeGreaterThanOrEqual(0);
              expect(sx * fit.scale + fit.x).toBeLessThanOrEqual(width);
              expect(sy * fit.scale + fit.y).toBeGreaterThanOrEqual(0);
              expect(sy * fit.scale + fit.y).toBeLessThanOrEqual(height);
            }
        }
      }
    }
  });
});
