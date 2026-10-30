#!/bin/bash
# GPT restyle of the Blender renders: gen.sh NAME ASPECT  (reads out/NAME-notext.png)
cd "$(dirname "$0")"
n=$1; ar=$2
python3 -c "from PIL import Image; Image.open('out/$n-notext.png').convert('RGB').save('gen/in-$n.jpg', quality=92)"
higgsfield generate create gpt_image_2 --prompt "$(cat p-restyle.txt)" --image gen/in-$n.jpg --image gen/style.jpg \
  --aspect_ratio $ar --resolution 2k --quality high --wait --json > gen/$n.json 2>&1
url=$(python3 -c "import json;print(json.load(open('gen/$n.json'))[0]['result_url'])") && curl -s -o gen/$n.png "$url" && echo "OK $n"
