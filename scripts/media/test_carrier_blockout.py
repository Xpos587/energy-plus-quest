from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/media/carrier_blockout.py"


def test_blockout_describes_v12_metropolitan_logistics_scene(tmp_path: Path) -> None:
    manifest = tmp_path / "layout.json"
    env = os.environ.copy()
    compat_library = Path("/usr/lib/libjsoncpp.so.27")
    if compat_library.exists() and not Path("/usr/lib/libjsoncpp.so.26").exists():
        compat_dir = tmp_path / "blender-libs"
        compat_dir.mkdir()
        (compat_dir / "libjsoncpp.so.26").symlink_to(compat_library)
        env["LD_LIBRARY_PATH"] = os.pathsep.join(
            filter(None, (str(compat_dir), env.get("LD_LIBRARY_PATH"))),
        )

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
        env=env,
        text=True,
        timeout=120,
    )

    assert result.returncode == 0, result.stderr or result.stdout
    layout = json.loads(manifest.read_text())

    assert layout["season"] == "early-autumn"
    assert layout["setting"] == "metropolitan-logistics-centre"
    assert layout["network_connected"] is True
    assert len(layout["roads"]) >= 7
    assert len(layout["buildings"]) >= 12
    assert layout["props"]["loading_bays"] >= 6
    assert layout["props"]["trees"] >= 12
    assert layout["props"]["snowbanks"] == 0
    assert layout["props"]["decorative_vehicles"] == 0
    assert layout["props"]["express_vehicles"] == 0

    assert list(layout["trucks"]) == ["truck-1", "truck-2", "truck-3", "truck-4"]
    assert [truck["outcome"] for truck in layout["trucks"].values()] == [
        "old",
        "near",
        "crew",
        "old",
    ]
    assert len({truck["road_id"] for truck in layout["trucks"].values()}) == 4
    assert layout["trucks"]["truck-2"]["nearest_to_warehouse"] is True
    assert layout["trucks"]["truck-3"]["drivers"] == 2

    assert set(layout["viewports"]) == {"desktop", "mobile"}
    assert layout["viewports"]["desktop"]["size"] == [2880, 1800]
    assert layout["viewports"]["mobile"]["size"] == [780, 1688]
    for viewport in layout["viewports"].values():
        assert viewport["landmarks"]["warehouse"]["visible_fraction"] >= 0.75
        assert set(viewport["trucks"]) == set(layout["trucks"])
        for truck in viewport["trucks"].values():
            assert truck["visible"] is True
            assert truck["visible_fraction"] >= 0.7
