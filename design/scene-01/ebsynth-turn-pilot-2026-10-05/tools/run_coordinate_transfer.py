#!/usr/bin/env python3
"""Bounded, independent-key EbSynth turn trial; preserves native inputs."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
from pathlib import Path
import subprocess
import time

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2) + '\n')


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--style', type=Path, default=ROOT / 'style/key-0035.png')
    parser.add_argument('--keys', type=Path, nargs='+',
                        help='Exactly three registered key PNGs for frames 0000, 0035, 0071, in that order')
    parser.add_argument('--probe-only', action='store_true', help='Run frames 0036,0017,0054 before a full sequence')
    parser.add_argument('--wait-style', type=float, default=60)
    args = parser.parse_args()
    if args.keys and len(args.keys) != 3:
        parser.error('--keys requires three style PNGs in frame order 0000,0035,0071')
    key_paths = dict(zip(['0000', '0035', '0071'], args.keys)) if args.keys else {'0035': args.style}
    def key_for_frame(name: str) -> str:
        if not args.keys:
            return '0035'
        return '0000' if int(name) <= 17 else ('0035' if int(name) <= 53 else '0071')
    output = ROOT / 'transfer-coordinates'
    for directory in ['frames', 'prepared/rgb', 'prepared/gray', 'prepared/normal', 'prepared/alpha', 'prepared/coordinate', 'logs']:
        (output / directory).mkdir(parents=True, exist_ok=True)
    receipt = {'source_keys': list(key_paths), 'benchmark_target': '0036', 'width': 512,
               'guide_channels': ['RGB appearance', 'RGB world normal', 'RGB stable local generated coordinate'],
               'weights': {'style': 1, 'RGB guide': 1, 'normal guide': 1, 'coordinate guide': 4},
               'settings': {'backend': 'cpu', 'pyramidlevels': 3, 'searchvoteiters': 3,
                            'patchmatchiters': 4, 'patchsize': 5},
               'method': '72 targets independently synthesized from nearest registered frame key; no temporal propagation or crossfade',
               'key_ranges': {'0000': [0, 17], '0035': [18, 53], '0071': [54, 71]} if args.keys else {'0035': [0, 71]},
               'limitations': ['Discrete key switches may create temporal seams at frames 0018 and 0054'] if args.keys else ['One view supplies all target orientations'],
               'background': 'raw synthesis output; native alpha retained for parent compositing',
               'styles': {name: str(path) for name, path in key_paths.items()}, 'status': 'waiting for style'}
    receipt_path = output / 'timing.json'
    write_json(receipt_path, receipt)
    deadline = time.monotonic() + max(0, args.wait_style)
    while not all(path.exists() for path in key_paths.values()) and time.monotonic() < deadline:
        time.sleep(min(1, max(0, deadline - time.monotonic())))
    if not all(path.exists() for path in key_paths.values()):
        receipt.update(status='blocked', blocker='registered style key missing after bounded wait')
        write_json(receipt_path, receipt)
        print(json.dumps(receipt), flush=True)
        return 2
    executable = ROOT / 'tools/ebsynth/bin/ebsynth'
    if not executable.is_file() or not os.access(executable, os.X_OK):
        raise RuntimeError(f'CPU executable missing: {executable}')
    frame_names = [f'{i:04d}' for i in range(72)]
    with Image.open(ROOT / 'geometry/guideframes/0035.png') as source:
        native = source.size
    target_size = (512, round(native[1] * 512 / native[0]))
    for name, path in key_paths.items():
        with Image.open(path) as style:
            if style.size != native:
                raise ValueError(f'Registration mismatch: key {name} style {style.size}, native {native}')
            style.convert('RGB').resize(target_size, Image.Resampling.LANCZOS).save(output / f'prepared/style-{name}.png')
    for name in frame_names:
        with Image.open(ROOT / f'geometry/guideframes/{name}.png') as image:
            if image.size != native:
                raise ValueError(f'guide size mismatch: {name}')
            rgb = image.convert('RGB').resize(target_size, Image.Resampling.LANCZOS)
            rgb.save(output / f'prepared/rgb/{name}.png')
            rgb.convert('L').save(output / f'prepared/gray/{name}.png')
        with Image.open(ROOT / f'geometry/normalframes/{name}.png') as image:
            if image.size != native:
                raise ValueError(f'normal size mismatch: {name}')
            normal = image.convert('RGBA')
            flattened = Image.new('RGB', native, (0, 0, 0))
            flattened.paste(normal.convert('RGB'), mask=normal.getchannel('A'))
            flattened.resize(target_size, Image.Resampling.BILINEAR).save(output / f'prepared/normal/{name}.png')
        with Image.open(ROOT / f'geometry/coordinateframes/{name}.png') as image:
            if image.size != native:
                raise ValueError(f'coordinate size mismatch: {name}')
            coordinate = image.convert('RGBA')
            flattened = Image.new('RGB', native, (0, 0, 0))
            flattened.paste(coordinate.convert('RGB'), mask=coordinate.getchannel('A'))
            flattened.resize(target_size, Image.Resampling.BILINEAR).save(output / f'prepared/coordinate/{name}.png')
        with Image.open(ROOT / f'geometry/alphaframes/{name}.png') as image:
            if image.size != native:
                raise ValueError(f'alpha size mismatch: {name}')
            image.convert('L').resize(target_size, Image.Resampling.LANCZOS).save(output / f'prepared/alpha/{name}.png')
    receipt.update(status='benchmark', native_dimensions=list(native), prepared_dimensions=list(target_size),
                   gray_guides='prepared for inspection; synthesis uses RGB and normal only',
                   normal_background='alpha composited onto zero RGB before bilinear resize')
    write_json(receipt_path, receipt)

    def run_frame(name: str, threads: int, timeout: float = 90) -> dict:
        source = key_for_frame(name)
        command = [str(executable), '-style', str(output / f'prepared/style-{source}.png'), '-weight', '1',
                   '-guide', str(output / f'prepared/rgb/{source}.png'), str(output / f'prepared/rgb/{name}.png'), '-weight', '1',
                   '-guide', str(output / f'prepared/normal/{source}.png'), str(output / f'prepared/normal/{name}.png'), '-weight', '1',
                   '-guide', str(output / f'prepared/coordinate/{source}.png'), str(output / f'prepared/coordinate/{name}.png'), '-weight', '4',
                   '-output', str(output / f'frames/{name}.png'), '-backend', 'cpu',
                   '-pyramidlevels', '3', '-searchvoteiters', '3', '-patchmatchiters', '4', '-patchsize', '5']
        env = dict(os.environ, OMP_NUM_THREADS=str(threads))
        start = time.monotonic()
        with (output / f'logs/{name}.log').open('w') as log:
            try:
                result = subprocess.run(command, env=env, stdout=log, stderr=subprocess.STDOUT, timeout=timeout)
                code = result.returncode
            except subprocess.TimeoutExpired:
                code = 124
        entry = {'frame': name, 'source_key': source, 'threads': threads, 'elapsed_seconds': round(time.monotonic() - start, 3),
                 'exit': code, 'command': command}
        if code == 0:
            with Image.open(output / f'frames/{name}.png') as image:
                image.load()
                entry['dimensions'] = list(image.size)
                entry['mode'] = image.mode
                entry['decoded'] = image.size == target_size and image.mode == 'RGB'
        print(json.dumps(entry), flush=True)
        return entry

    benchmark = run_frame('0036', 4)
    receipt['benchmark'] = benchmark
    if benchmark['exit'] != 0 or not benchmark.get('decoded') or benchmark['elapsed_seconds'] >= 15:
        receipt.update(status='bounded benchmark only',
                       blocker='benchmark unsuccessful or >=15 seconds/frame; full sequence deliberately not started')
        write_json(receipt_path, receipt)
        return 3
    if args.probe_only:
        probes = [benchmark, run_frame('0017', 4), run_frame('0054', 4)]
        receipt.update(status='probe complete', frames=probes)
        write_json(receipt_path, receipt)
        return 0 if all(entry['exit'] == 0 and entry.get('decoded') for entry in probes) else 4
    receipt.update(status='sequence', workers=2, threads_per_worker=2)
    write_json(receipt_path, receipt)
    results = [benchmark]
    start = time.monotonic()
    deadline = start + 600

    def bounded_frame(name: str) -> dict:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return {'frame': name, 'exit': 124, 'blocker': 'sequence 600-second cap'}
        return run_frame(name, 2, min(90, remaining))

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(bounded_frame, name) for name in frame_names if name != '0036']
        for future in as_completed(futures):
            results.append(future.result())
            receipt['frames'] = sorted(results, key=lambda entry: entry['frame'])
            write_json(receipt_path, receipt)
    success = [entry for entry in results if entry['exit'] == 0 and entry.get('decoded')]
    receipt.update(status='complete' if len(success) == 72 else 'incomplete',
                   sequence_elapsed_seconds=round(time.monotonic() - start, 3),
                   successful_frames=len(success), frames=sorted(results, key=lambda entry: entry['frame']))
    write_json(receipt_path, receipt)
    print(f'{receipt["status"]}: {len(success)}/72 frames', flush=True)
    return 0 if len(success) == 72 else 4


if __name__ == '__main__':
    raise SystemExit(main())
