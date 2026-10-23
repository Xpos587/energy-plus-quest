export const readingLeadStyle = { display: "block", fontWeight: 600 } as const;
export const readingRemainderStyle = { display: "block", fontWeight: 400, marginTop: 8 } as const;

/** Offset includes authored separators; rendering hides them without losing them. */
export function openingSentenceLength(text: string): number {
  for (const { segment, index } of new Intl.Segmenter("ru", { granularity: "sentence" }).segment(text)) {
    if (segment.trim()) return index + segment.length;
  }
  return 0;
}

export function splitPageLead(text: string, leadLength = 0) {
  const end = Math.min(text.length, Math.max(0, leadLength));
  const lead = text.slice(0, end).trimEnd();
  const rest = text.slice(lead.length);
  const separator = rest.match(/^\s*/u)?.[0] ?? "";
  return { lead, separator, remainder: rest.slice(separator.length) };
}

/** Preserve source whitespace for text extraction, without blank lines at page edges. */
export function PageText({ text = "", leadLength = 0 }: { text?: string; leadLength?: number }) {
  const leading = text.match(/^\s*/u)?.[0] ?? "";
  const rest = text.slice(leading.length);
  const trailing = rest.match(/\s*$/u)?.[0] ?? "";
  const visible = rest.slice(0, rest.length - trailing.length);
  const opening = leadLength > leading.length
    ? splitPageLead(visible, leadLength - leading.length)
    : undefined;
  return (
    <>
      <span hidden aria-hidden="true">
        {leading}
      </span>
      {opening ? <>
        <span data-reading-lead style={readingLeadStyle}>{opening.lead}</span>
        <span hidden aria-hidden="true">{opening.separator}</span>
        {opening.remainder && <span data-reading-remainder style={readingRemainderStyle}>{opening.remainder}</span>}
      </> : visible}
      <span hidden aria-hidden="true">
        {trailing}
      </span>
    </>
  );
}
