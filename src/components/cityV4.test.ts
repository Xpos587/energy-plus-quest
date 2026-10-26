import { describe, expect, it } from "vitest";
import { carrierFacts, mapCarrierIds } from "../game/carrierFacts";
import {
  cityRoutes,
  createTraffic,
  landmark,
  lapSpeed,
  MPS_PER_KMH,
  plateFor,
  plates,
  project,
  RIG,
  rigBoxes,
  rigsTouch,
  rattle,
  sputter,
  stepTraffic,
  trafficFrame,
  trafficRigs,
  truckSpeed,
} from "./cityV4";

function simulate(
  seconds: number,
  onFrame?: (t: ReturnType<typeof createTraffic>) => void,
) {
  const t = createTraffic();
  for (let f = 0; f < seconds * 30; f++) {
    stepTraffic(t, 1 / 30);
    onFrame?.(t);
  }
  return t;
}

describe("scene 1 city v4", () => {
  it("drives each rig at its carrierFacts speed, in the required order", () => {
    for (const id of mapCarrierIds)
      expect(truckSpeed(id)).toBeCloseTo(
        carrierFacts[id].citySpeedKmh * 0.55,
        5,
      );
    // The map drives the timetable; carrierFacts holds it rounded to km/h.
    for (const r of cityRoutes())
      expect(
        Math.abs(lapSpeed(r) / MPS_PER_KMH - carrierFacts[r.id].citySpeedKmh),
      ).toBeLessThan(0.5);
    expect(truckSpeed("crew")).toBeGreaterThan(truckSpeed("old4"));
    expect(truckSpeed("old4")).toBeGreaterThan(truckSpeed("near"));
  });

  it("shows the three rigs with distinct outcomes; the red one is off the map", () => {
    expect([...mapCarrierIds]).toEqual(["near", "crew", "old4"]);
  });

  it("gives the green crew the widest loop and keeps the blue rig by the warehouse", () => {
    const len = Object.fromEntries(cityRoutes().map((r) => [r.id, r.length]));
    expect(len.crew).toBeGreaterThan(Math.max(len.old4, len.near));
    expect(len.near).toBeLessThan(len.old4);
    for (const name of ["wide", "tall"] as const) {
      const [wx, wy] = landmark(name, "warehouse");
      simulate(30, (t) => {
        const [x, y] = trafficFrame(t, name)[mapCarrierIds.indexOf("near")];
        expect(
          Math.hypot(
            (x - wx) * plates[name].res[0],
            (y - wy) * plates[name].res[1],
          ) * plates[name].mpp,
        ).toBeLessThan(75);
      });
    }
  });

  it("never lets two rigs come within 1.5 m, tractors and trailers included", () => {
    let hits = 0;
    // Two full timetable cycles (the blue lap is 1.5 green laps).
    simulate(160, (t) => {
      const p = trafficRigs(t);
      for (let a = 0; a < p.length; a++)
        for (let b = a + 1; b < p.length; b++)
          if (rigsTouch(p[a], p[b], 1.5)) hits++;
    });
    expect(hits).toBe(0);
  });

  it("articulates in corners: the trailer swings, the hitch stays joined", () => {
    let maxBend = 0;
    simulate(60, (t) => {
      for (const g of trafficRigs(t)) {
        const bend = Math.abs(
          ((g.tractor - g.trailer + 3 * Math.PI) % (2 * Math.PI)) - Math.PI,
        );
        maxBend = Math.max(maxBend, bend);
        // the trailer box starts right behind the hitch
        const [, [trl, hl]] = rigBoxes(g);
        const nose = [
          trl.x + Math.cos(trl.heading) * hl,
          trl.y + Math.sin(trl.heading) * hl,
        ];
        expect(
          Math.hypot(nose[0] - g.kingpin[0], nose[1] - g.kingpin[1]),
        ).toBeCloseTo(RIG.trailerFront - RIG.kingpin, 1);
        expect(bend).toBeLessThan(Math.PI / 2);
      }
    });
    expect(maxBend).toBeGreaterThan(0.5);
  });

  it("drives smoothly: constant speed, no stops, no jumps in heading", () => {
    const t = createTraffic();
    const routes = cityRoutes();
    let prev = [...t.s];
    let heads = trafficRigs(t).map((g) => g.tractor);
    for (let f = 0; f < 60 * 30; f++) {
      stepTraffic(t, 1 / 30);
      const rigs = trafficRigs(t);
      t.s.forEach((s, i) => {
        const moved = (s - prev[i] + routes[i].length) % routes[i].length;
        expect(moved).toBeCloseTo(lapSpeed(routes[i]) / 30, 6);
        const turn = Math.abs(
          ((rigs[i].tractor - heads[i] + 3 * Math.PI) % (2 * Math.PI)) -
            Math.PI,
        );
        // Never sharper than the ~8.5 m minimum radius of routes.py.
        expect(turn).toBeLessThan(lapSpeed(routes[i]) / 30 / 8);
      });
      prev = [...t.s];
      heads = rigs.map((g) => g.tractor);
    }
  });

  it("keeps every rig inside the safe area of both plates", () => {
    for (const name of ["wide", "tall"] as const) {
      const [u0, v0, u1, v1] = plates[name].keep;
      simulate(120, (t) => {
        for (const [x, y] of trafficFrame(t, name)) {
          expect(x).toBeGreaterThan(u0 - 0.02);
          expect(x).toBeLessThan(u1 + 0.02);
          expect(y).toBeGreaterThan(v0 - 0.02);
          expect(y).toBeLessThan(v1 + 0.02);
        }
      });
    }
  });

  it("parks the express rig at the dock doors", () => {
    for (const name of ["wide", "tall"] as const) {
      const [dx, dy] = plates[name].dock;
      const [ex, ey] = plates[name].express;
      expect(Math.hypot(ex - dx, ey - dy) * plates[name].mpp).toBeLessThan(20);
    }
  });

  it("projects world metres onto each plate consistently", () => {
    const [x, y] = cityRoutes()[0].pts[0];
    for (const name of ["wide", "tall"] as const) {
      const [px, py] = project(name, x, y);
      expect(px).toBeGreaterThan(0);
      expect(px).toBeLessThan(plates[name].res[0]);
      expect(py).toBeGreaterThan(0);
      expect(py).toBeLessThan(plates[name].res[1]);
    }
    expect(plateFor(1440, 900)).toBe("wide");
    expect(plateFor(390, 844)).toBe("tall");
    expect(plateFor(320, 310)).toBe("tall");
  });

  it("makes the yellow rig sputter: gaps, puffs and a dark backfire", () => {
    const samples = Array.from({ length: 340 }, (_, k) => sputter(k / 100));
    expect(samples.some((s) => !s.on)).toBe(true);
    expect(samples.some((s) => s.on && !s.dark)).toBe(true);
    expect(samples.some((s) => s.dark)).toBe(true);
  });

  it("rattles the yellow rig hardest right after the backfire", () => {
    const lift = (t: number) => -rattle(t).cab[1];
    const peak = Math.max(
      ...Array.from({ length: 20 }, (_, k) => lift(k / 100)),
    );
    const calm = Math.max(
      ...Array.from({ length: 20 }, (_, k) => lift(2 + k / 100)),
    );
    expect(peak).toBeGreaterThan(0.5); // metres: a visible kick
    expect(calm).toBeLessThan(0.3); // between misfires only the idle buzz
    expect(sputter(0.05).dark).toBe(true); // same beat as the dark puff
  });
});
