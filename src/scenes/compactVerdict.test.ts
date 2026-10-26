import { expect, it } from "vitest";
import { compactScene } from "./compact";
import { compactVerdict } from "./ScenesGame";

it("ranks every Compact outcome against the best choice for the gift", () => {
  const tones = (parcel: "camera" | "socks" | "boat") => {
    const options = compactScene.options({ parcel, recipient: "alva", profile: "student" });
    return options.map((o) => compactVerdict(o.score, options.map((x) => x.score)).tone).join(",");
  };
  expect(tones("camera")).toBe("bad,fair,best,bad,best");
  expect(tones("socks")).toBe("bad,fair,best,bad,best");
  expect(tones("boat")).toBe("bad,bad,bad,best,best");
});
