// SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0
import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { ResultsError, validateResults } from "./results";

const good = () => JSON.parse(readFileSync("public/data/results.json", "utf8"));

describe("validateResults", () => {
  it("accepts the exported results file", () => {
    expect(validateResults(good()).experiments.length).toBeGreaterThan(0);
  });
  it("rejects a wrong schema name", () => {
    expect(() => validateResults({ ...good(), schema: "other" })).toThrow(ResultsError);
  });
  it("rejects an unsupported major version", () => {
    expect(() => validateResults({ ...good(), schema_version: "2.0.0" })).toThrow(ResultsError);
  });
  it("rejects a missing estimate", () => {
    const r = good();
    delete r.experiments[0].estimates?.[0]?.estimate;
    if (r.experiments[0].estimates.length === 0) r.experiments[0].title = 7;
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects a non-finite number", () => {
    const r = good();
    r.experiments[0].estimates = [{ label: "x", estimate: "NaN", ci_low: null, ci_high: null, ci_level: null, unit: "" }];
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects a half-open interval", () => {
    const r = good();
    r.experiments[0].estimates = [{ label: "x", estimate: 1, ci_low: 0, ci_high: null, ci_level: 0.95, unit: "" }];
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects a malformed source hash", () => {
    expect(() => validateResults({ ...good(), sources: [{ path: "a", sha256: "zz" }] })).toThrow(ResultsError);
  });
  it("rejects an estimate without the manuscript's display text", () => {
    const r = good();
    r.experiments[0].estimates[0].display = null;
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects an unknown result kind", () => {
    const r = good();
    r.experiments[0].estimates[0].kind = "positive";
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects missing project data (arm means, curves, replay)", () => {
    for (const k of ["arm_means", "curves", "replay"]) {
      const r = good();
      delete r[k];
      expect(() => validateResults(r)).toThrow(ResultsError);
    }
  });
  it("rejects a curve whose quartiles are out of order", () => {
    const r = good();
    r.curves.items[0].arms[0].q25[5] = 24;
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects a truncated or inconsistent replay trace", () => {
    const r = good();
    r.replay.arms[0].runs[0].fitness_hex = r.replay.arms[0].runs[0].fitness_hex.slice(2);
    expect(() => validateResults(r)).toThrow(ResultsError);
    const r2 = good();
    r2.replay.arms[2].runs[0].returned_index = 0;
    expect(() => validateResults(r2)).toThrow(ResultsError);
    const r3 = good();
    const p = r3.replay.arms[2].runs[0].parents_b64;
    r3.replay.arms[2].runs[0].parents_b64 = "A" + p.slice(1);
    expect(() => validateResults(r3)).toThrow(ResultsError);
  });
  it("decodes the committed replay traces", () => {
    const r = validateResults(good());
    const evo = r.replay.arms.find((a) => a.arm === "EVO")!;
    expect(evo.runs.length).toBe(30);
    expect(evo.runs[0].fitness.length).toBe(2000);
    expect(evo.runs[0].parents[60]).toBeGreaterThanOrEqual(0);
  });
});
