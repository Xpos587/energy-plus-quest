import { act } from "react";
import { createRoot } from "react-dom/client";
import { renderToStaticMarkup } from "react-dom/server";
import { expect, it, vi } from "vitest";
import { CraneZones } from "./CraneZones";

Object.assign(globalThis, { IS_REACT_ACT_ENVIRONMENT: true });

it.each(["rush", "wait"])("highlights one shared crane silhouette for %s", selectedId => {
  const host = document.createElement("div");
  host.innerHTML = renderToStaticMarkup(<CraneZones composition="wide" selectedId={selectedId} onSelect={() => {}} />);
  expect(host.querySelectorAll("[data-crane-zone]")).toHaveLength(3);
  expect(host.querySelectorAll('[data-crane-zone][data-active="true"]')).toHaveLength(1);
  expect(host.querySelector('[data-crane-zone="crane"]')?.getAttribute("data-active")).toBe("true");
  expect(host.querySelector("[tabindex], button")).toBeNull();
  expect(host.firstElementChild?.getAttribute("aria-hidden")).toBe("true");
});

it("focuses the numbered crane action without silently selecting rush", async () => {
  const host = document.createElement("div");
  document.body.append(host);
  const root = createRoot(host);
  const onSelect = vi.fn();
  try {
    await act(async () => root.render(<><button data-hotspot="rush">Outside</button><div data-world-plane><button data-hotspot="rush">1</button><button data-hotspot="wait">2</button><CraneZones composition="tall" onSelect={onSelect} /></div></>));
    const zone = host.querySelector('[data-crane-zone="crane"]');
    await act(async () => zone?.dispatchEvent(new MouseEvent("click", { bubbles: true })));
    expect(document.activeElement).toBe(host.querySelector('[data-world-plane] [data-hotspot="rush"]'));
    expect(onSelect).not.toHaveBeenCalled();
    for (const id of ["petr", "remote"]) {
      await act(async () => host.querySelector(`[data-crane-zone="${id}"]`)?.dispatchEvent(new MouseEvent("click", { bubbles: true })));
      expect(onSelect).toHaveBeenLastCalledWith(id);
    }
  } finally {
    await act(async () => root.unmount());
    host.remove();
  }
});

it("disables other silhouettes after selection while retaining the selected object", async () => {
  const host = document.createElement("div");
  const root = createRoot(host);
  const onSelect = vi.fn();
  try {
    await act(async () => root.render(<CraneZones composition="wide" selectedId="petr" onSelect={onSelect} />));
    for (const id of ["crane", "remote", "petr"]) {
      await act(async () => host.querySelector(`[data-crane-zone="${id}"]`)?.dispatchEvent(new MouseEvent("click", { bubbles: true })));
    }
    expect(onSelect).toHaveBeenCalledExactlyOnceWith("petr");
    expect(host.querySelector('[data-crane-zone="crane"]')?.getAttribute("data-interactive")).toBe("false");
    await act(async () => root.render(<CraneZones composition="wide" />));
    expect(host.querySelector('[data-crane-zone][data-interactive="true"]')).toBeNull();
  } finally {
    await act(async () => root.unmount());
  }
});
