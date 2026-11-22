// Scene 5 choice map: public/scene-art/lastmile-family-v1/revision-30/layout.json (design/scene-05/r30), wide plate only.
// Owner 22.11: this one drawing serves every screen; ./camera.ts only scales it to cover the stage and pans.
// Landmarks are native plate px boxes; the gift tip is where its pin points (the painted parcel is ~9 px).
export const lastmileChoiceArtwork = {
  "width": 2400,
  "height": 1800,
  "hotspots": [
    {
      "id": "helicopter",
      "x": 0.3020833333333333,
      "y": 0.7577777777777778
    },
    {
      "id": "rover",
      "x": 0.3904166666666667,
      "y": 0.7483333333333333
    },
    {
      "id": "pipe-carrier",
      "x": 0.5291666666666667,
      "y": 0.7577777777777778
    },
    {
      "id": "robot",
      "x": 0.61875,
      "y": 0.7577777777777778
    }
  ],
  "motion": {
    "rover": {
      "x": 886,
      "y": 1310,
      "w": 142,
      "h": 93,
      "image": "scene-art/lastmile-family-v1/revision-30/wide-rover.webp"
    },
    "pipe-carrier": {
      "x": 1129,
      "y": 1306,
      "w": 181,
      "h": 101,
      "image": "scene-art/lastmile-family-v1/revision-30/wide-pipe-carrier.webp"
    },
    "barge": {
      "x": 1164,
      "y": 1525,
      "w": 625,
      "h": 163,
      "image": "scene-art/lastmile-family-v1/revision-30/wide-barge.webp"
    },
    "floes": {
      "x": 0,
      "y": 1553,
      "w": 2394,
      "h": 247,
      "image": "scene-art/lastmile-family-v1/revision-30/wide-floes.webp"
    },
    "rotor": {
      "x": 540,
      "y": 1220,
      "w": 277,
      "h": 190,
      "frames": 12,
      "image": "scene-art/lastmile-family-v1/revision-30/wide-rotor.webp"
    }
  },
  "landmarks": {
    "gift": {
      "x": 1143,
      "y": 1484,
      "w": 9,
      "h": 9,
      "tip": [
        1147,
        1488
      ]
    },
    "chums": {
      "x": 460,
      "y": 343,
      "w": 154,
      "h": 94
    },
    "abk": {
      "x": 978,
      "y": 669,
      "w": 545,
      "h": 147
    },
    "helipad": {
      "x": 1233,
      "y": 558,
      "w": 211,
      "h": 67
    },
    "industry": {
      "x": 1833,
      "y": 153,
      "w": 211,
      "h": 200
    },
    "reindeer": {
      "x": 527,
      "y": 404,
      "w": 59,
      "h": 31
    },
    "windsock": {
      "x": 875,
      "y": 1256,
      "w": 57,
      "h": 58
    }
  }
};
