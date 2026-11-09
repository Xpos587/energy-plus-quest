#!/bin/sh
# Second pass over the restyled results: company PPE from ppe-ref.jpg (original 10-28 results + scene 4 Pyotr)
# and the emotion of each result text (results-style.md). Higgsfield Nano Banana Pro, image edit.
#   sh ppe.sh MOOD SRC.png ASPECT OUT.png   (MOOD = tired | keeper | wms)
set -e
here=$(dirname "$0"); mood=$1 src=$2 ar=$3 out=$4
p="$(cat "$here/p-ppe.txt")
$(cat "$here/p-ppe-$mood.txt")"
higgsfield generate create nano_banana_pro --prompt "$p" --image "$src" --image "$here/ppe-ref.jpg" \
  --aspect_ratio "$ar" --resolution 2k --wait --json > "$out.json"
curl -sSL -o "$out" "$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))[0]['result_url'])" "$out.json")"
