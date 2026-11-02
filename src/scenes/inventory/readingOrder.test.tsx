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
it('uses one illustrated coordinate plane for wide and tall layouts',()=>{
 for(const gift of ['camera','socks','boat'] as const)expect(warehouseContour('alphabet',gift,'tall')).toEqual(warehouseContour('alphabet',gift,'wide'));
 expect(warehouseCallouts('camera','tall').alphabet.x).toBeCloseTo(1065/1672,2);
 const html=renderToStaticMarkup(<WarehouseZones context={{parcel:'camera',recipient:'alva',profile:'student'}} composition="tall" onSelect={()=>{}}/>);
 expect(html).toContain('viewBox="0 0 1672 941"');
 expect(html).toContain(warehouseContour('alphabet','camera','tall').path);
});
