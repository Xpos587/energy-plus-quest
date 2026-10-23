import { useEffect, useLayoutEffect, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { CityMap } from '../../src/components/CityMap';
import { CarrierInspection } from '../../src/components/CarrierInspection';
import { carrierFacts, mapCarrierIds } from '../../src/game/carrierFacts';
import { carrierBriefing, carrierQuestion, carriers, parcels } from '../../src/game/content';
import { interpolateOutcome } from '../../src/game/outcomeText';
import type { CarrierId, ParcelId } from '../../src/game/types';
import { compactScene } from '../../src/scenes/compact';
import { inventoryScene } from '../../src/scenes/inventory';
import { craneScene } from '../../src/scenes/crane';
import { lastmileScene } from '../../src/scenes/lastmile';
import { choiceLabel } from '../../src/scenes/choiceLabel';
import type { SceneContext } from '../../src/scenes/types';
import '../../src/index.css';
import './preview.css';

const scenes = [null, compactScene, inventoryScene, craneScene, lastmileScene];
const titles = ['Перевозчик', 'Укладка подарка', 'Поиск на складе', 'Погрузка на баржу', 'Последняя миля'];
const tabs = ['Перевозчик', 'Укладка', 'Склад', 'Баржа', 'Последняя миля'];
const captions: Record<string, string> = { rush: 'Иван', wait: 'Ждать кран', petr: 'Пётр', remote: 'Удалённо', entrance: 'У приёмки', alphabet: 'По алфавиту', keeper: 'Кладовщик', wms: 'Система WMS', helicopter: 'Вертолёт', rover: 'Снегоболотоход', robot: 'Робот', 'pipe-carrier': 'Трубовоз', 'place-1': 'Место 1', 'place-2': 'Место 2', 'place-3': 'Место 3', 'place-4': 'Место 4', auto: 'Автоподбор', express: 'Автоподбор Express', old: 'Красная фура', old4: 'Жёлтая фура', near: 'Синяя фура', crew: 'Зелёная фура' };

// Preview-only decoration of the real scene controls. Their hit areas and pan logic remain owned by the scene.
function usePreviewMarks(root: React.RefObject<HTMLDivElement | null>, scene: string) {
  useEffect(() => {
    const element = root.current;
    if (!element) return;
    element.querySelectorAll<HTMLElement>('[data-hotspot]').forEach(button => {
      button.dataset.reviewLabel = captions[button.dataset.hotspot!];
      button.dataset.reviewEdge = parseFloat(button.style.left) > 80 ? 'right' : 'left';
    });
    const cleanup: (() => void)[] = [];
    element.querySelectorAll<HTMLButtonElement>('[data-carrier-choice]').forEach(button => {
      const id = button.dataset.carrierChoice as Exclude<CarrierId, 'express'>;
      const pin = document.createElement('span');
      pin.className = 'rv-carrier-pin';
      pin.setAttribute('aria-hidden', 'true');
      const number = document.createElement('b');
      number.textContent = String(mapCarrierIds.indexOf(id) + 1);
      const label = document.createElement('span');
      label.className = 'rv-carrier-caption';
      label.textContent = captions[id].replace(' фура', '');
      pin.append(number, label);
      button.append(pin);
      const align = () => {
        const angle = Number(button.style.transform.match(/rotate\(([-.\d]+)rad\)/)?.[1] ?? 0);
        pin.style.transform = `translate(-50%, -50%) rotate(${-angle}rad) translateY(-36px)`;
      };
      align();
      const observer = new MutationObserver(align);
      observer.observe(button, { attributes: true, attributeFilter: ['style'] });
      cleanup.push(() => { observer.disconnect(); pin.remove(); });
    });
    return () => cleanup.forEach(fn => fn());
  }, [root, scene]);
}

function Preview() {
  const [step, setStep] = useState(3);
  const [parcel, setParcel] = useState<ParcelId>('camera');
  const [pending, setPending] = useState<string>();
  const [result, setResult] = useState<string>();
  const [situation, setSituation] = useState(false);
  const [page, setPage] = useState(0);
  const [route, setRoute] = useState(false);
  const [panHint, setPanHint] = useState(true);
  const root = useRef<HTMLDivElement>(null);
  const trigger = useRef<HTMLElement | null>(null);
  const panelHeading = useRef<HTMLHeadingElement>(null);
  usePreviewMarks(root, `${step}-${parcel}`);
  const context: SceneContext = { parcel, profile: 'student', recipient: 'alva' };
  const scene = scenes[step];
  const gift = parcels.find(item => item.id === parcel)!;
  const carrierSentences = carrierQuestion.split(/(?<=\.)\s+/);
  const intro = scene ? scene.intro(context) : [interpolateOutcome(carrierBriefing, undefined, gift.accusativeTitle), ...carrierSentences.slice(0, -1)];
  const separate = step === 1 || step === 4;
  const question = !scene ? carrierSentences.at(-1)!.replace(/:\s*$/, '') : separate ? intro.at(-1)! : step === 2 ? intro[0].split(/(?<=\.)\s+/).at(-1)! : 'Как погрузить подарок на баржу?';
  const situationPages = separate ? intro.slice(0, -1) : intro;
  const options = scene ? scene.options(context) : carriers.map(item => ({ id: item.id, label: item.description ?? item.title, result: interpolateOutcome(item.resultBody, 'Альва', gift.accusativeTitle).replaceAll('(подарок)', gift.accusativeTitle).split('\n\n'), score: item.score, accessibleDescription: '' }));
  const option = options.find(item => item.id === (pending ?? result));
  const copy = result ? option?.result ?? [] : option ? [choiceLabel(option.label), ...(option.accessibleDescription ? [option.accessibleDescription] : [])] : situationPages;
  const shownPage = Math.min(page, Math.max(0, copy.length - 1));
  const panelOpen = !!pending || !!result || situation;
  const Art = scene?.Art;
  const auto = options.find(item => ['auto', 'express'].includes(item.id));
  const restoreFocus = () => { setPending(undefined); setSituation(false); setPage(0); queueMicrotask(() => trigger.current?.focus({ preventScroll: true })); };
  const choose = (id: string) => { trigger.current = document.activeElement as HTMLElement; setPending(id); setResult(undefined); setSituation(false); setRoute(false); setPage(0); };
  const changeScene = (index: number) => { setStep(index); setPending(undefined); setResult(undefined); setSituation(false); setRoute(false); setPage(0); setPanHint(true); };
  useLayoutEffect(() => {
    const element = root.current;
    const task = element?.querySelector<HTMLElement>('.rv-task');
    const sheet = element?.querySelector<HTMLElement>('.rv-sheet');
    if (!element || !task) return;
    let frame = 0;
    const fit = () => {
      const taskBottom = task.getBoundingClientRect().bottom;
      element.style.setProperty('--rv-scene-top', `${taskBottom + 8}px`);
      element.style.setProperty('--rv-sheet-limit', `${Math.max(180, window.innerHeight - taskBottom - 140)}px`);
      element.style.setProperty('--rv-scene-bottom', sheet ? `${window.innerHeight - sheet.getBoundingClientRect().top + 8}px` : '0px');
      if (pending && window.innerWidth <= 700) {
        cancelAnimationFrame(frame);
        frame = requestAnimationFrame(() => {
          const viewport = element.querySelector<HTMLElement>('[data-pan-viewport]');
          const mark = element.querySelector<HTMLElement>(`[data-hotspot="${pending}"], [data-carrier-choice="${pending}"]`);
          if (viewport && mark) {
            const rect = mark.getBoundingClientRect();
            const port = viewport.getBoundingClientRect();
            viewport.scrollLeft += rect.left + rect.width / 2 - port.left - port.width / 2;
          }
        });
      }
    };
    fit();
    const observer = new ResizeObserver(fit);
    observer.observe(task);
    if (sheet) observer.observe(sheet);
    window.addEventListener('resize', fit);
    return () => { observer.disconnect(); window.removeEventListener('resize', fit); cancelAnimationFrame(frame); };
  }, [step, parcel, pending, result, situation, page]);
  useEffect(() => { if (panelOpen) panelHeading.current?.focus({ preventScroll: true }); }, [pending, result, situation]);
  useEffect(() => {
    const viewport = root.current?.querySelector('[data-pan-viewport]');
    if (!viewport) return;
    const dismiss = () => setPanHint(false);
    viewport.addEventListener('scroll', dismiss, { passive: true });
    return () => viewport.removeEventListener('scroll', dismiss);
  }, [step]);

  return <div className="rv" ref={root} data-review-scene={step} data-review-inspecting={pending ? true : undefined} onKeyDown={event => { if (event.key === 'Escape') { if (route) setRoute(false); else restoreFocus(); } }}>
    <div className="rv-art" key={`${step}-${parcel}`}>
      {Art ? <Art context={context} selectedId={pending ?? result} showResult={false} onSelect={choose} /> : <CityMap mode="live" selectedId={(pending ?? result) as CarrierId | undefined} onSelect={choose} />}
    </div>
    <header className="rv-header">
      <div className="rv-brands"><img src="/brand/energy-plus-logo.svg" alt="Энергия+" /><span /><img src="/brand/gpn-snabzhenie.svg" alt="Газпромнефть-Снабжение" /></div>
      <button className="rv-route" aria-label="Маршрут" aria-expanded={route} onClick={() => setRoute(!route)}><b>{String(step + 1).padStart(2, '0')}<span> / 05</span></b><span>Маршрут <i aria-hidden="true">⌄</i></span></button>
    </header>
    {route && <nav className="rv-route-panel" aria-label="Этапы маршрута">
      <p>Путь подарка</p>{tabs.map((tab, index) => <button key={tab} aria-label={tab} aria-current={step === index ? 'step' : undefined} onClick={() => changeScene(index)}><span>0{index + 1}</span>{tab}</button>)}
      <label>Подарок<select value={parcel} onChange={event => { setParcel(event.target.value as ParcelId); setPending(undefined); setResult(undefined); setPage(0); }}>{parcels.map(item => <option key={item.id} value={item.id}>{item.title}</option>)}</select></label>
      <small>Отдельный вариант интерфейса · сохранение игры отключено</small>
    </nav>}
    <section className="rv-task" aria-label="Задача сцены">
      <div className="rv-task-top"><h1>{titles[step]}</h1><button aria-expanded={situation} onClick={() => { trigger.current = document.activeElement as HTMLElement; setSituation(!situation); setPending(undefined); setResult(undefined); setPage(0); }}>Ситуация <span aria-hidden="true">↗</span></button></div>
      <p data-testid="question">{question}</p>
      {auto && !panelOpen && <button className="rv-auto" onClick={() => choose(auto.id)}>✧ Автоподбор</button>}
    </section>
    {panHint && !panelOpen && <div className="rv-pan-hint" aria-hidden="true">↔ <span>Листайте сцену</span></div>}
    {panelOpen && <section className="rv-sheet" aria-label={situation ? 'Ситуация' : result ? 'Результат выбора' : 'Описание варианта'} data-testid={result ? 'result' : situation ? 'situation' : 'inspection'}>
      <div className="rv-sheet-top"><span>{situation ? 'Ситуация' : result ? 'Результат' : 'Перед выбором'}</span><button className="rv-close" aria-label="Закрыть карточку" onClick={() => { restoreFocus(); setResult(undefined); }}>×</button></div>
      <h2 ref={panelHeading} tabIndex={-1}>{situation ? titles[step] : captions[pending ?? result ?? '']}</h2>
      <div className="rv-copy" key={`${pending}-${result}-${situation}-${shownPage}`}>
        {!scene && pending && pending !== 'express' ? <CarrierInspection carrierId={pending as CarrierId} /> : <p>{copy[shownPage]}</p>}
      </div>
      {copy.length > 1 && !(!scene && pending && pending !== 'express') && <div className="rv-pages"><button aria-label="Предыдущий фрагмент" disabled={shownPage === 0} onClick={() => setPage(shownPage - 1)}>←</button><span>{shownPage + 1} / {copy.length}</span><button aria-label="Следующий фрагмент" disabled={shownPage === copy.length - 1} onClick={() => setPage(shownPage + 1)}>→</button></div>}
      <div className="rv-actions">
        {situation ? <button className="rv-primary" onClick={restoreFocus}>К сцене <span aria-hidden="true">→</span></button> : result ? <><button onClick={() => { setResult(undefined); setPage(0); }}>Изменить выбор</button><button className="rv-primary" onClick={() => changeScene((step + 1) % 5)}>Дальше <span aria-hidden="true">→</span></button></> : <><button aria-label="К вариантам" onClick={restoreFocus}><span aria-hidden="true">←</span> Назад</button><button className="rv-primary" onClick={() => { setResult(pending); setPending(undefined); setPage(0); }}><span aria-hidden="true">✓</span> Выбрать</button></>}
      </div>
    </section>}
  </div>;
}
createRoot(document.getElementById('review-root')!).render(<Preview />);
