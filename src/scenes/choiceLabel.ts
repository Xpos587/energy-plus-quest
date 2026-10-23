/** Strip document list markers without changing the scenario wording. */
export function choiceLabel(label: string): string {
  return label.replace(
    /^\s*(?:(?:Место|Вариант)\s*№?\s*\d+|№\s*\d+|\d+[.)])(?:[.):]\s*|\s+)*/u,
    "",
  );
}
