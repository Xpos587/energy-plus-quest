#!/bin/sh
# Header stage icons: trim each master to its object, centre it on a square
# whose inscribed circle holds the whole object, export 128 px webp.
set -eu
cd "$(dirname "$0")"
out=../../public/opening/stage-icons-v1
mkdir -p "$out"
for k in carrier loading warehouse barge lastmile; do
  bg=$(magick "$k-nbp.png" -format '%[pixel:p{4,4}]' info:)
  # ponytail: one padding factor for all five; tune per icon if one reads small.
  magick "$k-nbp.png" -fuzz 6% -trim +repage \
    -gravity center -background "$bg" \
    -extent "%[fx:max(w,h)*1.22]x%[fx:max(w,h)*1.22]" \
    -resize 128x128 -quality 90 "$out/$k.webp"
done
