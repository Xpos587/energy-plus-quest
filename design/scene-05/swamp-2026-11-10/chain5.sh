cd "$(dirname "$0")"
run(){ for i in 1 2 3 4 5 6; do
  higgsfield generate create nano_banana_pro --prompt "$(cat $1)" $2 --aspect_ratio 16:9 --resolution 2k --wait --json > gen/hf-$3.json 2> gen/hf-$3.err && break; sleep 30; done
  u=$(python3 -c "import json;print(json.load(open('gen/hf-$3.json'))[0]['result_url'])"); curl -s -o gen/hf-$3.png "$u"; echo "$3 $(magick gen/hf-$3.png -format %wx%h info:)"; }
magick gen/base-wide.png -crop 896x504+430+1410 +repage gen/c-heli-wide.png
magick gen/base-tall.png -crop 896x504+740+1830 +repage gen/c-heli-tall.png
magick gen/base-wide.png -crop 1400x788+2350+1130 +repage gen/c-abk-wide.png
magick gen/base-tall.png -crop 1400x788+1300+560 +repage gen/c-abk-tall.png
R="--image gen/ref-heli.png --image gen/ref-intro-heli.png"
run p-heli2.txt "--image gen/c-heli-wide.png $R" f-heli-wide
run p-heli2.txt "--image gen/c-heli-tall.png $R" f-heli-tall
run p-abk.txt "--image gen/c-abk-wide.png --image ../v9/ref/abk.png" f-abk-wide
run p-abk.txt "--image gen/c-abk-tall.png --image ../v9/ref/abk.png" f-abk-tall
echo ALLDONE
