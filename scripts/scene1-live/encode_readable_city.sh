#!/usr/bin/env bash
set -euo pipefail

# Usage: bash scripts/scene1-live/encode_readable_city.sh RENDER_DIRECTORY OUTPUT_DIRECTORY [FRAME_COUNT]
render_dir=$1
output_dir=$2
expected_frames=${3:-768}
[[ $expected_frames =~ ^[1-9][0-9]*$ ]] || exit 1
mkdir -p "$output_dir"
stage_dir=$(mktemp -d "$output_dir/.encode.XXXXXX")
trap 'rm -rf "$stage_dir"' EXIT

ffmpeg -v error -framerate 24 -start_number 1 -i "$render_dir/frames/%04d.png" \
  -frames:v "$expected_frames" -c:v libx264 -threads 2 -crf 20 -pix_fmt yuv420p -movflags +faststart \
  "$stage_dir/city-motion-desktop.mp4"
for variant in tablet mobile; do
  if [[ $variant == tablet ]]; then resolution=864:600; else resolution=720:500; fi
  ffmpeg -v error -i "$stage_dir/city-motion-desktop.mp4" -vf "scale=$resolution" \
    -c:v libx264 -threads 2 -crf 20 -pix_fmt yuv420p -movflags +faststart \
    "$stage_dir/city-motion-$variant.mp4"
done
for video in "$stage_dir"/*.mp4; do
  frame_count=$(ffprobe -v error -select_streams v:0 -show_entries stream=nb_frames -of csv=p=0 "$video")
  [[ $frame_count == "$expected_frames" ]] || { echo "Incomplete animation: $frame_count frames" >&2; exit 1; }
  ffmpeg -v error -i "$video" -f null -
  ffprobe -v error -show_entries stream=width,height,r_frame_rate,nb_frames:format=duration -of json "$video"
done
magick "$render_dir/after.png" -quality 92 "$stage_dir/city-poster.webp"
mv "$stage_dir"/*.mp4 "$stage_dir/city-poster.webp" "$output_dir/"
