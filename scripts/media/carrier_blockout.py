"""Build deterministic V12 carrier-scene guides for image generation."""

from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Matrix, Vector


COLORS = {
    "ground": (0.64, 0.68, 0.47, 1.0),
    "road": (0.17, 0.2, 0.22, 1.0),
    "line": (0.92, 0.88, 0.7, 1.0),
    "warehouse": (0.03, 0.24, 0.52, 1.0),
    "warehouse_light": (0.55, 0.68, 0.72, 1.0),
    "old": (0.25, 0.32, 0.34, 1.0),
    "near": (0.16, 0.49, 0.62, 1.0),
    "crew": (0.02, 0.25, 0.55, 1.0),
    "orange": (0.96, 0.31, 0.04, 1.0),
    "skin": (0.68, 0.4, 0.24, 1.0),
    "glass": (0.09, 0.23, 0.3, 1.0),
    "concrete": (0.5, 0.52, 0.5, 1.0),
    "building_blue": (0.22, 0.36, 0.49, 1.0),
    "building_ochre": (0.52, 0.34, 0.18, 1.0),
    "building_grey": (0.4, 0.43, 0.43, 1.0),
    "leaf_green": (0.27, 0.39, 0.17, 1.0),
    "leaf_ochre": (0.68, 0.4, 0.1, 1.0),
    "warm": (1.0, 0.66, 0.25, 1.0),
}


@dataclass(frozen=True)
class Road:
    id: str
    position: tuple[float, float]
    half_width: float
    half_length: float
    angle: float


@dataclass(frozen=True)
class Truck:
    position: tuple[float, float]
    angle: float
    road_id: str
    outcome: str
    old: bool = False
    drivers: int = 1
    nearest_to_warehouse: bool = False


ROAD_LAYOUT = (
    Road("north-branch", (0.0, 16.0), 2.7, 28.0, math.pi / 2),
    Road("dock-apron", (0.0, 2.0), 3.2, 29.0, math.pi / 2),
    Road("main-arterial", (0.0, -12.0), 3.8, 31.0, math.pi / 2),
    Road("south-branch", (0.0, -28.0), 2.9, 28.0, math.pi / 2),
    Road("west-link", (-20.0, -6.0), 2.6, 22.0, 0.0),
    Road("central-link", (0.0, -6.0), 2.6, 22.0, 0.0),
    Road("east-link", (20.0, -6.0), 2.7, 22.0, 0.0),
    Road("gate-loop", (12.0, 8.0), 2.3, 8.0, 0.0),
)

TRUCK_LAYOUT = {
    "truck-1": Truck((-20.0, -2.0), 0.0, "west-link", "old", old=True),
    "truck-2": Truck((8.0, 2.0), math.pi / 2, "dock-apron", "near", nearest_to_warehouse=True),
    "truck-3": Truck((-7.0, -12.0), math.pi / 2, "main-arterial", "crew", drivers=2),
    "truck-4": Truck((16.0, -28.0), math.pi / 2, "south-branch", "old", old=True),
}

URBAN_BLOCKS = (
    (-27.0, 25.0, 5.5, 5.5, 8.0, "building_grey"),
    (-13.0, 27.0, 5.0, 4.5, 11.0, "building_ochre"),
    (4.0, 27.0, 6.0, 4.8, 14.0, "building_blue"),
    (24.0, 27.0, 6.0, 5.0, 10.0, "building_grey"),
    (-29.0, 7.0, 5.5, 4.5, 13.0, "building_blue"),
    (29.0, 8.0, 5.0, 5.0, 12.0, "building_ochre"),
    (-30.0, -10.0, 5.0, 5.0, 9.0, "building_ochre"),
    (30.0, -10.0, 5.5, 5.0, 14.0, "building_blue"),
    (-29.0, -27.0, 5.0, 5.0, 12.0, "building_grey"),
    (-12.0, -28.0, 4.5, 5.0, 9.0, "building_blue"),
    (7.0, -29.0, 5.0, 4.5, 11.0, "building_ochre"),
    (29.0, -29.0, 5.5, 5.0, 13.0, "building_grey"),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--manifest")
    parser.add_argument("--skip-render", action="store_true")
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


def material(name: str) -> bpy.types.Material:
    result = bpy.data.materials.get(name)
    if result is None:
        result = bpy.data.materials.new(name)
        result.diffuse_color = COLORS[name]
        result.roughness = 0.76
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
    bevel: float = 0.1,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(location=location, rotation=(0, 0, rotation_z))
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material(color))
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
    rotation: tuple[float, float, float] = (0, 0, 0),
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=20,
        radius=radius,
        depth=depth,
        location=location,
        rotation=rotation,
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(material(color))
    obj.color = COLORS[color]
    move_to_collection(obj, target)
    return obj


def add_road(road: Road, target: bpy.types.Collection) -> None:
    cube(
        road.id,
        (*road.position, 0.08),
        (road.half_width, road.half_length, 0.12),
        "road",
        target,
        road.angle,
        bevel=0.16,
    )
    for index in range(-8, 9):
        local = Vector((0, index * road.half_length / 8, 0))
        local.rotate(Matrix.Rotation(road.angle, 4, "Z"))
        cube(
            f"{road.id}-dash-{index}",
            (road.position[0] + local.x, road.position[1] + local.y, 0.22),
            (0.08, 0.72, 0.025),
            "line",
            target,
            road.angle,
            bevel=0.01,
        )


def add_truck(name: str, truck: Truck, target: bpy.types.Collection) -> None:
    x, y = truck.position
    forward = Vector((0, 1, 0))
    forward.rotate(Matrix.Rotation(truck.angle, 4, "Z"))
    side = Vector((1, 0, 0))
    side.rotate(Matrix.Rotation(truck.angle, 4, "Z"))

    def at(longitudinal: float, lateral: float, z: float) -> tuple[float, float, float]:
        point = Vector((x, y, 0)) + forward * longitudinal + side * lateral
        return point.x, point.y, z

    color = "old" if truck.old else "near" if truck.outcome == "near" else "crew"
    if truck.old:
        cube(f"{name}-bed", at(-0.8, 0, 0.72), (1.25, 1.85, 0.3), "building_ochre", target, truck.angle, 0.05)
        cube(f"{name}-load", at(-0.9, 0, 1.35), (1.12, 1.55, 0.58), color, target, truck.angle, 0.3)
    else:
        cube(f"{name}-box", at(-0.75, 0, 1.35), (1.25, 2.0, 1.22), color, target, truck.angle, 0.18)
    cube(f"{name}-cab", at(1.65, 0, 1.0), (1.18, 0.7, 0.92), color, target, truck.angle, 0.24)
    cube(f"{name}-glass", at(2.35, 0, 1.25), (1.02, 0.06, 0.48), "glass", target, truck.angle, 0.03)
    for lateral in (-0.82, 0.82):
        for longitudinal in (-1.35, 1.5):
            cylinder(
                f"{name}-wheel-{lateral}-{longitudinal}",
                at(longitudinal, lateral, 0.4),
                0.4,
                0.24,
                "road",
                target,
                rotation=(math.pi / 2, 0, truck.angle),
            )
    driver_offsets = (0.0,) if truck.drivers == 1 else (-0.42, 0.42)
    for index, lateral in enumerate(driver_offsets, 1):
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=16,
            ring_count=10,
            radius=0.23,
            location=at(2.28, lateral, 1.3),
        )
        head = bpy.context.object
        head.name = f"{name}-driver-{index}"
        head.data.materials.append(material("skin"))
        head.color = COLORS["skin"]
        move_to_collection(head, target)


def add_urban_block(index: int, data: tuple, target: bpy.types.Collection) -> None:
    x, y, half_width, half_depth, height, color = data
    cube(
        f"UrbanBlock-{index}",
        (x, y, height / 2),
        (half_width, half_depth, height / 2),
        color,
        target,
        bevel=0.16,
    )
    cube(
        f"UrbanRoof-{index}",
        (x, y, height + 0.25),
        (half_width + 0.2, half_depth + 0.2, 0.24),
        "concrete",
        target,
        bevel=0.08,
    )
    for row in range(2):
        for column in (-0.55, 0.0, 0.55):
            cube(
                f"UrbanWindow-{index}-{row}-{column}",
                (x + column * half_width, y - half_depth - 0.05, 2.2 + row * 2.4),
                (0.48, 0.06, 0.55),
                "warm",
                target,
                bevel=0.02,
            )


def add_tree(name: str, position: tuple[float, float], target: bpy.types.Collection, ochre: bool) -> None:
    x, y = position
    cylinder(f"{name}-trunk", (x, y, 0.8), 0.12, 1.6, "building_ochre", target)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1.2, location=(x, y, 2.2))
    crown = bpy.context.object
    crown.name = f"{name}-crown"
    leaf = "leaf_ochre" if ochre else "leaf_green"
    crown.data.materials.append(material(leaf))
    crown.color = COLORS[leaf]
    crown.scale = (0.8, 0.9, 1.25)
    move_to_collection(crown, target)


def roads_connected() -> bool:
    def intersects(first: Road, second: Road) -> bool:
        first_horizontal = abs(math.sin(first.angle)) > 0.5
        second_horizontal = abs(math.sin(second.angle)) > 0.5
        if first_horizontal == second_horizontal:
            if first_horizontal:
                return abs(first.position[1] - second.position[1]) <= first.half_width + second.half_width and abs(first.position[0] - second.position[0]) <= first.half_length + second.half_length
            return abs(first.position[0] - second.position[0]) <= first.half_width + second.half_width and abs(first.position[1] - second.position[1]) <= first.half_length + second.half_length
        horizontal, vertical = (first, second) if first_horizontal else (second, first)
        return abs(vertical.position[0] - horizontal.position[0]) <= horizontal.half_length + vertical.half_width and abs(horizontal.position[1] - vertical.position[1]) <= vertical.half_length + horizontal.half_width

    seen = {0}
    frontier = [0]
    while frontier:
        current = frontier.pop()
        for index, road in enumerate(ROAD_LAYOUT):
            if index not in seen and intersects(ROAD_LAYOUT[current], road):
                seen.add(index)
                frontier.append(index)
    return len(seen) == len(ROAD_LAYOUT)


def add_environment() -> dict[str, int]:
    environment = collection("Environment")
    warehouse = collection("Warehouse")
    cube("EarlyAutumnGround", (0, -4, -0.45), (42, 48, 0.45), "ground", environment, bevel=0)
    for road in ROAD_LAYOUT:
        add_road(road, environment)

    for index, block in enumerate(URBAN_BLOCKS):
        add_urban_block(index, block, environment)

    cube("WarehouseApron", (0, 8.0, 0.12), (15.5, 7.2, 0.12), "concrete", warehouse, bevel=0.1)
    cube("WarehouseBody", (0, 12.0, 4.2), (14.0, 5.5, 4.2), "warehouse", warehouse, bevel=0.2)
    cube("WarehouseRoof", (0, 12.0, 8.65), (14.4, 5.9, 0.28), "warehouse_light", warehouse, bevel=0.14)
    cube("WarehouseOffice", (-10.5, 6.6, 4.0), (3.2, 2.0, 4.0), "warehouse_light", warehouse, bevel=0.15)
    for index, x in enumerate((-10.5, -7.0, -3.5, 0.0, 3.5, 7.0, 10.5), 1):
        cube(f"LoadingBay-{index}", (x, 6.43, 1.75), (1.25, 0.16, 1.75), "road", warehouse, bevel=0.04)
        cube(f"LoadingBayFrame-{index}", (x, 6.2, 3.62), (1.42, 0.1, 0.11), "orange", warehouse, bevel=0.03)
        cube(f"DockBumper-{index}", (x, 6.14, 0.6), (0.12, 0.12, 0.6), "orange", warehouse, bevel=0.02)
    cube("GateHouse", (15.2, 4.5, 1.4), (1.2, 1.0, 1.4), "warehouse_light", warehouse, bevel=0.12)
    cube("GateBarrier", (12.8, 3.3, 0.8), (2.3, 0.08, 0.08), "orange", warehouse, bevel=0.02)
    cylinder("GateScanner", (15.2, 2.8, 2.1), 0.12, 4.2, "road", warehouse)

    tree_positions = (
        (-36, 31), (-34, 18), (-36, 1), (-35, -18), (-34, -37),
        (-22, 34), (-7, 35), (10, 35), (24, 35), (36, 29),
        (35, 15), (36, -1), (35, -18), (34, -37), (-6, -40), (14, -41),
    )
    for index, position in enumerate(tree_positions):
        add_tree(f"Tree-{index}", position, environment, ochre=index % 3 == 0)

    for name, truck in TRUCK_LAYOUT.items():
        add_truck(name, truck, collection(name))

    return {
        "loading_bays": 7,
        "trees": len(tree_positions),
        "snowbanks": 0,
        "decorative_vehicles": 0,
        "express_vehicles": 0,
    }


def point_camera(camera: bpy.types.Object, target: tuple[float, float, float]) -> None:
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()


def create_camera(name: str, location: tuple[float, float, float], target: tuple[float, float, float], ortho_scale: float) -> bpy.types.Object:
    data = bpy.data.cameras.new(name)
    data.type = "ORTHO"
    data.ortho_scale = ortho_scale
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
    scene.world.color = (0.78, 0.8, 0.7)
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.resolution_percentage = 100
    desktop = create_camera("CameraDesktop", (42, -70, 130), (0, -6, 0), 84)
    mobile = create_camera("CameraMobile", (28, -72, 155), (0, -5, 0), 104)
    bpy.context.view_layer.update()
    return desktop, mobile


def visibility_fraction(camera: bpy.types.Object, objects: list[bpy.types.Object]) -> float:
    scene = bpy.context.scene
    depsgraph = bpy.context.evaluated_depsgraph_get()
    target_objects = set(objects)
    visible = 0
    mesh_objects = [obj for obj in objects if obj.type == "MESH"]
    for obj in mesh_objects:
        target = obj.matrix_world.translation
        origin = camera.matrix_world.translation
        direction = target - origin
        distance = direction.length + 0.5
        direction.normalize()
        hit, _, _, _, hit_object, _ = scene.ray_cast(depsgraph, origin, direction, distance=distance)
        if hit and hit_object in target_objects:
            visible += 1
    return visible / max(1, len(mesh_objects))


def object_bounds(camera: bpy.types.Object, objects: list[bpy.types.Object], size: tuple[int, int]) -> tuple[list[float], bool]:
    scene = bpy.context.scene
    scene.render.resolution_x, scene.render.resolution_y = size
    points = [
        world_to_camera_view(scene, camera, obj.matrix_world @ Vector(corner))
        for obj in objects
        if obj.type == "MESH"
        for corner in obj.bound_box
    ]
    bounds = [
        min(point.x for point in points),
        min(point.y for point in points),
        max(point.x for point in points),
        max(point.y for point in points),
    ]
    in_frame = all(point.z > 0 for point in points) and bounds[0] >= 0.01 and bounds[1] >= 0.01 and bounds[2] <= 0.99 and bounds[3] <= 0.99
    return [round(value, 4) for value in bounds], in_frame


def viewport_manifest(camera: bpy.types.Object, size: tuple[int, int]) -> dict:
    warehouse_objects = list(bpy.data.collections["Warehouse"].objects)
    trucks = {}
    for name in TRUCK_LAYOUT:
        objects = list(bpy.data.collections[name].objects)
        bounds, in_frame = object_bounds(camera, objects, size)
        fraction = visibility_fraction(camera, objects)
        trucks[name] = {"bounds": bounds, "visible": in_frame and fraction >= 0.7, "visible_fraction": round(fraction, 4)}
    return {
        "size": list(size),
        "landmarks": {"warehouse": {"visible_fraction": round(visibility_fraction(camera, warehouse_objects), 4)}},
        "trucks": trucks,
    }


def write_manifest(path: Path, props: dict[str, int], cameras: dict[str, tuple[bpy.types.Object, tuple[int, int]]]) -> None:
    payload = {
        "season": "early-autumn",
        "setting": "metropolitan-logistics-centre",
        "roads": [road.__dict__ for road in ROAD_LAYOUT],
        "buildings": [list(block) for block in URBAN_BLOCKS],
        "trucks": {
            name: {
                "position": truck.position,
                "angle": truck.angle,
                "road_id": truck.road_id,
                "outcome": truck.outcome,
                "drivers": truck.drivers,
                "nearest_to_warehouse": truck.nearest_to_warehouse,
            }
            for name, truck in TRUCK_LAYOUT.items()
        },
        "props": props,
        "network_connected": roads_connected(),
        "viewports": {name: viewport_manifest(camera, size) for name, (camera, size) in cameras.items()},
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n")


def render_pass(output: Path, camera: bpy.types.Object, size: tuple[int, int], depth: bool = False) -> None:
    scene = bpy.context.scene
    scene.camera = camera
    scene.render.resolution_x, scene.render.resolution_y = size
    scene.render.filepath = str(output)
    shading = scene.display.shading
    original_color_type = shading.color_type
    original_light = shading.light
    original_shadows = shading.show_shadows
    original_colors = {obj.name: tuple(obj.color) for obj in scene.objects if hasattr(obj, "color")}
    if depth:
        shading.color_type = "OBJECT"
        shading.light = "FLAT"
        shading.show_shadows = False
        for obj in scene.objects:
            if obj.type == "MESH":
                value = 1.0 - min(0.92, max(0.08, (obj.location - camera.location).length / 150.0))
                obj.color = (value, value, value, 1.0)
    bpy.ops.render.render(write_still=True)
    for name, color in original_colors.items():
        if name in scene.objects:
            scene.objects[name].color = color
    shading.color_type = original_color_type
    shading.light = original_light
    shading.show_shadows = original_shadows


def render_id_masks(output: Path, camera: bpy.types.Object, size: tuple[int, int]) -> None:
    scene = bpy.context.scene
    original_transparent = scene.render.film_transparent
    original_mode = scene.render.image_settings.color_mode
    scene.render.film_transparent = True
    scene.render.image_settings.color_mode = "RGBA"
    for name in TRUCK_LAYOUT:
        for target in TRUCK_LAYOUT:
            bpy.data.collections[target].hide_render = target != name
        bpy.data.collections["Environment"].hide_render = True
        bpy.data.collections["Warehouse"].hide_render = True
        render_pass(output / f"{name}-id.png", camera, size)
    for target in TRUCK_LAYOUT:
        bpy.data.collections[target].hide_render = False
    bpy.data.collections["Environment"].hide_render = False
    bpy.data.collections["Warehouse"].hide_render = False
    scene.render.film_transparent = original_transparent
    scene.render.image_settings.color_mode = original_mode


def main() -> None:
    args = parse_args()
    output = Path(args.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    reset_scene()
    props = add_environment()
    desktop, mobile = configure_scene()
    cameras = {
        "desktop": (desktop, (2880, 1800)),
        "mobile": (mobile, (780, 1688)),
    }
    if args.manifest:
        write_manifest(Path(args.manifest).resolve(), props, cameras)
    bpy.ops.wm.save_as_mainfile(filepath=str(output / "carrier-v12-scene.blend"))
    if args.skip_render:
        print(f"validated={output}")
        return
    for prefix, (camera, size) in cameras.items():
        render_pass(output / f"{prefix}-color.png", camera, size)
        render_pass(output / f"{prefix}-depth.png", camera, size, depth=True)
        subprocess.run(
            ["magick", str(output / f"{prefix}-color.png"), "-colorspace", "Gray", "-canny", "0x1+8%+22%", str(output / f"{prefix}-canny.png")],
            check=True,
        )
        mask_dir = output / f"{prefix}-truck-masks"
        mask_dir.mkdir(exist_ok=True)
        render_id_masks(mask_dir, camera, size)
    subprocess.run(
        [
            "magick",
            "montage",
            str(output / "desktop-color.png"),
            str(output / "mobile-color.png"),
            "-thumbnail",
            "720x450",
            "-tile",
            "2x1",
            "-geometry",
            "+16+16",
            str(output / "geometry-contact-sheet.png"),
        ],
        check=True,
    )
    print(f"saved={output}")


if __name__ == "__main__":
    main()
