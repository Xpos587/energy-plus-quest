#!/bin/bash
# GPT restyle of a Blender notext render in the approved style.
#   gen.sh NAME SIZE PROMPTFILE [STORY]   (render .tmp-work/v10/bl/NAME-notext.png -> .tmp-work/v10/gen/NAME.png)
set -e
here=$(cd "$(dirname "$0")" && pwd); w=$here/../../../.tmp-work/v10
n=$1; size=$2; p=$3; story=$4; o=$n${SUF:-}  # SUF: new name after a completion-unknown receipt
python3 -c "from PIL import Image; Image.open('$w/bl/$n-notext.png').convert('RGB').save('$w/gen/in-$n.jpg', quality=92)"
sed "s|__STORY__|$story|" "$here/$p" > "$w/gen/p-$n.txt"
cd ~/.agents/skills/imagegen/scripts
uv run media_images.py edit --model cx/gpt-image-2 --image "$w/gen/in-$n.jpg" --image "$here/ref/master-desk.jpg" \
  --image "$here/ref/style-people.jpg" --prompt-file "$w/gen/p-$n.txt" --size "$size" --quality high --timeout 600 --out "$w/gen/$o.png"
