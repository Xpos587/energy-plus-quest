import {expect,it} from 'vitest';
import {renderToStaticMarkup} from 'react-dom/server';
import {warehouseShelfRanges,warehouseZone} from './warehouseZones';
import {warehouseCallouts,warehouseContour} from './callouts';
import {WarehouseZones} from './WarehouseZones';

it('starts the alphabet at receiving (left) and places each gift in its bay',()=>{
 expect(warehouseShelfRanges.map(r=>r.label)).toEqual(['А–Б','В–К','Л–М','Н–У','Ф–Э','Ю–Я']);
 warehouseShelfRanges.slice(1).forEach((r,i)=>expect(r.x).toBeGreaterThan(warehouseShelfRanges[i].x));
 const p=(gift:'camera'|'socks'|'boat')=>warehouseContour('alphabet',gift).anchorPixel;
 expect(p('boat')[0]).toBeLessThan(p('socks')[0]);
 expect(p('socks')[0]).toBeLessThan(p('camera')[0]);
 expect(warehouseZone('alphabet',{parcel:'camera',recipient:'alva',profile:'student'}).description).toContain('приёмки');
});
it('uses the portrait source coordinates for tall composition without changing wide default',()=>{
 expect(warehouseContour('alphabet','camera','tall').anchorPixel).toEqual([631,319]);
 expect(warehouseContour('alphabet','socks','tall').anchorPixel).toEqual([498,338]);
 expect(warehouseContour('alphabet','boat','tall').anchorPixel).toEqual([420,349]);
 expect(warehouseCallouts('camera','tall').alphabet.x).toBeCloseTo(631/1024);
 const html=renderToStaticMarkup(<WarehouseZones context={{parcel:'camera',recipient:'alva',profile:'student'}} composition="tall" onSelect={()=>{}}/>);
 expect(html).toContain('viewBox="0 0 1024 1536"');
 expect(html).toContain(warehouseContour('alphabet','camera','tall').path);
});
