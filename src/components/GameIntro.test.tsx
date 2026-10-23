import { act } from "react";
import { createRoot } from "react-dom/client";
import { afterEach, expect, it, vi } from "vitest";
import { App } from "../App";
import { GameIntro } from "./GameIntro";
import { scenarioParagraph } from "../game/scenarioDocument";

const mounts: Array<() => void> = [];
afterEach(async () => { for (const dispose of mounts.splice(0)) await act(dispose); localStorage.clear(); vi.unstubAllGlobals(); });
async function render(element: React.ReactNode, compact = false) {
  vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);
  vi.stubGlobal("matchMedia", () => ({ matches: compact, addEventListener() {}, removeEventListener() {} }));
  const host = document.createElement("div"); document.body.append(host);
  const root = createRoot(host); mounts.push(() => { root.unmount(); host.remove(); });
  await act(async () => root.render(element)); return host;
}
it("keeps canonical exposition in two mobile states before starting", async () => {
  const start = vi.fn(); const host = await render(<GameIntro onStart={start} />, true);
  if (host.querySelector("[data-intro-enter]")) await act(async () => host.querySelector<HTMLButtonElement>("[data-intro-enter]")!.click());
  expect(host.textContent).toContain(scenarioParagraph("24D093EF"));
  expect(host.textContent).toContain(scenarioParagraph("42DF6085"));
  expect(host.textContent).not.toContain(scenarioParagraph("38763B42"));
  expect(host.textContent).not.toContain(scenarioParagraph("4C9AA992"));
  await act(async () => host.querySelector<HTMLButtonElement>('[data-intro-next]')!.click());
  expect(start).not.toHaveBeenCalled();
  expect(host.textContent).toContain(scenarioParagraph("38763B42"));
  expect(host.querySelectorAll("li")).toHaveLength(3);
  expect(host.textContent).toContain("экономите ресурсы");
  expect(host.textContent).toContain("проявляете заботу");
  expect(host.textContent).toContain("принимаете наиболее эффективные решения");
  expect(host.textContent).not.toContain(scenarioParagraph("24D093EF"));
  if (host.querySelector('[data-intro-next]')) await act(async () => host.querySelector<HTMLButtonElement>('[data-intro-next]')!.click());
  await act(async () => host.querySelector<HTMLButtonElement>('[data-intro-start]')!.click());
  expect(start).toHaveBeenCalledOnce();
});
it("reveals the same metric explanation progressively on desktop", async () => {
  const host = await render(<GameIntro onStart={() => {}} />);
  if (host.querySelector("[data-intro-enter]")) await act(async () => host.querySelector<HTMLButtonElement>("[data-intro-enter]")!.click());
  expect(host.textContent).toContain(scenarioParagraph("24D093EF"));
  expect(host.querySelector("li")).toBeNull();
  await act(async () => host.querySelector<HTMLButtonElement>('[data-intro-next]')!.click());
  expect(host.querySelectorAll("li")).toHaveLength(3);
  expect(host.querySelector("h1")?.textContent).toBe("Доставляем радость");
  expect(host.textContent).toContain(scenarioParagraph("38763B42"));
});
it("introduces a fresh game before profile and remembers dismissal after reload", async () => {
  let host = await render(<App />);
  expect(host.querySelector('[data-intro-enter]')).not.toBeNull();
  await act(async () => host.querySelector<HTMLButtonElement>('[data-intro-enter]')!.click());
  if (host.querySelector('[data-intro-next]')) await act(async () => host.querySelector<HTMLButtonElement>('[data-intro-next]')!.click());
  await act(async () => host.querySelector<HTMLButtonElement>('[data-intro-start]')!.click());
  expect(host.textContent).toContain("Студент");
  expect(host.textContent).not.toContain("нажмите на вариант");
  host = await render(<App />);
  expect(host.querySelector('[data-intro-start]')).toBeNull();
  expect(host.textContent).toContain("Профессионал");
});

it("returns from sender selection to the introduction and resumes preparation", async () => {
  window.scrollTo = vi.fn();
  const host = await render(<App />);
  await act(async () => host.querySelector<HTMLButtonElement>('[data-intro-enter]')!.click());
  if (host.querySelector('[data-intro-next]')) await act(async () => host.querySelector<HTMLButtonElement>('[data-intro-next]')!.click());
  await act(async () => host.querySelector<HTMLButtonElement>('[data-intro-start]')!.click());
  expect(host.querySelector("h1")?.textContent).toBe("Кто отправит подарок?");
  const back = Array.from(host.querySelectorAll("button")).find(button => button.textContent?.trim() === "Назад")!;
  await act(async () => back.click());
  expect(host.querySelector("h1")?.textContent).toBe("Доставляем радость");
  await act(async () => host.querySelector<HTMLButtonElement>('[data-intro-enter]')!.click());
  await act(async () => host.querySelector<HTMLButtonElement>('[data-intro-next]')!.click());
  expect(host.querySelectorAll("li")).toHaveLength(3);
  expect(host.textContent).toContain("экономите ресурсы");
  expect(host.textContent).toContain("проявляете заботу");
  expect(host.textContent).toContain("принимаете наиболее эффективные решения");
  if (host.querySelector('[data-intro-next]')) await act(async () => host.querySelector<HTMLButtonElement>('[data-intro-next]')!.click());
  await act(async () => host.querySelector<HTMLButtonElement>('[data-intro-start]')!.click());
  expect(host.querySelector("h1")?.textContent).toBe("Кто отправит подарок?");
  await act(async () => host.querySelector<HTMLButtonElement>('[data-choice="student"]')!.click());
  expect(host.querySelector("h1")?.textContent).toBe("Кому отправим подарок?");
  await act(async () => Array.from(host.querySelectorAll("button")).find(button => button.textContent?.trim() === "Назад")!.click());
  await act(async () => Array.from(host.querySelectorAll("button")).find(button => button.textContent?.trim() === "Назад")!.click());
  expect(host.querySelector("h1")?.textContent).toBe("Доставляем радость");
});

it("shows all metric meanings without extra controls before starting", async () => {
  const start = vi.fn();
  const host = await render(<GameIntro onStart={start} />);
  expect(host.querySelector('img[src*="opening/dispatch-v1.png"]')).toBeNull();
  await act(async () => host.querySelector<HTMLButtonElement>('[data-intro-enter]')!.click());
  await act(async () => host.querySelector<HTMLButtonElement>('[data-intro-next]')!.click());
  const meanings = Array.from(host.querySelectorAll<HTMLElement>('li span'));
  expect(meanings.map(node => node.textContent)).toEqual([
    "экономите ресурсы", "проявляете заботу", "принимаете наиболее эффективные решения",
  ]);
  for (const meaning of meanings) expect(meaning.closest('[hidden]')).toBeNull();
  expect(host.querySelector('button[aria-controls^="intro-metric-"]')).toBeNull();
  expect(start).not.toHaveBeenCalled();
  expect(host.querySelector<HTMLButtonElement>('[data-intro-start]')!.disabled).toBe(false);
  await act(async () => host.querySelector<HTMLButtonElement>('[data-intro-start]')!.click());
  expect(start).toHaveBeenCalledOnce();
});

it("opens the approved illustrated cover before both authored briefings and returns to it", async () => {
  const start = vi.fn();
  const host = await render(<GameIntro onStart={start} />);
  expect(host.querySelector('[data-intro-enter]')).not.toBeNull();
  expect(host.querySelector('img[src*="choice-final-wide-v10"]')).not.toBeNull();
  expect(host.textContent).not.toContain(scenarioParagraph("24D093EF"));
  await act(async () => host.querySelector<HTMLButtonElement>('[data-intro-enter]')!.click());
  expect(host.textContent).toContain(scenarioParagraph("24D093EF"));
  await act(async () => Array.from(host.querySelectorAll('button')).find(button => button.textContent?.trim() === 'Назад')!.click());
  expect(host.querySelector('[data-intro-enter]')).not.toBeNull();
  expect(start).not.toHaveBeenCalled();
});
