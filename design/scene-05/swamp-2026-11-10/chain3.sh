cd "$(dirname "$0")"
run(){ for i in 1 2 3 4 5 6; do
  higgsfield generate create nano_banana_pro --prompt "$(cat $1)" --image $2 --aspect_ratio $3 --resolution 2k --wait --json > gen/hf-$4.json 2> gen/hf-$4.err && break; sleep 30; done
  u=$(python3 -c "import json;print(json.load(open('gen/hf-$4.json'))[0]['result_url'])"); curl -s -o gen/hf-$4.png "$u"; echo "$4 $(magick gen/hf-$4.png -format %wx%h info:)"; }
run p-swamp-wide.txt gen/hin-wide.png 5:4 swamp2-wide
run p-swamp-tall.txt gen/hin-tall.png 4:5 swamp2-tall
