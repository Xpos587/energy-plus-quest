import type { CSSProperties } from "react";
import { imageAsset } from "../../game/imageAssets";
import { lastmileChoiceArtwork } from "./expandedArtwork";
import styles from "./LastmileMotion.module.css";

type Box = { x: number; y: number; w: number; h: number };
type Sprite = Box & { image: string };
type Motion = Record<"floes" | "barge" | "rover" | "pipe-carrier", Sprite> & {
  rotor: Sprite & { frames: number };
};

/**
 * Ambient life on the R5 map: rotor, barge, floes and vehicles. Every layer is cut from the same
 * painted plate (scripts/lastmile-r5/compose.py), so the moving parts carry no style seam.
 * Static frames are pixel-identical to the plate; reduced motion keeps them still.
 */
export function LastmileMotion({
  composition,
}: {
  composition: "wide" | "tall";
}) {
  const {
    width,
    height,
    motion,
  }: { width: number; height: number; motion?: Motion } =
    lastmileChoiceArtwork[composition];
  if (!motion) return null;
  const place = ({ x, y, w, h }: Box): CSSProperties => ({
    left: `${(x / width) * 100}%`,
    top: `${(y / height) * 100}%`,
    width: `${(w / width) * 100}%`,
    height: `${(h / height) * 100}%`,
  });
  const sprite = (
    id: "floes" | "barge" | "rover" | "pipe-carrier",
    className: string,
  ) => (
    <img
      className={className}
      src={imageAsset(motion[id].image)}
      style={{
        ...place(motion[id]),
        // logical-pixel amplitudes as a share of the sprite, so they scale with the map
        ["--lift" as string]: `${(-2 / motion[id].h) * 100}%`,
        ["--shake" as string]: `${(0.6 / motion[id].h) * 100}%`,
        // floes drift inside the 3 px inpainted margin left around them in the plate
        ["--drift" as string]: `${(2.5 / motion[id].w) * 100}%`,
      }}
      alt=""
      draggable={false}
    />
  );
  return (
    <div
      className={styles.motion}
      aria-hidden="true"
      data-lastmile-motion={composition}
    >
      {sprite("floes", styles.floes)}
      {sprite("barge", styles.barge)}
      {sprite("rover", styles.idle)}
      {sprite("pipe-carrier", `${styles.idle} ${styles.late}`)}
      <div className={styles.rotor} style={place(motion.rotor)}>
        <img
          src={imageAsset(motion.rotor.image)}
          style={{ width: `${motion.rotor.frames * 100}%` }}
          alt=""
          draggable={false}
        />
      </div>
    </div>
  );
}
