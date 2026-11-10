cd "$(dirname "$0")"
run(){ for i in 1 2 3 4 5 6; do
  higgsfield generate create nano_banana_pro --prompt "$(cat $1)" $2 --aspect_ratio $3 --resolution 2k --wait --json > gen/hf-$4.json 2> gen/hf-$4.err && break; sleep 25; done
  u=$(python3 -c "import json;print(json.load(open('gen/hf-$4.json'))[0]['result_url'])"); curl -s -o gen/hf-$4.png "$u"; echo "$4 $(magick gen/hf-$4.png -format %wx%h info:)"; }
R="--image gen/ref-heli-big.png"
run p-heli7.txt "--image gen/c-fl-boat.png $R" 16:9 h7-fl-boat
run p-heli7.txt "--image gen/c-fl-parcel.png $R" 16:9 h7-fl-parcel
echo H7DONE
echo H5TALLDONE
