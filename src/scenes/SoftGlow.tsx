import { useId, type SVGProps } from "react";

/**
 * Soft white light around a choice outline (R19): a widened, blurred halo minus a
 * feathered copy of the shape, so the light fades into the object instead of
 * stopping at a hard cut-out edge. One filter, no mask (masks with blurred holes
 * render as a boxed haze in Chromium and are unreliable in Safari).
 */
export function SoftGlow({ d, ...rest }: { d: string } & SVGProps<SVGPathElement>) {
  const id = `soft-glow-${useId().replace(/[^a-zA-Z0-9]/g, "")}`;
  return (
    <>
      <defs>
        {/* A user-space region: ±50% of a narrow figure is smaller than the halo and clips it to a box. */}
        <filter id={id} filterUnits="userSpaceOnUse" x="-5000" y="-5000" width="15000" height="15000" colorInterpolationFilters="sRGB">
          <feMorphology in="SourceAlpha" operator="dilate" radius="10" result="grow" />
          <feGaussianBlur in="grow" stdDeviation="12" result="halo" />
          <feGaussianBlur in="SourceAlpha" stdDeviation="4" result="body" />
          <feComposite in="halo" in2="body" operator="out" result="ring" />
          <feFlood floodColor="#fff" />
          <feComposite in2="ring" operator="in" />
        </filter>
      </defs>
      <path d={d} fill="#000" stroke="none" filter={`url(#${id})`} pointerEvents="none" {...rest} />
    </>
  );
}
