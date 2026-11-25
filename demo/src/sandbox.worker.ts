// SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0
// Bounded, cancellable sandbox: runs RS, NOSEL and EVO with matched starts on
// the reduced engine port (engine.ts). Output is sandbox output, never a
// research result.
import { search, simulate, testLayouts, type ArmName, type SearchSettings } from "./engine";

export interface SandboxSettings {
  seed: number;
  budget: 500 | 2000;
  sigma: number;
  k: 1 | 5;
}

export interface SandboxArm {
  arm: ArmName;
  fitness: number[];
  parent: number[];
  returned: number;
  testMean: number;
  testScores: number[];
  theta: number[];
}

export type WorkerRequest = { type: "run"; settings: SandboxSettings } | { type: "cancel" };
export type WorkerReply =
  | { type: "progress"; fraction: number; arm: ArmName }
  | { type: "done"; settings: SandboxSettings; population: number; generations: number; nTest: number; arms: SandboxArm[] }
  | { type: "cancelled" }
  | { type: "error"; message: string };

const N_TEST = 50;
const ARMS: ArmName[] = ["RS", "NOSEL", "EVO"];
let cancelled = false;

export function validSettings(s: SandboxSettings): boolean {
  return Number.isInteger(s.seed) && s.seed >= 1 && s.seed <= 1_000_000 && (s.budget === 500 || s.budget === 2000)
    && [0.02, 0.1, 0.5].includes(s.sigma) && (s.k === 1 || s.k === 5);
}

async function run(s: SandboxSettings): Promise<WorkerReply> {
  if (!validSettings(s)) return { type: "error", message: "settings out of range" };
  const population = s.budget === 500 ? 25 : 50;
  const generations = s.budget / population;
  const cfg: SearchSettings = {
    seed: s.seed, population, generations, sigma: s.sigma, k: s.k, fixed: s.k === 1,
    nParents: Math.round(population * 0.2), elitism: 1, nTest: N_TEST,
  };
  const tests = testLayouts(s.seed, N_TEST);
  const out: SandboxArm[] = [];
  for (let ai = 0; ai < ARMS.length; ai++) {
    const arm = ARMS[ai];
    let last = 0;
    const trace = search(arm, cfg, (done, total) => {
      if (cancelled) return false;
      if (done - last >= population * 4 || done === total) {
        last = done;
        postMessage({ type: "progress", fraction: (ai + done / total) / ARMS.length, arm } satisfies WorkerReply);
      }
      return true;
    });
    await new Promise((r) => setTimeout(r, 0)); // let a cancel message in between arms
    if (trace === null || cancelled) return { type: "cancelled" };
    const theta = trace.thetas[0];
    const testScores = tests.map((lay) => simulate(theta, lay).eaten);
    out.push({
      arm, fitness: Array.from(trace.fitness), parent: Array.from(trace.parent), returned: trace.returned,
      testMean: testScores.reduce((a, b) => a + b, 0) / N_TEST, testScores, theta: Array.from(theta),
    });
  }
  return { type: "done", settings: s, population, generations, nTest: N_TEST, arms: out };
}

onmessage = async (ev: MessageEvent<WorkerRequest>) => {
  const m = ev.data;
  if (m.type === "cancel") {
    cancelled = true;
    return;
  }
  cancelled = false;
  try {
    postMessage((await run(m.settings)) satisfies WorkerReply);
  } catch (e) {
    postMessage({ type: "error", message: e instanceof Error ? e.message : String(e) } satisfies WorkerReply);
  }
};
