import { clearReadingState } from "./useReadingState";

export function briefingReadingKeys(title: string, paragraphs: string[]) {
  const text = paragraphs.join("\n\n");
  return [
    "briefing:open:" + title + text,
    "SceneBriefing:page:" + text,
  ] as const;
}

export function resetBriefingReadingState(
  scope: string | undefined,
  title: string,
  paragraphs: string[],
) {
  clearReadingState(scope, [
    ...briefingReadingKeys(title, paragraphs),
    "map-navigation:" + title,
  ]);
}
