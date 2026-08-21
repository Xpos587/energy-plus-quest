#!/usr/bin/env sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
SOURCE_DIR="$ROOT_DIR/design/scene-01/assets"
OUTPUT_DIR="$SOURCE_DIR/feedback-v1"

mkdir -p "$OUTPUT_DIR"

# Keep the road geometry intact while pushing the map behind the clickable vehicles.
magick "$SOURCE_DIR/map-v2-desktop/edited.webp" \
  -colorspace sRGB -modulate 112,34,100 -fill '#f8fbfd' -colorize 42% \
  -blur 0x0.2 -quality 92 "$OUTPUT_DIR/map-desktop.webp"

magick "$SOURCE_DIR/map-mobile/edited.webp" \
  -colorspace sRGB -modulate 112,34,100 -fill '#f8fbfd' -colorize 42% \
  -blur 0x0.2 -quality 92 "$OUTPUT_DIR/map-mobile.webp"

# Add restrained age/experience cues without redesigning the approved character.
magick "$SOURCE_DIR/choices-v2/professional.webp" \
  -stroke 'rgba(22,55,88,0.72)' -strokewidth 2 -fill none \
  -draw "ellipse 177,117 16,11 0,360 ellipse 222,117 16,11 0,360 line 193,117 206,117" \
  -stroke 'rgba(197,181,166,0.62)' -strokewidth 2 \
  -draw "path 'M 151,77 C 146,88 146,99 150,108' path 'M 245,78 C 249,90 249,101 246,110'" \
  -quality 94 "$OUTPUT_DIR/professional.webp"

# These v2 assets already answer the framing and scale notes; version them with the feedback set.
magick "$SOURCE_DIR/choices-v2/khor.webp" -quality 94 "$OUTPUT_DIR/khor.webp"
magick "$SOURCE_DIR/choices-v2/boat.webp" -quality 94 "$OUTPUT_DIR/boat.webp"

# Normalize every vehicle to the same transparent canvas, then make its story legible at map scale.
magick "$SOURCE_DIR/carriers-cutout/old.png" -trim +repage -resize 390x150 \
  -gravity center -background none -extent 512x256 \
  -fill 'rgba(99,109,119,0.42)' -stroke none \
  -draw "circle 37,132 56,132 circle 61,118 78,118 circle 67,145 83,145" \
  -stroke 'rgba(220,230,237,0.72)' -strokewidth 3 \
  -draw "line 178,111 215,106 line 208,138 254,132 line 277,116 302,111" \
  "$OUTPUT_DIR/carrier-old.png"

magick "$SOURCE_DIR/carriers-cutout/near.png" -trim +repage -resize 390x150 \
  -gravity center -background none -extent 512x256 \
  -modulate 98,72,100 "$OUTPUT_DIR/carrier-near.png"

magick "$SOURCE_DIR/carriers-cutout/crew.png" -trim +repage -resize 390x150 \
  -gravity center -background none -extent 512x256 \
  -fill '#f1b177' -stroke '#ffffff' -strokewidth 2 \
  -draw "circle 346,108 351,108 circle 358,108 363,108" \
  -fill '#ff5500' -stroke none \
  -draw "roundrectangle 340,113 352,122 4,4 roundrectangle 353,113 365,122 4,4" \
  "$OUTPUT_DIR/carrier-crew.png"

magick "$SOURCE_DIR/carriers-cutout/express.png" -trim +repage -resize 390x150 \
  -gravity center -background none -extent 512x256 \
  -font DejaVu-Sans-Bold -pointsize 24 -fill '#ffffff' -stroke none \
  -gravity center -annotate -44+12 'EXPRESS' \
  "$OUTPUT_DIR/carrier-express.png"

# A representative human outcome: Express arrives with the selected camera for Alva.
magick -size 1536x768 gradient:'#f9f0df-#dceafa' \
  \( "$OUTPUT_DIR/map-desktop.webp" -resize '1536x768^' -gravity center -extent 1536x768 \
     -alpha set -channel A -evaluate set 18% +channel \) -compose over -composite \
  -gravity northwest -stroke 'rgba(255,85,0,0.78)' -strokewidth 7 -fill none \
  -draw "path 'M 80,590 C 410,430 770,615 1440,330'" \
  -fill 'rgba(255,85,0,0.18)' -stroke none -draw "circle 1290,128 1395,128" \
  -fill 'rgba(0,60,166,0.13)' -draw "circle 145,155 235,155" \
  -fill '#ffffff' -draw "circle 1260,350 1410,350 circle 1272,552 1348,552" \
  \( "$OUTPUT_DIR/carrier-express.png" -resize 560x280 \) -geometry +350+345 -compose over -composite \
  \( "$SOURCE_DIR/choices-v2/alva.webp" -resize 300x300 -alpha set \
     \( -size 300x300 xc:none -fill white -draw 'circle 150,150 150,4' \) -compose DstIn -composite \) \
     -geometry +1110+200 -compose over -composite \
  \( "$SOURCE_DIR/choices-v2/camera.webp" -resize 145x145 -alpha set \
     \( -size 145x145 xc:none -fill white -draw 'circle 72,72 72,3' \) -compose DstIn -composite \) \
     -geometry +1200+480 -compose over -composite \
  -quality 94 "$OUTPUT_DIR/outcome-express.webp"
