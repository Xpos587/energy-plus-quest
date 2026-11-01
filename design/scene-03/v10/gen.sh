#!/bin/bash
# GPT restyle of a Blender notext render in the approved style.
#   [STYLE=ref/style-map.jpg] gen.sh NAME SIZE PROMPTFILE [STORY]   (render .tmp-work/v15/bl/NAME-notext.png -> .tmp-work/v15/gen/NAME.png)
set -e
here=$(cd "$(dirname "$0")" && pwd); w=$here/../../../.tmp-work/v15
n=$1; size=$2; p=$3; story=$4; o=$n${SUF:-}  # SUF: new name after a completion-unknown receipt
# inputs downsized: the gateway drops uploads much over ~1 MB total (SSL EOF)
python3 -c "
from PIL import Image
for s, d in (('$w/bl/$n-notext.png', 'in-$n'), ('$here/${STYLE:-ref/master-desk.jpg}', 's-master'), ('$here/ref/style-people.jpg', 's-people')):
    im = Image.open(s).convert('RGB'); im.thumbnail((1536, 1536)); im.save('$w/gen/' + d + '.jpg', quality=80)"
sed "s|__STORY__|$story|" "$here/$p" > "$w/gen/p-$n.txt"
cd ~/.agents/skills/imagegen/scripts
uv run media_images.py edit --model cx/gpt-image-2 --image "$w/gen/in-$n.jpg" --image "$w/gen/s-master.jpg" \
  --image "$w/gen/s-people.jpg" --prompt-file "$w/gen/p-$n.txt" --size "$size" --quality high --timeout 600 --out "$w/gen/$o.png"
