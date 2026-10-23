import { describe, expect, it } from "vitest";
import {
  defaultLayout,
  parseLayout,
  saveLayout,
  readLayout,
  createHistory,
  commitHistory,
  undoHistory,
} from "./layout";
describe("Compact editor contract", () => {
  it("round trips saved independent badge and zone geometry", () => {
    const layout = structuredClone(defaultLayout);
    layout.profiles.portrait[0].badge.x += 40;
    saveLayout(localStorage, layout);
    expect(readLayout(localStorage).profiles.portrait[0].badge.x).toBe(
      layout.profiles.portrait[0].badge.x,
    );
    expect(readLayout(localStorage).profiles.portrait[0].zone.x).toBe(
      defaultLayout.profiles.portrait[0].zone.x,
    );
    localStorage.clear();
  });
  it("rejects malformed, nonfinite, missing and unsupported documents", () => {
    expect(() => parseLayout("{")).toThrow();
    expect(() =>
      parseLayout(JSON.stringify({ ...defaultLayout, version: 99 })),
    ).toThrow();
    const broken = structuredClone(defaultLayout);
    broken.profiles.wide[0].zone.width = -1;
    expect(() => parseLayout(JSON.stringify(broken))).toThrow();
    expect(() =>
      parseLayout(JSON.stringify({ ...defaultLayout, profiles: {} })),
    ).toThrow();
  });
  it("undo restores a full edit, including reset, without mutating earlier snapshots", () => {
    const previous = createHistory(defaultLayout);
    const next = structuredClone(defaultLayout);
    next.profiles.wide[1].badge.size = 32;
    const edited = commitHistory(previous, next);
    expect(undoHistory(edited).present).toEqual(defaultLayout);
    expect(previous.present.profiles.wide[1].badge.size).toBe(24);
    expect(undoHistory(commitHistory(edited, defaultLayout)).present).toEqual(
      next,
    );
  });
});
