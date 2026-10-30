#!/bin/bash
D=$(dirname "$(readlink -f "$0")"); cd "$D"
for n in "$@"; do
  sed "s/OUT/g-$n.png/" q.txt > t-$n.txt
  for try in 1 2; do
    codex exec --skip-git-repo-check -s workspace-write -C "$D" -i "ctx.png,$n.png" - < t-$n.txt > log-$n.txt 2>&1
    [ -f g-$n.png ] && break
  done
  echo "$n done"
done
