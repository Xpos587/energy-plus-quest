cd "$(dirname "$0")"
run(){ for i in 1 2 3 4 5 6; do
  higgsfield generate create nano_banana_pro --prompt "$(cat $1)" $2 --aspect_ratio 16:9 --resolution 2k --wait --json > gen/hf-$3.json 2> gen/hf-$3.err && break; sleep 30; done
  u=$(python3 -c "import json;print(json.load(open('gen/hf-$3.json'))[0]['result_url'])"); curl -s -o gen/hf-$3.png "$u"; echo "$3 $(magick gen/hf-$3.png -format %wx%h info:)"; }
R="--image gen/ref-intro-heli.png --image gen/ref-heli.png"
run p-heli3.txt "--image gen/c-heli-wide.png $R" g-heli-wide
run p-heli3.txt "--image gen/c-heli-tall.png $R" g-heli-tall
echo ALLDONE
