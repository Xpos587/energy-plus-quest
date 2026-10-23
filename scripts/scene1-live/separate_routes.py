"""Generate and certify district routes from archived evaluated vehicle geometry.

Run with a Python environment containing numpy and shapely:
  uv run --python ENV/bin/python --no-project python SCRIPT ARCHIVE OUTPUT
No scene assets or review-file metadata are changed by this step.
"""
import json
import math
import pickle
import sys
from pathlib import Path

import numpy as np
import shapely as sh
from shapely.geometry import MultiPoint, box

archive, output = map(Path, sys.argv[1:3])
output.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(archive))
from audit_geometry import load

cache = output/'local-geometry-cache.pickle'
if cache.exists():
    scene, objects, footprints, road, static = pickle.loads(cache.read_bytes())
else:
    scene, objects, footprints, road, static = load('fixed')
    cache.write_bytes(pickle.dumps((scene, objects, footprints, road, static)))
N = 1152
DURATION = 48
LOT = box(-51.8, -21.8, -32.15, 23.2)


def length(spec):
    left, right, bottom, top, radius = spec
    return 2 * (right-left+top-bottom-4*radius) + 2*math.pi*radius


def at(spec, distance):
    left, right, bottom, top, radius = spec
    distance %= length(spec)
    segments = [
        ('line', (left+radius, bottom), (right-radius, bottom)),
        ('arc', (right-radius, bottom+radius), (-math.pi/2, 0)),
        ('line', (right, bottom+radius), (right, top-radius)),
        ('arc', (right-radius, top-radius), (0, math.pi/2)),
        ('line', (right-radius, top), (left+radius, top)),
        ('arc', (left+radius, top-radius), (math.pi/2, math.pi)),
        ('line', (left, top-radius), (left, bottom+radius)),
        ('arc', (left+radius, bottom+radius), (math.pi, 3*math.pi/2)),
    ]
    for kind, start, end in segments:
        span = math.dist(start, end) if kind == 'line' else radius*math.pi/2
        if distance <= span:
            angle = math.atan2(end[1]-start[1], end[0]-start[0]) if kind == 'line' else end[0]+distance/radius
            vector = np.array((math.cos(angle), math.sin(angle)))
            return (np.array(start)+distance*vector, angle) if kind == 'line' else (np.array(start)+radius*vector, angle+math.pi/2)
        distance -= span


def motion(spec, laps, warehouse_pace=0):
    theta, previous, poses = 0., None, []
    distances = np.linspace(0, length(spec), 4097)
    xs = np.array([at(spec, d)[0][0] for d in distances])
    weights = 1+warehouse_pace*np.exp(-((xs+29.8)/10)**2)
    times = np.concatenate(([0], np.cumsum((weights[:-1]+weights[1:])/2)))
    times /= times[-1]
    for step in range(-N*24, N*8):
        progress = (laps*step/(N*8)) % 1
        position, angle = at(spec, np.interp(progress, times, distances))
        if laps < 0:
            angle += math.pi
        hitch = position-3.036*np.array((math.cos(angle), math.sin(angle)))
        if previous is not None:
            dx, dy = hitch-previous
            theta += (dy*math.cos(theta)-dx*math.sin(theta))/7.062
        previous = hitch
        if step >= 0 and step % 8 == 0:
            poses.append([[*position, 0, angle], [*hitch, 0, theta]])
    return np.array(poses)


hulls = [np.array(MultiPoint((np.array(t['vertices'])*t['scale'])[:, :2]).convex_hull.exterior.coords)[:-1]
         for t in scene['trucks']]


def polygons(poses, index):
    result = []
    for part in range(2):
        angle = poses[:, part, 3]
        c, s = np.cos(angle), np.sin(angle)
        rotations = np.stack((c, -s, s, c), axis=-1).reshape(-1, 2, 2)
        result.append(sh.polygons(np.einsum('nij,kj->nki', rotations, hulls[index*2+part])+poses[:, part, None, :2]))
    return np.stack(result, axis=1)


specs = [
    [-1.8, 29.8, -9.8, 29.8, 12],
    [-29.8, 1.8, -6.2, 29.8, 12],
    [-1.8, 29.8, -29.8, 29.8, 12],
    [-1.8, 29.8, -29.8, -6.2, 11.8],
]
laps = [2, 1, 2, 2]
warehouse_pace = 2
if len(sys.argv) > 3:
    configuration = json.loads(Path(sys.argv[3]).read_text())
    specs, laps = configuration['specs'], configuration['laps']
    DURATION = configuration.get('duration', DURATION)
    N = DURATION*24
    warehouse_pace = configuration.get('warehouse_pace', 0)
poses = [motion(spec, lap, warehouse_pace if i == 1 else 0) for i, (spec, lap) in enumerate(zip(specs, laps))]
bodies = [polygons(p, i) for i, p in enumerate(poses)]
obstacles = sh.union_all(list(static.values()))
for i, body in enumerate(bodies):
    envelope = sh.union_all(body)
    offroad = float(sh.area(sh.difference(envelope, road)))
    hits = [name for name, footprint in static.items() if sh.intersects(envelope, footprint)]
    print('ROUTE', i+1, 'offroad', offroad, 'obstacles', hits, flush=True)
    assert offroad < .001 and not hits, (i+1, offroad, hits)

# Search start phases over the actual tractor and trailer hulls, not point centers.
steps = list(range(0, N, 8))
compatibility = {}
for i in range(4):
    for j in range(i+1, 4):
        compatibility[i, j] = np.array([
            float(sh.distance(bodies[i][:, :, None], np.roll(bodies[j], -phase, axis=0)[:, None, :]).min())
            for phase in steps])
        print('PAIR BEST', i+1, j+1, float(compatibility[i, j].max()), flush=True)


def gap(i, j, first, second):
    return compatibility[i, j][((second-first) % N)//8]


near = min(steps, key=lambda k: np.linalg.norm(poses[1][k, 0, :2]-[-29.8, 18]))
best = (-1, None)
for first in steps:
    for third in steps:
        base = min(gap(0, 1, first, near), gap(0, 2, first, third), gap(1, 2, near, third))
        if base <= best[0]:
            continue
        gaps = np.minimum.reduce([
            np.full(len(steps), base),
            gap(0, 3, first, np.array(steps)),
            gap(1, 3, near, np.array(steps)),
            gap(2, 3, third, np.array(steps)),
        ])
        index = int(np.argmax(gaps))
        if gaps[index] > best[0]:
            best = (float(gaps[index]), [first, near, third, steps[index]])
print('PHASES', best, flush=True)
assert best[0] > .3, best
chosen = np.concatenate([np.roll(p, -phase, axis=0) for p, phase in zip(poses, best[1])], axis=1)
for k in range(8):
    chosen[:, k, 3] = np.unwrap(chosen[:, k, 3])
endpoint = chosen[0].copy()
endpoint[:, 3] += np.repeat(laps, 2)*2*np.pi
chosen = np.concatenate((chosen, endpoint[None]))

# Conservative enclosures of every consecutive rendered-key interval, including wrap.
sweeps = []
for i in range(4):
    body = polygons(chosen[:, i*2:i*2+2], i)
    for part in range(2):
        h = hulls[i*2+part]
        delta = np.abs(np.diff(chosen[:, i*2+part, 3]))
        error = float((np.max(np.linalg.norm(h, axis=1))*(1-np.cos(delta/2))).max())+.0001
        sweeps.append(sh.buffer(sh.convex_hull(sh.union(body[:-1, part], body[1:, part])), error))
offroad = [int((sh.area(sh.difference(sweep, road)) > .001).sum()) for sweep in sweeps]
collisions = [int(sh.intersects(sweep, obstacles).sum()) for sweep in sweeps]
inlot = [int(sh.intersects(sweep, LOT).sum()) for sweep in sweeps]
pair = min(float(sh.distance(sweeps[a], sweeps[b]).min())
           for i in range(4) for j in range(i+1, 4)
           for a in (2*i, 2*i+1) for b in (2*j, 2*j+1))
distances = [sh.distance(sh.union(sweeps[i*2], sweeps[i*2+1]), LOT) for i in range(4)]
key_distances = []
for i in range(4):
    body = polygons(chosen[:, i*2:i*2+2], i)
    key_distances.append(sh.distance(sh.union(body[:, 0], body[:, 1]), LOT))
near_margin = np.min(np.array(key_distances)[[0, 2, 3]], axis=0)-key_distances[1]
articulation = max(float(np.abs((chosen[:, 2*i, 3]-chosen[:, 2*i+1, 3]+np.pi) % (2*np.pi)-np.pi).max()*180/np.pi) for i in range(4))
hitch = max(float(np.linalg.norm(chosen[:, 2*i, :2]-3.036*np.stack((np.cos(chosen[:, 2*i, 3]), np.sin(chosen[:, 2*i, 3])), axis=1)-chosen[:, 2*i+1, :2], axis=1).max()) for i in range(4))
report = {
    'specs': specs, 'laps_per_cycle': laps, 'phases': best[1], 'fps': 24, 'frames': N, 'duration': DURATION,
    'roles': ['1 upper far district', '2 warehouse-side district', '3 far perimeter', '4 lower far district'],
    'mean_speeds_scene_units_per_second': [length(s)*abs(lap)/DURATION for s, lap in zip(specs, laps)],
    'warehouse_pace': warehouse_pace,
    'nearest_truck_2_on_all_keyframes': bool((near_margin > 0).all()),
    'minimum_near_far_distance_margin': float(near_margin.min()),
    'speed_ranges': [[float(v.min()), float(v.max())] for v in [np.linalg.norm(np.diff(chosen[:, i*2, :2], axis=0), axis=1)*24 for i in range(4)]],
    'offroad_swept_intervals': offroad, 'static_collision_intervals': collisions,
    'warehouse_lot_swept_intervals': inlot, 'pair_clearance_min': pair,
    'warehouse_distance_min': [float(d.min()) for d in distances],
    'warehouse_distance_max': [float(d.max()) for d in distances],
    'trucks_ever_within_25_scene_units_of_warehouse': [i+1 for i, d in enumerate(distances) if d.min() < 25],
    'max_articulation_degrees': articulation, 'hitch_error': hitch,
    'loop_position_error': float(np.abs(chosen[0, :, :2]-chosen[-1, :, :2]).max()),
    'method': 'Actual evaluated local mesh convex hulls. Every linear-key interval enclosed with angular interpolation error buffer. Scene units, not real-world meters.',
}
report['passed'] = not any(offroad+collisions+inlot) and pair > .1 and articulation < 65 and hitch < .001 and report['trucks_ever_within_25_scene_units_of_warehouse'] == [2]
speeds = report['mean_speeds_scene_units_per_second']
report['passed'] = report['passed'] and speeds[1] < min(speeds[0], speeds[2], speeds[3]) and specs[0] != specs[3] and report['nearest_truck_2_on_all_keyframes']
(output/'route-check.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2), flush=True)
assert report['passed']
np.save(output/'motion.npy', chosen)
