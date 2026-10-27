import { expect, it } from "vitest";
import { compactScene } from "./compact";
import { inventoryScene } from "./inventory";
import { lastmileScene } from "./lastmile";
import { rankChoice } from "./ScenesGame";
import type { SceneDefinition } from "./types";

const tones = (scene: SceneDefinition, parcel: "camera" | "socks" | "boat" = "camera", recipient: "alva" | "khor" | "arseniy" = "alva") => {
  const options = scene.options({ parcel, recipient, profile: "student" });
  return options.map((o) => rankChoice(o.score, options.map((x) => x.score))).join(",");
};

it("ranks every outcome against the best choice in its context", () => {
  expect(tones(compactScene, "camera")).toBe("bad,fair,best,bad,best");
  expect(tones(compactScene, "socks")).toBe("bad,fair,best,bad,best");
  expect(tones(compactScene, "boat")).toBe("bad,bad,bad,best,best");
  expect(tones(inventoryScene)).toBe("bad,bad,fair,best");
  expect(tones(lastmileScene)).toBe("bad,best,bad,bad");
  expect(tones(lastmileScene, "camera", "arseniy")).toBe("bad,best,bad,bad");
});
