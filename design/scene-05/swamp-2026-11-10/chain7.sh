cd "$(dirname "$0")"
run(){ for i in 1 2 3 4 5 6; do
  higgsfield generate create nano_banana_pro --prompt "$(cat $1)" $2 --aspect_ratio $3 --resolution 2k --wait --json > gen/hf-$4.json 2> gen/hf-$4.err && break; sleep 25; done
  u=$(python3 -c "import json;print(json.load(open('gen/hf-$4.json'))[0]['result_url'])"); curl -s -o gen/hf-$4.png "$u"; echo "$4 $(magick gen/hf-$4.png -format %wx%h info:)"; }
run p-swamp4-wide.txt "--image gen/hin-wide.png" 5:4 swamp4-wide
run p-swamp4-tall.txt "--image gen/hin-tall.png" 4:5 swamp4-tall
sed -i 's/"swamp2-wide", "tall": "swamp3-tall"/"swamp4-wide", "tall": "swamp4-tall"/' compose_base.py
uv run --with pillow --with numpy python compose_base.py
magick gen/base-wide.png -resize 1100x ../../.tmp-work/scene5-map/b4w.jpg 2>/dev/null || magick gen/base-wide.png -resize 1100x ../../../.tmp-work/scene5-map/b4w.jpg
magick gen/base-tall.png -resize 900x ../../../.tmp-work/scene5-map/b4t.jpg
echo SWAMPDONE
R="--image gen/ref-intro-heli.png --image gen/ref-heli.png"
magick gen/base-wide.png -crop 896x504+430+1410 +repage gen/c-heli-wide.png
magick gen/base-tall.png -crop 896x504+740+1830 +repage gen/c-heli-tall.png
magick gen/base-wide.png -crop 1400x788+2350+1130 +repage gen/c-abk-wide.png
magick gen/base-tall.png -crop 1400x788+1300+560 +repage gen/c-abk-tall.png
run p-heli3.txt "--image gen/c-heli-wide.png $R" 16:9 f-heli-wide
run p-heli3.txt "--image gen/c-heli-tall.png $R" 16:9 f-heli-tall
run p-abk.txt "--image gen/c-abk-wide.png --image ../v9/ref/abk.png" 16:9 f-abk-wide
run p-abk.txt "--image gen/c-abk-tall.png --image ../v9/ref/abk.png" 16:9 f-abk-tall
uv run --with pillow --with numpy python finish.py
uv run --with opencv-python-headless --with numpy python contours.py
echo ALLDONE
