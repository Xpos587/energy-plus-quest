import type { ParcelId } from "../../game/types";
import styles from "./CompactOutcome.module.css";

// Neutral consequence schematics, not artwork or an engineering load model.
const paths = {
  scatter:
    "M49 25h22v22H49Z M30 36H8m0 0 8-6m-8 6 8 6 M90 36h22m0 0-8-6m8 6-8 6 M60 17V3m0 0-5 5m5-5 5 5 M60 55v14m0 0-5-5m5 5 5-5",
  dishes:
    "M47 3h26v19H47Z M60 26v12m0 0-5-5m5 5 5-5 M54 43C25 31 24 69 53 64l-5-8 9-5Z M66 43C95 31 96 69 67 64l5-8-9-5Z",
  axle: "M42 3h36v19H42Z M60 25v12m0 0-5-5m5 5 5-5 M24 51H96 M15 7v15m0 6v1 M24 41a10 13 0 1 0 0 26 10 13 0 1 0 0-26 M96 41a10 13 0 1 0 0 26 10 13 0 1 0 0-26",
  "secured-space":
    "M8 5v60h104V5 M45 40h30v20H45Z M40 36v29m40-29v29 M35 36h10m30 0h10 M30 26h60m-60 0 6-5m-6 5 6 5m54-5-6-5m6 5-6 5",
  compact:
    "M12 10h30v24H12Z M78 10h30v24H78Z M12 40h30v24H12Z M78 40h30v24H78Z M48 25h24v25H48Z M51 22v31m18-31v31 M48 61l7 6 17-12",
  "unload-three":
    "M5 43h20v20H5Z M32 43h20v20H32Z M59 43h20v20H59Z M7 25h67m-67 0 8-6m-8 6 8 6 M87 8h25v27H87Z M90 5v33m19-33v33",
  "unused-space":
    "M8 5v60h104V5 M15 43h18v18H15Z M45 36h59m-59 0 6-5m-6 5 6 5m47-5-6-5m6 5-6 5 M45 17v38m59-38v38",
  "no-fit":
    "M45 12H31v49h14 M75 12h14v49H75 M8 24h104v23H8Z M52 55l16 14m0-14L52 69",
  "reload-upright":
    "M86 8h23v55H86Z M82 19h31m-31 31h31 M5 46h13v17H5Z M23 46h13v17H23Z M41 46h13v17H41Z M59 46h13v17H59Z M7 25h65m-65 0 8-6m-8 6 8 6",
  upright:
    "M48 5h24v60H48Z M37 20h46m-46 30h46 M37 15v10m46-10v10M37 45v10m46-10v10 M87 56l7 7 18-20",
};

type Consequence = readonly [keyof typeof paths, string, string];
// Captions are verbatim excerpts. Auto has its own source, not the manual branch's costs.
const consequences: Record<ParcelId, Record<string, Consequence>> = {
  socks: {
    "place-1": [
      "scatter",
      "p208",
      "Во время перевозки носки метались по кузову, не находя себе места.",
    ],
    "place-2": [
      "secured-space",
      "p230",
      "Носки надежно закрепили на ящике с посудой",
    ],
    "place-3": [
      "compact",
      "p257",
      "Вы разместили вязаный подарок компактно, закрепили его и сэкономили место для других грузов.",
    ],
    "place-4": [
      "unused-space",
      "p278",
      "Вы использовали пространство не очень эффективно",
    ],
    auto: [
      "compact",
      "p301",
      "носки поместились очень компактно и легко доехали до склада.",
    ],
  },
  camera: {
    "place-1": [
      "dishes",
      "p216",
      "Фотоаппарат заметался по кузову фуры и при падении повредил посуду.",
    ],
    "place-2": [
      "secured-space",
      "p240",
      "пространство над фотоаппаратом осталось неиспользованным.",
    ],
    "place-3": ["unload-three", "p264", "достать из кузова сразу три коробки."],
    "place-4": [
      "unused-space",
      "p284",
      "большое пространство кузова осталось пустым и было использовано неэффективно.",
    ],
    auto: [
      "compact",
      "p308",
      "хорошо закрепленный фотоаппарат не повредился сам и не повредил посуду.",
    ],
  },
  boat: {
    "place-1": [
      "axle",
      "p223",
      "Подарок стал последней каплей и перегрузил заднюю ось. Машина сломалась",
    ],
    "place-2": ["dishes", "p247", "Хрупкие тарелки были просто раздавлены"],
    "place-3": [
      "no-fit",
      "p270",
      "Лодка физически не может поместиться в таком узком пространстве",
    ],
    "place-4": [
      "reload-upright",
      "p290",
      "Для такой погрузки придется доставать весь уже размещенный груз",
    ],
    auto: [
      "upright",
      "p316",
      "Вертикальные крепления зафиксировали расположение лодки в кузове",
    ],
  },
};

export function CompactOutcome({
  parcel,
  selectedId,
}: {
  parcel: ParcelId;
  selectedId: string;
}) {
  const consequence = consequences[parcel][selectedId];
  if (!consequence) return null;
  const [diagram, sourceId, caption] = consequence;
  return (
    <figure
      className={styles.consequence}
      data-compact-consequence={`${parcel}-${selectedId}`}
      data-source-id={sourceId}
      aria-label="Схема последствия"
    >
      <svg
        viewBox="0 0 120 72"
        width="120"
        height="72"
        data-diagram={diagram}
        aria-hidden="true"
      >
        <path
          d={paths[diagram]}
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinejoin="round"
          strokeLinecap="round"
        />
      </svg>
      <figcaption>{caption}</figcaption>
    </figure>
  );
}
