import {
  ArrowLeft,
  ArrowUpRight,
  BriefcaseBusiness,
  Download,
  GraduationCap,
  Home,
  RotateCcw,
  Share2,
  X,
} from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { ImageSources } from "../components/ImageSources";
import { imageAsset } from "../game/imageAssets";
import type { ProfileId } from "../game/types";
import {
  certificateCopy,
  exportCertificate,
  type LogistCopy,
} from "./certificateExport";
import { endingHomeLabel, endingRestartLabel } from "./endingCopy";
import styles from "./LogistCertificate.module.css";

const certificateArtwork = {
  student: {
    future: "scene-art/certificates-v1/student-future.webp",
    energy: "scene-art/certificates-v1/student-energy.webp",
    empathy: "scene-art/certificates-v1/student-empathy.webp",
    efficiency: "scene-art/certificates-v1/student-efficiency.webp",
  },
  professional: {
    future: "scene-art/certificates-v1/professional-energy.webp",
    energy: "scene-art/certificates-v1/professional-energy.webp",
    empathy: "scene-art/certificates-v1/professional-empathy.webp",
    efficiency: "scene-art/certificates-v1/professional-efficiency.webp",
  },
} satisfies Record<ProfileId, Record<LogistCopy["type"], string>>;

/* The final invitation is one card for both profiles: students to the internship,
   professionals to the team. Both lead to the career pages of Газпромнефть‑Снабжение,
   the company the game is about: students to its university programmes with
   practice at the company, professionals to its vacancies (logistics, purchasing,
   warehouses). A deployment may override either address. */
const invitation = {
  student: {
    title: "Практика в команде снабжения",
    action: "Записаться на практику",
    more: "Подробнее о практике",
    url:
      import.meta.env.VITE_PRACTICE_URL ||
      "https://supply.gazprom-neft.ru/career/studentam/",
    icon: GraduationCap,
  },
  professional: {
    title: "Работа в команде снабжения",
    action: "Смотреть вакансии",
    more: "Подробнее о вакансиях",
    url:
      import.meta.env.VITE_CAREER_URL ||
      "https://supply.gazprom-neft.ru/career/vakansii-i-stazhirovki/",
    icon: BriefcaseBusiness,
  },
} satisfies Record<ProfileId, unknown>;

export function LogistCertificate({
  profile,
  copy,
  onRestart,
  onHome,
}: {
  profile: ProfileId;
  copy: LogistCopy;
  onRestart: () => void;
  onHome: () => void;
}) {
  const invite = invitation[profile];
  const artwork = imageAsset(certificateArtwork[profile][copy.type]);
  const [prepared, setPrepared] = useState<File>();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [compactPage, setCompactPage] = useState<"result" | "practice">(
    "result",
  );
  const heading = useRef<HTMLHeadingElement>(null);
  const practiceHeading = useRef<HTMLHeadingElement>(null);
  const shareDialog = useRef<HTMLDialogElement>(null);
  const shareTrigger = useRef<HTMLButtonElement>(null);
  const [shareOpen, setShareOpen] = useState(false);
  const closeShare = () => {
    shareDialog.current?.close();
    setShareOpen(false);
    shareTrigger.current?.focus({ preventScroll: true });
  };
  useEffect(() => {
    if (shareOpen && !shareDialog.current?.open) {
      shareDialog.current?.showModal();
      shareDialog.current?.querySelector<HTMLButtonElement>("button")?.focus();
    }
  }, [shareOpen]);
  const turnCompactPage = () => {
    const next = compactPage === "result" ? "practice" : "result";
    setCompactPage(next);
    requestAnimationFrame(() =>
      (next === "practice" ? practiceHeading : heading).current?.focus({
        preventScroll: true,
      }),
    );
  };
  useEffect(() => {
    heading.current?.focus({ preventScroll: true });
  }, []);
  useEffect(() => {
    let active = true;
    setPrepared(undefined);
    exportCertificate(copy, artwork).then(
      (file) => {
        if (active) setPrepared(file);
      },
      () => {
        /* Download can retry on demand. */
      },
    );
    return () => {
      active = false;
    };
  }, [copy, artwork]);

  const getFile = async () => prepared ?? exportCertificate(copy, artwork);
  const download = async () => {
    setBusy(true);
    setError("");
    try {
      const file = await getFile();
      setPrepared(file);
      const url = URL.createObjectURL(file);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = file.name;
      document.body.append(anchor);
      anchor.click();
      anchor.remove();
      window.setTimeout(() => URL.revokeObjectURL(url), 60_000);
    } catch {
      setError("Не удалось скачать сертификат. Попробуйте ещё раз.");
    } finally {
      setBusy(false);
    }
  };
  const share = async () => {
    if (!prepared) return;
    setError("");
    try {
      await navigator.share({
        files: [prepared],
        title: certificateCopy(copy)[0],
        text: certificateCopy(copy).join(" "),
      });
    } catch (e) {
      if (!(e instanceof DOMException && e.name === "AbortError"))
        setError(
          "Не удалось отправить файл. Скачайте его и прикрепите к сообщению.",
        );
    }
  };
  const canShareFile = Boolean(
    prepared &&
      typeof navigator.share === "function" &&
      typeof navigator.canShare === "function" &&
      navigator.canShare({ files: [prepared] }),
  );
  const pageUrl = new URL(location.href);
  pageUrl.search = "";
  pageUrl.hash = "";
  const message = `${certificateCopy(copy).join(" ")} ${pageUrl.href}`;

  return (
    <section
      className={styles.profile}
      data-logist-profile={copy.type}
      data-compact-page={compactPage}
    >
      <article className={styles.certificate} data-logist-certificate>
        <div className={styles.art}>
          <picture>
            <ImageSources
              src={artwork}
              sizes="(max-width: 360px) 100px, (max-width: 700px) 180px, 390px"
            />
            <img
              data-certificate-art
              src={artwork}
              width={1024}
              height={1024}
              alt=""
            />
          </picture>
        </div>
        <div className={styles.copy}>
          <h1 tabIndex={-1} ref={heading}>
            {copy.title}
          </h1>
          {copy.paragraphs.map((paragraph) => (
            <p key={paragraph}>{paragraph}</p>
          ))}
        </div>
      </article>
      <aside
        className={styles.practice}
        data-practice-cta={profile}
        aria-labelledby="ending-practice-title"
      >
        <span className={styles.practiceIcon} aria-hidden="true">
          <invite.icon size={26} strokeWidth={1.8} />
        </span>
        <div>
          <h2 id="ending-practice-title" ref={practiceHeading} tabIndex={-1}>
            {invite.title}
          </h2>
          <p>{copy.callToAction}</p>
        </div>
        <a
          className={styles.practiceAction}
          href={invite.url}
          target="_blank"
          rel="noopener noreferrer"
        >
          {invite.action}
          <ArrowUpRight size={20} aria-hidden="true" />
        </a>
      </aside>
      <button
        className={styles.compactPageToggle}
        data-certificate-page-toggle
        type="button"
        onClick={turnCompactPage}
        aria-label={
          compactPage === "result" ? invite.more : "Назад к результату"
        }
        title={compactPage === "result" ? invite.more : "Назад к результату"}
      >
        {compactPage === "result" && invite.more}
        {compactPage === "result" ? (
          <ArrowUpRight size={20} aria-hidden="true" />
        ) : (
          <ArrowLeft size={20} aria-hidden="true" />
        )}
      </button>
      <div className={styles.resultActions}>
        <button
          className={styles.shareTrigger}
          data-certificate-actions
          type="button"
          ref={shareTrigger}
          aria-haspopup="dialog"
          aria-expanded={shareOpen}
          onClick={() => {
            setError("");
            setShareOpen(true);
          }}
        >
          <Share2 size={21} aria-hidden="true" />
          Поделиться
        </button>
        <nav className={styles.secondaryActions} aria-label="Продолжить игру">
          <button
            type="button"
            onClick={onRestart}
            aria-label={endingRestartLabel}
            title={endingRestartLabel}
          >
            <RotateCcw aria-hidden="true" size={22} />
          </button>
          <button
            type="button"
            onClick={onHome}
            aria-label={endingHomeLabel}
            title={endingHomeLabel}
          >
            <Home aria-hidden="true" size={22} />
          </button>
        </nav>
      </div>
      <dialog
        ref={shareDialog}
        className={styles.shareDialog}
        aria-labelledby="ending-share-title"
        aria-describedby="ending-share-description"
        onCancel={(event) => {
          event.preventDefault();
          closeShare();
        }}
        onClose={closeShare}
        onKeyDown={(event) => {
          if (event.key !== "Tab") return;
          const controls = event.currentTarget.querySelectorAll<HTMLElement>(
            "button:not(:disabled), a[href]",
          );
          const first = controls[0];
          const last = controls[controls.length - 1];
          if (event.shiftKey && document.activeElement === first) {
            event.preventDefault();
            last?.focus();
          } else if (!event.shiftKey && document.activeElement === last) {
            event.preventDefault();
            first?.focus();
          }
        }}
        onClick={(event) => {
          if (event.target !== event.currentTarget) return;
          const r = event.currentTarget.getBoundingClientRect();
          if (
            event.clientX < r.left ||
            event.clientX > r.right ||
            event.clientY < r.top ||
            event.clientY > r.bottom
          )
            closeShare();
        }}
      >
        <button
          type="button"
          className={styles.closeShare}
          onClick={closeShare}
          aria-label="Закрыть"
          title="Закрыть"
        >
          <X size={23} aria-hidden="true" />
        </button>
        <h2 id="ending-share-title">Поделиться результатом</h2>
        <p id="ending-share-description">
          Отправьте результат друзьям или сохраните сертификат.
        </p>
        <nav
          className={styles.social}
          aria-label="Поделиться текстом результата"
        >
          <a
            href={`https://max.ru/:share?${new URLSearchParams({ text: message })}`}
            target="_blank"
            rel="noopener noreferrer"
            aria-label="MAX"
            title="MAX"
          >
            <SocialIcon channel="max" />
            <span>MAX</span>
          </a>
          <a
            href={`https://t.me/share/url?${new URLSearchParams({ url: pageUrl.href, text: certificateCopy(copy).join(" ") })}`}
            target="_blank"
            rel="noopener noreferrer"
            aria-label="Telegram"
            title="Telegram"
          >
            <SocialIcon channel="telegram" />
            <span>Telegram</span>
          </a>
          <a
            href={`https://vk.com/share.php?${new URLSearchParams({ url: pageUrl.href, title: certificateCopy(copy)[0] })}`}
            target="_blank"
            rel="noopener noreferrer"
            aria-label="ВКонтакте"
            title="ВКонтакте"
          >
            <SocialIcon channel="vk" />
            <span>ВКонтакте</span>
          </a>
        </nav>
        <div className={styles.fileActions}>
          {canShareFile && (
            <button type="button" onClick={share}>
              <Share2 size={21} aria-hidden="true" />
              Отправить сертификат
            </button>
          )}
          <button type="button" onClick={download} disabled={busy}>
            <Download size={21} aria-hidden="true" />
            {busy ? "Сохраняем сертификат…" : "Скачать сертификат"}
          </button>
          <small>PNG-файл с вашим результатом</small>
        </div>
        {error && (
          <p role="alert" className={styles.error}>
            {error}
          </p>
        )}
      </dialog>
    </section>
  );
}

function SocialIcon({ channel }: { channel: "max" | "telegram" | "vk" }) {
  if (channel === "max")
    return <img src="/brand/max-official.svg" width="30" height="30" alt="" />;
  return (
    <svg
      viewBox="0 0 24 24"
      width="24"
      height="24"
      aria-hidden="true"
      focusable="false"
    >
      {channel === "telegram" ? (
        <path
          fill="currentColor"
          d="M21.8 3.4 18.5 20c-.2 1-1 1.2-1.8.7l-5-3.7-2.4 2.3c-.3.3-.5.5-1 .5l.4-5.1 9.4-8.5c.4-.4-.1-.6-.6-.3L5.9 13.2 1 11.7c-1-.3-1-1 .2-1.5L20.4 2.8c.9-.3 1.6.2 1.4.6Z"
        />
      ) : (
        <path
          fill="currentColor"
          d="M2 5.5h3.8c.3 5.7 2.7 8.1 4.6 8.6V5.5H14v4.9c1.9-.2 4-2.5 4.7-4.9h3.6c-.6 3-2.8 5.2-4.3 6.1 1.5.8 4.1 2.8 5 6.4h-4c-.8-2.4-2.6-4.2-5-4.4V18h-.4C6.9 18 2.4 13.5 2 5.5Z"
        />
      )}
    </svg>
  );
}
