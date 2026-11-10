cd "$(dirname "$0")"
run(){ higgsfield generate create nano_banana_pro --prompt "$(cat $1)" $2 --aspect_ratio 16:9 --resolution 2k --wait --json > gen/hf-$3.json 2> gen/hf-$3.err
  u=$(python3 -c "import json;print(json.load(open('gen/hf-$3.json'))[0]['result_url'])"); curl -s -o gen/hf-$3.png "$u"; echo "$3 $(magick gen/hf-$3.png -format %wx%h info:)"; }
R="--image gen/ref-heli.png --image gen/ref-intro-heli.png"
run p-heli2.txt "--image gen/c-heli-wide.png $R" m-heli-wide
run p-heli2.txt "--image gen/c-heli-tall.png $R" m-heli-tall
