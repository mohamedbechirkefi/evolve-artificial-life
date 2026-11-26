// SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0
// Hero illustration: three culture plates of an invented run (generations 0,
// 9 and 39) slide into a stack, then their colonies appear. Scattered founders
// on the first plate become a few dominant lineages on the last. It is drawn
// from a fixed pseudo-random sequence, not from any study data, and it shows
// no number. Motion is CSS only (transform and opacity); reduced motion shows
// the final frame.
import { useMemo } from "react";

const N = 16; // the foraging grid is 16 x 16

function rng(seed: number) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const STAINS = ["var(--violet)", "var(--methylene)", "var(--safranin)", "var(--malachite)", "var(--bismarck)", "var(--ink)"];

type Cell = { i: number; lineage: number };

/** Grow `lineages` colonies to `cells` cells in total by a seeded random walk. */
function plate(seed: number, lineages: number, cells: number, weights: number[]): Cell[] {
  const r = rng(seed);
  const taken = new Map<number, number>();
  const fronts: number[][] = [];
  for (let l = 0; l < lineages; l++) {
    let i = Math.floor(r() * N * N);
    while (taken.has(i)) i = Math.floor(r() * N * N);
    taken.set(i, l);
    fronts.push([i]);
  }
  const total = weights.reduce((a, b) => a + b, 0);
  let guard = 0;
  while (taken.size < cells && guard++ < 20000) {
    let pick = r() * total, l = 0;
    while (pick > weights[l]) { pick -= weights[l]; l++; }
    const f = fronts[l];
    const from = f[Math.floor(r() * f.length)];
    const dir = Math.floor(r() * 4);
    const row = Math.floor(from / N) + (dir === 0 ? -1 : dir === 1 ? 1 : 0);
    const col = (from % N) + (dir === 2 ? -1 : dir === 3 ? 1 : 0);
    if (row < 0 || row >= N || col < 0 || col >= N) continue;
    const j = row * N + col;
    if (taken.has(j)) continue;
    taken.set(j, l);
    f.push(j);
  }
  // Appearance order: by lineage, then by distance from its founder.
  return [...taken.entries()].map(([i, lineage]) => ({ i, lineage })).sort((a, b) => a.lineage - b.lineage);
}

const PLATES = [
  { gen: 0, cx: 168, cy: 150, cells: () => plate(11, 34, 34, Array(34).fill(1)) },
  { gen: 9, cx: 262, cy: 232, cells: () => plate(23, 6, 46, [5, 3, 3, 2, 1, 1]) },
  { gen: 39, cx: 356, cy: 314, cells: () => plate(37, 2, 58, [9, 1]) },
];
const R = 136;
const SIDE = 176; // the grid square inside the plate
const CELL = SIDE / N;

export function PlateStack() {
  const plates = useMemo(() => PLATES.map((p) => ({ ...p, list: p.cells() })), []);
  return (
    <figure className="hero-figure">
      <svg viewBox="0 0 520 470" className="plates" role="img"
        aria-label="Illustration, not study data: three culture plates of an invented run. Generation 0 holds many scattered founders; by generation 39 a few lineages fill the plate.">
        {plates.map((p, k) => {
          const gx = p.cx - SIDE / 2, gy = p.cy - SIDE / 2;
          const colonyDelay = 900 + k * 260;
          return (
            <g key={p.gen} className="plate" style={{ animationDelay: `${k * 160}ms` }}>
              <ellipse cx={p.cx + 6} cy={p.cy + 12} rx={R} ry={R - 4} className="plate-shadow" />
              <circle cx={p.cx} cy={p.cy} r={R} className="plate-agar" />
              <circle cx={p.cx} cy={p.cy} r={R - 9} className="plate-lid" />
              {Array.from({ length: N + 1 }, (_, i) => (
                <g key={i} className="plate-grid">
                  <line x1={gx + i * CELL} x2={gx + i * CELL} y1={gy} y2={gy + SIDE} />
                  <line y1={gy + i * CELL} y2={gy + i * CELL} x1={gx} x2={gx + SIDE} />
                </g>
              ))}
              {p.list.map((c, n) => (
                <rect key={c.i} x={gx + (c.i % N) * CELL + 0.8} y={gy + Math.floor(c.i / N) * CELL + 0.8} width={CELL - 1.6} height={CELL - 1.6} rx={2}
                  className="colony" style={{ fill: STAINS[p.gen === 0 ? c.lineage % STAINS.length : c.lineage], animationDelay: `${colonyDelay + Math.min(n, 40) * 18}ms` }} />
              ))}
              <text x={p.cx - 60} y={p.cy - 94} className="plate-label">gen. {p.gen}</text>
            </g>
          );
        })}
      </svg>
      <figcaption>Illustration, not study data. An invented run drawn to show what selection does to lineages; the measured runs are in the replay below.</figcaption>
    </figure>
  );
}
