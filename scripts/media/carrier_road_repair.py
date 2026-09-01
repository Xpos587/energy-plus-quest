#!/usr/bin/env python3
"""Deterministically collapse the lower carrier arterial to two lanes.

This is clone-stamp raster editing only. It does not load or run an image model.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Iterable

import numpy as np
from PIL import Image, ImageFilter


ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "design/scene-01/assets/feedback-v11"
MOBILE_SOURCE = (
    ASSETS
    / "comfyui/gpt2-three-vehicle-scale-v4-output"
    / "carrier_v11_mobile_gpt2_three_vehicle_scale_v4_00001_.png"
)
DESKTOP_SOURCE = (
    ASSETS
    / "comfyui/desktop-side-cleanup-v5-output"
    / "carrier_v11_desktop_side_cleanup_v5_00001_.png"
)
DEFAULT_OUTPUT = ASSETS / "comfyui/two-lane-repair-v12"

# (target rectangle, donor y, vertical feather, horizontal feather)
Plan = tuple[tuple[tuple[int, int, int, int], int, int, int], ...]

DESKTOP_PLAN: Plan = (
    ((1240, 946, 1390, 970), 918, 4, 10),
    ((1550, 946, 2528, 970), 918, 4, 10),
    ((1240, 993, 1350, 1025), 940, 3, 10),
    ((1660, 993, 2528, 1025), 940, 3, 10),
    ((1680, 1054, 2528, 1082), 1026, 0, 10),
)

MOBILE_PLAN: Plan = (
    ((350, 946, 540, 970), 918, 4, 10),
    ((690, 946, 768, 970), 918, 4, 10),
    ((350, 993, 480, 1025), 940, 3, 10),
    ((710, 993, 768, 1025), 940, 3, 10),
    ((720, 1054, 768, 1082), 1026, 0, 10),
)


def _blend_mask(
    width: int, height: int, feather_y: int, feather_x: int
) -> Image.Image:
    alpha = np.full((height, width), 255, dtype=np.uint8)
    for offset in range(min(feather_y, height // 2)):
        value = round(255 * (offset + 1) / (feather_y + 1))
        alpha[offset] = np.minimum(alpha[offset], value)
        alpha[-1 - offset] = np.minimum(alpha[-1 - offset], value)
    for offset in range(min(feather_x, width // 2)):
        value = round(255 * (offset + 1) / (feather_x + 1))
        alpha[:, offset] = np.minimum(alpha[:, offset], value)
        alpha[:, -1 - offset] = np.minimum(alpha[:, -1 - offset], value)
    return Image.fromarray(alpha).filter(ImageFilter.GaussianBlur(1))


def _atomic_save(image: Image.Image, path: Path, image_format: str, **options: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        raise ValueError(f"refusing to replace symlink: {path}")
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w+b") as temporary:
            image.save(temporary, format=image_format, **options)
            temporary.flush()
            os.fsync(temporary.fileno())
            os.fchmod(temporary.fileno(), 0o644)
        os.replace(temporary_name, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    except Exception:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def repair_image(source_path: Path, output_path: Path, plan: Plan) -> Image.Image:
    source = Image.open(source_path).convert("RGB")
    repaired = source.copy()
    touched = Image.new("L", source.size)

    for (left, top, right, bottom), donor_y, feather_y, feather_x in plan:
        width, height = right - left, bottom - top
        if not (0 <= left < right <= source.width and 0 <= top < bottom <= source.height):
            raise ValueError("repair rectangle is outside the source image")
        if not 0 <= donor_y <= source.height - height:
            raise ValueError("repair donor strip is outside the source image")

        patch = source.crop((left, donor_y, right, donor_y + height))
        alpha = _blend_mask(width, height, feather_y, feather_x)
        repaired.paste(patch, (left, top), alpha)
        touched.paste(255, (left, top, right, bottom))

    _atomic_save(repaired, output_path, "PNG")
    return touched


def horizontal_marking_bands(
    image_path: Path,
    bounds: tuple[int, int, int, int],
    *,
    minimum_pixels: int = 40,
) -> list[tuple[int, int]]:
    left, top, right, bottom = bounds
    pixels = np.asarray(Image.open(image_path).convert("RGB"))[top:bottom, left:right]
    brightest = pixels.max(axis=2)
    darkest = pixels.min(axis=2)
    active_rows = np.flatnonzero(
        ((brightest > 160) & ((brightest - darkest) < 55)).sum(axis=1)
        >= minimum_pixels
    )
    if not len(active_rows):
        return []

    bands: list[tuple[int, int]] = []
    start = previous = int(active_rows[0])
    for row in map(int, active_rows[1:]):
        if row != previous + 1:
            bands.append((top + start, top + previous))
            start = row
        previous = row
    bands.append((top + start, top + previous))
    return bands


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _outside_changed_pixels(source_path: Path, output_path: Path, mask: Image.Image) -> int:
    source = np.asarray(Image.open(source_path).convert("RGB"))
    output = np.asarray(Image.open(output_path).convert("RGB"))
    changed = np.any(source != output, axis=2)
    return int(np.count_nonzero(changed & (np.asarray(mask) == 0)))


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as temporary:
            json.dump(payload, temporary, ensure_ascii=True, indent=2)
            temporary.write("\n")
            temporary.flush()
            os.fsync(temporary.fileno())
            os.fchmod(temporary.fileno(), 0o644)
        if path.is_symlink():
            raise ValueError(f"refusing to replace symlink: {path}")
        os.replace(temporary_name, path)
    except Exception:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def render(output_dir: Path) -> None:
    jobs = {
        "mobile": (MOBILE_SOURCE, MOBILE_PLAN, (720, 920, 768, 1100), 8),
        "desktop": (DESKTOP_SOURCE, DESKTOP_PLAN, (1800, 920, 2300, 1100), 40),
    }
    receipt: dict[str, object] = {
        "status": "candidate-verified",
        "method": "deterministic-pixel-clone",
        "local_models_used": False,
        "road_contract": "one connected road band with exactly two lanes",
        "assets": {},
    }

    for name, (source, plan, verification_bounds, minimum_pixels) in jobs.items():
        png = output_dir / f"carrier-{name}.png"
        mask = repair_image(source, png, plan)
        _atomic_save(mask, output_dir / f"carrier-{name}-repair-mask.png", "PNG")

        image = Image.open(png).convert("RGB")
        _atomic_save(image, output_dir / f"carrier-{name}.webp", "WEBP", quality=82, method=6)
        preview_width = 375 if name == "mobile" else 1440
        preview = image.resize(
            (preview_width, round(image.height * preview_width / image.width)),
            Image.Resampling.LANCZOS,
        )
        _atomic_save(preview, output_dir / f"carrier-{name}-{preview_width}.png", "PNG")

        bands = horizontal_marking_bands(
            png, verification_bounds, minimum_pixels=minimum_pixels
        )
        if len(bands) != 1:
            raise AssertionError(f"{name} road has {len(bands)} internal marking bands")
        outside_changed = _outside_changed_pixels(source, png, mask)
        if outside_changed:
            raise AssertionError(f"{name} changed {outside_changed} protected pixels")

        receipt["assets"][name] = {
            "source": str(source.relative_to(ROOT)),
            "source_sha256": _sha256(source),
            "output_sha256": _sha256(png),
            "dimensions": list(image.size),
            "internal_marking_bands": [list(band) for band in bands],
            "protected_pixels_changed": outside_changed,
            "repair_rectangles": [list(operation[0]) for operation in plan],
        }

    _write_json(output_dir / "receipt.json", receipt)


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    render(args.output_dir.resolve())
    print(f"two-lane carrier assets: {args.output_dir.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
