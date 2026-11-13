import { act } from "react";
import { createRoot } from "react-dom/client";
import { expect, it, vi } from "vitest";
import { CraneArt } from "./CraneArt";
import * as consequence from "./consequence";

it("keeps the approved crane shell while adding one synchronized operator layer", async () => {
  vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);
  const decode = Object.getOwnPropertyDescriptor(HTMLImageElement.prototype, "decode");
  Object.defineProperty(HTMLImageElement.prototype, "decode", { configurable: true, value: () => Promise.resolve() });
  const beat = vi.spyOn(consequence, "craneBeat");
  const host = document.createElement("div"), root = createRoot(host);
  document.body.append(host);
  try {
    for (const operator of ["ivan", "petr"] as const) {
      beat.mockReturnValue({ ...consequence.craneRest, operator, frame: 9, cab: operator === "petr" ? "empty" : undefined });
      await act(async () => root.render(<CraneArt context={{ parcel: "camera", recipient: "alva", profile: "student" }} showResult playing={operator === "ivan" ? "rush" : "petr"} />));
      const shell = host.querySelector<HTMLImageElement>('[data-layer="top"] img')!;
      expect(shell.getAttribute("src")).toMatch(/\/top\.webp$/);
      const person = host.querySelectorAll<HTMLImageElement>('[data-layer="operator"] img');
      expect(person).toHaveLength(1);
      expect(person[0].getAttribute("src")).toMatch(new RegExp(`/top-${operator}\\.webp$`));
      expect(person[0].style.transform).toBe(shell.style.transform);
      expect(person[0].style.transform).toBe("translate(-25%, -50%)");
      const far = host.querySelector<HTMLImageElement>('[data-layer="far"]')!;
      expect(far.getAttribute("src")).toMatch(operator === "petr" ? /\/far-empty\.webp$/ : /\/far\.webp$/);
      expect(host.querySelector('[data-layer="cab"]')).toBeNull();
      expect(host.querySelector('[data-layer="pru"]')).not.toBeNull();
      expect(host.querySelector('[data-layer="ivan"]')).toBeNull();
    }
  } finally {
    await act(async () => root.unmount()); host.remove();
    vi.restoreAllMocks(); vi.unstubAllGlobals();
    if (decode) Object.defineProperty(HTMLImageElement.prototype, "decode", decode);
    else delete (HTMLImageElement.prototype as Partial<HTMLImageElement>).decode;
  }
});
