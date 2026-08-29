"""Render deterministic per-carrier RGBA cutouts from canonical Blender scene."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import bpy
from PIL import Image


def parse() -> argparse.Namespace:
    argv = __import__("sys").argv
    argv = argv[argv.index("--") + 1 :] if "--" in argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--blend", required=True, type=Path)
    p.add_argument("--output-dir", required=True, type=Path)
    return p.parse_args(argv)


def main() -> None:
    a = parse()
    bpy.ops.wm.open_mainfile(filepath=str(a.blend.resolve()))
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = True
    scene.render.resolution_percentage = 100

    carriers = {
        "old": ("OldCarrier", "north-service", "old-"),
        "near": ("NearCarrier", "east-street", "near-"),
        "crew": ("CrewCarrier", "main-avenue", "crew-"),
        "express": ("ExpressCarrier", "south-arterial", "express-"),
    }
    collections = list(bpy.data.collections)
    environment = bpy.data.collections["Environment"]
    cues = bpy.data.collections["CueProps"]
    output = a.output_dir.resolve()
    manifest: dict[str, object] = {"blend": str(a.blend.resolve()), "viewports": {}}

    for viewport, camera_name, size in (
        ("desktop", "CameraDesktop", (1536, 864)),
        ("tablet", "CameraTablet", (1200, 1200)),
        ("mobile", "CameraMobile", (944, 1792)),
    ):
        camera = bpy.data.objects[camera_name]
        scene.camera = camera
        scene.render.resolution_x, scene.render.resolution_y = size
        vp = output / viewport
        vp.mkdir(parents=True, exist_ok=True)
        manifest["viewports"][viewport] = {"size": list(size), "camera": camera_name, "carriers": {}}

        for carrier, (carrier_collection, road_prefix, cue_prefix) in carriers.items():
            keep = {carrier_collection}
            # Road branch and lane dashes establish contact and direction.
            road_objects = [o for o in environment.objects if o.name == road_prefix or o.name.startswith(road_prefix + "-")]
            keep_objects = set(bpy.data.collections[carrier_collection].objects) | set(road_objects)
            keep_objects |= {o for o in cues.objects if o.name.startswith(cue_prefix)}
            if carrier == "old":
                keep_objects |= {o for o in cues.objects if o.name in {"InspectionBooth", "InspectionSign"}}
            if carrier == "near":
                keep_objects |= {o for o in cues.objects if o.name in {"GateBarrier", "GateSnowBank"}}

            for collection in collections:
                collection.hide_render = collection.name not in {"Environment", "CueProps", carrier_collection}
            for obj in environment.objects:
                obj.hide_render = obj not in keep_objects
            for obj in cues.objects:
                obj.hide_render = obj not in keep_objects
            for collection in collections:
                if collection.name == carrier_collection:
                    collection.hide_render = False

            color_path = vp / f"{carrier}-color.png"
            scene.render.filepath = str(color_path)
            bpy.ops.render.render(write_still=True)
            with Image.open(color_path) as im:
                im = im.convert("RGBA")
                alpha = im.getchannel("A")
                alpha_path = vp / f"{carrier}-id.png"
                alpha.point(lambda px: 255 if px > 8 else 0).save(alpha_path)
                manifest["viewports"][viewport]["carriers"][carrier] = {
                    "color": str(color_path),
                    "id_mask": str(alpha_path),
                    "size": list(im.size),
                    "nonzero_alpha": sum(1 for px in alpha.getdata() if px > 8),
                    "road_prefix": road_prefix,
                }

    (output / "cutouts.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
