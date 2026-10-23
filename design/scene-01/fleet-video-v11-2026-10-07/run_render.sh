#!/bin/sh
set -eu
cd /home/michael/Github/energy-plus-quest
blender -b design/scene-01/fleet-video-v11-2026-10-07/fleet-v11-video.blend -t 4 --python design/scene-01/fleet-video-v11-2026-10-07/render_projected_shadow.py > design/scene-01/fleet-video-v11-2026-10-07/shadow-full.log 2>&1
blender -b design/scene-01/fleet-video-v11-2026-10-07/fleet-v11-video.blend -t 4 --python design/scene-01/fleet-video-v11-2026-10-07/render_color.py > design/scene-01/fleet-video-v11-2026-10-07/color-full.log 2>&1
uv run --no-project --with pillow --with numpy python design/scene-01/fleet-video-v11-2026-10-07/composite_video.py > design/scene-01/fleet-video-v11-2026-10-07/encode.log 2>&1
