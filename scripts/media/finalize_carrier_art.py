#!/usr/bin/env python3
"""Compose selected crew cutouts into final V9 carrier panoramas."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "design/scene-01/assets/feedback-v9"


def load_rgba(path: Path) -> Image.Image:
    return Image.open(path).convert("RGBA")


def trim_desktop_cutout(cutout: Image.Image) -> Image.Image:
    """Remove building fragment connected to desktop GrabCut silhouette."""
    alpha = cutout.getchannel("A")
    alpha.paste(0, (187, 0, cutout.width, 53))
    cleaned = cutout.copy()
    cleaned.putalpha(alpha)
    return cleaned


def compose(
    base_path: Path,
    cutout_path: Path,
    position: tuple[int, int],
    size: tuple[int, int] | None = None,
    trim_desktop: bool = False,
) -> Image.Image:
    base = load_rgba(base_path)
    cutout = load_rgba(cutout_path)
    if trim_desktop:
        cutout = trim_desktop_cutout(cutout)
    if size:
        cutout = cutout.resize(size, Image.Resampling.LANCZOS)
    base.alpha_composite(cutout, position)
    return base.convert("RGB")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ASSETS / "production",
    )
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    desktop = compose(
        ASSETS / "candidates/base/desktop-26083401.png",
        ASSETS / "candidates/local/crew-cutout.png",
        (420, 280),
        trim_desktop=True,
    )
    mobile = compose(
        ASSETS / "candidates/base/mobile-26083402.png",
        ASSETS / "candidates/local/mobile-crew-cutout.png",
        (175, 785),
        size=(202, 154),
    ).convert("RGBA")
    old_cutout = load_rgba(
        ASSETS / "candidates/local/mobile-old-cutout.png"
    ).crop((0, 70, 125, 196))
    mobile.alpha_composite(old_cutout, (265, 660))
    # Mobile camera includes large quiet margins; crop to playable town at phone scale.
    mobile = mobile.convert("RGB").crop((160, 500, 720, 1562)).resize(
        (944, 1792), Image.Resampling.LANCZOS
    )

    for name, image in (("desktop", desktop), ("mobile", mobile)):
        image.save(args.output_dir / f"carrier-{name}.png", optimize=True)
        image.save(
            args.output_dir / f"carrier-{name}.webp",
            "WEBP",
            quality=88,
            method=6,
        )
        print(f"saved carrier-{name}.png and carrier-{name}.webp")


if __name__ == "__main__":
    main()
