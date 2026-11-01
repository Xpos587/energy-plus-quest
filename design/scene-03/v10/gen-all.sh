#!/bin/bash
# All v10 restyles, one at a time (the gateway drops parallel requests); skips finished ones.
cd "$(dirname "$0")"; L=../../../.tmp-work/v10/gen
G="the gift box with a red ribbon"
R="orange dashed walking routes on the floor stay visible exactly where image 1 has them"
run() { [ -f $L/$1.png ] || [ -f $L/$1$SUF.png ] || ./gen.sh "$@" > $L/$1$SUF.log 2>&1; }
run tall 1024x1536 p-tall.txt
run outcome-entrance 2048x864 p-outcome.txt "$G sits in a free floor cell right by the receiving door instead of a rack; two workers carry cardboard boxes along a long detour; $R."

for p in boat camera; do
run outcome-alphabet-$p 2048x864 p-outcome.txt "$G sits on the bottom shelf at the front of its rack row; two workers walk long distances along the lane carrying boxes; $R."
done

run outcome-alphabet-socks 2048x864 p-outcome.txt "$G sits on the bottom shelf at the front of its rack row; two workers walk long distances along the lane carrying boxes; $R."
run outcome-keeper 2048x864 p-outcome.txt "the experienced storekeeper has left; two new-shift workers in GREEN hard hats stand by the racks looking puzzled, scratching their heads, not knowing where things are; $G stands on a pallet by the dispatch door."

run outcome-wms 2048x864 p-outcome.txt "the orange forklift carries $G straight from the kiosk towards the open dispatch door and the waiting truck along a short green dashed route; the WMS kiosk screen is lit (blank)."
