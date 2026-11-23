import type { CSSProperties } from "react";
import { imageAsset } from "../../game/imageAssets";
import { lastmileChoiceArtwork } from "./expandedArtwork";
import styles from "./LastmileMotion.module.css";

type Box = { x: number; y: number; w: number; h: number };
type Sprite = Box & { image: string };
type Motion = Record<"floes" | "barge" | "rover" | "pipe-carrier", Sprite> & {
  rotor: Sprite & { frames: number };
};

/** Pixel-matched map layers stay still; only the helicopter's rotor animates. */
export function LastmileMotion() {
  const {
    width,
    height,
    motion,
  }: { width: number; height: number; motion?: Motion } =
    lastmileChoiceArtwork;
  if (!motion) return null;
  const place = ({ x, y, w, h }: Box): CSSProperties => ({
    left: `${(x / width) * 100}%`,
    top: `${(y / height) * 100}%`,
    width: `${(w / width) * 100}%`,
    height: `${(h / height) * 100}%`,
  });
  const sprite = (id: "floes" | "barge" | "rover" | "pipe-carrier") => (
    <img
      src={imageAsset(motion[id].image)}
      style={place(motion[id])}
      alt=""
      draggable={false}
    />
  );
  return (
    <div
      className={styles.motion}
      aria-hidden="true"
      data-lastmile-motion
    >
      {sprite("floes")}
      {sprite("barge")}
      {sprite("rover")}
      {sprite("pipe-carrier")}
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
