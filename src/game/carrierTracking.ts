import frames from "./carrierTracking.json";

// Compare distance travelled over the complete video loop in camera
// coordinates. This is an ordering on the map, not a claim of real km/h.
const screenDistance = [0, 0, 0, 0];
for (let frame = 0; frame < frames.length; frame++) {
  const current = frames[frame];
  const next = frames[(frame + 1) % frames.length];
  for (let truck = 0; truck < 4; truck++) {
    screenDistance[truck] += Math.hypot(
      (next[truck][0] - current[truck][0]) * 1.44,
      next[truck][1] - current[truck][1],
    );
  }
}
export const carrierSpeedRank = screenDistance.map(
  (distance) => 1 + screenDistance.filter((other) => other > distance).length,
);

// Roof centers exported from the exact Blender animation used by city-motion.
// All three encodes preserve the same uncropped 1.44:1 camera plane, 24 fps.
export function carrierFrame(mediaTime: number) {
  const index = Number.isFinite(mediaTime)
    ? Math.floor(Math.max(0, mediaTime) * 24) % frames.length
    : 0;
  return frames[index];
}

// Half-second travelled distance suppresses single-frame tracking noise.
// One shared range for all trucks; camera coordinates have no km/h calibration.
const windowFrames = 12;
function paceAt(frame: number, truck: number) {
  let distance = 0;
  for (let step = 0; step < windowFrames; step++) {
    const a = frames[(frame - step + frames.length) % frames.length][truck];
    const b = frames[(frame - step - 1 + frames.length) % frames.length][truck];
    distance += Math.hypot((a[0] - b[0]) * 1.44, a[1] - b[1]);
  }
  return distance;
}
const peakPace = Math.max(...frames.flatMap((_, frame) =>
  [0, 1, 2, 3].map(truck => paceAt(frame, truck))));
export function carrierMotionFraction(time: number, truck: number) {
  const frame = Math.floor(Math.max(0, time) * 24) % frames.length;
  return Math.min(1, paceAt(frame, truck) / peakPace);
}
