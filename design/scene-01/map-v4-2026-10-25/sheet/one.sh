#!/bin/bash
# one.sh plate rid q  (q = 0..3 → headings 8q..8q+7)
set -e
cd "$(dirname "$0")"
plate=$1; rid=$2; q=$3
name=batch/$plate-$rid-$q
H=$(python3 -c "print(','.join(str(8*$q+i) for i in range(8)))")
parts=cab,trailer; [ "$rid" = express ] && parts=""
~/.local/share/comfyui/venv/bin/python mksheet2.py $plate $rid $name $H "$parts" >/dev/null
gn=batch/g-$plate-$rid-$q.png; [ -f $gn ] || { sed "s#OUT#$gn#" q.txt | sed "s#sprite sheet of ONE truck rendered in 3D: the top row shows its blue tractor cab at 8 headings, the two lower rows its white box trailer at 8 headings#sprite sheet of ONE truck rendered in 3D: the same vehicle parts at 8 headings, in rows#; s#cab colour (blue), trailer colour (white)#every part's original colours#" > $name.txt
  for t in 1 2; do codex exec --skip-git-repo-check -s workspace-write -C "$PWD" -i "ctx.png,$name.png" - < $name.txt > $name.log 2>&1 || true; gn=batch/g-$plate-$rid-$q.png; [ -f $gn ] && break; done; }
~/.local/share/comfyui/venv/bin/python reslice.py $name
