import { renderToStaticMarkup } from "react-dom/server";
import { expect, it } from "vitest";
import { ChoiceInspection } from "./ChoiceInspection";

it("does not render a zero or an empty description for automatic selection", () => {
  const host = document.createElement("div");
  host.innerHTML = renderToStaticMarkup(
    <ChoiceInspection selectionKey="compact:auto" title="Автоматический подбор"
      paragraphs={[]} onConfirm={() => {}} onCancel={() => {}} />,
  );
  expect(host.textContent).not.toContain("0");
  expect(host.querySelector('[aria-label="Описание варианта"]')).toBeNull();
  expect(host.querySelector('[data-choice-confirm]')).not.toBeNull();
});

it("names preview cancellation as returning to options before an answer exists", () => {
  const host = document.createElement("div");
  host.innerHTML = renderToStaticMarkup(
    <ChoiceInspection selectionKey="inventory:keeper" title="Опытный кладовщик"
      onConfirm={() => {}} onCancel={() => {}} />,
  );
  expect(host.querySelector('[data-choice-cancel]')?.textContent).toBe(
    "К вариантам",
  );
  expect(
    host.querySelector('[aria-label="Закрыть описание варианта"]'),
  ).toBeNull();
});
