import { useReadingState } from "./useReadingState";
import { ArrowLeft, ArrowRight } from "lucide-react";
import { PageText } from "./PageText";
import { useTextPages } from "./useTextPages";
import styles from "./ResultCopy.module.css";

export function PagedDescription({ paragraphs }: { paragraphs: string[] }) {
  const { body, pages } = useTextPages(paragraphs, true, true);
  const [page, setPage] = useReadingState<number>(
    "PagedDescription:page:" + paragraphs.join("\n\n"),
    0,
  );
  const current = Math.min(page, Math.max(0, pages.length - 1));
  return (
    <div>
      <div ref={body} className={styles.body} aria-live="polite">
        <p>
          <PageText text={pages[current]} />
        </p>
      </div>
      {pages.length > 1 && (
        <nav className={styles.navigation} aria-label="Страницы описания">
          <button
            type="button"
            aria-label="Предыдущий фрагмент"
            disabled={current === 0}
            onClick={() => setPage(current - 1)}
          >
            <ArrowLeft size={20} aria-hidden="true" />
          </button>
          <span>
            {current + 1} / {pages.length}
          </span>
          <button
            type="button"
            aria-label="Следующий фрагмент"
            disabled={current === pages.length - 1}
            onClick={() => setPage(current + 1)}
          >
            <ArrowRight size={20} aria-hidden="true" />
          </button>
        </nav>
      )}
    </div>
  );
}
