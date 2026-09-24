import records from "./sourceCopy.json";

const paragraphs = new Map(records.map(({ id, text }) => [id, text]));

export function source(id: string): string {
  const text = paragraphs.get(id);
  if (text === undefined) throw new Error(`Missing scenario paragraph: ${id}`);
  return text;
}
