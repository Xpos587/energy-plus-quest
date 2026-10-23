import { renderToStaticMarkup } from "react-dom/server";
import { expect, it } from "vitest";
import { scenarioParagraph } from "../../game/scenarioDocument";
import { CraneDecisionContext } from "./CraneDecisionContext";

it("shows only the current decision context from the canonical scenario", () => {
  const source = scenarioParagraph("62451EC9");
  const expected = source.slice(source.indexOf(". ") + 2);
  const html = renderToStaticMarkup(<CraneDecisionContext />);

  expect(html).toContain("data-crane-decision-context");
  expect(html).toContain(`>${expected}</p>`);
  expect(html).toContain(scenarioParagraph("6F7BE91B"));
  for (const resultId of ["27629778", "14753450", "77362BA7"])
    expect(html).not.toContain(scenarioParagraph(resultId));
});
