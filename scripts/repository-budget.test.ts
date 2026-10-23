import { test, expect } from "bun:test";
import { mkdtempSync, writeFileSync, mkdirSync, symlinkSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { inspectBudget, inspectLocalGenerated, inspectGitStorage, trackedEntries, type Budget } from "./repository-budget";

const budget: Budget = { maxFileBytes: 100, maxTrackedBytes: 150, maxPngBytes: 40, maxPdfBytes: 80, forbiddenPatterns: [".tmp-work/**", "**/*-frames/**"], exceptions: [] };
function fixture(run: (root: string, git: (...args: string[]) => void) => void) {
  const root = mkdtempSync(path.join(tmpdir(), "repository-budget-"));
  const git = (...args: string[]) => { const result = spawnSync("git", args, { cwd: root, encoding: "utf8" }); expect(result.status, result.stderr).toBe(0); };
  try { git("init", "-q"); run(root, git); } finally { rmSync(root, { recursive: true, force: true }); }
}

test("index checks staged bytes even after an oversized file is shrunk only in the worktree", () => fixture((root, git) => {
  writeFileSync(path.join(root, "asset.bin"), Buffer.alloc(120)); git("add", "asset.bin");
  writeFileSync(path.join(root, "asset.bin"), "small unstaged content");
  const entries = trackedEntries(root);
  expect(entries).toEqual([{ path: "asset.bin", bytes: 120 }]);
  expect(inspectBudget(entries, budget).violations).toContain("asset.bin: 120 bytes exceeds file budget 100");
}));

test("staged deletion removes bytes; untracked files do not inflate the candidate", () => fixture((root, git) => {
  writeFileSync(path.join(root, "keep.txt"), "keep"); writeFileSync(path.join(root, "remove.txt"), "remove"); git("add", ".");
  git("rm", "--cached", "remove.txt"); writeFileSync(path.join(root, "large-untracked.bin"), Buffer.alloc(1000));
  expect(trackedEntries(root)).toEqual([{ path: "keep.txt", bytes: 4 }]);
}));

test("forbidden generated sequences remain forbidden even with an oversized-file exception", () => {
  const result = inspectBudget([{ path: "design/pilot/final-4k-frames/0001.png", bytes: 120 }], {
    ...budget, exceptions: [{ pattern: "design/**", maxBytes: 200, allowLargePng: true, reason: "An exception cannot permit generated frame sequences." }],
  });
  expect(result.violations).toEqual(["design/pilot/final-4k-frames/0001.png: generated/private directory must not be tracked"]);
});

test("PNG lossless exceptions require a reason and do not bypass PDF or aggregate budgets", () => {
  const configured = { ...budget, exceptions: [{ pattern: "art/accepted/*.png", maxBytes: 200, allowLargePng: true, reason: "Source alpha is essential for accepted transparent artwork." }] };
  expect(inspectBudget([{ path: "art/accepted/master.png", bytes: 120 }], configured).violations).toEqual([]);
  const result = inspectBudget([{ path: "art/accepted/master.png", bytes: 120 }, { path: "review.pdf", bytes: 90 }], configured);
  expect(result.violations).toContain("review.pdf: PDF exceeds 80 bytes; compress the delivery report");
  expect(result.violations).toContain("Tracked total 210 bytes exceeds repository budget 150");
  expect(() => inspectBudget([], { ...configured, exceptions: [{ ...configured.exceptions[0], reason: "ok" }] })).toThrow("specific reason");
});

test("HEAD mode checks committed files independently of staged changes", () => fixture((root, git) => {
  writeFileSync(path.join(root, "committed.txt"), "original"); git("add", ".");
  git("-c", "user.name=Budget Test", "-c", "user.email=budget@example.invalid", "commit", "-qm", "fixture");
  writeFileSync(path.join(root, "staged.txt"), "staged"); git("add", "staged.txt");
  expect(trackedEntries(root, true)).toEqual([{ path: "committed.txt", bytes: 8 }]);
  expect(trackedEntries(root).length).toBe(2);
}));

test("only an exact original PDF exception can exceed the compressed-report limit", () => {
  const configured = { ...budget, exceptions: [{ pattern: "materials/brand-guide.pdf", maxBytes: 200, allowLargePdf: true, reason: "Original brand document retained verbatim as a source reference." }] };
  expect(inspectBudget([{ path: "materials/brand-guide.pdf", bytes: 120 }], configured).violations).toEqual([]);
  expect(inspectBudget([{ path: "docs/reviews/report.pdf", bytes: 90 }], configured).violations).toContain("docs/reviews/report.pdf: PDF exceeds 80 bytes; compress the delivery report");
  expect(() => inspectBudget([], { ...configured, exceptions: [{ ...configured.exceptions[0], pattern: "docs/reviews/report.pdf" }] })).toThrow("original source document");
  expect(() => inspectBudget([], { ...configured, exceptions: [{ ...configured.exceptions[0], pattern: "materials/*.pdf" }] })).toThrow("original source document");
});

test("local cache budget aggregates directories without following nested or root symlinks", () => {
  const root = mkdtempSync(path.join(tmpdir(), "repository-local-budget-"));
  const outside = mkdtempSync(path.join(tmpdir(), "repository-outside-"));
  try {
    for (const folder of [".tmp-work", "build"]) mkdirSync(path.join(root, folder));
    writeFileSync(path.join(root, ".tmp-work/a.bin"), Buffer.alloc(60));
    writeFileSync(path.join(root, "build/b.bin"), Buffer.alloc(50));
    writeFileSync(path.join(outside, "do-not-count.bin"), Buffer.alloc(1000));
    symlinkSync(outside, path.join(root, ".tmp-work/linked-folder"));
    symlinkSync(path.join(outside, "do-not-count.bin"), path.join(root, "build/linked-file"));
    symlinkSync(outside, path.join(root, "release"));
    const result = inspectLocalGenerated(root, { ...budget, maxLocalGeneratedBytes: 100 });
    expect(result.files).toBe(2);
    expect(result.bytes).toBe(110);
    expect(result.violations).toHaveLength(1);
    expect(() => inspectLocalGenerated(root, { ...budget, localGeneratedPaths: ["../outside"] })).toThrow("Unsafe");
    expect(() => inspectLocalGenerated(root, { ...budget, localGeneratedPaths: ["build", "build/nested"] })).toThrow("overlap");
  } finally { rmSync(root, { recursive: true, force: true }); rmSync(outside, { recursive: true, force: true }); }
});

test("local-only CLI runs before git init and never inspects oversized Git storage", () => {
  const root = mkdtempSync(path.join(tmpdir(), "repository-preflight-"));
  try {
    mkdirSync(path.join(root, ".git"));
    mkdirSync(path.join(root, "build"));
    writeFileSync(path.join(root, ".git/pack.bin"), Buffer.alloc(1000));
    writeFileSync(path.join(root, "build/output.bin"), Buffer.alloc(60));
    writeFileSync(path.join(root, "repository-budget.json"), JSON.stringify({ ...budget, maxLocalGeneratedBytes: 100, maxGitBytes: 100 }));
    const script = path.resolve(import.meta.dir, "repository-budget.ts");
    const result = spawnSync(process.execPath, [script, "--local-only"], { cwd: root, encoding: "utf8" });
    expect(result.status, result.stderr).toBe(0);
    expect(result.stdout).not.toContain("Git storage");
    expect(inspectGitStorage(root, { ...budget, maxGitBytes: 100 }).violations).toHaveLength(1);
    writeFileSync(path.join(root, "build/output.bin"), Buffer.alloc(110));
    const exceeded = spawnSync(process.execPath, [script, "--local-only"], { cwd: root, encoding: "utf8" });
    expect(exceeded.status).toBe(1);
    expect(exceeded.stderr).toContain("Local generated total 110");
    rmSync(path.join(root, ".git"), { recursive: true });
    writeFileSync(path.join(root, ".git"), "gitdir: /external/worktree");
    expect(inspectGitStorage(root, { ...budget, maxGitBytes: 100 }).bytes).toBe(0);
  } finally { rmSync(root, { recursive: true, force: true }); }
});
