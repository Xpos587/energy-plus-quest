#!/bin/bash
# All v10 restyles, one at a time (the gateway drops parallel requests); skips finished ones.
cd "$(dirname "$0")"; L=../../../.tmp-work/v13/gen
G="the gift box with a red ribbon"
R="the floor stays clean between the lane lines (walking routes are painted on later)"
ONE="there is exactly ONE gift box in the whole picture, keep it where image 1 shows it; the small rack by the receiving door holds only plain brown boxes"
run() { [ -f $L/$1.png ] || [ -f $L/$1$SUF.png ] || ./gen.sh "$@" > $L/$1$SUF.log 2>&1; }
run tall 1024x1536 p-tall.txt
run outcome-entrance 2048x864 p-outcome.txt "$G sits in a free bottom cell of the small rack by the receiving door; two workers carry cardboard boxes along a long detour; $R."

for p in boat camera; do
run outcome-alphabet-$p 2048x864 p-outcome.txt "$G sits on the bottom shelf at the front of its rack row; two workers walk long distances along the lane carrying boxes; $ONE; $R."
done

run outcome-alphabet-socks 2048x864 p-outcome.txt "$G sits on the bottom shelf at the front of its rack row; two workers walk long distances along the lane carrying boxes; $ONE; $R."
run outcome-keeper 2048x864 p-outcome.txt "the experienced storekeeper has left; two new-shift workers in GREEN hard hats stand by the racks looking puzzled, scratching their heads, not knowing where things are; $G stands on a pallet in front of the rightmost rack row, near the dispatch door."

run outcome-wms 2048x864 p-outcome.txt "the orange forklift carries $G along the lane towards the dispatch door and the waiting truck over a short distance; the kiosk screen is lit (blank)."
