// SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0
// Reduced TypeScript port of the EVOLVE engine for the visitor sandbox.
//
// Exact port (checked against a fixture from the Python engine in
// engine.test.ts, tolerance zero): the toroidal grid, the 5 x 5 egocentric
// observation, the 25-8-4 tanh policy with argmax (ties to the lowest action),
// the action rules and the consumed-food count (src/evolve/env.py, policy.py).
//
// Not an exact port: random numbers. The research engine uses NumPy PCG64
// streams from SeedSequence spawn keys; this port uses mulberry32 with a
// Box-Muller normal, so a sandbox seed never reproduces a research run, and
// the clustered layout generator only follows the same recipe. The search
// operators (src/evolve/search.py) follow the same rules at a smaller scale.

export const GRID = 16;
export const N_FOOD = 24;
export const N_CLUSTERS = 3;
export const CLUSTER_SPREAD = 2.0;
export const STEPS = 100;
export const HIDDEN = 8;
export const N_INPUTS = 25;
export const N_ACTIONS = 4;
export const N_PARAMS = N_INPUTS * HIDDEN + HIDDEN * N_ACTIONS + N_ACTIONS; // 236

export const FORWARD = 0;
export const LEFT = 1;
export const RIGHT = 2;
export const STAY = 3;
const DELTAS: ReadonlyArray<readonly [number, number]> = [[-1, 0], [0, 1], [1, 0], [0, -1]];

// Window cells ordered by forward distance f = 2..-2, then rightward offset r = -2..2, own cell excluded.
const WINDOW: Array<[number, number]> = [];
for (const f of [2, 1, 0, -1, -2]) for (const r of [-2, -1, 0, 1, 2]) if (f !== 0 || r !== 0) WINDOW.push([f, r]);

/** OFFSETS[h][i] = [drow, dcol] of window cell i for heading h. */
const OFFSETS: Array<Array<[number, number]>> = [0, 1, 2, 3].map((h) => {
  const fwd = DELTAS[h], right = DELTAS[(h + 1) % 4];
  return WINDOW.map(([f, r]) => [f * fwd[0] + r * right[0], f * fwd[1] + r * right[1]] as [number, number]);
});

const mod = (a: number, n: number) => ((a % n) + n) % n;

export interface Rng {
  uniform(): number;
  normal(): number;
  int(n: number): number;
}

export function makeRng(seed: number): Rng {
  let a = seed >>> 0;
  let spare: number | null = null;
  const uniform = () => {
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
  return {
    uniform,
    normal() {
      if (spare !== null) { const s = spare; spare = null; return s; }
      let u = 0;
      while (u === 0) u = uniform();
      const v = uniform();
      const m = Math.sqrt(-2 * Math.log(u));
      spare = m * Math.sin(2 * Math.PI * v);
      return m * Math.cos(2 * Math.PI * v);
    },
    int(n: number) { return Math.min(n - 1, Math.floor(uniform() * n)); },
  };
}

/** Independent stream for (seed, stream id, index), derived by integer hashing. */
export function streamSeed(seed: number, stream: number, index = 0): number {
  let h = Math.imul(seed ^ 0x9e3779b9, 0x85ebca6b) ^ Math.imul(stream + 1, 0xc2b2ae35) ^ Math.imul(index + 7, 0x27d4eb2f);
  h ^= h >>> 16; h = Math.imul(h, 0x7feb352d); h ^= h >>> 15; h = Math.imul(h, 0x846ca68b); h ^= h >>> 16;
  return h >>> 0;
}

export interface Layout {
  food: Uint8Array; // GRID * GRID, row-major
  heading: number;
}

export function layoutFromCells(cells: number[], heading: number): Layout {
  const food = new Uint8Array(GRID * GRID);
  for (const c of cells) food[c] = 1;
  return { food, heading };
}

/** Clustered layout, same recipe as generate_layout (different random stream). */
export function generateLayout(rng: Rng): Layout {
  const food = new Uint8Array(GRID * GRID);
  const start = (GRID >> 1) * GRID + (GRID >> 1);
  const centres = Array.from({ length: N_CLUSTERS }, () => [rng.int(GRID), rng.int(GRID)]);
  let placed = 0, attempts = 0;
  while (placed < N_FOOD) {
    if (++attempts > 100_000) throw new Error("clustered placement did not converge");
    const c = centres[rng.int(N_CLUSTERS)];
    const r = mod(c[0] + Math.round(rng.normal() * CLUSTER_SPREAD), GRID);
    const col = mod(c[1] + Math.round(rng.normal() * CLUSTER_SPREAD), GRID);
    const idx = r * GRID + col;
    if (idx === start || food[idx]) continue;
    food[idx] = 1;
    placed++;
  }
  return { food, heading: rng.int(4) };
}

/** One forward pass: obs (24 values in {0,1}) to an action, argmax with ties to the lowest index. */
export function act(theta: ArrayLike<number>, obs: ArrayLike<number>, hid: Float64Array = new Float64Array(HIDDEN)): number {
  for (let j = 0; j < HIDDEN; j++) {
    let s = 0;
    for (let i = 0; i < N_INPUTS - 1; i++) s += obs[i] * theta[i * HIDDEN + j];
    s += theta[(N_INPUTS - 1) * HIDDEN + j];
    hid[j] = Math.tanh(s);
  }
  const base = N_INPUTS * HIDDEN;
  let best = 0, bestV = -Infinity;
  for (let a = 0; a < N_ACTIONS; a++) {
    let v = 0;
    for (let j = 0; j < HIDDEN; j++) v += hid[j] * theta[base + j * N_ACTIONS + a];
    v += theta[base + HIDDEN * N_ACTIONS + a];
    if (v > bestV) { bestV = v; best = a; }
  }
  return best;
}

export interface Episode {
  eaten: number;
  nStay: number;
  nTurn: number;
  actions?: Uint8Array;
  /** Per step t (0..T): row, col, heading after t steps; recorded when requested. */
  path?: Int16Array;
  /** Step at which each eaten cell was consumed (cell index -> step), when recorded. */
  eatenAt?: Map<number, number>;
}

export function simulate(theta: ArrayLike<number>, layout: Layout, steps = STEPS, record = false): Episode {
  const food = layout.food.slice();
  const initial = food.reduce((s, v) => s + v, 0);
  let r = GRID >> 1, c = GRID >> 1, h = layout.heading;
  if (food[r * GRID + c]) throw new Error("start cell holds food");
  const obs = new Float64Array(N_INPUTS - 1);
  const hid = new Float64Array(HIDDEN);
  let eaten = 0, nStay = 0, nTurn = 0;
  const actions = record ? new Uint8Array(steps) : undefined;
  const path = record ? new Int16Array((steps + 1) * 3) : undefined;
  const eatenAt = record ? new Map<number, number>() : undefined;
  if (path) { path[0] = r; path[1] = c; path[2] = h; }
  for (let t = 0; t < steps; t++) {
    const off = OFFSETS[h];
    for (let i = 0; i < off.length; i++) obs[i] = food[mod(r + off[i][0], GRID) * GRID + mod(c + off[i][1], GRID)];
    const a = act(theta, obs, hid);
    if (actions) actions[t] = a;
    if (a === LEFT) { h = mod(h - 1, 4); nTurn++; }
    else if (a === RIGHT) { h = mod(h + 1, 4); nTurn++; }
    else if (a === STAY) nStay++;
    else {
      r = mod(r + DELTAS[h][0], GRID); c = mod(c + DELTAS[h][1], GRID);
      const idx = r * GRID + c;
      if (food[idx]) { food[idx] = 0; eaten++; eatenAt?.set(idx, t + 1); }
    }
    if (path) { path[(t + 1) * 3] = r; path[(t + 1) * 3 + 1] = c; path[(t + 1) * 3 + 2] = h; }
  }
  const remaining = food.reduce((s, v) => s + v, 0);
  if (initial - remaining !== eaten) throw new Error("replay check failed");
  return { eaten, nStay, nTurn, actions, path, eatenAt };
}

// ------------------------------------------------------------------ search

export type ArmName = "RS" | "NOSEL" | "EVO";

export interface SearchSettings {
  seed: number;
  population: number;
  generations: number;
  sigma: number;
  k: number; // training episodes per evaluation
  fixed: boolean; // one fixed training environment (K = 1 design)
  nParents: number;
  elitism: number;
  nTest: number;
}

export interface SearchTrace {
  arm: ArmName;
  fitness: Float64Array; // training fitness per evaluation (mean over K episodes)
  parent: Int32Array; // evaluation id of the parent, -1 if none
  returned: number;
  thetas: Float64Array[]; // only the returned policy is kept: thetas[0]
}

export interface Progress { (done: number, total: number): boolean | void }

/** Builds the training-environment provider for one seed: evaluation i uses environments i*K..i*K+K-1, or environment 0 when fixed. */
function trainEnvs(s: SearchSettings) {
  const cache = new Map<number, Layout>();
  const get = (j: number) => {
    let lay = cache.get(j);
    if (!lay) { lay = generateLayout(makeRng(streamSeed(s.seed, 3, j))); cache.set(j, lay); }
    return lay;
  };
  return (evalId: number): Layout[] => (s.fixed ? [get(0)] : Array.from({ length: s.k }, (_, q) => get(evalId * s.k + q)));
}

export function evaluate(theta: ArrayLike<number>, layouts: Layout[]): number {
  let total = 0;
  for (const lay of layouts) total += simulate(theta, lay).eaten;
  return total / layouts.length;
}

function sampleInitial(rng: Rng): Float64Array {
  const t = new Float64Array(N_PARAMS);
  for (let i = 0; i < N_PARAMS; i++) t[i] = rng.normal();
  return t;
}

/** Runs one arm. Generation 0 of population arms equals the first P RS draws (matched starts); mutation noise is always drawn. */
export function search(arm: ArmName, s: SearchSettings, progress?: Progress): SearchTrace | null {
  const p = s.population, e = p * s.generations;
  const env = trainEnvs(s);
  const init = makeRng(streamSeed(s.seed, 1));
  const parentRng = makeRng(streamSeed(s.seed, 2, 0));
  const noise = makeRng(streamSeed(s.seed, 2, 1));
  const fitness = new Float64Array(e);
  const parent = new Int32Array(e).fill(-1);
  let bestTheta: Float64Array | null = null, bestFit = -Infinity, returned = -1;
  const note = (id: number, theta: Float64Array, f: number) => {
    fitness[id] = f;
    if (f > bestFit) { bestFit = f; returned = id; bestTheta = theta; }
  };
  if (arm === "RS") {
    for (let id = 0; id < e; id++) {
      const th = sampleInitial(init);
      note(id, th, evaluate(th, env(id)));
      if (id % p === p - 1 && progress && progress(id + 1, e) === false) return null;
    }
  } else {
    let current: Float64Array[] = [];
    for (let id = 0; id < p; id++) {
      const th = sampleInitial(init);
      current.push(th);
      note(id, th, evaluate(th, env(id)));
    }
    for (let g = 1; g < s.generations; g++) {
      if (progress && progress(g * p, e) === false) return null;
      const prevIds = Array.from({ length: p }, (_, i) => (g - 1) * p + i);
      const order = prevIds.map((_, i) => i).sort((x, y) => fitness[prevIds[y]] - fitness[prevIds[x]] || x - y);
      let pool: number[], copied: number[];
      if (arm === "EVO") {
        pool = order.slice(0, s.nParents);
        copied = order.slice(0, s.elitism);
      } else {
        pool = order.map((_, i) => i);
        const shuffled = pool.slice();
        for (let i = shuffled.length - 1; i > 0; i--) { const j = parentRng.int(i + 1); [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]]; }
        copied = shuffled.slice(0, s.elitism);
      }
      const next: Float64Array[] = [];
      for (let i = 0; i < s.elitism; i++) {
        const id = g * p + i;
        parent[id] = (g - 1) * p + copied[i];
        next.push(current[copied[i]]);
      }
      for (let i = s.elitism; i < p; i++) {
        const slot = pool[parentRng.int(pool.length)];
        const th = new Float64Array(N_PARAMS);
        const src = current[slot];
        for (let q = 0; q < N_PARAMS; q++) th[q] = src[q] + s.sigma * noise.normal();
        parent[g * p + i] = (g - 1) * p + slot;
        next.push(th);
      }
      for (let i = 0; i < p; i++) note(g * p + i, next[i], evaluate(next[i], env(g * p + i)));
      current = next;
    }
  }
  progress?.(e, e);
  return { arm, fitness, parent, returned, thetas: [bestTheta as unknown as Float64Array] };
}

/** Sandbox held-out layouts: a stream that no training environment uses. */
export function testLayouts(seed: number, n: number): Layout[] {
  return Array.from({ length: n }, (_, j) => generateLayout(makeRng(streamSeed(seed, 4, j))));
}
