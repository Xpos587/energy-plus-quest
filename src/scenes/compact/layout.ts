export type LayoutProfile = "wide" | "portrait" | "unloaded";
export type LayoutZone = {
  x: number;
  y: number;
  width: number;
  height: number;
};
export type LayoutBadge = { x: number; y: number; size: number };
export type LayoutPlace = {
  id: string;
  number: number;
  zone: LayoutZone;
  badge: LayoutBadge;
};
export type LogoId = "energy" | "company";
export type LogoAdjustment = { dx: number; dy: number; scale: number };
export type CompactLayout = {
  version: 1;
  profiles: Record<LayoutProfile, LayoutPlace[]>;
  logos: Record<"mobile" | "desktop", Record<LogoId, LogoAdjustment>>;
};
const places = (rects: number[][]): LayoutPlace[] =>
  rects.map(([x, y, width, height], i) => ({
    id: `place-${i + 1}`,
    number: i + 1,
    zone: { x, y, width, height },
    badge: { x, y, size: 24 },
  }));
export const defaultLayout: CompactLayout = {
  version: 1,
  profiles: {
    wide: places([
      [68, 94, 372, 94],
      [269, 194, 166, 36],
      [450, 94, 99, 35],
      [686, 94, 110, 221],
    ]),
    portrait: places([
      [68, 328, 372, 94],
      [269, 428, 166, 36],
      [448, 328, 106, 34],
      [686, 328, 115, 220],
    ]),
    unloaded: places([
      [64, 289, 148, 45],
      [218, 289, 200, 130],
      [439, 289, 105, 36],
      [678, 289, 113, 203],
    ]),
  },
  logos: {
    mobile: {
      energy: { dx: 0, dy: 0, scale: 1 },
      company: { dx: 0, dy: 0, scale: 1 },
    },
    desktop: {
      energy: { dx: 0, dy: 0, scale: 1 },
      company: { dx: 0, dy: 0, scale: 1 },
    },
  },
};
export const layoutStorageKey = "compact-layout-v1";
export const draftStorageKey = "compact-layout-draft-v1";
export function parseLayout(text: string): CompactLayout {
  const value = JSON.parse(text);
  const finite = (n: unknown, min: number, max: number) =>
    typeof n === "number" && Number.isFinite(n) && n >= min && n <= max;
  if (value?.version !== 1)
    throw Error("Неподдерживаемая версия координат. Нужна версия 1.");
  for (const profile of ["wide", "portrait", "unloaded"] as const) {
    const entries = value.profiles?.[profile];
    if (!Array.isArray(entries) || entries.length !== 4)
      throw Error(`Нужны четыре места: ${profile}.`);
    entries.forEach((entry, i) => {
      const z = entry?.zone,
        b = entry?.badge;
      if (
        entry?.id !== `place-${i + 1}` ||
        entry.number !== i + 1 ||
        !z ||
        !b ||
        !finite(z.x, -1040, 2080) ||
        !finite(z.y, -1040, 2080) ||
        !finite(z.width, 8, 1040) ||
        !finite(z.height, 8, 1600) ||
        !finite(b.x, -1040, 2080) ||
        !finite(b.y, -1040, 2080) ||
        !finite(b.size, 12, 96)
      )
        throw Error(`Некорректная геометрия: ${profile}, место ${i + 1}.`);
    });
  }
  for (const profile of ["mobile", "desktop"] as const)
    for (const id of ["energy", "company"] as const) {
      const logo = value.logos?.[profile]?.[id];
      if (
        !logo ||
        !finite(logo.dx, -400, 400) ||
        !finite(logo.dy, -400, 400) ||
        !finite(logo.scale, 0.25, 4)
      )
        throw Error("Некорректные координаты логотипа.");
    }
  // Whitelist schema fields; imported documents cannot introduce executable styling.
  return {
    version: 1,
    profiles: Object.fromEntries(
      (["wide", "portrait", "unloaded"] as const).map((p) => [
        p,
        value.profiles[p].map((e: LayoutPlace) => ({
          id: e.id,
          number: e.number,
          zone: {
            x: e.zone.x,
            y: e.zone.y,
            width: e.zone.width,
            height: e.zone.height,
          },
          badge: { x: e.badge.x, y: e.badge.y, size: e.badge.size },
        })),
      ]),
    ) as CompactLayout["profiles"],
    logos: Object.fromEntries(
      (["mobile", "desktop"] as const).map((p) => [
        p,
        Object.fromEntries(
          (["energy", "company"] as const).map((id) => [
            id,
            {
              dx: value.logos[p][id].dx,
              dy: value.logos[p][id].dy,
              scale: value.logos[p][id].scale,
            },
          ]),
        ),
      ]),
    ) as CompactLayout["logos"],
  };
}
export function readLayout(
  storage: Pick<Storage, "getItem">,
  key = layoutStorageKey,
): CompactLayout {
  try {
    const text = storage.getItem(key);
    return text ? parseLayout(text) : structuredClone(defaultLayout);
  } catch {
    return structuredClone(defaultLayout);
  }
}
export function saveLayout(
  storage: Pick<Storage, "setItem">,
  layout: CompactLayout,
  key = layoutStorageKey,
) {
  storage.setItem(key, JSON.stringify(parseLayout(JSON.stringify(layout))));
}
export function layoutRegions(layout: CompactLayout, profile: LayoutProfile) {
  return layout.profiles[profile].map((p) => ({
    id: p.id,
    number: p.number,
    ...p.zone,
    markerX: p.zone.x + p.zone.width / 2,
    markerY: p.zone.y + p.zone.height / 2,
  }));
}
export type LayoutHistory = {
  past: CompactLayout[];
  present: CompactLayout;
  future: CompactLayout[];
};
export const createHistory = (layout: CompactLayout): LayoutHistory => ({
  past: [],
  present: structuredClone(layout),
  future: [],
});
export const commitHistory = (
  h: LayoutHistory,
  next: CompactLayout,
): LayoutHistory =>
  JSON.stringify(h.present) === JSON.stringify(next)
    ? h
    : {
        past: [...h.past.slice(-79), h.present],
        present: structuredClone(next),
        future: [],
      };
export const undoHistory = (h: LayoutHistory): LayoutHistory =>
  h.past.length
    ? {
        past: h.past.slice(0, -1),
        present: h.past.at(-1)!,
        future: [h.present, ...h.future],
      }
    : h;
export const redoHistory = (h: LayoutHistory): LayoutHistory =>
  h.future.length
    ? {
        past: [...h.past, h.present],
        present: h.future[0],
        future: h.future.slice(1),
      }
    : h;
