import { renderToStaticMarkup } from "react-dom/server";
import { expect, it } from "vitest";
import { scenarioParagraph } from "../../game/scenarioDocument";
import { lastmileScene } from "./index";
for (const recipient of ["alva","khor","arseniy"] as const) for (const parcel of ["boat","camera","socks"] as const) {
 it(`${recipient}/${parcel}: canonical options, remote delivery and rescue`,()=>{
  const context={profile:"student" as const,recipient,parcel};
  const options=lastmileScene.options(context);
  expect(options.map(o=>o.label)).toEqual(["2D9B5DEE","42123CE2","3B981493","4172314D"].map(id=>scenarioParagraph(id)));
  expect(options[0].result).toHaveLength(recipient==="arseniy"?1:2);
  expect(options[0].score.empathy).toBe(recipient==="arseniy"?0:-2);
  expect(options[3].result).toEqual([scenarioParagraph("4E705130"),scenarioParagraph("7F6FF7ED")]);
  const markup=renderToStaticMarkup(<lastmileScene.Art context={context} selectedId="pipe-carrier" showResult />);
  expect(markup).toContain('data-rescue="rover"');
  expect(markup).not.toContain('data-rescue="drone"');
  const choices=renderToStaticMarkup(<lastmileScene.Art context={context} showResult={false} onSelect={()=>{}} />);
  expect(choices.match(/data-hotspot=/g)).toHaveLength(4);
 });
}
