import styles from "./BrandLockup.module.css";

/** Approved Figma lockup: optical letter alignment, including the 2px downshift. */
export function BrandLockup({ large = false }: { large?: boolean }) {
  return (
    <span className={`${styles.lockup} ${large ? styles.large : ""}`} data-brand-lockup>
      <img
        src={`${import.meta.env.BASE_URL}brand/quest-brand-lockup.svg`}
        alt="Энергия+ — Газпром нефть — Газпромнефть-Снабжение"
        width={484}
        height={65.94}
        style={{ display: "block", width: "100%", height: "auto", maxHeight: "none", transform: "none" }}
      />
    </span>
  );
}
