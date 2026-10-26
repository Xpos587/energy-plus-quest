import { imageAsset } from "../../game/imageAssets";
/** Integrated Compact illustrations. Missing entries retain the selected V26 loading bay. */
export const compactResultArtwork: Record<string, string> = {
  'boat:place-3': imageAsset('compact-art/boat-zone3-no-fit-v48.webp'),
  'camera:place-2': imageAsset('compact-art/camera-zone2-v53.png'),
  'camera:place-4': imageAsset('compact-art/camera-zone4-v53.png'),
  'socks:place-2': imageAsset('compact-art/socks-zone2-v53.png'),
  'socks:place-4': imageAsset('compact-art/socks-zone4-v53.png'),
  'boat:place-4': imageAsset('compact-art/boat-zone4-supported-v53.png'),
  'boat:auto': imageAsset('compact-art/boat-zone4-supported-v53.png'),
  'camera:place-1': imageAsset('compact-art/camera-zone1-fallen-v53.png'),
  'camera:place-3': imageAsset('compact-art/camera-zone3-packed-v53.png'),
  'camera:auto': imageAsset('compact-art/camera-zone3-packed-v53.png'),
  'socks:place-1': imageAsset('compact-art/socks-zone1-unsecured-v53.png'),
  'socks:place-3': imageAsset('compact-art/socks-zone3-secured-v53.png'),
  'socks:auto': imageAsset('compact-art/socks-zone3-secured-v53.png'),
  'boat:place-2': imageAsset('compact-art/boat-zone2-v53.png'),
  'boat:place-1': imageAsset('compact-art/boat-zone1-axle-v53.png'),
};

/** Coordinates share the artwork's normalized 1040-unit width. Every frame
 * keeps the right edge (x = 1040) in view so the cab stays visible. */
const keepCab = (width: number, y: number) => ({ x: 1040 - width / 2, y, width, desktopWidth: width });
export const compactResultFrames: Record<string, {
  x: number; y: number; width: number; desktopWidth: number; desktopX?: number;
  height?: number; unloaded?: boolean;
}> = {
  'camera:place-1': keepCab(1040, 470),
  'socks:place-1': keepCab(1040, 470),
  'boat:place-1': keepCab(1040, 480),
  'camera:place-2': keepCab(840, 460),
  'socks:place-2': keepCab(840, 460),
  'boat:place-2': keepCab(840, 460),
  'camera:place-3': keepCab(680, 450),
  'camera:auto': keepCab(680, 450),
  'socks:place-3': keepCab(680, 450),
  'socks:auto': keepCab(680, 450),
  'boat:place-3': keepCab(680, 450),
  'camera:place-4': keepCab(560, 440),
  'socks:place-4': keepCab(560, 445),
  'boat:place-4': keepCab(560, 445),
  'boat:auto': keepCab(560, 445),
};
