import { renderToStaticMarkup } from "react-dom/server";
import { expect, it } from "vitest";
import { scenarioParagraph } from "../../game/scenarioDocument";
import { craneScene } from "./index";
import { CraneDecisionContext } from "./CraneDecisionContext";

it("puts the whole scene story on the choice screen without spoiling results", () => {
  const intro = craneScene.intro({ parcel: "camera", recipient: "alva", profile: "student" });
  const html = renderToStaticMarkup(<CraneDecisionContext paragraphs={intro} />);
  expect(html).toContain("data-crane-decision-context");
  for (const text of intro) expect(html).toContain(text);
  for (const resultId of ["27629778", "64BD7433", "77362BA7", "42344E38"])
    expect(html).not.toContain(scenarioParagraph(resultId));
});
