import { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { createPortal } from 'react-dom';
import { ScenesGame } from '../../src/scenes/ScenesGame';
import '../../src/index.css';
import './preview.css';
function Preview() {
  const [plane, setPlane] = useState<Element | null>(null);
  const [selected, setSelected] = useState(false);
  const [available, setAvailable] = useState(false);
  useEffect(() => {
    const update = () => {
      const artwork = document.querySelector('[data-cargo-view] image');
      if (artwork && artwork.getAttribute('href') !== '/design/compact-object-choice/compact-integrated.png') artwork.setAttribute('href', '/design/compact-object-choice/compact-integrated.png');
      const heading = document.querySelector('[data-choice-inspection="compact:auto"] h3');
      if (heading && heading.textContent !== 'Система Compact') heading.textContent = 'Система Compact';
      const trigger = document.querySelector<HTMLButtonElement>('[data-testid="scene-question"] [data-choice-id="auto"]');
      setPlane(document.querySelector('[data-world-scene="compact"] [data-world-plane]'));
      setAvailable(!!trigger && !document.querySelector('[data-testid="scene-intro"]'));
      setSelected(trigger?.getAttribute('aria-pressed') === 'true');
    };
    const observer = new MutationObserver(update);
    observer.observe(document.getElementById('root')!, {subtree:true, childList:true, attributes:true, attributeFilter:['aria-pressed']});
    update();
    return () => observer.disconnect();
  }, []);
  return <div data-object-preview><ScenesGame startAt="compact" context={{parcel:'camera',recipient:'alva',profile:'student'}} />
    {plane && available && createPortal(<button className="compact-terminal" title="Система Compact" aria-label="Определить место автоматически — система Compact" aria-pressed={selected} onClick={() => document.querySelector<HTMLButtonElement>('[data-testid="scene-question"] [data-choice-id="auto"]')?.click()}>
    </button>, plane)}
  </div>;
}
createRoot(document.getElementById('root')!).render(<Preview />);
