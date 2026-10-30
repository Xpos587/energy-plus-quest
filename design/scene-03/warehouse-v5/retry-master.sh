#!/bin/bash
# retry master generation until a provider recovers (max ~80 min)
S=~/.agents/skills/imagegen/scripts/media_images.py
for i in $(seq 1 20); do
  for m in cx/gpt-image-2 gemini/gemini-3-pro-image-preview; do
    n=$(echo $m | tr '/.' '__')
    extra=""; [[ $m == cx/* ]] && extra="--size 1536x1024 --quality high"
    out=gen/master-$n-$i.png
    timeout 600 $S edit --model $m --image ref/ref-barge-mid.png --image ref/ref-city.png --prompt-file p-master.txt $extra --out $out > gen/try-$n-$i.log 2>&1
    if [ -s "$out" ]; then echo "SUCCESS $out"; exit 0; fi
    echo "fail $m $i: $(tail -1 gen/try-$n-$i.log | cut -c1-120)"
  done
  sleep 240
done
exit 1
