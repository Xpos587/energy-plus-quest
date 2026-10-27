/** Barge scene v3: one isometric quay drawing in two crops, four result stills. */
const base = "scene-art/barge-v3";

type Rect = { x: number; y: number; width: number; height: number };
/** What a choice highlights: frames around who and what it uses, one path to the near crane's cabin. */
type Mark = { frames: readonly Rect[]; path?: string };

export const craneArtwork = {
  // Desktop beside the choice rail (about 5:4): the whole quay, no crop.
  mid: {
    image: `${base}/choice-mid.webp`,
    width: 1402,
    height: 1122,
    focus: { x: 25, y: 150, width: 1350, height: 900 },
    hotspots: {
      remote: { x: 398, y: 362, side: "right" },
      rush: { x: 470, y: 640, side: "left" },
      wait: { x: 762, y: 470, side: "right" },
      petr: { x: 1122, y: 245, side: "left" },
    },
    chips: { barge: { x: 912, y: 985 }, gift: { x: 203, y: 838 } },
    marks: {
      remote: { frames: [{ x: 115, y: 360, width: 275, height: 140 }, { x: 590, y: 435, width: 140, height: 120 }], path: "M392 410 Q500 330 588 462" },
      rush: { frames: [{ x: 590, y: 435, width: 140, height: 120 }], path: "M290 600 Q380 720 500 700 L552 560" },
      wait: { frames: [{ x: 590, y: 435, width: 140, height: 120 }] },
      petr: { frames: [{ x: 1108, y: 262, width: 105, height: 115 }, { x: 590, y: 435, width: 140, height: 120 }], path: "M1105 320 Q900 330 734 470" },
    },
    zoom: {},
  },
  // Desktop: the whole quay at 3:2, so the picture beside the choice rail needs no crop.
  desk: {
    image: `${base}/choice-desk.webp`,
    width: 1536,
    height: 1024,
    focus: { x: 0, y: 60, width: 1536, height: 940 },
    hotspots: {
      remote: { x: 372, y: 262, side: "right" },
      rush: { x: 586, y: 500, side: "left" },
      wait: { x: 812, y: 400, side: "right" },
      petr: { x: 1300, y: 140, side: "left" },
    },
    chips: { barge: { x: 1000, y: 900 }, gift: { x: 240, y: 765 } },
    marks: {
      remote: { frames: [{ x: 108, y: 255, width: 265, height: 162 }, { x: 655, y: 325, width: 152, height: 145 }], path: "M376 300 Q520 215 650 350" },
      rush: { frames: [{ x: 655, y: 325, width: 152, height: 145 }], path: "M205 400 Q300 610 540 650 L606 350" },
      wait: { frames: [{ x: 655, y: 325, width: 152, height: 145 }] },
      petr: { frames: [{ x: 1245, y: 160, width: 112, height: 115 }, { x: 655, y: 325, width: 152, height: 145 }], path: "M1242 225 Q1000 235 812 365" },
    },
    zoom: {},
  },
  wide: {
    image: `${base}/choice-wide.webp`,
    width: 1942,
    height: 809,
    // The strip that must stay in frame: office, gift, near crane, barge, far crane.
    focus: { x: 0, y: 40, width: 1942, height: 760 },
    hotspots: {
      remote: { x: 372, y: 262, side: "right" },
      rush: { x: 760, y: 430, side: "left" },
      wait: { x: 1000, y: 236, side: "right" },
      petr: { x: 1612, y: 96, side: "left" },
    },
    chips: { barge: { x: 1300, y: 718 }, gift: { x: 402, y: 646 } },
    marks: {
      remote: { frames: [{ x: 128, y: 225, width: 300, height: 160 }, { x: 840, y: 208, width: 145, height: 140 }], path: "M428 270 Q640 110 838 250" },
      rush: { frames: [{ x: 840, y: 208, width: 145, height: 140 }], path: "M312 470 Q520 575 735 525 L790 300" },
      wait: { frames: [{ x: 840, y: 208, width: 145, height: 140 }] },
      petr: { frames: [{ x: 1630, y: 55, width: 118, height: 118 }, { x: 840, y: 208, width: 145, height: 140 }], path: "M1628 118 Q1300 60 988 244" },
    },
    zoom: {},
  },
  tall: {
    image: `${base}/choice-tall.webp`,
    width: 1024,
    height: 1536,
    focus: { x: 0, y: 100, width: 1024, height: 1340 },
    hotspots: {
      remote: { x: 385, y: 410, side: "right" },
      rush: { x: 290, y: 870, side: "right" },
      wait: { x: 615, y: 640, side: "right" },
      petr: { x: 760, y: 290, side: "left" },
    },
    chips: { barge: { x: 480, y: 1372 }, gift: { x: 88, y: 762 } },
    marks: {
      remote: { frames: [{ x: 95, y: 255, width: 270, height: 175 }, { x: 445, y: 575, width: 150, height: 160 }], path: "M365 345 Q470 390 500 568" },
      rush: { frames: [{ x: 445, y: 575, width: 150, height: 160 }], path: "M250 500 Q170 760 290 890 L385 612" },
      wait: { frames: [{ x: 445, y: 575, width: 150, height: 160 }] },
      petr: { frames: [{ x: 780, y: 250, width: 115, height: 115 }, { x: 445, y: 575, width: 150, height: 160 }], path: "M778 330 Q650 400 600 572" },
    },
    // Card open on a phone: the camera closes in on the chosen way.
    zoom: {
      remote: { x: 40, y: 200, width: 700, height: 700 },
      rush: { x: 100, y: 380, width: 700, height: 640 },
      wait: { x: 200, y: 360, width: 700, height: 640 },
      petr: { x: 324, y: 180, width: 700, height: 700 },
    },
  },
} satisfies Record<string, {
  image: string; width: number; height: number; focus: Rect;
  hotspots: Record<string, { x: number; y: number; side: "left" | "right" }>;
  chips: Record<"barge" | "gift", { x: number; y: number }>;
  marks: Record<string, Mark>;
  zoom: Partial<Record<string, Rect>>;
}>;

export type CraneFormat = keyof typeof craneArtwork;

/** What each pin points at in the drawing. */
export const craneCaptions = {
  remote: "Иван в офисе",
  rush: "Подъём в кабину",
  wait: "Кран свободен через 3 ч",
  petr: "Пётр на дальнем кране",
} as const;

/** Card facts, as the truck card lists speed and year: who, from where, when. */
export const craneFacts = {
  remote: { who: "Иван", where: "Из офиса, с пульта", when: "Сразу", note: "Кран управляется дистанционно" },
  rush: { who: "Иван", where: "Из кабины", when: "После подъёма", note: "Подъём по лестнице на высоту крана" },
  wait: { who: "По графику", where: "Из кабины", when: "Через 3 ч", note: "Баржа готова к отходу уже сейчас" },
  petr: { who: "Пётр", where: "Из ближнего крана", when: "Сразу", note: "У Петра скоро своя погрузка" },
} as const;

export const craneOutcomeImage = (id: string) => `${base}/outcome-${id}.webp`;
export const craneChoiceImage = craneArtwork.wide.image;
