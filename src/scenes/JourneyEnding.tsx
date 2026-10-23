import { ArrowRight } from "lucide-react";
import { ImageSources } from "../components/ImageSources";
import { BrandLockup } from "../components/BrandLockup";
import { useOptionalSaveScope } from "../game/GameContext";
import { useStoredState } from "../game/persistence";
import type { Scores } from "../game/types";
import { endingGiftCopy, endingHeading, logistProfileCopy } from "./endingCopy";
import styles from "./JourneyEnding.module.css";
import { LogistCertificate } from "./LogistCertificate";
import { resolutionArtwork } from "./resolutionArtwork";
import type { SceneContext } from "./types";

type EndingProps = {
  context: SceneContext;
  scores: Scores;
  onRestart: () => void;
  onHome?: () => void;
};
export function JourneyEnding({
  context,
  scores,
  onRestart,
  onHome = onRestart,
}: EndingProps) {
  const scope = useOptionalSaveScope();
  const [showProfile, setShowProfile] = useStoredState(
    scope && `${scope}:ending-profile`,
    false,
    (value): value is boolean => typeof value === "boolean",
  );
  const focusHeading = (node: HTMLHeadingElement | null) => {
    node?.focus({ preventScroll: true });
  };
  const profile = logistProfileCopy(context.profile, context.recipient, scores);
  const art = resolutionArtwork(context.recipient, context.parcel);
  const [mission, greeting] = endingHeading(context.recipient).split(
    /(?<=!)\s+/u,
  );
  return (
    <main className={styles.ending} id="quest-main" data-journey-ending>
      <div className={styles.brand}>
        <BrandLockup large />
      </div>
      {showProfile ? (
        <LogistCertificate
          profile={context.profile}
          copy={profile}
          onRestart={onRestart}
          onHome={onHome}
        />
      ) : (
        <section className={styles.composition}>
          <div className={styles.art}>
            <picture>
            <ImageSources src={art.src} sizes="(max-width: 900px) 100vw, 50vw" />
            <img
              data-resolution-art
              src={art.src}
              alt={art.alt}
              width={1024}
              height={1024}
            />
            </picture>
          </div>
          <div className={styles.copy}>
            <h1 ref={focusHeading} tabIndex={-1}>
              {mission}
            </h1>{" "}
            <p>
              {greeting} {endingGiftCopy(context.parcel, context.recipient)}
            </p>
            <button type="button" onClick={() => setShowProfile(true)}>
              Узнать, какой вы логист
              <ArrowRight size={20} aria-hidden="true" />
            </button>
          </div>
        </section>
      )}
    </main>
  );
}
