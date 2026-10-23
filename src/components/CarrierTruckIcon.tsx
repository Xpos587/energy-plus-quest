import { useId } from "react";
import type { MapCarrierId } from "../game/carrierFacts";

type Point = readonly [number, number, number];
const project = ([x, y, z]: Point) =>
  `${10 + x + y * 0.5},${70 + x * 0.24 - y * 0.35 - z}`;
const face = (...points: Point[]) => points.map(project).join(" ");
const palette = {
  old: { paint: "#bf5140", light: "#e18b70", shade: "#8f392e" },
  near: { paint: "#2589bc", light: "#71bce0", shade: "#12648f" },
  crew: { paint: "#4b956b", light: "#92c28e", shade: "#2e6c4a" },
  old4: { paint: "#d4a634", light: "#f1d477", shade: "#a17722" },
};

/** One projected construction for all four articulated trucks, without bitmap scaling. */
export function CarrierTruckIcon({ carrierId }: { carrierId: MapCarrierId }) {
  const id = useId().replace(/:/g, "");
  const color = palette[carrierId];
  const old = carrierId === "old" || carrierId === "old4";
  const roof = old ? 43 : 51;
  const cabFront = old ? 130 : 147;
  const cabBack = 109;
  const wheel = (x: number, y: number, key: string) => {
    const [cx, cy] = project([x, y, 6]).split(",").map(Number);
    return (
      <g key={key}>
        <ellipse cx={cx + 2} cy={cy - 1} rx="5.5" ry="7.3" fill="#162d3b" />
        <ellipse
          cx={cx}
          cy={cy}
          rx="5.4"
          ry="7.3"
          fill="#253e4c"
          stroke="#17313f"
          strokeWidth="1"
        />
        <ellipse cx={cx} cy={cy} rx="2.8" ry="4.2" fill="#a8bac1" />
        <ellipse cx={cx} cy={cy} rx="1.2" ry="2" fill="#607b8a" />
      </g>
    );
  };
  return (
    <svg
      viewBox="0 0 184 108"
      fill="none"
      aria-hidden="true"
      data-carrier-illustration={carrierId}
    >
      <defs>
        <linearGradient id={`${id}-side`} x1="0" y1="0" x2="0.1" y2="1">
          <stop stopColor={color.light} />
          <stop offset=".35" stopColor={color.paint} />
          <stop offset="1" stopColor={color.shade} />
        </linearGradient>
        <linearGradient id={`${id}-glass`} x1="0" y1="0" x2="1" y2="1">
          <stop stopColor="#b9deeb" />
          <stop offset=".5" stopColor="#6794ac" />
          <stop offset="1" stopColor="#31566c" />
        </linearGradient>
      </defs>
      <ellipse cx="99" cy="86" rx="81" ry="13" fill="#17374a" opacity=".1" />
      {[18, 30, 101, 138].map((x) => wheel(x, 27, `far-${x}`))}
      <polygon
        points={face([7, 0, 10], [152, 0, 10], [152, 30, 10], [7, 30, 10])}
        fill="#334b57"
      />
      <polygon
        points={face([7, 0, 10], [152, 0, 10], [152, 0, 15], [7, 0, 15])}
        fill="#304651"
      />
      {/* Trailer: roof, long side, front bulkhead and continuous lower rail. */}
      <polygon
        points={face([8, 0, 53], [8, 32, 53], [100, 32, 53], [100, 0, 53])}
        fill={color.light}
        stroke={color.paint}
        strokeWidth=".7"
        strokeLinejoin="round"
      />
      <polygon
        points={face([8, 0, 17], [100, 0, 17], [100, 0, 53], [8, 0, 53])}
        fill={`url(#${id}-side)`}
        stroke={color.shade}
        strokeWidth=".8"
      />
      <polygon
        points={face([100, 0, 17], [100, 32, 17], [100, 32, 53], [100, 0, 53])}
        fill={color.shade}
        stroke={color.shade}
        strokeWidth=".7"
      />
      {[19, 31, 43, 55, 67, 79, 91].map((x) => (
        <polyline
          key={x}
          points={face([x, 0, 19], [x, 0, 51], [x, 32, 51])}
          stroke="#fff"
          opacity=".18"
          strokeWidth=".8"
        />
      ))}
      <polyline
        points={face([9, 0, 52], [99, 0, 52], [99, 32, 52])}
        stroke="#fff"
        opacity=".42"
        strokeWidth="1"
      />
      <polyline
        points={face([8, -0.2, 18], [100, -0.2, 18])}
        stroke="#d3dce0"
        strokeWidth="2"
      />
      <polyline
        points={face([11, -0.4, 20], [96, -0.4, 20])}
        stroke="#fff0bd"
        opacity=".7"
        strokeWidth=".7"
      />
      {[17, 52, 89].map((x) => (
        <polygon
          key={x}
          points={face(
            [x, -0.6, 21],
            [x + 3, -0.6, 21],
            [x + 3, -0.6, 22.5],
            [x, -0.6, 22.5],
          )}
          fill="#f6d27b"
        />
      ))}
      {old && (
        <>
          <polyline
            points={face([106, 26, 15], [106, 26, 52])}
            stroke="#5c6b6d"
            strokeWidth="2.5"
          />
          <polyline
            points={face([13, -0.6, 24], [23, -0.6, 22], [28, -0.6, 24])}
            stroke={color.shade}
            opacity=".55"
            strokeWidth="1.2"
          />
        </>
      )}
      {/* Cab shares the trailer projection; old trucks retain their bonnet. */}
      <polygon
        points={face(
          [cabBack, 0, 15],
          [cabFront, 0, 15],
          [cabFront, 0, roof],
          [cabBack, 0, roof],
        )}
        fill={color.paint}
        stroke={color.shade}
        strokeWidth=".8"
        strokeLinejoin="round"
      />
      <polygon
        points={face(
          [cabBack, 0, roof],
          [cabBack, 30, roof],
          [cabFront, 30, roof],
          [cabFront, 0, roof],
        )}
        fill={color.light}
        stroke={color.paint}
        strokeWidth=".7"
      />
      <polygon
        points={face(
          [cabFront, 0, 15],
          [cabFront, 30, 15],
          [cabFront, 30, roof],
          [cabFront, 0, roof],
        )}
        fill={color.shade}
        stroke={color.shade}
        strokeWidth=".8"
      />
      <polygon
        points={face(
          [116, -0.5, 29],
          [cabFront - 3, -0.5, 29],
          [cabFront - 3, -0.5, roof - 5],
          [116, -0.5, roof - 5],
        )}
        fill={`url(#${id}-glass)`}
        stroke="#315365"
        strokeWidth="1"
      />
      <polygon
        points={face(
          [cabFront + 0.3, 3, roof - 5],
          [cabFront + 0.3, 27, roof - 5],
          [cabFront + 0.3, 27, old ? 28 : 30],
          [cabFront + 0.3, 3, old ? 28 : 30],
        )}
        fill={`url(#${id}-glass)`}
        stroke="#274e63"
        strokeWidth="1"
      />
      <polyline
        points={face(
          [cabFront + 0.5, 5, roof - 7],
          [cabFront + 0.5, 24, roof - 7],
        )}
        stroke="#e0f3fa"
        opacity=".65"
        strokeWidth="1.4"
      />
      <polyline
        points={face([114, -0.7, 17], [114, -0.7, roof - 4])}
        stroke={color.shade}
        opacity=".65"
        strokeWidth=".7"
      />
      <polyline
        points={face([117, -0.8, 25], [121, -0.8, 25])}
        stroke="#d4e0e4"
        strokeWidth="1.4"
      />
      {old && (
        <>
          <polygon
            points={face(
              [130, 0, 25],
              [130, 30, 25],
              [151, 30, 25],
              [151, 0, 25],
            )}
            fill={color.light}
          />
          <polygon
            points={face(
              [130, 0, 15],
              [151, 0, 15],
              [151, 0, 25],
              [130, 0, 25],
            )}
            fill={color.paint}
          />
          <polygon
            points={face(
              [151, 0, 15],
              [151, 30, 15],
              [151, 30, 25],
              [151, 0, 25],
            )}
            fill={color.shade}
          />
        </>
      )}
      {(() => {
        const front = old ? 151.5 : 147.5;
        return (
          <>
            <polygon
              points={face(
                [front, 6, 16],
                [front, 24, 16],
                [front, 24, 23],
                [front, 6, 23],
              )}
              fill="#344e5c"
            />
            {[18, 20, 22].map((z) => (
              <polyline
                key={z}
                points={face([front + 0.2, 7, z], [front + 0.2, 23, z])}
                stroke="#8b9da5"
                strokeWidth=".6"
              />
            ))}
            {[2, 26].map((y) => (
              <polygon
                key={y}
                points={face(
                  [front + 0.3, y, 18],
                  [front + 0.3, y + 3, 18],
                  [front + 0.3, y + 3, 22],
                  [front + 0.3, y, 22],
                )}
                fill="#f4f1cf"
              />
            ))}
            <polyline
              points={face([front, 0, 14], [front, 30, 14])}
              stroke="#c0cdd3"
              strokeWidth="3"
            />
          </>
        );
      })()}
      <polyline
        points={face(
          [cabFront + 1, -2, 36],
          [cabFront + 1, -5, 36],
          [cabFront + 1, -5, 31],
        )}
        stroke="#334e60"
        strokeWidth="1.3"
        strokeLinecap="round"
      />
      <polygon
        points={face(
          [cabFront, -6, 31],
          [cabFront + 2, -6, 31],
          [cabFront + 2, -6, 36],
          [cabFront, -6, 36],
        )}
        fill="#426172"
      />
      {[18, 30, 101, 138].map((x) => wheel(x, -0.7, `near-${x}`))}
      <polyline
        points={face([125, -1, 11], [129, -1, 11])}
        stroke="#c9d5da"
        strokeWidth="2"
      />
    </svg>
  );
}
