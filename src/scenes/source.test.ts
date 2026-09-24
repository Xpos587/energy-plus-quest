import { describe, expect, it } from "vitest";
import { source } from "./source";
import records from "./sourceCopy.json";

describe("verbatim scenario source", () => {
  it("returns the document paragraph without rewriting or trimming", () => {
    for (const record of records) expect(source(record.id)).toBe(record.text);
  });
  it("rejects a missing source instead of displaying empty copy", () => {
    expect(() => source("missing")).toThrow("missing");
  });
});
