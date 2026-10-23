import type { ParcelId } from "../../game/types";
import styles from "./CompactOutcome.module.css";
import { compactArtwork } from "./artwork";
import { ImageSources } from "../../components/ImageSources";
import { ArtworkLoading } from "../../components/ArtworkLoading";
import { useArtworkLoading } from "../../components/useArtworkLoading";

// Semantic identifiers keep automatic and manual consequences distinct.
type ConsequenceKind =
  | "scatter"
  | "dishes"
  | "axle"
  | "secured-space"
  | "compact"
  | "unload-three"
  | "unused-space"
  | "no-fit"
  | "reload-upright"
  | "upright";
type Consequence = readonly [ConsequenceKind, string, string];
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
  showCaption = true,
}: {
  parcel: ParcelId;
  selectedId: string;
  showCaption?: boolean;
}) {
  const consequence = consequences[parcel][selectedId];
  const image = compactArtwork(parcel, selectedId);
  const artwork = useArtworkLoading(image?.src ?? "");
  if (!consequence || !image) return null;
  const [diagram, sourceId, caption] = consequence;
  return (
    <figure
      className={styles.consequence}
      data-image-only={!showCaption || undefined}
      data-compact-consequence={`${parcel}-${selectedId}`}
      data-source-id={sourceId}
      aria-label="Иллюстрация последствия"
    >
      <picture>
      <ImageSources src={artwork.src} sizes="144px" />
      <img
        ref={artwork.ref}
        onLoad={artwork.onLoad}
        onError={artwork.onError}
        src={artwork.src}
        decoding="async"
        alt={image.alt}
        width="1536"
        height="1024"
        data-diagram={diagram}
      />
      </picture>
      <ArtworkLoading viewport status={artwork.status} onRetry={artwork.retry} />
      {showCaption && <figcaption>{caption}</figcaption>}
    </figure>
  );
}
