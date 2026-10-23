import { describe, expect, it } from "vitest";
import { carrierMotionFraction } from "./carrierTracking";

describe("animation pace", () => {
  it("changes with the blue truck motion rather than a fixed carrier fact", () => {
    const values = Array.from({ length: 128 }, (_, i) =>
      carrierMotionFraction(i / 2, 1),
    );
    expect(Math.max(...values) - Math.min(...values)).toBeGreaterThan(0.2);
    expect(
      values.every(
        (value) => Number.isFinite(value) && value >= 0 && value <= 1,
      ),
    ).toBe(true);
  });
  it("uses a periodic shared scale without a discontinuity at the video seam", () => {
    for (let truck = 0; truck < 4; truck++) {
      expect(carrierMotionFraction(3, truck)).toBe(
        carrierMotionFraction(67, truck),
      );
      expect(
        Math.abs(
          carrierMotionFraction(63.999, truck) -
            carrierMotionFraction(0, truck),
        ),
      ).toBeLessThan(0.05);
    }
  });
});
