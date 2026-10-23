# Keeper illustration proof — local comparison only

Review `keeper-v3-v5-paired-proof.png` at native display size or `keeper-v3-v5-paired-proof-3x.png` for detail. Left is the existing v3 source crop; right is the illustrated keeper in the same context. No production routes or source files changed.

The native RGBA sprite is unmodified. A Blender camera-facing card samples its character texture bounds and applies an explicit alpha cutoff of 192/255 in the shader to remove broad low-alpha glow. It emits only for camera rays, while the existing 3D keeper is hidden only from camera rays and retains its original shadow. The card does not cast another shadow or illuminate the room.

V4's physical z0–z1.76 centerline mapping made the sprite's feet appear above the existing shoe footprint. That candidate is retained as rejected scale evidence. V5 matches the actual evaluated v3 head/shoe projection envelope, including shoe depth: top y640.9903, bottom y760.9926 in the full 1440×1000 source. Its width fits inside the previous horizontal silhouette. Physical reference landmarks remain (9.8,2.3,0) and (9.8,2.3,1.76); camera-facing card dimensions compensate for projection and are not a new physical human dimension.

`keeper-v5-native-render.png` retains the raw 250×200 regional Blender output. Cycles regional denoising/sample differences also change unrelated context pixels. The review proof therefore preserves decoded v3 source pixels outside the keeper's old/new projection union plus a two-pixel margin; this operation does not edit the native sprite. `keeper-v5-context-equality.json` records 42,692 protected pixels with zero channel differences. The mask and raw render are retained for inspection.

Scene: `design/warehouse-finish-2026-10-22/warehouse-keeper-proof-v5.blend`. This is a local style experiment. It is not an accepted scene, full-frame render or production promotion. No other objects have received illustration treatment.
