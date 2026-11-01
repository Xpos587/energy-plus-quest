#!/bin/bash
# All tall/outcome restyles, one at a time (the gateway drops parallel requests); skips finished ones.
cd "$(dirname "$0")"; L=../../../.tmp-work/v15/gen
# the gateway drops some TLS handshakes (SSL EOF before the request is sent): retry those under a new name
run() { ls $L/$1*.png >/dev/null 2>&1 && return; for i in 1 2 3 4 5 6 7 8; do
  SUF=-r$i ./gen.sh "$@" > $L/$1-r$i.log 2>&1; [ -f $L/$1-r$i.png ] && return
  grep -q UNEXPECTED_EOF $L/$1-r$i.log || return; sleep 15; done; }
run tall 1024x1536 p-tall.txt
run outcome-entrance 2048x864 p-outcome.txt "the gift was stored in a free bottom cell of the small rack by the receiving door, the far end of the hall; one worker carries a box all the way across the hall towards the dispatch door, another walks back to the receiving rack for the next one."
for p in boat camera socks; do
run outcome-alphabet-$p 2048x864 p-outcome.txt "the gift lies on the top shelf of its letter row; a worker with a scanner stands in the aisle by that row, another worker carries a box along the open floor towards the dispatch door."
done
run outcome-keeper 2048x864 p-outcome.txt "the experienced storekeeper has left; two new-shift workers in GREEN hard hats look around puzzled with their scanners, not knowing where things are; the gift lies on the top shelf of the rightmost rack row, near the dispatch door, unnoticed."
run outcome-wms 2048x864 p-outcome.txt "the system chose the cell nearest dispatch, so the gift already leaves: a worker tows it on a pallet jack through the dispatch door into the truck; the monitor on the desk keeps its dark blue screen."
