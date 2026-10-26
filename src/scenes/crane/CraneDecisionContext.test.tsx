import { renderToStaticMarkup } from "react-dom/server";
import { expect, it } from "vitest";
import { scenarioParagraph } from "../../game/scenarioDocument";
import { CraneDecisionContext } from "./CraneDecisionContext";

it("restates the deadline, the 3 h wait and both operators without spoiling results", () => {
  const html = renderToStaticMarkup(<CraneDecisionContext />);
  expect(html).toContain("data-crane-decision-context");
  for (const fact of ["Баржа", "3 часа", "Иван", "Пётр"]) expect(html).toContain(fact);
  for (const resultId of ["27629778", "14753450", "77362BA7", "42344E38"])
    expect(html).not.toContain(scenarioParagraph(resultId));
});
