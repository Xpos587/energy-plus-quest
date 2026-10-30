#!/bin/bash
# usage: run.sh SOURCE tile...
D=$(dirname "$(readlink -f "$0")"); cd "$D"; SRC=$1; shift
for n in "$@"; do
  sed "s/OUT/g-$n.png/" q.txt > t-$n.txt
  for try in 1 2; do
    codex exec --skip-git-repo-check -s workspace-write -C "$D" -i "$SRC,$n.png" - < t-$n.txt > log-$n.txt 2>&1
    [ -f g-$n.png ] && break
  done
  echo "$n done $(python3 -c "from PIL import Image;print(Image.open('g-$n.png').size)" 2>&1)"
done
