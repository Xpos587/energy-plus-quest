from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

from scripts.media.carrier_road_repair import (
    DESKTOP_PLAN,
    MOBILE_PLAN,
    horizontal_marking_bands,
    repair_image,
)


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


def assert_only_masked_pixels_changed(
    source: Path, repaired: Path, mask: Image.Image
) -> None:
    before = np.asarray(Image.open(source).convert("RGB"))
    after = np.asarray(Image.open(repaired).convert("RGB"))
    changed = np.any(before != after, axis=2)
    assert not np.any(changed & (np.asarray(mask) == 0))
    assert np.any(changed)


def test_desktop_arterial_has_one_internal_marking_band(tmp_path: Path) -> None:
    output = tmp_path / "desktop.png"
    mask = repair_image(DESKTOP_SOURCE, output, DESKTOP_PLAN)

    assert Image.open(output).size == (2528, 1424)
    assert_only_masked_pixels_changed(DESKTOP_SOURCE, output, mask)
    assert len(horizontal_marking_bands(DESKTOP_SOURCE, (1800, 920, 2300, 1100))) == 3
    assert horizontal_marking_bands(output, (1800, 920, 2300, 1100)) == [
        (1010, 1014)
    ]


def test_mobile_arterial_has_one_internal_marking_band(tmp_path: Path) -> None:
    output = tmp_path / "mobile.png"
    mask = repair_image(MOBILE_SOURCE, output, MOBILE_PLAN)

    assert Image.open(output).size == (768, 1424)
    assert_only_masked_pixels_changed(MOBILE_SOURCE, output, mask)
    assert len(
        horizontal_marking_bands(
            MOBILE_SOURCE, (720, 920, 768, 1100), minimum_pixels=8
        )
    ) == 3
    assert len(
        horizontal_marking_bands(output, (720, 920, 768, 1100), minimum_pixels=8)
    ) == 1
