#!/usr/bin/env python3
"""Create contour-only carrier protection masks with SAM2.

This module uses a segmentation model for masks only. It never generates or
edits image pixels with a generative model; the image repair remains a separate
and explicitly guarded ComfyUI step.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Iterable

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "design/scene-01/assets/feedback-v11"
DEFAULT_SOURCE = (
    ASSETS
    / "comfyui/gpt2-three-vehicle-scale-v4-output"
    / "carrier_v11_mobile_gpt2_three_vehicle_scale_v4_00001_.png"
)
DEFAULT_SESSION = ASSETS / "comfyui/interactive-repair/road-02-lower-arterial"
DEFAULT_MODEL = "facebook/sam2.1-hiera-tiny"
EDIT_BOUNDS = (0, 890, 768, 1170)

# Box and point prompts are kept in source-pixel coordinates for reproducibility.
PROTECTION_COMMENTS = {
    "crew": "Preserve only the visible Crew truck contour, including its body, cab, wheels, and two-driver pixels; do not preserve its road shadow, wake, or surrounding asphalt.",
    "express": "Preserve only the visible Express truck contour, including its body, cab, wheels, and wordmark pixels; do not preserve its snow wake, shadow, or surrounding asphalt.",
}

CARRIER_PROMPTS: dict[str, dict[str, Any]] = {
    "crew": {
        "box": [105, 890, 345, 1048],
        "points": [[205, 970], [285, 980], [145, 925], [245, 910], [115, 900], [335, 900]],
        "labels": [1, 1, 1, 1, 0, 0],
        "seed": [205, 970],
    },
    "express": {
        "box": [460, 995, 740, 1170],
        "points": [[590, 1085], [675, 1090], [520, 1060], [650, 1140], [470, 1000], [735, 1165]],
        "labels": [1, 1, 1, 1, 0, 0],
        "seed": [590, 1085],
    },
}


def _binary(mask: np.ndarray) -> np.ndarray:
    value = np.asarray(mask)
    if value.ndim != 2:
        raise ValueError("mask must be a two-dimensional array")
    return value > 0


def keep_seed_component(mask: np.ndarray, *, seed: tuple[int, int]) -> np.ndarray:
    """Keep the 8-connected component containing the supplied (x, y) seed."""
    source = _binary(mask)
    x, y = seed
    height, width = source.shape
    if not (0 <= x < width and 0 <= y < height) or not source[y, x]:
        raise ValueError("segmentation seed is not inside the predicted mask")

    result = np.zeros_like(source, dtype=bool)
    pending = [(x, y)]
    result[y, x] = True
    while pending:
        current_x, current_y = pending.pop()
        for delta_y in (-1, 0, 1):
            for delta_x in (-1, 0, 1):
                if not delta_x and not delta_y:
                    continue
                next_x = current_x + delta_x
                next_y = current_y + delta_y
                if (
                    0 <= next_x < width
                    and 0 <= next_y < height
                    and source[next_y, next_x]
                    and not result[next_y, next_x]
                ):
                    result[next_y, next_x] = True
                    pending.append((next_x, next_y))
    return result.astype(np.uint8) * 255


def _fill_holes(mask: np.ndarray) -> np.ndarray:
    source = _binary(mask)
    height, width = source.shape
    outside = np.zeros_like(source, dtype=bool)
    pending: list[tuple[int, int]] = []
    for x in range(width):
        pending.extend(((x, 0), (x, height - 1)))
    for y in range(height):
        pending.extend(((0, y), (width - 1, y)))
    while pending:
        x, y = pending.pop()
        if not (0 <= x < width and 0 <= y < height) or source[y, x] or outside[y, x]:
            continue
        outside[y, x] = True
        pending.extend(((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)))
    return (source | (~outside)).astype(np.uint8) * 255


def _dilate(mask: np.ndarray, iterations: int) -> np.ndarray:
    result = _binary(mask)
    for _ in range(max(0, iterations)):
        padded = np.pad(result, 1, mode="constant")
        result = np.zeros_like(result, dtype=bool)
        for y in range(3):
            for x in range(3):
                result |= padded[y : y + result.shape[0], x : x + result.shape[1]]
    return result.astype(np.uint8) * 255


def refine_vehicle_mask(
    mask: np.ndarray,
    *,
    seed: tuple[int, int],
    growth: int = 2,
) -> np.ndarray:
    """Remove detached model noise, fill interior holes, and grow the edge safely."""
    connected = keep_seed_component(mask, seed=seed)
    filled = _fill_holes(connected)
    return _dilate(filled, growth)


def subtract_protection(edit_mask: np.ndarray, protections: Iterable[np.ndarray]) -> np.ndarray:
    """Return a logical white=edit mask with contour-only preserve regions removed."""
    result = np.where(_binary(edit_mask), 255, 0).astype(np.uint8)
    for protection in protections:
        value = np.asarray(protection)
        if value.shape != result.shape:
            raise ValueError("protection mask dimensions do not match the edit mask")
        result[_binary(value)] = 0
    return result


def _validate_protection_geometry(
    protections: dict[str, np.ndarray], bounds: tuple[int, int, int, int]
) -> None:
    left, top, right, bottom = bounds
    occupied = None
    for name, mask in protections.items():
        value = _binary(mask)
        if occupied is not None and np.any(value & occupied):
            raise ValueError(f"vehicle protection masks overlap: {name}")
        outside = value.copy()
        outside[top:bottom, left:right] = False
        if np.any(outside):
            raise ValueError(f"vehicle protection mask leaves the edit band: {name}")
        occupied = value if occupied is None else occupied | value


def mask_bounds(mask: np.ndarray) -> list[int]:
    value = _binary(mask)
    ys, xs = np.where(value)
    if not len(xs):
        raise ValueError("mask is empty")
    return [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _assert_safe_destination(path: Path) -> None:
    if path.is_symlink():
        raise ValueError(f"refusing to replace symlink: {path}")
    for parent in path.parents:
        if parent == parent.parent:
            break
        if parent.exists() and parent.is_symlink():
            raise ValueError(f"refusing symlink path component: {parent}")


def _atomic_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    _assert_safe_destination(path)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
            os.fchmod(stream.fileno(), 0o644)
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


def _atomic_json(path: Path, value: Any) -> None:
    _atomic_bytes(path, (json.dumps(value, ensure_ascii=True, indent=2) + "\n").encode())


def write_rgb_mask(path: Path, alpha: np.ndarray) -> None:
    value = np.where(_binary(alpha), 255, 0).astype(np.uint8)
    buffer = io.BytesIO()
    Image.fromarray(value, mode="L").convert("RGB").save(buffer, format="PNG", optimize=False)
    _atomic_bytes(path, buffer.getvalue())


def _read_rgb_mask(path: Path, size: tuple[int, int]) -> np.ndarray:
    with Image.open(path) as image:
        rgb = image.convert("RGB")
        if rgb.size != size:
            raise ValueError(f"mask {path} does not match source dimensions")
        values = np.asarray(rgb)
    if not np.all(values[..., 0] == values[..., 1]) or not np.all(values[..., 1] == values[..., 2]):
        raise ValueError(f"mask {path} is not grayscale")
    return np.where(values[..., 0] > 0, 255, 0).astype(np.uint8)


def mask_metadata(path: Path, mask_id: str) -> dict[str, Any]:
    with Image.open(path) as image:
        values = np.asarray(image.convert("L"))
        width, height = image.size
    return {
        "id": mask_id,
        "dimensions": [width, height],
        "bounds": mask_bounds(values),
        "pixel_count": int(np.count_nonzero(values)),
        "sha256": _sha256_file(path),
    }


def _review_overlay(
    source: Image.Image,
    edit_mask: np.ndarray,
    protections: dict[str, np.ndarray],
    output: Path,
) -> None:
    base = source.convert("RGBA")
    edit_layer = Image.new("RGBA", base.size, (239, 68, 68, 0))
    edit_layer.putalpha(Image.fromarray(np.where(_binary(edit_mask), 92, 0).astype(np.uint8)))
    result = Image.alpha_composite(base, edit_layer)
    colors = {"crew": (34, 197, 94), "express": (16, 185, 129)}
    for name, mask in protections.items():
        layer = Image.new("RGBA", base.size, (*colors.get(name, (34, 197, 94)), 0))
        layer.putalpha(Image.fromarray(np.where(_binary(mask), 118, 0).astype(np.uint8)))
        result = Image.alpha_composite(result, layer)
        # A one-pixel edge keeps the contour readable at the native review size.
        values = _binary(mask)
        edge = values & ~(
            np.roll(values, 1, 0)
            & np.roll(values, -1, 0)
            & np.roll(values, 1, 1)
            & np.roll(values, -1, 1)
        )
        contour = Image.new("RGBA", base.size, (*colors.get(name, (34, 197, 94)), 0))
        contour.putalpha(Image.fromarray(np.where(edge, 220, 0).astype(np.uint8)))
        result = Image.alpha_composite(result, contour)
    buffer = io.BytesIO()
    result.convert("RGB").save(buffer, format="PNG", optimize=False)
    _atomic_bytes(output, buffer.getvalue())


def _load_sam2(repo: str, token: str, device: str):
    try:
        import torch
        from transformers import Sam2Model, Sam2Processor
    except ImportError as error:  # pragma: no cover - exercised only in the model environment
        raise RuntimeError("SAM2 inference requires torch and transformers") from error
    processor = Sam2Processor.from_pretrained(repo, token=token)
    model = Sam2Model.from_pretrained(repo, token=token).eval().to(device)
    revision = getattr(model.config, "_commit_hash", None)
    return processor, model, torch, revision


def segment(
    source_path: Path,
    output_dir: Path,
    *,
    model_repo: str = DEFAULT_MODEL,
    token: str | None = None,
    growth: int = 2,
    device: str = "cpu",
) -> dict[str, Any]:
    """Run SAM2 box/point segmentation and write reviewable silhouette artifacts."""
    if not token:
        raise RuntimeError("HF_TOKEN is required; pass it through the environment, never a CLI argument")
    if growth < 0:
        raise ValueError("growth must be non-negative")
    with Image.open(source_path) as image:
        source = image.convert("RGB")
    processor, model, torch, model_revision = _load_sam2(model_repo, token, device)
    names = list(CARRIER_PROMPTS)
    boxes = [[CARRIER_PROMPTS[name]["box"] for name in names]]
    points = [[CARRIER_PROMPTS[name]["points"] for name in names]]
    labels = [[CARRIER_PROMPTS[name]["labels"] for name in names]]
    inputs = processor(
        images=source,
        input_boxes=boxes,
        input_points=points,
        input_labels=labels,
        return_tensors="pt",
    )
    inputs = {key: value.to(device) if hasattr(value, "to") else value for key, value in inputs.items()}
    with torch.no_grad():
        outputs = model(**inputs, multimask_output=True)
    postprocessed = processor.post_process_masks(outputs.pred_masks, inputs["original_sizes"])[0]
    scores = outputs.iou_scores.detach().cpu().numpy()[0]
    output_dir.mkdir(parents=True, exist_ok=True)
    protections: dict[str, np.ndarray] = {}
    metadata: dict[str, Any] = {}
    for index, name in enumerate(names):
        candidate_index = int(np.argmax(scores[index]))
        raw = (postprocessed[index, candidate_index].detach().cpu().numpy() > 0).astype(np.uint8) * 255
        prompt = CARRIER_PROMPTS[name]
        refined = refine_vehicle_mask(
            raw,
            seed=tuple(prompt["seed"]),
            growth=growth,
        )
        path = output_dir / f"{name}-sam2-silhouette.png"
        raw_path = output_dir / f"{name}-sam2-raw.png"
        write_rgb_mask(path, refined)
        write_rgb_mask(raw_path, raw)
        protections[name] = refined
        metadata[name] = {
            "model_mask_index": candidate_index,
            "iou_scores": [round(float(value), 6) for value in scores[index]],
            "prompt": prompt,
            "mask": mask_metadata(path, f"{name}-sam2-silhouette"),
            "raw_mask_sha256": _sha256_file(raw_path),
            "growth_pixels": growth,
        }

    full_edit = np.zeros((source.height, source.width), dtype=np.uint8)
    left, top, right, bottom = EDIT_BOUNDS
    full_edit[top:bottom, left:right] = 255
    _validate_protection_geometry(protections, EDIT_BOUNDS)
    edit_mask = subtract_protection(full_edit, protections.values())
    edit_path = output_dir / "lower-arterial-two-lanes-sam2.png"
    write_rgb_mask(edit_path, edit_mask)
    _review_overlay(source, edit_mask, protections, output_dir / "review-overlay-native.png")
    preview_width = 375
    preview = Image.open(output_dir / "review-overlay-native.png").convert("RGB")
    preview = preview.resize(
        (preview_width, round(preview.height * preview_width / preview.width)),
        Image.Resampling.LANCZOS,
    )
    buffer = io.BytesIO()
    preview.save(buffer, format="PNG", optimize=False)
    _atomic_bytes(output_dir / "review-overlay-375.png", buffer.getvalue())

    receipt = {
        "status": "segmentation-candidate",
        "task": "vehicle-only protection masks",
        "local_image_generation": False,
        "local_segmentation_model_used": True,
        "model": {
            "repo": model_repo,
            "revision": model_revision,
            "task": "prompted image segmentation",
            "device": device,
            "token_source": "HF_TOKEN",
            "token_recorded": False,
        },
        "source": {
            "file": str(source_path),
            "sha256": _sha256_file(source_path),
            "dimensions": [source.width, source.height],
        },
        "edit_bounds": list(EDIT_BOUNDS),
        "logical_convention": "white=edit,black=preserve",
        "protections": metadata,
        "edit_mask": mask_metadata(edit_path, "lower-arterial-two-lanes-sam2"),
        "next_step": "inspect native and 375px overlays before applying to the workbench session",
    }
    _atomic_json(output_dir / "segmentation-receipt.json", receipt)
    return receipt


def apply_session(session_dir: Path, segmentation_dir: Path) -> dict[str, Any]:
    """Install a reviewed candidate while archiving the former rectangular mask."""
    manifest_path = session_dir / "manifest.json"
    execution_path = session_dir / "execution.json"
    old_manifest = json.loads(manifest_path.read_text())
    old_mask_name = old_manifest["masks"][0]["file"]
    old_mask_path = session_dir / old_mask_name
    new_edit_path = segmentation_dir / "lower-arterial-two-lanes-sam2.png"
    # The first version of this session used this exact rectangular filename.
    # Keep that immutable archive as the comparison point on repeated applies.
    rectangular_mask_name = "masks/lower-arterial-two-lanes.png"
    rectangular_archive_name = "archive/rectangular-v1/lower-arterial-two-lanes.png"
    source_path = session_dir / old_manifest["source"]["file"]
    with Image.open(source_path) as source_image:
        size = source_image.size
    edit_mask = _read_rgb_mask(new_edit_path, size)
    protections = {
        name: _read_rgb_mask(segmentation_dir / f"{name}-sam2-silhouette.png", size)
        for name in CARRIER_PROMPTS
    }
    _validate_protection_geometry(protections, EDIT_BOUNDS)

    archive_dir = session_dir / "archive/rectangular-v1"
    # Archive the original rectangular session exactly once; later reruns must
    # not replace that provenance with the already-refined candidate.
    if not (archive_dir / "manifest.json").is_file():
        if old_mask_path.is_file():
            _atomic_bytes(archive_dir / old_mask_path.name, old_mask_path.read_bytes())
        _atomic_json(archive_dir / "manifest.json", old_manifest)

    for name, protection in protections.items():
        destination = session_dir / f"protection/{name}-sam2-silhouette.png"
        write_rgb_mask(destination, protection)
        raw_path = segmentation_dir / f"{name}-sam2-raw.png"
        if raw_path.is_file():
            _atomic_bytes(session_dir / f"protection/raw/{name}-sam2-raw.png", raw_path.read_bytes())
    new_mask_name = "masks/lower-arterial-two-lanes-sam2-v2.png"
    new_mask_path = session_dir / new_mask_name
    write_rgb_mask(new_mask_path, edit_mask)

    updated = json.loads(json.dumps(old_manifest))
    mask = updated["masks"][0]
    mask.update(
        {
            "name": "Entire lower arterial - two lanes; contour-protected trucks",
            "comment": (
                "Regenerate the entire lower horizontal arterial as one connected ordinary two-lane road: "
                "exactly two lanes total, one lane in each direction, one restrained dashed center line, "
                "coherent asphalt and snowy edges. Remove the current four-to-five parallel lane-like strips "
                "and duplicate road bands. Keep Crew and Express exactly where they are using only their "
                "contour-following vehicle silhouettes; preserve the trucks but do not preserve rectangular "
                "road areas, shadows, wakes, snow, or surrounding pixels. Do not add vehicles, text, logos, "
                "road labels, route overlays, or extra lane markings. Preserve the northern winter illustration "
                "style, camera, lighting, connected intersections, railway, warehouse context, and every pixel "
                "outside the white edit region."
            ),
            "file": new_mask_name,
            "bounds": mask_bounds(edit_mask),
            "sha256": _sha256_file(new_mask_path),
            "pixel_count": int(np.count_nonzero(edit_mask)),
        }
    )
    updated["source"]["sha256"] = _sha256_file(source_path)
    _atomic_json(manifest_path, updated)

    with Image.open(source_path) as source_image:
        source = source_image.convert("RGB")
    _review_overlay(source, edit_mask, protections, session_dir / "overlay.png")
    _review_overlay(source, edit_mask, protections, session_dir / "review-overlay-native.png")
    preview = Image.open(session_dir / "review-overlay-native.png").convert("RGB")
    preview = preview.resize(
        (375, round(preview.height * 375 / preview.width)),
        Image.Resampling.LANCZOS,
    )
    preview_buffer = io.BytesIO()
    preview.save(preview_buffer, format="PNG", optimize=False)
    _atomic_bytes(session_dir / "review-overlay-375.png", preview_buffer.getvalue())
    segmentation_receipt_path = segmentation_dir / "segmentation-receipt.json"
    if segmentation_receipt_path.is_file():
        _atomic_bytes(session_dir / "segmentation-receipt.json", segmentation_receipt_path.read_bytes())

    # Import the workbench's canonical state helper only after the manifest is valid.
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from mask_workbench import _atomic_json_write, execution_state_for_manifest

    new_state = execution_state_for_manifest(updated)
    _atomic_json_write(execution_path, new_state)
    new_mask_sha256 = _sha256_file(new_mask_path)
    segmentation_receipt = {}
    segmentation_receipt_path = session_dir / "segmentation-receipt.json"
    if segmentation_receipt_path.is_file():
        segmentation_receipt = json.loads(segmentation_receipt_path.read_text())
    receipt = {
        "status": "prepared-for-human-review",
        "previous_mask": rectangular_mask_name,
        "previous_mask_archived": rectangular_archive_name,
        "new_mask": new_mask_name,
        "new_mask_sha256": new_mask_sha256,
        "source_sha256": _sha256_file(source_path),
        "logical_convention": "white=edit,black=preserve",
        "edit_bounds": mask_bounds(edit_mask),
        "edit_pixels": int(np.count_nonzero(edit_mask)),
        "mask": new_mask_name,
        "mask_sha256": new_mask_sha256,
        "mask_pixel_count": int(np.count_nonzero(edit_mask)),
        "mask_bounds": mask_bounds(edit_mask),
        "protected_trucks": {
            name: {
                **mask_metadata(session_dir / f"protection/{name}-sam2-silhouette.png", f"{name}-sam2-silhouette"),
                "name": f"{name.title()} vehicle silhouette",
                "comment": PROTECTION_COMMENTS[name],
                "raw_mask": (
                    {
                        "file": f"protection/raw/{name}-sam2-raw.png",
                        "sha256": _sha256_file(session_dir / f"protection/raw/{name}-sam2-raw.png"),
                    }
                    if (session_dir / f"protection/raw/{name}-sam2-raw.png").is_file()
                    else None
                ),
            }
            for name in protections
        },
        "segmentation_model": segmentation_receipt.get("model", {}),
        "rectangle_protection_removed": True,
        "local_image_generation": False,
        "local_generative_models_used": False,
        "paid_submission_authorized": False,
        "segmentation_receipt": "segmentation-receipt.json",
        "local_segmentation_model_used": True,
        "next_step": "human visual review, then dry-run compile; no paid request submitted",
    }
    _atomic_json(session_dir / "segmentation-apply-receipt.json", receipt)
    # Keep the original review receipt fields but make the new protection geometry explicit.
    review_path = session_dir / "review-receipt.json"
    review = json.loads(review_path.read_text()) if review_path.is_file() else {}
    review.update(receipt)
    _atomic_json(review_path, review)
    return receipt


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    segment_parser = subparsers.add_parser("segment")
    segment_parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    segment_parser.add_argument("--output-dir", type=Path, required=True)
    segment_parser.add_argument("--model", default=DEFAULT_MODEL)
    segment_parser.add_argument("--device", choices=("cpu",), default="cpu")
    segment_parser.add_argument("--growth", type=int, default=2)
    segment_parser.set_defaults(command_func="segment")
    apply_parser = subparsers.add_parser("apply")
    apply_parser.add_argument("--session-dir", type=Path, default=DEFAULT_SESSION)
    apply_parser.add_argument("--segmentation-dir", type=Path, required=True)
    apply_parser.set_defaults(command_func="apply")
    args = parser.parse_args(argv)
    if args.command_func == "segment":
        receipt = segment(
            args.source.resolve(),
            args.output_dir.resolve(),
            model_repo=args.model,
            token=os.environ.get("HF_TOKEN"),
            growth=args.growth,
            device=args.device,
        )
        print(json.dumps({"status": receipt["status"], "output_dir": str(args.output_dir.resolve())}))
    else:
        receipt = apply_session(args.session_dir.resolve(), args.segmentation_dir.resolve())
        print(json.dumps({"status": receipt["status"], "new_mask": receipt["new_mask"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
