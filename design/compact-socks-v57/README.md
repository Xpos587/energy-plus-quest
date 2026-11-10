# Scene 2 socks — v57, approved

The client review on 10 November requires a red strap **in front of** the
secured box, consistent socks and a readable pair count. Copy and score icons
are unchanged. This candidate has **two pairs**: cream/blue/orange Nordic and
red/grey striped (four socks).

## Source and reproduction

`place1-box.png` is the existing Higgsfield `nano_banana_pro` illustration of the
damaged cardboard box and spilled socks. The current revision makes no new
image-generation request. `scripts/compose-socks-v57.py` extracts the actual
Nordic pair and striped sock from that source, duplicates the striped sock,
and reuses them inside every secured box. The stray green sock is excluded
from the unsecured result and replaced by that same striped sock.

```sh
uv run --with pillow --with numpy --with scipy python scripts/compose-socks-v57.py
```

The script produces the four `public/compact-art/socks-*-v57.png` files.
Places 2–4 use the identical 124×44-pixel box; auto uses place 3. They rest on
the dishes cloth, the top carton and the cargo-bay floor, respectively. The
place-4 lower strap is moved down to meet the box. All straps are composited
last, including their metal buckles. No drop shadows are added. Assertions
check common box size, cargo bounds and foreground-strap pixels.

Place 1 retains the previously reviewed damaged box and spilled arrangement.
Its projected silhouette differs because it is damaged and viewed on its side;
it is not a second, deliberately larger package.

`CompactArt.tsx` moves only the socks place-3 **result badge** to the left;
choice hit areas, other gifts and layout-editor coordinates are unchanged.
The focused regression lives in `compact-camera.test.tsx`.

Binary media are local and excluded from Git by repository policy. The
coordinator must publish approved media through the existing artifact workflow
before a source deployment. Michael accepted this candidate and authorized its
commit in the client-review form on 10 November 2026 at 21:20:02Z (question
`socks`, choice `accept`: «Принять и разрешить коммит»). Push and deployment
are not included in that approval.
