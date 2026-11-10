cd "$(dirname "$0")"
for i in 1 2 3 4 5 6; do higgsfield generate create nano_banana_pro --prompt "$(cat p-trail-tall.txt)" --image gen/c-trail-tall.png --aspect_ratio 16:9 --resolution 2k --wait --json > gen/hf-t2-trail-tall.json 2> gen/hf-t2-trail-tall.err && break; sleep 25; done
curl -s -o gen/hf-t2-trail-tall.png "$(python3 -c "import json;print(json.load(open('gen/hf-t2-trail-tall.json'))[0]['result_url'])")"; echo TALL2DONE
