#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["fonttools==4.65.0", "brotli==1.2.0"]
# ///
"""Derive WOFF2 subsets without modifying the editable font sources."""

import json
import sys
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont


def main():
    manifest = json.loads(Path(sys.argv[1]).read_text())
    receipts = []
    for item in manifest["fonts"]:
        options = subset.Options()
        options.flavor = "woff2"
        options.layout_features = ["*"]
        options.name_IDs = ["*"]
        options.name_languages = ["*"]
        options.name_legacy = True
        options.recalc_timestamp = False
        font = subset.load_font(item["source"], options)
        original_cmap = font.getBestCmap()
        license_records = {
            (record.nameID, record.platformID, record.platEncID, record.langID, record.toUnicode())
            for record in font["name"].names
            if record.nameID in (0, 13, 14)
        }
        subsetter = subset.Subsetter(options=options)
        subsetter.populate(unicodes=manifest["unicodes"])
        subsetter.subset(font)
        subset.save_font(font, item["output"], options)
        output = TTFont(item["output"])
        actual = output.getBestCmap()
        expected = set(manifest["unicodes"]) & original_cmap.keys()
        if not expected <= actual.keys():
            raise RuntimeError("Subset lost requested glyphs")
        retained_license = {
            (record.nameID, record.platformID, record.platEncID, record.langID, record.toUnicode())
            for record in output["name"].names
            if record.nameID in (0, 13, 14)
        }
        if not license_records <= retained_license:
            raise RuntimeError("Subset lost font copyright or license records")
        receipts.append({
            "source": item["name"],
            "sourceBytes": Path(item["source"]).stat().st_size,
            "optimizedBytes": Path(item["output"]).stat().st_size,
            "codepoints": sorted(actual),
        })
    print(json.dumps({"fonts": receipts}))


if __name__ == "__main__":
    main()
