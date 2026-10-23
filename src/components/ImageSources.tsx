import { imageVariants } from "../game/imageAssets";

/** Let the browser negotiate AVIF and retain WebP on older embedded engines. */
export function ImageSources({
  src,
  sizes = "(min-aspect-ratio: 2/1) 100vw, 200vh",
  media,
  responsive = true,
}: {
  src: string;
  sizes?: string;
  media?: string;
  responsive?: boolean;
}) {
  const variants = imageVariants(src);
  if (!variants) return media ? <source media={media} srcSet={src} /> : null;
  return (
    <>
      {(variants.desktopAvif || variants.desktopWebp) && !media && responsive && (
        <source type={variants.desktopAvif ? "image/avif" : "image/webp"} media="(min-width: 1100px)" srcSet={variants.desktopAvif ?? variants.desktopWebp} />
      )}
      <source
        type="image/avif"
        media={media}
        srcSet={responsive ? variants.avifSrcSet : variants.avif}
        sizes={sizes}
      />
      <source
        type="image/webp"
        media={media}
        srcSet={responsive ? variants.webpSrcSet : src}
        sizes={sizes}
      />
    </>
  );
}
