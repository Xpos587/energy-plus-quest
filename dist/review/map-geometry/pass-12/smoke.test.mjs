import assert from 'node:assert/strict';
import { emitters, lifetime, cycle, smokeAt, smokeMarkup } from './smoke.mjs';
assert.deepEqual(emitters.map(e => e.truck), [1, 4]);
assert.throws(() => smokeAt(NaN), TypeError);
assert.throws(() => smokeAt(Infinity), TypeError);
// These anchors are the visible metal outlets beside the cabs, not trailer roofs.
assert.deepEqual(emitters.map(({x,y}) => [x,y]), [[311,88],[654,640]]);
for (let frame = 0; frame <= 768; frame++) {
  const seconds = frame / 24;
  const state = smokeAt(seconds);
  for (const truck of [1,4]) {
    const count = state.filter(puff => puff.truck === truck).length;
    assert(count >= 2 && count <= 6, 'Controlled, continuously legible pulse');
  }
  for (const puff of state) {
    const source = emitters.find(e => e.truck === puff.truck);
    assert(puff.x <= source.x && puff.x >= source.x + source.dx);
    assert(puff.y <= source.y && puff.y >= source.y + source.dy);
    assert(puff.radius >= 2.8 && puff.radius <= 13.3);
    assert(puff.opacity >= 0 && puff.opacity <= .88);
    assert(puff.age >= 0 && puff.age < lifetime);
  }
}
for (const seconds of [0,.48,.96,1.44,10.21]) {
  smokeAt(seconds).forEach((puff,index) => {
    const looped = smokeAt(seconds + cycle)[index];
    for (const key of ['x','y','radius','opacity']) assert(Math.abs(puff[key]-looped[key])<1e-8);
  });
}
assert.notEqual(smokeMarkup(.1), smokeMarkup(.6), 'Smoke must visibly evolve');
assert(!smokeMarkup(0).includes('data-truck="2"'));
assert(!smokeMarkup(0).includes('data-truck="3"'));
console.log('PASS: 769 deterministic frames; cab-side anchors; bounded drift, loop, opacity; old trucks only.');
