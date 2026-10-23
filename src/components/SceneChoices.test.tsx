import { act } from "react";
import { createRoot } from "react-dom/client";
import { expect, it, vi } from "vitest";
import { SceneChoices } from "./SceneChoices";

it("exposes every option equally and only requests inspection when clicked", async () => {
  const host = document.createElement("div");
  document.body.append(host);
  const root = createRoot(host);
  const onInspect = vi.fn();
  const options = [
    { id: "first", label: "Первый вариант" },
    { id: "second", label: "Второй вариант" },
    { id: "auto", label: "Поручить системе" },
  ];
  try {
    await act(async () => root.render(<SceneChoices options={options} onInspect={onInspect} />));
    const buttons = [...host.querySelectorAll<HTMLButtonElement>("[data-scene-choice]")];
    expect(buttons.map(button => button.lastElementChild?.textContent)).toEqual(options.map(option => option.label));
    expect(buttons.map(button => button.querySelector('[aria-hidden="true"]')?.textContent)).toEqual(["1", "2", "3"]);
    expect(buttons.every(button => !button.hasAttribute("aria-haspopup"))).toBe(true);
    expect(onInspect).not.toHaveBeenCalled();
    for (const [index, button] of buttons.entries()) {
      await act(async () => button.click());
      expect(onInspect).toHaveBeenNthCalledWith(index + 1, options[index].id);
    }
    expect(host.querySelector("[data-choice-confirm], [data-result]")).toBeNull();
    expect(buttons.every(button => button.getAttribute("aria-pressed") === "false")).toBe(true);
    await act(async () => root.render(<SceneChoices options={options} onInspect={onInspect} numbered={false} />));
    expect([...host.querySelectorAll("[data-scene-choice]")].map(button => button.textContent)).toEqual(options.map(option => option.label));
    expect(host.querySelector('[aria-hidden="true"]')).toBeNull();
  } finally {
    await act(async () => root.unmount());
    host.remove();
  }
});
