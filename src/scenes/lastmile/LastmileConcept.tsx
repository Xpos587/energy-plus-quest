import type { ParcelId } from "../../game/types";
import type { SceneContext } from "../types";

const navy = "#041327";
const blue = "#205ac6";
const orange = "#ff5500";

type VehicleKind = "helicopter" | "rover" | "robot" | "pipe-carrier" | "drone";

function Gift({
  parcel,
  x = 0,
  y = 0,
}: {
  parcel: ParcelId;
  x?: number;
  y?: number;
}) {
  return (
    <g transform={`translate(${x} ${y})`} data-parcel={parcel}>
      <rect
        x="-25"
        y="-23"
        width="50"
        height="40"
        rx="5"
        fill={orange}
        stroke={navy}
        strokeWidth="3"
      />
      {parcel === "camera" ? (
        <g fill="white">
          <rect x="-15" y="-12" width="30" height="21" rx="4" />
          <circle cy="-2" r="7" fill={orange} />
          <path d="M-10-12v-5h10v5" />
        </g>
      ) : parcel === "boat" ? (
        <g fill="none" stroke="white" strokeWidth="3">
          <ellipse cy="-3" rx="18" ry="9" />
          <path d="m-11 7 22-21" />
        </g>
      ) : (
        <path
          d="M-10-15v17l-7 5q-2 7 6 7l12-9v-20zm16 0v17l-5 4 5 5 11-7v-19z"
          fill="white"
        />
      )}
    </g>
  );
}

function Pipes({ x = 0, y = 0 }: { x?: number; y?: number }) {
  return (
    <g
      transform={`translate(${x} ${y})`}
      data-cargo="pipes"
      stroke={navy}
      strokeWidth="3"
    >
      {[0, 12, 24].map((dy) => (
        <g key={dy}>
          <rect
            x="-43"
            y={dy - 10}
            width="85"
            height="12"
            rx="6"
            fill="#a3b4be"
          />
          <circle cx="38" cy={dy - 4} r="5" fill="#eef4f5" />
        </g>
      ))}
    </g>
  );
}

function Vehicle({
  kind,
  x,
  y,
  scale = 1,
}: {
  kind: VehicleKind;
  x: number;
  y: number;
  scale?: number;
}) {
  return (
    <g
      transform={`translate(${x} ${y}) scale(${scale})`}
      data-vehicle={kind}
      stroke={navy}
      strokeWidth="4"
      strokeLinejoin="round"
    >
      {kind === "helicopter" ? (
        <>
          <path d="m-34-7-54-13-13-21-8 2 9 41 66 8" fill={blue} />
          <path
            d="M-47-13Q-20-45 22-28L55-5Q72 21 30 27H-26Q-52 23-47-13Z"
            fill={blue}
          />
          <path d="m9-27 29 22H5Z" fill="#d3eef1" />
          <path
            d="M-12-34v-19m-76 0H73M-30 28l-6 13m64-13 9 13m-86 0h103"
            fill="none"
            strokeLinecap="round"
          />
        </>
      ) : kind === "rover" ? (
        <>
          <path d="M-66 1v-47h85l32 24 8 26Z" fill={blue} />
          <path d="M-52-35h33v24h-33zm46 0h19l27 24H-6Z" fill="#d3eef1" />
          {[-40, 38].map((cx) => (
            <g key={cx}>
              <circle cx={cx} cy="13" r="28" fill={navy} />
              <circle cx={cx} cy="13" r="12" fill="#9aabb6" />
            </g>
          ))}
        </>
      ) : kind === "robot" ? (
        <>
          <rect x="-47" y="-31" width="94" height="44" rx="12" fill="#f4f7f7" />
          <path d="M-30-31v-14h44v14" fill="#a3b4be" />
          <path d="M-28-13H20" stroke={blue} strokeWidth="7" />
          <circle cx="32" cy="-8" r="5" fill={orange} />
          {[-29, 29].map((cx) => (
            <circle key={cx} cx={cx} cy="17" r="10" fill={navy} />
          ))}
        </>
      ) : kind === "pipe-carrier" ? (
        <>
          <rect x="-82" y="4" width="162" height="31" rx="16" fill={navy} />
          {[-64, -36, -8, 20, 48, 66].map((cx) => (
            <circle
              key={cx}
              cx={cx}
              cy="20"
              r="9"
              fill="#a3b4be"
              strokeWidth="2"
            />
          ))}
          <path d="M-85 2v-46h37l20 23V2Z" fill={blue} />
          <path d="M-75-36h22l13 16h-35Z" fill="#d3eef1" />
          <path d="M-24 0h105" strokeWidth="9" />
          <Pipes x={28} y={-32} />
        </>
      ) : (
        <>
          <path d="m-38-10 76 0m-65-13L0 0l27-23" fill="none" />
          <ellipse cx="-39" cy="-14" rx="25" ry="5" fill="#a3b4be" />
          <ellipse cx="39" cy="-14" rx="25" ry="5" fill="#a3b4be" />
          <rect x="-14" y="-8" width="28" height="16" rx="5" fill={blue} />
          <path d="m-9 10-7 18m25-18 7 18" />
        </>
      )}
    </g>
  );
}

function NumberLabel({
  number,
  x,
  y,
  label,
}: {
  number: number;
  x: number;
  y: number;
  label: string;
}) {
  return (
    <g transform={`translate(${x} ${y})`}>
      <circle r="22" fill={navy} />
      <text
        textAnchor="middle"
        y="8"
        fill="white"
        fontSize="25"
        fontWeight="700"
      >
        {number}
      </text>
      <text x="34" y="8" fill={navy} fontSize="25" fontWeight="700">
        {label}
      </text>
    </g>
  );
}

export function LastmileConcept({
  context,
  format,
  outcome,
}: {
  context: SceneContext;
  format: "desktop" | "mobile";
  outcome?: string;
}) {
  const mobile = format === "mobile";
  const width = mobile ? 900 : 1200;
  const height = mobile ? 1200 : 1000;
  const dock = mobile ? { x: 175, y: 200 } : { x: 155, y: 430 };
  const bog = mobile ? { x: 380, y: 390 } : { x: 430, y: 450 };
  const river = mobile ? { x: 480, y: 645 } : { x: 765, y: 440 };
  const end = mobile ? { x: 670, y: 840 } : { x: 1010, y: 380 };
  const extraLeg = outcome === "helicopter" && context.recipient !== "arseniy";
  const rescue =
    outcome === "pipe-carrier"
      ? context.parcel === "boat"
        ? "rover"
        : "drone"
      : undefined;
  const activePosition =
    outcome === "robot"
      ? bog
      : outcome === "pipe-carrier"
        ? { x: river.x - (mobile ? 0 : 115), y: river.y - (mobile ? 100 : 0) }
        : river;
  return (
    <svg
      viewBox={`0 0 ${width} ${height}`}
      width="100%"
      height="100%"
      role="img"
      aria-label="Плоская карта доставки: причал, болото, речка с первым льдом и получатель"
      data-concept="lastmile"
      data-concept-format={format}
      data-outcome={outcome ?? "choice"}
      data-rescue={rescue}
      data-extra-leg={extraLeg ? "rover-10km" : undefined}
      style={{ display: "block", fontFamily: "inherit" }}
    >
      <rect width={width} height={height} fill="#eef4f5" />
      <path
        d={
          mobile
            ? "M0 40Q210 10 410 120T900 90V1040Q690 1080 440 1010T0 1070Z"
            : "M0 190Q160 90 340 180T720 150T1200 210V780Q940 860 690 740T0 800Z"
        }
        fill="#dde7d8"
      />
      <g fill="#b8cbb5">
        {(mobile
          ? [
              [690, 210],
              [730, 370],
              [150, 610],
              [190, 840],
              [460, 920],
            ]
          : [
              [240, 210],
              [550, 250],
              [1000, 680],
              [390, 660],
              [1120, 260],
            ]
        ).map(([x, y]) => (
          <g key={`${x}-${y}`} transform={`translate(${x} ${y})`}>
            <path d="m0-30-20 40h40Zm25 0-17 35h34Z" />
            <path d="M0 10v18m25-3v-15" stroke="#779271" strokeWidth="4" />
          </g>
        ))}
      </g>
      {/* The river spans the map; there is deliberately no bridge or road over it. */}
      <path
        d={
          mobile
            ? "M0 576Q180 542 370 591T900 577V715Q610 765 355 711T0 724Z"
            : "M683 0Q625 180 694 357T681 700T703 1000H844Q785 803 837 633T824 327T838 0Z"
        }
        fill="#abd5e5"
        data-obstacle="river"
      />
      <g fill="#eef9fa" stroke="#7eb5cb" strokeWidth="2">
        {(mobile
          ? [
              [115, 626],
              [280, 681],
              [590, 630],
              [768, 677],
            ]
          : [
              [735, 120],
              [778, 265],
              [743, 590],
              [775, 810],
            ]
        ).map(([x, y]) => (
          <path
            key={`${x}-${y}`}
            d={`M${x - 25} ${y}l22-15 33 9-15 20-28 4Z`}
          />
        ))}
      </g>
      <g transform={`translate(${bog.x} ${bog.y})`} data-obstacle="bog">
        <path
          d="M-125-60Q-90-110 1-76T146-38Q191 19 99 74T-116 66Q-167 21-125-60Z"
          fill="#9cac86"
        />
        <g fill="#728e76">
          <ellipse cx="-56" cy="22" rx="41" ry="14" />
          <ellipse cx="62" cy="-20" rx="48" ry="13" />
          <ellipse cx="37" cy="53" rx="29" ry="9" />
        </g>
        <path
          d="m-96-23-5-25m5 25 10-24m79 89-4-24m4 24 12-22m95-32 6-24m-6 24-8-18"
          stroke="#607850"
          strokeWidth="4"
        />
      </g>
      <NumberLabel number={1} x={bog.x - 95} y={bog.y - 110} label="Болото" />
      <NumberLabel
        number={2}
        x={mobile ? 290 : 727}
        y={mobile ? 550 : 230}
        label={mobile ? "Речка · первый лёд" : "Первый лёд"}
      />
      <g transform={`translate(${dock.x} ${dock.y})`} data-location="quay">
        <path d="M-155 44h260v78h-260Z" fill="#abd5e5" />
        <path
          d="M-107 42H94L68 95H-80Z"
          fill={blue}
          stroke={navy}
          strokeWidth="4"
        />
        <rect x="-109" y="-20" width="227" height="50" rx="5" fill="#c0c9c9" />
        <path
          d="M-90 30v20m60-20v20m60-20v20m60-20v20"
          stroke={navy}
          strokeWidth="6"
        />
        <Pipes x={-10} y={22} />
        {!outcome && <Gift parcel={context.parcel} x={60} y={12} />}
        <text
          textAnchor="middle"
          y="151"
          fill={navy}
          fontSize="27"
          fontWeight="700"
        >
          Причал
        </text>
        {outcome === "pipe-carrier" && (
          <>
            <Pipes x={-22} y={-31} />
            <text x="0" y="184" textAnchor="middle" fontSize="20" fill={navy}>
              Трубы возвращены
            </text>
          </>
        )}
      </g>
      <g transform={`translate(${end.x} ${end.y})`} data-location="recipient">
        <g
          opacity={context.recipient === "arseniy" ? 1 : 0.6}
          transform={
            context.recipient === "arseniy"
              ? "translate(0 0)"
              : "translate(-50 -60) scale(.55)"
          }
        >
          <rect
            x="-60"
            y="-55"
            width="120"
            height="80"
            rx="5"
            fill="white"
            stroke={navy}
            strokeWidth="4"
          />
          <rect x="-61" y="-61" width="122" height="15" fill={blue} />
          {[-40, -8, 24].map((x) => (
            <rect key={x} x={x} y="-29" width="20" height="22" fill="#abd5e5" />
          ))}
          <text textAnchor="middle" y="55" fontSize="23" fill={navy}>
            АБК
          </text>
        </g>
        {context.recipient !== "arseniy" && (
          <>
            <path
              d="M25-49-40 60H90Z"
              fill="#f1e3cb"
              stroke={navy}
              strokeWidth="4"
            />
            <path d="m25-49 10 109H12Z" fill="#bd9a74" />
            <path d="m20-58 14 22m-5-22-14 22" stroke={navy} strokeWidth="4" />
          </>
        )}
        <circle cx="105" cy="17" r="13" fill="#d6a47c" />
        <path d="M86 69V38q19-20 38 0v31" fill={orange} />
        <path d="m96 69-4 25m23-25 4 25" stroke={navy} strokeWidth="8" />
        <text
          x="40"
          y="127"
          textAnchor="middle"
          fill={navy}
          fontSize="27"
          fontWeight="700"
        >
          {context.recipient === "arseniy"
            ? "Арсений"
            : context.recipient === "alva"
              ? "Альва"
              : "Хор"}
        </text>
      </g>
      {outcome && outcome !== "helicopter" && (
        <>
          <Vehicle
            kind={outcome as VehicleKind}
            x={activePosition.x}
            y={activePosition.y}
            scale={0.94}
          />
          {outcome === "robot" ? (
            <g data-event="stuck-in-ground">
              <path
                d={`M${bog.x - 60} ${bog.y + 18}q60 25 120 0v22h-120Z`}
                fill="#7c8062"
              />
              <Gift parcel={context.parcel} x={bog.x} y={bog.y - 54} />
            </g>
          ) : outcome === "rover" ? (
            <g data-event="swimming">
              <path
                d={`M${river.x - 82} ${river.y + 24}q30-14 55 0t55 0t55 0`}
                fill="none"
                stroke="#4d9fbf"
                strokeWidth="7"
              />
              <Gift parcel={context.parcel} x={river.x} y={river.y - 72} />
            </g>
          ) : (
            <g data-event="stopped-at-water">
              <path
                d={`M${activePosition.x + 85} ${activePosition.y - 50}v85`}
                stroke={orange}
                strokeWidth="7"
              />
              <Vehicle
                kind={rescue!}
                x={mobile ? 640 : 896}
                y={mobile ? 648 : 500}
                scale={0.75}
              />
              <Gift
                parcel={context.parcel}
                x={mobile ? 640 : 896}
                y={
                  mobile
                    ? rescue === "drone"
                      ? 688
                      : 595
                    : rescue === "drone"
                      ? 541
                      : 447
                }
              />
            </g>
          )}
        </>
      )}
      {outcome === "helicopter" && (
        <g data-event="air-delivery">
          <Vehicle
            kind="helicopter"
            x={mobile ? 570 : 970}
            y={mobile ? 180 : 125}
            scale={1.05}
          />
          <path
            d={mobile ? "M480 205v36" : "M920 150v35"}
            stroke={navy}
            strokeWidth="3"
          />
          <Pipes x={mobile ? 480 : 920} y={mobile ? 249 : 194} />
          {extraLeg ? (
            <>
              <Vehicle
                kind="rover"
                x={mobile ? 400 : 985}
                y={mobile ? 875 : 580}
                scale={0.7}
              />
              <Gift
                parcel={context.parcel}
                x={mobile ? 400 : 985}
                y={mobile ? 827 : 532}
              />
              <text
                x={mobile ? 300 : 890}
                y={mobile ? 944 : 650}
                fill={navy}
                fontSize="23"
                fontWeight="700"
              >
                Ещё ≥ 10 км
              </text>
            </>
          ) : (
            <Gift parcel={context.parcel} x={end.x + 58} y={end.y + 70} />
          )}
        </g>
      )}
      {!outcome && (
        <g data-transport-options="illustrated">
          <rect
            x="28"
            y={mobile ? 1012 : 770}
            width={width - 56}
            height={mobile ? 176 : 210}
            rx="24"
            fill="white"
          />
          {(["helicopter", "rover", "robot", "pipe-carrier"] as const).map(
            (kind, i) => {
              const x = mobile ? 150 + i * 200 : 175 + i * 280;
              const y = mobile ? 1080 : 850;
              return (
                <g key={kind}>
                  <Vehicle
                    kind={kind}
                    x={x}
                    y={y}
                    scale={mobile ? 0.74 : 0.9}
                  />
                  <circle cx={x - 72} cy={y - 53} r="17" fill="white" />
                  <text
                    x={x - 72}
                    y={y - 47}
                    textAnchor="middle"
                    fontSize="20"
                    fill={navy}
                  >
                    {i + 1}
                  </text>
                </g>
              );
            },
          )}
        </g>
      )}
    </svg>
  );
}
