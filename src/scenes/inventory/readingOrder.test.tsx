import {expect,it} from 'vitest';
import {renderToStaticMarkup} from 'react-dom/server';
import {warehouseShelfRanges,warehouseZone} from './warehouseZones';
import {warehouseCallouts,warehouseContour} from './callouts';
import {WarehouseZones} from './WarehouseZones';

it('starts the alphabet at dispatch (right) and places each gift in its bay',()=>{
 expect(warehouseShelfRanges.map(r=>r.label)).toEqual(['А–Б','В–К','Л–М','Н–У','Ф–Э','Ю–Я']);
 warehouseShelfRanges.slice(1).forEach((r,i)=>expect(r.x).toBeLessThan(warehouseShelfRanges[i].x));
 const p=(gift:'camera'|'socks'|'boat')=>warehouseContour('alphabet',gift).anchorPixel;
 expect(p('camera')[0]).toBeLessThan(500);
 expect(p('socks')[0]).toBeLessThan(p('boat')[0]);
 expect(warehouseZone('alphabet',{parcel:'camera',recipient:'alva',profile:'student'}).description).toContain('отгрузки');
});
it('uses one illustrated coordinate plane for wide and tall layouts',()=>{
 expect(warehouseContour('alphabet','camera','tall').anchorPixel).toEqual([481,383]);
 expect(warehouseContour('alphabet','socks','tall').anchorPixel).toEqual([730,441]);
 expect(warehouseContour('alphabet','boat','tall').anchorPixel).toEqual([798,462]);
 expect(warehouseCallouts('camera','tall').alphabet.x).toBeCloseTo(481/1672);
 const html=renderToStaticMarkup(<WarehouseZones context={{parcel:'camera',recipient:'alva',profile:'student'}} composition="tall" onSelect={()=>{}}/>);
 expect(html).toContain('viewBox="0 0 1672 941"');
 expect(html).toContain(warehouseContour('alphabet','camera','tall').path);
});
