# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "fal-client>=0.7.0",
#   "pillow>=11.0.0",
# ]
# ///

"""Generate and refine carrier-scene artwork through fal.ai."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from collections import deque
from pathlib import Path
from urllib.request import urlretrieve

import fal_client
from PIL import Image, ImageChops, ImageDraw, ImageFilter


def configure_credentials() -> None:
    if "FAL_KEY" not in os.environ and "FAL_API_KEY" in os.environ:
        os.environ["FAL_KEY"] = os.environ["FAL_API_KEY"]
    if not os.environ.get("FAL_KEY"):
        raise SystemExit("FAL_KEY or FAL_API_KEY is required")


def upload(path: str) -> str:
    return fal_client.upload_file(str(Path(path).resolve()))


def save_result(result: dict, output: Path, metadata: Path | None) -> None:
    image_url = result["images"][0]["url"]
    output.parent.mkdir(parents=True, exist_ok=True)
    urlretrieve(image_url, output)

    if metadata:
        metadata.parent.mkdir(parents=True, exist_ok=True)
        metadata.write_text(json.dumps(result, ensure_ascii=False, indent=2))

    print(f"saved={output}")
    print(f"seed={result.get('seed', 'not-returned')}")


def save_single_image_result(
    result: dict, output: Path, metadata: Path | None
) -> None:
    image_url = result["image"]["url"]
    output.parent.mkdir(parents=True, exist_ok=True)
    urlretrieve(image_url, output)

    if metadata:
        metadata.parent.mkdir(parents=True, exist_ok=True)
        metadata.write_text(json.dumps(result, ensure_ascii=False, indent=2))

    print(f"saved={output}")


def save_image_url(
    image_url: str, result: dict, output: Path, metadata: Path | None
) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    urlretrieve(image_url, output)
    if metadata:
        metadata.parent.mkdir(parents=True, exist_ok=True)
        metadata.write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"saved={output}")


def compose(args: argparse.Namespace) -> None:
    prompt = Path(args.prompt_file).read_text()
    result = fal_client.subscribe(
        "fal-ai/flux-2-pro/edit",
        arguments={
            "prompt": prompt,
            "image_urls": [upload(path) for path in args.reference],
            "image_size": {"width": args.width, "height": args.height},
            "seed": args.seed,
            "output_format": "png",
            "enable_safety_checker": True,
        },
    )
    save_result(result, Path(args.output), Path(args.metadata) if args.metadata else None)


def inpaint(args: argparse.Namespace) -> None:
    result = fal_client.subscribe(
        "fal-ai/qwen-image-edit/inpaint",
        arguments={
            "prompt": Path(args.prompt_file).read_text(),
            "image_url": upload(args.image),
            "mask_url": upload(args.mask),
            "image_size": {"width": args.width, "height": args.height},
            "num_inference_steps": args.steps,
            "guidance_scale": args.guidance,
            "seed": args.seed,
            "negative_prompt": args.negative_prompt,
            "output_format": "png",
            "enable_safety_checker": True,
        },
    )
    save_result(result, Path(args.output), Path(args.metadata) if args.metadata else None)


def outpaint(args: argparse.Namespace) -> None:
    result = fal_client.subscribe(
        "fal-ai/flux-2-pro/outpaint",
        arguments={
            "image_url": upload(args.image),
            "expand_top": args.top,
            "expand_bottom": args.bottom,
            "expand_left": args.left,
            "expand_right": args.right,
            "auto_crop": False,
            "mode": "high",
            "output_format": "png",
            "enable_safety_checker": True,
        },
    )
    save_result(result, Path(args.output), Path(args.metadata) if args.metadata else None)


def segment(args: argparse.Namespace) -> None:
    result = fal_client.subscribe(
        "fal-ai/evf-sam",
        arguments={
            "image_url": upload(args.image),
            "prompt": args.prompt,
            "negative_prompt": args.negative_prompt,
            "mask_only": True,
            "use_grounding_dino": True,
            "semantic_type": False,
            "fill_holes": True,
            "expand_mask": args.expand,
            "blur_mask": args.blur,
        },
    )
    save_single_image_result(
        result, Path(args.output), Path(args.metadata) if args.metadata else None
    )


def segment_box(args: argparse.Namespace) -> None:
    point_prompts = [
        {"x": point[0], "y": point[1], "label": 1, "object_id": 1}
        for point in args.positive_point
    ]
    point_prompts.extend(
        {"x": point[0], "y": point[1], "label": 0, "object_id": 1}
        for point in args.negative_point
    )
    result = fal_client.subscribe(
        "fal-ai/sam-3-1/image",
        arguments={
            "image_url": upload(args.image),
            "prompt": args.prompt,
            "point_prompts": point_prompts,
            "box_prompts": [
                {
                    "x_min": args.x_min,
                    "y_min": args.y_min,
                    "x_max": args.x_max,
                    "y_max": args.y_max,
                    "object_id": 1,
                }
            ],
            "apply_mask": args.apply_mask,
            "output_format": "png",
            "return_multiple_masks": True,
            "max_masks": 1,
            "include_scores": True,
            "include_boxes": True,
        },
    )
    images = result.get("masks") or [result["image"]]
    image = images[0]
    save_image_url(
        image["url"], result, Path(args.output), Path(args.metadata) if args.metadata else None
    )


def remove_object(args: argparse.Namespace) -> None:
    result = fal_client.subscribe(
        "fal-ai/object-removal/mask",
        arguments={
            "image_url": upload(args.image),
            "mask_url": upload(args.mask),
            "model": "best_quality",
            "mask_expansion": args.mask_expansion,
        },
    )
    save_result(
        result, Path(args.output), Path(args.metadata) if args.metadata else None
    )


def extract_layer(args: argparse.Namespace) -> None:
    source = Image.open(args.image).convert("RGBA")
    mask = Image.open(args.mask).convert("L").resize(source.size, Image.Resampling.NEAREST)
    if args.source_box:
        restricted = Image.new("L", source.size, 0)
        restricted.paste(mask.crop(tuple(args.source_box)), tuple(args.source_box[:2]))
        mask = restricted
    if args.threshold is not None:
        threshold = args.threshold
        mask = mask.point(lambda value: 255 if value >= threshold else 0)
    if args.largest_component:
        mask = keep_largest_component(mask)
    if args.invert:
        mask = ImageChops.invert(mask)
    if args.feather > 0:
        mask = mask.filter(ImageFilter.GaussianBlur(radius=args.feather))
    source.putalpha(mask)

    if args.crop:
        bounds = mask.getbbox()
        if bounds is None:
            raise SystemExit("Mask is empty")
        left = max(0, bounds[0] - args.padding)
        top = max(0, bounds[1] - args.padding)
        right = min(source.width, bounds[2] + args.padding)
        bottom = min(source.height, bounds[3] + args.padding)
        source = source.crop((left, top, right, bottom))

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    source.save(output)
    print(f"saved={output}")


def keep_largest_component(mask: Image.Image) -> Image.Image:
    bounds = mask.getbbox()
    if bounds is None:
        return mask

    crop = mask.crop(bounds).convert("L")
    width, height = crop.size
    pixels = bytearray(crop.tobytes())
    visited = bytearray(width * height)
    largest: list[int] = []

    for start, value in enumerate(pixels):
        if value == 0 or visited[start]:
            continue
        component: list[int] = []
        queue = deque([start])
        visited[start] = 1
        while queue:
            index = queue.popleft()
            component.append(index)
            x = index % width
            y = index // width
            for neighbor in (
                index - 1 if x > 0 else -1,
                index + 1 if x + 1 < width else -1,
                index - width if y > 0 else -1,
                index + width if y + 1 < height else -1,
            ):
                if neighbor >= 0 and pixels[neighbor] and not visited[neighbor]:
                    visited[neighbor] = 1
                    queue.append(neighbor)
        if len(component) > len(largest):
            largest = component

    cleaned = bytearray(width * height)
    for index in largest:
        cleaned[index] = 255
    cleaned_crop = Image.frombytes("L", (width, height), bytes(cleaned))
    result = Image.new("L", mask.size, 0)
    result.paste(cleaned_crop, bounds[:2])
    return result


def rectangle_mask(args: argparse.Namespace) -> None:
    source = Image.open(args.image)
    mask = Image.new("L", source.size, 0)
    draw = ImageDraw.Draw(mask)
    for box in args.box:
        draw.rounded_rectangle(tuple(box), radius=args.radius, fill=255)
    if args.blur > 0:
        mask = mask.filter(ImageFilter.GaussianBlur(radius=args.blur))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    mask.save(output)
    print(f"saved={output}")


def chunk_inpaint(args: argparse.Namespace) -> None:
    source = Image.open(args.image).convert("RGB")
    source_width, source_height = source.size
    left = max(0, args.x - args.padding)
    top = max(0, args.y - args.padding)
    right = min(source_width, args.x + args.width + args.padding)
    bottom = min(source_height, args.y + args.height + args.padding)

    crop = source.crop((left, top, right, bottom))
    crop_width, crop_height = crop.size
    scaled_size = (crop_width * args.scale, crop_height * args.scale)
    crop_scaled = crop.resize(scaled_size, Image.Resampling.LANCZOS)

    target_mask = Image.new("L", (crop_width, crop_height), 0)
    target_left = args.x - left
    target_top = args.y - top
    target_right = min(crop_width, target_left + args.width)
    target_bottom = min(crop_height, target_top + args.height)
    target_mask.paste(255, (target_left, target_top, target_right, target_bottom))
    model_mask = target_mask.resize(scaled_size, Image.Resampling.NEAREST)

    with tempfile.TemporaryDirectory(prefix="carrier-chunk-") as temp_directory:
        temp_path = Path(temp_directory)
        crop_path = temp_path / "crop.png"
        mask_path = temp_path / "mask.png"
        result_path = temp_path / "result.png"
        crop_scaled.save(crop_path)
        model_mask.save(mask_path)

        result = fal_client.subscribe(
            "fal-ai/qwen-image-edit/inpaint",
            arguments={
                "prompt": Path(args.prompt_file).read_text(),
                "image_url": upload(str(crop_path)),
                "mask_url": upload(str(mask_path)),
                "image_size": {"width": scaled_size[0], "height": scaled_size[1]},
                "num_inference_steps": args.steps,
                "guidance_scale": args.guidance,
                "seed": args.seed,
                "negative_prompt": args.negative_prompt,
                "output_format": "png",
                "enable_safety_checker": True,
            },
        )
        urlretrieve(result["images"][0]["url"], result_path)
        edited_crop = Image.open(result_path).convert("RGB").resize(
            (crop_width, crop_height), Image.Resampling.LANCZOS
        )

    blend_mask = target_mask.filter(ImageFilter.GaussianBlur(radius=args.feather))
    merged_crop = Image.composite(edited_crop, crop, blend_mask)
    source.paste(merged_crop, (left, top))

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    source.save(output)
    if args.metadata:
        metadata = {
            "result": result,
            "chunk": {
                "x": args.x,
                "y": args.y,
                "width": args.width,
                "height": args.height,
                "padding": args.padding,
                "scale": args.scale,
                "feather": args.feather,
            },
        }
        Path(args.metadata).write_text(json.dumps(metadata, ensure_ascii=False, indent=2))

    print(f"saved={output}")
    print(f"seed={result.get('seed', 'not-returned')}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    compose_parser = subparsers.add_parser("compose")
    compose_parser.add_argument("--reference", action="append", required=True)
    compose_parser.add_argument("--prompt-file", required=True)
    compose_parser.add_argument("--width", type=int, required=True)
    compose_parser.add_argument("--height", type=int, required=True)
    compose_parser.add_argument("--seed", type=int, required=True)
    compose_parser.add_argument("--output", required=True)
    compose_parser.add_argument("--metadata")
    compose_parser.set_defaults(func=compose)

    inpaint_parser = subparsers.add_parser("inpaint")
    inpaint_parser.add_argument("--image", required=True)
    inpaint_parser.add_argument("--mask", required=True)
    inpaint_parser.add_argument("--prompt-file", required=True)
    inpaint_parser.add_argument("--width", type=int, required=True)
    inpaint_parser.add_argument("--height", type=int, required=True)
    inpaint_parser.add_argument("--steps", type=int, default=40)
    inpaint_parser.add_argument("--guidance", type=float, default=4.5)
    inpaint_parser.add_argument("--seed", type=int, required=True)
    inpaint_parser.add_argument("--negative-prompt", default="text, logo, watermark, duplicated vehicle, malformed vehicle, malformed person")
    inpaint_parser.add_argument("--output", required=True)
    inpaint_parser.add_argument("--metadata")
    inpaint_parser.set_defaults(func=inpaint)

    outpaint_parser = subparsers.add_parser("outpaint")
    outpaint_parser.add_argument("--image", required=True)
    outpaint_parser.add_argument("--top", type=int, default=0)
    outpaint_parser.add_argument("--bottom", type=int, default=0)
    outpaint_parser.add_argument("--left", type=int, default=0)
    outpaint_parser.add_argument("--right", type=int, default=0)
    outpaint_parser.add_argument("--output", required=True)
    outpaint_parser.add_argument("--metadata")
    outpaint_parser.set_defaults(func=outpaint)

    segment_parser = subparsers.add_parser("segment")
    segment_parser.add_argument("--image", required=True)
    segment_parser.add_argument("--prompt", required=True)
    segment_parser.add_argument("--negative-prompt", default="")
    segment_parser.add_argument("--expand", type=int, default=2)
    segment_parser.add_argument("--blur", type=int, default=1)
    segment_parser.add_argument("--output", required=True)
    segment_parser.add_argument("--metadata")
    segment_parser.set_defaults(func=segment)

    segment_box_parser = subparsers.add_parser("segment-box")
    segment_box_parser.add_argument("--image", required=True)
    segment_box_parser.add_argument("--prompt", default="truck")
    segment_box_parser.add_argument("--x-min", type=int, required=True)
    segment_box_parser.add_argument("--y-min", type=int, required=True)
    segment_box_parser.add_argument("--x-max", type=int, required=True)
    segment_box_parser.add_argument("--y-max", type=int, required=True)
    segment_box_parser.add_argument(
        "--positive-point", type=int, nargs=2, action="append", default=[]
    )
    segment_box_parser.add_argument(
        "--negative-point", type=int, nargs=2, action="append", default=[]
    )
    segment_box_parser.add_argument("--apply-mask", action="store_true")
    segment_box_parser.add_argument("--output", required=True)
    segment_box_parser.add_argument("--metadata")
    segment_box_parser.set_defaults(func=segment_box)

    remove_parser = subparsers.add_parser("remove-object")
    remove_parser.add_argument("--image", required=True)
    remove_parser.add_argument("--mask", required=True)
    remove_parser.add_argument("--mask-expansion", type=int, default=8)
    remove_parser.add_argument("--output", required=True)
    remove_parser.add_argument("--metadata")
    remove_parser.set_defaults(func=remove_object)

    extract_parser = subparsers.add_parser("extract-layer")
    extract_parser.add_argument("--image", required=True)
    extract_parser.add_argument("--mask", required=True)
    extract_parser.add_argument("--crop", action="store_true")
    extract_parser.add_argument("--source-box", type=int, nargs=4)
    extract_parser.add_argument("--padding", type=int, default=12)
    extract_parser.add_argument("--feather", type=float, default=0.8)
    extract_parser.add_argument("--threshold", type=int, default=127)
    extract_parser.add_argument("--largest-component", action="store_true")
    extract_parser.add_argument("--invert", action="store_true")
    extract_parser.add_argument("--output", required=True)
    extract_parser.set_defaults(func=extract_layer)

    mask_parser = subparsers.add_parser("rectangle-mask")
    mask_parser.add_argument("--image", required=True)
    mask_parser.add_argument(
        "--box", type=int, nargs=4, action="append", required=True
    )
    mask_parser.add_argument("--radius", type=int, default=24)
    mask_parser.add_argument("--blur", type=float, default=3)
    mask_parser.add_argument("--output", required=True)
    mask_parser.set_defaults(func=rectangle_mask)

    chunk_parser = subparsers.add_parser("chunk-inpaint")
    chunk_parser.add_argument("--image", required=True)
    chunk_parser.add_argument("--x", type=int, required=True)
    chunk_parser.add_argument("--y", type=int, required=True)
    chunk_parser.add_argument("--width", type=int, required=True)
    chunk_parser.add_argument("--height", type=int, required=True)
    chunk_parser.add_argument("--padding", type=int, default=96)
    chunk_parser.add_argument("--scale", type=int, default=2)
    chunk_parser.add_argument("--feather", type=float, default=10)
    chunk_parser.add_argument("--prompt-file", required=True)
    chunk_parser.add_argument("--steps", type=int, default=40)
    chunk_parser.add_argument("--guidance", type=float, default=4.5)
    chunk_parser.add_argument("--seed", type=int, required=True)
    chunk_parser.add_argument("--negative-prompt", default="text, logo, watermark, duplicated vehicle, malformed vehicle, malformed person")
    chunk_parser.add_argument("--output", required=True)
    chunk_parser.add_argument("--metadata")
    chunk_parser.set_defaults(func=chunk_inpaint)

    return parser


def main() -> None:
    configure_credentials()
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
