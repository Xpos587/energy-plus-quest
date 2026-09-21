// Art-review only: stationary trucks, deterministic exhaust; no simulated routes.
export const emitters = [
  { truck: 1, x: 311, y: 88, dx: -35, dy: -39 },
  { truck: 4, x: 654, y: 640, dx: -30, dy: -43 },
];
export const lifetime = 1.92;
export const cycle = 3.2;
const births = [0, .32, .72, 1.25, 1.65, 2, 2.6];
export function smokeAt(seconds) {
  if (!Number.isFinite(seconds)) throw new TypeError('Finite smoke time required');
  return emitters.flatMap(emitter => births.flatMap(birth => {
    const offset = emitter.truck === 4 ? .14 : 0;
    const age = ((seconds - birth + offset) % cycle + cycle) % cycle;
    if (age >= lifetime) return [];
    const phase = age / lifetime;
    return [{
      truck: emitter.truck, age,
      x: emitter.x + emitter.dx * phase,
      y: emitter.y + emitter.dy * phase,
      radius: 2.8 + 10.5 * phase,
      opacity: .88 * (1 - phase) ** .5,
    }];
  }));
}
export function smokeMarkup(seconds) {
  return smokeAt(seconds).map(puff => `<g data-truck="${puff.truck}" opacity="${puff.opacity.toFixed(4)}" transform="translate(${puff.x.toFixed(3)} ${puff.y.toFixed(3)}) scale(${puff.radius.toFixed(3)})"><path d="M-1 .1C-1.25-.35-.8-.8-.43-.71C-.32-1.15 .38-1.13 .59-.63C1.12-.74 1.38-.14 1.04 .18C1.27 .64 .57 .95 .22 .65C-.19 1.02-.9 .72-1 .1Z" fill="#586d7b" stroke="#526776" stroke-width=".035"/><path d="M-.83-.14C-.85-.49-.49-.67-.2-.52C.04-.82 .49-.73 .56-.4" fill="none" stroke="#bfccd3" stroke-width=".17" stroke-linecap="round"/></g>`).join('');
}

if (typeof document !== 'undefined') {
  const layers = [...document.querySelectorAll('[data-smoke]')];
  const clock = document.querySelector('#clock');
  const toggle = document.querySelector('#toggle');
  const time = document.querySelector('#time');
  const explicitTime = new URLSearchParams(location.search).get('t');
  let seconds = explicitTime === null ? .4 : Number(explicitTime);
  if (!Number.isFinite(seconds)) seconds = .4;
  let playing = explicitTime === null && !matchMedia('(prefers-reduced-motion: reduce)').matches;
  let previous;
  function render() {
    for (const layer of layers) layer.innerHTML = smokeMarkup(seconds);
    clock.textContent = `${seconds.toFixed(2)} s`;
    time.value = String(seconds % cycle);
    toggle.textContent = playing ? 'Остановить дым' : 'Включить дым';
    toggle.setAttribute('aria-pressed', String(playing));
    document.documentElement.dataset.smokeTime = String(seconds);
  }
  toggle.addEventListener('click', () => { playing = !playing; render(); });
  time.addEventListener('input', () => { playing = false; seconds = Number(time.value); render(); });
  function tick(now) {
    if (playing && previous !== undefined) seconds = (seconds + (now - previous) / 1000) % cycle;
    previous = now;
    if (playing) render();
    requestAnimationFrame(tick);
  }
  render();
  requestAnimationFrame(tick);
}
