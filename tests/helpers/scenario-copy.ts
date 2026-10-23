import { readFileSync } from "node:fs";

const markdown = readFileSync(
  new URL("../../docs/scenario.md", import.meta.url),
  "utf8",
);
const blocks = new Map<string, { role: string; text: string }>();
for (const [, id, role, body] of markdown.matchAll(
  /<!-- scenario-block id="([^"]+)" role="([^"]+)" origin="[^"]+" -->\n([\s\S]*?)<!-- \/scenario-block -->/g,
)) {
  if (blocks.has(id)) throw new Error(`Duplicate scenario block: ${id}`);
  blocks.set(id, {
    role,
    text: body
      .split("\n")
      .filter((line) => line.startsWith("> "))
      .map((line) => line.slice(2).replace(/\\([\\`*_<>{}[\]])/g, "$1"))
      .join("\n"),
  });
}

export function scenarioParagraph(id: string, role = "text"): string {
  const block = blocks.get(id);
  if (!block) throw new Error(`Missing canonical scenario block: ${id}`);
  if (block.role !== role)
    throw new Error(`Scenario block ${id} is ${block.role}, not ${role}`);
  return block.text;
}

const paragraph = (id: string) =>
  scenarioParagraph(id)
    .trim()
    .replaceAll("%имя получателя%", "{recipient}")
    .replaceAll(
      "%название посылки%",
      id === "512D2AEE" ? "{parcelGenitive}" : "{parcel}",
    )
    .replaceAll("%выбранную посылку%", "{parcel}")
    .replaceAll("%Посылку%", "{parcel}")
    .replaceAll("№герой%", "{recipientDative}");
const intro = paragraph("2A80D000");
const prompt = intro.slice(intro.lastIndexOf(". ") + 2);
const near = paragraph("512D2AEE");
const nearHeading = near.slice(0, near.indexOf("!") + 1);

export const sourceCopy = {
  carrierPrompt: prompt,
  carrierBriefing: intro.slice(0, -prompt.length).trim(),
  outcomes: {
    old: { heading: "", body: paragraph("6656C720") },
    near: { heading: nearHeading, body: near.slice(nearHeading.length).trim() },
    crew: { heading: paragraph("4264BB8C"), body: paragraph("67C929B0") },
    express: {
      heading: "",
      body: [paragraph("7E9315CC"), paragraph("46FE90C1")].join("\n\n"),
    },
  },
} as const;
