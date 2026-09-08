import { type RefObject, useEffect, useRef, useState } from "react";
import detail1 from "../../design/scene-01/assets/current/map/inspect-1.webp";
import detail2 from "../../design/scene-01/assets/current/map/inspect-2.webp";
import detail3 from "../../design/scene-01/assets/current/map/inspect-3.webp";
import detail4 from "../../design/scene-01/assets/current/map/inspect-4.webp";
import styles from "../App.module.css";
import { mapMarkerPositions } from "../game/mapMarkerPositions";
import tracks from "../game/mapTracks.json";

const details = [detail1, detail2, detail3, detail4];
const descriptions = [
  "Потрёпанная синяя фура, ржавчина на кузове, выхлоп у кабины.",
  "Современная синяя фура с одним водителем в кабине.",
  "Ухоженная бирюзовая фура: два взрослых водителя сидят рядом за стеклом кабины.",
  "Старая охристая фура с длинным капотом, следами ржавчины и выхлопом.",
];

export function MapInspection({
  format,
  video,
  playing,
}: {
  format: "mobile" | "desktop";
  video: RefObject<HTMLVideoElement | null>;
  playing: boolean;
}) {
  const markers = useRef<(HTMLButtonElement | null)[]>([]);
  const leaders = useRef<(SVGLineElement | null)[]>([]);
  const dialog = useRef<HTMLDialogElement>(null);
  const opener = useRef<HTMLButtonElement | null>(null);
  const [selected, setSelected] = useState(0);
  useEffect(() => {
    const element = playing ? video.current : null;
    const paths = tracks[format];
    let frame = 0;
    let active = true;
    const update = () => {
      if (!active) return;
      // Track the decoded video's clock, including seeks, pauses and loop wrap.
      const position = ((element?.currentTime ?? 0) * 18) % paths[0].length;
      const index = Math.floor(position);
      const fraction = position - index;
      const bounds = markers.current[0]?.parentElement?.getBoundingClientRect();
      if (!bounds) return;
      const anchors = paths.map((path) => {
        const from = path[index],
          to = path[(index + 1) % path.length];
        return from.map((value, axis) => value + (to[axis] - value) * fraction);
      });
      const positions = mapMarkerPositions(
        anchors,
        bounds.width,
        bounds.height,
      );
      positions.forEach(([x, y], i) => {
        const marker = markers.current[i];
        if (marker) {
          marker.style.left = `${x}px`;
          marker.style.top = `${y}px`;
        }
        const line = leaders.current[i];
        if (line) {
          line.setAttribute("x1", `${anchors[i][0]}%`);
          line.setAttribute("y1", `${anchors[i][1]}%`);
          line.setAttribute("x2", `${x}`);
          line.setAttribute("y2", `${y}`);
        }
      });
    };
    const decodedFrames = element && "requestVideoFrameCallback" in element;
    const tick = () => {
      update();
      if (decodedFrames) frame = element.requestVideoFrameCallback(tick);
      else frame = requestAnimationFrame(tick);
    };
    update();
    tick();
    element?.addEventListener("seeked", update);
    const observer = new ResizeObserver(update);
    if (markers.current[0]?.parentElement)
      observer.observe(markers.current[0].parentElement);
    return () => {
      active = false;
      observer.disconnect();
      if (decodedFrames) element.cancelVideoFrameCallback(frame);
      else cancelAnimationFrame(frame);
      element?.removeEventListener("seeked", update);
    };
  }, [format, playing, video]);
  return (
    <>
      <svg className={styles.mapInspectLeaders} aria-hidden="true">
        {details.map((detail, i) => (
          <line
            key={detail}
            ref={(element) => {
              leaders.current[i] = element;
            }}
          />
        ))}
      </svg>
      {details.map((detail, i) => (
        <button
          key={detail}
          className={styles.mapInspectMarker}
          data-truck-inspect={i + 1}
          aria-label={`Рассмотреть машину №${i + 1}`}
          aria-haspopup="dialog"
          ref={(element) => {
            markers.current[i] = element;
          }}
          onClick={(event) => {
            opener.current = event.currentTarget;
            setSelected(i);
            dialog.current?.showModal();
          }}
          type="button"
        >
          {i + 1}
        </button>
      ))}
      <dialog
        className={styles.mapInspectDialog}
        ref={dialog}
        aria-label={`Машина №${selected + 1}`}
        onClose={() => opener.current?.focus()}
      >
        <div className={styles.mapInspectHeading}>
          <h2>№{selected + 1}</h2>
          <button type="button" onClick={() => dialog.current?.close()}>
            Закрыть
          </button>
        </div>
        <img src={details[selected]} alt={descriptions[selected]} />
        <nav aria-label="Рассмотреть другую машину">
          {details.map((detail, i) => (
            <button
              key={detail}
              type="button"
              aria-pressed={selected === i}
              onClick={() => setSelected(i)}
            >
              №{i + 1}
            </button>
          ))}
        </nav>
      </dialog>
    </>
  );
}
