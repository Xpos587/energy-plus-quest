#!/bin/bash
# GPT restyle through Keyrelay: gen-kr.sh NAME SIZE  (out/NAME-notext.png -> gen/NAME.png)
cd "$(dirname "$0")"
n=$1; size=$2
python3 -c "from PIL import Image; Image.open('out/$n-notext.png').convert('RGB').save('gen/in-$n.jpg', quality=92)"
~/.agents/skills/imagegen/scripts/media_images.py edit --model cx/gpt-image-2 --image gen/in-$n.jpg --image gen/style.jpg \
  --prompt-file p-restyle.txt --size $size --quality high --out gen/$n.png && echo "OK $n"
