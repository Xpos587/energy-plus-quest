import { expect, test } from 'bun:test';
import { patchMedia } from './media_patch';
test('changes only canonical fallback and responsive values', () => {
 const js='const ui="keep",a={"scene/x.webp":"./old.webp"},b={"scene/x.webp":{webp:"./old.webp"}};';
 const result=patchMedia(js, {'scene/x.webp':{fallback:'./new.webp',responsive:{webp:'./new.webp'}}});
 expect(result.code).toContain('const ui="keep"');
 expect(result.patches).toHaveLength(2);
 expect(result.nonMediaBytesPreserved).toBe(true);
 expect(result.code).not.toContain('./old.webp');
});
test('missing published source refuses overlay', () => {
 expect(()=>patchMedia('const ui=1;',{'missing':{fallback:'x',responsive:{}}})).toThrow();
});
test('ambiguous canonical property refuses overlay', () => {
 expect(()=>patchMedia('const a={"x":1},b={"x":"old"},c={"x":{}};',{'x':{fallback:'new',responsive:{}}})).toThrow();
});
