import { useEffect, useRef } from "react";
import { type MapCarrierId, mapCarrierIds } from "../game/carrierFacts";
import { carrierMotionFraction } from "../game/carrierTracking";
import styles from "./CarrierSpeedometer.module.css";

export function CarrierSpeedometer({ carrierId }: { carrierId: MapCarrierId }) {
  const instrument = useRef<HTMLSpanElement>(null);
  useEffect(() => {
    let request = 0;
    let previous = -Infinity;
    const paint = (now: number) => {
      if (now - previous >= 100) {
        previous = now;
        const video =
          document.querySelector<HTMLVideoElement>("[data-city-video]");
        const fraction =
          video && !video.paused && !video.ended
            ? carrierMotionFraction(
                video.currentTime,
                mapCarrierIds.indexOf(carrierId),
              )
            : 0;
        const element = instrument.current;
        if (element) {
          element.dataset.speedometerValue = fraction.toFixed(3);
          element.setAttribute(
            "aria-valuenow",
            String(Math.round(fraction * 100)),
          );
          element.style.setProperty(
            "--needle-angle",
            `${-90 + fraction * 180}deg`,
          );
          element.style.setProperty("--dial-offset", `${100 * (1 - fraction)}`);
        }
      }
      request = requestAnimationFrame(paint);
    };
    request = requestAnimationFrame(paint);
    return () => cancelAnimationFrame(request);
  }, [carrierId]);
  return (
    // biome-ignore lint/a11y/useSemanticElements: Custom SVG dial needs ARIA meter semantics; native meter hides its children.
    <span
      ref={instrument}
      className={styles.instrument}
      data-speedometer
      data-speedometer-value="0"
      role="meter"
      aria-label="Темп движения на карте"
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuenow={0}
    >
      <svg
        className={styles.dial}
        viewBox="0 0 104 64"
        fill="none"
        aria-hidden="true"
      >
        <path
          d="M9 52a43 43 0 0 1 86 0"
          stroke="#d9e5ed"
          strokeWidth="7"
          strokeLinecap="round"
        />
        <path
          d="M9 52a43 43 0 0 1 86 0"
          pathLength="100"
          stroke="#0b659a"
          strokeWidth="7"
          strokeLinecap="round"
          strokeDasharray="100"
          className={styles.progress}
        />
        {[-90, -67.5, -45, -22.5, 0, 22.5, 45, 67.5, 90].map((angle) => (
          <line
            key={angle}
            x1="52"
            y1="16"
            x2="52"
            y2={angle % 45 === 0 ? "22" : "20"}
            stroke="#7d96a9"
            strokeWidth="1.5"
            transform={`rotate(${angle} 52 52)`}
          />
        ))}
        <g className={styles.needle}>
          <path d="M50 52 52 20 54 52Z" fill="#073e63" />
        </g>
        <circle
          cx="52"
          cy="52"
          r="5"
          fill="#fff"
          stroke="#073e63"
          strokeWidth="3"
        />
      </svg>
    </span>
  );
}
