// SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0
// The sandbox port against a fixture from the Python engine
// (scripts/export_sandbox_fixture.py). Tolerance: zero. Every action of every
// episode and every score must be identical.
import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { evaluate, layoutFromCells, N_PARAMS, search, simulate, type SearchSettings } from "./engine";

interface Fixture {
  grid_size: number;
  steps: number;
  hidden_units: number;
  layouts: { food: number[]; heading: number }[];
  thetas: number[][];
  episodes: { layout: number; policy: number; eaten: number; n_stay: number; n_turn: number; actions: string }[];
}
const fx: Fixture = JSON.parse(readFileSync("src/engine.fixture.json", "utf8"));

describe("port of the Python environment and policy (fixture, tolerance zero)", () => {
  it("has the research dimensions", () => {
    expect(fx.grid_size).toBe(16);
    expect(fx.hidden_units).toBe(8);
    expect(fx.thetas[0].length).toBe(N_PARAMS);
    expect(fx.episodes.length).toBe(24);
    expect(fx.episodes.some((e) => e.eaten >= 5)).toBe(true);
  });
  it("reproduces every action sequence and score exactly", () => {
    let mismatched = 0;
    for (const ep of fx.episodes) {
      const lay = fx.layouts[ep.layout];
      const out = simulate(fx.thetas[ep.policy], layoutFromCells(lay.food, lay.heading), fx.steps, true);
      const actions = Array.from(out.actions!).join("");
      if (actions !== ep.actions || out.eaten !== ep.eaten || out.nStay !== ep.n_stay || out.nTurn !== ep.n_turn) mismatched++;
    }
    expect(mismatched).toBe(0);
  });
});

const small: SearchSettings = { seed: 3, population: 10, generations: 5, sigma: 0.1, k: 2, fixed: false, nParents: 2, elitism: 1, nTest: 5 };

describe("sandbox search operators", () => {
  it("spends exactly the budget and returns the earliest best evaluation", () => {
    for (const arm of ["RS", "NOSEL", "EVO"] as const) {
      const t = search(arm, small)!;
      expect(t.fitness.length).toBe(50);
      const max = Math.max(...t.fitness);
      expect(t.returned).toBe(t.fitness.indexOf(max));
    }
  });
  it("uses matched starts: generation 0 of EVO equals the first P RS draws", () => {
    const rs = search("RS", small)!, evo = search("EVO", small)!;
    expect(Array.from(evo.fitness.slice(0, 10))).toEqual(Array.from(rs.fitness.slice(0, 10)));
  });
  it("EVO parents come from the top of the previous generation; RS has no parents", () => {
    const t = search("EVO", small)!;
    for (let g = 1; g < 5; g++) {
      const prev = Array.from(t.fitness.slice((g - 1) * 10, g * 10));
      const cutoff = [...prev].sort((a, b) => b - a)[small.nParents - 1];
      for (let i = 0; i < 10; i++) {
        const par = t.parent[g * 10 + i];
        expect(par).toBeGreaterThanOrEqual((g - 1) * 10);
        expect(par).toBeLessThan(g * 10);
        expect(t.fitness[par]).toBeGreaterThanOrEqual(cutoff);
      }
    }
    expect(Array.from(search("RS", small)!.parent).every((x) => x === -1)).toBe(true);
  });
  it("is deterministic for a seed and stops when cancelled", () => {
    expect(Array.from(search("NOSEL", small)!.fitness)).toEqual(Array.from(search("NOSEL", small)!.fitness));
    expect(search("EVO", small, () => false)).toBeNull();
  });
  it("training fitness stays within [0, 24]", () => {
    const t = search("EVO", { ...small, sigma: 0.5 })!;
    expect(Math.min(...t.fitness)).toBeGreaterThanOrEqual(0);
    expect(Math.max(...t.fitness)).toBeLessThanOrEqual(24);
    expect(evaluate(t.thetas[0], [layoutFromCells([], 0)])).toBe(0);
  });
});
