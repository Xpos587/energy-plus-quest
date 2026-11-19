import { renderToStaticMarkup } from "react-dom/server";
import { expect, it } from "vitest";
import { scenarioParagraph } from "../../game/scenarioDocument";
import { lastmileScene, pipeCarrierResult } from "./index";
import { LastmileZones } from "./LastmileZones";
it("breathing rings remain separate at their maximum animated scale in both compositions", () => {
  for (const composition of ["wide", "tall"] as const) {
    const host = document.createElement("div");
    host.innerHTML = renderToStaticMarkup(<LastmileZones composition={composition} />);
    const rings = [...host.querySelectorAll("[data-lastmile-ripple]")].map(circle => ({
      cx: Number(circle.getAttribute("cx")), cy: Number(circle.getAttribute("cy")),
      radius: Number(circle.getAttribute("r")) * 1.15,
    }));
    expect(rings).toHaveLength(4);
    for (let i = 0; i < rings.length; i++) for (let j = i + 1; j < rings.length; j++) {
      const a = rings[i], b = rings[j];
      expect(a.radius).toBeGreaterThan(0);
      expect(Math.hypot(a.cx - b.cx, a.cy - b.cy)).toBeGreaterThan(a.radius + b.radius);
    }
  }
});
for (const recipient of ["alva","khor","arseniy"] as const) for (const parcel of ["boat","camera","socks"] as const) {
 it(`${recipient}/${parcel}: canonical options, remote delivery and rescue`,()=>{
  const context={profile:"student" as const,recipient,parcel};
  const options=lastmileScene.options(context);
  expect(options.map(o=>o.label)).toEqual(["2D9B5DEE","42123CE2","3B981493","4172314D"].map(id=>scenarioParagraph(id)));
  expect(options[0].result).toHaveLength(recipient==="arseniy"?1:2);
  expect(options[0].score.empathy).toBe(recipient==="arseniy"?0:-2);
  expect(options[3].result).toEqual([pipeCarrierResult]);
  const markup=renderToStaticMarkup(<lastmileScene.Art context={context} selectedId="pipe-carrier" showResult />);
  expect(markup).toContain('data-rescue="rover"');
  expect(markup).not.toContain('data-rescue="drone"');
  const choices=renderToStaticMarkup(<lastmileScene.Art context={context} showResult={false} onSelect={()=>{}} />);
  expect(choices.match(/data-hotspot=/g)).toHaveLength(4);
  expect(choices).not.toContain("data-lastmile-label");
 });
}
