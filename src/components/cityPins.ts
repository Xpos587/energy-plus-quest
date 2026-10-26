import { carrierFacts, type MapCarrierId } from "../game/carrierFacts";

// Screen-space markers drawn over the scene 1 city (cityV4): rig pins with a
// small pace dial, the warehouse pill and the sparkle used by the Express
// arrival. Sizes are CSS pixels; the caller scales for the pin size.

export const carrierColors = {
  old: "#d8452c",
  near: "#2f7fe0",
  crew: "#22a447",
  old4: "#e8ad0c",
} as const;

export function rr(
  c: CanvasRenderingContext2D,
  x: number,
  y: number,
  w: number,
  h: number,
  r: number,
) {
  c.beginPath();
  c.roundRect(x, y, w, h, r);
}

export function sparkle(
  c: CanvasRenderingContext2D,
  x: number,
  y: number,
  r: number,
  color = "#fff7c2",
) {
  c.fillStyle = color;
  c.beginPath();
  c.moveTo(x, y - r);
  c.quadraticCurveTo(x, y, x + r, y);
  c.quadraticCurveTo(x, y, x, y + r);
  c.quadraticCurveTo(x, y, x - r, y);
  c.quadraticCurveTo(x, y, x, y - r);
  c.fill();
}

/** Relative city pace 0..1: the fastest rig sits near the right stop. */
export const paceFraction = (id: MapCarrierId) => {
  const max = Math.max(
    ...Object.values(carrierFacts).map((f) => f.citySpeedKmh),
  );
  return carrierFacts[id].citySpeedKmh / (max * 1.08);
};

/** Rig marker: the same small speedometer over every cab. The needle shows
 * how fast the rig moves through the city; no numbers. The green rig adds a
 * two-driver badge. Tail touches (x, y). */
export function rigPin(
  c: CanvasRenderingContext2D,
  id: MapCarrierId,
  x: number,
  y: number,
  s: number,
) {
  c.save();
  // Snap to whole CSS pixels: a sub-pixel pin blurs its thin ticks.
  c.translate(Math.round(x), Math.round(y));
  c.scale(s, s);
  const color = carrierColors[id];
  const r = 15;
  const cy = -r - 6;
  // shadow, tail, white disc with a coloured rim
  c.fillStyle = "rgba(10,30,50,0.18)";
  c.beginPath();
  c.arc(0.8, cy + 1.6, r, 0, Math.PI * 2);
  c.fill();
  c.beginPath();
  c.moveTo(-5, cy + r - 2);
  c.lineTo(0, 0);
  c.lineTo(5, cy + r - 2);
  c.closePath();
  c.fillStyle = color;
  c.fill();
  c.beginPath();
  c.arc(0, cy, r, 0, Math.PI * 2);
  c.fillStyle = "#fff";
  c.fill();
  c.lineWidth = 2.5;
  c.strokeStyle = color;
  c.stroke();
  // Dial: a 240° speedometer (grey track, navy fill up to the pace) that is
  // concentric with the disc: hub on the disc centre and the arc an even
  // ring inside the rim, so the pin reads round and level at any needle.
  const R = 10.4;
  const lw = 2.6;
  const start = (150 * Math.PI) / 180;
  const sweep = (240 * Math.PI) / 180;
  const gy = cy;
  const f = paceFraction(id);
  c.lineCap = "butt";
  c.lineWidth = lw;
  c.strokeStyle = "#dfe7ee";
  c.beginPath();
  c.arc(0, gy, R, start, start + sweep);
  c.stroke();
  c.strokeStyle = "#1f4f7a";
  c.beginPath();
  c.arc(0, gy, R, start, start + sweep * f);
  c.stroke();
  c.lineWidth = 1.1;
  c.strokeStyle = "#8aa0b3";
  c.lineCap = "round";
  for (let t = 0; t <= 4; t++) {
    const a = start + (sweep * t) / 4;
    const r0 = R - lw / 2 - 2.4;
    const r1 = R - lw / 2 - 0.9;
    c.beginPath();
    c.moveTo(Math.cos(a) * r0, gy + Math.sin(a) * r0);
    c.lineTo(Math.cos(a) * r1, gy + Math.sin(a) * r1);
    c.stroke();
  }
  const na = start + sweep * f;
  const nl = R - lw / 2 - 1.2;
  c.strokeStyle = "#e0451f";
  c.lineWidth = 1.8;
  c.beginPath();
  c.moveTo(-Math.cos(na) * 1.6, gy - Math.sin(na) * 1.6);
  c.lineTo(Math.cos(na) * nl, gy + Math.sin(na) * nl);
  c.stroke();
  c.fillStyle = "#1f2b3c";
  c.beginPath();
  c.arc(0, gy, 1.9, 0, Math.PI * 2);
  c.fill();
  if (id === "crew") {
    // two drivers: a small badge on the pin's shoulder
    const bx = r + 3;
    const by = cy - r + 4;
    c.fillStyle = color;
    c.beginPath();
    c.arc(bx, by, 7.5, 0, Math.PI * 2);
    c.fill();
    c.lineWidth = 1.5;
    c.strokeStyle = "#fff";
    c.stroke();
    c.fillStyle = "#fff";
    for (const dx of [-2.4, 2.4]) {
      c.beginPath();
      c.arc(bx + dx, by - 1.8, 1.6, 0, Math.PI * 2);
      c.fill();
      c.beginPath();
      c.arc(bx + dx, by + 3.6, 2.7, Math.PI, 0);
      c.fill();
    }
  }
  c.restore();
}

/** Warehouse marker: one pill with the orange cargo box and "СКЛАД", its
 * tail touching (x, y). Replaces the separate sign tag and cargo pin. */
export function depotPill(
  c: CanvasRenderingContext2D,
  x: number,
  y: number,
  s: number,
  bob = 0,
) {
  c.save();
  c.translate(x, y - bob * s);
  c.scale(s, s);
  c.font = '700 13px "Roboto Condensed", Arial, sans-serif';
  const label = "СКЛАД";
  const tw = c.measureText(label).width;
  const h = 26;
  const icon = 20;
  const w = 4 + icon + 6 + tw + 10;
  const top = -h - 6;
  const left = -w / 2;
  c.fillStyle = "rgba(10,30,50,0.2)";
  rr(c, left + 1, top + 2, w, h, h / 2);
  c.fill();
  c.beginPath();
  c.moveTo(-5, top + h - 1);
  c.lineTo(0, 0);
  c.lineTo(5, top + h - 1);
  c.closePath();
  c.fillStyle = "#0057b8";
  c.fill();
  c.fillStyle = "#fff";
  c.strokeStyle = "#0057b8";
  c.lineWidth = 2;
  rr(c, left, top, w, h, h / 2);
  c.fill();
  c.stroke();
  // orange cargo disc with a white box outline
  const ix = left + 3 + icon / 2;
  const iy = top + h / 2;
  c.fillStyle = "#ff6a13";
  c.beginPath();
  c.arc(ix, iy, icon / 2, 0, Math.PI * 2);
  c.fill();
  c.strokeStyle = "#fff";
  c.lineWidth = 1.5;
  c.lineJoin = "round";
  c.beginPath();
  c.moveTo(ix, iy - 6);
  c.lineTo(ix + 5.5, iy - 3);
  c.lineTo(ix + 5.5, iy + 3.5);
  c.lineTo(ix, iy + 6.5);
  c.lineTo(ix - 5.5, iy + 3.5);
  c.lineTo(ix - 5.5, iy - 3);
  c.closePath();
  c.moveTo(ix - 5.5, iy - 3);
  c.lineTo(ix, iy);
  c.lineTo(ix + 5.5, iy - 3);
  c.moveTo(ix, iy);
  c.lineTo(ix, iy + 6.5);
  c.stroke();
  c.fillStyle = "#0057b8";
  c.textAlign = "left";
  c.textBaseline = "middle";
  c.fillText(label, ix + icon / 2 + 6, iy + 1);
  c.restore();
}
