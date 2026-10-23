import { expect, test } from 'bun:test';
import { makeInventory } from './inventory';
test('queues canonical originals once, excludes explicit legacy, includes direct opening raster',()=>{
 const result=makeInventory({sources:[{source:'public/a.webp',uses:['choice']},{source:'public/a.webp',uses:['result']},{source:'public/old.png',uses:['legacy']},{source:'public/opening/parcel-heart-v2.webp',uses:['intro']}],excluded:['public/old.png'],previous:[]});
 expect(result.assets).toHaveLength(2);expect(result.assets[0].uses).toEqual(['choice','result']);expect(result.assets.some(x=>x.source.includes('parcel-heart'))).toBe(true);
});
test('resuming preserves stable IDs and processing state when sorted source order changes',()=>{
 const first=makeInventory({sources:[{source:'public/z.webp',uses:['scene']}],excluded:[],previous:[]});first.assets[0].processingStatus='p1_in_progress';
 const next=makeInventory({sources:[{source:'public/a.webp',uses:['new']},{source:'public/z.webp',uses:['scene']}],excluded:[],previous:first.assets});
 expect(next.assets.find(x=>x.source==='public/z.webp')?.id).toBe(first.assets[0].id);expect(next.assets.find(x=>x.source==='public/z.webp')?.processingStatus).toBe('p1_in_progress');expect(new Set(next.assets.map(x=>x.id)).size).toBe(2);
});
