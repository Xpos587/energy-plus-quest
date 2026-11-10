import { renderToStaticMarkup } from "react-dom/server";
import { expect, it } from "vitest";
import { scenarioParagraph } from "../../game/scenarioDocument";
import { CraneDecisionContext } from "./CraneDecisionContext";

it("restates the deadline and the empty crane without spoiling results", () => {
  const html = renderToStaticMarkup(<CraneDecisionContext />);
  expect(html).toContain("data-crane-decision-context");
  for (const fact of ["Баржа", "без машиниста"]) expect(html).toContain(fact);
  for (const resultId of ["27629778", "64BD7433", "77362BA7", "42344E38"])
    expect(html).not.toContain(scenarioParagraph(resultId));
});
