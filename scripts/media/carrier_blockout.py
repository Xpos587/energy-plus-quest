"""Build deterministic carrier-scene guides for whole-frame image generation."""

from __future__ import annotations

import argparse
import math
import subprocess
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector


COLORS = {
    "snow": (0.84, 0.91, 0.96, 1.0),
    "road": (0.16, 0.20, 0.25, 1.0),
    "warehouse": (0.02, 0.22, 0.55, 1.0),
    "old": (0.25, 0.20, 0.16, 1.0),
    "near": (0.68, 0.72, 0.73, 1.0),
    "crew": (0.02, 0.24, 0.55, 1.0),
    "express": (1.0, 0.20, 0.02, 1.0),
    "orange": (1.0, 0.32, 0.02, 1.0),
    "skin": (0.63, 0.33, 0.18, 1.0),
    "glass": (0.12, 0.28, 0.38, 1.0),
    "building": (0.48, 0.38, 0.29, 1.0),
    "warm": (1.0, 0.55, 0.16, 1.0),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    return parser.parse_args(args)


def reset_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.collections, bpy.data.materials, bpy.data.cameras):
        for block in list(datablocks):
            if block.users == 0:
                datablocks.remove(block)


def collection(name: str) -> bpy.types.Collection:
    result = bpy.data.collections.get(name)
    if result is None:
        result = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(result)
    return result


def material(name: str, color: tuple[float, float, float, float]) -> bpy.types.Material:
    result = bpy.data.materials.get(name)
    if result is None:
        result = bpy.data.materials.new(name)
        result.diffuse_color = color
        result.roughness = 0.72
    return result


def move_to_collection(obj: bpy.types.Object, target: bpy.types.Collection) -> None:
    for current in list(obj.users_collection):
        current.objects.unlink(obj)
    target.objects.link(obj)


def cube(
    name: str,
    location: tuple[float, float, float],
    scale: tuple[float, float, float],
    color: str,
    target: bpy.types.Collection,
    rotation_z: float = 0.0,
    bevel: float = 0.12,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(location=location, rotation=(0, 0, rotation_z))
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material(f"Mat-{color}", COLORS[color]))
    obj.color = COLORS[color]
    move_to_collection(obj, target)
    if bevel:
        modifier = obj.modifiers.new("Soft edges", "BEVEL")
        modifier.width = bevel
        modifier.segments = 2
    return obj


def cylinder(
    name: str,
    location: tuple[float, float, float],
    radius: float,
    depth: float,
    color: str,
    target: bpy.types.Collection,
    rotation: tuple[float, float, float] = (math.pi / 2, 0, 0),
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=24, radius=radius, depth=depth, location=location, rotation=rotation
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(material(f"Mat-{color}", COLORS[color]))
    obj.color = COLORS[color]
    move_to_collection(obj, target)
    return obj


def add_road(
    name: str,
    location: tuple[float, float, float],
    scale: tuple[float, float, float],
    angle: float,
    target: bpy.types.Collection,
) -> None:
    cube(name, location, scale, "road", target, angle, bevel=0.18)
    length = scale[1] * 2
    for offset in range(-int(length // 3), int(length // 3) + 1):
        dash_y = offset * 3.0
        local = Vector((0, dash_y, 0))
        local.rotate(Matrix.Rotation(angle, 4, "Z"))
        cube(
            f"{name}-dash-{offset}",
            (location[0] + local.x, location[1] + local.y, location[2] + 0.08),
            (0.09, 0.65, 0.025),
            "snow",
            target,
            angle,
            bevel=0.01,
        )


def add_truck(
    name: str,
    position: tuple[float, float],
    angle: float,
    color: str,
    target: bpy.types.Collection,
    *,
    old: bool = False,
    drivers: int = 1,
    scale_factor: float = 1.0,
) -> None:
    x, y = position
    forward = Vector((0, 1, 0))
    forward.rotate(Matrix.Rotation(angle, 4, "Z"))
    side = Vector((1, 0, 0))
    side.rotate(Matrix.Rotation(angle, 4, "Z"))

    def at(longitudinal: float, lateral: float, z: float) -> tuple[float, float, float]:
        point = Vector((x, y, 0)) + forward * longitudinal + side * lateral
        return point.x, point.y, z

    s = scale_factor
    cube(f"{name}-box", at(-0.65 * s, 0, 1.25 * s), (1.25 * s, 1.75 * s, 1.15 * s), color, target, angle)
    cube(f"{name}-cab", at(1.52 * s, 0, 0.9 * s), (1.22 * s, 0.62 * s, 0.88 * s), color, target, angle, bevel=0.24 * s)
    cube(f"{name}-windshield", at(2.16 * s, 0, 1.1 * s), (1.02 * s, 0.05 * s, 0.44 * s), "glass", target, angle, bevel=0.03)
    for lateral in (-0.82 * s, 0.82 * s):
        for longitudinal in (-1.25 * s, 1.45 * s):
            cylinder(
                f"{name}-wheel",
                at(longitudinal, lateral, 0.38 * s),
                0.39 * s,
                0.24 * s,
                "road",
                target,
                rotation=(math.pi / 2, 0, angle),
            )
    driver_offsets = [-0.42] if drivers == 1 else [-0.43, 0.43]
    for index, lateral in enumerate(driver_offsets, 1):
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=20,
            ring_count=12,
            radius=0.23 * s,
            location=at(2.24 * s, lateral * s, 1.18 * s),
        )
        head = bpy.context.object
        head.name = f"{name}-driver-{index}"
        head.data.materials.append(material("Mat-skin", COLORS["skin"]))
        head.color = COLORS["skin"]
        move_to_collection(head, target)
    if old:
        cube(f"{name}-old-bumper", at(2.22 * s, 0, 0.38 * s), (1.18 * s, 0.12 * s, 0.1 * s), "near", target, angle, bevel=0.02)


def add_environment() -> None:
    environment = collection("Environment")
    warehouse = collection("Warehouse")
    cues = collection("CueProps")
    old_collection = collection("OldCarrier")
    near_collection = collection("NearCarrier")
    crew_collection = collection("CrewCarrier")
    express_collection = collection("ExpressCarrier")

    cube("SnowGround", (0, 2, -0.45), (17, 15, 0.45), "snow", environment, bevel=0.0)
    add_road("FarRoad", (-4.5, 9.2, 0.05), (2.2, 12.0, 0.12), math.radians(-69), environment)
    add_road("WarehouseRoad", (1.5, 2.0, 0.08), (2.4, 11.5, 0.12), math.radians(-18), environment)
    add_road("FrontRoad", (0.8, -5.4, 0.1), (2.8, 15.0, 0.13), math.radians(-82), environment)

    cube("WarehouseBody", (0.0, 5.1, 2.2), (4.3, 3.0, 2.2), "warehouse", warehouse, bevel=0.22)
    cube("WarehouseRoof", (0.0, 5.1, 4.65), (4.7, 3.35, 0.26), "snow", warehouse, bevel=0.18)
    cube("LoadingGate", (1.8, 1.98, 1.15), (1.35, 0.16, 1.2), "road", warehouse, bevel=0.05)
    for x in (-2.5, 0.0, 2.5):
        cube(f"WarehouseWindow-{x}", (x, 2.06, 3.25), (0.58, 0.08, 0.4), "warm", warehouse, bevel=0.03)

    for index, (x, y) in enumerate(((-13.0, 13.0), (9.5, 11.5), (13.0, 13.0))):
        cube(f"TownBuilding-{index}", (x, y, 1.8), (2.0, 2.3, 1.8), "building", environment, bevel=0.15)
        cube(f"TownRoof-{index}", (x, y, 3.9), (2.25, 2.55, 0.24), "snow", environment, bevel=0.12)

    add_truck("OldTruck", (-10.5, 7.0), math.radians(-72), "old", old_collection, old=True, scale_factor=0.72)
    add_truck("NearTruck", (3.2, 0.2), math.radians(162), "near", near_collection, scale_factor=0.93)
    add_truck("CrewTruck", (-3.2, -5.2), math.radians(-82), "crew", crew_collection, drivers=2, scale_factor=1.08)
    add_truck("ExpressTruck", (4.6, -3.4), math.radians(96), "express", express_collection, scale_factor=0.96)

    cube("InspectionBooth", (-7.0, 10.0, 0.75), (0.75, 0.75, 0.75), "building", cues, bevel=0.12)
    cylinder("InspectionSign", (-7.1, 9.0, 1.25), 0.38, 0.08, "orange", cues, rotation=(0, math.pi / 2, 0))
    cube("GateBarrier", (4.0, 1.7, 0.75), (1.35, 0.08, 0.08), "orange", cues, math.radians(-18), bevel=0.02)
    cube("GateSnowBank", (5.0, 2.8, 0.34), (0.8, 1.25, 0.34), "snow", cues, math.radians(-18), bevel=0.28)
    for index in range(5):
        bpy.ops.mesh.primitive_ico_sphere_add(
            subdivisions=2,
            radius=0.33 + index * 0.08,
            location=(4.2 + index * 0.55, -3.8 + index * 0.15, 0.25 + index * 0.05),
        )
        plume = bpy.context.object
        plume.name = f"ExpressSnowPlume-{index}"
        plume.scale = (1.2, 0.65, 0.5)
        plume.data.materials.append(material("Mat-snow", COLORS["snow"]))
        plume.color = COLORS["snow"]
        move_to_collection(plume, cues)


def point_camera(camera: bpy.types.Object, target: tuple[float, float, float]) -> None:
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()


def create_camera(name: str, location: tuple[float, float, float], target: tuple[float, float, float], lens: float) -> bpy.types.Object:
    data = bpy.data.cameras.new(name)
    data.lens = lens
    data.sensor_width = 36
    camera = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(camera)
    camera.location = location
    point_camera(camera, target)
    return camera


def configure_scene() -> tuple[bpy.types.Object, bpy.types.Object]:
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.display.shading.light = "STUDIO"
    scene.display.shading.studio_light = "paint.sl"
    scene.display.shading.show_shadows = True
    scene.display.shading.show_cavity = True
    scene.display.shading.cavity_type = "WORLD"
    scene.display.shading.color_type = "MATERIAL"
    scene.display.shading.background_type = "WORLD"
    scene.display.shading.show_specular_highlight = True
    scene.world.color = (0.72, 0.82, 0.9)
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.resolution_percentage = 100
    scene.unit_settings.system = "METRIC"
    desktop = create_camera("CameraDesktop", (22.5, -29.0, 27.0), (0.2, 2.1, 0.7), 55)
    mobile = create_camera("CameraMobile", (17.0, -34.0, 34.0), (-0.8, 2.5, 0.5), 60)
    return desktop, mobile


def render_pass(output: Path, camera: bpy.types.Object, size: tuple[int, int], pass_name: str) -> None:
    scene = bpy.context.scene
    scene.camera = camera
    scene.render.resolution_x, scene.render.resolution_y = size
    scene.render.filepath = str(output)
    shading = scene.display.shading
    original_color_type = shading.color_type
    original_light = shading.light
    original_colors = {obj.name: tuple(obj.color) for obj in scene.objects if hasattr(obj, "color")}

    if pass_name == "depth":
        shading.color_type = "OBJECT"
        shading.light = "FLAT"
        shading.show_shadows = False
        for obj in scene.objects:
            if obj.type == "MESH":
                distance = min(1.0, max(0.08, (obj.location - camera.location).length / 55.0))
                value = 1.0 - distance
                obj.color = (value, value, value, 1.0)
    bpy.ops.render.render(write_still=True)

    for name, color in original_colors.items():
        if name in scene.objects:
            scene.objects[name].color = color
    shading.color_type = original_color_type
    shading.light = original_light
    shading.show_shadows = True


def main() -> None:
    args = parse_args()
    output = Path(args.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    reset_scene()
    add_environment()
    desktop, mobile = configure_scene()
    bpy.ops.wm.save_as_mainfile(filepath=str(output / "carrier-scene.blend"))
    for prefix, camera, size in (
        ("desktop", desktop, (1536, 864)),
        ("mobile", mobile, (944, 1792)),
    ):
        for pass_name in ("color", "depth"):
            render_pass(output / f"{prefix}-{pass_name}.png", camera, size, pass_name)
        subprocess.run(
            [
                "magick",
                str(output / f"{prefix}-color.png"),
                "-colorspace",
                "Gray",
                "-canny",
                "0x1+8%+22%",
                str(output / f"{prefix}-canny.png"),
            ],
            check=True,
        )
    print(f"saved={output}")


if __name__ == "__main__":
    main()
