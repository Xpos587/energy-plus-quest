from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
PRODUCTION = ROOT / "design/scene-01/assets/feedback-v12/production"
EXPECTED = {
    "choices/professional.webp": (1536, 1920),
    "map/carrier-desktop.webp": (2880, 1800),
    "map/carrier-mobile.webp": (780, 1688),
    "outcomes/old-desktop.webp": (2880, 1800),
    "outcomes/old-mobile.webp": (780, 1688),
    "outcomes/near-desktop.webp": (2880, 1800),
    "outcomes/near-mobile.webp": (780, 1688),
    "outcomes/crew-desktop.webp": (2880, 1800),
    "outcomes/crew-mobile.webp": (780, 1688),
    "outcomes/express-desktop.webp": (2880, 1800),
    "outcomes/express-mobile.webp": (780, 1688),
}


def test_feedback_v12_runtime_assets_are_complete_and_large_enough() -> None:
    discovered = {
        path.relative_to(PRODUCTION).as_posix()
        for path in PRODUCTION.rglob("*")
        if path.is_file()
    }
    assert discovered == set(EXPECTED)

    for relative_path, minimum_size in EXPECTED.items():
        with Image.open(PRODUCTION / relative_path) as image:
            assert image.format == "WEBP"
            assert image.width >= minimum_size[0]
            assert image.height >= minimum_size[1]
