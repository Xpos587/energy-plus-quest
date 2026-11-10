import { expect, it } from 'vitest';
import { reframeCastBox } from './cast';

it('keeps existing character patches aligned when the Blender camera scales and shifts', () => {
  const box = { x: 80, y: 130, w: 40, h: 60 };
  const authored = [100, 100, 500] as const;
  expect(reframeCastBox(box, authored, authored)).toEqual(box);
  // Office anchor moves (100,100)→(50,80); the crane span shrinks to half.
  expect(reframeCastBox(box, authored, [50, 80, 250])).toEqual({ x: 40, y: 95, w: 20, h: 30 });
});
