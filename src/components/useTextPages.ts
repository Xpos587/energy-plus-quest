import { useLayoutEffect, useRef, useState } from "react";
import { readingLeadStyle, readingRemainderStyle, splitPageLead } from "./PageText";

/** Alternating paragraphs and their exact authored separators. */
export function splitReadingParagraphs(text: string): string[] {
  return text.split(/(\n[\t ]*\n(?:[\t ]*\n)*)/u);
}

/** Prefer sentences, optionally fill by words; joined pages recover the source. */
export function splitTextPages(
  text: string,
  limit = 260,
  fits?: (text: string, pageIndex: number) => boolean,
  fillSpace = false,
  fillWords = false,
): string[] {
  const pages: string[] = [];
  let page = "";
  const accepts = (value: string, pageIndex = pages.length) =>
    fits ? fits(value, pageIndex) : value.length <= limit;
  const segments = fillSpace && (!fits || fillWords)
    ? Array.from(text.matchAll(/\S+\s*|\s+/gu), match => ({ segment: match[0] }))
    : new Intl.Segmenter("ru", { granularity: "sentence" }).segment(text);
  for (const { segment } of segments) {
    if (
      page &&
      (!accepts(page + segment) || (!fits && /\n\s*\n$/.test(page)))
    ) {
      pages.push(page);
      page = "";
    }
    if (fits && !accepts(segment)) {
      const words = segment.match(/\S+\s*|\s+/gu) ?? [];
      // Find the longest fitting prefix instead of laying out every word.
      for (let start = 0; start < words.length;) {
        let lo = start + 1;
        let hi = words.length;
        while (lo < hi) {
          const mid = Math.ceil((lo + hi) / 2);
          if (accepts(page + words.slice(start, mid).join(""))) lo = mid;
          else hi = mid - 1;
        }
        page += words.slice(start, lo).join("");
        start = lo;
        if (start < words.length) { pages.push(page); page = ""; }
      }
    } else {
      page += segment;
    }
  }
  if (page) pages.push(page);
  if (fits && !fillSpace) {
    for (let index = pages.length - 1; index > 0; index--) {
      const left = pages[index - 1];
      const right = pages[index];
      const combined = left + right;
      if (accepts(combined, index - 1)) {
        pages.splice(index - 1, 2, combined);
        continue;
      }
      if (right.trim().length >= left.trim().length * 0.4) continue;
      // Prefer complete sentences; rebalance by words only if a sentence itself
      // is too long. Every candidate keeps the original characters untouched.
      let offset = 0;
      const sentenceEnds = new Set<number>();
      for (const { segment } of new Intl.Segmenter("ru", {
        granularity: "sentence",
      }).segment(combined)) {
        offset += segment.length;
        sentenceEnds.add(offset);
      }
      const splits = Array.from(combined.matchAll(/\s+(?=\S)/gu), m => m.index + m[0].length);
      const score = (at: number) => Math.abs(2 * at - combined.length) + (sentenceEnds.has(at) ? 0 : combined.length);
      // Same stable preference as a full scan; stop measuring at its first fit.
      const best = splits.sort((a, b) => score(a) - score(b)).find(at => {
        const first = combined.slice(0, at), second = combined.slice(at);
        return Math.min(first.trim().length, second.trim().length) >= combined.trim().length * 0.28 &&
          accepts(first, index - 1) && accepts(second, index);
      }) ?? left.length;
      pages.splice(index - 1, 2, combined.slice(0, best), combined.slice(best));
    }
  }
  return pages;
}

/** Preserve authored paragraph boundaries while filling each measured page. */
export function paginateTextBlocks(
  blocks: string[],
  fits?: (text: string, pageIndex: number) => boolean,
  merge = false,
): string[] {
  if (merge) return splitTextPages(blocks.join("\n\n"), 260, fits);
  const pages: string[] = [];
  for (const block of blocks) {
    const offset = pages.length;
    pages.push(...splitTextPages(block, 260, fits && ((value, index) => fits(value, offset + index))));
  }
  return pages;
}

export function useTextPages(
  paragraphs: string[],
  enabled = true,
  fitMaxHeight = false,
  keepBlocks = false,
  preserveWhitespace = false,
  fillSpace = false,
  mergeBlocks = false,
  leadLength = 0,
  capPages = false,
) {
  const text = JSON.stringify(paragraphs);
  const body = useRef<HTMLDivElement>(null);
  const [pages, setPages] = useState(() =>
    paragraphs.flatMap((part) => splitTextPages(part)),
  );
  useLayoutEffect(() => {
    const container = body.current;
    if (!container) return;
    const paginate = () => {
      const resultFrame = capPages ? container.closest<HTMLElement>('[data-layout="result"]') : null;
      resultFrame?.style.removeProperty("--scene-panel-height");
      // Portrait results have variable titles, links and footer rows. Reserve
      // their actual height instead of estimating it from the viewport width.
      if (getComputedStyle(container).getPropertyValue("--result-fit-viewport").trim() === "1") {
        const frame = container.closest<HTMLElement>('[data-layout="result"]');
        const panel = container.closest<HTMLElement>("[data-sheet-panel]");
        if (frame && panel) {
          const reading = container.getBoundingClientRect();
          const panelBox = panel.getBoundingClientRect();
          const reader = container.closest<HTMLElement>('[data-result-reader]');
          const narrative = container.closest<HTMLElement>('[data-result-narrative]');
          let reserved = panelBox.bottom - reading.bottom;
          if (reader && narrative) {
            const following = Array.from(reader.children).slice(Array.from(reader.children).indexOf(narrative) + 1)
              .filter((element) => element.getBoundingClientRect().height > 0);
            const readerStyle = getComputedStyle(reader);
            // Result controls use the reader's gap. Their auto margins are spare
            // reading space, not content to reserve (computed styles resolve them to pixels).
            reserved = following.reduce((total, element) => total + element.getBoundingClientRect().height, 0)
              + (parseFloat(readerStyle.rowGap) || 0) * following.length
              + parseFloat(readerStyle.paddingBottom) + parseFloat(getComputedStyle(panel).paddingBottom);
          }
          const panelLimit = parseFloat(getComputedStyle(panel).maxHeight);
          const available = Math.max(1, Number.isFinite(panelLimit)
            // A content-sized sheet would otherwise shrink to its current page.
            ? panelBox.top + panelLimit - reading.top - reserved
            : Math.min(frame.getBoundingClientRect().bottom, panelBox.bottom) - reading.top - reserved);
          container.style.setProperty("--result-reading-height", `${available}px`);
        }
      }
      const computed = getComputedStyle(container);
      const width =
        container.clientWidth -
        parseFloat(computed.paddingLeft) -
        parseFloat(computed.paddingRight);
      const maxHeight = parseFloat(computed.maxHeight);
      const fitViewport = computed.getPropertyValue("--result-fit-viewport").trim() === "1";
      const height =
        ((fitMaxHeight || fitViewport) && Number.isFinite(maxHeight)
          ? Math.max(parseFloat(computed.minHeight) || 0, maxHeight)
          // clientHeight rounds away fractional line heights. Comparing that
          // integer with the probe's fractional height can reject text that
          // fits exactly and repeatedly toggle the compact result layout.
          : container.getBoundingClientRect().height -
            parseFloat(computed.borderTopWidth) -
            parseFloat(computed.borderBottomWidth)) -
        parseFloat(computed.paddingTop) -
        parseFloat(computed.paddingBottom);
      if (width <= 0 || height <= 0) return;
      const sources: string[] = JSON.parse(text);
      const probe = document.createElement("p");
      probe.style.cssText = `position:absolute;visibility:hidden;pointer-events:none;width:${width}px;inset:0 auto auto 0;margin:0;white-space:pre-wrap;overflow-wrap:anywhere;`;
      container.append(probe);
      const paragraphGap = parseFloat(computed.getPropertyValue("--reading-paragraph-gap"));
      // Reuse heights only within this pass; resize/font changes measure afresh.
      const measured = new Map<string, number>();
      const keyFor = (value: string, pageIndex: number) => `${pageIndex === 0 && leadLength > 0}:${value}`;
      const prepare = (probe: HTMLParagraphElement, value: string, pageIndex: number) => {
        const candidate = preserveWhitespace ? value : value.trim();
        if (pageIndex === 0 && leadLength > 0) {
          const leadingLength = value.length - value.trimStart().length;
          const { lead, remainder } = splitPageLead(candidate, leadLength - (preserveWhitespace ? 0 : leadingLength));
          const opening = document.createElement("span");
          opening.textContent = lead;
          Object.assign(opening.style, readingLeadStyle);
          probe.replaceChildren(opening);
          if (remainder) {
            const prose = document.createElement("span");
            prose.textContent = remainder;
            Object.assign(prose.style, readingRemainderStyle, { marginTop: `${readingRemainderStyle.marginTop}px` });
            probe.append(prose);
          }
        } else if (Number.isFinite(paragraphGap)) {
          probe.replaceChildren(...splitReadingParagraphs(candidate).map((part, index) => {
            const span = document.createElement("span");
            span.textContent = part;
            if (index % 2) span.hidden = true;
            else {
              span.style.display = "block";
              if (index > 0) span.style.marginTop = `${paragraphGap}px`;
            }
            return span;
          }));
        } else probe.textContent = candidate;
      };
      const measure = (value: string, pageIndex: number) => {
        const key = keyFor(value, pageIndex);
        const cached = measured.get(key);
        if (cached !== undefined) return cached;
        prepare(probe, value, pageIndex);
        const measuredHeight = probe.getBoundingClientRect().height;
        measured.set(key, measuredHeight);
        return measuredHeight;
      };
      const measureTogether = (values: string[]) => {
        const pending = new Map<string, HTMLParagraphElement>();
        for (const value of values) {
          const key = keyFor(value, 1);
          if (measured.has(key) || pending.has(key)) continue;
          const candidate = probe.cloneNode(false) as HTMLParagraphElement;
          prepare(candidate, value, 1);
          pending.set(key, candidate);
        }
        // Insert every candidate before reading heights; one layout for this batch.
        container.append(...pending.values());
        for (const [key, candidate] of pending) measured.set(key, candidate.getBoundingClientRect().height);
        for (const candidate of pending.values()) candidate.remove();
      };
      // Serialized lh limits can differ from laid-out lines by a fraction of a pixel.
      const fits = (value: string, pageIndex: number) => measure(value, pageIndex) <= height + 0.5;
      const fitted = capPages
        ? (() => {
          // Results read as at most two sentence-bounded pages (three for long
          // copy). Authored beats keep their own page. Before splitting a
          // sentence, the sheet grows by up to two lines.
          const source = sources.join("\n\n");
          const tall = (value: string) => measure(value, 1);
          const lineHeight = parseFloat(computed.lineHeight) || 0;
          // CSS serialization rounds fractional heights; allow subpixels, not half a line.
          const limit = height + 0.5;
          const panel = container.closest<HTMLElement>("[data-sheet-panel]");
          const grow = (need: number) => {
            if (fitViewport || !resultFrame || !panel || need - height > lineHeight * 2) return false;
            resultFrame.style.setProperty("--scene-panel-height", `${Math.ceil(panel.getBoundingClientRect().height + need - height)}px`);
            if (container.getBoundingClientRect().height >= need - 1) return true;
            resultFrame.style.removeProperty("--scene-panel-height");
            return false;
          };
          if (keepBlocks) {
            measureTogether(sources);
            const worst = Math.max(...sources.map(tall));
            return worst <= limit || grow(worst) ? sources : paginateTextBlocks(sources, fits, mergeBlocks);
          }
          const sentences = Array.from(new Intl.Segmenter("ru", { granularity: "sentence" }).segment(source), (part) => part.segment);
          const join = (from: number, to: number) => sentences.slice(from, to).join("");
          let best = [source];
          let worst = tall(source);
          for (let count = 2; count <= Math.min(3, sentences.length) && worst > limit; count++) {
            const candidates: string[][] = [];
            for (let i = 1; i < sentences.length; i++)
              for (let j = count > 2 ? i + 1 : sentences.length; j <= sentences.length - (count > 2 ? 1 : 0); j++)
                candidates.push(count > 2 ? [join(0, i), join(i, j), join(j, sentences.length)] : [join(0, i), join(i, sentences.length)]);
            measureTogether(candidates.flat());
            let score = Infinity;
            for (const parts of candidates) {
              const heights = parts.map(tall);
              const candidate = Math.max(...heights) * 1000 + Math.max(...heights) - Math.min(...heights);
              if (candidate < score) [score, best, worst] = [candidate, parts, Math.max(...heights)];
            }
            if (worst > limit && (count === 3 || source.length <= 600) && grow(worst)) return best;
          }
          return worst > limit ? splitTextPages(source, 260, fits) : best;
        })()
        : keepBlocks
        ? paginateTextBlocks(sources, fits, mergeBlocks)
        : splitTextPages(sources.join("\n\n"), 260, fits, fillSpace, fitViewport);
      probe.remove();
      setPages((previous) =>
        previous.length === fitted.length &&
        previous.every((part, index) => part === fitted[index])
          ? previous
          : fitted,
      );
    };
    // The first ResizeObserver notification already measures the mounted layout.
    // Doing it synchronously as well repeats the work inside the click handler.
    const observer = typeof ResizeObserver === "undefined" ? null : new ResizeObserver(paginate);
    if (observer) observer.observe(container);
    else paginate();
    const resultFrame = container.closest('[data-layout="result"]');
    if (resultFrame) observer?.observe(resultFrame);
    const resultPanel = container.closest("[data-sheet-panel]");
    if (resultPanel) observer?.observe(resultPanel);
    window.addEventListener("resize", paginate);
    document.fonts?.addEventListener("loadingdone", paginate);
    return () => {
      observer?.disconnect();
      document.fonts?.removeEventListener("loadingdone", paginate);
      window.removeEventListener("resize", paginate);
    };
  }, [text, enabled, fitMaxHeight, keepBlocks, preserveWhitespace, fillSpace, mergeBlocks, leadLength, capPages]);
  return { body, pages };
}
