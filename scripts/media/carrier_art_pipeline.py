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
from pathlib import Path
from urllib.request import urlretrieve

import fal_client
from PIL import Image, ImageFilter


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
