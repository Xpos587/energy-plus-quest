from __future__ import annotations

import json
import math
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/media/carrier_blockout.py"


def angle_difference(first: float, second: float) -> float:
    return abs((first - second + math.pi) % (2 * math.pi) - math.pi)


def test_blockout_describes_populated_connected_town(tmp_path: Path) -> None:
    manifest = tmp_path / "layout.json"
    result = subprocess.run(
        [
            "blender",
            "--background",
            "--python",
            str(SCRIPT),
            "--",
            "--output-dir",
            str(tmp_path),
            "--manifest",
            str(manifest),
            "--skip-render",
        ],
        capture_output=True,
        cwd=ROOT,
        text=True,
        timeout=120,
    )

    assert result.returncode == 0, result.stderr or result.stdout
    layout = json.loads(manifest.read_text())

    assert len(layout["roads"]) >= 7
    assert len(layout["buildings"]) >= 14
    assert layout["props"]["lamps"] >= 8
    assert layout["props"]["trees"] >= 12
    assert layout["props"]["snowbanks"] >= 12
    assert layout["props"]["mountains"] >= 4
    assert layout["props"]["motion_tracks"] >= 8
    assert layout["props"]["snow_plumes"] >= 8
    assert layout["props"]["express_wordmarks"] == 1
    assert layout["network_connected"] is True

    body_types = {carrier["body_type"] for carrier in layout["carriers"].values()}
    assert body_types == {
        "old-tarp-flatbed",
        "panel-van",
        "high-box-crew",
        "streamlined-express",
    }

    assert set(layout["viewports"]) == {"desktop", "tablet", "mobile"}
    for viewport in layout["viewports"].values():
        assert viewport["landmarks"]["warehouse"]["visible_fraction"] >= 0.75
        assert viewport["landmarks"]["loading_gate"]["visible_fraction"] >= 0.75
        assert set(viewport["vehicles"]) == {"old", "near", "crew", "express"}
        for vehicle in viewport["vehicles"].values():
            assert vehicle["visible"] is True
            assert vehicle["visible_fraction"] >= 0.75
            left, bottom, right, top = vehicle["bounds"]
            assert right - left >= 0.055
            assert top - bottom >= 0.025

    road_angles = {road["id"]: road["angle"] for road in layout["roads"]}
    carriers = layout["carriers"]
    assert len({carrier["road_id"] for carrier in carriers.values()}) == 4
    for carrier in carriers.values():
        difference = angle_difference(carrier["angle"], road_angles[carrier["road_id"]])
        assert min(difference, abs(math.pi - difference)) <= math.radians(1)
