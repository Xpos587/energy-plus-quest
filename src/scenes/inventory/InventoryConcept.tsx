import type { ParcelId } from "../../game/types";
import type { SceneArtProps } from "../types";

const ink = "#041327";
const orange = "#ff5500";
const blue = "#205ac6";

function Parcel({ x, y, parcel }: { x: number; y: number; parcel: ParcelId }) {
  return (
    <g transform={`translate(${x} ${y})`} data-warehouse-gift={parcel}>
      <rect
        x={-45}
        y={-36}
        width={90}
        height={72}
        rx={8}
        fill={orange}
        stroke="white"
        strokeWidth={6}
      />
      {parcel === "camera" ? (
        <g fill="white">
          <rect x={-27} y={-16} width={54} height={36} rx={5} />
          <rect x={-19} y={-23} width={20} height={9} rx={2} />
          <circle cx={5} cy={2} r={12} fill={orange} />
          <circle cx={5} cy={2} r={6} fill="white" />
        </g>
      ) : parcel === "boat" ? (
        <g fill="none" stroke="white" strokeWidth={6}>
          <ellipse rx={31} ry={17} />
          <path d="M-12-13v26M12-13v26" />
        </g>
      ) : (
        <g fill="white">
          <path d="M-25-23h18V4l-7 17h-18l7-24zM5-23h18V4l-7 17H-2L5-3z" />
          <path d="M-25-14h18M5-14h18" stroke={orange} strokeWidth={4} />
        </g>
      )}
    </g>
  );
}

function Rack({ x, y, letter }: { x: number; y: number; letter: string }) {
  return (
    <g transform={`translate(${x} ${y})`}>
      <rect
        width={150}
        height={100}
        rx={7}
        fill="white"
        stroke="#b8c7ce"
        strokeWidth={4}
      />
      <path d="M0 50h150M50 0v100M100 0v100" stroke="#b8c7ce" strokeWidth={3} />
      {[0, 1, 2, 3, 4, 5].map((i) => (
        <g
          key={i}
          transform={`translate(${10 + (i % 3) * 50} ${10 + Math.floor(i / 3) * 50})`}
        >
          <rect
            width={30}
            height={30}
            rx={3}
            fill={i === 1 ? "#a9c8b4" : "#e3c59b"}
          />
          <path d="M15 0v30" stroke="white" strokeWidth={3} />
        </g>
      ))}
      <rect x={44} y={-41} width={62} height={38} rx={7} fill={blue} />
      <text
        x={75}
        y={-13}
        fill="white"
        fontSize={29}
        fontWeight={800}
        textAnchor="middle"
      >
        {letter}
      </text>
    </g>
  );
}

function Person({
  x,
  y,
  scanner = false,
  confused = false,
}: {
  x: number;
  y: number;
  scanner?: boolean;
  confused?: boolean;
}) {
  return (
    <g transform={`translate(${x} ${y})`}>
      <path
        d="M-13 27l-8 27M12 27l8 27"
        stroke={ink}
        strokeWidth={11}
        strokeLinecap="round"
      />
      <rect x={-20} y={-7} width={40} height={43} rx={13} fill={orange} />
      <path d="M-14 6h28M-14 20h28" stroke="#ffeabe" strokeWidth={6} />
      <circle cy={-20} r={17} fill="#dba382" />
      <path d="M-20-20a20 20 0 0 1 40 0z" fill={blue} />
      <path d="M17 6l23 9" stroke={ink} strokeWidth={9} strokeLinecap="round" />
      {scanner && (
        <g transform="translate(38 -3) rotate(12)">
          <rect width={21} height={29} rx={4} fill={ink} />
          <rect x={4} y={5} width={13} height={13} rx={2} fill="#a9d8df" />
        </g>
      )}
      {confused && (
        <g>
          <circle cx={45} cy={-40} r={23} fill="white" />
          <text
            x={45}
            y={-29}
            fill={blue}
            textAnchor="middle"
            fontSize={32}
            fontWeight={800}
          >
            ?
          </text>
        </g>
      )}
    </g>
  );
}

function Forklift({ x, y }: { x: number; y: number }) {
  return (
    <g transform={`translate(${x} ${y})`} data-warehouse-robot="forklift">
      <rect x={-39} y={-33} width={17} height={26} rx={4} fill={ink} />
      <rect x={22} y={-33} width={17} height={26} rx={4} fill={ink} />
      <rect x={-39} y={21} width={17} height={26} rx={4} fill={ink} />
      <rect x={22} y={21} width={17} height={26} rx={4} fill={ink} />
      <rect x={-30} y={-45} width={60} height={96} rx={13} fill={blue} />
      <rect x={-20} y={-22} width={40} height={31} rx={6} fill="white" />
      <circle cy={-6} r={8} fill={ink} />
      <path d="M-19-45v-38M19-45v-38" stroke={ink} strokeWidth={8} />
      <circle cy={32} r={7} fill="#9bd8b5" />
    </g>
  );
}

function Drone({ x, y }: { x: number; y: number }) {
  return (
    <g transform={`translate(${x} ${y})`} data-warehouse-drone="inventory">
      <path d="M-29-24L29 24M-29 24L29-24" stroke={ink} strokeWidth={8} />
      {[-1, 1].flatMap((a) =>
        [-1, 1].map((b) => (
          <ellipse
            key={`${a}${b}`}
            cx={a * 32}
            cy={b * 25}
            rx={20}
            ry={11}
            fill="#e6eef0"
            stroke={ink}
            strokeWidth={4}
          />
        )),
      )}
      <rect x={-18} y={-21} width={36} height={42} rx={10} fill={blue} />
      <circle cy={6} r={7} fill="white" />
    </g>
  );
}

function AddressCard({
  x,
  y,
  recorded,
}: {
  x: number;
  y: number;
  recorded: boolean;
}) {
  return (
    <g
      transform={`translate(${x} ${y})`}
      data-warehouse-address={recorded ? "recorded" : "missing-handover"}
    >
      <rect
        width={180}
        height={91}
        rx={12}
        fill="white"
        stroke={recorded ? blue : "#c5d0d5"}
        strokeWidth={3}
      />
      <text x={15} y={29} fontSize={18} fill="#526575">
        {recorded ? "Адрес в системе" : "Новая смена"}
      </text>
      <text x={15} y={65} fontSize={29} fontWeight={800} fill={ink}>
        {recorded ? "А · 01" : "Где подарок?"}
      </text>
      {recorded && (
        <path
          d="M137 49l9 10 18-23"
          stroke={blue}
          strokeWidth={6}
          fill="none"
          strokeLinecap="round"
        />
      )}
    </g>
  );
}

export function InventoryConcept({
  format,
  context,
  selectedId,
  showResult,
}: SceneArtProps & { format: "desktop" | "mobile" }) {
  const mobile = format === "mobile";
  const outcome = showResult ? selectedId : undefined;
  const alphabet = outcome === "alphabet";
  const near = outcome === "keeper" || outcome === "wms";
  const letter =
    context.parcel === "camera" ? "Ф" : context.parcel === "boat" ? "Л" : "Н";
  const gift = mobile
    ? near
      ? [510, 878]
      : alphabet
        ? context.parcel === "camera"
          ? [255, 405]
          : context.parcel === "boat"
            ? [255, 605]
            : [580, 605]
        : [220, 270]
    : near
      ? [984, 474]
      : alphabet
        ? context.parcel === "camera"
          ? [390, 332]
          : context.parcel === "boat"
            ? [590, 562]
            : [590, 332]
        : [186, 527];
  const title =
    outcome === "entrance"
      ? "У входа — далеко до отгрузки"
      : alphabet
        ? `По алфавиту: ${letter}`
        : outcome === "keeper"
          ? "Место верное. Адрес не передан"
          : outcome === "wms"
            ? "Рядом с отгрузкой. Адрес сохранён"
            : "Куда отправится подарок?";
  return (
    <svg
      viewBox={mobile ? "0 0 900 1100" : "0 0 1200 900"}
      width="100%"
      height="100%"
      role="img"
      aria-label={`Плоский план склада. ${title}`}
      data-inventory-concept={format}
      data-concept-outcome={outcome ?? "choice"}
      data-gift-zone={
        near ? "dispatch" : alphabet ? `alphabet-${letter}` : "entrance"
      }
      style={{ display: "block", fontFamily: "inherit" }}
    >
      <rect width={1200} height={1100} fill="#eef4f5" />
      {mobile ? (
        <>
          <rect
            x={108}
            y={252}
            width={684}
            height={675}
            rx={22}
            fill="#e2ebec"
            stroke="#a6b9c2"
            strokeWidth={8}
          />
          <rect
            x={116}
            y={262}
            width={190}
            height={77}
            rx={12}
            fill="#c5d9e5"
          />
          <rect
            x={452}
            y={791}
            width={328}
            height={124}
            rx={12}
            fill="#cfdfd1"
          />
          <path
            d="M400 274v515q0 45 45 45h130"
            fill="none"
            stroke="white"
            strokeWidth={32}
          />
          <path
            d="M400 280v500q0 55 55 55h107"
            fill="none"
            stroke="#a4b7bf"
            strokeWidth={3}
            strokeDasharray="10 13"
          />
          <Rack x={180} y={355} letter="Ф" />
          <Rack x={505} y={355} letter="Р" />
          <Rack x={180} y={555} letter="Л" />
          <Rack x={505} y={555} letter="Н" />
          <Rack x={505} y={728} letter="А" />
          <text x={105} y={179} fontSize={29} fontWeight={800} fill={blue}>
            ПРИЁМКА
          </text>
          <path
            d="M140 202v34m-12-12 12 12 12-12"
            stroke={blue}
            strokeWidth={5}
            fill="none"
          />
          <text x={575} y={985} fontSize={29} fontWeight={800} fill={blue}>
            ОТГРУЗКА
          </text>
          <text x={575} y={1019} fontSize={21} fill="#526575">
            Груз на баржу
          </text>
          <path
            d="M741 915v37m-12-12 12 12 12-12"
            stroke={blue}
            strokeWidth={5}
            fill="none"
          />
          <Drone x={710} y={211} />
          <Forklift x={401} y={627} />
          <Person x={694} y={428} scanner />
          <Person
            x={323}
            y={932}
            scanner={outcome === "wms"}
            confused={outcome === "keeper"}
          />
          {near && <AddressCard x={105} y={965} recorded={outcome === "wms"} />}
          {outcome === "entrance" && (
            <path
              d="M250 283h145v568h185"
              stroke={orange}
              strokeWidth={7}
              strokeDasharray="12 10"
              fill="none"
            />
          )}
          {alphabet && (
            <path
              d={`M${gift[0]} ${gift[1] + 43}H401V853H575`}
              stroke={orange}
              strokeWidth={7}
              strokeDasharray="12 10"
              fill="none"
            />
          )}
        </>
      ) : (
        <>
          <rect
            x={250}
            y={175}
            width={840}
            height={534}
            rx={22}
            fill="#e2ebec"
            stroke="#a6b9c2"
            strokeWidth={8}
          />
          <rect
            x={91}
            y={358}
            width={160}
            height={235}
            rx={13}
            fill="#c5d9e5"
          />
          <rect
            x={925}
            y={375}
            width={155}
            height={212}
            rx={13}
            fill="#cfdfd1"
          />
          <path
            d="M266 425h645M887 200v475"
            fill="none"
            stroke="white"
            strokeWidth={37}
          />
          <path
            d="M268 425h619V652"
            fill="none"
            stroke="#a4b7bf"
            strokeWidth={3}
            strokeDasharray="10 13"
          />
          <Rack x={315} y={282} letter="Ф" />
          <Rack x={515} y={282} letter="Н" />
          <Rack x={715} y={282} letter="А" />
          <Rack x={315} y={512} letter="Р" />
          <Rack x={515} y={512} letter="Л" />
          <Rack x={715} y={512} letter="Б" />
          <text x={66} y={281} fontSize={29} fontWeight={800} fill={blue}>
            ПРИЁМКА
          </text>
          <text x={936} y={283} fontSize={26} fontWeight={800} fill={blue}>
            ОТГРУЗКА
          </text>
          <text x={936} y={313} fontSize={20} fill="#526575">
            Груз на баржу
          </text>
          <path
            d="M187 307v33m-12-12 12 12 12-12M1100 470h42m-12-12 12 12-12 12"
            stroke={blue}
            strokeWidth={5}
            fill="none"
          />
          <Drone x={1015} y={194} />
          <Forklift x={603} y={692} />
          <Person x={795} y={429} scanner />
          <Person
            x={991}
            y={720}
            scanner={outcome === "wms"}
            confused={outcome === "keeper"}
          />
          {near && <AddressCard x={920} y={788} recorded={outcome === "wms"} />}
          {outcome === "entrance" && (
            <path
              d="M187 568v86H887V475h47"
              stroke={orange}
              strokeWidth={7}
              strokeDasharray="12 10"
              fill="none"
            />
          )}
          {alphabet && (
            <path
              d={`M${gift[0]} ${gift[1] + 43}V425H887V475h47`}
              stroke={orange}
              strokeWidth={7}
              strokeDasharray="12 10"
              fill="none"
            />
          )}
          <text x={65} y={800} fontSize={22} fill="#526575">
            Алфавит начинается у зоны отгрузки
          </text>
          <path
            d="M688 786H833m-12-12 12 12-12 12"
            stroke="#526575"
            strokeWidth={4}
            fill="none"
          />
        </>
      )}
      <Parcel x={gift[0]} y={gift[1]} parcel={context.parcel} />
      {outcome === "wms" && (
        <g transform={`translate(${gift[0] + 25} ${gift[1] - 39})`}>
          <circle r={21} fill={blue} stroke="white" strokeWidth={4} />
          <path
            d="m-10 0 7 7L11-8"
            stroke="white"
            strokeWidth={5}
            fill="none"
            strokeLinecap="round"
          />
        </g>
      )}
    </svg>
  );
}
