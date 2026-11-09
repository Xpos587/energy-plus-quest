import {expect,it} from 'vitest';
import {renderToStaticMarkup} from 'react-dom/server';
import {warehouseShelfRanges,warehouseZone} from './warehouseZones';
import {warehouseCallouts,warehouseContour} from './callouts';
import {WarehouseZones} from './WarehouseZones';

it('starts the alphabet at receiving (left) and places each gift in its bay',()=>{
 expect(warehouseShelfRanges.map(r=>r.label)).toEqual(['А–Б','В–К','Л–М','Н–У','Ф–Э','Ю–Я']);
 warehouseShelfRanges.slice(1).forEach((r,i)=>expect(r.x).toBeGreaterThan(warehouseShelfRanges[i].x));
 const p=(gift:'camera'|'socks'|'boat')=>warehouseContour('alphabet',gift).anchorPixel;
 expect(p('camera')[0]).toBeGreaterThan(1672/2);
 expect(p('boat')[0]).toBeLessThan(p('socks')[0]);
 expect(warehouseZone('alphabet',{parcel:'camera',recipient:'alva',profile:'student'}).description).toContain('приёмки');
});
it('gives the tall phone plate its own coordinate plane with the same reading order',()=>{
 const t=(gift:'camera'|'socks'|'boat')=>warehouseContour('alphabet',gift,'tall').anchorPixel[0];
 expect(t('boat')).toBeLessThan(t('socks'));expect(t('socks')).toBeLessThan(t('camera'));
 expect(warehouseCallouts('camera','tall').alphabet.x).toBeCloseTo(745/1200,2);
 const html=renderToStaticMarkup(<WarehouseZones context={{parcel:'camera',recipient:'alva',profile:'student'}} composition="tall" onSelect={()=>{}}/>);
 expect(html).toContain('viewBox="0 0 1200 1750"');
 expect(html).toContain(warehouseContour('alphabet','camera','tall').path);
});
