// SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0
// Published results: loaded from public/data/results.json, which
// scripts/export_demo_data.py writes from committed results only.
// Validation fails closed: any missing or malformed field means no numbers are shown.

export const SCHEMA = "lab-demo-results";
export const SCHEMA_MAJOR = 1;

export interface Estimate {
  label: string;
  estimate: number;
  ci_low: number | null;
  ci_high: number | null;
  ci_level: number | null;
  unit: string;
  /** Exact text the manuscript prints for the estimate and interval; shown verbatim when present. */
  display: string | null;
  interval_display: string | null;
  /** EVOLVE: paired seeds, effect size and reading under the frozen rule. */
  n_pairs: number;
  dz_display: string | null;
  seeds_display: string | null;
  reading: string;
  kind: EstimateKind;
  headline: boolean;
}

export const KINDS = ["supported", "contradicting", "inconclusive", "as-predeclared", "estimate", "descriptive", "exploratory"] as const;
export type EstimateKind = (typeof KINDS)[number];

export interface Experiment {
  id: string;
  title: string;
  status: string;
  verdict: string;
  estimates: Estimate[];
  claim_ids: string[];
  report_path: string;
  notes: string[];
}

export interface Assumption {
  name: string;
  value: string;
  source: string;
}

export interface Source {
  path: string;
  sha256: string;
}

export interface ArmMean {
  experiment_id: string;
  condition: string;
  arm: string;
  n: number;
  mean: number;
  sd: number;
  display: string;
  sd_display: string;
  sd_source: string;
}

export interface CurveArm {
  arm: string;
  n_seeds: number;
  evaluation: number[];
  median: number[];
  q25: number[];
  q75: number[];
}

export interface CurveSet {
  experiment_id: string;
  condition: string;
  budget: number;
  population: number;
  generations: number;
  train_episodes_per_eval: number;
  arms: CurveArm[];
}

export interface ReplayRun {
  seed: number;
  run_id: string;
  returned_index: number;
  f_test: number;
  best_per_generation: number[];
  /** Decoded: training fitness of every evaluation (items per episode). */
  fitness: Float64Array;
  /** Decoded: parent slot in the previous generation, -1 for none. */
  parents: Int16Array;
}

export interface ReplayArm {
  arm: string;
  experiment_id: string;
  runs: ReplayRun[];
}

export interface Replay {
  condition: string;
  budget: number;
  population: number;
  generations: number;
  train_episodes_per_eval: number;
  arms: ReplayArm[];
}

export interface Results {
  schema: string;
  schema_version: string;
  project: string;
  question: string;
  status_label: string;
  code_revision: string;
  sources: Source[];
  experiments: Experiment[];
  assumptions: Assumption[];
  limitations: string[];
  arm_means: ArmMean[];
  curves: { metric: string; summary: string; items: CurveSet[] };
  replay: Replay;
}

export class ResultsError extends Error {}

type Obj = Record<string, unknown>;

function obj(v: unknown, where: string): Obj {
  if (typeof v !== "object" || v === null || Array.isArray(v)) {
    throw new ResultsError(`${where}: expected an object`);
  }
  return v as Obj;
}

function str(o: Obj, k: string, where: string): string {
  const v = o[k];
  if (typeof v !== "string" || v.length === 0) {
    throw new ResultsError(`${where}.${k}: expected a non-empty string`);
  }
  return v;
}

function num(o: Obj, k: string, where: string, nullable = false): number | null {
  const v = o[k];
  if (nullable && v === null) return null;
  if (typeof v !== "number" || !Number.isFinite(v)) {
    throw new ResultsError(`${where}.${k}: expected a finite number`);
  }
  return v;
}

function arr(o: Obj, k: string, where: string): unknown[] {
  const v = o[k];
  if (!Array.isArray(v)) throw new ResultsError(`${where}.${k}: expected an array`);
  return v;
}

function strArr(o: Obj, k: string, where: string): string[] {
  return arr(o, k, where).map((v, i) => {
    if (typeof v !== "string") throw new ResultsError(`${where}.${k}[${i}]: expected a string`);
    return v;
  });
}

function int(o: Obj, k: string, where: string, min = 0, max = Number.MAX_SAFE_INTEGER): number {
  const v = o[k];
  if (typeof v !== "number" || !Number.isInteger(v) || v < min || v > max) {
    throw new ResultsError(`${where}.${k}: expected an integer in [${min}, ${max}]`);
  }
  return v;
}

function bool(o: Obj, k: string, where: string): boolean {
  if (typeof o[k] !== "boolean") throw new ResultsError(`${where}.${k}: expected a boolean`);
  return o[k] as boolean;
}

function optStr(o: Obj, k: string, where: string): string | null {
  const v = o[k];
  if (v === null) return null;
  if (typeof v !== "string" || v.length === 0) throw new ResultsError(`${where}.${k}: expected a string or null`);
  return v;
}

function numArr(o: Obj, k: string, where: string, len?: number, lo = -Infinity, hi = Infinity): number[] {
  const a = arr(o, k, where);
  if (len !== undefined && a.length !== len) throw new ResultsError(`${where}.${k}: expected ${len} values`);
  return a.map((v, i) => {
    if (typeof v !== "number" || !Number.isFinite(v) || v < lo || v > hi) throw new ResultsError(`${where}.${k}[${i}]: out of range`);
    return v;
  });
}

const B64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
const MAX_FOOD = 24;

function armMean(v: unknown, where: string): ArmMean {
  const o = obj(v, where);
  const m: ArmMean = {
    experiment_id: str(o, "experiment_id", where), condition: str(o, "condition", where), arm: str(o, "arm", where),
    n: int(o, "n", where, 1), mean: num(o, "mean", where) as number, sd: num(o, "sd", where) as number,
    display: str(o, "display", where), sd_display: str(o, "sd_display", where), sd_source: str(o, "sd_source", where),
  };
  if (m.mean < 0 || m.mean > MAX_FOOD || m.sd < 0) throw new ResultsError(`${where}: mean or SD out of range`);
  return m;
}

function curveSet(v: unknown, where: string): CurveSet {
  const o = obj(v, where);
  const c: CurveSet = {
    experiment_id: str(o, "experiment_id", where), condition: str(o, "condition", where),
    budget: int(o, "budget", where, 1), population: int(o, "population", where, 1), generations: int(o, "generations", where, 1),
    train_episodes_per_eval: int(o, "train_episodes_per_eval", where, 1),
    arms: arr(o, "arms", where).map((x, i) => {
      const w = `${where}.arms[${i}]`;
      const a = obj(x, w);
      const evaluation = numArr(a, "evaluation", w, undefined, 1);
      const n = evaluation.length;
      if (n < 2) throw new ResultsError(`${w}.evaluation: too few points`);
      const q25 = numArr(a, "q25", w, n, 0, MAX_FOOD), median = numArr(a, "median", w, n, 0, MAX_FOOD), q75 = numArr(a, "q75", w, n, 0, MAX_FOOD);
      for (let j = 0; j < n; j++) {
        if (!(q25[j] <= median[j] && median[j] <= q75[j])) throw new ResultsError(`${w}: quartiles out of order at ${j}`);
        if (j > 0 && (evaluation[j] <= evaluation[j - 1] || median[j] < median[j - 1])) throw new ResultsError(`${w}: curve not monotone at ${j}`);
      }
      return { arm: str(a, "arm", w), n_seeds: int(a, "n_seeds", w, 1), evaluation, median, q25, q75 };
    }),
  };
  if (c.arms.length === 0) throw new ResultsError(`${where}.arms: empty`);
  if (c.population * c.generations !== c.budget) throw new ResultsError(`${where}: budget is not population x generations`);
  return c;
}

function replay(v: unknown, where: string): Replay {
  const o = obj(v, where);
  const p = int(o, "population", where, 1, B64.length), g = int(o, "generations", where, 1);
  const k = int(o, "train_episodes_per_eval", where, 1);
  const budget = int(o, "budget", where, 1);
  if (p * g !== budget) throw new ResultsError(`${where}: budget is not population x generations`);
  const arms = arr(o, "arms", where).map((x, i) => {
    const w = `${where}.arms[${i}]`;
    const a = obj(x, w);
    const runs = arr(a, "runs", w).map((y, j) => {
      const wr = `${w}.runs[${j}]`;
      const r = obj(y, wr);
      const hex = str(r, "fitness_hex", wr), par = str(r, "parents_b64", wr);
      if (hex.length !== 2 * budget || !/^[0-9a-f]+$/.test(hex)) throw new ResultsError(`${wr}.fitness_hex: malformed`);
      if (par.length !== budget) throw new ResultsError(`${wr}.parents_b64: malformed`);
      const fitness = new Float64Array(budget), parents = new Int16Array(budget);
      for (let e = 0; e < budget; e++) {
        const cnt = parseInt(hex.slice(2 * e, 2 * e + 2), 16);
        if (cnt > MAX_FOOD * k) throw new ResultsError(`${wr}: training fitness above the ceiling`);
        fitness[e] = cnt / k;
        const ch = par[e];
        const s = ch === "." ? -1 : B64.indexOf(ch);
        if ((ch !== "." && (s < 0 || s >= p)) || (e < p && s !== -1)) throw new ResultsError(`${wr}.parents_b64: bad slot at ${e}`);
        parents[e] = s;
      }
      const best = numArr(r, "best_per_generation", wr, g, 0, MAX_FOOD);
      const returned = int(r, "returned_index", wr, 0, budget - 1);
      let m = -Infinity;
      for (let e = 0; e < budget; e++) {
        m = Math.max(m, fitness[e]);
        if (e % p === p - 1 && Math.abs(best[(e + 1) / p - 1] - m) > 1e-6) throw new ResultsError(`${wr}: best-so-far disagrees with the trace`);
      }
      if (fitness[returned] !== m || fitness.indexOf(m) !== returned) throw new ResultsError(`${wr}: returned index is not the earliest best`);
      const fTest = num(r, "f_test", wr) as number;
      if (fTest < 0 || fTest > MAX_FOOD) throw new ResultsError(`${wr}.f_test: out of range`);
      return { seed: int(r, "seed", wr), run_id: str(r, "run_id", wr), returned_index: returned, f_test: fTest, best_per_generation: best, fitness, parents };
    });
    if (runs.length === 0) throw new ResultsError(`${w}.runs: empty`);
    return { arm: str(a, "arm", w), experiment_id: str(a, "experiment_id", w), runs };
  });
  if (arms.length === 0) throw new ResultsError(`${where}.arms: empty`);
  return { condition: str(o, "condition", where), budget, population: p, generations: g, train_episodes_per_eval: k, arms };
}

function estimate(v: unknown, where: string): Estimate {
  const o = obj(v, where);
  const e: Estimate = {
    label: str(o, "label", where),
    estimate: num(o, "estimate", where) as number,
    ci_low: num(o, "ci_low", where, true),
    ci_high: num(o, "ci_high", where, true),
    ci_level: num(o, "ci_level", where, true),
    unit: typeof o.unit === "string" ? o.unit : "",
    display: typeof o.display === "string" ? o.display : null,
    interval_display: typeof o.interval_display === "string" ? o.interval_display : null,
    n_pairs: int(o, "n_pairs", where, 1),
    dz_display: optStr(o, "dz_display", where),
    seeds_display: optStr(o, "seeds_display", where),
    reading: str(o, "reading", where),
    kind: o.kind as EstimateKind,
    headline: bool(o, "headline", where),
  };
  if (!(KINDS as readonly unknown[]).includes(o.kind)) throw new ResultsError(`${where}.kind: unknown kind`);
  // EVOLVE: every published estimate carries the manuscript's exact text and an interval.
  if (e.display === null || e.interval_display === null) throw new ResultsError(`${where}: display text missing`);
  if (e.ci_low === null || e.ci_level === null) throw new ResultsError(`${where}: interval missing`);
  if (e.estimate < e.ci_low! || e.estimate > e.ci_high!) throw new ResultsError(`${where}: estimate outside its interval`);
  if ((e.ci_low === null) !== (e.ci_high === null)) {
    throw new ResultsError(`${where}: interval must have both bounds or neither`);
  }
  if (e.ci_low !== null && e.ci_high !== null && e.ci_low > e.ci_high) {
    throw new ResultsError(`${where}: ci_low exceeds ci_high`);
  }
  return e;
}

export function validateResults(raw: unknown): Results {
  const o = obj(raw, "results");
  if (o.schema !== SCHEMA) throw new ResultsError(`results.schema: expected "${SCHEMA}"`);
  const version = str(o, "schema_version", "results");
  if (Number(version.split(".")[0]) !== SCHEMA_MAJOR) {
    throw new ResultsError(`results.schema_version: unsupported major version ${version}`);
  }
  const experiments = arr(o, "experiments", "results").map((v, i) => {
    const w = `experiments[${i}]`;
    const e = obj(v, w);
    return {
      id: str(e, "id", w),
      title: str(e, "title", w),
      status: str(e, "status", w),
      verdict: str(e, "verdict", w),
      estimates: arr(e, "estimates", w).map((x, j) => estimate(x, `${w}.estimates[${j}]`)),
      claim_ids: strArr(e, "claim_ids", w),
      report_path: str(e, "report_path", w),
      notes: strArr(e, "notes", w),
    };
  });
  if (experiments.length === 0) throw new ResultsError("results.experiments: empty");
  return {
    schema: SCHEMA,
    schema_version: version,
    project: str(o, "project", "results"),
    question: str(o, "question", "results"),
    status_label: str(o, "status_label", "results"),
    code_revision: (() => {
      const rev = str(o, "code_revision", "results");
      if (!/^[0-9a-f]{40}$/.test(rev)) throw new ResultsError("results.code_revision: not a full git revision");
      return rev;
    })(),
    sources: arr(o, "sources", "results").map((v, i) => {
      const s = obj(v, `sources[${i}]`);
      const sha = str(s, "sha256", `sources[${i}]`);
      if (!/^[0-9a-f]{64}$/.test(sha)) throw new ResultsError(`sources[${i}].sha256: not a sha256`);
      return { path: str(s, "path", `sources[${i}]`), sha256: sha };
    }),
    experiments,
    assumptions: arr(o, "assumptions", "results").map((v, i) => {
      const a = obj(v, `assumptions[${i}]`);
      return {
        name: str(a, "name", `assumptions[${i}]`),
        value: str(a, "value", `assumptions[${i}]`),
        source: str(a, "source", `assumptions[${i}]`),
      };
    }),
    limitations: strArr(o, "limitations", "results"),
    arm_means: arr(o, "arm_means", "results").map((v, i) => armMean(v, `arm_means[${i}]`)),
    curves: (() => {
      const c = obj(o.curves, "curves");
      const items = arr(c, "items", "curves").map((v, i) => curveSet(v, `curves.items[${i}]`));
      if (items.length === 0) throw new ResultsError("curves.items: empty");
      return { metric: str(c, "metric", "curves"), summary: str(c, "summary", "curves"), items };
    })(),
    replay: replay(o.replay, "replay"),
  };
}

export async function loadResults(url = "./data/results.json"): Promise<Results> {
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) throw new ResultsError(`could not load ${url} (HTTP ${res.status})`);
  let raw: unknown;
  try {
    raw = await res.json();
  } catch {
    throw new ResultsError(`${url} is not valid JSON`);
  }
  return validateResults(raw);
}

/** Formats a number for display without inventing precision. */
export function fmt(x: number, digits = 3): string {
  if (Number.isInteger(x)) return x.toString();
  return Number(x.toPrecision(digits)).toString();
}

export function fmtEstimate(e: Estimate, digits = 3): string {
  return e.display ?? `${fmt(e.estimate, digits)}${e.unit ? " " + e.unit : ""}`;
}

export function fmtInterval(e: Estimate, digits = 3): string {
  if (e.interval_display !== null) return e.interval_display;
  if (e.ci_low === null || e.ci_high === null) return "no interval";
  const level = e.ci_level === null ? "" : `${Math.round(e.ci_level * 100)}% `;
  return `${level}[${fmt(e.ci_low, digits)}, ${fmt(e.ci_high, digits)}]`;
}
