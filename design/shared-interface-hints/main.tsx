import { useEffect, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { createRoot } from 'react-dom/client';
import { ScenesGame } from '../../src/scenes/ScenesGame';
import { SceneBriefing } from '../../src/components/SceneBriefing';
import { ChoiceInspection } from '../../src/components/ChoiceInspection';
import { CarrierInspection } from '../../src/components/CarrierInspection';
import { CityMap } from '../../src/components/CityMap';
import { QuestHeader } from '../../src/components/QuestShell';
import { carrierBriefing, carrierQuestion, findCarrier } from '../../src/game/content';
import { carrierFacts } from '../../src/game/carrierFacts';
import { interpolateOutcome } from '../../src/game/outcomeText';
import type { CarrierId } from '../../src/game/types';
import type { SceneContext, SceneId } from '../../src/scenes/types';
import flow from '../../src/components/SceneInteraction.module.css';
import '../../src/index.css';
import './preview.css';

const context: SceneContext = { parcel: 'camera', recipient: 'alva', profile: 'student' };
const requested = new URLSearchParams(location.search).get('scene');
const stage = ['carrier', 'compact', 'inventory', 'crane', 'lastmile'].includes(requested ?? '') ? requested! : 'inventory';
const hints: Record<string, string> = {
  carrier: 'Нажмите на фуру, чтобы рассмотреть её.',
  compact: 'Нажмите на свободное место в кузове.',
  inventory: 'Нажмите на метку, чтобы рассмотреть вариант.',
  crane: 'Нажмите на метку, чтобы рассмотреть вариант.',
  lastmile: 'Нажмите на метку, чтобы рассмотреть вариант.',
};

function CarrierPreview() {
  const [pending, setPending] = useState<CarrierId>();
  const [result, setResult] = useState<CarrierId>();
  const sentences = carrierQuestion.split(/(?<=\.)\s+/);
  return <div className={flow.app} data-scene="carrier"><QuestHeader state={context} currentStep={0} /><main className={flow.main}><section className={flow.frame} data-interaction="inspect-confirm" data-inspecting={!!pending}>
    <SceneBriefing title="Перевозчик" question={sentences.at(-1)!.replace(/:\s*$/, '')} paragraphs={[interpolateOutcome(carrierBriefing, undefined, 'фотоаппарат'), ...sentences.slice(0, -1)]} inspecting={!!pending} onOpen={() => setPending(undefined)} action={<button onClick={() => setPending('express')}>Автоподбор</button>} />
    <div className={flow.carrierMap}><CityMap mode="live" selectedId={pending} onSelect={id => { setPending(id); setResult(undefined); }} /></div>
    {pending && <ChoiceInspection selectionKey={pending} title={pending === 'express' ? 'Автоматический подбор' : carrierFacts[pending].label} media={pending !== 'express'} onCancel={() => setPending(undefined)} onConfirm={() => { setResult(pending); setPending(undefined); }}><CarrierInspection carrierId={pending} /></ChoiceInspection>}
    {result && <section className={flow.result}><p>{interpolateOutcome(findCarrier(result)!.resultBody, 'Альва', 'фотоаппарат')}</p><button onClick={() => setResult(undefined)}>К вариантам</button></section>}
  </section></main></div>;
}

type Enhancement = { hintTarget: Element | null; questionTarget: Element | null; sheet: Element | null; question: string; hint: string };
function Preview() {
  const root = useRef<HTMLDivElement>(null);
  const [enhancement, setEnhancement] = useState<Enhancement>({ hintTarget: null, questionTarget: null, sheet: null, question: '', hint: '' });
  useEffect(() => {
    const element = root.current!;
    // Isolated UI experiment: the production components and their scenario strings are imported unchanged.
    const sync = () => {
      const question = element.querySelector('[data-testid="scene-question"]');
      const inspection = element.querySelector('[data-choice-inspection]');
      const next: Enhancement = {
        sheet: inspection,
        hintTarget: question?.firstElementChild ?? null,
        questionTarget: inspection?.querySelector('[data-inspection-question]') ? null : inspection,
        question: question?.querySelector('p')?.textContent ?? '',
        hint: hints[element.querySelector('[data-scene]')?.getAttribute('data-scene') ?? stage],
      };
      setEnhancement(previous => Object.keys(next).every(key => previous[key as keyof Enhancement] === next[key as keyof Enhancement]) ? previous : next);
    };
    sync();
    const observer = new MutationObserver(sync);
    observer.observe(element, { childList: true, subtree: true, characterData: true });
    return () => observer.disconnect();
  }, []);
  useEffect(() => {
    const element = root.current!;
    const sheet = element.querySelector<HTMLElement>('[data-choice-inspection]');
    if (!sheet) return;
    const place = () => {
      const bounds = sheet.getBoundingClientRect();
      element.style.setProperty('--review-task-right', `${innerWidth - bounds.right}px`);
      element.style.setProperty('--review-task-bottom', `${innerHeight - bounds.top + 8}px`);
      element.style.setProperty('--review-task-width', `${bounds.width}px`);
    };
    place();
    const observer = new ResizeObserver(place);
    observer.observe(sheet);
    window.addEventListener('resize', place);
    return () => { observer.disconnect(); window.removeEventListener('resize', place); };
  }, [enhancement]);
  return <div ref={root} data-hints-preview>
    {stage === 'carrier' ? <CarrierPreview /> : <ScenesGame context={context} startAt={stage as SceneId} />}
    {enhancement.hintTarget && createPortal(<span className="hint-control">{enhancement.hint}</span>, enhancement.hintTarget)}
    {enhancement.questionTarget && enhancement.question && createPortal(<p data-hint-question>{enhancement.question}</p>, enhancement.questionTarget)}
  </div>;
}
createRoot(document.getElementById('hint-preview')!).render(<Preview />);
