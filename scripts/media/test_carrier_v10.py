"""Small artifact gate for the carrier-map v10 structural master."""

from __future__ import annotations

import json
import sys
from pathlib import Path

EXPECTED_CARRIERS = {"old", "near", "crew", "express"}
REQUIRED_LANDMARKS = {"warehouse", "loading_gate"}
REQUIRED_VIEWPORTS = {"desktop", "tablet", "mobile"}


def check_manifest(path: Path) -> None:
    payload = json.loads(path.read_text())
    assert payload["network_connected"] is True
    assert set(payload["carriers"]) == EXPECTED_CARRIERS
    assert set(payload["viewports"]) == REQUIRED_VIEWPORTS

    for viewport in payload["viewports"].values():
        assert REQUIRED_LANDMARKS <= set(viewport["landmarks"])
        assert all(
            viewport["landmarks"][landmark]["visible_fraction"] >= 0.75
            for landmark in REQUIRED_LANDMARKS
        )
        assert set(viewport["vehicles"]) == EXPECTED_CARRIERS
        assert all(vehicle["visible"] for vehicle in viewport["vehicles"].values())


if __name__ == "__main__":
    check_manifest(Path(sys.argv[1]))
    print("carrier v10 manifest: ok")
