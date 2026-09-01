"""Build deterministic carrier-scene guides for whole-frame image generation."""

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
    "snow": (0.84, 0.91, 0.96, 1.0),
    "road": (0.16, 0.20, 0.25, 1.0),
    "warehouse": (0.02, 0.22, 0.55, 1.0),
    "old": (0.24, 0.34, 0.40, 1.0),
    "near": (0.24, 0.50, 0.66, 1.0),
    "crew": (0.02, 0.24, 0.55, 1.0),
    "express": (1.0, 0.20, 0.02, 1.0),
    "orange": (1.0, 0.32, 0.02, 1.0),
    "skin": (0.63, 0.33, 0.18, 1.0),
    "glass": (0.12, 0.28, 0.38, 1.0),
    "building": (0.48, 0.38, 0.29, 1.0),
    "building_blue": (0.15, 0.38, 0.55, 1.0),
    "building_red": (0.55, 0.20, 0.12, 1.0),
    "wood": (0.42, 0.29, 0.19, 1.0),
    "warm": (1.0, 0.55, 0.16, 1.0),
}


@dataclass(frozen=True)
class TownDistrict:
    position: tuple[float, float]
    angle: float
    road_id: str


@dataclass(frozen=True)
class Road:
    id: str
    position: tuple[float, float]
    half_width: float
    half_length: float
    angle: float


@dataclass(frozen=True)
class Building:
    position: tuple[float, float]
    half_width: float
    half_depth: float
    wall_height: float
    color: str
    ridge_y: bool = True


ROAD_LAYOUT = (
    Road("north-service", (0.0, 16.0), 2.4, 25.0, math.pi / 2),
    Road("main-avenue", (0.0, -4.0), 3.0, 25.0, math.pi / 2),
    Road("south-arterial", (0.0, -16.0), 3.2, 25.0, math.pi / 2),
    Road("west-street", (-18.0, 1.0), 2.4, 15.0, 0.0),
    Road("central-street", (0.0, 1.0), 2.5, 15.0, 0.0),
    Road("east-street", (14.0, 1.0), 2.5, 15.0, 0.0),
    Road("warehouse-spur", (13.5, 8.0), 2.3, 3.5, math.pi / 2),
    Road("crew-street", (-8.0, -7.0), 2.8, 9.0, 0.0),
)

CARRIER_LAYOUT = {
    "old": TownDistrict((-6.0, 16.0), math.pi / 2, "north-service"),
    "near": TownDistrict((14.0, 0.0), math.pi, "east-street"),
    "crew": TownDistrict((-8.0, -5.0), math.pi, "crew-street"),
    "express": TownDistrict((13.0, -16.0), math.pi / 2, "south-arterial"),
}

BUILDING_LAYOUT = (
    Building((-28, 21), 3.0, 3.2, 4.8, "wood"),
    Building((-15, 23), 3.7, 3.0, 6.2, "building", False),
    Building((-3, 21), 3.0, 3.1, 4.5, "building"),
    Building((10, 21), 3.5, 3.0, 5.8, "building_red", False),
    Building((22, 23), 3.2, 3.1, 4.6, "wood"),
    Building((-27, 8), 3.1, 3.0, 4.4, "wood", False),
    Building((-16, 7), 3.8, 3.1, 5.5, "building"),
    Building((28, 9), 3.2, 3.0, 4.6, "wood", False),
    Building((-29, -7), 3.6, 3.0, 5.8, "building_red"),
    Building((-12, -7), 3.1, 3.0, 4.5, "wood", False),
    Building((23, -7), 3.7, 3.1, 5.6, "building"),
    Building((28, -7), 3.1, 3.0, 4.4, "building"),
    Building((-28, -21), 3.3, 3.2, 4.7, "building"),
    Building((-14, -21), 3.8, 3.0, 5.9, "building_red", False),
    Building((2, -22), 3.1, 3.0, 4.5, "wood"),
    Building((20, -22), 4.0, 3.2, 5.7, "wood", False),
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
    if old:
        cube(f"{name}-flatbed", at(-0.7 * s, 0, 0.72 * s), (1.35 * s, 1.8 * s, 0.32 * s), "wood", target, angle, bevel=0.06 * s)
        cube(f"{name}-tarp", at(-0.72 * s, 0, 1.38 * s), (1.2 * s, 1.55 * s, 0.58 * s), color, target, angle, bevel=0.38 * s)
    else:
        cube(f"{name}-box", at(-0.65 * s, 0, 1.25 * s), (1.25 * s, 1.75 * s, 1.15 * s), color, target, angle)
    cube(f"{name}-cab", at(1.52 * s, 0, 0.9 * s), (1.22 * s, 0.62 * s, 0.88 * s), color, target, angle, bevel=0.24 * s)
    cube(f"{name}-windshield", at(2.18 * s, 0, 1.12 * s), (1.08 * s, 0.07 * s, 0.5 * s), "glass", target, angle, bevel=0.03)
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
            location=at(2.12 * s, lateral * s, 1.2 * s),
        )
        head = bpy.context.object
        head.name = f"{name}-driver-{index}"
        head.data.materials.append(material("Mat-skin", COLORS["skin"]))
        head.color = COLORS["skin"]
        move_to_collection(head, target)
    if old:
        cube(f"{name}-old-bumper", at(2.22 * s, 0, 0.38 * s), (1.18 * s, 0.12 * s, 0.1 * s), "near", target, angle, bevel=0.02)


def add_van(
    name: str,
    position: tuple[float, float],
    angle: float,
    color: str,
    target: bpy.types.Collection,
    *,
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
    cube(f"{name}-body", at(-0.2 * s, 0, 0.85 * s), (0.92 * s, 1.65 * s, 0.82 * s), color, target, angle, bevel=0.32 * s)
    cube(f"{name}-nose", at(1.48 * s, 0, 0.62 * s), (0.9 * s, 0.38 * s, 0.55 * s), color, target, angle, bevel=0.24 * s)
    cube(f"{name}-windshield", at(1.87 * s, 0, 0.9 * s), (0.76 * s, 0.04 * s, 0.32 * s), "glass", target, angle, bevel=0.03 * s)
    for lateral in (-0.66 * s, 0.66 * s):
        for longitudinal in (-0.85 * s, 1.05 * s):
            cylinder(
                f"{name}-wheel",
                at(longitudinal, lateral, 0.3 * s),
                0.3 * s,
                0.2 * s,
                "road",
                target,
                rotation=(math.pi / 2, 0, angle),
            )


def add_express_truck(
    position: tuple[float, float],
    angle: float,
    target: bpy.types.Collection,
    *,
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
    cube("ExpressTruck-body", at(-0.55 * s, 0, 1.05 * s), (1.08 * s, 1.85 * s, 0.95 * s), "express", target, angle, bevel=0.34 * s)
    cube("ExpressTruck-cab", at(1.58 * s, 0, 0.78 * s), (1.0 * s, 0.72 * s, 0.72 * s), "express", target, angle, bevel=0.38 * s)
    cube("ExpressTruck-windshield", at(2.33 * s, 0, 0.98 * s), (0.82 * s, 0.05 * s, 0.37 * s), "glass", target, angle, bevel=0.04 * s)
    cube("ExpressTruck-roof-band", at(-0.4 * s, 0, 1.98 * s), (1.0 * s, 1.72 * s, 0.08 * s), "warm", target, angle, bevel=0.06 * s)

    bpy.ops.object.text_add(location=at(-0.55 * s, -1.1 * s, 1.18 * s))
    wordmark = bpy.context.object
    wordmark.name = "ExpressTruck-wordmark"
    wordmark.data.body = "Express"
    wordmark.data.align_x = "CENTER"
    wordmark.data.align_y = "CENTER"
    wordmark.data.size = 0.72 * s
    wordmark.data.extrude = 0.025
    wordmark.data.materials.append(material("Mat-snow", COLORS["snow"]))
    wordmark.rotation_euler = (math.pi / 2, 0, 0)
    move_to_collection(wordmark, target)

    for lateral in (-0.78 * s, 0.78 * s):
        for longitudinal in (-1.25 * s, 1.35 * s):
            cylinder(
                "ExpressTruck-wheel",
                at(longitudinal, lateral, 0.34 * s),
                0.35 * s,
                0.22 * s,
                "road",
                target,
                rotation=(math.pi / 2, 0, angle),
            )


def add_gable_roof(name, building, target):
    # Pitched geometry gives img2img real roof planes instead of asking it to invent them.
    x, y = building.position
    width = building.half_width + 0.35
    depth = building.half_depth + 0.35
    eave = building.wall_height + 0.1
    ridge = eave + min(width, depth) * 0.68
    if building.ridge_y:
        vertices = [
            (x - width, y - depth, eave), (x + width, y - depth, eave), (x, y - depth, ridge),
            (x - width, y + depth, eave), (x + width, y + depth, eave), (x, y + depth, ridge),
        ]
    else:
        vertices = [
            (x - width, y - depth, eave), (x - width, y + depth, eave), (x - width, y, ridge),
            (x + width, y - depth, eave), (x + width, y + depth, eave), (x + width, y, ridge),
        ]
    faces = [(0, 1, 2), (3, 5, 4), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)]
    mesh = bpy.data.meshes.new(f"{name}-mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.append(material("Mat-snow", COLORS["snow"]))
    roof = bpy.data.objects.new(name, mesh)
    target.objects.link(roof)


def add_house(index: int, building: Building, target: bpy.types.Collection) -> None:
    x, y = building.position
    cube(
        f"TownBuilding-{index}",
        (x, y, building.wall_height / 2),
        (building.half_width, building.half_depth, building.wall_height / 2),
        building.color,
        target,
        bevel=0.12,
    )
    add_gable_roof(f"TownRoof-{index}", building, target)
    window_rows = 2 if building.wall_height >= 5.4 else 1
    for row in range(window_rows):
        z = 1.45 + row * 2.15
        for offset in (-building.half_width * 0.52, building.half_width * 0.52):
            cube(
                f"TownWindow-{index}-{row}-{offset}",
                (x + offset, y - building.half_depth - 0.05, z),
                (0.48, 0.07, 0.42),
                "warm",
                target,
                bevel=0.03,
            )
    cube(
        f"TownDoor-{index}",
        (x, y - building.half_depth - 0.07, 0.9),
        (0.48, 0.08, 0.9),
        "road",
        target,
        bevel=0.03,
    )


def add_lamp(name: str, position: tuple[float, float], target: bpy.types.Collection) -> None:
    x, y = position
    cylinder(name, (x, y, 1.8), 0.09, 3.6, "road", target, rotation=(0, 0, 0))
    cube(f"{name}-light", (x, y, 3.7), (0.28, 0.28, 0.22), "warm", target, bevel=0.08)


def add_conifer(name: str, position: tuple[float, float], target: bpy.types.Collection) -> None:
    x, y = position
    cylinder(f"{name}-trunk", (x, y, 0.8), 0.13, 1.6, "wood", target, rotation=(0, 0, 0))
    for index, (z, radius) in enumerate(((1.4, 1.2), (2.2, 0.95), (2.9, 0.65))):
        bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=radius, radius2=0.0, depth=1.7, location=(x, y, z))
        cone = bpy.context.object
        cone.name = f"{name}-snow-tier-{index}"
        cone.data.materials.append(material("Mat-snow", COLORS["snow"]))
        move_to_collection(cone, target)


def add_snowbank(name: str, position: tuple[float, float], scale: tuple[float, float], target: bpy.types.Collection) -> None:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, location=(position[0], position[1], 0.28))
    bank = bpy.context.object
    bank.name = name
    bank.scale = (scale[0], scale[1], 0.42)
    bank.data.materials.append(material("Mat-snow", COLORS["snow"]))
    move_to_collection(bank, target)


def add_mountain(
    name: str,
    position: tuple[float, float],
    width: float,
    height: float,
    target: bpy.types.Collection,
) -> None:
    bpy.ops.mesh.primitive_cone_add(
        vertices=7,
        radius1=width,
        radius2=0,
        depth=height,
        location=(position[0], position[1], height / 2),
    )
    mountain = bpy.context.object
    mountain.name = name
    mountain.scale.y = 0.42
    mountain.data.materials.append(material("Mat-near", COLORS["near"]))
    move_to_collection(mountain, target)


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


def validate_layout() -> None:
    districts = list(CARRIER_LAYOUT.values())
    road_ids = {district.road_id for district in districts}
    if len(road_ids) != len(districts):
        raise ValueError("each carrier must occupy a distinct road")

    for index, first in enumerate(districts):
        for second in districts[index + 1 :]:
            distance = (Vector(first.position) - Vector(second.position)).length
            if distance < 7.0:
                raise ValueError(f"carrier centres are only {distance:.2f}m apart")

    road_angles = {road.id: road.angle for road in ROAD_LAYOUT}
    for name, district in CARRIER_LAYOUT.items():
        difference = abs((district.angle - road_angles[district.road_id] + math.pi) % (2 * math.pi) - math.pi)
        if min(difference, abs(math.pi - difference)) > math.radians(1):
            raise ValueError(f"{name} is not parallel to {district.road_id}")
    if not roads_connected():
        raise ValueError("road network must be connected")


def add_motion_cues(
    name: str,
    district: TownDistrict,
    target: bpy.types.Collection,
    plume_count: int,
) -> tuple[int, int]:
    forward = Vector((0, 1, 0))
    forward.rotate(Matrix.Rotation(district.angle, 4, "Z"))
    side = Vector((1, 0, 0))
    side.rotate(Matrix.Rotation(district.angle, 4, "Z"))
    origin = Vector((*district.position, 0))

    track_center = origin - forward * 4.0
    for index, lateral in enumerate((-0.72, 0.72)):
        point = track_center + side * lateral
        cube(
            f"{name}-motion-track-{index}",
            (point.x, point.y, 0.24),
            (0.07, 2.5, 0.025),
            "near",
            target,
            district.angle,
            bevel=0.01,
        )

    for index in range(plume_count):
        distance = 2.8 + index * 0.5
        lateral = ((index % 3) - 1) * 0.34
        point = origin - forward * distance + side * lateral
        bpy.ops.mesh.primitive_ico_sphere_add(
            subdivisions=2,
            radius=0.2 + index * 0.035,
            location=(point.x, point.y, 0.24 + index * 0.035),
        )
        plume = bpy.context.object
        plume.name = f"{name}-snow-plume-{index}"
        plume.scale = (1.15 + index * 0.04, 0.62, 0.48)
        plume.data.materials.append(material("Mat-snow", COLORS["snow"]))
        plume.color = COLORS["snow"]
        move_to_collection(plume, target)

    return 2, plume_count


def add_environment() -> dict[str, int]:
    environment = collection("Environment")
    warehouse = collection("Warehouse")
    cues = collection("CueProps")
    old_collection = collection("OldCarrier")
    near_collection = collection("NearCarrier")
    crew_collection = collection("CrewCarrier")
    express_collection = collection("ExpressCarrier")

    validate_layout()
    cube("SnowGround", (0, -10, -0.45), (45, 55, 0.45), "snow", environment, bevel=0.0)
    for road in ROAD_LAYOUT:
        add_road(
            road.id,
            (road.position[0], road.position[1], 0.08),
            (road.half_width, road.half_length, 0.13),
            road.angle,
            environment,
        )

    add_road("foreground-footpath", (0.0, -31.0, 0.02), (0.65, 31.0, 0.05), math.pi / 2, environment)

    # The warehouse dominates the mobile storyboard; no vehicle may rival its scale.
    warehouse_center = (8.0, 7.0)
    cube("WarehouseBody", (8.0, 7.0, 3.4), (7.2, 4.5, 3.4), "warehouse", warehouse, bevel=0.2)
    cube("WarehouseRoof", (8.0, 7.0, 7.05), (7.45, 4.75, 0.28), "snow", warehouse, bevel=0.18)
    cube("WarehouseRoofTrim", (8.0, 2.3, 6.35), (7.0, 0.16, 0.16), "orange", warehouse, bevel=0.04)
    cube("WarehouseYard", (8.0, 1.05, 0.12), (7.7, 2.2, 0.12), "road", warehouse, bevel=0.08)
    # Three south-facing loading bays establish a logistics destination, not a house.
    for index, x in enumerate((3.5, 8.0, 12.5), 1):
        gate_name = "LoadingGate" if index == 2 else f"LoadingGate-{index}"
        cube(gate_name, (x, 2.24, 1.55), (1.35, 0.16, 1.55), "road", warehouse, bevel=0.04)
        cube(f"LoadingGateFrame-{index}", (x, 2.0, 3.15), (1.55, 0.13, 0.12), "orange", warehouse, bevel=0.03)
        cube(f"LoadingBayLight-{index}", (x, 1.96, 3.58), (0.22, 0.12, 0.18), "warm", warehouse, bevel=0.04)
    cube("LoadingCanopy", (8.0, 1.72, 3.45), (7.05, 0.3, 0.16), "snow", warehouse, bevel=0.08)
    cube("WarehouseSign", (8.0, 1.98, 5.45), (2.6, 0.12, 0.78), "road", warehouse, bevel=0.08)
    cube("WarehouseSignAccent", (8.0, 1.82, 5.45), (0.9, 0.08, 0.42), "orange", warehouse, bevel=0.08)
    for x in (3.5, 8.0, 12.5):
        cube(f"WarehouseWindow-{x}", (x, 2.24, 4.75), (0.75, 0.08, 0.48), "warm", warehouse, bevel=0.03)
    for x in (2.5, 5.5, 10.5, 13.5):
        cube(f"DockBumper-{x}", (x, 1.98, 0.65), (0.12, 0.18, 0.65), "orange", warehouse, bevel=0.03)
    cylinder("WarehouseVent", (12.8, 7.0, 8.05), 0.3, 1.2, "near", warehouse, rotation=(0, 0, 0))

    for index, building in enumerate(BUILDING_LAYOUT):
        add_house(index, building, environment)

    old = CARRIER_LAYOUT["old"]
    near = CARRIER_LAYOUT["near"]
    crew = CARRIER_LAYOUT["crew"]
    express = CARRIER_LAYOUT["express"]
    add_truck("OldTruck", old.position, old.angle, "old", old_collection, old=True, scale_factor=1.0)
    add_van("NearVan", near.position, near.angle, "near", near_collection, scale_factor=1.5)
    add_truck("CrewTruck", crew.position, crew.angle, "crew", crew_collection, drivers=2, scale_factor=1.25)
    add_express_truck(express.position, express.angle, express_collection, scale_factor=1.0)

    motion_tracks = 0
    snow_plumes = 0
    for name, district, plume_count in (
        ("old", old, 2),
        ("near", near, 1),
        ("crew", crew, 3),
        ("express", express, 7),
    ):
        tracks, plumes = add_motion_cues(name, district, cues, plume_count)
        motion_tracks += tracks
        snow_plumes += plumes

    cube("InspectionBooth", (-13.0, 16.0, 1.1), (1.0, 1.0, 1.1), "building_blue", cues, bevel=0.12)
    cylinder("InspectionSign", (-11.5, 16.0, 1.55), 0.42, 0.08, "orange", cues, rotation=(0, math.pi / 2, 0))
    cube("GateBarrier", (13.8, 1.4, 0.78), (1.45, 0.08, 0.08), "orange", cues, bevel=0.02)
    cube("GateSnowBank", (14.0, 2.6, 0.4), (1.0, 1.35, 0.4), "snow", cues, bevel=0.3)

    lamp_positions = ((-25, 17.5), (-8, 17.5), (8, 17.5), (23, 17.5), (-25, 3.5), (3.5, 3.5), (16.5, -3.5), (-18, -17.5), (3, -17.5), (24, -17.5))
    for index, position in enumerate(lamp_positions):
        add_lamp(f"StreetLamp-{index}", position, cues)

    tree_positions = ((-35, 24), (-32, 14), (-34, 0), (-34, -15), (-31, -27), (-21, 27), (-8, 27), (6, 27), (19, 27), (33, 23), (35, 13), (35, -1), (34, -14), (31, -26), (12, -27), (-4, -27), (-24, -38), (-10, -42), (8, -39), (25, -43))
    for index, position in enumerate(tree_positions):
        add_conifer(f"Conifer-{index}", position, environment)

    snowbank_positions = ((-24, 11), (-10, 11), (5, 11), (17, 11), (-24, 3), (-10, 3), (8, 3), (23, 3), (-24, -10), (-9, -10), (5, -10), (22, -10), (-25, -17), (-8, -17), (12, -17), (27, -17), (-4, 17), (14, 17), (-20, -34), (-2, -36), (17, -35), (30, -38))
    for index, position in enumerate(snowbank_positions):
        add_snowbank(f"Snowbank-{index}", position, (1.5 + index % 3 * 0.35, 0.55 + index % 2 * 0.2), cues)

    mountain_positions = ((-28, 31, 10, 6), (-14, 33, 11, 8), (1, 32, 12, 7), (16, 33, 11, 9), (30, 31, 10, 6))
    for index, (x, y, width, height) in enumerate(mountain_positions):
        add_mountain(f"BackgroundMountain-{index}", (x, y), width, height, environment)

    return {
        "lamps": len(lamp_positions),
        "trees": len(tree_positions),
        "snowbanks": len(snowbank_positions),
        "mountains": len(mountain_positions),
        "motion_tracks": motion_tracks,
        "snow_plumes": snow_plumes,
        "express_wordmarks": 1,
    }


def point_camera(camera: bpy.types.Object, target: tuple[float, float, float]) -> None:
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()


def create_camera(
    name: str,
    location: tuple[float, float, float],
    target: tuple[float, float, float],
    lens: float,
    ortho_scale: float | None = None,
) -> bpy.types.Object:
    data = bpy.data.cameras.new(name)
    data.lens = lens
    data.sensor_width = 36
    camera = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(camera)
    camera.location = location
    if ortho_scale is not None:
        data.type = "ORTHO"
        data.ortho_scale = ortho_scale
    else:
        data.type = "PERSP"
    point_camera(camera, target)
    return camera


def configure_scene() -> tuple[bpy.types.Object, bpy.types.Object, bpy.types.Object]:
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
    # Perspective gives the master a real foreground/midground/background hierarchy.
    desktop = create_camera("CameraDesktop", (30.0, -90.0, 130.0), (2.0, 2.0, 2.0), 76)
    tablet = create_camera("CameraTablet", (34.0, -72.0, 92.0), (3.0, 4.0, 2.0), 52)
    mobile = create_camera("CameraMobile", (5.0, -74.0, 86.0), (5.0, 3.0, 1.5), 54)
    bpy.context.view_layer.update()
    return desktop, tablet, mobile


def visibility_fraction(
    camera: bpy.types.Object,
    objects: list[bpy.types.Object],
) -> float:
    scene = bpy.context.scene
    depsgraph = bpy.context.evaluated_depsgraph_get()
    target_objects = set(objects)
    mesh_objects = [obj for obj in objects if obj.type == "MESH"]
    visible_samples = 0
    for obj in mesh_objects:
        target = obj.matrix_world.translation
        if camera.data.type == "ORTHO":
            direction = camera.matrix_world.to_quaternion() @ Vector((0, 0, -1))
            origin = target - direction * 200.0
            distance = 400.0
        else:
            origin = camera.matrix_world.translation
            direction = target - origin
            distance = direction.length + 0.5
            direction.normalize()
        hit, _, _, _, hit_object, _ = scene.ray_cast(
            depsgraph, origin, direction, distance=distance
        )
        if hit and hit_object in target_objects:
            visible_samples += 1
    return visible_samples / max(1, len(mesh_objects))


def landmark_visibility(camera: bpy.types.Object) -> dict[str, dict[str, float]]:
    warehouse_objects = [
        bpy.data.objects[name]
        for name in (
            "WarehouseBody",
            "WarehouseRoof",
            "LoadingGate",
            "LoadingCanopy",
            "WarehouseWindow-3.5",
            "WarehouseWindow-8.0",
        )
    ]
    return {
        "warehouse": {
            "visible_fraction": round(visibility_fraction(camera, warehouse_objects), 4)
        },
        "loading_gate": {
            "visible_fraction": round(
                visibility_fraction(camera, [bpy.data.objects["LoadingGate"]]), 4
            )
        },
    }


def carrier_bounds(
    camera: bpy.types.Object,
    size: tuple[int, int],
) -> dict[str, dict[str, object]]:
    scene = bpy.context.scene
    scene.render.resolution_x, scene.render.resolution_y = size
    scene.render.resolution_percentage = 100
    bpy.context.view_layer.update()
    collection_names = {
        "old": "OldCarrier",
        "near": "NearCarrier",
        "crew": "CrewCarrier",
        "express": "ExpressCarrier",
    }
    result: dict[str, dict[str, object]] = {}
    margin = 0.01
    for carrier, collection_name in collection_names.items():
        points = []
        for obj in bpy.data.collections[collection_name].objects:
            if obj.type != "MESH":
                continue
            for corner in obj.bound_box:
                world = obj.matrix_world @ Vector(corner)
                points.append(world_to_camera_view(scene, camera, world))
        left = min(point.x for point in points)
        bottom = min(point.y for point in points)
        right = max(point.x for point in points)
        top = max(point.y for point in points)
        in_frame = (
            all(point.z > 0 for point in points)
            and left >= margin
            and bottom >= margin
            and right <= 1 - margin
            and top <= 1 - margin
        )

        target_objects = list(bpy.data.collections[collection_name].objects)
        visible_fraction = visibility_fraction(camera, target_objects)

        result[carrier] = {
            "bounds": [round(value, 4) for value in (left, bottom, right, top)],
            "visible": in_frame and visible_fraction >= 0.75,
            "visible_fraction": round(visible_fraction, 4),
        }
    return result


def write_manifest(
    path: Path,
    props: dict[str, int],
    cameras: dict[str, tuple[bpy.types.Object, tuple[int, int]]],
) -> None:
    payload = {
        "roads": [
            {"id": road.id, "position": road.position, "half_width": road.half_width, "half_length": road.half_length, "angle": road.angle}
            for road in ROAD_LAYOUT
        ],
        "buildings": [
            {"position": building.position, "size": [building.half_width, building.half_depth], "height": building.wall_height, "color": building.color}
            for building in BUILDING_LAYOUT
        ],
        "carriers": {
            name: {
                "position": district.position,
                "angle": district.angle,
                "road_id": district.road_id,
                "body_type": {
                    "old": "old-tarp-flatbed",
                    "near": "panel-van",
                    "crew": "high-box-crew",
                    "express": "streamlined-express",
                }[name],
            }
            for name, district in CARRIER_LAYOUT.items()
        },
        "props": props,
        "network_connected": roads_connected(),
        "viewports": {
            name: {
                "size": list(size),
                "landmarks": landmark_visibility(camera),
                "vehicles": carrier_bounds(camera, size),
            }
            for name, (camera, size) in cameras.items()
        },
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n")


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
    props = add_environment()
    desktop, tablet, mobile = configure_scene()
    cameras = {
        "desktop": (desktop, (1536, 864)),
        "tablet": (tablet, (1200, 1200)),
        "mobile": (mobile, (944, 1792)),
    }
    if args.manifest:
        write_manifest(Path(args.manifest).resolve(), props, cameras)
    bpy.ops.wm.save_as_mainfile(filepath=str(output / "carrier-scene.blend"))
    if args.skip_render:
        print(f"validated={output}")
        return
    for prefix, (camera, size) in cameras.items():
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
