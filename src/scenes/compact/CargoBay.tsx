import { useId } from "react";
import { ArtworkLoading } from "../../components/ArtworkLoading";
import { useArtworkLoading } from "../../components/useArtworkLoading";
import { detailImageAsset, imageAsset } from "../../game/imageAssets";
import type { CarrierId } from "../../game/types";
import styles from "./CompactSectors.module.css";
import { defaultLayout, layoutRegions } from "./layout";

// Coordinates are normalized from each V26 composition independently.
export const cargoSpaces = layoutRegions(defaultLayout, "wide");
export const portraitCargoSpaces = layoutRegions(defaultLayout, "portrait");
export const unloadedCargoSpaces = layoutRegions(defaultLayout, "unloaded");

export function CargoBay({
  placement,
  focused,
  portrait = false,
  canvasHeight = 520,
  image,
  imageHeight,
  carrier,
  regions,
  offsetY = (canvasHeight - (portrait ? 874 : 520)) / 2,
}: {
  placement?: number;
  focused?: string;
  portrait?: boolean;
  canvasHeight?: number;
  image?: string;
  imageHeight?: number;
  carrier?: CarrierId;
  regions?: typeof cargoSpaces;
  offsetY?: number;
}) {
  const edgeMask = useId();
  const cabClip = useId();
  const cabHue = useId();
  const cabBlue = useId();
  const cabMask = useId();
  // The carrier choice is identified by color on the city map. Keep that
  // identity on the same truck here without recoloring cargo or surroundings.
  const hue = carrier === "old" ? 150 : carrier === "old4" ? 200 :
    carrier === "crew" || carrier === "express" ? -80 : undefined;
  const expandedBackground = !image && portrait && canvasHeight > 874;
  const source = image ?? imageAsset(portrait
    ? 'compact-art/compact-environment-v53-portrait.png'
    : 'compact-art/compact-environment-v54-wide.png');
  const artwork = useArtworkLoading<SVGImageElement>(detailImageAsset(source), source);
  return (
    <svg
      className={styles.art}
      viewBox={`0 0 1040 ${canvasHeight}`}
      aria-hidden={artwork.status === "ready" ? true : undefined}
      data-cargo-view="side-2d"
    >
      <title>Грузовой отсек</title>
      <defs>
        {hue !== undefined && <>
          <clipPath id={cabClip}>
            <path transform={`translate(0 ${offsetY})`} d={portrait
              ? "M825 313 L870 313 L880 330 L924 333 L981 355 L1015 389 L1039 453 L1040 675 L1000 685 L948 670 L929 640 L891 610 L853 600 L827 600 Z"
              : "M825 69 L870 69 L880 84 L924 86 L981 109 L1015 145 L1039 210 L1040 430 L1000 440 L948 425 L929 395 L891 365 L853 355 L827 355 Z"} />
          </clipPath>
          <filter id={cabHue} colorInterpolationFilters="sRGB">
            {carrier === "old4" ?
              <feColorMatrix type="matrix"
                values="0 0 1 0 0  0.18 0 0.82 0 0  0.77 0 0.23 0 0  0 0 0 1 0" /> :
              <feColorMatrix type="hueRotate" values={String(hue)} />}
            {carrier === "crew" || carrier === "express" ?
              <feColorMatrix type="saturate" values="0.7" /> : null}
          </filter>
          <filter id={cabBlue} colorInterpolationFilters="sRGB">
            <feColorMatrix type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  -1.4 0 1.4 0 0" />
            <feComponentTransfer><feFuncA type="discrete" tableValues="0 0 1 1" /></feComponentTransfer>
          </filter>
          <mask id={cabMask} maskUnits="userSpaceOnUse" maskContentUnits="userSpaceOnUse"
            x="0" y="0" width="1040" height={canvasHeight}>
            <image href={artwork.src} y={offsetY} width="1040"
              height={imageHeight ?? (portrait ? 874 : 520)}
              preserveAspectRatio="xMidYMid meet" clipPath={`url(#${cabClip})`}
              filter={`url(#${cabBlue})`} />
            {/* Blue reflections are not paint. Keep these materials from the
                original image, in the same normalized plane as the cabin. */}
            <g fill="black" transform={`translate(0 ${offsetY + (portrait ? 234 : 0)})`}
              data-cab-protected-materials>
              <path data-cab-material="side-glass-interior-mirrors"
                d="M922 180 L977 181 L982 188 L990 242 L980 244 L924 231 Q919 229 919 222 L919 185 Q919 181 922 180 Z" />
              <path data-cab-material="windshield-mirror-trim"
                d="M1000 181 L1007 182 L1018 237 L1017 241 L1010 240 Z" />
            </g>
          </mask>
        </>}
      {expandedBackground && <>
        <linearGradient id={`${edgeMask}-gradient`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="black" />
          <stop offset="0.06" stopColor="white" />
          <stop offset="0.94" stopColor="white" />
          <stop offset="1" stopColor="black" />
        </linearGradient>
        <mask id={edgeMask} maskUnits="userSpaceOnUse" x="0" y={offsetY} width="1040" height="874">
          <rect x="0" y={offsetY} width="1040" height="874" fill={`url(#${edgeMask}-gradient)`} />
        </mask>
      </>}
      </defs>
      {expandedBackground && <image
        href={imageAsset('compact-art/loading-background-tall-v1.webp')}
        y={offsetY - 604}
        width="1040"
        height="2080"
        preserveAspectRatio="none"
      />}
      <image
        ref={artwork.ref}
        href={artwork.src}
        onLoad={artwork.onLoad}
        onError={artwork.onError}
        y={offsetY}
        width="1040"
        height={imageHeight ?? (portrait ? 874 : 520)}
        preserveAspectRatio="xMidYMid meet"
        mask={expandedBackground ? `url(#${edgeMask})` : undefined}
      />
      {hue !== undefined && <image
        href={artwork.src}
        y={offsetY}
        width="1040"
        height={imageHeight ?? (portrait ? 874 : 520)}
        preserveAspectRatio="xMidYMid meet"
        clipPath={`url(#${cabClip})`}
        mask={`url(#${cabMask})`}
        filter={`url(#${cabHue})`}
        aria-hidden="true"
      />}
      {artwork.status !== "ready" && (
        <foreignObject x="350" y="365" width="340" height="130">
          <ArtworkLoading
            status={artwork.status}
            onRetry={artwork.retry}
            inline
          />
        </foreignObject>
      )}
      {(regions ?? (portrait ? portraitCargoSpaces : cargoSpaces)).map((space) => (
        <rect
          key={space.id}
          data-loading-zone={space.id}
          data-active={placement === space.number}
          data-focused={focused === space.id}
          className={styles.space}
          x={space.x}
          y={space.y + offsetY}
          width={space.width}
          height={space.height}
          rx="6"
        />
      ))}
    </svg>
  );
}
