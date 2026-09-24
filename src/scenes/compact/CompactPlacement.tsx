import type { ParcelId } from "../../game/types";
import { parcelNames } from "../names";
import styles from "./CompactPlacement.module.css";

const zones = [
  [110, 168, 176, 178],
  [312, 180, 188, 187],
  [600, 282, 78, 99],
  [795, 144, 112, 329],
];

export function CompactPlacement({
  parcel,
  placement,
}: {
  parcel: ParcelId;
  placement?: number;
}) {
  const selectedZone = placement ? zones[placement - 1] : undefined;
  const boat = parcel === "boat";
  const blocked = boat && placement === 3;
  const waiting = !placement || blocked;
  const upright = boat && placement === 4;
  // Coordinates share cargo-bay.svg's floor and load surfaces; gifts never shrink to fit.
  const [x, y] = waiting
    ? [490, 569]
    : placement === 1
      ? [190, 345]
      : placement === 2
        ? [399, 367]
        : placement === 3
          ? [640, 379]
          : boat
            ? [852, 320]
            : parcel === "camera"
              ? [850, 356]
              : [850, 471];
  const status = `${parcelNames[parcel].nominative} · ${!placement ? "На погрузке" : blocked ? "№3: не помещается" : `Место №${placement}`}`;
  return (
    <>
      <svg className={styles.layer} viewBox="0 0 1000 480" aria-hidden="true">
        <defs>
          <linearGradient id="cargo-boat-tube" x1="0" y1="0" x2="0" y2="1">
            <stop stopColor="#a1c6c9" />
            <stop offset=".45" stopColor="#689ca9" />
            <stop offset="1" stopColor="#37687e" />
          </linearGradient>
          <pattern
            id="cargo-knit"
            width="7"
            height="7"
            patternUnits="userSpaceOnUse"
          >
            <path
              d="m1 1 2 3 2-3"
              fill="none"
              stroke="#f0cfab"
              strokeWidth=".8"
            />
          </pattern>
          <g id="cargo-buckle" stroke="#733f34" strokeWidth="1.5">
            <rect x="-6" y="-9" width="12" height="18" rx="2" fill="#ddd8c4" />
            <path d="M-3-5H3V5H-3Z" fill="#b55345" />
            <path d="M-5 0H5" />
          </g>
        </defs>
        <g
          transform="translate(45 -30) scale(.8)"
          stroke="#6b3f26"
          strokeWidth="2.5"
          strokeLinejoin="round"
          strokeLinecap="round"
        >
          {/* Technical zone bounds share the cargo surfaces, not the marker hit areas. */}
          {zones.map(([left, top, width, height], index) => (
            <g
              key={left}
              className={styles.zone}
              data-loading-zone={`place-${index + 1}`}
              data-active={placement === index + 1}
            >
              <rect x={left} y={top} width={width} height={height} />
              <text x={left + 8} y={top + 25}>
                {index + 1}
              </text>
            </g>
          ))}
          {/* Side-carried boat rests in two padded saddles on a 240-unit deck. */}
          <g data-loading-trolley transform="translate(190 15)">
            <ellipse
              cx="300"
              cy="593"
              rx="137"
              ry="6"
              fill="#738571"
              opacity=".2"
              stroke="none"
            />
            <path
              d="M228 545V450q0-12-10-8l-20 11q-8 3-8 12v95"
              fill="none"
              stroke="#6f857b"
              strokeWidth="6"
            />
            <g fill="#50645c">
              <circle cx="211" cy="574" r="10" />
              <circle cx="402" cy="574" r="10" />
            </g>
            <path d="M193 545H420L407 560H180Z" fill="#b4c3b2" />
            <path d="M180 560H407v10H180Z" fill="#7c9081" />
            <path d="m407 560 13-15v11l-13 14Z" fill="#667d6e" />
            <path
              d="M197 550H408M194 555H401"
              stroke="#d8dfca"
              strokeWidth="1.5"
            />
            <path d="m198 453 21-12" stroke="#b79b6d" strokeWidth="8" />
            <g fill="#52645d" strokeWidth="2">
              <path
                d="M195 570v10l9 6 8-5v-11m171 0v10l9 6 8-5v-11"
                fill="#a8b6a6"
              />
              <circle cx="205" cy="582" r="11" />
              <circle cx="392" cy="582" r="11" />
              <circle cx="205" cy="582" r="4" fill="#b8c4af" />
              <circle cx="392" cy="582" r="4" fill="#b8c4af" />
            </g>
            <g fill="#9eae96" stroke="#637c6d" strokeWidth="2">
              <path d="M218 557v-17h9q3 14 15 14t17-14h8v17Z" />
              <path d="M351 557v-17h9q3 14 15 14t17-14h8v17Z" />
              <path
                d="M222 540q5 14 20 14t21-14m92 0q5 14 20 14t21-14"
                fill="none"
                stroke="#d9d9b8"
                strokeWidth="6"
              />
            </g>
            {waiting && boat && (
              <g data-trolley-rear-webbing>
                <path
                  d="M384 545 370 458"
                  fill="none"
                  stroke="#947347"
                  strokeWidth="5"
                />
                <path d="M380 541h8v7h-8Z" fill="#cdd5bf" strokeWidth="1.5" />
              </g>
            )}
          </g>
          <g data-idle-restraints fill="none" stroke="#b55345" strokeWidth="5">
            {placement !== 2 && (
              <g data-idle-restraint="2">
                <path d="M343 199v91q0 35 13 63l3 37-9 90M463 199v70q0 47-15 83l-4 38 7 90" />
                <use href="#cargo-buckle" x="354" y="456" />
                <use href="#cargo-buckle" x="448" y="456" />
              </g>
            )}
            {(placement !== 3 || blocked) && (
              <g data-idle-restraint="3">
                <path d="M608 338v25q28 14 61 0v-25" />
                <use
                  href="#cargo-buckle"
                  transform="translate(649 369) rotate(90)"
                />
              </g>
            )}
            {placement !== 4 && (
              <g data-idle-restraint="4">
                <path d="M798 199q37 18 106 0M798 338q38 21 106 0" />
                <use
                  href="#cargo-buckle"
                  transform="translate(881 205) rotate(80)"
                />
                <use
                  href="#cargo-buckle"
                  transform="translate(881 345) rotate(80)"
                />
                <path d="M885 351v28q0 10 8 8" strokeWidth="3" />
              </g>
            )}
          </g>
          {upright && (
            <g data-boat-pad>
              <path
                d="M822 459q31-4 59 0l5 10q-36 6-69 0Z"
                fill="#bacbb2"
                stroke="#8fa48c"
                strokeWidth="1.5"
              />
              <path d="M832 469h40" stroke="#718b73" strokeWidth="3" />
            </g>
          )}
          {!waiting && placement === 2 && (
            <path
              data-padding-contact
              d={boat ? "M304 367H478" : "M363 367q35-6 77 0"}
              stroke="#91a89e"
              strokeWidth="5"
            />
          )}
          {blocked && (
            <g data-placement-blocked>
              <path
                d="M603 294H675V369H603Z"
                fill="#edc16e"
                fillOpacity=".25"
                stroke="#a66a28"
                strokeDasharray="6 5"
              />
              <path
                d="M607 314H671m-58-5-6 5 6 5m52-10 6 5-6 5"
                fill="none"
                stroke="#8c5823"
              />
              <circle
                cx="640"
                cy="345"
                r="15"
                fill="#fff4da"
                stroke="#9c682a"
              />
              <path
                d="m634 339 12 12m0-12-12 12"
                stroke="#9c682a"
                strokeWidth="3"
              />
            </g>
          )}
          <g
            data-placed-parcel={parcel}
            data-parcel-location={
              waiting ? "loading-apron" : `place-${placement}`
            }
            data-orientation={upright ? "upright" : "horizontal"}
            className={styles.parcel}
            style={{ transform: `translate(${x}px, ${y}px)` }}
          >
            {!upright && (
              <ellipse
                cy="1"
                rx={boat ? 125 : 37}
                ry={boat ? 8 : 5}
                fill="#435b54"
                opacity=".25"
                stroke="none"
              />
            )}
            {boat ? (
              <g
                className={styles.turn}
                style={{
                  transform: upright
                    ? "rotate(-90deg) translateY(49px)"
                    : "rotate(0deg)",
                }}
              >
                <path
                  d="M-147-49Q-141-92-94-98H117Q147-93 147-56V-30Q142-5 111 0H-95Q-137-4-147-49Z"
                  fill="#315b70"
                />
                <path
                  d="M-146-49Q-135-19-94-17H113q22-2 33-19v6Q142-5 111 0H-95Q-137-4-146-49Z"
                  fill="#254e63"
                  stroke="none"
                />
                <path
                  d="M-145-52Q-138-88-94-94H115q27 3 28 36v15q-3 27-34 30H-94q-41-3-51-39Z"
                  fill="url(#cargo-boat-tube)"
                />
                <path
                  d="M-115-50q4-23 30-25H105v48H-84q-25-1-31-23Z"
                  fill="#284b5a"
                />
                <path
                  d="M-105-46q9-14 27-15H105v32H-82q-16 0-23-17Z"
                  fill="#a5b3a2"
                  strokeWidth="1.5"
                />
                <path
                  d="M-77-53H101m-175 9H101m-161 9H101"
                  stroke="#7c9488"
                  strokeWidth="1"
                />
                <path
                  d="M-130-62q12-26 44-27H106"
                  fill="none"
                  stroke="#bfd9d3"
                  strokeWidth="5"
                />
                <path
                  d="M-110-19q18 4 35 4H102"
                  fill="none"
                  stroke="#7fa8b0"
                  strokeWidth="3"
                />
                <path d="M-48-72h22v43h-22Zm82 0h22v43H34Z" fill="#d7c394" />
                <path
                  d="M-48-72h22v6h-22Zm82 0h22v6H34Z"
                  fill="#f1e2bb"
                  strokeWidth="1.5"
                />
                <path
                  d="M-48-29h22v5h-22Zm82 0h22v5H34Z"
                  fill="#a99570"
                  strokeWidth="1.5"
                />
                <path
                  d="M-51-74h28m54 0h28M-51-24h28m54 0h28"
                  stroke="#426d7b"
                  strokeWidth="4"
                />
                <path d="M105-77h13v53h-13Z" fill="#9c987d" />
                <path d="m118-77 8 6v47h-8Z" fill="#666f64" />
                <path d="M109-70v39" stroke="#d2c6a1" strokeWidth="2" />
                <path
                  d="m-102-92-7 15m70-17v13m108-13v13m-174 63-3 13m69-9v12m108-12v12"
                  stroke="#426d7d"
                  strokeWidth="2"
                />
                <path
                  d="M-93-85H99M-89-9H101"
                  stroke="#d1ab70"
                  strokeWidth="2.5"
                />
                <path d="M-101-39H90" stroke="#e7d7ad" strokeWidth="4" />
                <path
                  d="m-100-44-30-3q-9 7 0 14l30-2Z"
                  fill="#d2a368"
                  strokeWidth="1.5"
                />
                <path
                  d="M-18-44v10m85-10v10"
                  stroke="#b45342"
                  strokeWidth="4"
                />
                <ellipse
                  cx="-120"
                  cy="-65"
                  rx="7"
                  ry="5"
                  fill="#d9dfcf"
                  strokeWidth="1.5"
                />
                <path d="m-123-65 6 0" stroke="#596f70" strokeWidth="2" />
                <path d="M128-61v17" stroke="#d8e4d7" strokeWidth="3" />
              </g>
            ) : parcel === "socks" ? (
              <g data-knitted-bundle>
                <path
                  d="M-30-27q-6-11 1-20l9-10q12-4 24 1l23 1q12 4 12 16l1 23q0 12-12 15H-21q-11-1-11-10Z"
                  fill="#bd8064"
                  stroke="#805f4c"
                />
                <path
                  d="M-28-27q22-9 51 0l13 3v12q-1 10-13 10h-43q-10-1-10-9Z"
                  fill="#d5a781"
                  stroke="#8c6b54"
                  strokeWidth="1.5"
                />
                <path
                  d="M-25-48q9-10 18-6l4 20q-1 8 9 10l14 1q10 1 9 10-9 9-25 1l-16-7q-6-4-8-13Z"
                  fill="#dfb590"
                  stroke="#946b52"
                  strokeWidth="1.5"
                />
                <path
                  d="M-4-54q10-6 20-1l-1 18q-2 8 8 11l11 4q7 4 4 11-9 7-23-2L2-21q-8-5-7-14Z"
                  fill="#c58e70"
                  stroke="#946b52"
                  strokeWidth="1.5"
                />
                <path
                  d="M-25-48q9-10 18-6l4 20q-1 8 9 10l14 1q10 1 9 10-9 9-25 1l-16-7q-6-4-8-13ZM-4-54q10-6 20-1l-1 18q-2 8 8 11l11 4q7 4 4 11-9 7-23-2L2-21q-8-5-7-14Z"
                  fill="url(#cargo-knit)"
                  stroke="none"
                />
                <path
                  d="m-23-49 3 9m3-12 3 9m3-11 3 9m9-8v10m5-11v10m5-10v10M-17-23q9-4 13 2m17-9q5-3 10 4M-27-8q23 3 48 0"
                  fill="none"
                  stroke="#efcfaa"
                  strokeWidth="1.5"
                />
              </g>
            ) : (
              <g data-camera-parcel>
                <path d="M-32-49-20-59H40L29-49Z" fill="#f3ddb0" />
                <path d="M29-49 40-59V-11L29 0Z" fill="#cfb07d" />
                <path d="M-32-49H29V0H-32Z" fill="#fff4d7" />
                <path
                  d="M-28-44H25V-5H-28Z"
                  fill="#e1eddf"
                  stroke="#b4bfaa"
                  strokeWidth="1"
                />
                <g>
                  <path d="M-22-34h10l4-6H5l5 6h13v24h-45Z" fill="#536b6c" />
                  <circle cx="0" cy="-23" r="13" fill="#304f5c" />
                  <circle cx="0" cy="-23" r="8" fill="#94bac2" />
                  <circle cx="-2" cy="-25" r="3" fill="#deece3" stroke="none" />
                  <path d="M-19-30h6m28-1h4" stroke="#d7ddc6" strokeWidth="2" />
                </g>

                <path
                  d="M-29-47H26M-29-2H26"
                  stroke="#fffaf0"
                  strokeWidth="2"
                />
                <path
                  d="M-11-59H1l-12 10v4h-12v-4Z"
                  fill="#e5ba73"
                  stroke="none"
                />
                <path d="M-24-55h4m15 0H35" stroke="#b9a174" strokeWidth="1" />
              </g>
            )}
          </g>
          {waiting && boat && (
            <g data-trolley-retainer transform="translate(190 15)">
              <path
                d="M370 458v80q0 13 7 17l9 4"
                fill="none"
                stroke="#b58b55"
                strokeWidth="5"
              />
              <use href="#cargo-buckle" x="370" y="530" />
              <path d="M382 558h10v7h-10Z" fill="#cdd5bf" strokeWidth="1.5" />
            </g>
          )}
          {!waiting && placement === 2 && (
            <g
              data-gift-restraints="2"
              fill="none"
              stroke="#b55345"
              strokeWidth="5"
            >
              <path
                d={
                  boat
                    ? "M343 199 339 274 322 290 322 351 350 480M463 199 459 273 476 291 476 352 451 480"
                    : "M343 199 374 310 374 344 359 367 350 480M463 199 426 310 426 344 445 367 451 480"
                }
              />
              <use href="#cargo-buckle" x="352" y="451" />
              <use href="#cargo-buckle" x="449" y="451" />
              <path d="M347 477v5h6v-5m95 0v5h6v-5" strokeWidth="2" />
            </g>
          )}
          {!waiting && placement === 3 && (
            <g
              data-gift-restraints="3"
              fill="none"
              stroke="#b55345"
              strokeWidth="5"
            >
              <path d="M608 338 610 349H668L669 338" />
              <use
                href="#cargo-buckle"
                transform="translate(655 349) rotate(90)"
              />
            </g>
          )}
          {!waiting && placement === 4 && (
            <g
              data-gift-restraints="4"
              fill="none"
              stroke="#b55345"
              strokeWidth="6"
            >
              {boat ? (
                <>
                  <path d="M798 199 815 210H889L904 199M798 338 809 345H895L904 338" />
                  <use
                    href="#cargo-buckle"
                    transform="translate(880 210) rotate(90)"
                  />
                  <use
                    href="#cargo-buckle"
                    transform="translate(880 345) rotate(90)"
                  />
                </>
              ) : parcel === "camera" ? (
                <>
                  <path d="M798 338 819 330H879L904 338M798 338 819 357H879L904 338" />
                  <use
                    href="#cargo-buckle"
                    transform="translate(866 330) rotate(90)"
                  />
                </>
              ) : (
                <>
                  <path d="M798 338 818 437 824 446H882L904 338" />
                  <use
                    href="#cargo-buckle"
                    transform="translate(866 446) rotate(90)"
                  />
                </>
              )}
            </g>
          )}
        </g>
      </svg>
      {selectedZone && (
        <span
          className={styles.zoneLabel}
          data-selected-zone-label
          aria-hidden="true"
          style={{
            left: `${(45 + selectedZone[0] * 0.8) / 10}%`,
            top: `${(-30 + selectedZone[1] * 0.8) / 4.8}%`,
          }}
        >
          №{placement}
        </span>
      )}
      <span className={styles.status} data-placement-status role="status">
        {status}
      </span>
    </>
  );
}
