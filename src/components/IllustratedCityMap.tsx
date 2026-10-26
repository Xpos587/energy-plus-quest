import { Hand, RotateCcw, ZoomIn } from "lucide-react";
import { useEffect, useId, useLayoutEffect, useRef, useState } from "react";
import { carrierFacts, mapCarrierIds } from "../game/carrierFacts";
import type { CarrierId } from "../game/types";
import {
  createSmoke,
  createTraffic,
  drawCity,
  landmark,
  loadTruckAtlas,
  type PlateName,
  plateAspect,
  plateFor,
  plateSource,
  plateSrcSet,
  plates,
  stepTraffic,
  trafficFrame,
  trafficPoses,
} from "./cityV4";
import styles from "./IllustratedCityMap.module.css";
import { useCityMapZoom } from "./useCityMapZoom";

export function IllustratedCityMap({
  onSelect,
  selectedId,
  interactive = true,
}: {
  onSelect?: (id: CarrierId) => void;
  selectedId?: CarrierId;
  interactive?: boolean;
}) {
  const description = useId();
  const viewport = useRef<HTMLElement>(null);
  // Wide plate for landscape viewports, tall plate for portrait.
  // Start from the window shape so a phone never fetches the wide atlas.
  const [plate, setPlate] = useState<PlateName>(() =>
    typeof window === "undefined"
      ? "wide"
      : plateFor(window.innerWidth, window.innerHeight),
  );
  const plateRef = useRef(plate);
  plateRef.current = plate;
  useLayoutEffect(() => {
    const element = viewport.current;
    if (!element) return;
    const sync = () => {
      const rect = element.getBoundingClientRect();
      if (rect.width && rect.height)
        setPlate(plateFor(rect.width, rect.height));
    };
    sync();
    const observer =
      typeof ResizeObserver === "function"
        ? new ResizeObserver(sync)
        : undefined;
    observer?.observe(element);
    return () => observer?.disconnect();
  }, []);
  const navigation = useCityMapZoom(viewport, onSelect, {
    enabled: interactive,
    aspectRatio: plateAspect(plate),
  });
  const camera = useRef(navigation);
  camera.current = navigation;
  const selected = useRef(selectedId);
  selected.current = selectedId;
  const targets = useRef<(HTMLButtonElement | null)[]>([]);
  // One traffic simulation drives the sprites, the hit targets and the camera.
  const traffic = useRef(createTraffic());
  const frameAt = () => trafficFrame(traffic.current, plateRef.current);
  const expressStart = useRef<number | undefined>(undefined);
  const clock = useRef(0);
  const dynamicCanvas = useRef<HTMLCanvasElement>(null);
  const [playing, setPlaying] = useState(false);
  const [failed, setFailed] = useState(false);
  const [reduced, setReduced] = useState(false);
  // The gesture hint disappears after the first zoom/pan or choice.
  const [hinted, setHinted] = useState(false);
  const [touch, setTouch] = useState(false);
  useEffect(() => {
    setTouch(matchMedia("(pointer: coarse)").matches);
  }, []);

  useEffect(() => {
    const element = viewport.current;
    const dismiss = () => setHinted(true);
    element?.addEventListener("scene-map-gesture-start", dismiss);
    return () =>
      element?.removeEventListener("scene-map-gesture-start", dismiss);
  }, []);

  useLayoutEffect(() => {
    if (selectedId === "express") expressStart.current ??= clock.current;
    else expressStart.current = undefined;
    if (selectedId) setHinted(true);
    const index = mapCarrierIds.findIndex((id) => id === selectedId);
    const position = index >= 0 ? frameAt()[index] : undefined;
    if (selectedId === "express") {
      // The new rig appears at the warehouse doors: bring them into view.
      const [x, y] = landmark(plateRef.current, "express");
      camera.current.inspect("express", { x, y }, 1.5);
      return;
    }
    camera.current.inspect(
      position ? selectedId : undefined,
      position ? { x: position[0], y: position[1] } : undefined,
    );
  }, [selectedId]);

  useEffect(() => {
    const preference = matchMedia("(prefers-reduced-motion: reduce)");
    const sync = () => setReduced(preference.matches);
    sync();
    preference.addEventListener("change", sync);
    return () => preference.removeEventListener("change", sync);
  }, []);

  const [assets, setAssets] = useState<{
    plate: PlateName;
    atlas: HTMLImageElement;
  }>();
  useEffect(() => {
    let cancelled = false;
    loadTruckAtlas(plate).then(
      (atlas) => !cancelled && setAssets({ plate, atlas }),
      () => !cancelled && setFailed(true),
    );
    return () => {
      cancelled = true;
    };
  }, [plate]);

  useEffect(() => {
    if (!assets) return;
    let handle = 0;
    let last = performance.now();
    const smoke = createSmoke();
    const name = assets.plate;
    const [plateWidth] = plates[name].res;
    const tick = (now: number) => {
      handle = requestAnimationFrame(tick);
      const canvas = dynamicCanvas.current;
      const area = viewport.current;
      const surface = area?.querySelector<HTMLElement>("[data-map-surface]");
      if (!canvas || !area || !surface) return;
      // A hidden tab pauses rAF; never fast-forward the trucks afterwards.
      const dt = Math.min(0.1, Math.max(0, (now - last) / 1000));
      last = now;
      if (!reduced) stepTraffic(traffic.current, dt);
      const time = traffic.current.time;
      clock.current = time;
      const dpr = Math.min(2, window.devicePixelRatio || 1);
      const view = area.getBoundingClientRect();
      const width = Math.round(view.width * dpr);
      const height = Math.round(view.height * dpr);
      if (canvas.width !== width || canvas.height !== height) {
        canvas.width = width;
        canvas.height = height;
      }
      const box = surface.getBoundingClientRect();
      const k = (box.width / plateWidth) * dpr;
      const context = canvas.getContext("2d");
      if (!context) return;
      context.setTransform(1, 0, 0, 1, 0, 0);
      context.clearRect(0, 0, width, height);
      const start = expressStart.current;
      const pinScale = view.width < 520 || view.height < 420 ? 0.78 : 1;
      if (surface.style.getPropertyValue("--pin-scale") !== String(pinScale))
        surface.style.setProperty("--pin-scale", String(pinScale));
      drawCity(context, traffic.current, assets.atlas, smoke, {
        plate: name,
        reduced,
        k,
        ox: (box.left - view.left) * dpr,
        oy: (box.top - view.top) * dpr,
        dpr,
        selected: selected.current,
        expressAge:
          start === undefined ? undefined : reduced ? 3 : time - start,
        pins: !selected.current,
        pinScale,
      });
      const poses = trafficPoses(traffic.current);
      trafficFrame(traffic.current, name).forEach(([x, y], index) => {
        const target = targets.current[index];
        if (target) {
          // Screen heading of the rig: project its world direction.
          const p = poses[index];
          const [a, b] = plates[name].proj;
          const dx = a[0] * Math.cos(p.heading) + a[1] * Math.sin(p.heading);
          const dy = b[0] * Math.cos(p.heading) + b[1] * Math.sin(p.heading);
          target.style.left = `${x * 100}%`;
          target.style.top = `${y * 100}%`;
          target.style.transform = `translate(-50%, -50%) rotate(${Math.atan2(dy, dx)}rad)`;
        }
        if (mapCarrierIds[index] === selected.current)
          camera.current.track({ x, y }, false);
      });
    };
    handle = requestAnimationFrame(tick);
    setPlaying(!reduced);
    return () => cancelAnimationFrame(handle);
  }, [reduced, assets]);

  return (
    <div className={styles.root}>
      {interactive && !hinted && !selectedId && (
        <p className={styles.coach} data-map-zoom-hint>
          <span className={styles.coachItem}>
            <span className={styles.coachIcon} aria-hidden="true">
              <ZoomIn size={18} />
            </span>
            {touch ? "Два пальца — масштаб" : "Колёсико — масштаб"}
          </span>
          <span className={styles.coachItem}>
            <span className={styles.coachIcon} aria-hidden="true">
              <Hand size={18} />
            </span>
            {touch ? "Палец — двигать карту" : "Тяните — двигать карту"}
          </span>
        </p>
      )}
      {interactive && navigation.isZoomed && (
        <button
          type="button"
          className={styles.reset}
          data-map-controls
          onClick={() => {
            navigation.reset();
            viewport.current?.focus({ preventScroll: true });
          }}
        >
          <RotateCcw size={18} aria-hidden="true" /> Вернуть карту
        </button>
      )}
      <section
        inert={!interactive}
        ref={viewport}
        className={styles.map}
        aria-label="Карта доступных перевозчиков"
        aria-describedby={description}
        data-mode="live"
        data-map-viewport
        data-map-scale={navigation.scale}
        // biome-ignore lint/a11y/noNoninteractiveTabindex: Keyboard zoom and arrow navigation expose the entire city.
        tabIndex={interactive ? 0 : -1}
      >
        <div
          className={styles.surface}
          style={navigation.style}
          data-map-surface
          data-motion-reason={
            failed
              ? "load-error"
              : reduced
                ? "reduced-motion"
                : !assets
                  ? "images-loading"
                  : "ready"
          }
          data-motion-state={playing && assets ? "playing" : "paused"}
        >
          <>
            <img
              className={styles.plate}
              src={plateSource(plate)}
              srcSet={plateSrcSet(plate)}
              sizes="100vw"
              alt="Город со складом в центре и четыре грузовика"
              data-city-poster
              data-city-plate={plate}
              decoding="async"
            />
            <button
              type="button"
              className={styles.autopick}
              data-map-autopick
              data-carrier-choice="express"
              style={{
                // The canvas draws the pill here (cityV4 expressCall) and
                // hides it while any option is open; so does the hit area.
                visibility: selectedId ? "hidden" : undefined,
                left: `${landmark(plate, "express")[0] * 100}%`,
                top: `${landmark(plate, "express")[1] * 100}%`,
              }}
              aria-label="Express: подобрать фуру"
              aria-pressed={selectedId === "express"}
              onClick={() => onSelect?.("express")}
            />
          </>
          {onSelect &&
            mapCarrierIds.map((id, index) => (
              <button
                ref={(element) => {
                  targets.current[index] = element;
                }}
                type="button"
                key={id}
                className={styles.target}
                data-carrier-choice={id}
                style={{
                  left: `${frameAt()[index][0] * 100}%`,
                  top: `${frameAt()[index][1] * 100}%`,
                  transform: "translate(-50%, -50%)",
                  // A rig is ~21 m long and ~4.5 m wide in plate metres.
                  width: `max(calc(44px / var(--map-zoom, 1)), ${(22 / plates[plate].mpp / plates[plate].res[0]) * 100}cqw)`,
                  height: `max(calc(36px / var(--map-zoom, 1)), ${(9 / plates[plate].mpp / plates[plate].res[0]) * 100}cqw)`,
                }}
                aria-label={`Рассмотреть: ${carrierFacts[id].label}`}
                aria-pressed={selectedId === id}
                onClick={() => {
                  onSelect(id);
                }}
              />
            ))}
        </div>
        <canvas
          ref={dynamicCanvas}
          className={styles.overlay}
          aria-hidden="true"
          data-carrier-effects
        />
        <p id={description} className={styles.hidden}>
          Раздвигайте и сводите пальцы, чтобы менять масштаб карты. На
          компьютере используйте колёсико мыши или жест масштабирования на
          тачпаде. Перемещайте карту пальцем или перетаскивайте её, зажав кнопку
          мыши. Нажмите на фуру, чтобы рассмотреть её. С клавиатуры: плюс и
          минус меняют масштаб, стрелки перемещают карту, Home возвращает
          начальный вид.
        </p>
      </section>
    </div>
  );
}
