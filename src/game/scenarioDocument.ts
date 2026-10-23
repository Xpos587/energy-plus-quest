import markdown from "../../docs/scenario.md?raw";

type ScenarioRole = "text" | "visual" | "mechanic" | "scores" | "structure" | "mixed";
const blocks = new Map<string, { role: ScenarioRole; text: string }>();
for (const match of markdown.matchAll(
  /<!-- scenario-block id="([^"]+)" role="([^"]+)" origin="[^"]+" -->\n([\s\S]*?)<!-- \/scenario-block -->/g,
)) {
  const [, id, role, body] = match;
  if (blocks.has(id)) throw new Error(`Duplicate scenario block: ${id}`);
  const text = body.split("\n")
    .filter(line => line.startsWith("> "))
    .map(line => line.slice(2).replace(/\\([\\`*_<>{}\[\]])/g, "$1"))
    .join("\n");
  blocks.set(id, { role: role as ScenarioRole, text });
}

/** Role must match: visual/logic instructions cannot silently become player copy. */
export function scenarioParagraph(id: string, expectedRole: ScenarioRole = "text"): string {
  const block = blocks.get(id);
  if (!block) throw new Error(`Missing canonical scenario block: ${id}`);
  if (block.role !== expectedRole)
    throw new Error(`Scenario block ${id} is ${block.role}, not ${expectedRole}`);
  return block.text;
}
