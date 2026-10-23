import { spawnSync } from "node:child_process";
import { lstatSync, readdirSync, readFileSync } from "node:fs";
import path from "node:path";

export interface SizeException {
  pattern: string;
  maxBytes: number;
  allowLargePng?: boolean;
  allowLargePdf?: boolean;
  reason: string;
}
export interface Budget {
  maxFileBytes: number;
  maxTrackedBytes: number;
  maxPngBytes: number;
  maxPdfBytes: number;
  forbiddenPatterns: string[];
  exceptions: SizeException[];
  maxLocalGeneratedBytes?: number;
  localGeneratedPaths?: string[];
  maxGitBytes?: number;
}
export interface Entry { path: string; bytes: number }
export interface Result { files: number; bytes: number; violations: string[] }

function git(cwd: string, args: string[], input?: string): string {
  const result = spawnSync("git", args, { cwd, input, encoding: "utf8", maxBuffer: 32 * 1024 * 1024 });
  if (result.status !== 0) throw new Error(`git ${args[0]} failed: ${result.stderr.trim()}`);
  return result.stdout;
}

/** The staged object sizes are authoritative; unstaged edits cannot evade this check. */
export function trackedEntries(cwd: string, head = false): Entry[] {
  if (head) {
    return git(cwd, ["ls-tree", "-r", "-l", "-z", "HEAD"]).split("\0").filter(Boolean).map(row => {
      const tab = row.indexOf("\t");
      const metadata = row.slice(0, tab).trim().split(/\s+/);
      if (metadata[1] !== "blob") throw new Error(`Unsupported tracked entry: ${row.slice(tab + 1)}`);
      return { path: row.slice(tab + 1), bytes: Number(metadata[3]) };
    });
  }
  const rows = git(cwd, ["ls-files", "--stage", "-z"]).split("\0").filter(Boolean).map(row => {
    const tab = row.indexOf("\t");
    const [mode, object, stage] = row.slice(0, tab).split(" ");
    if (stage !== "0") throw new Error(`Resolve the index conflict first: ${row.slice(tab + 1)}`);
    if (mode === "160000") throw new Error(`Submodule storage is not covered by this budget: ${row.slice(tab + 1)}`);
    return { path: row.slice(tab + 1), object };
  });
  if (!rows.length) return [];
  // Git reads existing object metadata; this does not hash or read file contents.
  const sizes = git(cwd, ["cat-file", "--batch-check=%(objectsize)"], rows.map(row => row.object).join("\n") + "\n")
    .trim().split("\n").map(Number);
  return rows.map((row, index) => {
    if (!Number.isSafeInteger(sizes[index]) || sizes[index] < 0) throw new Error(`Missing staged object: ${row.path}`);
    return { path: row.path, bytes: sizes[index] };
  });
}

export function glob(pattern: string, value: string): boolean {
  let source = "^";
  for (let index = 0; index < pattern.length; index++) {
    const char = pattern[index];
    if (char === "*" && pattern[index + 1] === "*") {
      index++;
      if (pattern[index + 1] === "/") { index++; source += "(?:.*/)?"; }
      else source += ".*";
    } else if (char === "*") source += "[^/]*";
    else if (char === "?") source += "[^/]";
    else source += char.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  }
  return new RegExp(source + "$", "i").test(value);
}

function validateBudget(budget: Budget): void {
  for (const key of ["maxFileBytes", "maxTrackedBytes", "maxPngBytes", "maxPdfBytes"] as const) {
    if (!Number.isSafeInteger(budget[key]) || budget[key] < 1) throw new Error(`Invalid budget: ${key}`);
  }
  for (const exception of budget.exceptions) {
    if (!exception.pattern || !Number.isSafeInteger(exception.maxBytes) || exception.maxBytes < 1 || exception.reason.trim().length < 12) {
      throw new Error("Each size exception needs a pattern, positive byte limit and specific reason");
    }
    if (exception.allowLargePdf && (!/\.pdf$/i.test(exception.pattern) || /[*?]/.test(exception.pattern) || /^docs\/reviews\//i.test(exception.pattern))) {
      throw new Error("Large PDF exceptions must name one original source document, never generated review reports");
    }
  }
  for (const key of ["maxLocalGeneratedBytes", "maxGitBytes"] as const) {
    if (budget[key] !== undefined && (!Number.isSafeInteger(budget[key]) || budget[key]! < 1)) throw new Error(`Invalid budget: ${key}`);
  }
}

export function inspectBudget(entries: Entry[], budget: Budget): Result {
  validateBudget(budget);
  const violations: string[] = [];
  let total = 0;
  for (const entry of entries) {
    total += entry.bytes;
    if (budget.forbiddenPatterns.some(pattern => glob(pattern, entry.path))) violations.push(`${entry.path}: generated/private directory must not be tracked`);
    // First match wins: put narrow exceptions before broader asset families.
    const exception = budget.exceptions.find(rule => glob(rule.pattern, entry.path));
    const limit = exception?.maxBytes ?? budget.maxFileBytes;
    if (entry.bytes > limit) violations.push(`${entry.path}: ${entry.bytes} bytes exceeds file budget ${limit}`);
    if (/\.png$/i.test(entry.path) && entry.bytes > budget.maxPngBytes && !exception?.allowLargePng) {
      violations.push(`${entry.path}: large PNG requires compression or a documented lossless exception`);
    }
    if (/\.pdf$/i.test(entry.path) && entry.bytes > budget.maxPdfBytes && !exception?.allowLargePdf) violations.push(`${entry.path}: PDF exceeds ${budget.maxPdfBytes} bytes; compress the delivery report`);
  }
  if (total > budget.maxTrackedBytes) violations.push(`Tracked total ${total} bytes exceeds repository budget ${budget.maxTrackedBytes}`);
  return { files: entries.length, bytes: total, violations };
}

/** Never traverse symlinks, including intermediate path components. */
function localFiles(root: string, relative: string): Entry[] {
  if (path.isAbsolute(relative) || relative.split(/[\\/]/).some(part => part === ".." || part === ".git") || !relative) {
    throw new Error(`Unsafe local generated directory: ${relative}`);
  }
  const components = relative.split(/[\\/]/).filter(Boolean);
  let current = root;
  for (const component of components) {
    current = path.join(current, component);
    try { if (lstatSync(current).isSymbolicLink()) return []; }
    catch (error: any) { if (error.code === "ENOENT") return []; throw error; }
  }
  return walkFiles(current, relative);
}

function walkFiles(absolute: string, relative: string): Entry[] {
  const stat = lstatSync(absolute);
  if (stat.isSymbolicLink()) return [];
  if (stat.isFile()) return [{ path: relative, bytes: stat.size }];
  if (!stat.isDirectory()) return [];
  return readdirSync(absolute).flatMap(name => walkFiles(path.join(absolute, name), `${relative}/${name}`));
}

export function inspectLocalGenerated(root: string, budget: Budget): Result {
  validateBudget(budget);
  // Reject overlapping roots: otherwise nested files would be counted twice.
  const directories = budget.localGeneratedPaths ?? [".tmp-work", "build", "release"];
  const normalized = directories.map(value => value.replace(/\/$/, ""));
  if (normalized.some((value, index) => normalized.some((other, otherIndex) => index !== otherIndex && (value === other || value.startsWith(`${other}/`))))) {
    throw new Error("Local generated directories must not overlap");
  }
  const files = normalized.flatMap(directory => localFiles(root, directory));
  const bytes = files.reduce((sum, file) => sum + file.bytes, 0);
  const limit = budget.maxLocalGeneratedBytes;
  return { files: files.length, bytes, violations: limit !== undefined && bytes > limit ? [`Local generated total ${bytes} bytes exceeds cache budget ${limit}; remove reproducible stale outputs before generating more`] : [] };
}

export function inspectGitStorage(root: string, budget: Budget): Result {
  validateBudget(budget);
  if (budget.maxGitBytes === undefined) return { files: 0, bytes: 0, violations: [] };
  const location = path.join(root, ".git");
  try {
    const stat = lstatSync(location);
    // A worktree .git pointer must not cause traversal of an external common dir.
    if (!stat.isDirectory() || stat.isSymbolicLink()) return { files: 0, bytes: 0, violations: [] };
  } catch (error: any) { if (error.code === "ENOENT") return { files: 0, bytes: 0, violations: [] }; throw error; }
  const files = walkFiles(location, ".git");
  const bytes = files.reduce((sum, file) => sum + file.bytes, 0);
  return { files: files.length, bytes, violations: bytes > budget.maxGitBytes ? [`Git storage ${bytes} bytes exceeds history budget ${budget.maxGitBytes}; inspect historical artifacts before committing more`] : [] };
}

export function main(args = process.argv.slice(2)): number {
  const head = args.includes("--head");
  const localOnly = args.includes("--local-only");
  const configAt = args.indexOf("--config");
  const allowed = args.filter((_, index) => index !== configAt && index !== configAt + 1);
  const unknown = (values: string[]) => values.some(arg => arg !== "--head" && arg !== "--local-only");
  if (head && localOnly || configAt < 0 && unknown(args) || configAt >= 0 && (!args[configAt + 1] || unknown(allowed))) {
    throw new Error("Usage: bun scripts/repository-budget.ts [--head | --local-only] [--config FILE]");
  }
  const budget = JSON.parse(readFileSync(path.resolve(configAt >= 0 ? args[configAt + 1] : "repository-budget.json"), "utf8")) as Budget;
  const results: [string, Result][] = [["Local generated", inspectLocalGenerated(process.cwd(), budget)]];
  if (!localOnly) {
    results.unshift([head ? "HEAD" : "Index", inspectBudget(trackedEntries(process.cwd(), head), budget)]);
    results.push(["Git storage", inspectGitStorage(process.cwd(), budget)]);
  }
  for (const [label, result] of results) {
    console.log(`${label}: ${result.files} files, ${(result.bytes / 1024 ** 2).toFixed(1)} MiB`);
    for (const violation of result.violations) console.error(violation);
  }
  return results.some(([, result]) => result.violations.length) ? 1 : 0;
}
if (import.meta.main) {
  try { process.exitCode = main(); }
  catch (error) { console.error(error instanceof Error ? error.message : String(error)); process.exitCode = 2; }
}
