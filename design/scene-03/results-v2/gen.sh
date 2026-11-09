#!/bin/sh
# Restyle scene 3 results into the common game style (results-style.md) with Higgsfield Nano Banana Pro.
# cx/gpt-image-2 was down (HTTP 502) on 2026-11-09; Higgsfield gpt_image_2 needs a paid plan.
# Image 1 = current result (edit target), 2 = style-ref.jpg (scenes 4/1 + scene 3 overview people),
# 3 = worker crop of the restyled entrance (cast reference; a full entrance frame made the model copy its composition).
#   sh gen.sh NAME SRC.png ASPECT OUT_DIR [CAST.png]   (wms: no CAST — the operator is another person)
set -e
here=$(dirname "$0"); name=$1 src=$2 ar=$3 out=$4 cast=$5
p=$(cat "$here/p-base.txt")
[ -n "$cast" ] && p="$p
$(cat "$here/cast.txt")"
p="$p
$(cat "$here/p-${name%%-*}.extra.txt")"
set -- --image "$src" --image "$here/style-ref.jpg"
[ -n "$cast" ] && set -- "$@" --image "$cast"
higgsfield generate create nano_banana_pro --prompt "$p" "$@" --aspect_ratio "$ar" --resolution 2k --wait --json > "$out/hf-$name.json"
curl -sSL -o "$out/hf-$name.png" "$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))[0]['result_url'])" "$out/hf-$name.json")"
