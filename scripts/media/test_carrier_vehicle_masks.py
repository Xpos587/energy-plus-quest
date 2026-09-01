from pathlib import Path

import numpy as np
from PIL import Image

import carrier_vehicle_masks as masks


def test_keep_seed_component_discards_detached_segmentation_noise():
    raw = np.zeros((12, 16), dtype=np.uint8)
    raw[2:9, 3:10] = 255
    raw[0, 0] = 255
    raw[10:12, 14:16] = 255

    cleaned = masks.keep_seed_component(raw, seed=(6, 5))

    assert cleaned[6, 5] == 255
    assert cleaned[0, 0] == 0
    assert cleaned[10, 14] == 0
    assert int(np.count_nonzero(cleaned)) == 49


def test_refine_vehicle_mask_grows_the_contour_without_filling_the_canvas():
    raw = np.zeros((20, 30), dtype=np.uint8)
    raw[6:14, 8:20] = 255

    refined = masks.refine_vehicle_mask(raw, seed=(12, 10), growth=2)

    assert refined.shape == raw.shape
    assert refined[4, 8] == 255
    assert refined[6, 5] == 0
    assert refined[0, 0] == 0
    assert int(np.count_nonzero(refined)) < raw.size // 2


def test_subtract_protection_preserves_only_vehicle_pixels():
    edit = np.full((10, 14), 255, dtype=np.uint8)
    protection = np.zeros_like(edit)
    protection[3:7, 5:9] = 255

    result = masks.subtract_protection(edit, [protection])

    assert np.all(result[3:7, 5:9] == 0)
    assert result[0, 0] == 255
    assert int(np.count_nonzero(result)) == int(np.count_nonzero(edit) - 16)


def test_mask_metadata_uses_intrinsic_bounds_and_sha256(tmp_path: Path):
    alpha = np.zeros((8, 10), dtype=np.uint8)
    alpha[2:6, 3:8] = 255
    path = tmp_path / "mask.png"
    masks.write_rgb_mask(path, alpha)

    metadata = masks.mask_metadata(path, "mask-id")

    assert metadata["id"] == "mask-id"
    assert metadata["dimensions"] == [10, 8]
    assert metadata["bounds"] == [3, 2, 8, 6]
    assert metadata["pixel_count"] == 20
    assert len(metadata["sha256"]) == 64
    assert Image.open(path).mode == "RGB"
