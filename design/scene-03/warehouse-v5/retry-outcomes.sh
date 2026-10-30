#!/bin/bash
# Retry missing outcome stills across providers every 10 min (max ~4 h).
S=~/.agents/skills/imagegen/scripts/media_images.py
for i in $(seq 1 24); do
  left=0
  for n in entrance keeper wms; do
    [ -s gen/$n.png ] && continue
    left=1
    for m in gpt_image_2 nano_banana_pro; do
      extra=""; [ $m = gpt_image_2 ] && extra="--quality high"
      timeout 900 higgsfield generate create $m --prompt "$(cat p-$n.txt)" --image ref/master.jpg --aspect_ratio 21:9 --resolution 2k $extra --wait --wait-timeout 14m --json > gen/$n.json 2> gen/$n.err
      u=$(python3 -c "import json;d=json.load(open('gen/$n.json'));d=d[0] if isinstance(d,list) else d;print(d['result_url'])" 2>/dev/null)
      [ -n "$u" ] && curl -sfL "$u" -o gen/$n.png && { echo "OK $n via hf/$m"; break; }
    done
    [ -s gen/$n.png ] && continue
    rm -f gen/$n-cx.png*; timeout 600 $S edit --model cx/gpt-image-2 --image ref/master.jpg --prompt-file p-$n.txt --size 2048x880 --quality high --out gen/$n-cx.png > gen/$n-cx.log 2>&1
    [ -s gen/$n-cx.png ] && mv gen/$n-cx.png gen/$n.png && echo "OK $n via cx"
  done
  [ $left = 0 ] && { echo ALL DONE; exit 0; }
  ls gen/*.png | tr '\n' ' '; echo " round $i $(date +%H:%M)"
  sleep 600
done
exit 1
