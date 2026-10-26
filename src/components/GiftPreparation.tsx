import { ArrowLeft, Pencil } from "lucide-react";
import { useEffect, useRef } from "react";
import { choiceArtwork, preparationCardArtwork } from "../game/artwork";
import {
  findParcel,
  findProfile,
  findRecipient,
  parcels,
  profiles,
  recipients,
} from "../game/content";
import { scenarioParagraph } from "../game/scenarioDocument";
import type { GameAction, GameState } from "../game/types";
import styles from "./GiftPreparation.module.css";

type Props = {
  state: GameState;
  onAction: (action: GameAction) => void;
  onBackToIntro?: () => void;
};
const recipientDative = { alva: "Майме", khor: "Хабту", arseniy: "Арсению" };

/* "Девочка Майма (всплывающая подсказка: …)" → who the recipient is, shown on the card,
   so the player never meets an unexplained name such as «Хабт». */
function recipientKind(id: string, role: "text" | "mixed") {
  const [line] = scenarioParagraph(id, role).split(" (");
  return line.slice(0, line.lastIndexOf(" "));
}
const cardDetails: Record<string, { kind?: string; note?: string }> = {
  alva: {
    kind: recipientKind("6BACF81D", "mixed"),
    note: "«Радость» по\u2011ненецки",
  },
  khor: {
    kind: recipientKind("65B771C9", "mixed"),
    note: "«Дикий олень» по\u2011ненецки",
  },
  arseniy: { kind: recipientKind("49951299", "text") },
};
const slots = [
  { step: "profile", label: "Отправитель" },
  { step: "recipient", label: "Получатель" },
  { step: "parcel", label: "Груз" },
] as const;

/** One preparation table, with the chosen people staying beside the next decision. */
export function GiftPreparation({ state, onAction, onBackToIntro }: Props) {
  const heading = useRef<HTMLHeadingElement>(null);
  const previousStep = useRef(state.step);
  useEffect(() => {
    if (previousStep.current !== state.step)
      heading.current?.focus({ preventScroll: true });
    previousStep.current = state.step;
  }, [state.step]);
  const profile = findProfile(state.profile);
  const recipient = findRecipient(state.recipient);
  const current = slots.findIndex((slot) => slot.step === state.step);
  const items =
    state.step === "profile"
      ? profiles
      : state.step === "recipient"
        ? recipients
        : parcels;
  const title =
    state.step === "profile"
      ? "Кто отправит подарок?"
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
          <ol
            className={styles.waybill}
            aria-label="Маршрутный лист"
            data-gift-summary
          >
            {slots.map((slot, index) => {
              const chosen =
                slot.step === "profile"
                  ? profile
                  : slot.step === "recipient"
                    ? recipient
                    : findParcel(state.parcel);
              const done = index < current && chosen;
              const label = (
                <>
                  <span className={styles.slotMark} aria-hidden="true">
                    {done ? (
                      <img src={choiceArtwork[chosen.id]} alt="" />
                    ) : (
                      index + 1
                    )}
                  </span>
                  <span className={styles.slotText}>
                    <small>{slot.label}</small>
                    <strong>
                      {done
                        ? chosen.title
                        : index === current
                          ? "Выбираем"
                          : "—"}
                    </strong>
                  </span>
                </>
              );
              return (
                <li
                  key={slot.step}
                  data-summary={slot.step}
                  data-state={
                    done ? "done" : index === current ? "current" : "todo"
                  }
                >
                  {done ? (
                    <button
                      type="button"
                      className={styles.slot}
                      aria-label={`${slot.label}: ${chosen.title}. Изменить`}
                      onClick={() => {
                        for (let n = index; n < current; n++)
                          onAction({ type: "BACK" });
                      }}
                    >
                      {label}
                      <Pencil
                        className={styles.slotEdit}
                        size={14}
                        strokeWidth={2.2}
                        aria-hidden="true"
                      />
                    </button>
                  ) : (
                    <span
                      className={styles.slot}
                      aria-current={index === current ? "step" : undefined}
                    >
                      {label}
                    </span>
                  )}
                </li>
              );
            })}
          </ol>
        </div>
        <div className={styles.question}>
          <h1 id="preparation-question" ref={heading} tabIndex={-1}>
            {title}
          </h1>
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
                  {cardDetails[item.id]?.kind && (
                    <small className={styles.kind}>
                      {cardDetails[item.id].kind}
                    </small>
                  )}
                  <span>{item.title}</span>
                  {cardDetails[item.id]?.note && (
                    <small className={styles.note}>
                      {cardDetails[item.id].note}
                    </small>
                  )}
                </span>
              </button>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
