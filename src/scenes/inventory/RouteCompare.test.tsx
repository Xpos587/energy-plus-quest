import { renderToStaticMarkup } from "react-dom/server";
import { expect, it } from "vitest";
import manifest from "../../../design/scene-03/v10/manifest-wide-outcomes.json";
import { RouteCompare, routeMetres } from "./RouteCompare";

it("uses the metres painted on the warehouse floor", () => {
  expect(routeMetres).toEqual(manifest.route_m);
});

it("lists every spot, marks the chosen one, and only auto-placement is both short and findable", () => {
  const html = renderToStaticMarkup(<RouteCompare parcel="socks" chosen="keeper" />);
  expect(html.match(/<tr data-chosen="true"[^>]*><th scope="row">([^<]+)/)?.[1]).toBe("Кладовщик");
  expect(html.match(/data-best="true"[^>]*><th scope="row">([^<]+)/)?.[1]).toBe("Автоподбор");
  expect(html).toContain("26 м");
  expect(html.match(/<tbody>.*<\/tbody>/)?.[0].match(/<tr/g)).toHaveLength(4);
});
