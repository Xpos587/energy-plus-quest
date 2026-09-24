import type { SceneArtProps } from "../types";

const ink = "#041327";
const blue = "#205ac6";
const orange = "#ff5500";

type Props = SceneArtProps & { format: "desktop" | "mobile" };

function Operator({
  x,
  y,
  name,
  mood = "happy",
  scale = 1,
}: {
  x: number;
  y: number;
  name: string;
  mood?: "happy" | "tired" | "sad" | "surprised";
  scale?: number;
}) {
  return (
    <g
      transform={`translate(${x} ${y}) scale(${scale})`}
      data-operator={name}
      data-mood={mood}
    >
      <path d="M-25 64 Q-24 30 0 29 Q24 30 25 64Z" fill={blue} />
      <path d="M-19 43H19M-20 51H20" stroke="#d7f1ee" strokeWidth="5" />
      <path d="M-8 63V83M10 63V83" stroke={ink} strokeWidth="11" />
      <rect x="-15" y="0" width="30" height="34" rx="13" fill="#d99466" />
      <path d="M-20 9Q-20-13 0-13Q20-13 20 9Z" fill={orange} />
      <path d="M-23 10H23M0-12V3" stroke={ink} strokeWidth="3" />
      <path
        d={mood === "tired" ? "M-8 19H-3M4 19H9" : "M-7 18V20M7 18V20"}
        stroke={ink}
        strokeWidth="3"
        strokeLinecap="round"
      />
      {mood === "surprised" ? (
        <ellipse cx="0" cy="27" rx="3" ry="4" fill={ink} />
      ) : (
        <path
          d={mood === "sad" ? "M-5 28Q0 23 5 28" : "M-5 26Q0 32 5 26"}
          fill="none"
          stroke={ink}
          strokeWidth="2"
        />
      )}
      {mood === "tired" && (
        <path d="M29 9Q20 23 29 25Q38 23 29 9" fill="#abd5e5" />
      )}
    </g>
  );
}

function Gift({
  x,
  y,
  parcel,
  location,
}: {
  x: number;
  y: number;
  parcel: Props["context"]["parcel"];
  location: string;
}) {
  return (
    <g
      transform={`translate(${x} ${y})`}
      data-gift-type={parcel}
      data-gift-location={location}
    >
      <rect x="-65" y="22" width="130" height="12" rx="3" fill={ink} />
      {parcel === "boat" ? (
        <>
          <path
            d="M-62 9Q-36-25 0-25Q36-25 62 9Q36 27 0 27Q-36 27-62 9Z"
            fill={orange}
            stroke={ink}
            strokeWidth="3"
          />
          <ellipse cx="0" cy="0" rx="40" ry="12" fill="#ffd6b9" />
          <path d="M-31-14V18M31-14V18" stroke={ink} strokeWidth="5" />
        </>
      ) : (
        <>
          <rect
            x="-42"
            y="-42"
            width="84"
            height="67"
            rx="5"
            fill="#ffbb86"
            stroke={ink}
            strokeWidth="3"
          />
          <path d="M0-42V25M-42-12H42" stroke={orange} strokeWidth="9" />
          <rect x="-25" y="-30" width="50" height="43" rx="5" fill="#fff" />
          {parcel === "camera" ? (
            <>
              <rect x="-18" y="-17" width="36" height="23" rx="4" fill={ink} />
              <circle cx="2" cy="-6" r="8" fill="#abd5e5" />
              <path d="M-10-17V-22H1V-17" fill={ink} />
            </>
          ) : (
            <path
              d="M-14-23H-3V-3L-12 6Q-23 8-23 0L-14-6ZM6-23H17V-3L8 6Q-3 8-3 0L6-6Z"
              fill={orange}
            />
          )}
        </>
      )}
    </g>
  );
}

function Crane({
  x,
  ground,
  scale = 1,
  operator,
  mood,
  far = false,
}: {
  x: number;
  ground: number;
  scale?: number;
  operator?: string;
  mood?: "sad" | "happy";
  far?: boolean;
}) {
  return (
    <g
      transform={`translate(${x} ${ground}) scale(${scale})`}
      data-crane={far ? "far" : "near"}
    >
      <path
        d="M-46 0L-22-205H22L46 0M-35-45H35M-29-105H29M-23-166H23"
        fill="none"
        stroke={far ? "#648a99" : blue}
        strokeWidth="15"
        strokeLinejoin="round"
      />
      <path
        d="M-35-45L28-105L-23-166L22-205M35-45L-28-105L23-166L-22-205"
        fill="none"
        stroke={far ? "#648a99" : blue}
        strokeWidth="5"
      />
      <path
        d="M-18-206L10-325L180-230L-18-206Z"
        fill="none"
        stroke={far ? "#648a99" : blue}
        strokeWidth="12"
        strokeLinejoin="round"
      />
      <path
        d="M10-325L40-216L75-288L105-221L138-253L180-230"
        fill="none"
        stroke={far ? "#648a99" : blue}
        strokeWidth="4"
      />
      <path
        d="M176-230V-80M166-80H186M176-80V-65Q194-63 187-48Q178-36 169-47"
        fill="none"
        stroke={ink}
        strokeWidth="4"
      />
      <rect
        x="-51"
        y="-240"
        width="71"
        height="51"
        rx="5"
        fill={far ? "#d5e5e8" : "#f7bd77"}
        stroke={ink}
        strokeWidth="3"
      />
      <rect x="-43" y="-234" width="53" height="37" rx="3" fill="#eaf5f7" />
      {operator && (
        <Operator x={-16} y={-221} name={operator} mood={mood} scale={0.43} />
      )}
      <path d="M-15-185V0M-6-185V0" stroke={ink} strokeWidth="2" />
      {Array.from({ length: 13 }, (_, i) => (
        <path
          key={i}
          d={`M-15 ${-180 + i * 14}H-6`}
          stroke={ink}
          strokeWidth="2"
        />
      ))}
      <rect x="-61" y="-8" width="122" height="15" rx="4" fill={ink} />
    </g>
  );
}

export function CraneConcept({
  format,
  context,
  selectedId,
  showResult,
}: Props) {
  const mobile = format === "mobile";
  const width = mobile ? 900 : 1200;
  const height = mobile ? 1100 : 900;
  const outcome = showResult ? selectedId : undefined;
  const loaded = !!outcome && outcome !== "wait";
  const leaving = !!outcome;
  const quay = mobile ? 650 : 495;
  const officeX = mobile ? 150 : 290;
  const officeY = mobile ? 332 : 220;
  const bargeX = mobile ? (leaving ? 620 : 500) : leaving ? 795 : 700;
  const bargeY = mobile ? 815 : 640;
  const nearX = mobile ? 500 : 605;
  const farX = mobile ? 665 : 925;
  const giftX = mobile ? 367 : 470;
  return (
    <svg
      viewBox={`0 0 ${width} ${height}`}
      width="100%"
      height="100%"
      role="img"
      aria-label={`Плоская иллюстрация причала на Оби. Два крана, офис ПРУ и баржа с трубами. ${loaded ? "Подарок на барже." : "Подарок на причале."}`}
      data-concept="crane"
      data-outcome={outcome ?? "choice"}
      data-barge-departing={leaving}
      style={{ display: "block", fontFamily: "inherit" }}
    >
      <rect width={width} height={height} fill="#eef4f5" />
      <circle cx={width - 105} cy="103" r="43" fill="#ffe5b0" />
      <path
        d={`M0 ${quay - 166}Q120 ${quay - 210} 230 ${quay - 180}T520 ${quay - 174}T${width} ${quay - 180}V${quay}H0Z`}
        fill="#d6e3dc"
      />
      <rect y={quay} width={width} height={height - quay} fill="#abd5e5" />
      <path
        d={`M0 ${quay + 98}H${width}M0 ${quay + 267}H${width}M60 ${height - 46}H${width - 55}`}
        stroke="#cbe8ef"
        strokeWidth="3"
      />
      <g data-distant-quay="true">
        <rect y={quay - 84} width={width} height="37" fill="#becdcf" />
        <path
          d={`M0 ${quay - 63}H${width}`}
          stroke="#446a7d"
          strokeWidth="12"
        />
        {[width - 200, width - 65].map((x) => (
          <path
            key={x}
            d={`M${x} ${quay - 57}V${quay + 37}`}
            stroke="#7a959d"
            strokeWidth="15"
          />
        ))}
      </g>
      <path
        d={`M0 ${quay - 74}H${mobile ? 700 : 770}V${quay + 17}H0Z`}
        fill="#d3d9d6"
      />
      <path d={`M0 ${quay}H${mobile ? 700 : 770}V${quay + 21}H0Z`} fill={ink} />
      {[80, 270, 460, 650].map((x) => (
        <path
          key={x}
          d={`M${x} ${quay + 18}V${quay + 72}`}
          stroke="#7a959d"
          strokeWidth="17"
        />
      ))}
      <g
        transform={`translate(${mobile ? 15 : 18} ${quay - (mobile ? 262 : 195)})`}
      >
        <path d="M0 30L97 0L194 30V185H0Z" fill="#d5e1e3" />
        <rect x="12" y="78" width="165" height="107" fill="#7d9ba7" />
        {[105, 130, 155].map((y) => (
          <path key={y} d={`M12 ${y}H177`} stroke="#b8ccd2" strokeWidth="3" />
        ))}
        <text
          x="96"
          y="57"
          textAnchor="middle"
          fill={ink}
          fontSize="19"
          fontWeight="700"
        >
          СКЛАД
        </text>
      </g>
      <Crane
        x={farX}
        ground={quay - 77}
        scale={mobile ? 0.78 : 0.85}
        far
        operator={outcome === "petr" ? undefined : "Пётр"}
      />
      <Crane
        x={nearX}
        ground={quay - 12}
        scale={mobile ? 0.92 : 1}
        operator={outcome === "petr" ? "Пётр" : undefined}
        mood={outcome === "petr" ? "sad" : undefined}
      />
      <g
        transform={`translate(${officeX} ${officeY})`}
        data-office-console={outcome === "remote" ? "active" : "idle"}
      >
        <path
          d={`M24 208V${quay - officeY - 20}M164 208V${quay - officeY - 20}M24 220L164 ${quay - officeY - 20}M164 220L24 ${quay - officeY - 20}`}
          fill="none"
          stroke={blue}
          strokeWidth="8"
        />
        <rect
          width="188"
          height="208"
          fill="#fff"
          stroke={ink}
          strokeWidth="3"
        />
        <rect x="-8" y="-12" width="204" height="24" rx="3" fill={blue} />
        <text x="18" y="42" fill={ink} fontSize="25" fontWeight="700">
          ПРУ
        </text>
        <rect x="17" y="60" width="154" height="112" rx="4" fill="#dcecf0" />
        {outcome !== "rush" && (
          <Operator
            x={outcome === "remote" ? 68 : 92}
            y={91}
            name="Иван"
            mood={outcome === "wait" ? "surprised" : "happy"}
            scale={0.82}
          />
        )}
        {outcome === "remote" && (
          <g data-remote-console="true">
            <path
              d="M40 133V159H86M59 159V175"
              fill="none"
              stroke={ink}
              strokeWidth="9"
            />
            <rect x="101" y="97" width="50" height="34" rx="4" fill={ink} />
            <path
              d="M111 119L121 109L131 119L141 105"
              fill="none"
              stroke="#80ddc0"
              strokeWidth="3"
            />
            <path
              d="M94 143H156M108 143V175M143 143V175"
              stroke={ink}
              strokeWidth="5"
            />
            <path d="M91 143V130" stroke={orange} strokeWidth="5" />
          </g>
        )}
        {outcome === "wait" && (
          <g data-wait-clock="true">
            <circle
              cx="146"
              cy="87"
              r="19"
              fill="#fff"
              stroke={ink}
              strokeWidth="3"
            />
            <path
              d="M146 73V87L158 93"
              fill="none"
              stroke={ink}
              strokeWidth="3"
            />
          </g>
        )}
        <path d="M17 181H171" stroke={blue} strokeWidth="7" />
      </g>
      {outcome === "rush" && (
        <Operator
          x={officeX + 214}
          y={quay - 128}
          name="Иван"
          mood="tired"
          scale={1.05}
        />
      )}
      <g
        transform={`translate(${mobile ? 40 : 210} ${quay - 40})`}
        data-autonomous-tractor="true"
      >
        <rect x="0" y="-24" width="78" height="35" rx="8" fill={blue} />
        <rect
          x="11"
          y="-43"
          width="31"
          height="23"
          rx="5"
          fill="#dcecf0"
          stroke={ink}
          strokeWidth="3"
        />
        <path d="M26-43V-51M19-51H33" stroke={ink} strokeWidth="3" />
        <circle cx="17" cy="14" r="12" fill={ink} />
        <circle cx="62" cy="14" r="12" fill={ink} />
        <path d="M80 0H151M112 0V17" stroke={ink} strokeWidth="5" />
        <circle cx="136" cy="16" r="10" fill={ink} />
      </g>
      {!loaded && (
        <Gift x={giftX} y={quay - 55} parcel={context.parcel} location="quay" />
      )}
      {outcome === "petr" && (
        <g
          transform={`translate(${farX - 45} ${quay - 109})`}
          data-delayed-cargo="true"
        >
          <rect
            x="-15"
            y="-30"
            width="60"
            height="47"
            fill="#d3a778"
            stroke={ink}
            strokeWidth="3"
          />
          <path d="M15-30V17" stroke="#fff0d7" strokeWidth="8" />
          <rect
            x="49"
            y="-47"
            width="52"
            height="64"
            fill="#d3a778"
            stroke={ink}
            strokeWidth="3"
          />
          <path d="M75-47V17" stroke="#fff0d7" strokeWidth="8" />
          <text x="45" y="43" textAnchor="middle" fill={ink} fontSize="17">
            Следующий рейс
          </text>
        </g>
      )}
      <g
        transform={`translate(${bargeX} ${bargeY})`}
        data-barge="pipes"
        data-barge-gift={loaded}
      >
        <path
          d="M-195 0H230L200 66H-160Z"
          fill={blue}
          stroke={ink}
          strokeWidth="3"
        />
        <path d="M-185 22H217" stroke="#fff" strokeWidth="5" />
        <rect x="-190" y="-12" width="418" height="16" rx="4" fill={ink} />
        <g data-pipes="aboard">
          {[0, 1, 2].map((row) => (
            <g key={row} transform={`translate(${row * 12} ${-26 - row * 21})`}>
              <rect
                x="-168"
                y="-13"
                width="185"
                height="25"
                rx="12"
                fill="#819ca8"
                stroke={ink}
                strokeWidth="2"
              />
              <ellipse
                cx="17"
                cy="0"
                rx="13"
                ry="12"
                fill="#c6dbe1"
                stroke={ink}
                strokeWidth="2"
              />
              <ellipse cx="17" cy="0" rx="7" ry="6" fill={ink} />
              <path
                d="M-115-12V12M-48-12V12"
                stroke="#dbe9ea"
                strokeWidth="5"
              />
            </g>
          ))}
        </g>
        <rect
          x="172"
          y="-77"
          width="43"
          height="62"
          rx="4"
          fill="#fff"
          stroke={ink}
          strokeWidth="3"
        />
        <rect x="180" y="-66" width="27" height="20" fill="#abd5e5" />
        <path d="M172-77H215M187-78V-108" stroke={ink} strokeWidth="5" />
        {loaded && (
          <Gift x={101} y={-47} parcel={context.parcel} location="barge" />
        )}
        <path
          d="M-170 81Q-125 91-80 81M-5 83Q40 93 85 83M151 81Q180 90 215 81"
          fill="none"
          stroke="#fff"
          strokeWidth="4"
        />
        {leaving && (
          <path
            d="M-241 39H-211M-269 61H-206"
            stroke="#fff"
            strokeWidth="5"
            strokeLinecap="round"
          />
        )}
      </g>
      <text
        x="42"
        y={height - 46}
        fill="#446a7d"
        fontSize="21"
        letterSpacing="5"
      >
        ОБЬ
      </text>
    </svg>
  );
}
