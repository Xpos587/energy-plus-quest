# Observed roof tracking

Ten JSON tracks,121rows each at24fps, preserve source frame IDs. The upper40percent of observed local cab-color pixels is tracked, reducing the demonstrated redmid2 roof-to-windshield centroid jump from11.03px to2.54px maxstep. All210quartersecond source overlays were viewed; marks stay on the colored cab upperface/roof. These are image estimates, not exact3D anchors.

`source_cab_px` belongs to the original provider clip, including crop padding. `cab_px` and `cab_roof_estimate` belong to the common1280×720 padded full map after exact inverse crop placement. `city_crop_roof_estimate` belongs to the1037×720 city crop(x121..1158). Every JSON records its projection.

Retiming or rigid seam shifts must use the exact same source-row selection and translation as the video layer. Red1-mid may trim54initialframes; yellow1-mid must keep all120since it already travels left. Canonical [timing measurements](timing-receipt.json).

Semantic alpha acceptance and final fleet assembly are pending. No production/app files changed.
