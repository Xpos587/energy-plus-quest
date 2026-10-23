import { act } from "react";
import { createRoot } from "react-dom/client";
import { expect, it, vi } from "vitest";
import { SceneBriefing } from "./SceneBriefing";

it.each(["choosing", "reading"])(
  "keeps the route back action distinct from rereading the condition while %s",
  async (phase) => {
    vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);
    const host = document.createElement("div");
    document.body.append(host);
    const root = createRoot(host);
    const onBack = vi.fn();
    try {
      await act(async () =>
        root.render(
          <SceneBriefing
            title={`Возврат ${phase}`}
            paragraphs={["Первый абзац.", "Второй абзац."]}
            question="Что выберете?"
            onBack={onBack}
            initiallyOpen
          />,
        ),
      );
      const press = async (label: string) => {
        const button = [...host.querySelectorAll("button")].find(
          (el) => el.textContent === label,
        );
        if (!button) throw new Error(`Missing ${label}`);
        await act(async () => button.click());
      };
      await press("Далее");
      if (phase === "choosing") await press("К выбору");
      if (phase === "reading") {
        await press("Предыдущая страница");
        expect(onBack).not.toHaveBeenCalled();
      }
      await press("К выбору подарка");
      expect(onBack).toHaveBeenCalledTimes(1);
    } finally {
      await act(async () => root.unmount());
      host.remove();
      vi.unstubAllGlobals();
    }
  },
);

it("can return directly to choices and still reopen the full condition", async () => {
  vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);
  const host = document.createElement("div");
  document.body.append(host);
  const root = createRoot(host);
  try {
    await act(async () =>
      root.render(
        <SceneBriefing
          title="Повторный выбор"
          paragraphs={["Груз прибыл.", "Найдите подходящий транспорт."]}
          question="Какую машину выберете?"
          initiallyOpen={false}
        />,
      ),
    );
    expect(host.querySelector('[aria-label="Условие задания"]')).toBeNull();
    const condition = [...host.querySelectorAll("button")].find(
      (button) => button.textContent === "О задаче",
    );
    await act(async () => condition?.click());
    expect(
      host.querySelector('[data-testid="scene-intro"]')?.textContent,
    ).toContain("Груз прибыл.");
  } finally {
    await act(async () => root.unmount());
    host.remove();
    vi.unstubAllGlobals();
  }
});
