import { type RefObject, useEffect, useRef } from "react";
import styles from "../App.module.css";
import { mapMarkerPositions } from "../game/mapMarkerPositions";
import tracks from "../game/mapTracks.json";

export function MapNumbers({
  format,
  video,
  playing,
}: {
  format: "mobile" | "desktop";
  video: RefObject<HTMLVideoElement | null>;
  playing: boolean;
}) {
  const markers = useRef<(HTMLSpanElement | null)[]>([]);
  useEffect(() => {
    const element = playing ? video.current : null;
    const paths = tracks[format];
    let frame = 0;
    let videoFrame = 0;
    let mediaTime = element?.currentTime ?? 0;
    const update = () => {
      // Use the presented frame, never a smoothed or independently running UI clock.
      const index = Math.floor(mediaTime * tracks.fps + 1e-6) % paths[0].length;
      const bounds = markers.current[0]?.parentElement?.getBoundingClientRect();
      if (!bounds) return;
      mapMarkerPositions(paths.map(path => path[index]), bounds.width, bounds.height)
        .forEach(([x, y], i) => {
          const marker = markers.current[i];
          if (marker) {
            marker.style.left = `${x}px`;
            marker.style.top = `${y}px`;
          }
        });
    };
    const presented = (_now: number, metadata: VideoFrameCallbackMetadata) => {
      mediaTime = metadata.mediaTime;
      update();
      videoFrame = element!.requestVideoFrameCallback(presented);
    };
    const fallback = () => {
      mediaTime = element?.currentTime ?? 0;
      update();
      frame = requestAnimationFrame(fallback);
    };
    const seek = () => {
      mediaTime = element?.currentTime ?? 0;
      update();
    };
    update();
    if (element?.requestVideoFrameCallback) videoFrame = element.requestVideoFrameCallback(presented);
    else if (element) frame = requestAnimationFrame(fallback);
    element?.addEventListener("seeked", seek);
    const observer = new ResizeObserver(update);
    if (markers.current[0]?.parentElement) observer.observe(markers.current[0].parentElement);
    return () => {
      observer.disconnect();
      cancelAnimationFrame(frame);
      if (videoFrame) element?.cancelVideoFrameCallback(videoFrame);
      element?.removeEventListener("seeked", seek);
    };
  }, [format, playing, video]);
  return (
    <>
      {[1, 2, 3, 4].map((number, i) => (
        <span
          key={number}
          className={styles.mapNumber}
          data-truck-number={number}
          aria-hidden="true"
          ref={(element) => {
            markers.current[i] = element;
          }}
        >
          {number}
        </span>
      ))}
    </>
  );
}
