import json

import fal_client
from PIL import Image

from carrier_art_pipeline import (
    assemble_regions,
    build_parser,
    extract_regions,
    load_region_manifest,
    upload,
)


def test_structured_generate_arguments() -> None:
    args = build_parser().parse_args(
        [
            "structured-generate",
            "--image",
            "color.png",
            "--control",
            "depth.png",
            "--control-type",
            "depth",
            "--prompt-file",
            "prompt.txt",
            "--width",
            "1536",
            "--height",
            "864",
            "--seed",
            "26082601",
            "--output",
            "result.png",
        ]
    )

    assert args.control_type == "depth"
    assert args.width == 1536
    assert args.height == 864


def test_load_region_manifest_validates_overlapping_regions(tmp_path) -> None:
    manifest_path = tmp_path / "desktop-regions.json"
    manifest_path.write_text(
        json.dumps(
            {
                "size": [1536, 864],
                "regions": {
                    "old": [0, 0, 720, 430],
                    "near": [650, 0, 1536, 500],
                    "crew": [0, 330, 850, 864],
                    "express": [700, 330, 1536, 864],
                },
            }
        )
    )

    manifest = load_region_manifest(manifest_path)

    assert manifest.size == (1536, 864)
    assert manifest.regions["express"] == (700, 330, 1536, 864)


def test_extract_regions_uses_identical_image_and_control_coordinates(tmp_path) -> None:
    image_path = tmp_path / "color.png"
    control_path = tmp_path / "canny.png"
    manifest_path = tmp_path / "regions.json"
    output_dir = tmp_path / "regions"
    Image.new("RGB", (100, 80), "red").save(image_path)
    Image.new("L", (100, 80), 127).save(control_path)
    manifest_path.write_text(
        json.dumps(
            {
                "size": [100, 80],
                "regions": {
                    "old": [0, 0, 60, 50],
                    "near": [40, 0, 100, 50],
                    "crew": [0, 30, 60, 80],
                    "express": [40, 30, 100, 80],
                },
            }
        )
    )

    extract_regions(image_path, control_path, manifest_path, output_dir)

    assert Image.open(output_dir / "old-image.png").size == (60, 50)
    assert Image.open(output_dir / "old-control.png").size == (60, 50)
    metadata = json.loads((output_dir / "old.json").read_text())
    assert metadata["bounds"] == [0, 0, 60, 50]


def test_assemble_regions_has_no_alpha_holes_or_hard_overlap_seam(tmp_path) -> None:
    base_path = tmp_path / "base.png"
    manifest_path = tmp_path / "regions.json"
    left_path = tmp_path / "old.png"
    right_path = tmp_path / "near.png"
    output_path = tmp_path / "assembled.png"
    Image.new("RGB", (100, 50), (100, 100, 100)).save(base_path)
    Image.new("RGB", (60, 50), (80, 80, 80)).save(left_path)
    Image.new("RGB", (60, 50), (120, 120, 120)).save(right_path)
    manifest_path.write_text(
        json.dumps(
            {
                "size": [100, 50],
                "regions": {
                    "old": [0, 0, 60, 50],
                    "near": [40, 0, 100, 50],
                    "crew": [0, 20, 60, 50],
                    "express": [40, 20, 100, 50],
                },
            }
        )
    )

    assemble_regions(
        base_path,
        manifest_path,
        {"old": left_path, "near": right_path},
        feather=12,
        output_path=output_path,
    )

    assembled = Image.open(output_path).convert("RGBA")
    assert assembled.getextrema()[3] == (255, 255)
    pixels = assembled.convert("RGB")
    before = pixels.getpixel((49, 25))[0]
    after = pixels.getpixel((50, 25))[0]
    assert abs(after - before) <= 4


def test_upload_falls_back_to_data_url(monkeypatch, tmp_path) -> None:
    image = tmp_path / "guide.png"
    image.write_bytes(b"png-data")

    def fail_upload(_path: str) -> str:
        raise RuntimeError("storage token unavailable")

    monkeypatch.setattr(fal_client, "upload_file", fail_upload)
    monkeypatch.setattr(fal_client, "encode_file", lambda path: f"data:{path}")

    assert upload(str(image)) == f"data:{image.resolve()}"
