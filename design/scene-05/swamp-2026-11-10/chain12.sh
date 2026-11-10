cd "$(dirname "$0")"
run(){ for i in 1 2 3 4 5 6; do
  higgsfield generate create nano_banana_pro --prompt "$(cat $1)" $2 --aspect_ratio $3 --resolution 2k --wait --json > gen/hf-$4.json 2> gen/hf-$4.err && break; sleep 25; done
  u=$(python3 -c "import json;print(json.load(open('gen/hf-$4.json'))[0]['result_url'])"); curl -s -o gen/hf-$4.png "$u"; echo "$4 $(magick gen/hf-$4.png -format %wx%h info:)"; }
run p-trail.txt "--image gen/c-trail-wide.png" 16:9 t-trail-wide
run p-trail.txt "--image gen/c-trail-tall.png" 16:9 t-trail-tall
echo TRAILDONE
