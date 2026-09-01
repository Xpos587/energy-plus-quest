import base64
import io
import json
import multiprocessing
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest
from PIL import Image

import mask_workbench as workbench
from mask_workbench import (
    ComfyController,
    DuplicateJobError,
    ManifestError,
    accept_candidate,
    canvas_point,
    compile_graph,
    compile_jobs,
    composite_checkpoint,
    compile_template_graph,
    encode_comfy_alpha,
    encode_mask_rgb,
    execution_state_for_manifest,
    extract_output_reference,
    initial_execution_state,
    load_execution_state,
    manifest_identity,
    make_handler,
    mark_candidate,
    next_mask_id,
    normalize_checkpoint,
    protected_pixel_diff,
    provider_preserves_aspect,
    read_mask_alpha,
    reject_candidate,
    stable_submission_fingerprint,
    _safe_output_reference,
    _safe_session_path,
    union_alpha,
    validate_graph,
    validate_graph_schemas,
    validate_manifest,
    uploaded_name,
    write_mask_png,
)


def _post_json(base_url: str, path: str, payload: dict) -> dict:
    request = Request(
        base_url + path,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    return json.loads(urlopen(request).read())


def _png_bytes(width: int, height: int, values: bytes) -> bytes:
    output = io.BytesIO()
    Image.frombytes("L", (width, height), bytes(values)).save(output, "PNG")
    return output.getvalue()


def _post_json_allow_error(base_url: str, path: str, payload: dict) -> tuple[int, dict]:
    request = Request(
        base_url + path,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        response = urlopen(request)
        return response.status, json.loads(response.read())
    except HTTPError as error:
        return error.code, json.loads(error.read())


def _capture_submit(controller: ComfyController, graph: dict) -> object:
    try:
        return controller.submit(graph, confirmation="SUBMIT_PAID")
    except Exception as error:
        return error


def _process_submit(session_dir: str, base_url: str, start, results) -> None:
    controller = ComfyController(base_url, session_dir=session_dir, allow_paid=True)
    controller._open_websocket = lambda: None
    graph = compile_graph(
        source_file="source.png", mask_file="road.png", prompt="Repair road",
        output_prefix="repair/road", width=768, height=1424,
    )
    start.wait(5)
    if not start.is_set():
        result = RuntimeError("start timeout")
    else:
        try:
            result = controller.submit(
                graph,
                confirmation="SUBMIT_PAID",
                preflighted=True,
            )
        except Exception as error:
            result = error
    results.put(type(result).__name__)


def sample_manifest() -> dict:
    return {
        "schema": "carrier-mask-workbench/v1",
        "session_id": "road-repair-01",
        "source": {
            "file": "source.png",
            "width": 768,
            "height": 1424,
        },
        "mask_convention": "white=edit,black=preserve",
        "mode": "sequential",
        "overlap_policy": "allow",
        "masks": [
            {
                "id": "road-main",
                "name": "Road behind warehouse",
                "comment": "Repair the road behind the warehouse and keep the gate unchanged.",
                "color": "#f97316",
                "visible": True,
                "file": "masks/road-main.png",
                "bounds": [120, 780, 650, 1080],
            },
            {
                "id": "gate-edge",
                "name": "Gate edge",
                "comment": "Keep the attached barrier and loading gate crisp.",
                "color": "#38bdf8",
                "visible": True,
                "file": "masks/gate-edge.png",
                "bounds": [500, 560, 740, 820],
            },
        ],
    }


def test_canvas_point_maps_css_coordinates_to_intrinsic_pixels() -> None:
    assert canvas_point(
        client_x=160,
        client_y=298,
        rect=(10, 20, 300, 556),
        canvas_size=(768, 1424),
    ) == (384, 712)


def test_union_alpha_keeps_the_strongest_edit_value_per_pixel() -> None:
    assert union_alpha([bytes([0, 20, 255]), bytes([40, 10, 100])]) == bytes([40, 20, 255])


def test_mask_rgb_uses_white_for_edit_and_black_for_preserve() -> None:
    encoded = encode_mask_rgb(bytes([0, 127, 255]))
    assert encoded == bytes(
        [0, 0, 0, 127, 127, 127, 255, 255, 255]
    )


def test_comfy_alpha_transport_inverts_native_load_image_alpha() -> None:
    encoded = encode_comfy_alpha(bytes([0, 127, 255]))
    assert encoded == bytes(
        [
            255,
            255,
            255,
            255,
            255,
            255,
            255,
            128,
            255,
            255,
            255,
            0,
        ]
    )


def test_manifest_round_trips_multiple_named_comments_and_canvas_size() -> None:
    manifest = validate_manifest(sample_manifest())
    assert manifest["source"]["width"] == 768
    assert manifest["source"]["height"] == 1424
    assert [mask["id"] for mask in manifest["masks"]] == [
        "road-main",
        "gate-edge",
    ]
    assert manifest["masks"][0]["comment"].startswith("Repair the road")


def test_manifest_rejects_union_with_different_comments() -> None:
    payload = sample_manifest()
    payload["mode"] = "union"
    with pytest.raises(ManifestError, match="same comment"):
        validate_manifest(payload)


def test_union_job_uses_the_compiled_union_mask() -> None:
    payload = sample_manifest()
    payload["mode"] = "union"
    payload["masks"][1]["comment"] = payload["masks"][0]["comment"]
    manifest = validate_manifest(payload)
    jobs = compile_jobs(
        manifest,
        source_file="source.png",
        mask_files={"road-main": "masks/road-main.png", "gate-edge": "masks/gate-edge.png"},
        union_mask_file="masks/union.png",
    )
    assert jobs[0]["mask_id"] == "union"
    assert jobs[0]["mask_file"] == "masks/union.png"
    assert jobs[0]["graph"]["2"]["inputs"]["image"] == "masks/union.png"


def test_union_manifest_accepts_one_shared_instruction() -> None:
    payload = sample_manifest()
    payload["mode"] = "union"
    payload["masks"][1]["comment"] = payload["masks"][0]["comment"]
    assert validate_manifest(payload)["mode"] == "union"


def test_union_file_must_equal_member_mask_union(tmp_path) -> None:
    payload = {
        "schema": "carrier-mask-workbench/v1",
        "session_id": "union-check",
        "source": {"file": "source.png", "width": 4, "height": 4},
        "mask_convention": "white=edit,black=preserve",
        "mode": "union",
        "overlap_policy": "allow",
        "union_file": "masks/union.png",
        "masks": [
            {"id": "one", "name": "One", "comment": "Repair road", "color": "#f97316", "visible": True, "file": "masks/one.png", "bounds": [0, 0, 1, 1]},
            {"id": "two", "name": "Two", "comment": "Repair road", "color": "#38bdf8", "visible": True, "file": "masks/two.png", "bounds": [3, 3, 4, 4]},
        ],
    }
    Image.new("RGB", (4, 4), (0, 0, 0)).save(tmp_path / "source.png")
    first = bytearray(16)
    first[0] = 255
    second = bytearray(16)
    second[-1] = 255
    write_mask_png(tmp_path / "masks/one.png", 4, 4, bytes(first))
    write_mask_png(tmp_path / "masks/two.png", 4, 4, bytes(second))
    write_mask_png(tmp_path / "masks/union.png", 4, 4, bytes(first))
    with pytest.raises(ManifestError, match="union mask does not match"):
        validate_manifest(payload, base_dir=tmp_path, require_files=True)


def test_manifest_requires_source_file_when_file_checks_are_enabled(tmp_path) -> None:
    payload = sample_manifest()
    for mask in payload["masks"]:
        write_mask_png(tmp_path / mask["file"], 768, 1424, bytes(768 * 1424))
    with pytest.raises(ManifestError, match="source file"):
        validate_manifest(payload, base_dir=tmp_path, require_files=True)


def test_manifest_rejects_session_id_path_traversal() -> None:
    payload = sample_manifest()
    payload["session_id"] = "../outside"
    with pytest.raises(ManifestError, match="session_id"):
        validate_manifest(payload)


def test_manifest_rejects_empty_mask_file_when_file_checks_are_enabled(tmp_path) -> None:
    payload = sample_manifest()
    source = tmp_path / "source.png"
    Image.new("RGB", (768, 1424), (0, 0, 0)).save(source)
    for mask in payload["masks"]:
        write_mask_png(tmp_path / mask["file"], 768, 1424, bytes(768 * 1424))
    payload["source"]["file"] = "source.png"
    with pytest.raises(ManifestError, match="empty"):
        validate_manifest(payload, base_dir=tmp_path, require_files=True)


def test_manifest_rejects_declared_source_hash_mismatch(tmp_path) -> None:
    payload = sample_manifest()
    source = tmp_path / "source.png"
    Image.new("RGB", (768, 1424), (0, 0, 0)).save(source)
    payload["source"]["file"] = "source.png"
    payload["source"]["sha256"] = "0" * 64
    for mask in payload["masks"]:
        write_mask_png(tmp_path / mask["file"], 768, 1424, bytes(768 * 1424))
    with pytest.raises(ManifestError, match="source file hash"):
        validate_manifest(payload, base_dir=tmp_path, require_files=True)


def test_manifest_rejects_declared_mask_hash_mismatch(tmp_path) -> None:
    payload = sample_manifest()
    source = tmp_path / "source.png"
    Image.new("RGB", (768, 1424), (0, 0, 0)).save(source)
    payload["source"]["file"] = "source.png"
    for mask in payload["masks"]:
        alpha = bytearray(768 * 1424)
        left, top, right, bottom = mask["bounds"]
        for y in range(top, bottom):
            alpha[y * 768 + left:y * 768 + right] = b"\xff" * (right - left)
        write_mask_png(tmp_path / mask["file"], 768, 1424, bytes(alpha))
    payload["masks"][0]["sha256"] = "0" * 64
    with pytest.raises(ManifestError, match="hash"):
        validate_manifest(payload, base_dir=tmp_path, require_files=True)


def test_manifest_rejects_mask_pixels_outside_declared_bounds(tmp_path) -> None:
    payload = sample_manifest()
    source = tmp_path / "source.png"
    Image.new("RGB", (768, 1424), (0, 0, 0)).save(source)
    alpha = bytearray(768 * 1424)
    alpha[10 * 768 + 10] = 255
    for mask in payload["masks"]:
        write_mask_png(tmp_path / mask["file"], 768, 1424, bytes(alpha))
    payload["source"]["file"] = "source.png"
    with pytest.raises(ManifestError, match="bounds do not match"):
        validate_manifest(payload, base_dir=tmp_path, require_files=True)


def test_manifest_rejects_mask_outside_canvas() -> None:
    payload = sample_manifest()
    payload["masks"][0]["bounds"] = [700, 1300, 800, 1500]
    with pytest.raises(ManifestError, match="bounds"):
        validate_manifest(payload)


def test_compile_template_replaces_editor_values_with_api_inputs() -> None:
    template = {
        "nodes": [
            {"id": 41, "type": "LoadImage"},
            {"id": 99, "type": "MaskToImage"},
            {"id": 7, "type": "GPTImage15Edit_fal", "widgets_values_named": {"quality": "low"}},
            {"id": 8, "type": "PreviewImage"},
        ],
        "links": [[12, 41, 1, 99, 0, "MASK"]],
    }
    graph = compile_template_graph(
        template,
        source_file="source.png",
        mask_file="mask.png",
        prompt="Repair only",
        output_prefix="repair/test",
        width=768,
        height=1424,
    )
    assert "clipspace-painted-masked" not in json.dumps(graph)
    assert graph["2"]["class_type"] == "LoadImage"
    assert graph["4"]["inputs"]["quality"] == "low"
    assert graph["3"]["inputs"]["mask"] == ["2", 1]


def test_compile_template_rejects_ambiguous_mask_topology() -> None:
    template = {
        "nodes": [
            {"id": 1, "type": "LoadImage"},
            {"id": 2, "type": "LoadImageMask"},
            {"id": 3, "type": "MaskToImage"},
            {"id": 4, "type": "GPTImage15Edit_fal"},
            {"id": 5, "type": "SaveImage"},
        ],
        "links": [
            [1, 1, 1, 3, 0, "MASK"],
            [2, 2, 0, 3, 0, "MASK"],
        ],
    }
    with pytest.raises(ValueError, match="exactly one mask transport"):
        compile_template_graph(
            template,
            source_file="source.png",
            mask_file="mask.png",
            prompt="Repair only",
            output_prefix="repair/test",
            width=768,
            height=1424,
        )


def test_compile_template_rejects_unverifiable_mask_topology() -> None:
    template = {
        "nodes": [
            {"id": 1, "type": "LoadImage"},
            {"id": 2, "type": "MaskToImage"},
            {"id": 3, "type": "GPTImage15Edit_fal"},
            {"id": 4, "type": "SaveImage"},
        ],
        "links": [],
    }
    with pytest.raises(ValueError, match="mask transport"):
        compile_template_graph(
            template,
            source_file="source.png",
            mask_file="mask.png",
            prompt="Repair only",
            output_prefix="repair/test",
            width=768,
            height=1424,
        )


def test_gpt15_aspect_guard_rejects_an_unsupported_source_ratio() -> None:
    assert provider_preserves_aspect("GPTImage15Edit_fal", 1024, 1536)
    assert provider_preserves_aspect("GPTImage15Edit_fal", 1536, 1024)
    assert not provider_preserves_aspect("GPTImage15Edit_fal", 768, 1424)
    assert provider_preserves_aspect("GPTImage2Edit_fal", 768, 1424)


def test_compile_graph_replaces_stale_image_and_keeps_mask_to_image_link() -> None:
    graph = compile_graph(
        source_file="uploaded/source.png",
        mask_file="uploaded/road-main.png",
        prompt="Repair the road only.",
        output_prefix="mask_workbench/road-main",
        width=768,
        height=1424,
    )
    validate_graph(graph)
    assert "clipspace-painted-masked-1788170150011.png" not in json.dumps(graph)
    assert graph["2"]["class_type"] == "LoadImageMask"
    assert graph["3"]["class_type"] == "MaskToImage"
    assert graph["3"]["inputs"]["mask"] == ["2", 0]
    assert graph["4"]["inputs"]["mask_image"] == ["3", 0]
    assert graph["5"]["inputs"]["images"] == ["4", 0]


def test_sequential_execution_advances_only_after_candidate_acceptance() -> None:
    manifest = validate_manifest(sample_manifest())
    state = initial_execution_state(manifest)
    assert next_mask_id(manifest, state) == "road-main"
    state = mark_candidate(
        manifest,
        state,
        mask_id="road-main",
        prompt_id="12345678-1234-1234-1234-123456789012",
        file="candidates/road-main.png",
    )
    with pytest.raises(ValueError, match="pending candidate"):
        next_mask_id(manifest, state)
    state = accept_candidate(
        state,
        prompt_id="12345678-1234-1234-1234-123456789012",
        candidate_sha256="0" * 64,
        dimensions=[768, 1424],
    )
    assert state["current_source"] == "candidates/road-main.png"
    assert next_mask_id(manifest, state) == "gate-edge"


def test_extract_output_reference_selects_a_safe_saved_image() -> None:
    prompt_id = "12345678-1234-1234-1234-123456789012"
    history = {
        prompt_id: {
            "outputs": {
                "5": {"images": [{"filename": "repair.png", "subfolder": "", "type": "output"}]}
            }
        }
    }
    assert extract_output_reference(history, prompt_id)["filename"] == "repair.png"
    history[prompt_id]["outputs"]["5"]["images"][0]["filename"] = "../secret.png"
    with pytest.raises(ValueError, match="unsafe"):
        extract_output_reference(history, prompt_id)


def test_normalize_checkpoint_rejects_aspect_ratio_drift(tmp_path) -> None:
    raw = tmp_path / "raw.png"
    Image.new("RGBA", (1001, 1000), (1, 2, 3, 255)).save(raw)
    with pytest.raises(ValueError, match="aspect ratio"):
        normalize_checkpoint(raw, tmp_path / "checkpoint.png", (1000, 1000))


def test_normalize_checkpoint_records_raw_and_target_dimensions(tmp_path) -> None:
    raw = tmp_path / "raw.png"
    output = tmp_path / "checkpoint.png"
    Image.new("RGBA", (4, 3), (1, 2, 3, 255)).save(raw)
    receipt = normalize_checkpoint(raw, output, (8, 6))
    assert receipt == {"raw_size": [4, 3], "size": [8, 6]}
    assert Image.open(output).size == (8, 6)


def test_checkpoint_composite_preserves_black_mask_pixels(tmp_path) -> None:
    source = tmp_path / "source.png"
    generated = tmp_path / "generated.png"
    mask = tmp_path / "mask.png"
    candidate = tmp_path / "candidate.png"
    Image.new("RGB", (3, 2), (10, 20, 30)).save(source)
    changed = Image.new("RGB", (3, 2), (200, 210, 220))
    changed.save(generated)
    alpha = bytearray(6)
    alpha[4] = 255
    write_mask_png(mask, 3, 2, bytes(alpha))
    protection = composite_checkpoint(source, generated, mask, candidate, (3, 2))
    assert protection["provider_outside_changed_pixels"] == 5
    assert protection["outside_changed_pixels"] == 0
    with Image.open(candidate) as output:
        assert output.getpixel((0, 0)) == (10, 20, 30)
        assert output.getpixel((1, 1)) == (200, 210, 220)
    assert protected_pixel_diff(source, candidate, mask, (3, 2))["outside_changed_pixels"] == 0


def test_execution_state_resets_when_manifest_identity_changes() -> None:
    manifest = validate_manifest(sample_manifest())
    state = initial_execution_state(manifest)
    state["manifest_digest"] = "old"
    refreshed = execution_state_for_manifest(manifest, state)
    assert refreshed["next_index"] == 0
    assert refreshed["pending"] is None


def test_corrupt_execution_state_fails_closed(tmp_path) -> None:
    manifest = validate_manifest(sample_manifest())
    (tmp_path / "execution.json").write_text("not-json")
    with pytest.raises(RuntimeError, match="execution state"):
        load_execution_state(tmp_path, manifest)


def test_mismatched_execution_state_fails_closed(tmp_path) -> None:
    manifest = validate_manifest(sample_manifest())
    state = initial_execution_state(manifest)
    state["manifest_digest"] = "0" * 64
    (tmp_path / "execution.json").write_text(json.dumps(state))
    with pytest.raises(RuntimeError, match="does not match"):
        load_execution_state(tmp_path, manifest)


def test_invalid_pending_execution_state_fails_closed(tmp_path) -> None:
    manifest = validate_manifest(sample_manifest())
    state = initial_execution_state(manifest)
    state["manifest_digest"] = manifest_identity(manifest)
    state["pending"] = {"mask_id": "gate-edge", "prompt_id": "12345678", "file": "candidate.png"}
    (tmp_path / "execution.json").write_text(json.dumps(state))
    with pytest.raises(RuntimeError, match="execution state"):
        load_execution_state(tmp_path, manifest)


def test_annotation_changes_after_accepted_prefix_keep_checkpoint_cursor() -> None:
    previous = validate_manifest(sample_manifest())
    state = initial_execution_state(previous)
    state["manifest_digest"] = manifest_identity(previous)
    state = mark_candidate(
        previous,
        state,
        mask_id="road-main",
        prompt_id="12345678-1234-1234-1234-123456789012",
        file="candidates/road-main.png",
    )
    state = accept_candidate(
        state,
        prompt_id="12345678-1234-1234-1234-123456789012",
        candidate_sha256="0" * 64,
        dimensions=[768, 1424],
    )
    updated_manifest = json.loads(json.dumps(previous))
    updated_manifest["masks"][1]["comment"] = "Repair the gate edge with a cleaner transition."
    refreshed = execution_state_for_manifest(
        updated_manifest,
        state,
        previous_manifest=previous,
    )
    assert refreshed["next_index"] == 1
    assert refreshed["current_source"] == "candidates/road-main.png"


def test_annotation_changes_to_an_accepted_mask_restart_checkpoints() -> None:
    previous = validate_manifest(sample_manifest())
    state = initial_execution_state(previous)
    state["manifest_digest"] = manifest_identity(previous)
    state = mark_candidate(
        previous,
        state,
        mask_id="road-main",
        prompt_id="12345678-1234-1234-1234-123456789012",
        file="candidates/road-main.png",
    )
    state = accept_candidate(
        state,
        prompt_id="12345678-1234-1234-1234-123456789012",
        candidate_sha256="0" * 64,
        dimensions=[768, 1424],
    )
    updated_manifest = json.loads(json.dumps(previous))
    updated_manifest["masks"][0]["comment"] = "Regenerate the entire road."
    refreshed = execution_state_for_manifest(
        updated_manifest,
        state,
        previous_manifest=previous,
    )
    assert refreshed["next_index"] == 0
    assert refreshed["current_source"] == "source.png"


def test_mask_content_changes_to_an_accepted_mask_restart_checkpoints() -> None:
    previous = validate_manifest(sample_manifest())
    previous["masks"][0]["sha256"] = "a" * 64
    state = initial_execution_state(previous)
    state["manifest_digest"] = manifest_identity(previous)
    state = mark_candidate(
        previous,
        state,
        mask_id="road-main",
        prompt_id="12345678-1234-1234-1234-123456789012",
        file="candidates/road-main.png",
    )
    state = accept_candidate(
        state,
        prompt_id="12345678-1234-1234-1234-123456789012",
        candidate_sha256="0" * 64,
        dimensions=[768, 1424],
    )
    updated_manifest = json.loads(json.dumps(previous))
    updated_manifest["masks"][0]["sha256"] = "b" * 64
    refreshed = execution_state_for_manifest(
        updated_manifest,
        state,
        previous_manifest=previous,
    )
    assert refreshed["next_index"] == 0
    assert refreshed["current_source"] == "source.png"


def test_reject_candidate_clears_pending_without_advancing_cursor() -> None:
    manifest = validate_manifest(sample_manifest())
    state = mark_candidate(
        manifest,
        initial_execution_state(manifest),
        mask_id="road-main",
        prompt_id="12345678-1234-1234-1234-123456789012",
        file="candidates/road-main.png",
    )
    rejected = reject_candidate(
        state, prompt_id="12345678-1234-1234-1234-123456789012"
    )
    assert rejected["pending"] is None
    assert rejected["next_index"] == 0
    assert rejected["rejected"][0]["mask_id"] == "road-main"


def test_sequential_jobs_require_explicit_checkpoint_sources_after_first_pass() -> None:
    manifest = validate_manifest(sample_manifest())
    jobs = compile_jobs(
        manifest,
        source_file="uploaded/source.png",
        mask_files={
            "road-main": "uploaded/road-main.png",
            "gate-edge": "uploaded/gate-edge.png",
        },
    )
    assert jobs[0]["source_file"] == "uploaded/source.png"
    assert jobs[1]["source_file"] is None
    assert jobs[1]["requires_checkpoint"] is True


def test_validate_graph_rejects_ui_workflow_shape() -> None:
    with pytest.raises(ValueError, match="API-format"):
        validate_graph({"nodes": [], "links": []})


def test_graph_preflight_checks_live_required_inputs_and_enum_values() -> None:
    graph = compile_graph(
        source_file="source.png",
        mask_file="road.png",
        prompt="Repair road",
        output_prefix="repair/road",
        width=768,
        height=1424,
    )
    schemas = {
        "LoadImage": {"input": {"required": {"image": ["COMBO"]}}},
        "LoadImageMask": {
            "input": {
                "required": {
                    "image": ["COMBO"],
                    "channel": [["alpha", "red"]],
                }
            }
        },
        "MaskToImage": {"input": {"required": {"mask": ["MASK"]}}},
        "GPTImage15Edit_fal": {
            "input": {
                "required": {"prompt": ["STRING"], "images": ["IMAGE"]},
                "optional": {
                    "mask_image": ["IMAGE"],
                    "image_size": [["auto"]],
                    "background": [["opaque"]],
                    "quality": [["high"]],
                    "input_fidelity": [["high"]],
                    "num_images": ["INT"],
                    "output_format": [["png"]],
                    "sync_mode": ["BOOLEAN"],
                },
            }
        },
        "SaveImage": {"input": {"required": {"images": ["IMAGE"], "filename_prefix": ["STRING"]}}},
    }
    validate_graph_schemas(graph, schemas)
    broken = json.loads(json.dumps(graph))
    del broken["4"]["inputs"]["prompt"]
    with pytest.raises(ValueError, match="required input"):
        validate_graph_schemas(broken, schemas)
    invalid_enum = json.loads(json.dumps(graph))
    invalid_enum["2"]["inputs"]["channel"] = "blue"
    with pytest.raises(ValueError, match="enum"):
        validate_graph_schemas(invalid_enum, schemas)


def test_controller_rejects_non_loopback_comfy_url(tmp_path) -> None:
    with pytest.raises(ValueError, match="loopback"):
        ComfyController("http://192.0.2.1:8191", session_dir=tmp_path)


def test_controller_rejects_credentials_in_comfy_url(tmp_path) -> None:
    with pytest.raises(ValueError, match="credentials"):
        ComfyController("http://user:secret@127.0.0.1:8191", session_dir=tmp_path)
    with pytest.raises(ValueError, match="query or fragment"):
        ComfyController("http://127.0.0.1:8191?token=secret", session_dir=tmp_path)


def test_submit_runs_live_preflight_before_posting(tmp_path, monkeypatch) -> None:
    controller = ComfyController(session_dir=tmp_path, allow_paid=True)
    graph = compile_graph(
        source_file="source.png",
        mask_file="road.png",
        prompt="Repair road",
        output_prefix="repair/road",
        width=768,
        height=1424,
    )
    calls = []
    monkeypatch.setattr(controller, "preflight_graph", lambda graph, **kwargs: calls.append(graph))
    monkeypatch.setattr(
        "mask_workbench._json_request",
        lambda *args, **kwargs: (200, b'{"prompt_id":"12345678-1234-1234-1234-123456789012"}'),
    )
    result = controller.submit(graph, confirmation="SUBMIT_PAID")
    assert result["prompt_id"].startswith("12345678")
    assert calls == [graph]


def test_corrupt_existing_ledger_fails_closed_before_submission(tmp_path, monkeypatch) -> None:
    controller = ComfyController(session_dir=tmp_path, allow_paid=True)
    controller.ledger_path.write_text("not-json")
    graph = compile_graph(
        source_file="source.png", mask_file="road.png", prompt="Repair road",
        output_prefix="repair/road", width=768, height=1424,
    )
    monkeypatch.setattr(controller, "preflight_graph", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        "mask_workbench._json_request",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("must not submit")),
    )
    with pytest.raises(RuntimeError, match="ledger"):
        controller.submit(graph, confirmation="SUBMIT_PAID")


def test_submit_records_ambiguous_response_and_blocks_retry(tmp_path, monkeypatch) -> None:
    controller = ComfyController(session_dir=tmp_path, allow_paid=True)
    graph = compile_graph(
        source_file="source.png", mask_file="road.png", prompt="Repair road",
        output_prefix="repair/road", width=4, height=4,
    )
    monkeypatch.setattr(controller, "preflight_graph", lambda *args, **kwargs: None)
    monkeypatch.setattr(controller, "_open_websocket", lambda: None)
    monkeypatch.setattr("mask_workbench._json_request", lambda *args, **kwargs: (500, b"{}"))
    with pytest.raises(RuntimeError, match="ambiguous"):
        controller.submit(graph, confirmation="SUBMIT_PAID")
    ledger = json.loads((tmp_path / "jobs.json").read_text())
    assert next(iter(ledger.values()))["state"] == "unknown-reconcile-required"


def test_submit_records_ambiguous_transport_failure_and_blocks_retry(tmp_path, monkeypatch) -> None:
    controller = ComfyController(session_dir=tmp_path, allow_paid=True)
    graph = compile_graph(
        source_file="source.png", mask_file="road.png", prompt="Repair road",
        output_prefix="repair/road", width=768, height=1424,
    )
    monkeypatch.setattr(controller, "preflight_graph", lambda *args, **kwargs: None)
    monkeypatch.setattr(controller, "_open_websocket", lambda: None)
    monkeypatch.setattr("mask_workbench._json_request", lambda *args, **kwargs: (_ for _ in ()).throw(TimeoutError()))
    with pytest.raises(RuntimeError, match="outcome is unknown"):
        controller.submit(graph, confirmation="SUBMIT_PAID")
    ledger = json.loads((tmp_path / "jobs.json").read_text())
    assert next(iter(ledger.values()))["state"] == "unknown-reconcile-required"
    with pytest.raises(DuplicateJobError):
        controller.submit(graph, confirmation="SUBMIT_PAID")


def test_concurrent_duplicate_submissions_queue_only_once(tmp_path, monkeypatch) -> None:
    controllers = [
        ComfyController(session_dir=tmp_path, allow_paid=True),
        ComfyController(session_dir=tmp_path, allow_paid=True),
    ]
    graph = compile_graph(
        source_file="source.png", mask_file="road.png", prompt="Repair road",
        output_prefix="repair/road", width=768, height=1424,
    )
    for controller in controllers:
        monkeypatch.setattr(controller, "preflight_graph", lambda *args, **kwargs: None)
        monkeypatch.setattr(controller, "_open_websocket", lambda: None)
    calls = 0
    calls_lock = threading.Lock()

    def submit_once(*args, **kwargs):
        nonlocal calls
        with calls_lock:
            calls += 1
        time.sleep(0.05)
        return 200, b'{"prompt_id":"12345678-1234-1234-1234-123456789012"}'

    monkeypatch.setattr("mask_workbench._json_request", submit_once)
    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(
            lambda controller: _capture_submit(controller, graph),
            controllers,
        ))
    assert calls == 1
    assert sum(isinstance(result, DuplicateJobError) for result in results) == 1


def test_duplicate_lock_serializes_separate_processes(tmp_path) -> None:
    calls = []

    class PromptServer(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_POST(self):
            if self.path != "/prompt":
                self.send_error(404)
                return
            self.rfile.read(int(self.headers.get("Content-Length", "0")))
            calls.append(1)
            time.sleep(0.1)
            body = b'{"prompt_id":"12345678-1234-1234-1234-123456789012"}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    server = ThreadingHTTPServer(("127.0.0.1", 0), PromptServer)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    context = multiprocessing.get_context("spawn")
    start = context.Event()
    results = context.Queue()
    processes = [
        context.Process(
            target=_process_submit,
            args=(str(tmp_path), f"http://127.0.0.1:{server.server_address[1]}", start, results),
        )
        for _ in range(2)
    ]
    try:
        for process in processes:
            process.start()
        start.set()
        for process in processes:
            process.join(10)
            assert process.exitcode == 0
        outcomes = sorted(results.get(timeout=2) for _ in processes)
        assert calls == [1]
        assert outcomes == ["DuplicateJobError", "dict"]
    finally:
        for process in processes:
            if process.is_alive():
                process.terminate()
                process.join(2)
        server.shutdown()
        server.server_close()
        server_thread.join(timeout=2)


def test_submit_persists_reservation_before_remote_success(tmp_path, monkeypatch) -> None:
    controller = ComfyController(session_dir=tmp_path, allow_paid=True)
    graph = compile_graph(
        source_file="source.png", mask_file="road.png", prompt="Repair road",
        output_prefix="repair/road", width=768, height=1424,
    )
    monkeypatch.setattr(controller, "preflight_graph", lambda *args, **kwargs: None)
    monkeypatch.setattr(controller, "_open_websocket", lambda: None)
    monkeypatch.setattr(
        "mask_workbench._json_request",
        lambda *args, **kwargs: (200, b'{"prompt_id":"12345678-1234-1234-1234-123456789012"}'),
    )
    save_calls = 0
    real_save = controller._save_ledger

    def fail_final_save(ledger):
        nonlocal save_calls
        save_calls += 1
        if save_calls == 2:
            raise OSError("disk full")
        real_save(ledger)

    monkeypatch.setattr(controller, "_save_ledger", fail_final_save)
    with pytest.raises(RuntimeError, match="final receipt"):
        controller.submit(graph, confirmation="SUBMIT_PAID")
    persisted = json.loads((tmp_path / "jobs.json").read_text())
    assert next(iter(persisted.values()))["state"] == "reserved"
    recovery = json.loads((tmp_path / "reconcile-12345678-1234-1234-1234-123456789012.json").read_text())
    assert recovery["prompt_id"] == "12345678-1234-1234-1234-123456789012"
    with pytest.raises(DuplicateJobError):
        controller.submit(graph, confirmation="SUBMIT_PAID")


def test_confirmed_terminal_failure_allows_a_retry(tmp_path, monkeypatch) -> None:
    controller = ComfyController(session_dir=tmp_path, allow_paid=True)
    graph = compile_graph(
        source_file="source.png", mask_file="road.png", prompt="Repair road",
        output_prefix="repair/road", width=4, height=4,
    )
    monkeypatch.setattr(controller, "preflight_graph", lambda *args, **kwargs: None)
    prompt_ids = iter([
        "12345678-1234-1234-1234-123456789012",
        "87654321-4321-4321-4321-210987654321",
    ])
    monkeypatch.setattr(
        "mask_workbench._json_request",
        lambda *args, **kwargs: (200, json.dumps({"prompt_id": next(prompt_ids)}).encode()),
    )
    first = controller.submit(graph, confirmation="SUBMIT_PAID")
    controller.mark_terminal_failure(first["prompt_id"], {"status": "failed"})
    second = controller.submit(graph, confirmation="SUBMIT_PAID")
    assert second["prompt_id"] != first["prompt_id"]


def test_submit_rejects_the_same_fingerprint_twice(tmp_path, monkeypatch) -> None:
    controller = ComfyController(session_dir=tmp_path, allow_paid=True)
    graph = compile_graph(
        source_file="source.png",
        mask_file="road.png",
        prompt="Repair road",
        output_prefix="repair/road",
        width=768,
        height=1424,
    )
    monkeypatch.setattr(controller, "preflight_graph", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        "mask_workbench._json_request",
        lambda *args, **kwargs: (200, b'{"prompt_id":"12345678-1234-1234-1234-123456789012"}'),
    )
    controller.submit(graph, confirmation="SUBMIT_PAID")
    with pytest.raises(DuplicateJobError):
        controller.submit(graph, confirmation="SUBMIT_PAID")


def test_uploaded_name_keeps_comfy_subfolder() -> None:
    assert uploaded_name({"name": "mask.png", "subfolder": "session", "type": "input"}) == "session/mask.png"
    assert uploaded_name({"name": "source.png"}) == "source.png"


def test_controller_preflight_fetches_each_live_schema_before_submission(tmp_path, monkeypatch) -> None:
    controller = ComfyController(session_dir=tmp_path)
    graph = compile_graph(
        source_file="source.png",
        mask_file="road.png",
        prompt="Repair road",
        output_prefix="repair/road",
        width=768,
        height=1424,
    )
    schemas = {
        "LoadImage": {"input": {"required": {"image": [["known-source.png"]]}}, "output": ["IMAGE", "MASK"]},
        "LoadImageMask": {"input": {"required": {"image": [["known-mask.png"]], "channel": [["red"]]}}, "output": ["MASK"]},
        "MaskToImage": {"input": {"required": {"mask": ["MASK"]}}, "output": ["IMAGE"]},
        "GPTImage15Edit_fal": {
            "input": {
                "required": {"prompt": ["STRING"], "images": ["IMAGE"]},
                "optional": {
                    "mask_image": ["IMAGE"], "image_size": [["auto"]], "background": [["opaque"]],
                    "quality": [["high"]], "input_fidelity": [["high"]], "num_images": ["INT"],
                    "output_format": [["png"]], "sync_mode": ["BOOLEAN"],
                },
            },
            "output": ["IMAGE"],
        },
        "SaveImage": {"input": {"required": {"images": ["IMAGE"], "filename_prefix": ["STRING"]}}, "output": ["IMAGE"]},
    }
    monkeypatch.setattr(controller, "json", lambda path: {path.removeprefix("/object_info/"): schemas[path.removeprefix("/object_info/")]})
    controller.preflight_graph(graph, uploaded_files={"source.png", "road.png"})


def test_manifest_identity_ignores_generated_union_receipts() -> None:
    manifest = validate_manifest(sample_manifest())
    generated = json.loads(json.dumps(manifest))
    generated["union_file"] = "masks/union.png"
    generated["union_sha256"] = "a" * 64
    assert manifest_identity(manifest) == manifest_identity(generated)


def test_safe_output_reference_rejects_nested_filename() -> None:
    with pytest.raises(ValueError, match="unsafe output filename"):
        _safe_output_reference({"filename": "nested/result.png", "type": "output"})


def test_controller_client_id_is_stable_for_a_session(tmp_path) -> None:
    first = ComfyController(session_dir=tmp_path)
    second = ComfyController(session_dir=tmp_path)
    assert first.client_id == second.client_id
    assert "127.0.0.1" not in first.client_id


def test_submit_opens_websocket_before_prompt_post(tmp_path, monkeypatch) -> None:
    controller = ComfyController(session_dir=tmp_path, allow_paid=True)
    graph = compile_graph(
        source_file="source.png",
        mask_file="road.png",
        prompt="Repair road",
        output_prefix="repair/road",
        width=768,
        height=1424,
    )
    order = []

    class Socket:
        def close(self):
            order.append("close")

    monkeypatch.setattr(controller, "_open_websocket", lambda: order.append("ws") or Socket())
    monkeypatch.setattr(
        "mask_workbench._json_request",
        lambda *args, **kwargs: (order.append("prompt") or (200, b'{"prompt_id":"12345678-1234-1234-1234-123456789012"}')),
    )
    controller.submit(graph, confirmation="SUBMIT_PAID", preflighted=True)
    assert order[:2] == ["ws", "prompt"]


def test_watch_reconciles_completed_history_without_websocket(tmp_path, monkeypatch) -> None:
    controller = ComfyController(session_dir=tmp_path)
    prompt_id = "12345678-1234-1234-1234-123456789012"
    monkeypatch.setattr(controller, "_open_websocket", lambda: None)
    monkeypatch.setattr(
        controller,
        "history",
        lambda value: {
            value: {
                "status": {"completed": True, "messages": [["execution_success", {}]]},
                "outputs": {"5": {"images": [{"filename": "result.png", "type": "output"}]}},
            }
        },
    )
    result = controller.watch(prompt_id, timeout=1)
    assert result["success"] is True
    assert result["status"] == "success"


def test_stable_submission_fingerprint_ignores_remote_upload_names() -> None:
    first = compile_graph(
        source_file="remote-a/source.png", mask_file="remote-a/mask.png",
        prompt="Repair road", output_prefix="repair/road", width=4, height=4,
    )
    second = compile_graph(
        source_file="remote-b/source.png", mask_file="remote-b/mask.png",
        prompt="Repair road", output_prefix="repair/road", width=4, height=4,
    )
    assert stable_submission_fingerprint(first) == stable_submission_fingerprint(second)


def test_watch_treats_explicit_history_error_as_failure(tmp_path, monkeypatch) -> None:
    controller = ComfyController(session_dir=tmp_path)
    prompt_id = "12345678-1234-1234-1234-123456789012"
    monkeypatch.setattr(controller, "_open_websocket", lambda: None)
    monkeypatch.setattr(
        controller,
        "history",
        lambda value: {
            value: {
                "status": {"completed": True, "status_str": "error"},
                "outputs": {"5": {"images": [{"filename": "partial.png"}]}},
            }
        },
    )
    result = controller.watch(prompt_id, timeout=1)
    assert result["success"] is False
    assert result["status"] == "failed"


def test_watch_keeps_nonterminal_history_in_reconcile_state(tmp_path, monkeypatch) -> None:
    controller = ComfyController(session_dir=tmp_path)
    prompt_id = "12345678-1234-1234-1234-123456789012"
    monkeypatch.setattr(controller, "_open_websocket", lambda: None)
    monkeypatch.setattr(
        controller,
        "history",
        lambda value: {value: {"status": {"completed": False}, "outputs": {}}},
    )
    result = controller.watch(prompt_id, timeout=1)
    assert result["success"] is False
    assert result["status"] == "unknown/reconcile required"


def test_session_save_fails_closed_when_existing_execution_is_corrupt(tmp_path) -> None:
    source = tmp_path / "source.png"
    Image.new("RGB", (4, 4), (10, 20, 30)).save(source)
    session = tmp_path / "session"
    session.mkdir()
    session_manifest = sample_manifest()
    session_manifest["source"]["file"] = "source.png"
    (session / "manifest.json").write_text(json.dumps(session_manifest))
    (session / "execution.json").write_text("not-json")
    handler = make_handler(
        source_path=source,
        session_dir=session,
        comfy_url="http://127.0.0.1:8191",
        allow_paid=False,
    )
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{server.server_address[1]}"
    try:
        mask = bytearray(16)
        mask[0] = 255
        payload = {
            "manifest": {
                "schema": "carrier-mask-workbench/v1",
                "session_id": "save-check",
                "source": {"file": "source.png", "width": 4, "height": 4},
                "mask_convention": "white=edit,black=preserve",
                "mode": "sequential",
                "overlap_policy": "allow",
                "masks": [{"id": "road", "name": "Road", "comment": "Repair road", "color": "#f97316", "visible": True, "file": "masks/road.png", "bounds": [0, 0, 1, 1]}],
            },
            "masks": {"road": "data:image/png;base64," + base64.b64encode(_png_bytes(4, 4, mask)).decode()},
        }
        response = _post_json_allow_error(base_url, "/api/session", payload)
        assert response[0] >= 400
        assert (session / "execution.json").read_text() == "not-json"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_http_session_save_and_compile_round_trip(tmp_path) -> None:
    source = tmp_path / "source.png"
    Image.new("RGB", (4, 4), (10, 20, 30)).save(source)
    template = tmp_path / "template.json"
    template.write_text(json.dumps({
        "nodes": [
            {"id": 41, "type": "LoadImage"},
            {"id": 99, "type": "MaskToImage"},
            {"id": 7, "type": "GPTImage15Edit_fal"},
            {"id": 8, "type": "SaveImage"},
        ],
        "links": [[12, 41, 1, 99, 0, "MASK"]],
    }))
    session = tmp_path / "session"
    handler = make_handler(
        source_path=source,
        session_dir=session,
        comfy_url="http://127.0.0.1:8191",
        allow_paid=False,
        template_path=template,
    )
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{server.server_address[1]}"
    try:
        config = json.loads(urlopen(base_url + "/api/config").read())
        assert "comfy_url" not in config
        mask_bytes = io.BytesIO()
        Image.new("RGB", (4, 4), (0, 0, 0)).save(mask_bytes, "PNG")
        mask_image = Image.open(io.BytesIO(mask_bytes.getvalue())).copy()
        mask_image.putpixel((1, 2), (255, 255, 255))
        mask_bytes = io.BytesIO()
        mask_image.save(mask_bytes, "PNG")
        data_url = "data:image/png;base64," + base64.b64encode(mask_bytes.getvalue()).decode()
        manifest = {
            "schema": "carrier-mask-workbench/v1",
            "session_id": "http-smoke",
            "source": {"file": "source.png", "width": 4, "height": 4},
            "mask_convention": "white=edit,black=preserve",
            "mode": "sequential",
            "overlap_policy": "allow",
            "masks": [{
                "id": "road", "name": "Road", "comment": "Repair road",
                "color": "#f97316", "visible": True,
                "file": "masks/road.png", "bounds": [1, 2, 2, 3],
            }],
        }
        saved = _post_json(base_url, "/api/session", {"manifest": manifest, "masks": {"road": data_url}})
        compiled = _post_json(base_url, "/api/compile", {})
        assert saved["execution"]["next_index"] == 0
        job = compiled["report"]["jobs"][0]
        assert job["graph"]["4"]["class_type"] == "GPTImage15Edit_fal"
        assert job["graph"]["2"]["inputs"]["image"] == "uploads/road-comfy-alpha.png"
        assert read_mask_alpha(session / "uploads/road-comfy-alpha.png", transport="comfy-alpha")[2][9] == 255
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_paid_http_submit_watch_accept_and_reject_round_trip(tmp_path, monkeypatch) -> None:
    prompt_ids = [
        "11111111-1111-1111-1111-111111111111",
        "22222222-2222-2222-2222-222222222222",
    ]
    submissions = []
    output = io.BytesIO()
    Image.new("RGB", (4, 4), (40, 50, 60)).save(output, "PNG")
    schemas = {
        "LoadImage": {"input": {"required": {"image": ["STRING"]}}, "output": ["IMAGE", "MASK"]},
        "LoadImageMask": {"input": {"required": {"image": ["STRING"], "channel": [["red", "alpha"]]}}, "output": ["MASK"]},
        "MaskToImage": {"input": {"required": {"mask": ["MASK"]}}, "output": ["IMAGE"]},
        "GPTImage15Edit_fal": {
            "input": {
                "required": {"prompt": ["STRING"], "images": ["IMAGE"]},
                "optional": {
                    "mask_image": ["IMAGE"], "image_size": [["auto"]],
                    "background": [["opaque"]], "quality": [["high"]],
                    "input_fidelity": [["high"]], "num_images": ["INT"],
                    "output_format": [["png"]], "sync_mode": ["BOOLEAN"],
                },
            },
            "output": ["IMAGE"],
        },
        "SaveImage": {
            "input": {"required": {"images": ["IMAGE"], "filename_prefix": ["STRING"]}},
            "output": ["IMAGE"],
        },
    }

    class FakeComfy(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def send_json(self, value, status=200):
            body = json.dumps(value).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            path = urlparse(self.path).path
            if path.startswith("/object_info/"):
                class_name = path.rsplit("/", 1)[-1]
                self.send_json({class_name: schemas[class_name]})
                return
            if path.startswith("/history/"):
                prompt_id = path.rsplit("/", 1)[-1]
                self.send_json({
                    prompt_id: {
                        "status": {"completed": True, "messages": [["execution_success", {}]]},
                        "outputs": {"5": {"images": [{
                            "filename": f"{prompt_id}.png", "subfolder": "", "type": "output",
                        }]}},
                    }
                })
                return
            if path == "/view":
                body = output.getvalue()
                self.send_response(200)
                self.send_header("Content-Type", "image/png")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            self.send_error(404)

        def do_POST(self):
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length)
            if self.path == "/upload/image":
                filename = re.search(br'filename="([^\"]+)"', body).group(1).decode()
                self.send_json({"name": filename, "subfolder": "", "type": "input"})
                return
            if self.path == "/prompt":
                submissions.append(json.loads(body))
                self.send_json({"prompt_id": prompt_ids[len(submissions) - 1], "number": len(submissions), "node_errors": {}})
                return
            self.send_error(404)

    fake_comfy = ThreadingHTTPServer(("127.0.0.1", 0), FakeComfy)
    fake_thread = threading.Thread(target=fake_comfy.serve_forever, daemon=True)
    fake_thread.start()
    source = tmp_path / "source.png"
    Image.new("RGB", (4, 4), (10, 20, 30)).save(source)
    session = tmp_path / "session"
    monkeypatch.setattr(ComfyController, "_open_websocket", lambda self: None)
    handler = make_handler(
        source_path=source,
        session_dir=session,
        comfy_url=f"http://127.0.0.1:{fake_comfy.server_address[1]}",
        allow_paid=True,
    )
    workbench = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    workbench_thread = threading.Thread(target=workbench.serve_forever, daemon=True)
    workbench_thread.start()
    base_url = f"http://127.0.0.1:{workbench.server_address[1]}"
    try:
        mask_payloads = {}
        masks = []
        for mask_id, point in (("road", (0, 0)), ("gate", (3, 3))):
            image = Image.new("RGB", (4, 4), (0, 0, 0))
            image.putpixel(point, (255, 255, 255))
            stream = io.BytesIO()
            image.save(stream, "PNG")
            mask_payloads[mask_id] = "data:image/png;base64," + base64.b64encode(stream.getvalue()).decode()
            masks.append({
                "id": mask_id, "name": mask_id.title(), "comment": f"Repair {mask_id}",
                "color": "#f97316", "visible": True,
                "file": f"masks/{mask_id}.png",
                "bounds": [point[0], point[1], point[0] + 1, point[1] + 1],
            })
        manifest = {
            "schema": "carrier-mask-workbench/v1", "session_id": "paid-http",
            "source": {"file": "source.png", "width": 4, "height": 4},
            "mask_convention": "white=edit,black=preserve",
            "mode": "sequential", "overlap_policy": "allow", "masks": masks,
        }
        _post_json(base_url, "/api/session", {"manifest": manifest, "masks": mask_payloads})

        first = _post_json(base_url, "/api/comfy/submit", {"mask_id": "road", "confirmation": "SUBMIT_PAID"})
        first_id = first["response"]["prompt_id"]
        submit_receipts = list(session.glob("submit-road-*.json"))
        assert len(submit_receipts) == 1
        submit_receipt = json.loads(submit_receipts[0].read_text())
        assert submit_receipt["source_upload"]["name"] == "source.png"
        assert submit_receipt["mask_upload"]["name"] == "road.png"
        assert len(submit_receipt["transport_mask_sha256"]) == 64
        watched = _post_json(base_url, "/api/comfy/watch", {"prompt_id": first_id})
        assert watched["success"] is True
        assert Image.open(io.BytesIO(urlopen(base_url + watched["candidate"]["url"]).read())).size == (4, 4)
        accepted = _post_json(base_url, "/api/comfy/accept", {"prompt_id": first_id})
        assert accepted["execution"]["next_index"] == 1

        second = _post_json(base_url, "/api/comfy/submit", {"mask_id": "gate", "confirmation": "SUBMIT_PAID"})
        second_id = second["response"]["prompt_id"]
        assert _post_json(base_url, "/api/comfy/watch", {"prompt_id": second_id})["success"] is True
        rejected = _post_json(base_url, "/api/comfy/reject", {"prompt_id": second_id})
        assert rejected["execution"]["next_index"] == 1
        assert rejected["execution"]["pending"] is None
        assert len(submissions) == 2
        assert all(entry["prompt"]["4"]["class_type"] == "GPTImage15Edit_fal" for entry in submissions)
    finally:
        workbench.shutdown()
        workbench.server_close()
        workbench_thread.join(timeout=2)
        fake_comfy.shutdown()
        fake_comfy.server_close()
        fake_thread.join(timeout=2)


def test_accept_candidate_requires_integrity_metadata() -> None:
    manifest = validate_manifest(sample_manifest())
    state = mark_candidate(
        manifest,
        initial_execution_state(manifest),
        mask_id="road-main",
        prompt_id="12345678-1234-1234-1234-123456789012",
        file="candidates/road-main.png",
    )
    with pytest.raises(ValueError, match="hash"):
        accept_candidate(
            state,
            prompt_id="12345678-1234-1234-1234-123456789012",
            candidate_sha256=None,
            dimensions=[768, 1424],
        )
    with pytest.raises(ValueError, match="dimensions"):
        accept_candidate(
            state,
            prompt_id="12345678-1234-1234-1234-123456789012",
            candidate_sha256="0" * 64,
            dimensions=None,
        )


def test_submission_recovery_record_is_self_contained() -> None:
    submission = {
        "prompt_id": "12345678-1234-1234-1234-123456789012",
        "source_sha256": "1" * 64,
        "mask_sha256": "2" * 64,
        "source_upload": {"name": "source.png"},
        "mask_upload": {"name": "mask.png"},
        "graph": {"1": {"class_type": "LoadImage", "inputs": {"image": "source.png"}}},
    }
    execution = {"pending": {"prompt_id": submission["prompt_id"]}}
    recovery = workbench.submission_recovery_record(
        submission,
        execution,
        receipt_name="submit-road.json",
    )
    assert recovery["submission"] == submission
    assert recovery["execution"] == execution
    assert recovery["receipt"] == "submit-road.json"


def test_mask_png_refuses_a_symlink_destination(tmp_path) -> None:
    outside = tmp_path / "outside.png"
    Image.new("RGB", (2, 2), (1, 2, 3)).save(outside)
    original = outside.read_bytes()
    destination = tmp_path / "mask.png"
    destination.symlink_to(outside.name)

    with pytest.raises(ValueError, match="symlink"):
        write_mask_png(destination, 2, 2, bytes([0, 255, 0, 255]))
    assert outside.read_bytes() == original


def test_session_path_rejects_an_existing_symlink(tmp_path) -> None:
    session = tmp_path / "session"
    session.mkdir()
    (session / "real.png").write_bytes(b"protected")
    (session / "overlay.png").symlink_to("real.png")
    with pytest.raises(ValueError, match="symlink"):
        _safe_session_path(session, "overlay.png")


def test_mask_png_payload_is_decodable_and_keeps_dimensions(tmp_path) -> None:
    alpha = bytes([0, 255, 127, 255])
    from mask_workbench import write_mask_png

    path = tmp_path / "mask.png"
    write_mask_png(path, 2, 2, alpha)
    image = Image.open(path).convert("RGB")
    assert image.size == (2, 2)
    assert list(image.get_flattened_data()) == [
        (0, 0, 0),
        (255, 255, 255),
        (127, 127, 127),
        (255, 255, 255),
    ]
