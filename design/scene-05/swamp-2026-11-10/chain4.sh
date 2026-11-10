cd "$(dirname "$0")"
for i in 1 2 3 4 5 6; do higgsfield generate create nano_banana_pro --prompt "$(cat p-swamp-tall2.txt)" --image gen/hin-tall.png --aspect_ratio 4:5 --resolution 2k --wait --json > gen/hf-swamp3-tall.json 2> gen/hf-swamp3-tall.err && break; sleep 30; done
u=$(python3 -c "import json;print(json.load(open('gen/hf-swamp3-tall.json'))[0]['result_url'])"); curl -s -o gen/hf-swamp3-tall.png "$u"; magick gen/hf-swamp3-tall.png -resize 900x ../../../.tmp-work/scene5-map/s3t.jpg
