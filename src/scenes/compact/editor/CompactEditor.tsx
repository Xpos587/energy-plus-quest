import {
  useCallback,
  useEffect,
  useRef,
  useState,
  type PointerEvent as ReactPointerEvent,
} from "react";
import {
  commitHistory,
  createHistory,
  defaultLayout,
  draftStorageKey,
  layoutStorageKey,
  parseLayout,
  readLayout,
  redoHistory,
  saveLayout,
  undoHistory,
  type CompactLayout,
  type LayoutProfile,
  type LogoId,
} from "../layout";
type Kind = "badge" | "zone" | "logo";
type Box = { id: string; x: number; y: number; width: number; height: number };
const presets = [
  [390, 844],
  [320, 568],
  [844, 390],
  [1440, 900],
];
const copy = <T,>(value: T): T => structuredClone(value);
export function CompactEditor() {
  const [history, setHistory] = useState(() =>
    createHistory(
      readLayout(
        localStorage,
        localStorage.getItem(draftStorageKey)
          ? draftStorageKey
          : layoutStorageKey,
      ),
    ),
  );
  const layout = history.present;
  const [applied, setApplied] = useState(() =>
    JSON.stringify(readLayout(localStorage)),
  );
  const current = useRef(layout);
  current.current = layout;
  const [kind, setKind] = useState<Kind>("badge");
  const [selected, setSelected] = useState("place-1");
  const [viewport, setViewport] = useState({ width: 390, height: 844 });
  const [parcel, setParcel] = useState("boat");
  const [carrier, setCarrier] = useState("near");
  const [revision, setRevision] = useState(0);
  const [ready, setReady] = useState(false);
  const [profile, setProfile] = useState<LayoutProfile>("portrait");
  const [boxes, setBoxes] = useState<Box[]>([]);
  const [zoom, setZoom] = useState(1);
  const [editing, setEditing] = useState(true);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [json, setJson] = useState("");
  const [dialogOpen, setDialogOpen] = useState(false);
  const iframe = useRef<HTMLIFrameElement>(null);
  const workspace = useRef<HTMLDivElement>(null);
  const dialog = useRef<HTMLDialogElement>(null);
  const drag = useRef<{
    start: CompactLayout;
    x: number;
    y: number;
    unit: number;
    id: string;
    kind: Kind;
    resize: boolean;
    width: number;
  } | null>(null);
  const logoProfile = viewport.width <= 900 ? "mobile" : "desktop";
  const commit = useCallback(
    (next: CompactLayout) => setHistory((h) => commitHistory(h, next)),
    [],
  );
  useEffect(() => {
    try {
      saveLayout(localStorage, layout, draftStorageKey);
      setError("");
    } catch {
      setError("Не удалось сохранить черновик в браузере. Экспортируйте JSON.");
    }
    iframe.current?.contentWindow?.postMessage(
      { type: "compact-layout-preview", layout },
      location.origin,
    );
  }, [layout, ready]);
  useEffect(() => {
    const node = workspace.current;
    if (!node) return;
    const update = () =>
      setZoom(
        Math.min(
          1,
          Math.max(0.1, (node.clientWidth - 48) / viewport.width),
          Math.max(0.1, (node.clientHeight - 48) / viewport.height),
        ),
      );
    update();
    const observer = new ResizeObserver(update);
    observer.observe(node);
    return () => observer.disconnect();
  }, [viewport]);
  useEffect(() => {
    if (dialogOpen) dialog.current?.showModal();
    else dialog.current?.close();
  }, [dialogOpen]);
  useEffect(() => {
    if (!ready) return;
    let choosing = false;
    const measure = () => {
      const doc = iframe.current?.contentDocument;
      if (!doc) return;
      const stage = doc.querySelector<HTMLElement>(
        '[data-world-scene="compact"]',
      );
      if (!choosing && stage) {
        if (doc.querySelector("[data-hotspot]")?.getClientRects().length)
          choosing = true;
        else if (!doc.querySelector("[data-result-reader]")) {
          const next = [
            ...doc.querySelectorAll<HTMLButtonElement>("button"),
          ].find((b) => /^(К выбору|Далее)$/.test(b.textContent?.trim() ?? ""));
          next?.click();
        }
      }
      const actual = stage?.dataset.layoutProfile;
      if (actual === "wide" || actual === "portrait" || actual === "unloaded")
        setProfile(actual);
      const targets: { id: string; node: Element | null }[] =
        kind === "logo"
          ? (["energy", "company"] as const).map((id) => ({
              id,
              node:
                [
                  ...doc.querySelectorAll(
                    `[data-scene="compact"] img[alt="${id === "energy" ? "Энергия+" : "Газпром нефть — Газпромнефть-Снабжение"}"]`,
                  ),
                ].find((node) => node.getBoundingClientRect().width > 0) ??
                null,
            }))
          : [1, 2, 3, 4].map((n) => ({
              id: `place-${n}`,
              node: doc.querySelector(
                `[${kind === "badge" ? "data-layout-badge" : "data-loading-zone"}="place-${n}"]`,
              ),
            }));
      const next: Box[] = targets.flatMap(({ id, node }) => {
        if (!node || node.getClientRects().length === 0) return [];
        const r = node.getBoundingClientRect();
        return [{ id, x: r.x, y: r.y, width: r.width, height: r.height }];
      });
      setBoxes((previous) =>
        JSON.stringify(previous) === JSON.stringify(next) ? previous : next,
      );
    };
    let timer = 0;
    const tick = () => {
      measure();
      timer = requestAnimationFrame(tick);
    };
    tick();
    return () => cancelAnimationFrame(timer);
  }, [ready, kind, revision, viewport]);
  const changeKind = (next: Kind) => {
    setKind(next);
    setSelected(next === "logo" ? "energy" : "place-1");
  };
  const update = (field: string, value: number) => {
    if (!Number.isFinite(value)) return;
    const next = copy(layout);
    if (kind === "logo") {
      const target = next.logos[logoProfile][selected as LogoId];
      if (field === "scale") target.scale = Math.min(4, Math.max(0.25, value));
      if (field === "dx") target.dx = Math.min(400, Math.max(-400, value));
      if (field === "dy") target.dy = Math.min(400, Math.max(-400, value));
    } else {
      const place = next.profiles[profile].find((p) => p.id === selected)!;
      const target = kind === "badge" ? place.badge : place.zone;
      (target as unknown as Record<string, number>)[field] =
        field === "size"
          ? Math.min(96, Math.max(12, value))
          : field === "width" || field === "height"
            ? Math.min(field === "width" ? 1040 : 1600, Math.max(8, value))
            : Math.min(2080, Math.max(-1040, value));
    }
    commit(next);
    setMessage("");
  };
  const startDrag = (
    event: ReactPointerEvent<HTMLElement>,
    id: string,
    resize = false,
  ) => {
    if (event.button !== 0) return;
    event.preventDefault();
    event.currentTarget.setPointerCapture(event.pointerId);
    setSelected(id);
    const doc = iframe.current?.contentDocument;
    const plane = doc
      ?.querySelector("[data-world-plane]")
      ?.getBoundingClientRect();
    drag.current = {
      start: copy(current.current),
      x: event.clientX,
      y: event.clientY,
      unit: plane?.width ? 1040 / plane.width : 1,
      id,
      kind,
      resize,
      width: boxes.find((b) => b.id === id)?.width ?? 100,
    };
  };
  const moveDrag = (event: ReactPointerEvent<HTMLElement>) => {
    const d = drag.current;
    if (!d) return;
    const dx = (event.clientX - d.x) / zoom,
      dy = (event.clientY - d.y) / zoom;
    const next = copy(d.start);
    const round = (v: number) => Math.round(v * 10) / 10;
    const coordinate = (v: number) => Math.min(2080, Math.max(-1040, round(v)));
    if (d.kind === "logo") {
      const target = next.logos[logoProfile][d.id as LogoId];
      if (d.resize)
        target.scale = Math.min(
          4,
          Math.max(0.25, round(target.scale * (1 + dx / d.width))),
        );
      else {
        target.dx = Math.min(400, Math.max(-400, round(target.dx + dx)));
        target.dy = Math.min(400, Math.max(-400, round(target.dy + dy)));
      }
    } else {
      const p = next.profiles[profile].find((p) => p.id === d.id)!;
      if (d.kind === "badge") {
        if (d.resize)
          p.badge.size = Math.min(96, Math.max(12, round(p.badge.size + dx)));
        else {
          p.badge.x = coordinate(p.badge.x + dx * d.unit);
          p.badge.y = coordinate(p.badge.y + dy * d.unit);
        }
      } else if (d.resize) {
        p.zone.width = Math.min(
          1040,
          Math.max(8, round(p.zone.width + dx * d.unit)),
        );
        p.zone.height = Math.min(
          1600,
          Math.max(8, round(p.zone.height + dy * d.unit)),
        );
      } else {
        p.zone.x = coordinate(p.zone.x + dx * d.unit);
        p.zone.y = coordinate(p.zone.y + dy * d.unit);
      }
    }
    current.current = next;
    setHistory((h) => ({ ...h, present: next }));
  };
  const finishDrag = () => {
    const d = drag.current;
    if (!d) return;
    drag.current = null;
    setHistory((h) =>
      JSON.stringify(d.start) === JSON.stringify(h.present)
        ? h
        : {
            past: [...h.past.slice(-79), d.start],
            present: h.present,
            future: [],
          },
    );
    setMessage("");
  };
  const cancelDrag = () => {
    const d = drag.current;
    if (d) {
      drag.current = null;
      setHistory((h) => ({ ...h, present: d.start }));
    }
  };
  const keyboard = (
    event: React.KeyboardEvent<HTMLElement>,
    resize = false,
  ) => {
    const delta = event.shiftKey ? 10 : 1;
    if (
      !["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown"].includes(event.key)
    )
      return;
    event.preventDefault();
    const horizontal = event.key === "ArrowLeft" || event.key === "ArrowRight";
    const amount =
      event.key === "ArrowLeft" || event.key === "ArrowUp" ? -delta : delta;
    const target =
      kind === "logo"
        ? layout.logos[logoProfile][selected as LogoId]
        : layout.profiles[profile].find((p) => p.id === selected)![kind];
    const field = resize
      ? kind === "logo"
        ? "scale"
        : kind === "badge"
          ? "size"
          : horizontal
            ? "width"
            : "height"
      : kind === "logo"
        ? horizontal
          ? "dx"
          : "dy"
        : horizontal
          ? "x"
          : "y";
    update(
      field,
      (target as unknown as Record<string, number>)[field] +
        (field === "scale" ? amount * 0.01 : amount),
    );
  };
  const importJson = (text: string) => {
    try {
      const next = parseLayout(text);
      commit(next);
      setDialogOpen(false);
      setMessage("JSON импортирован в черновик.");
      setError("");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Не удалось прочитать JSON.");
    }
  };
  const exportJson = () => {
    const blob = new Blob([JSON.stringify(layout, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "compact-layout-v1.json";
    a.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    setMessage("JSON выгружен. Передайте файл для принятия в игру.");
  };
  const selectedPlace = layout.profiles[profile].find((p) => p.id === selected);
  const values =
    kind === "logo"
      ? layout.logos[logoProfile][selected as LogoId]
      : kind === "badge"
        ? selectedPlace?.badge
        : selectedPlace?.zone;
  const labels: Record<string, string> = {
    x: "X",
    y: "Y",
    width: "Ширина",
    height: "Высота",
    size: "Размер номера",
    dx: "Сдвиг X",
    dy: "Сдвиг Y",
    scale: "Масштаб",
  };
  const src = `./scenes.html?scene=compact&parcel=${parcel}&recipient=alva&carrier=${carrier}&compactEditor=1`;
  return (
    <div className="compact-editor">
      <header className="editor-toolbar">
        <div>
          <span className="editor-eyebrow">СЦЕНА 02 / ЛОКАЛЬНЫЙ РЕДАКТОР</span>
          <h1>Выравнивание Compact</h1>
        </div>
        <nav aria-label="Сохранение">
          <button
            type="button"
            onClick={() => {
              setJson(JSON.stringify(layout, null, 2));
              setDialogOpen(true);
            }}
          >
            Импорт / JSON
          </button>
          <button type="button" onClick={exportJson}>
            Экспорт JSON
          </button>
          <button
            className="primary"
            type="button"
            onClick={() => {
              try {
                saveLayout(localStorage, layout);
                setApplied(JSON.stringify(layout));
                setMessage("Сохранено для обычного Compact в этом браузере.");
              } catch {
                setError("Не удалось сохранить. Экспортируйте JSON.");
              }
            }}
          >
            Сохранить для игры
          </button>
        </nav>
      </header>
      <div className="editor-tools">
        <div className="editor-segments" aria-label="Что редактировать">
          {(
            [
              ["badge", "Номера"],
              ["zone", "Зоны"],
              ["logo", "Логотипы"],
            ] as const
          ).map(([id, label]) => (
            <button
              type="button"
              key={id}
              aria-pressed={kind === id}
              onClick={() => changeKind(id)}
            >
              {label}
            </button>
          ))}
        </div>
        <div className="editor-history">
          <button
            type="button"
            disabled={!history.past.length}
            onClick={() => {
              setHistory(undoHistory);
              setMessage("");
            }}
          >
            Отменить
          </button>
          <button
            type="button"
            disabled={!history.future.length}
            onClick={() => {
              setHistory(redoHistory);
              setMessage("");
            }}
          >
            Повторить
          </button>
          <button
            type="button"
            onClick={() => {
              commit(defaultLayout);
              setMessage("");
            }}
          >
            Сбросить всё
          </button>
        </div>
        <label className="editor-toggle">
          <input
            type="checkbox"
            checked={editing}
            onChange={(e) => setEditing(e.target.checked)}
          />
          Редактирование
        </label>
      </div>
      <main className="editor-main">
        <section className="editor-preview" aria-label="Предпросмотр">
          <div className="editor-preview-bar">
            <label>
              Окно
              <select
                aria-label="Размер окна"
                value={`${viewport.width}×${viewport.height}`}
                onChange={(e) => {
                  const [width, height] = e.target.value.split("×").map(Number);
                  setReady(false);
                  setViewport({ width, height });
                  setRevision((n) => n + 1);
                }}
              >
                {presets.map(([w, h]) => (
                  <option key={w} value={`${w}×${h}`}>
                    {w} × {h}
                  </option>
                ))}
              </select>
            </label>
            <span>
              {Math.round(zoom * 100)}% ·{" "}
              {profile === "wide"
                ? "широкая композиция"
                : profile === "portrait"
                  ? "портретная композиция"
                  : "разгруженный кузов"}
            </span>
            <button
              type="button"
              onClick={() => {
                setReady(false);
                setRevision((n) => n + 1);
              }}
            >
              Экран выбора
            </button>
          </div>
          <div className="editor-workspace" ref={workspace}>
            <div
              className="editor-scaled-wrap"
              style={{
                width: viewport.width * zoom,
                height: viewport.height * zoom,
              }}
            >
              <div
                className="editor-canvas"
                style={{
                  width: viewport.width,
                  height: viewport.height,
                  transform: `scale(${zoom})`,
                }}
              >
                <iframe
                  key={revision}
                  ref={iframe}
                  title="Живой Compact"
                  src={src}
                  style={{ width: viewport.width, height: viewport.height }}
                  onLoad={() => setReady(true)}
                />
                {editing && (
                  <div
                    className="editor-overlay"
                    aria-label="Редактируемые элементы"
                  >
                    {boxes.map((box) => (
                      <div
                        key={box.id}
                        className={`editor-box ${selected === box.id ? "selected" : ""}`}
                        data-editor-target={`${kind}:${box.id}`}
                        style={{
                          left: box.x,
                          top: box.y,
                          width: box.width,
                          height: box.height,
                        }}
                      >
                        <button
                          type="button"
                          className="editor-drag"
                          aria-label={`Переместить ${kind} ${box.id}`}
                          onFocus={() => setSelected(box.id)}
                          onPointerDown={(e) => startDrag(e, box.id)}
                          onPointerMove={moveDrag}
                          onPointerUp={finishDrag}
                          onPointerCancel={cancelDrag}
                          onKeyDown={keyboard}
                        />
                        {selected === box.id && (
                          <button
                            type="button"
                            className="editor-resize"
                            aria-label={`Изменить размер ${box.id}`}
                            onPointerDown={(e) => startDrag(e, box.id, true)}
                            onPointerMove={moveDrag}
                            onPointerUp={finishDrag}
                            onPointerCancel={cancelDrag}
                            onKeyDown={(e) => keyboard(e, true)}
                          />
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        </section>
        <aside className="editor-inspector">
          <span className="editor-eyebrow">ТОЧНАЯ НАСТРОЙКА</span>
          <h2>
            {kind === "badge"
              ? "Номер"
              : kind === "zone"
                ? "Область выбора"
                : "Логотип"}
          </h2>
          <label>
            Элемент
            <select
              aria-label="Элемент"
              value={selected}
              onChange={(e) => setSelected(e.target.value)}
            >
              {kind === "logo" ? (
                <>
                  <option value="energy">Энергия+</option>
                  <option value="company">Газпромнефть-Снабжение</option>
                </>
              ) : (
                [1, 2, 3, 4].map((n) => (
                  <option key={n} value={`place-${n}`}>
                    Место {n}
                  </option>
                ))
              )}
            </select>
          </label>
          <div className="editor-fields">
            {values &&
              Object.entries(values).map(([field, value]) => (
                <label key={field}>
                  {labels[field]}
                  <input
                    aria-label={labels[field]}
                    type="number"
                    step={field === "scale" ? 0.05 : 1}
                    value={value}
                    onChange={(e) => {
                      if (e.target.value !== "")
                        update(field, e.target.valueAsNumber);
                    }}
                  />
                </label>
              ))}
          </div>
          <p className="editor-hint">
            Тяните выделенный элемент. Нижний правый угол меняет размер. Стрелки
            — шаг 1, Shift — шаг 10.
          </p>
          <p className="editor-hint">
            {kind === "badge"
              ? "Положение номера не двигает зону нажатия. Размер задан в пикселях окна."
              : kind === "zone"
                ? "Сдвиг и размер зоны не двигают номер. Координаты — в плоскости иллюстрации шириной 1040."
                : "Сдвиги заданы в пикселях окна. Настройки отдельно для мобильной и десктопной шапки; другие сцены не меняются."}
          </p>
          <div className="editor-divider" />
          <h3>Контекст сцены</h3>
          <label>
            Подарок
            <select
              aria-label="Подарок"
              value={parcel}
              onChange={(e) => {
                setParcel(e.target.value);
                setReady(false);
                setRevision((n) => n + 1);
              }}
            >
              <option value="boat">Лодка</option>
              <option value="camera">Фотоаппарат</option>
              <option value="socks">Носки</option>
            </select>
          </label>
          <label>
            Фура
            <select
              aria-label="Фура"
              value={carrier}
              onChange={(e) => {
                setCarrier(e.target.value);
                setReady(false);
                setRevision((n) => n + 1);
              }}
            >
              {[
                ["near", "Синяя"],
                ["old", "Красная"],
                ["old4", "Жёлтая"],
                ["crew", "Зелёная"],
                ["express", "Express"],
              ].map(([id, label]) => (
                <option key={id} value={id}>
                  {label}
                </option>
              ))}
            </select>
          </label>
          <div className="editor-divider" />
          <p className="editor-hint" data-editor-save-state>
            {JSON.stringify(layout) === applied
              ? "Текущие настройки сохранены для игры."
              : "Есть изменения, ещё не применённые к игре."}
          </p>
          <p className="editor-hint">
            Черновик сохраняется автоматически в этом браузере. «Сохранить для
            игры» применяет его локально. Для принятия в исходники выгрузите
            JSON.
          </p>
          <a
            className="editor-game-link"
            href={`./scenes.html?scene=compact&parcel=${parcel}&recipient=alva&carrier=${carrier}`}
            target="_blank"
            rel="noreferrer"
          >
            Открыть обычный Compact ↗
          </a>
          {message && (
            <p className="editor-status" role="status">
              {message}
            </p>
          )}
          {error && (
            <p className="editor-error" role="alert">
              {error}
            </p>
          )}
        </aside>
      </main>
      <dialog
        ref={dialog}
        className="editor-dialog"
        onCancel={() => setDialogOpen(false)}
      >
        <h2>Координаты Compact</h2>
        <p>
          Вставьте экспортированный JSON или выберите файл. Ошибка импорта
          сохранит текущий черновик.
        </p>
        <input
          aria-label="Файл координат"
          type="file"
          accept="application/json,.json"
          onChange={async (e) => {
            const file = e.target.files?.[0];
            if (file)
              try {
                const text = await file.text();
                setJson(text);
                importJson(text);
              } catch {
                setError("Не удалось прочитать файл.");
              }
          }}
        />
        <textarea
          aria-label="JSON координат"
          value={json}
          onChange={(e) => setJson(e.target.value)}
          spellCheck={false}
        />
        {error && (
          <p role="alert" className="editor-error">
            {error}
          </p>
        )}
        <footer>
          <button type="button" onClick={() => setDialogOpen(false)}>
            Закрыть
          </button>
          <button
            type="button"
            className="primary"
            onClick={() => importJson(json)}
          >
            Импортировать
          </button>
        </footer>
      </dialog>
    </div>
  );
}
