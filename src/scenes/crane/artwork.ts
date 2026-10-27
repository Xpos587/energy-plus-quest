/** Barge scene v2: one neutral quay drawing in two crops, four result stills. */
const base = "scene-art/barge-v2";

export const craneArtwork = {
  wide: {
    image: `${base}/choice-wide.webp`,
    width: 1934,
    height: 813,
    // The strip that must stay in frame: office, gift, crane, barge, far crane.
    focus: { x: 180, y: 90, width: 1740, height: 600 },
    hotspots: {
      remote: { x: 395, y: 400, r: 90, side: "right" },
      rush: { x: 790, y: 380, r: 70, side: "right" },
      wait: { x: 822, y: 150, r: 70, side: "right" },
      petr: { x: 1790, y: 215, r: 70, side: "left" },
    },
    chips: { barge: { x: 1280, y: 560 }, gift: { x: 655, y: 440 } },
    // The gift's way onto the deck, then who reaches the crane controls and how.
    lift: "M655 455 Q760 250 900 560",
    routes: {
      remote: "M440 385 Q600 200 785 160",
      rush: "M480 540 L782 540 L782 175",
      wait: "",
      petr: "M1780 240 L1780 505 L800 515 L790 175",
    },
    // Card open: the camera closes in on the chosen way, as it follows a truck.
    zoom: {
      remote: { x: 250, y: 80, width: 750, height: 540 },
      rush: { x: 380, y: 80, width: 620, height: 540 },
      wait: { x: 520, y: 60, width: 560, height: 560 },
      petr: { x: 600, y: 110, width: 1330, height: 520 },
    },
  },
  tall: {
    image: `${base}/choice-tall.webp`,
    width: 1120,
    height: 1404,
    focus: { x: 0, y: 130, width: 1120, height: 980 },
    hotspots: {
      remote: { x: 248, y: 640, r: 90, side: "right" },
      rush: { x: 588, y: 580, r: 70, side: "right" },
      wait: { x: 612, y: 196, r: 70, side: "left" },
      petr: { x: 962, y: 445, r: 60, side: "left" },
    },
    chips: { barge: { x: 560, y: 1030 }, gift: { x: 437, y: 700 } },
    lift: "M437 715 Q280 760 330 915",
    routes: {
      remote: "M290 615 Q380 330 575 215",
      rush: "M372 785 L578 800 L585 260",
      wait: "",
      petr: "M962 480 L962 725 L600 800 L585 260",
    },
    zoom: {
      remote: { x: 0, y: 150, width: 720, height: 820 },
      rush: { x: 180, y: 150, width: 620, height: 820 },
      wait: { x: 260, y: 110, width: 620, height: 880 },
      petr: { x: 380, y: 150, width: 740, height: 820 },
    },
  },
} as const;
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
