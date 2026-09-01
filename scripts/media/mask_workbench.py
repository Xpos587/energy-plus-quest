"""Local multi-mask workbench and guarded ComfyUI controller.

The browser owns drawing and comments. This module owns the durable manifest,
mask polarity, API-graph compilation, and the loopback-only controller. No
provider credential is read or copied here; ComfyUI remains the credential
boundary for partner nodes.
"""

from __future__ import annotations

import argparse
import base64
import fcntl
import hashlib
import json
import io
import mimetypes
import os
import re
import secrets
import sys
import tempfile
import threading
import time
from contextlib import contextmanager
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import quote, unquote, urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

from PIL import Image, ImageChops

SCHEMA = "carrier-mask-workbench/v1"
MASK_CONVENTION = "white=edit,black=preserve"
PAID_CONFIRMATION = "SUBMIT_PAID"
MAX_MASKS = 32
MAX_COMMENT_LENGTH = 4000
_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")
_COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")
_SAFE_PREFIX_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_./-]{0,180}$")
_SESSION_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,119}$")
_TERMINAL_EVENTS = {"execution_success", "execution_error", "execution_interrupted"}


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise RuntimeError("redirects are disabled for the loopback ComfyUI boundary")


_NO_REDIRECT_OPENER = build_opener(_NoRedirect)


class ManifestError(ValueError):
    """Raised when a workbench manifest cannot be safely executed."""


class DuplicateJobError(RuntimeError):
    """Raised when an identical job is already recorded."""


@contextmanager
def _exclusive_file_lock(path: Path) -> Iterable[None]:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+b") as stream:
        fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def canvas_point(
    *, client_x: float, client_y: float, rect: tuple[float, float, float, float], canvas_size: tuple[int, int]
) -> tuple[int, int]:
    """Map CSS-space pointer coordinates to clamped intrinsic canvas pixels."""
    left, top, css_width, css_height = rect
    width, height = canvas_size
    if css_width <= 0 or css_height <= 0 or width <= 0 or height <= 0:
        raise ValueError("canvas and CSS dimensions must be positive")
    x = int((client_x - left) * width / css_width)
    y = int((client_y - top) * height / css_height)
    return max(0, min(width - 1, x)), max(0, min(height - 1, y))


def _check_alpha(alpha: bytes, width: int, height: int) -> None:
    if width <= 0 or height <= 0:
        raise ValueError("mask dimensions must be positive")
    if len(alpha) != width * height:
        raise ValueError("mask alpha length does not match dimensions")


def union_alpha(masks: Iterable[bytes]) -> bytes:
    """Union masks without weakening a partially painted pixel."""
    values = list(masks)
    if not values:
        raise ValueError("at least one mask is required")
    length = len(values[0])
    if any(len(mask) != length for mask in values):
        raise ValueError("all masks must have the same pixel count")
    result = bytearray(values[0])
    for mask in values[1:]:
        for index, value in enumerate(mask):
            if value > result[index]:
                result[index] = value
    return bytes(result)


def encode_mask_rgb(alpha: bytes) -> bytes:
    """Encode logical white=edit alpha as an RGB grayscale byte stream."""
    return b"".join(bytes((value, value, value)) for value in alpha)


def encode_comfy_alpha(alpha: bytes) -> bytes:
    """Encode logical white=edit for LoadImage's inverted alpha MASK output."""
    result = bytearray()
    for value in alpha:
        native_alpha = 255 - value
        result.extend((255, 255, 255, native_alpha))
    return bytes(result)


def write_mask_png(
    path: str | Path,
    width: int,
    height: int,
    alpha: bytes,
    *,
    transport: str = "rgb",
) -> None:
    """Write a canonical mask PNG without embedding comments or credentials."""
    _check_alpha(alpha, width, height)
    if transport == "rgb":
        image = Image.frombytes("RGB", (width, height), encode_mask_rgb(alpha))
    elif transport == "comfy-alpha":
        image = Image.frombytes("RGBA", (width, height), encode_comfy_alpha(alpha))
    else:
        raise ValueError("transport must be rgb or comfy-alpha")
    buffer = io.BytesIO()
    image.save(buffer, format="PNG", optimize=False)
    _atomic_bytes_write(path, buffer.getvalue())


def mask_png_sha256(width: int, height: int, alpha: bytes) -> str:
    _check_alpha(alpha, width, height)
    buffer = io.BytesIO()
    Image.frombytes("RGB", (width, height), encode_mask_rgb(alpha)).save(
        buffer,
        format="PNG",
        optimize=False,
    )
    return hashlib.sha256(buffer.getvalue()).hexdigest()


def read_mask_alpha(path: str | Path, *, transport: str = "rgb") -> tuple[int, int, bytes]:
    """Read a mask and return logical white=edit alpha pixels."""
    with Image.open(path) as source:
        image = source.convert("RGBA")
        width, height = image.size
        pixels = image.load()
        if transport == "rgb":
            values = []
            for y in range(height):
                for x in range(width):
                    red, green, blue, _ = pixels[x, y]
                    if red != green or red != blue:
                        raise ValueError("RGB mask must be grayscale")
                    values.append(red)
            alpha = bytes(values)
        elif transport == "comfy-alpha":
            alpha = bytes(255 - pixels[x, y][3] for y in range(height) for x in range(width))
        else:
            raise ValueError("transport must be rgb or comfy-alpha")
    return width, height, alpha


def _relative_file(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ManifestError(f"{field} must be a non-empty relative path")
    if "\x00" in value:
        raise ManifestError(f"{field} contains a NUL byte")
    path = Path(value.replace("\\", "/"))
    if path.is_absolute() or ".." in path.parts:
        raise ManifestError(f"{field} must stay inside the session")
    normalized = path.as_posix()
    if normalized in {"", "."}:
        raise ManifestError(f"{field} must be a non-empty relative path")
    return normalized


def _positive_int(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ManifestError(f"{field} must be a positive integer")
    return value


def _bounds(value: Any, width: int, height: int, field: str) -> list[int]:
    if not isinstance(value, list) or len(value) != 4:
        raise ManifestError(f"{field} must contain four integer bounds")
    if any(isinstance(item, bool) or not isinstance(item, int) for item in value):
        raise ManifestError(f"{field} must contain four integer bounds")
    left, top, right, bottom = value
    if not (0 <= left < right <= width and 0 <= top < bottom <= height):
        raise ManifestError(f"{field} is outside the canvas bounds")
    return [left, top, right, bottom]


def _same_instruction(comments: Iterable[str]) -> bool:
    normalized = {" ".join(comment.split()).casefold() for comment in comments}
    return len(normalized) == 1


def validate_manifest(
    payload: dict[str, Any],
    *,
    image_size: tuple[int, int] | None = None,
    base_dir: str | Path | None = None,
    require_files: bool = False,
) -> dict[str, Any]:
    """Validate and normalize a browser-exported manifest."""
    if not isinstance(payload, dict):
        raise ManifestError("manifest must be an object")
    if payload.get("schema") != SCHEMA:
        raise ManifestError(f"manifest schema must be {SCHEMA}")

    source = payload.get("source")
    if not isinstance(source, dict):
        raise ManifestError("source must be an object")
    width = _positive_int(source.get("width"), "source.width")
    height = _positive_int(source.get("height"), "source.height")
    if image_size is not None and (width, height) != image_size:
        raise ManifestError("manifest canvas size does not match the source image")
    normalized_source = dict(source)
    if "sha256" in source and (
        not isinstance(source["sha256"], str)
        or not re.fullmatch(r"[0-9a-f]{64}", source["sha256"])
    ):
        raise ManifestError("source.sha256 must be a lowercase SHA-256 digest")
    if "file" in source:
        normalized_source["file"] = _relative_file(source["file"], "source.file")
    if base_dir is not None and require_files:
        source_file = normalized_source.get("file")
        if not source_file:
            raise ManifestError("source file is required when file checks are enabled")
        source_path = _safe_session_path(Path(base_dir).resolve(), source_file)
        if not source_path.is_file():
            raise ManifestError(f"missing source file: {source_file}")
        try:
            with Image.open(source_path) as source_image:
                if source_image.size != (width, height):
                    raise ManifestError("source file does not match canvas size")
            declared_source_hash = normalized_source.get("sha256")
            if declared_source_hash is not None and sha256_file(source_path) != declared_source_hash:
                raise ManifestError("source file hash does not match the manifest")
        except ManifestError:
            raise
        except Exception as error:
            raise ManifestError("invalid source file") from error

    session_id = payload.get("session_id", "")
    if not isinstance(session_id, str) or not _SESSION_RE.fullmatch(session_id):
        raise ManifestError("session_id must be a safe identifier")

    convention = payload.get("mask_convention", MASK_CONVENTION)
    if convention != MASK_CONVENTION:
        raise ManifestError(f"mask_convention must be {MASK_CONVENTION}")
    mode = payload.get("mode", "sequential")
    if mode not in {"sequential", "union"}:
        raise ManifestError("mode must be sequential or union")
    overlap_policy = payload.get("overlap_policy", "allow")
    if overlap_policy not in {"allow", "reject"}:
        raise ManifestError("overlap_policy must be allow or reject")

    raw_masks = payload.get("masks")
    if not isinstance(raw_masks, list) or not raw_masks:
        raise ManifestError("masks must contain at least one mask")
    if len(raw_masks) > MAX_MASKS:
        raise ManifestError(f"masks cannot exceed {MAX_MASKS} entries")

    masks: list[dict[str, Any]] = []
    validated_mask_alphas: list[bytes] = []
    ids: set[str] = set()
    for index, raw_mask in enumerate(raw_masks):
        field = f"masks[{index}]"
        if not isinstance(raw_mask, dict):
            raise ManifestError(f"{field} must be an object")
        mask_id = raw_mask.get("id")
        if not isinstance(mask_id, str) or not _ID_RE.fullmatch(mask_id):
            raise ManifestError(f"{field}.id must match {_ID_RE.pattern}")
        if mask_id in ids:
            raise ManifestError(f"duplicate mask id: {mask_id}")
        ids.add(mask_id)
        name = raw_mask.get("name")
        if not isinstance(name, str) or not name.strip() or len(name) > 160:
            raise ManifestError(f"{field}.name must be a non-empty short string")
        comment = raw_mask.get("comment")
        if not isinstance(comment, str) or not comment.strip():
            raise ManifestError(f"{field}.comment must be a non-empty string")
        if len(comment) > MAX_COMMENT_LENGTH:
            raise ManifestError(f"{field}.comment is too long")
        color = raw_mask.get("color", "#f97316")
        if not isinstance(color, str) or not _COLOR_RE.fullmatch(color):
            raise ManifestError(f"{field}.color must be a six-digit hex color")
        visible = raw_mask.get("visible", True)
        if not isinstance(visible, bool):
            raise ManifestError(f"{field}.visible must be boolean")
        file_name = _relative_file(raw_mask.get("file"), f"{field}.file")
        bounds = _bounds(raw_mask.get("bounds"), width, height, f"{field}.bounds")
        if "sha256" in raw_mask and (
            not isinstance(raw_mask["sha256"], str)
            or not re.fullmatch(r"[0-9a-f]{64}", raw_mask["sha256"])
        ):
            raise ManifestError(f"{field}.sha256 must be a lowercase SHA-256 digest")
        normalized = dict(raw_mask)
        normalized.update(
            {
                "id": mask_id,
                "name": name,
                "comment": comment,
                "color": color.lower(),
                "visible": visible,
                "file": file_name,
                "bounds": bounds,
            }
        )
        masks.append(normalized)

        if base_dir is not None and require_files:
            candidate = (Path(base_dir) / file_name).resolve()
            root = Path(base_dir).resolve()
            if root not in candidate.parents:
                raise ManifestError(f"{field}.file escapes the session")
            if not candidate.is_file():
                raise ManifestError(f"missing mask file: {file_name}")
            try:
                mask_width, mask_height, mask_alpha = read_mask_alpha(candidate, transport="rgb")
            except Exception as error:
                raise ManifestError(f"invalid mask file: {file_name}") from error
            if (mask_width, mask_height) != (width, height):
                raise ManifestError(f"mask file {file_name} does not match canvas size")
            actual_bounds = _alpha_bounds(mask_alpha, width, height)
            if actual_bounds is None:
                raise ManifestError(f"mask file {file_name} is empty")
            if actual_bounds != bounds:
                raise ManifestError(f"mask file {file_name} bounds do not match its pixels")
            normalized["pixel_count"] = sum(value > 0 for value in mask_alpha)
            declared_mask_hash = normalized.get("sha256")
            if declared_mask_hash is not None and sha256_file(candidate) != declared_mask_hash:
                raise ManifestError(f"mask file {file_name} hash does not match the manifest")
            validated_mask_alphas.append(mask_alpha)

    if mode == "union" and not _same_instruction(mask["comment"] for mask in masks):
        raise ManifestError("union mode requires every mask to use the same comment")
    union_sha256 = None
    if "union_file" in payload:
        union_file = _relative_file(payload["union_file"], "union_file")
        if require_files and base_dir is not None:
            union_path = _safe_session_path(Path(base_dir).resolve(), union_file)
            if not union_path.is_file():
                raise ManifestError(f"missing union mask file: {union_file}")
            try:
                union_width, union_height, union_pixels = read_mask_alpha(
                    union_path,
                    transport="rgb",
                )
            except Exception as error:
                raise ManifestError("invalid union mask file") from error
            if (union_width, union_height) != (width, height):
                raise ManifestError("union mask does not match canvas size")
            if validated_mask_alphas and union_pixels != union_alpha(validated_mask_alphas):
                raise ManifestError("union mask does not match its member masks")
            union_sha256 = sha256_file(union_path)
            declared_hash = payload.get("union_sha256")
            if declared_hash is not None and declared_hash != union_sha256:
                raise ManifestError("union mask hash does not match the manifest")
    else:
        union_file = None

    normalized_payload = dict(payload)
    if union_file is None:
        normalized_payload.pop("union_file", None)
        normalized_payload.pop("union_sha256", None)
    normalized_payload.update(
        {
            "schema": SCHEMA,
            "session_id": session_id,
            "source": normalized_source,
            "mask_convention": MASK_CONVENTION,
            "mode": mode,
            "overlap_policy": overlap_policy,
            "masks": masks,
        }
    )
    if union_file is not None:
        normalized_payload["union_file"] = union_file
        if union_sha256 is not None:
            normalized_payload["union_sha256"] = union_sha256
    return normalized_payload


def _alpha_bounds(alpha: bytes, width: int, height: int) -> list[int] | None:
    left, top, right, bottom = width, height, -1, -1
    for index, value in enumerate(alpha):
        if not value:
            continue
        x = index % width
        y = index // width
        left = min(left, x)
        top = min(top, y)
        right = max(right, x + 1)
        bottom = max(bottom, y + 1)
    return None if right < 0 else [left, top, right, bottom]


def _safe_prefix(value: str) -> str:
    if not isinstance(value, str) or not _SAFE_PREFIX_RE.fullmatch(value) or ".." in value:
        raise ValueError("output prefix must be a safe relative name")
    return value


def build_prompt(mask_id: str, comment: str) -> str:
    """Turn a human note into a constrained, auditable edit instruction."""
    return (
        f"Repair only the white masked region for mask {mask_id}. Human note:\n"
        f"{comment.strip()}\n\n"
        "White means regenerate; black means preserve. Preserve every pixel, "
        "object, road, building, vehicle, text, lighting, camera, and composition "
        "outside the mask. Match the surrounding image with no extra objects, "
        "labels, logos, or text."
    )


def provider_preserves_aspect(node_type: str, width: int, height: int) -> bool:
    """Return whether a provider can request an output with this source ratio."""
    if width <= 0 or height <= 0:
        return False
    if node_type != "GPTImage15Edit_fal":
        return True
    return width == height or width * 2 == height * 3 or width * 3 == height * 2


def compile_graph(
    *,
    source_file: str,
    mask_file: str,
    prompt: str,
    output_prefix: str,
    width: int,
    height: int,
    node_type: str = "GPTImage15Edit_fal",
    mask_transport: str = "rgb",
    quality: str = "high",
    input_fidelity: str = "high",
    background: str = "opaque",
    output_format: str = "png",
) -> dict[str, dict[str, Any]]:
    """Compile one API-format graph from named uploaded files."""
    source_file = _relative_file(source_file, "source_file")
    mask_file = _relative_file(mask_file, "mask_file")
    output_prefix = _safe_prefix(output_prefix)
    if width < 1 or height < 1:
        raise ValueError("width and height must be positive")
    if not prompt.strip():
        raise ValueError("prompt must not be empty")
    if mask_transport not in {"rgb", "comfy-alpha"}:
        raise ValueError("mask_transport must be rgb or comfy-alpha")

    if mask_transport == "rgb":
        mask_loader: dict[str, Any] = {
            "class_type": "LoadImageMask",
            "inputs": {"image": mask_file, "channel": "red"},
        }
        mask_link = ["2", 0]
    else:
        mask_loader = {"class_type": "LoadImage", "inputs": {"image": mask_file}}
        mask_link = ["2", 1]

    if node_type == "GPTImage2Edit_fal":
        model_inputs: dict[str, Any] = {
            "prompt": prompt,
            "image_1": ["1", 0],
            "image_size": "custom",
            "width": width,
            "height": height,
            "mask_image": ["3", 0],
            "background": background,
            "quality": quality,
            "input_fidelity": input_fidelity,
            "num_images": 1,
            "output_format": output_format,
            "sync_mode": False,
        }
    elif node_type == "GPTImage15Edit_fal":
        model_inputs = {
            "prompt": prompt,
            "images": ["1", 0],
            "mask_image": ["3", 0],
            "image_size": "auto",
            "background": background,
            "quality": quality,
            "input_fidelity": input_fidelity,
            "num_images": 1,
            "output_format": output_format,
            "sync_mode": False,
        }
    elif node_type == "FluxPro1Fill_fal":
        model_inputs = {
            "prompt": prompt,
            "image": ["1", 0],
            "mask_image": ["3", 0],
            "num_images": 1,
            "safety_tolerance": "2",
            "output_format": output_format,
            "seed": -1,
            "sync_mode": False,
            "enhance_prompt": False,
        }
    else:
        raise ValueError(f"unsupported edit node: {node_type}")

    graph = {
        "1": {"class_type": "LoadImage", "inputs": {"image": source_file}},
        "2": mask_loader,
        "3": {"class_type": "MaskToImage", "inputs": {"mask": mask_link}},
        "4": {"class_type": node_type, "inputs": model_inputs},
        "5": {
            "class_type": "SaveImage",
            "inputs": {"images": ["4", 0], "filename_prefix": output_prefix},
        },
    }
    validate_graph(graph)
    return graph


def compile_template_graph(
    template: dict[str, Any],
    *,
    source_file: str,
    mask_file: str,
    prompt: str,
    output_prefix: str,
    width: int,
    height: int,
    node_type: str | None = None,
) -> dict[str, dict[str, Any]]:
    """Turn a ComfyUI editor JSON into a small executable graph.

    The editor document supplies the model/settings; filenames and prompt are
    always replaced with the session-controlled values.
    """
    if not isinstance(template, dict) or not isinstance(template.get("nodes"), list):
        raise ValueError("UI workflow template required")
    nodes = [node for node in template["nodes"] if isinstance(node, dict)]
    types = {str(node.get("type")) for node in nodes}
    if "MaskToImage" not in types or not ({"SaveImage", "PreviewImage"} & types):
        raise ValueError("template must contain MaskToImage and an observable output")
    model_nodes = [
        node for node in nodes
        if node.get("type") in {"GPTImage15Edit_fal", "GPTImage2Edit_fal", "FluxPro1Fill_fal"}
    ]
    if len(model_nodes) != 1:
        raise ValueError("template must contain exactly one supported edit node")
    model = model_nodes[0]
    selected_node = node_type or str(model["type"])
    if selected_node != str(model["type"]):
        raise ValueError("selected node does not match the template edit node")
    named = model.get("widgets_values_named", {})
    if not isinstance(named, dict):
        named = {}

    def setting(name: str, default: Any) -> Any:
        value = named.get(name, default)
        return value if isinstance(value, (str, int, bool)) else default

    node_types = {
        str(node.get("id")): str(node.get("type"))
        for node in nodes
        if isinstance(node.get("id"), (int, str))
    }
    transport_matches = []
    for link in template.get("links", []):
        if not isinstance(link, list) or len(link) < 6 or link[5] != "MASK":
            continue
        source_type = node_types.get(str(link[1]))
        target_type = node_types.get(str(link[3]))
        if target_type != "MaskToImage":
            continue
        if link[4] != 0:
            continue
        if source_type == "LoadImage" and link[2] == 1:
            transport_matches.append("comfy-alpha")
        elif source_type == "LoadImageMask" and link[2] == 0:
            transport_matches.append("rgb")
    if len(transport_matches) != 1:
        raise ValueError("template must contain exactly one mask transport link")
    mask_transport = transport_matches[0]
    return compile_graph(
        source_file=source_file,
        mask_file=mask_file,
        prompt=prompt,
        output_prefix=output_prefix,
        width=width,
        height=height,
        node_type=selected_node,
        mask_transport=mask_transport,
        quality=str(setting("quality", "high")),
        input_fidelity=str(setting("input_fidelity", "high")),
        background=str(setting("background", "opaque")),
        output_format=str(setting("output_format", "png")),
    )


def compile_jobs(
    manifest: dict[str, Any],
    *,
    source_file: str,
    mask_files: dict[str, str],
    checkpoint_sources: dict[str, str] | None = None,
    union_mask_file: str | None = None,
    node_type: str = "GPTImage15Edit_fal",
    mask_transport: str = "rgb",
) -> list[dict[str, Any]]:
    """Compile reviewable sequential jobs or one opt-in union job."""
    normalized = validate_manifest(manifest)
    source_file = _relative_file(source_file, "source_file")
    checkpoint_sources = checkpoint_sources or {}
    masks = normalized["masks"]
    missing = [mask["id"] for mask in masks if mask["id"] not in mask_files]
    if missing:
        raise ManifestError(f"missing mask files: {', '.join(missing)}")

    if normalized["mode"] == "union":
        if not union_mask_file:
            return [
                {
                    "job_id": f"union-{normalized['session_id']}",
                    "mask_id": "union",
                    "source_file": source_file,
                    "mask_file": None,
                    "prompt": build_prompt("union", masks[0]["comment"]),
                    "requires_union_mask": True,
                    "requires_checkpoint": False,
                    "graph": None,
                }
            ]
        graph = compile_graph(
            source_file=source_file,
            mask_file=union_mask_file,
            prompt=build_prompt("union", masks[0]["comment"]),
            output_prefix=f"mask_workbench/{normalized['session_id']}/union",
            width=normalized["source"]["width"],
            height=normalized["source"]["height"],
            node_type=node_type,
            mask_transport=mask_transport,
        )
        return [
            {
                "job_id": f"union-{normalized['session_id']}",
                "mask_id": "union",
                "source_file": source_file,
                "mask_file": _relative_file(union_mask_file, "union_mask_file"),
                "prompt": build_prompt("union", masks[0]["comment"]),
                "requires_union_mask": False,
                "requires_checkpoint": False,
                "graph": graph,
            }
        ]

    jobs: list[dict[str, Any]] = []
    for index, mask in enumerate(masks):
        mask_id = mask["id"]
        current_source = source_file if index == 0 else checkpoint_sources.get(mask_id)
        graph = None
        requires_checkpoint = index > 0 and current_source is None
        if current_source is not None:
            graph = compile_graph(
                source_file=current_source,
                mask_file=mask_files[mask_id],
                prompt=build_prompt(mask_id, mask["comment"]),
                output_prefix=f"mask_workbench/{normalized['session_id']}/{mask_id}",
                width=normalized["source"]["width"],
                height=normalized["source"]["height"],
                node_type=node_type,
                mask_transport=mask_transport,
            )
        jobs.append(
            {
                "job_id": f"{normalized['session_id']}-{index + 1:02d}-{mask_id}",
                "mask_id": mask_id,
                "source_file": current_source,
                "mask_file": _relative_file(mask_files[mask_id], f"mask_files[{mask_id}]"),
                "prompt": build_prompt(mask_id, mask["comment"]),
                "requires_union_mask": False,
                "requires_checkpoint": requires_checkpoint,
                "graph": graph,
            }
        )
    return jobs


def initial_execution_state(manifest: dict[str, Any]) -> dict[str, Any]:
    """Create the durable checkpoint cursor for a saved manifest."""
    normalized = validate_manifest(manifest)
    source_file = normalized["source"].get("file")
    if not isinstance(source_file, str):
        raise ManifestError("source.file is required for execution")
    return {
        "schema": "carrier-mask-execution/v1",
        "mode": normalized["mode"],
        "next_index": 0,
        "current_source": source_file,
        "accepted": [],
        "pending": None,
    }


def manifest_identity(manifest: dict[str, Any]) -> str:
    """Hash only human-editable manifest fields, not generated file receipts."""
    normalized = validate_manifest(manifest)
    identity = json.loads(json.dumps(normalized))
    identity.pop("union_file", None)
    identity.pop("union_sha256", None)
    for mask in identity.get("masks", []):
        mask.pop("pixel_count", None)
    return hashlib.sha256(
        json.dumps(identity, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _can_reuse_checkpoint_state(
    manifest: dict[str, Any], previous_manifest: dict[str, Any], state: dict[str, Any]
) -> bool:
    current = validate_manifest(manifest)
    previous = validate_manifest(previous_manifest)
    if current["mode"] != previous["mode"]:
        return False
    current_source = dict(current["source"])
    previous_source = dict(previous["source"])
    if (
        "sha256" in current_source
        or "sha256" in previous_source
    ) and current_source.get("sha256") != previous_source.get("sha256"):
        return False
    current_source.pop("sha256", None)
    previous_source.pop("sha256", None)
    if current_source != previous_source:
        return False
    index = state.get("next_index")
    if isinstance(index, bool) or not isinstance(index, int) or index < 0:
        return False
    if current["mode"] == "union":
        return index == 0
    current_masks = current["masks"]
    previous_masks = previous["masks"]
    if index > len(current_masks) or index > len(previous_masks):
        return False
    def human_mask(mask: dict[str, Any]) -> dict[str, Any]:
        result = dict(mask)
        result.pop("pixel_count", None)
        return result

    return [human_mask(mask) for mask in current_masks[:index]] == [
        human_mask(mask) for mask in previous_masks[:index]
    ]


def execution_state_for_manifest(
    manifest: dict[str, Any],
    state: dict[str, Any] | None = None,
    *,
    previous_manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return state only when accepted checkpoint inputs remain unchanged."""
    digest = manifest_identity(manifest)
    if not isinstance(state, dict) or state.get("manifest_digest") != digest:
        if (
            isinstance(state, dict)
            and isinstance(previous_manifest, dict)
            and state.get("pending") is None
            and _can_reuse_checkpoint_state(manifest, previous_manifest, state)
        ):
            updated = json.loads(json.dumps(state))
            updated["manifest_digest"] = digest
            updated["mode"] = manifest["mode"]
            return updated
        updated = initial_execution_state(manifest)
        updated["manifest_digest"] = digest
        return updated
    updated = json.loads(json.dumps(state))
    updated["manifest_digest"] = digest
    return updated


def next_mask_id(manifest: dict[str, Any], state: dict[str, Any]) -> str | None:
    normalized = validate_manifest(manifest)
    if state.get("pending") is not None:
        raise ValueError("pending candidate must be accepted or rejected first")
    index = state.get("next_index")
    if not isinstance(index, int) or index < 0:
        raise ValueError("invalid execution cursor")
    if normalized["mode"] == "union":
        return "union" if index == 0 else None
    return normalized["masks"][index]["id"] if index < len(normalized["masks"]) else None


def mark_candidate(
    manifest: dict[str, Any],
    state: dict[str, Any],
    *,
    mask_id: str,
    prompt_id: str,
    file: str,
) -> dict[str, Any]:
    expected = next_mask_id(manifest, state)
    if expected != mask_id:
        raise ValueError(f"candidate is out of order; expected {expected}")
    if not re.fullmatch(r"[A-Za-z0-9-]{8,128}", prompt_id):
        raise ValueError("invalid prompt id")
    candidate_file = _candidate_reference(file, "candidate.file")
    updated = json.loads(json.dumps(state))
    updated["pending"] = {"mask_id": mask_id, "prompt_id": prompt_id, "file": candidate_file}
    return updated


def accept_candidate(
    state: dict[str, Any],
    *,
    prompt_id: str,
    candidate_sha256: str | None = None,
    dimensions: tuple[int, int] | list[int] | None = None,
) -> dict[str, Any]:
    pending = state.get("pending")
    if not isinstance(pending, dict) or pending.get("prompt_id") != prompt_id:
        raise ValueError("no matching pending candidate")
    updated = json.loads(json.dumps(state))
    if not isinstance(candidate_sha256, str) or not re.fullmatch(
        r"[0-9a-f]{64}", candidate_sha256
    ):
        raise ValueError("candidate hash is required and must be lowercase hex")
    if (
        not isinstance(dimensions, (tuple, list))
        or len(dimensions) != 2
        or any(not isinstance(value, int) or value <= 0 for value in dimensions)
    ):
        raise ValueError("candidate dimensions are required and must be positive")
    pending_copy = dict(pending)
    pending_copy["sha256"] = candidate_sha256
    pending_copy["dimensions"] = list(dimensions)
    updated["accepted"].append(pending_copy)
    updated["current_source"] = pending_copy["file"]
    updated["next_index"] += 1
    updated["pending"] = None
    return updated


def reject_candidate(state: dict[str, Any], *, prompt_id: str) -> dict[str, Any]:
    """Discard a pending candidate without making it the next checkpoint."""
    pending = state.get("pending")
    if not isinstance(pending, dict) or pending.get("prompt_id") != prompt_id:
        raise ValueError("no matching pending candidate")
    updated = json.loads(json.dumps(state))
    updated.setdefault("rejected", []).append(dict(pending))
    updated["pending"] = None
    return updated


def _is_link(value: Any, node_ids: set[str]) -> bool:
    return (
        isinstance(value, list)
        and len(value) == 2
        and str(value[0]) in node_ids
        and isinstance(value[1], int)
        and not isinstance(value[1], bool)
    )


def _iter_links(value: Any, node_ids: set[str]) -> Iterable[tuple[str, int]]:
    if _is_link(value, node_ids):
        yield str(value[0]), value[1]
    elif isinstance(value, dict):
        for child in value.values():
            yield from _iter_links(child, node_ids)
    elif isinstance(value, list):
        for child in value:
            yield from _iter_links(child, node_ids)


def validate_graph(
    graph: dict[str, Any], *, schemas: dict[str, Any] | None = None
) -> None:
    """Reject UI graphs, dangling links, cycles, and missing output sinks."""
    if not isinstance(graph, dict) or "nodes" in graph or "links" in graph:
        raise ValueError("API-format graph required; UI workflow JSON is not executable")
    if not graph:
        raise ValueError("graph must not be empty")
    node_ids = {str(node_id) for node_id in graph}
    for node_id, node in graph.items():
        if not isinstance(node, dict) or not isinstance(node.get("class_type"), str):
            raise ValueError(f"node {node_id} must contain class_type")
        if not isinstance(node.get("inputs"), dict):
            raise ValueError(f"node {node_id} must contain inputs")
        if schemas is not None and str(node["class_type"]) not in schemas:
            raise ValueError(f"unknown node class: {node['class_type']}")
        for target_id, output_index in _iter_links(node["inputs"], node_ids):
            if output_index < 0:
                raise ValueError(f"negative output index in node {node_id}")
            if target_id == str(node_id):
                raise ValueError(f"self-cycle at node {node_id}")

    # A small dependency DFS catches cycles without assuming a particular graph shape.
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node_id: str) -> None:
        if node_id in visiting:
            raise ValueError("graph contains a cycle")
        if node_id in visited:
            return
        visiting.add(node_id)
        for target_id, _ in _iter_links(graph[node_id]["inputs"], node_ids):
            visit(target_id)
        visiting.remove(node_id)
        visited.add(node_id)

    for node_id in node_ids:
        visit(node_id)
    if not any(
        node.get("class_type") in {"SaveImage", "PreviewImage", "SaveVideo", "SaveAudio"}
        for node in graph.values()
    ):
        raise ValueError("graph must have an observable output node")


def validate_graph_schemas(
    graph: dict[str, Any],
    schemas: dict[str, Any],
    *,
    uploaded_files: set[str] | None = None,
) -> None:
    """Validate an API graph against `/object_info`-shaped schema data."""
    validate_graph(graph)
    node_ids = {str(node_id) for node_id in graph}
    for node_id, node in graph.items():
        class_name = str(node["class_type"])
        raw_schema = schemas.get(class_name)
        if raw_schema is None:
            raise ValueError(f"unknown node class: {class_name}")
        schema = raw_schema.get(class_name, raw_schema) if isinstance(raw_schema, dict) else {}
        input_schema = schema.get("input", {}) if isinstance(schema, dict) else {}
        required = input_schema.get("required", {})
        optional = input_schema.get("optional", {})
        hidden = input_schema.get("hidden", {})
        known = set(required) | set(optional) | set(hidden)
        inputs = node["inputs"]
        for name in required:
            if name not in inputs:
                raise ValueError(f"node {node_id} missing required input {name}")
        for name, value in inputs.items():
            if name not in known:
                raise ValueError(f"node {node_id} has unknown input {name}")
            if _is_link(value, node_ids):
                source_node = graph[str(value[0])]
                source_schema_raw = schemas.get(str(source_node["class_type"]), {})
                source_schema = (
                    source_schema_raw.get(str(source_node["class_type"]), source_schema_raw)
                    if isinstance(source_schema_raw, dict)
                    else {}
                )
                outputs = source_schema.get("output", []) if isinstance(source_schema, dict) else []
                if outputs and value[1] >= len(outputs):
                    raise ValueError(f"node {node_id} link points past {value[0]} outputs")
                expected_type = _schema_type(required.get(name) or optional.get(name) or hidden.get(name))
                actual_type = str(outputs[value[1]]) if outputs else None
                if expected_type and actual_type and expected_type != actual_type:
                    raise ValueError(
                        f"node {node_id} input {name} expects {expected_type}, got {actual_type}"
                    )
                continue
            spec = required.get(name) or optional.get(name) or hidden.get(name)
            enum_values = _schema_enum(spec)
            uploaded_image = (
                uploaded_files is not None
                and isinstance(value, str)
                and value in uploaded_files
                and class_name in {"LoadImage", "LoadImageMask"}
                and name == "image"
            )
            if enum_values and value not in enum_values and not uploaded_image:
                raise ValueError(f"node {node_id} input {name} has invalid enum value {value}")
            value_type = _schema_type(spec)
            if value_type == "INT" and (isinstance(value, bool) or not isinstance(value, int)):
                raise ValueError(f"node {node_id} input {name} must be an integer")
            if value_type == "BOOLEAN" and not isinstance(value, bool):
                raise ValueError(f"node {node_id} input {name} must be boolean")
            if value_type in {"STRING", "COMBO", "COLOR"} and not isinstance(value, str):
                raise ValueError(f"node {node_id} input {name} must be a string")

    # Every observable output must be downstream of the edit node. A saver that
    # only receives the source or mask would make a paid run look successful.
    edit_ids = {
        str(node_id)
        for node_id, node in graph.items()
        if "_fal" in str(node["class_type"]).lower()
    }
    observable_ids = {
        str(node_id)
        for node_id, node in graph.items()
        if node["class_type"] in {"SaveImage", "PreviewImage", "SaveVideo", "SaveAudio"}
    }
    if edit_ids and not any(
        _depends_on(graph, observable_id, edit_ids, node_ids)
        for observable_id in observable_ids
    ):
        raise ValueError("observable output is not downstream of the edit node")


def _depends_on(
    graph: dict[str, Any],
    node_id: str,
    targets: set[str],
    node_ids: set[str],
    seen: set[str] | None = None,
) -> bool:
    if node_id in targets:
        return True
    visited = set() if seen is None else seen
    if node_id in visited:
        return False
    visited.add(node_id)
    return any(
        _depends_on(graph, source_id, targets, node_ids, visited)
        for source_id, _ in _iter_links(graph[node_id]["inputs"], node_ids)
    )


def _schema_type(spec: Any) -> str | None:
    if isinstance(spec, list) and spec:
        if isinstance(spec[0], str):
            return spec[0]
    return None


def _schema_enum(spec: Any) -> list[Any] | None:
    if isinstance(spec, list) and spec and isinstance(spec[0], list):
        return spec[0]
    return None


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def uploaded_name(response: dict[str, Any]) -> str:
    """Return the session-relative filename returned by a Comfy upload."""
    if not isinstance(response, dict) or not isinstance(response.get("name"), str):
        raise ValueError("upload response has no filename")
    name = response["name"]
    subfolder = response.get("subfolder", "")
    if not isinstance(subfolder, str):
        raise ValueError("upload response has an invalid subfolder")
    combined = f"{subfolder}/{name}" if subfolder else name
    return _relative_file(combined, "uploaded filename")


def _validate_execution_state_shape(
    state: dict[str, Any],
    manifest: dict[str, Any],
    *,
    base_dir: Path | None = None,
) -> None:
    normalized = validate_manifest(manifest)
    if state.get("schema") != "carrier-mask-execution/v1":
        raise ValueError("execution state has an invalid schema")
    if state.get("mode") != normalized["mode"]:
        raise ValueError("execution state mode does not match the manifest")
    index = state.get("next_index")
    limit = 1 if normalized["mode"] == "union" else len(normalized["masks"])
    if isinstance(index, bool) or not isinstance(index, int) or not 0 <= index <= limit:
        raise ValueError("execution state has an invalid cursor")
    accepted = state.get("accepted")
    if not isinstance(accepted, list) or len(accepted) != index:
        raise ValueError("execution state has an invalid accepted history")
    expected_ids = (
        ["union"] if normalized["mode"] == "union" else [mask["id"] for mask in normalized["masks"]]
    )
    accepted_files: set[str] = set()
    accepted_prompts: set[str] = set()
    for position, record in enumerate(accepted):
        if not isinstance(record, dict) or record.get("mask_id") != expected_ids[position]:
            raise ValueError("execution state accepted history is out of order")
        prompt_id = record.get("prompt_id")
        if not isinstance(prompt_id, str) or not re.fullmatch(r"[A-Za-z0-9-]{8,128}", prompt_id):
            raise ValueError("execution state has an invalid accepted prompt")
        candidate_file = _candidate_reference(record.get("file"), "execution.accepted.file")
        if candidate_file in accepted_files or prompt_id in accepted_prompts:
            raise ValueError("execution state accepted history contains duplicates")
        accepted_files.add(candidate_file)
        accepted_prompts.add(prompt_id)
        _validate_checkpoint_record(record, candidate_file, base_dir, normalized["source"]["width"], normalized["source"]["height"])
    current_source = state.get("current_source")
    if not isinstance(current_source, str):
        raise ValueError("execution state has no current source")
    current_source = _relative_file(current_source, "execution.current_source")
    expected_source = normalized["source"].get("file") if index == 0 else accepted[-1].get("file")
    if current_source != expected_source:
        raise ValueError("execution state current source does not match accepted history")
    if base_dir is not None:
        _validate_checkpoint_file(base_dir, current_source, normalized["source"]["width"], normalized["source"]["height"])
    pending = state.get("pending")
    if pending is None:
        return
    if not isinstance(pending, dict):
        raise ValueError("execution state has an invalid pending candidate")
    prompt_id = pending.get("prompt_id")
    if not isinstance(prompt_id, str) or not re.fullmatch(r"[A-Za-z0-9-]{8,128}", prompt_id):
        raise ValueError("execution state has an invalid pending prompt")
    pending_file = _candidate_reference(pending.get("file"), "execution.pending.file")
    if pending_file in accepted_files or pending_file == current_source:
        raise ValueError("execution state pending file conflicts with the source chain")
    if normalized["mode"] != "union" and index >= len(normalized["masks"]):
        raise ValueError("execution state has a pending candidate after completion")
    expected = "union" if normalized["mode"] == "union" else normalized["masks"][index]["id"]
    if pending.get("mask_id") != expected:
        raise ValueError("execution state pending mask is out of order")


def _candidate_reference(value: Any, field: str) -> str:
    relative = _relative_file(value, field)
    if not relative.startswith("candidates/") or not relative.lower().endswith(".png"):
        raise ValueError(f"{field} must be a PNG under candidates/")
    return relative


def _validate_checkpoint_file(
    base_dir: Path, relative: str, width: int, height: int
) -> None:
    path = _safe_session_path(base_dir, relative)
    if not path.is_file():
        raise ValueError(f"execution checkpoint file is missing: {relative}")
    try:
        with Image.open(path) as image:
            if image.size != (width, height):
                raise ValueError(f"execution checkpoint has invalid dimensions: {relative}")
            image.verify()
    except ValueError:
        raise
    except Exception as error:
        raise ValueError(f"execution checkpoint is invalid: {relative}") from error


def _validate_checkpoint_record(
    record: dict[str, Any],
    relative: str,
    base_dir: Path | None,
    width: int,
    height: int,
) -> None:
    digest = record.get("sha256")
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise ValueError("execution accepted record has a required invalid hash")
    dimensions = record.get("dimensions")
    if (
        not isinstance(dimensions, list)
        or len(dimensions) != 2
        or dimensions != [width, height]
    ):
        raise ValueError("execution accepted record has required invalid dimensions")
    if base_dir is not None:
        _validate_checkpoint_file(base_dir, relative, width, height)
        if sha256_file(_safe_session_path(base_dir, relative)) != digest:
            raise ValueError("execution accepted record hash does not match its file")


def load_execution_state(session_dir: str | Path, manifest: dict[str, Any]) -> dict[str, Any]:
    """Load a checkpoint cursor and fail closed when its durable file is corrupt."""
    root = Path(session_dir).resolve()
    state_path = root / "execution.json"
    state: dict[str, Any] | None = None
    if state_path.is_file():
        try:
            value = json.loads(state_path.read_text())
        except (OSError, json.JSONDecodeError) as error:
            raise RuntimeError("execution state is unreadable; refusing to continue") from error
        if not isinstance(value, dict):
            raise RuntimeError("execution state is invalid; refusing to continue")
        state = value
    if state is not None:
        expected_digest = manifest_identity(manifest)
        if state.get("manifest_digest") != expected_digest:
            raise RuntimeError(
                "execution state does not match the saved manifest; refusing to continue"
            )
        updated = execution_state_for_manifest(manifest, state)
        try:
            _validate_execution_state_shape(updated, manifest, base_dir=root)
        except (ValueError, TypeError, KeyError) as error:
            raise RuntimeError("execution state is invalid; refusing to continue") from error
    else:
        updated = execution_state_for_manifest(manifest)
    current_source = updated.get("current_source")
    if not isinstance(current_source, str):
        raise ValueError("execution state has no current source")
    _relative_file(current_source, "execution.current_source")
    return updated


def _assert_no_symlink_components(path: Path) -> None:
    absolute = path if path.is_absolute() else path.absolute()
    current = Path(absolute.anchor)
    for component in absolute.parts[1:]:
        current /= component
        if current.is_symlink():
            raise ValueError(f"path contains a symlink: {current}")


def _atomic_bytes_write(path: str | Path, data: bytes, *, mode: int = 0o600) -> None:
    destination = Path(path)
    if not destination.is_absolute():
        destination = destination.absolute()
    _assert_no_symlink_components(destination.parent)
    destination.parent.mkdir(parents=True, exist_ok=True)
    _assert_no_symlink_components(destination.parent)
    if destination.is_symlink():
        raise ValueError(f"refusing to replace symlink: {destination}")
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.{os.getpid()}.{threading.get_ident()}.",
        dir=destination.parent,
    )
    try:
        with os.fdopen(descriptor, "wb") as temporary:
            temporary.write(data)
            temporary.flush()
            os.fsync(temporary.fileno())
            os.fchmod(temporary.fileno(), mode)
        os.replace(temporary_name, destination)
        directory = os.open(destination.parent, os.O_RDONLY)
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


def _atomic_json_write(path: str | Path, value: Any) -> None:
    data = (json.dumps(_redact(value), ensure_ascii=False, indent=2) + "\n").encode()
    _atomic_bytes_write(path, data)


def save_execution_state(session_dir: str | Path, state: dict[str, Any]) -> None:
    root = Path(session_dir).resolve()
    _atomic_json_write(root / "execution.json", state)


def _safe_output_reference(reference: Any) -> dict[str, Any]:
    if not isinstance(reference, dict):
        raise ValueError("output reference must be an object")
    filename = reference.get("filename")
    subfolder = reference.get("subfolder", "")
    output_type = reference.get("type", "output")
    if (
        not isinstance(filename, str)
        or not filename
        or "\x00" in filename
        or Path(filename).is_absolute()
        or "/" in filename
        or "\\" in filename
        or ".." in Path(filename).parts
    ):
        raise ValueError("unsafe output filename")
    if (
        not isinstance(subfolder, str)
        or "\x00" in subfolder
        or Path(subfolder).is_absolute()
        or ".." in Path(subfolder).parts
    ):
        raise ValueError("unsafe output subfolder")
    if output_type not in {"output", "temp"}:
        raise ValueError("unsafe output type")
    return {"filename": filename, "subfolder": subfolder, "type": output_type}


def normalize_checkpoint(
    source: str | Path,
    destination: str | Path,
    target_size: tuple[int, int],
) -> dict[str, list[int]]:
    """Normalize a provider output without changing its aspect ratio."""
    if target_size[0] <= 0 or target_size[1] <= 0:
        raise ValueError("target checkpoint size must be positive")
    with Image.open(source) as image:
        raw_size = image.size
        if raw_size[0] * target_size[1] != target_size[0] * raw_size[1]:
            raise ValueError("checkpoint aspect ratio differs from the source canvas")
        normalized = image.convert("RGB")
        if normalized.size != target_size:
            normalized = normalized.resize(target_size, Image.Resampling.LANCZOS)
        buffer = io.BytesIO()
        normalized.save(buffer, format="PNG", optimize=False)
        _atomic_bytes_write(destination, buffer.getvalue())
    return {"raw_size": list(raw_size), "size": list(target_size)}


def protected_pixel_diff(
    source: str | Path,
    candidate: str | Path,
    mask: str | Path,
    target_size: tuple[int, int],
) -> dict[str, int]:
    """Measure candidate changes where the logical mask is black."""
    with Image.open(source) as source_image, Image.open(candidate) as candidate_image:
        source_rgb = source_image.convert("RGB")
        candidate_rgb = candidate_image.convert("RGB")
        if source_rgb.size != target_size or candidate_rgb.size != target_size:
            raise ValueError("protected-pixel comparison dimensions do not match")
        mask_width, mask_height, logical = read_mask_alpha(mask, transport="rgb")
        if (mask_width, mask_height) != target_size:
            raise ValueError("protected-pixel mask dimensions do not match")
        mask_image = Image.frombytes("L", target_size, logical)
        preserve = mask_image.point(lambda value: 255 if value == 0 else 0)
        difference = ImageChops.multiply(
            ImageChops.difference(source_rgb, candidate_rgb).convert("L"),
            preserve,
        )
        histogram = difference.histogram()
        return {
            "outside_changed_pixels": sum(histogram[1:]),
            "outside_max_delta": max(
                (value for value, count in enumerate(histogram) if value and count),
                default=0,
            ),
        }


def composite_checkpoint(
    source: str | Path,
    generated: str | Path,
    mask: str | Path,
    destination: str | Path,
    target_size: tuple[int, int],
) -> dict[str, int]:
    """Keep protected pixels byte-identical while retaining the generated region."""
    with Image.open(source) as source_image, Image.open(generated) as generated_image:
        source_rgb = source_image.convert("RGB")
        generated_rgb = generated_image.convert("RGB")
        if source_rgb.size != target_size or generated_rgb.size != target_size:
            raise ValueError("checkpoint composite dimensions do not match")
        mask_width, mask_height, logical = read_mask_alpha(mask, transport="rgb")
        if (mask_width, mask_height) != target_size:
            raise ValueError("checkpoint mask dimensions do not match")
        mask_image = Image.frombytes("L", target_size, logical)
        provider_diff = protected_pixel_diff(source, generated, mask, target_size)
        composited = Image.composite(generated_rgb, source_rgb, mask_image)
        buffer = io.BytesIO()
        composited.save(buffer, format="PNG", optimize=False)
        _atomic_bytes_write(destination, buffer.getvalue())
    final_diff = protected_pixel_diff(source, destination, mask, target_size)
    if final_diff["outside_changed_pixels"]:
        raise ValueError("checkpoint composite changed protected pixels")
    return {
        "provider_outside_changed_pixels": provider_diff["outside_changed_pixels"],
        "provider_outside_max_delta": provider_diff["outside_max_delta"],
        **final_diff,
    }


def extract_output_reference(history: dict[str, Any], prompt_id: str) -> dict[str, Any]:
    """Find the first image emitted by a completed prompt, safely."""
    entry = history.get(prompt_id) if isinstance(history, dict) else None
    outputs = entry.get("outputs", {}) if isinstance(entry, dict) else {}
    if not isinstance(outputs, dict):
        raise ValueError("history has no output images")
    for output in outputs.values():
        if not isinstance(output, dict):
            continue
        images = output.get("images", [])
        if isinstance(images, list):
            for reference in images:
                if isinstance(reference, dict) and reference.get("filename"):
                    return _safe_output_reference(reference)
    raise ValueError("history has no output images")


def stable_submission_fingerprint(graph: dict[str, Any]) -> str:
    """Hash a job without volatile remote upload filenames."""
    stable = json.loads(json.dumps(graph))
    for node in stable.values():
        if not isinstance(node, dict) or node.get("class_type") not in {"LoadImage", "LoadImageMask"}:
            continue
        inputs = node.get("inputs")
        if isinstance(inputs, dict) and isinstance(inputs.get("image"), str):
            inputs["image"] = "__uploaded_image__"
    return hashlib.sha256(
        json.dumps(stable, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _redact(value: Any) -> Any:
    if isinstance(value, dict):
        result: dict[str, Any] = {}
        for key, child in value.items():
            if re.search(r"(?:api[_-]?key|authorization|secret|token|password)", str(key), re.I):
                result[key] = "[redacted]"
            else:
                result[key] = _redact(child)
        return result
    if isinstance(value, list):
        return [_redact(child) for child in value]
    return value


def submission_recovery_record(
    submission: dict[str, Any],
    execution: dict[str, Any],
    *,
    receipt_name: str,
) -> dict[str, Any]:
    """Persist enough post-submit context to reconcile without the submit receipt."""
    if not isinstance(submission, dict) or not isinstance(execution, dict):
        raise ValueError("submission and execution must be objects")
    prompt_id = submission.get("prompt_id")
    if not isinstance(prompt_id, str):
        raise ValueError("submission has no prompt id")
    return {
        "prompt_id": prompt_id,
        "receipt": receipt_name,
        "submission": _redact(submission),
        "execution": _redact(execution),
        "reason": "post-submit session persistence failed",
    }


def _json_request(
    base_url: str,
    path: str,
    *,
    method: str = "GET",
    payload: bytes | None = None,
    content_type: str | None = None,
    timeout: float = 30,
) -> tuple[int, bytes]:
    url = base_url.rstrip("/") + path
    headers = {"Accept": "application/json"}
    if content_type:
        headers["Content-Type"] = content_type
    request = Request(url, data=payload, headers=headers, method=method)
    with _NO_REDIRECT_OPENER.open(request, timeout=timeout) as response:
        return response.status, response.read()


def _multipart(fields: dict[str, str], file_field: str, filename: str, content: bytes) -> tuple[bytes, str]:
    boundary = f"----maskworkbench{secrets.token_hex(12)}"
    chunks: list[bytes] = []
    for name, value in fields.items():
        chunks.extend(
            [
                f"--{boundary}\r\n".encode(),
                f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode(),
                value.encode(),
                b"\r\n",
            ]
        )
    chunks.extend(
        [
            f"--{boundary}\r\n".encode(),
            f'Content-Disposition: form-data; name="{file_field}"; filename="{Path(filename).name}"\r\n'.encode(),
            f"Content-Type: {mimetypes.guess_type(filename)[0] or 'application/octet-stream'}\r\n\r\n".encode(),
            content,
            b"\r\n",
            f"--{boundary}--\r\n".encode(),
        ]
    )
    return b"".join(chunks), f"multipart/form-data; boundary={boundary}"


class ComfyController:
    """Small guarded client for the local ComfyUI HTTP/WebSocket boundary."""

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8191",
        *,
        session_dir: str | Path,
        client_id: str | None = None,
        timeout: float = 30,
        allow_paid: bool = False,
    ) -> None:
        parsed = urlparse(base_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("ComfyUI URL must be an HTTP(S) URL")
        if parsed.username is not None or parsed.password is not None:
            raise ValueError("ComfyUI URL must not contain credentials")
        if parsed.query or parsed.fragment:
            raise ValueError("ComfyUI URL must not contain a query or fragment")
        if parsed.path not in {"", "/"} or parsed.params:
            raise ValueError("ComfyUI URL must be a loopback origin without a path")
        if parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
            raise ValueError("ComfyUI must use a loopback URL")
        self.base_url = base_url.rstrip("/")
        self.session_dir = Path(session_dir).resolve()
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.client_id = client_id or "mask-workbench-" + hashlib.sha256(
            str(self.session_dir).encode()
        ).hexdigest()[:16]
        self.timeout = timeout
        self.allow_paid = allow_paid
        self.ledger_path = self.session_dir / "jobs.json"
        self.ledger_lock_path = self.session_dir / "jobs.lock"
        self._submit_lock = threading.Lock()
        self._socket_lock = threading.Lock()
        self._watch_sockets: dict[str, Any] = {}

    def json(self, path: str) -> Any:
        status, body = _json_request(self.base_url, path, timeout=self.timeout)
        if status < 200 or status >= 300:
            raise RuntimeError(f"ComfyUI returned HTTP {status} for {path}")
        try:
            return json.loads(body)
        except json.JSONDecodeError as error:
            raise RuntimeError(f"ComfyUI returned non-JSON data for {path}") from error

    def health(self) -> Any:
        return self.json("/system_stats")

    def preflight_graph(
        self,
        graph: dict[str, Any],
        *,
        uploaded_files: set[str] | None = None,
    ) -> None:
        """Fetch live node schemas and reject a graph before `/prompt`."""
        validate_graph(graph)
        classes = {str(node["class_type"]) for node in graph.values()}
        schemas: dict[str, Any] = {}
        for class_name in classes:
            response = self.json(f"/object_info/{quote(class_name, safe='')}")
            if not isinstance(response, dict) or class_name not in response:
                raise ValueError(f"ComfyUI did not expose schema for {class_name}")
            schemas[class_name] = response[class_name]
        validate_graph_schemas(graph, schemas, uploaded_files=uploaded_files)
        if uploaded_files is not None:
            for node in graph.values():
                if node["class_type"] not in {"LoadImage", "LoadImageMask"}:
                    continue
                filename = node["inputs"].get("image")
                if isinstance(filename, str) and filename not in uploaded_files:
                    raise ValueError(f"graph input has not been uploaded: {filename}")

    def queue(self) -> Any:
        return self.json("/queue")

    def history(self, prompt_id: str) -> Any:
        if not re.fullmatch(r"[A-Za-z0-9-]{8,128}", prompt_id):
            raise ValueError("invalid prompt id")
        return self.json(f"/history/{quote(prompt_id, safe='')}")

    def upload_image(self, path: str | Path, *, filename: str | None = None) -> dict[str, Any]:
        source = Path(path).resolve()
        if not source.is_file():
            raise FileNotFoundError(source)
        body, content_type = _multipart(
            {"type": "input", "overwrite": "false"},
            "image",
            filename or source.name,
            source.read_bytes(),
        )
        status, response_body = _json_request(
            self.base_url,
            "/upload/image",
            method="POST",
            payload=body,
            content_type=content_type,
            timeout=self.timeout,
        )
        if status < 200 or status >= 300:
            raise RuntimeError(f"ComfyUI image upload failed with HTTP {status}")
        result = json.loads(response_body)
        if not isinstance(result, dict) or not result.get("name"):
            raise RuntimeError("ComfyUI image upload returned no filename")
        return _redact(result)

    def upload_mask(self, path: str | Path, original_ref: dict[str, Any]) -> dict[str, Any]:
        """Use ComfyUI's alpha-copy route for native LoadImage mask transport."""
        if not isinstance(original_ref, dict) or not original_ref.get("filename"):
            raise ValueError("original_ref must contain a ComfyUI filename")
        source = Path(path).resolve()
        if not source.is_file():
            raise FileNotFoundError(source)
        body, content_type = _multipart(
            {
                "type": "input",
                "overwrite": "false",
                "original_ref": json.dumps(original_ref, separators=(",", ":")),
            },
            "image",
            source.name,
            source.read_bytes(),
        )
        status, response_body = _json_request(
            self.base_url,
            "/upload/mask",
            method="POST",
            payload=body,
            content_type=content_type,
            timeout=self.timeout,
        )
        if status < 200 or status >= 300:
            raise RuntimeError(f"ComfyUI mask upload failed with HTTP {status}")
        result = json.loads(response_body)
        if not isinstance(result, dict) or not result.get("name"):
            raise RuntimeError("ComfyUI mask upload returned no filename")
        return _redact(result)

    def _load_ledger(self) -> dict[str, Any]:
        if not self.ledger_path.is_file():
            return {}
        try:
            value = json.loads(self.ledger_path.read_text())
        except (OSError, json.JSONDecodeError) as error:
            raise RuntimeError("paid-job ledger is unreadable; refusing submission") from error
        if not isinstance(value, dict):
            raise RuntimeError("paid-job ledger is invalid; refusing submission")
        return value

    def _save_ledger(self, ledger: dict[str, Any]) -> None:
        _atomic_json_write(self.ledger_path, ledger)

    @staticmethod
    def is_paid_graph(graph: dict[str, Any]) -> bool:
        return any(
            "_fal" in str(node.get("class_type", "")).lower()
            or str(node.get("class_type", "")).lower().startswith("fal")
            for node in graph.values()
            if isinstance(node, dict)
        )

    def _websocket_url(self) -> str:
        return self.base_url.replace("https://", "wss://", 1).replace(
            "http://", "ws://", 1
        ) + f"/ws?clientId={quote(self.client_id, safe='')}"

    def _open_websocket(self) -> Any | None:
        try:
            from websockets.sync.client import connect  # type: ignore[import-not-found]

            return connect(self._websocket_url(), open_timeout=min(5.0, self.timeout), close_timeout=1)
        except Exception:
            return None

    @staticmethod
    def _close_websocket(socket: Any | None) -> None:
        if socket is None:
            return
        try:
            socket.close()
        except Exception:
            pass

    def submit(
        self,
        graph: dict[str, Any],
        *,
        confirmation: str | None = None,
        job_key: str | None = None,
        preflighted: bool = False,
    ) -> dict[str, Any]:
        validate_graph(graph)
        paid = self.is_paid_graph(graph)
        if paid and (not self.allow_paid or confirmation != PAID_CONFIRMATION):
            raise PermissionError(
                f"paid submission requires allow_paid and confirmation {PAID_CONFIRMATION}"
            )
        if not preflighted:
            self.preflight_graph(graph)
        fingerprint = hashlib.sha256(
            json.dumps(graph, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        if job_key is not None and (
            not isinstance(job_key, str)
            or len(job_key) > 512
            or re.search(r"[\x00-\x1f]", job_key)
        ):
            raise ValueError("invalid job key")
        key = job_key or fingerprint

        with self._submit_lock, _exclusive_file_lock(self.ledger_lock_path):
            ledger = self._load_ledger()
            previous = ledger.get(key)
            if previous and previous.get("state") not in {"failed-confirmed"}:
                raise DuplicateJobError("job is already recorded")
            ledger[key] = {
                "state": "reserved",
                "fingerprint": fingerprint,
                "recorded_at": time.time(),
            }
            self._save_ledger(ledger)

            # Open the monitor before queueing so fast jobs cannot outrun the client.
            preopened_socket = self._open_websocket()
            payload = json.dumps(
                {"prompt": graph, "client_id": self.client_id},
                separators=(",", ":"),
            ).encode()
            try:
                status, body = _json_request(
                    self.base_url,
                    "/prompt",
                    method="POST",
                    payload=payload,
                    content_type="application/json",
                    timeout=self.timeout,
                )
                result = json.loads(body)
            except Exception as error:
                self._close_websocket(preopened_socket)
                ledger[key] = {
                    "state": "unknown-reconcile-required",
                    "fingerprint": fingerprint,
                    "error": type(error).__name__,
                    "recorded_at": time.time(),
                }
                try:
                    self._save_ledger(ledger)
                except OSError:
                    pass  # The durable reservation still blocks an automatic retry.
                raise RuntimeError(
                    "prompt submission outcome is unknown; inspect ComfyUI queue/history before retrying"
                ) from error
            confirmed_failure = isinstance(result, dict) and (
                400 <= status < 500
                or 200 <= status < 300 and bool(result.get("node_errors"))
            )
            if not isinstance(result, dict) or status < 200 or status >= 300 or result.get("node_errors"):
                self._close_websocket(preopened_socket)
                failure_state = "failed-confirmed" if confirmed_failure else "unknown-reconcile-required"
                ledger[key] = {
                    "state": failure_state,
                    "fingerprint": fingerprint,
                    "response": _redact(result),
                    "recorded_at": time.time(),
                }
                self._save_ledger(ledger)
                if failure_state == "failed-confirmed":
                    raise RuntimeError(f"ComfyUI rejected prompt: {_redact(result)}")
                raise RuntimeError(
                    "prompt submission response was ambiguous; inspect ComfyUI queue/history before retrying"
                )
            prompt_id = result.get("prompt_id")
            if not isinstance(prompt_id, str) or not re.fullmatch(
                r"[A-Za-z0-9-]{8,128}", prompt_id
            ):
                self._close_websocket(preopened_socket)
                ledger[key] = {
                    "state": "unknown-reconcile-required",
                    "fingerprint": fingerprint,
                    "response": _redact(result),
                    "recorded_at": time.time(),
                }
                try:
                    self._save_ledger(ledger)
                except OSError:
                    pass
                raise RuntimeError(
                    "ComfyUI accepted an unsafe prompt id; reconcile before retrying"
                )
            ledger[key] = {
                "state": "submitted",
                "fingerprint": fingerprint,
                "prompt_id": prompt_id,
                "response": _redact(result),
                "recorded_at": time.time(),
            }
            try:
                self._save_ledger(ledger)
            except OSError as error:
                self._close_websocket(preopened_socket)
                try:
                    _atomic_json_write(
                        self.session_dir / f"reconcile-{prompt_id}.json",
                        {
                            "prompt_id": prompt_id,
                            "receipt": None,
                            "submission": {
                                "job_key": key,
                                "fingerprint": fingerprint,
                                "graph": graph,
                                "response": result,
                            },
                            "execution": {},
                            "reason": "provider accepted prompt but final ledger persistence failed",
                        },
                    )
                except OSError:
                    pass
                raise RuntimeError(
                    "prompt was accepted but its final receipt could not be persisted; reconcile before retrying"
                ) from error
            if preopened_socket is not None:
                with self._socket_lock:
                    self._watch_sockets[prompt_id] = preopened_socket
            return _redact(result)

    def mark_terminal_failure(self, prompt_id: str, result: dict[str, Any]) -> None:
        """Make a confirmed execution failure retryable without weakening reservations."""
        if not re.fullmatch(r"[A-Za-z0-9-]{8,128}", prompt_id):
            raise ValueError("invalid prompt id")
        with self._submit_lock, _exclusive_file_lock(self.ledger_lock_path):
            ledger = self._load_ledger()
            matching_keys = [
                candidate
                for candidate, entry in ledger.items()
                if isinstance(entry, dict) and entry.get("prompt_id") == prompt_id
            ]
            if len(matching_keys) != 1:
                raise RuntimeError("terminal failure has an ambiguous recorded submission")
            key = matching_keys[0]
            entry = ledger[key]
            if entry.get("state") == "submitted":
                entry["state"] = "failed-confirmed"
                entry["failure"] = _redact(result)
                entry["recorded_at"] = time.time()
                self._save_ledger(ledger)

    def watch(self, prompt_id: str, *, timeout: float = 600) -> dict[str, Any]:
        """Watch best-effort WebSocket progress, then reconcile through history."""
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        events: list[Any] = []
        deadline = time.monotonic() + timeout
        ws_error: str | None = None
        with self._socket_lock:
            socket = self._watch_sockets.pop(prompt_id, None)
        if socket is None:
            socket = self._open_websocket()
        try:
            if socket is not None:
                while time.monotonic() < deadline:
                    remaining = max(0.1, min(2.0, deadline - time.monotonic()))
                    try:
                        message = socket.recv(timeout=remaining)
                    except TimeoutError:
                        break
                    if isinstance(message, bytes):
                        continue
                    try:
                        event = json.loads(message)
                    except json.JSONDecodeError:
                        continue
                    if isinstance(event, dict):
                        events.append(_redact(event))
                        event_type = event.get("type")
                        data = event.get("data") or {}
                        event_prompt = data.get("prompt_id") if isinstance(data, dict) else None
                        if event_prompt in {None, prompt_id} and event_type in _TERMINAL_EVENTS:
                            break
        except Exception as error:  # history remains authoritative
            ws_error = type(error).__name__
        finally:
            self._close_websocket(socket)

        history: Any = {}
        # A bounded, short persistence window handles execution_success arriving first.
        delays = (0.0, 0.25, 0.5, 1.0, 2.0, 4.0)
        for delay in delays:
            if delay:
                time.sleep(delay)
            try:
                history = self.history(prompt_id)
            except Exception:
                history = {}
            if isinstance(history, dict) and prompt_id in history:
                break
            if time.monotonic() >= deadline:
                break
        entry = history.get(prompt_id, {}) if isinstance(history, dict) else {}
        status = entry.get("status", {}) if isinstance(entry, dict) else {}
        if not isinstance(status, dict):
            status = {}
        status_messages = status.get("messages", [])
        has_error = any(
            isinstance(message, list) and message and message[0] in {"execution_error", "execution_interrupted"}
            for message in status_messages
        )
        status_string = str(status.get("status_str", "")).casefold()
        explicit_failure = status_string in {"error", "failed", "failure", "interrupted", "cancelled", "canceled"}
        outputs = entry.get("outputs", {}) if isinstance(entry, dict) else {}
        completed = bool(isinstance(entry, dict) and status.get("completed"))
        success = bool(
            completed
            and isinstance(outputs, dict)
            and outputs
            and not has_error
            and not explicit_failure
        )
        terminal_failure = has_error or explicit_failure or (completed and not success)
        result = {
            "prompt_id": prompt_id,
            "success": success,
            "events": events,
            "history": _redact(history),
            "websocket_error": ws_error,
            "status": "success" if success else ("failed" if terminal_failure else "unknown/reconcile required"),
        }
        return result

    def download_output(self, reference: dict[str, Any], destination: str | Path) -> Path:
        safe_reference = _safe_output_reference(reference)
        filename = safe_reference["filename"]
        subfolder = safe_reference["subfolder"]
        output_type = safe_reference["type"]
        query = f"filename={quote(filename)}&subfolder={quote(subfolder)}&type={quote(str(output_type))}"
        url = f"{self.base_url}/view?{query}"
        with _NO_REDIRECT_OPENER.open(Request(url, headers={"Accept": "image/*"}), timeout=self.timeout) as response:
            content_type = response.headers.get_content_type()
            content_length = response.headers.get("Content-Length")
            if content_type not in {"image/png", "image/jpeg", "image/webp"}:
                raise ValueError("ComfyUI output is not a supported image")
            if content_length and int(content_length) > 100 * 1024 * 1024:
                raise ValueError("ComfyUI output is too large")
            content = response.read(100 * 1024 * 1024 + 1)
        if len(content) > 100 * 1024 * 1024:
            raise ValueError("ComfyUI output is too large")
        try:
            with Image.open(io.BytesIO(content)) as image:
                image.verify()
        except Exception as error:
            raise ValueError("ComfyUI output is not a valid image") from error
        _atomic_bytes_write(destination, content)
        return Path(destination)


def _decode_data_url(value: str) -> bytes:
    if not isinstance(value, str) or not value.startswith("data:image/"):
        raise ValueError("expected an image data URL")
    header, separator, encoded = value.partition(",")
    if separator == "" or ";base64" not in header:
        raise ValueError("expected a base64 image data URL")
    return base64.b64decode(encoded, validate=True)


def _serve_bytes(handler: BaseHTTPRequestHandler, body: bytes, content_type: str) -> None:
    handler.send_response(HTTPStatus.OK)
    handler.send_header("Content-Type", content_type)
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(body)


def _json_response(handler: BaseHTTPRequestHandler, value: Any, status: int = 200) -> None:
    body = json.dumps(_redact(value), ensure_ascii=True).encode()
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(body)


def _safe_session_path(root: Path, relative: str) -> Path:
    root = root.resolve()
    relative_path = Path(relative)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise ValueError("path escapes session")
    raw = root / relative_path
    try:
        raw.relative_to(root)
    except ValueError as error:
        raise ValueError("path escapes session") from error
    current = root
    for component in raw.relative_to(root).parts:
        current = current / component
        if current.is_symlink():
            raise ValueError("path contains a symlink")
    return raw


def make_handler(
    *,
    source_path: Path,
    session_dir: Path,
    comfy_url: str,
    allow_paid: bool,
    node_type: str = "GPTImage15Edit_fal",
    template_path: str | Path | None = None,
) -> type[BaseHTTPRequestHandler]:
    html_path = Path(__file__).with_name("mask_workbench.html")
    source_name = source_path.name
    with Image.open(source_path) as source_image:
        source_size = source_image.size
    if node_type not in {"GPTImage15Edit_fal", "GPTImage2Edit_fal", "FluxPro1Fill_fal"}:
        raise ValueError(f"unsupported edit node: {node_type}")
    template = None
    template_mask_transport = "rgb"
    if template_path is not None:
        template_file = Path(template_path).resolve()
        if not template_file.is_file():
            raise FileNotFoundError(template_file)
        template = json.loads(template_file.read_text())
        # Compile once at startup so a mismatched editor document fails before serving.
        template_probe = compile_template_graph(
            template,
            source_file=source_name,
            mask_file="template-mask.png",
            prompt="Template validation",
            output_prefix="mask_workbench/template-validation",
            width=source_size[0],
            height=source_size[1],
            node_type=node_type,
        )
        template_mask_transport = "comfy-alpha" if template_probe["2"]["class_type"] == "LoadImage" else "rgb"
    controller = ComfyController(
        comfy_url,
        session_dir=session_dir,
        allow_paid=allow_paid,
    )

    def prepare_transport_mask(mask_relative: str, mask_id: str) -> tuple[str, Path]:
        mask_local = _safe_session_path(session_dir, mask_relative)
        if template_mask_transport != "comfy-alpha":
            return mask_relative, mask_local
        transport_relative = f"uploads/{mask_id}-comfy-alpha.png"
        transport_local = _safe_session_path(session_dir, transport_relative)
        width, height, logical = read_mask_alpha(mask_local, transport="rgb")
        write_mask_png(
            transport_local,
            width,
            height,
            logical,
            transport="comfy-alpha",
        )
        return transport_relative, transport_local

    class Handler(BaseHTTPRequestHandler):
        server_version = "MaskWorkbench/1"

        def log_message(self, format: str, *args: Any) -> None:
            # Keep request logs useful without echoing query/body data.
            sys.stderr.write(f"mask-workbench: {format % args}\n")

        def do_GET(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            path = parsed.path
            try:
                if path == "/":
                    _serve_bytes(self, html_path.read_bytes(), "text/html; charset=utf-8")
                elif path == "/api/config":
                    _json_response(
                        self,
                        {
                            "schema": SCHEMA,
                            "source": {"file": source_name, "width": source_size[0], "height": source_size[1]},
                            "session_id": session_dir.name,
                            "mask_convention": MASK_CONVENTION,
                            "node_type": node_type,
                            "template": str(Path(template_path).name) if template_path is not None else None,
                            "paid_submission_enabled": allow_paid,
                        },
                    )
                elif path == "/api/source":
                    _serve_bytes(
                        self,
                        source_path.read_bytes(),
                        mimetypes.guess_type(source_path.name)[0] or "image/png",
                    )
                elif path == "/api/session":
                    manifest_path = session_dir / "manifest.json"
                    if not manifest_path.is_file():
                        _json_response(self, None)
                    else:
                        manifest = json.loads(manifest_path.read_text())
                        _json_response(
                            self,
                            {
                                **manifest,
                                "execution_state": load_execution_state(session_dir, manifest),
                            },
                        )
                elif path.startswith("/api/mask/"):
                    mask_id = unquote(path.removeprefix("/api/mask/"))
                    if not _ID_RE.fullmatch(mask_id):
                        raise ValueError("invalid mask id")
                    manifest_path = session_dir / "manifest.json"
                    manifest = json.loads(manifest_path.read_text()) if manifest_path.is_file() else {}
                    match = next((mask for mask in manifest.get("masks", []) if mask.get("id") == mask_id), None)
                    if not match:
                        raise FileNotFoundError(mask_id)
                    mask_path = _safe_session_path(session_dir, match["file"])
                    _serve_bytes(self, mask_path.read_bytes(), "image/png")
                elif path.startswith("/api/candidate/"):
                    prompt_id = unquote(path.removeprefix("/api/candidate/"))
                    if not re.fullmatch(r"[A-Za-z0-9-]{8,128}", prompt_id):
                        raise ValueError("invalid prompt id")
                    manifest_path = session_dir / "manifest.json"
                    if not manifest_path.is_file():
                        raise FileNotFoundError(prompt_id)
                    manifest = validate_manifest(
                        json.loads(manifest_path.read_text()),
                        image_size=source_size,
                    )
                    execution = load_execution_state(session_dir, manifest)
                    records = list(execution.get("accepted", []))
                    if isinstance(execution.get("pending"), dict):
                        records.append(execution["pending"])
                    record = next((item for item in records if item.get("prompt_id") == prompt_id), None)
                    if not record:
                        raise FileNotFoundError(prompt_id)
                    candidate_path = _safe_session_path(session_dir, record["file"])
                    _serve_bytes(self, candidate_path.read_bytes(), "image/png")
                elif path == "/api/comfy/health":
                    _json_response(self, controller.health())
                elif path == "/api/comfy/queue":
                    _json_response(self, controller.queue())
                elif path.startswith("/api/comfy/history/"):
                    _json_response(self, controller.history(unquote(path.rsplit("/", 1)[-1])))
                else:
                    self.send_error(HTTPStatus.NOT_FOUND)
            except FileNotFoundError:
                self.send_error(HTTPStatus.NOT_FOUND)
            except (ValueError, ManifestError) as error:
                _json_response(self, {"error": str(error)}, HTTPStatus.BAD_REQUEST)
            except Exception as error:
                _json_response(self, {"error": type(error).__name__}, HTTPStatus.BAD_GATEWAY)

        def do_POST(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length <= 0 or length > 60 * 1024 * 1024:
                    raise ValueError("request body is missing or too large")
                body = json.loads(self.rfile.read(length))
                if parsed.path == "/api/session":
                    self._save_session(body)
                elif parsed.path == "/api/compile":
                    self._compile_session(body)
                elif parsed.path == "/api/comfy/submit":
                    self._submit(body)
                elif parsed.path == "/api/comfy/watch":
                    self._watch(body)
                elif parsed.path == "/api/comfy/accept":
                    self._accept(body)
                elif parsed.path == "/api/comfy/reject":
                    self._reject(body)
                else:
                    self.send_error(HTTPStatus.NOT_FOUND)
            except json.JSONDecodeError:
                _json_response(self, {"error": "invalid JSON"}, HTTPStatus.BAD_REQUEST)
            except PermissionError as error:
                _json_response(self, {"error": str(error)}, HTTPStatus.FORBIDDEN)
            except (ValueError, ManifestError, FileNotFoundError) as error:
                _json_response(self, {"error": str(error)}, HTTPStatus.BAD_REQUEST)
            except DuplicateJobError as error:
                _json_response(self, {"error": str(error)}, HTTPStatus.CONFLICT)
            except Exception as error:
                _json_response(self, {"error": type(error).__name__}, HTTPStatus.BAD_GATEWAY)

        def _save_session(self, body: Any) -> None:
            with _exclusive_file_lock(session_dir / "session.lock"):
                self._save_session_locked(body)

        def _save_session_locked(self, body: Any) -> None:
            if not isinstance(body, dict) or not isinstance(body.get("manifest"), dict):
                raise ValueError("manifest object is required")
            manifest = validate_manifest(body["manifest"], image_size=source_size)
            manifest["source"]["file"] = source_name
            previous_manifest = None
            previous_state = None
            previous_manifest_path = session_dir / "manifest.json"
            if previous_manifest_path.is_file():
                previous_manifest = json.loads(previous_manifest_path.read_text())
                if not isinstance(previous_manifest, dict):
                    raise RuntimeError("saved manifest is invalid; refusing to overwrite it")
                previous_state = load_execution_state(session_dir, previous_manifest)
            masks_payload = body.get("masks", {})
            if not isinstance(masks_payload, dict):
                raise ValueError("masks must be an object of data URLs")
            masks_dir = session_dir / "masks"
            masks_dir.mkdir(parents=True, exist_ok=True)
            overlay_bytes = None
            overlay = body.get("overlay")
            if isinstance(overlay, str):
                overlay_bytes = _decode_data_url(overlay)
                with Image.open(io.BytesIO(overlay_bytes)) as overlay_image:
                    if overlay_image.size != source_size:
                        raise ValueError("overlay does not match source size")
            logical_masks: list[bytes] = []
            pending_masks: list[tuple[dict[str, Any], bytes, Path]] = []
            for mask in manifest["masks"]:
                data_url = masks_payload.get(mask["id"])
                if not isinstance(data_url, str):
                    raise ValueError(f"missing image for mask {mask['id']}")
                raw = _decode_data_url(data_url)
                with Image.open(io.BytesIO(raw)) as image:
                    image = image.convert("RGBA")
                    if image.size != source_size:
                        raise ValueError(f"mask {mask['id']} does not match source size")
                    logical_values = bytearray()
                    for y in range(image.height):
                        for x in range(image.width):
                            red, green, blue, _ = image.getpixel((x, y))
                            if red != green or red != blue:
                                raise ValueError(f"mask {mask['id']} must be grayscale")
                            logical_values.append(red)
                    logical = bytes(logical_values)
                actual_bounds = _alpha_bounds(logical, source_size[0], source_size[1])
                if actual_bounds is None:
                    raise ValueError(f"mask {mask['id']} is empty")
                if actual_bounds != mask["bounds"]:
                    raise ValueError(f"mask {mask['id']} bounds do not match its pixels")
                logical_masks.append(logical)
                mask["sha256"] = mask_png_sha256(source_size[0], source_size[1], logical)
                mask["pixel_count"] = sum(value > 0 for value in logical)
                pending_masks.append((mask, logical, _safe_session_path(session_dir, mask["file"])))
            if manifest["overlap_policy"] == "reject":
                occupied = bytearray(source_size[0] * source_size[1])
                for mask, logical, _ in pending_masks:
                    if any(value and occupied[index] for index, value in enumerate(logical)):
                        raise ValueError(f"mask {mask['id']} overlaps another mask")
                    for index, value in enumerate(logical):
                        if value:
                            occupied[index] = 1
            union_pixels = union_alpha(logical_masks) if manifest["mode"] == "union" else None
            if union_pixels is not None:
                manifest["union_file"] = "masks/union.png"
                manifest["union_sha256"] = mask_png_sha256(
                    source_size[0], source_size[1], union_pixels
                )
            manifest["source"]["sha256"] = sha256_file(source_path)
            if (
                previous_manifest is not None
                and isinstance(previous_state, dict)
                and previous_state.get("pending") is not None
                and manifest_identity(previous_manifest) != manifest_identity(manifest)
            ):
                raise ValueError("accept or reject the pending candidate before changing annotations")
            for mask, logical, output_path in pending_masks:
                write_mask_png(output_path, source_size[0], source_size[1], logical)
            if union_pixels is not None:
                write_mask_png(
                    _safe_session_path(session_dir, "masks/union.png"),
                    source_size[0],
                    source_size[1],
                    union_pixels,
                )
            source_copy = _safe_session_path(session_dir, source_name)
            if source_copy != source_path:
                _atomic_bytes_write(source_copy, source_path.read_bytes())
            manifest_path = session_dir / "manifest.json"
            _atomic_json_write(manifest_path, manifest)
            execution = execution_state_for_manifest(
                manifest,
                previous_state,
                previous_manifest=previous_manifest,
            )
            save_execution_state(session_dir, execution)
            if overlay_bytes is not None:
                with Image.open(io.BytesIO(overlay_bytes)) as overlay_image:
                    overlay_buffer = io.BytesIO()
                    overlay_image.convert("RGBA").save(
                        overlay_buffer,
                        format="PNG",
                        optimize=False,
                    )
                _atomic_bytes_write(session_dir / "overlay.png", overlay_buffer.getvalue())
            _json_response(
                self,
                {"saved": True, "manifest": manifest, "execution": execution},
            )

        def _compile_session(self, body: Any) -> None:
            with _exclusive_file_lock(session_dir / "session.lock"):
                self._compile_session_locked(body)

        def _compile_session_locked(self, body: Any) -> None:
            manifest_path = session_dir / "manifest.json"
            if not manifest_path.is_file():
                raise FileNotFoundError("save a session before compiling")
            manifest = validate_manifest(
                json.loads(manifest_path.read_text()),
                image_size=source_size,
                base_dir=session_dir,
                require_files=True,
            )
            mask_files = {mask["id"]: mask["file"] for mask in manifest["masks"]}
            execution = load_execution_state(session_dir, manifest)
            checkpoint_sources: dict[str, str] = {}
            try:
                current_id = next_mask_id(manifest, execution)
            except ValueError:
                current_id = None
            if current_id and execution.get("current_source") != source_name:
                checkpoint_sources[current_id] = execution["current_source"]
            jobs = (
                compile_jobs(
                    manifest,
                    source_file=source_name,
                    mask_files=mask_files,
                    checkpoint_sources=checkpoint_sources,
                    union_mask_file=manifest.get("union_file"),
                    node_type=node_type,
                )
                if current_id
                else []
            )
            graph_dir = session_dir / "graphs"
            graph_dir.mkdir(exist_ok=True)
            for job in jobs:
                if job["graph"] is not None:
                    if template is not None:
                        transport_mask, _ = prepare_transport_mask(
                            job["mask_file"],
                            job["mask_id"],
                        )
                        job["transport_mask_file"] = transport_mask
                        job["graph"] = compile_template_graph(
                            template,
                            source_file=job["source_file"],
                            mask_file=transport_mask,
                            prompt=job["prompt"],
                            output_prefix=f"mask_workbench/{manifest['session_id']}/{job['mask_id']}",
                            width=source_size[0],
                            height=source_size[1],
                            node_type=node_type,
                        )
                    _atomic_json_write(
                        graph_dir / f"{job['job_id']}.json",
                        {"prompt": job["graph"], "client_id": controller.client_id},
                    )
            report = {
                "manifest": manifest,
                "execution": execution,
                "jobs": jobs,
                "paid": any(
                    job["graph"] and controller.is_paid_graph(job["graph"])
                    for job in jobs
                ),
            }
            _atomic_json_write(session_dir / "dry-run.json", report)
            _json_response(self, {"valid": True, "report": report})

        def _submit(self, body: Any) -> None:
            with _exclusive_file_lock(session_dir / "session.lock"):
                self._submit_locked(body)

        def _submit_locked(self, body: Any) -> None:
            if not allow_paid:
                raise PermissionError("paid submission is disabled for this server")
            if not isinstance(body, dict) or body.get("confirmation") != PAID_CONFIRMATION:
                raise PermissionError(f"type {PAID_CONFIRMATION} to submit")
            requested_id = body.get("mask_id")
            if not isinstance(requested_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", requested_id):
                raise ValueError("mask_id is required")
            manifest = validate_manifest(
                json.loads((session_dir / "manifest.json").read_text()),
                image_size=source_size,
                base_dir=session_dir,
                require_files=True,
            )
            execution = load_execution_state(session_dir, manifest)
            if execution.get("pending") is not None:
                raise ValueError("review or reject the pending candidate before submitting")
            expected_id = next_mask_id(manifest, execution)
            if expected_id is None:
                raise ValueError("all masks have already been accepted")
            if requested_id != expected_id:
                raise ValueError(f"masks must be submitted in order; expected {expected_id}")
            if not provider_preserves_aspect(node_type, source_size[0], source_size[1]):
                raise ValueError(
                    "GPTImage15Edit_fal cannot preserve this source aspect ratio; use GPTImage2Edit_fal"
                )
            mask_files = {mask["id"]: mask["file"] for mask in manifest["masks"]}
            mask_relative = manifest.get("union_file") if requested_id == "union" else mask_files.get(requested_id)
            source_relative = execution.get("current_source")
            if not isinstance(mask_relative, str) or not isinstance(source_relative, str):
                raise ValueError("selected job has no local source or mask")
            source_local = _safe_session_path(session_dir, source_relative)
            mask_local = _safe_session_path(session_dir, mask_relative)
            if not source_local.is_file() or not mask_local.is_file():
                raise FileNotFoundError("selected source or mask file is missing")
            source_upload = controller.upload_image(source_local, filename=Path(source_relative).name)
            transport_mask_relative, upload_mask_local = prepare_transport_mask(
                mask_relative,
                requested_id,
            )
            mask_upload = controller.upload_image(
                upload_mask_local,
                filename=upload_mask_local.name,
            )
            source_remote_name = uploaded_name(source_upload)
            mask_remote_name = uploaded_name(mask_upload)
            selected_mask = next(
                (mask for mask in manifest["masks"] if mask["id"] == requested_id),
                None,
            )
            comment = (
                manifest["masks"][0]["comment"]
                if requested_id == "union"
                else selected_mask["comment"] if selected_mask else None
            )
            if not isinstance(comment, str):
                raise ValueError("selected mask comment is missing")
            job_id = f"{manifest['session_id']}-{execution['next_index'] + 1:02d}-{requested_id}"
            graph_args = {
                "source_file": source_remote_name,
                "mask_file": mask_remote_name,
                "prompt": build_prompt(requested_id, comment),
                "output_prefix": f"mask_workbench/{manifest['session_id']}/{requested_id}",
                "width": source_size[0],
                "height": source_size[1],
                "node_type": node_type,
            }
            graph = (
                compile_template_graph(template, **graph_args)
                if template is not None
                else compile_graph(**graph_args)
            )
            controller.preflight_graph(
                graph,
                uploaded_files={source_remote_name, mask_remote_name},
            )
            source_hash = sha256_file(source_local)
            mask_hash = sha256_file(mask_local)
            transport_mask_hash = sha256_file(upload_mask_local)
            graph_hash = hashlib.sha256(
                json.dumps(graph, sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest()
            submission_hash = stable_submission_fingerprint(graph)
            result = controller.submit(
                graph,
                confirmation=PAID_CONFIRMATION,
                job_key=f"{job_id}:{source_hash}:{mask_hash}:{submission_hash}",
                preflighted=True,
            )
            prompt_id = result["prompt_id"]
            candidate_file = f"candidates/{execution['next_index'] + 1:02d}-{requested_id}-{prompt_id}.png"
            updated_execution = mark_candidate(
                manifest,
                execution,
                mask_id=requested_id,
                prompt_id=prompt_id,
                file=candidate_file,
            )
            submit_record = {
                "job": job_id,
                "prompt_id": prompt_id,
                "source": source_relative,
                "source_sha256": source_hash,
                "mask": mask_relative,
                "mask_sha256": mask_hash,
                "transport_mask": transport_mask_relative,
                "transport_mask_sha256": transport_mask_hash,
                "graph_sha256": graph_hash,
                "submission_fingerprint": submission_hash,
                "mask_transport": template_mask_transport,
                "source_upload": source_upload,
                "mask_upload": mask_upload,
                "graph": graph,
                "response": result,
            }
            receipt_path = session_dir / f"submit-{requested_id}-{prompt_id}.json"
            try:
                _atomic_json_write(receipt_path, submit_record)
                save_execution_state(session_dir, updated_execution)
            except Exception as error:
                recovery_path = session_dir / f"reconcile-{prompt_id}.json"
                try:
                    _atomic_json_write(
                        recovery_path,
                        submission_recovery_record(
                            submit_record,
                            updated_execution,
                            receipt_name=receipt_path.name,
                        ),
                    )
                except OSError:
                    pass
                raise RuntimeError(
                    "prompt was accepted but session state could not be persisted; reconcile before retrying"
                ) from error
            execution = updated_execution
            _json_response(
                self,
                {"submitted": True, "job": job_id, "response": result, "execution": execution},
            )

        def _watch(self, body: Any) -> None:
            with _exclusive_file_lock(session_dir / "session.lock"):
                self._watch_locked(body)

        def _watch_locked(self, body: Any) -> None:
            if not isinstance(body, dict) or not isinstance(body.get("prompt_id"), str):
                raise ValueError("prompt_id is required")
            prompt_id = body["prompt_id"]
            manifest_path = session_dir / "manifest.json"
            manifest = validate_manifest(
                json.loads(manifest_path.read_text()),
                image_size=source_size,
                base_dir=session_dir,
                require_files=True,
            )
            execution = load_execution_state(session_dir, manifest)
            pending = execution.get("pending")
            if not isinstance(pending, dict) or pending.get("prompt_id") != prompt_id:
                raise ValueError("prompt is not the pending session job")
            cached_path = session_dir / f"watch-{prompt_id}.json"
            if cached_path.is_file():
                try:
                    cached = json.loads(cached_path.read_text())
                except (OSError, json.JSONDecodeError, TypeError):
                    cached = None
                if isinstance(cached, dict):
                    candidate_ready = isinstance(cached.get("candidate"), dict) and (
                        _safe_session_path(session_dir, pending["file"]).is_file()
                    )
                    if cached.get("status") == "failed" or (cached.get("success") and candidate_ready):
                        if cached.get("status") == "failed":
                            controller.mark_terminal_failure(prompt_id, cached)
                        _json_response(self, cached)
                        return
            result = controller.watch(prompt_id)
            if result.get("success"):
                reference = extract_output_reference(result.get("history", {}), prompt_id)
                raw_file = _safe_session_path(
                    session_dir,
                    pending["file"].replace(".png", "-raw.png"),
                )
                normalized_file = _safe_session_path(
                    session_dir,
                    pending["file"].replace(".png", "-normalized.png"),
                )
                candidate_file = _safe_session_path(session_dir, pending["file"])
                controller.download_output(reference, raw_file)
                dimensions = normalize_checkpoint(
                    raw_file,
                    normalized_file,
                    source_size,
                )
                source_file = _safe_session_path(session_dir, execution["current_source"])
                mask_relative = (
                    manifest.get("union_file")
                    if pending["mask_id"] == "union"
                    else next(
                        mask["file"]
                        for mask in manifest["masks"]
                        if mask["id"] == pending["mask_id"]
                    )
                )
                protection = composite_checkpoint(
                    source_file,
                    normalized_file,
                    _safe_session_path(session_dir, mask_relative),
                    candidate_file,
                    source_size,
                )
                result["candidate"] = {
                    "file": pending["file"],
                    "url": f"/api/candidate/{quote(prompt_id, safe='')}",
                    "dimensions": dimensions,
                    "reference": reference,
                    "protection": protection,
                }
            else:
                result["candidate"] = None
            if result.get("status") == "failed":
                controller.mark_terminal_failure(prompt_id, result)
            if result.get("success") or result.get("status") == "failed":
                _atomic_json_write(cached_path, result)
            _json_response(self, result)

        def _accept(self, body: Any) -> None:
            with _exclusive_file_lock(session_dir / "session.lock"):
                self._accept_locked(body)

        def _accept_locked(self, body: Any) -> None:
            if not isinstance(body, dict) or not isinstance(body.get("prompt_id"), str):
                raise ValueError("prompt_id is required")
            prompt_id = body["prompt_id"]
            manifest = validate_manifest(json.loads((session_dir / "manifest.json").read_text()), image_size=source_size)
            execution = load_execution_state(session_dir, manifest)
            pending = execution.get("pending")
            if not isinstance(pending, dict) or pending.get("prompt_id") != prompt_id:
                raise ValueError("no matching pending candidate")
            candidate_path = _safe_session_path(session_dir, pending["file"])
            if not candidate_path.is_file():
                raise FileNotFoundError("candidate image is not ready")
            candidate_hash = sha256_file(candidate_path)
            with Image.open(candidate_path) as candidate_image:
                candidate_dimensions = candidate_image.size
                candidate_image.verify()
            if candidate_dimensions != source_size:
                raise ValueError("candidate image does not match the source canvas")
            mask_relative = (
                manifest.get("union_file")
                if pending["mask_id"] == "union"
                else next(
                    mask["file"]
                    for mask in manifest["masks"]
                    if mask["id"] == pending["mask_id"]
                )
            )
            protection = protected_pixel_diff(
                _safe_session_path(session_dir, execution["current_source"]),
                candidate_path,
                _safe_session_path(session_dir, mask_relative),
                source_size,
            )
            if protection["outside_changed_pixels"]:
                raise ValueError("candidate changes protected pixels")
            updated = accept_candidate(
                execution,
                prompt_id=prompt_id,
                candidate_sha256=candidate_hash,
                dimensions=candidate_dimensions,
            )
            receipt = {
                "prompt_id": prompt_id,
                "mask_id": pending["mask_id"],
                "candidate": pending["file"],
                "candidate_sha256": candidate_hash,
                "dimensions": list(candidate_dimensions),
                "protection": protection,
                "approved": True,
                "approved_at": time.time(),
            }
            try:
                _atomic_json_write(session_dir / f"accept-{prompt_id}.json", receipt)
                save_execution_state(session_dir, updated)
            except Exception as error:
                try:
                    _atomic_json_write(
                        session_dir / f"reconcile-accept-{prompt_id}.json",
                        {"prompt_id": prompt_id, "receipt": f"accept-{prompt_id}.json", "reason": "checkpoint decision persistence failed"},
                    )
                except OSError:
                    pass
                raise RuntimeError("checkpoint decision could not be persisted; reconcile before retrying") from error
            _json_response(self, {"accepted": True, "execution": updated})

        def _reject(self, body: Any) -> None:
            with _exclusive_file_lock(session_dir / "session.lock"):
                self._reject_locked(body)

        def _reject_locked(self, body: Any) -> None:
            if not isinstance(body, dict) or not isinstance(body.get("prompt_id"), str):
                raise ValueError("prompt_id is required")
            prompt_id = body["prompt_id"]
            manifest = validate_manifest(json.loads((session_dir / "manifest.json").read_text()), image_size=source_size)
            execution = load_execution_state(session_dir, manifest)
            updated = reject_candidate(execution, prompt_id=prompt_id)
            receipt = {"prompt_id": prompt_id, "rejected": True, "at": time.time()}
            try:
                _atomic_json_write(session_dir / f"reject-{prompt_id}.json", receipt)
                save_execution_state(session_dir, updated)
            except Exception as error:
                try:
                    _atomic_json_write(
                        session_dir / f"reconcile-reject-{prompt_id}.json",
                        {"prompt_id": prompt_id, "receipt": f"reject-{prompt_id}.json", "reason": "checkpoint decision persistence failed"},
                    )
                except OSError:
                    pass
                raise RuntimeError("checkpoint decision could not be persisted; reconcile before retrying") from error
            _json_response(self, {"rejected": True, "execution": updated})

    return Handler


def serve(
    image: str | Path,
    *,
    session_dir: str | Path,
    host: str = "127.0.0.1",
    port: int = 8765,
    comfy_url: str = "http://127.0.0.1:8191",
    allow_paid: bool = False,
    node_type: str = "GPTImage15Edit_fal",
    template_path: str | Path | None = None,
) -> None:
    if host not in {"127.0.0.1", "localhost", "::1"}:
        raise ValueError("mask workbench must bind to loopback")
    source = Path(image).resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    session = Path(session_dir).resolve()
    session.mkdir(parents=True, exist_ok=True)
    handler = make_handler(
        source_path=source,
        session_dir=session,
        comfy_url=comfy_url,
        allow_paid=allow_paid,
        node_type=node_type,
        template_path=template_path,
    )
    server = ThreadingHTTPServer((host, port), handler)
    print(f"mask-workbench={server.server_address[0]}:{server.server_address[1]}")
    print(f"session={session}")
    print("paid-submission=enabled" if allow_paid else "paid-submission=disabled")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def _load_manifest(path: str | Path) -> dict[str, Any]:
    return validate_manifest(json.loads(Path(path).read_text()))


def _command_validate(args: argparse.Namespace) -> None:
    manifest = validate_manifest(json.loads(Path(args.manifest).read_text()))
    if args.base_dir:
        manifest = validate_manifest(manifest, base_dir=args.base_dir, require_files=True)
    print(json.dumps({"valid": True, "manifest": manifest}, ensure_ascii=False, indent=2))


def _command_compile(args: argparse.Namespace) -> None:
    manifest = _load_manifest(args.manifest)
    base_dir = Path(args.base_dir or Path(args.manifest).parent).resolve()
    manifest = validate_manifest(manifest, base_dir=base_dir, require_files=True)
    source_file = manifest["source"].get("file")
    if not source_file:
        raise SystemExit("manifest source.file is required")
    mask_files = {mask["id"]: mask["file"] for mask in manifest["masks"]}
    jobs = compile_jobs(
        manifest,
        source_file=source_file,
        mask_files=mask_files,
        union_mask_file=manifest.get("union_file"),
        node_type=args.node,
    )
    if args.template:
        template = json.loads(Path(args.template).read_text())
        probe = compile_template_graph(
            template,
            source_file=source_file,
            mask_file="template-mask.png",
            prompt="Template validation",
            output_prefix="mask_workbench/template-validation",
            width=manifest["source"]["width"],
            height=manifest["source"]["height"],
            node_type=args.node,
        )
        template_transport = "comfy-alpha" if probe["2"]["class_type"] == "LoadImage" else "rgb"
        for job in jobs:
            if job["graph"] is not None:
                mask_file = job["mask_file"]
                if template_transport == "comfy-alpha":
                    if not isinstance(mask_file, str):
                        raise ValueError("template job has no mask file")
                    mask_width, mask_height, logical = read_mask_alpha(
                        base_dir / mask_file,
                        transport="rgb",
                    )
                    transport_file = f"uploads/{job['mask_id']}-comfy-alpha.png"
                    write_mask_png(
                        base_dir / transport_file,
                        mask_width,
                        mask_height,
                        logical,
                        transport="comfy-alpha",
                    )
                    mask_file = transport_file
                job["transport_mask_file"] = mask_file
                job["graph"] = compile_template_graph(
                    template,
                    source_file=job["source_file"],
                    mask_file=mask_file,
                    prompt=job["prompt"],
                    output_prefix=f"mask_workbench/{manifest['session_id']}/{job['mask_id']}",
                    width=manifest["source"]["width"],
                    height=manifest["source"]["height"],
                    node_type=args.node,
                )
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    _atomic_json_write(output, {"manifest": manifest, "jobs": jobs})
    print(f"saved={output}")


def _command_serve(args: argparse.Namespace) -> None:
    serve(
        args.image,
        session_dir=args.session_dir,
        host=args.host,
        port=args.port,
        comfy_url=args.comfy_url,
        allow_paid=args.allow_paid,
        node_type=args.node,
        template_path=args.template,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Draw named masks and compile guarded ComfyUI repairs")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("--manifest", required=True)
    validate_parser.add_argument("--base-dir")
    validate_parser.set_defaults(func=_command_validate)

    compile_parser = subparsers.add_parser("compile")
    compile_parser.add_argument("--manifest", required=True)
    compile_parser.add_argument("--base-dir")
    compile_parser.add_argument(
        "--node",
        default="GPTImage15Edit_fal",
        choices=["GPTImage15Edit_fal", "GPTImage2Edit_fal", "FluxPro1Fill_fal"],
    )
    compile_parser.add_argument("--template")
    compile_parser.add_argument("--output", required=True)
    compile_parser.set_defaults(func=_command_compile)

    serve_parser = subparsers.add_parser("serve")
    serve_parser.add_argument("--image", required=True)
    serve_parser.add_argument("--session-dir", required=True)
    serve_parser.add_argument("--host", default="127.0.0.1")
    serve_parser.add_argument("--port", type=int, default=8765)
    serve_parser.add_argument("--comfy-url", default="http://127.0.0.1:8191")
    serve_parser.add_argument("--allow-paid", action="store_true")
    serve_parser.add_argument("--template")
    serve_parser.add_argument(
        "--node",
        default="GPTImage15Edit_fal",
        choices=["GPTImage15Edit_fal", "GPTImage2Edit_fal", "FluxPro1Fill_fal"],
    )
    serve_parser.set_defaults(func=_command_serve)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
