"""Remove baked trailer-roof numbers from the separated-routes frame sequence.

Export glyph silhouettes without modifying the .blend file:
  blender -b separated-city.blend --python remove_roof_numbers.py -- HULLS.json

Then encode the existing rendered frames using an environment with OpenCV:
  uv run --python /path/to/python --no-project python remove_roof_numbers.py \
    FRAMES_DIR HULLS.json OUTPUT_DIR
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path


WIDTH, HEIGHT, FPS, FRAMES = 1008, 700, 24, 1152


def export_hulls(path):
    import bpy
    from bpy_extras.object_utils import world_to_camera_view

    scene = bpy.context.scene
    frames = []
    for frame in range(1, FRAMES + 1):
        scene.frame_set(frame)
        depsgraph = bpy.context.evaluated_depsgraph_get()
        row = []
        for truck in range(1, 5):
            obj = scene.objects[f"vehicle {truck} identification"]
            evaluated = obj.evaluated_get(depsgraph)
            mesh = evaluated.to_mesh()
            points = []
            for vertex in mesh.vertices:
                projected = world_to_camera_view(
                    scene, scene.camera, obj.matrix_world @ vertex.co
                )
                points.append([projected.x * WIDTH, (1 - projected.y) * HEIGHT])
            evaluated.to_mesh_clear()
            row.append(points)
        frames.append(row)
    path.write_text(json.dumps(frames, separators=(",", ":")))


def run(command):
    subprocess.run(command, check=True)


def encode(frames_dir, hull_path, output_dir):
    import cv2
    import numpy as np

    hulls = json.loads(hull_path.read_text())
    if len(hulls) != FRAMES or any(len(row) != 4 for row in hulls):
        raise ValueError("Expected four glyph silhouettes on each of 1152 frames")
    output_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".denumber-", dir=output_dir) as temporary:
        stage = Path(temporary)
        desktop = stage / "city-motion-desktop.mp4"
        process = subprocess.Popen(
            [
                "ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24",
                "-s", f"{WIDTH}x{HEIGHT}", "-r", str(FPS), "-i", "-",
                "-frames:v", str(FRAMES), "-c:v", "libx264", "-threads", "2",
                "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                str(desktop),
            ],
            stdin=subprocess.PIPE,
        )
        try:
            for index, outlines in enumerate(hulls, 1):
                frame = cv2.imread(str(frames_dir / f"{index:04d}.png"))
                if frame is None or frame.shape[:2] != (HEIGHT, WIDTH):
                    raise ValueError(f"Missing or wrong-size source frame {index}")
                mask = np.zeros((HEIGHT, WIDTH), dtype=np.uint8)
                for points in outlines:
                    contour = cv2.convexHull(np.rint(points).astype(np.int32))
                    cv2.fillConvexPoly(mask, contour, 255)
                # Only the projected glyphs and a one-pixel antialias margin change.
                mask = cv2.dilate(mask, np.ones((3, 3), np.uint8))
                cleaned = cv2.inpaint(frame, mask, 3, cv2.INPAINT_TELEA)
                if index == 1:
                    cv2.imwrite(
                        str(stage / "city-poster.webp"), cleaned,
                        [cv2.IMWRITE_WEBP_QUALITY, 92],
                    )
                process.stdin.write(cleaned.tobytes())
        finally:
            process.stdin.close()
        if process.wait() != 0:
            raise RuntimeError("Desktop video encode failed")

        for variant, size in (("tablet", "864:600"), ("mobile", "720:500")):
            run([
                "ffmpeg", "-v", "error", "-y", "-i", str(desktop),
                "-vf", f"scale={size}", "-c:v", "libx264", "-threads", "2",
                "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                str(stage / f"city-motion-{variant}.mp4"),
            ])
        for name in (
            "city-motion-desktop.mp4", "city-motion-tablet.mp4",
            "city-motion-mobile.mp4", "city-poster.webp",
        ):
            (stage / name).replace(output_dir / name)


if __name__ == "__main__":
    if "--" in sys.argv:
        export_hulls(Path(sys.argv[sys.argv.index("--") + 1]))
    else:
        encode(*(Path(arg) for arg in sys.argv[1:4]))
