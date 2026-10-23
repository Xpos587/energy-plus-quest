import { renderToStaticMarkup } from "react-dom/server";
import { afterEach, expect, it, vi } from "vitest";
import { IllustratedCityMap } from "./IllustratedCityMap";

afterEach(() => vi.unstubAllGlobals());
it("retains usable static truck choices without requesting video on constrained mobile data", () => {
  vi.stubGlobal("navigator", {
    connection: { effectiveType: "3g", saveData: false },
  });
  const html = renderToStaticMarkup(<IllustratedCityMap onSelect={() => {}} />);
  expect(html).not.toContain("<video");
  expect(html).toContain("data-city-poster");
  expect(html).toContain("data-carrier-choice");
});
