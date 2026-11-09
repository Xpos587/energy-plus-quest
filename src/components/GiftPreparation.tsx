import { ArrowLeft } from "lucide-react";
import { useEffect, useRef } from "react";
import { preparationCardArtwork } from "../game/artwork";
import { parcels, profiles, recipients } from "../game/content";
import type { GameAction, GameState } from "../game/types";
import styles from "./GiftPreparation.module.css";

type Props = {
  state: GameState;
  onAction: (action: GameAction) => void;
  onBackToIntro?: () => void;
};
const recipientDative = { alva: "Майме", khor: "Хабту", arseniy: "Арсению" };
/* Cards answer their question: «Кому отправим?» → «Майме», «Что отправим?» → «Лодку». */
const cardName: Record<string, string> = {
  ...recipientDative,
  ...Object.fromEntries(
    parcels.map((p) => [p.id, p.accusativeTitle[0].toUpperCase() + p.accusativeTitle.slice(1)]),
  ),
};

/** One preparation table, with the chosen people staying beside the next decision. */
export function GiftPreparation({ state, onAction, onBackToIntro }: Props) {
  const heading = useRef<HTMLHeadingElement>(null);
  const previousStep = useRef(state.step);
  useEffect(() => {
    if (previousStep.current !== state.step)
      heading.current?.focus({ preventScroll: true });
    previousStep.current = state.step;
  }, [state.step]);
  const items =
    state.step === "profile"
      ? profiles
      : state.step === "recipient"
        ? recipients
        : parcels;
  const title =
    state.step === "profile"
      ? "Выберите свою роль"
      : state.step === "recipient"
        ? "Кому отправим подарок?"
        : `Что отправим ${state.recipient ? recipientDative[state.recipient] : "в подарок"}?`;
  const select = (id: string) => {
    if (state.step === "profile")
      onAction({
        type: "CHOOSE_PROFILE",
        value: id as NonNullable<GameState["profile"]>,
      });
    else if (state.step === "recipient")
      onAction({
        type: "CHOOSE_RECIPIENT",
        value: id as NonNullable<GameState["recipient"]>,
      });
    else
      onAction({
        type: "CHOOSE_PARCEL",
        value: id as NonNullable<GameState["parcel"]>,
      });
  };
  return (
    <section
      className={styles.preparation}
      data-preparation-step={state.step}
      aria-labelledby="preparation-question"
    >
      <img
        className={styles.backdrop}
        src={`${import.meta.env.BASE_URL}scene1-v4/backdrop.webp?v=1`}
        alt=""
        aria-hidden="true"
      />
      <div className={styles.table}>
        <div className={styles.journey}>
          {(state.step !== "profile" || onBackToIntro) && (
            <button
              type="button"
              className={styles.back}
              onClick={() =>
                state.step === "profile"
                  ? onBackToIntro?.()
                  : onAction({ type: "BACK" })
              }
            >
              <ArrowLeft size={20} strokeWidth={2} aria-hidden="true" />
              Назад
            </button>
          )}
        </div>
        <div className={styles.question}>
          <h1 id="preparation-question" ref={heading} tabIndex={-1}>
            {title}
          </h1>
          {/* The role only shapes the final offer; say so, or the choice reads as arbitrary. */}
          {state.step === "profile" && (
            <p className={styles.hint}>
              От роли зависит, что мы предложим вам в финале.
            </p>
          )}
        </div>
        <div className={styles.stage} data-kind={state.step} key={state.step}>
          <div
            className={styles.options}
            data-count={items.length}
            data-kind={state.step}
          >
            {items.map((item) => (
              <button
                type="button"
                key={item.id}
                data-choice={item.id}
                className={styles.option}
                onClick={() => select(item.id)}
              >
                <span className={styles.art}>
                  <img
                    src={preparationCardArtwork[item.id]}
                    alt=""
                    draggable={false}
                  />
                </span>
                <span className={styles.caption}>
                  <span>{cardName[item.id] ?? item.title}</span>
                </span>
              </button>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
