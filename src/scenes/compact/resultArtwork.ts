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

/** Coordinates share the artwork's normalized 1040-unit width. */
export const compactResultFrames: Record<string, {
  x: number; y: number; width: number; desktopWidth: number; desktopX?: number;
  height?: number; unloaded?: boolean;
}> = {
  'camera:place-1': { x: 260, y: 440, width: 440, desktopWidth: 720, desktopX: 360 },
  'socks:place-1': { x: 260, y: 440, width: 440, desktopWidth: 720, desktopX: 360 },
  'boat:place-1': { x: 290, y: 480, width: 580, desktopWidth: 1000, desktopX: 500 },
  'camera:place-2': { x: 330, y: 445, width: 420, desktopWidth: 680, desktopX: 350 },
  'socks:place-2': { x: 330, y: 445, width: 420, desktopWidth: 680, desktopX: 350 },
  'boat:place-2': { x: 345, y: 445, width: 480, desktopWidth: 760, desktopX: 380 },
  'camera:place-3': { x: 500, y: 440, width: 420, desktopWidth: 680 },
  'camera:auto': { x: 500, y: 440, width: 420, desktopWidth: 680 },
  'socks:place-3': { x: 500, y: 440, width: 420, desktopWidth: 680 },
  'socks:auto': { x: 500, y: 440, width: 420, desktopWidth: 680 },
  'camera:place-4': { x: 740, y: 430, width: 420, desktopWidth: 680, desktopX: 700 },
  'socks:place-4': { x: 740, y: 445, width: 420, desktopWidth: 680, desktopX: 700 },
  'boat:place-3': { x: 500, y: 440, width: 420, desktopWidth: 680 },
  'boat:place-4': { x: 740, y: 445, width: 420, desktopWidth: 680, desktopX: 700 },
  'boat:auto': { x: 740, y: 445, width: 420, desktopWidth: 680, desktopX: 700 },
};
