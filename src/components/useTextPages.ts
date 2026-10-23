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
      for (const word of segment.match(/\S+\s*|\s+/gu) ?? []) {
        if (page && !accepts(page + word)) {
          pages.push(page);
          page = "";
        }
        page += word;
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
      let best = left.length;
      let bestScore = Infinity;
      for (const match of combined.matchAll(/\s+(?=\S)/gu)) {
        const split = match.index + match[0].length;
        const first = combined.slice(0, split);
        const second = combined.slice(split);
        if (
          Math.min(first.trim().length, second.trim().length) <
          combined.trim().length * 0.28
        )
          continue;
        if (!accepts(first, index - 1) || !accepts(second, index)) continue;
        const score =
          Math.abs(first.length - second.length) +
          (sentenceEnds.has(split) ? 0 : combined.length);
        if (score < bestScore) {
          best = split;
          bestScore = score;
        }
      }
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
            reserved = following.reduce((total, element) => {
              const style = getComputedStyle(element);
              return total + element.getBoundingClientRect().height + parseFloat(style.marginTop) + parseFloat(style.marginBottom);
            }, 0) + (parseFloat(readerStyle.rowGap) || 0) * following.length
              + parseFloat(readerStyle.paddingBottom) + parseFloat(getComputedStyle(panel).paddingBottom);
          }
          const available = Math.max(1, Math.min(frame.getBoundingClientRect().bottom, panelBox.bottom) - reading.top - reserved);
          container.style.setProperty("--result-reading-height", `${available}px`);
        }
      }
      const computed = getComputedStyle(container);
      const width =
        container.clientWidth -
        parseFloat(computed.paddingLeft) -
        parseFloat(computed.paddingRight);
      const maxHeight = parseFloat(computed.maxHeight);
      const height =
        (fitMaxHeight && Number.isFinite(maxHeight)
          ? maxHeight
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
      const fits = (value: string, pageIndex: number) => {
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
        return probe.getBoundingClientRect().height <= height;
      };
      const fitted = keepBlocks
        ? paginateTextBlocks(sources, fits, mergeBlocks)
        : splitTextPages(sources.join("\n\n"), 260, fits, fillSpace,
          computed.getPropertyValue("--result-fit-viewport").trim() === "1");
      probe.remove();
      setPages((previous) =>
        previous.length === fitted.length &&
        previous.every((part, index) => part === fitted[index])
          ? previous
          : fitted,
      );
    };
    paginate();
    const observer =
      typeof ResizeObserver === "undefined"
        ? null
        : new ResizeObserver(paginate);
    observer?.observe(container);
    const resultFrame = container.closest('[data-layout="result"]');
    if (resultFrame) observer?.observe(resultFrame);
    const resultPanel = container.closest("[data-sheet-panel]");
    if (resultPanel) observer?.observe(resultPanel);
    window.addEventListener("resize", paginate);
    let active = true;
    document.fonts?.ready.then(() => {
      if (active) paginate();
    });
    return () => {
      active = false;
      observer?.disconnect();
      window.removeEventListener("resize", paginate);
    };
  }, [text, enabled, fitMaxHeight, keepBlocks, preserveWhitespace, fillSpace, mergeBlocks, leadLength]);
  return { body, pages };
}
