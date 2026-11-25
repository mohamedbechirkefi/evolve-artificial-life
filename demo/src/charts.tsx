// SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0
// Hand-written SVG charts: interval strips, fitness curves, ancestry and the
// organism grid. No chart library. Text inside SVG uses currentColor so it
// carries the page's text tokens.
import { useMemo, useState, type PointerEvent } from "react";
import type { Estimate, EstimateKind } from "./results";

export const ARM_STYLE: Record<string, { color: string; dash?: string; label: string }> = {
  RS: { color: "var(--c-rs)", label: "RS (random search)" },
  NOSEL: { color: "var(--c-nosel)", dash: "6 3", label: "NOSEL (no selection)" },
  EVO: { color: "var(--c-evo)", label: "EVO, sigma 0.1 (frozen)" },
  SELONLY: { color: "var(--c-s0)", dash: "2 3", label: "SELONLY (sigma 0)" },
  "EVO-sigma0.02": { color: "var(--c-s002)", dash: "6 3", label: "EVO, sigma 0.02" },
  "EVO-sigma0.5": { color: "var(--c-s05)", dash: "10 3 2 3", label: "EVO, sigma 0.5" },
};

export const KIND_LABEL: Record<EstimateKind, string> = {
  supported: "supported / above 0",
  contradicting: "contradicting result",
  inconclusive: "inconclusive",
  "as-predeclared": "as predeclared",
  estimate: "estimate",
  descriptive: "descriptive",
  exploratory: "exploratory",
};

// ------------------------------------------------------------ interval strip

export function domainOf(ests: Estimate[]): [number, number] {
  let lo = 0, hi = 0;
  for (const e of ests) { lo = Math.min(lo, e.ci_low ?? e.estimate); hi = Math.max(hi, e.ci_high ?? e.estimate); }
  const pad = (hi - lo) * 0.04;
  return [Math.floor(lo - pad), Math.ceil(hi + pad)];
}

/** One estimate on a shared axis: interval bar, point, zero line. The same mark weight for every kind. */
export function IntervalStrip({ e, domain }: { e: Estimate; domain: [number, number] }) {
  const pct = (x: number) => `${(((x - domain[0]) / (domain[1] - domain[0])) * 100).toFixed(3)}%`;
  const hollow = e.kind === "inconclusive" || e.kind === "exploratory";
  return (
    <svg className={`strip kind-${e.kind}`} height="26" width="100%" aria-hidden="true" focusable="false">
      <line x1={pct(0)} x2={pct(0)} y1="2" y2="24" className="zero" />
      {e.ci_low !== null && e.ci_high !== null && <line x1={pct(e.ci_low)} x2={pct(e.ci_high)} y1="13" y2="13" className="ci" />}
      {e.ci_low !== null && <line x1={pct(e.ci_low)} x2={pct(e.ci_low)} y1="7" y2="19" className="ci" />}
      {e.ci_high !== null && <line x1={pct(e.ci_high)} x2={pct(e.ci_high)} y1="7" y2="19" className="ci" />}
      <circle cx={pct(e.estimate)} cy="13" r="5.5" className={hollow ? "pt hollow" : "pt"} />
    </svg>
  );
}

export function AxisStrip({ domain }: { domain: [number, number] }) {
  const ticks: number[] = [];
  const step = domain[1] - domain[0] > 12 ? 4 : 2;
  for (let t = Math.ceil(domain[0] / step) * step; t <= domain[1]; t += step) ticks.push(t);
  const pct = (x: number) => `${(((x - domain[0]) / (domain[1] - domain[0])) * 100).toFixed(3)}%`;
  return (
    <svg className="strip axis" height="22" width="100%" aria-hidden="true" focusable="false">
      {ticks.map((t) => (
        <g key={t}>
          <line x1={pct(t)} x2={pct(t)} y1="0" y2="5" className="tick" />
          <text x={pct(t)} y="17" textAnchor="middle">{t}</text>
        </g>
      ))}
    </svg>
  );
}

// ------------------------------------------------------------ fitness curves

export interface CurveSeries {
  arm: string;
  x: number[];
  median: number[];
  q25?: number[];
  q75?: number[];
}

const W = 640, H = 340, M = { l: 68, r: 30, t: 14, b: 58 };

export function CurvesChart(props: {
  title: string;
  series: CurveSeries[];
  budget: number;
  cursor?: number; // evaluation index
  extra?: { arm: string; x: number[]; y: number[]; label: string }[];
  yLabel?: string;
}) {
  const { series, budget, cursor, extra = [] } = props;
  const [hover, setHover] = useState<number | null>(null);
  const yMax = 24;
  const sx = (x: number) => M.l + (x / budget) * (W - M.l - M.r);
  const sy = (y: number) => H - M.b - (y / yMax) * (H - M.t - M.b);
  const path = (xs: number[], ys: number[]) => xs.map((x, i) => `${i ? "L" : "M"}${sx(x).toFixed(1)},${sy(ys[i]).toFixed(1)}`).join("");
  const band = (s: CurveSeries) =>
    s.q25 && s.q75 ? path(s.x, s.q75) + s.x.slice().reverse().map((x, i) => `L${sx(x).toFixed(1)},${sy(s.q25![s.x.length - 1 - i]).toFixed(1)}`).join("") + "Z" : "";
  const xTicks = [0, budget / 4, budget / 2, (3 * budget) / 4, budget];
  const onMove = (ev: PointerEvent<SVGSVGElement>) => {
    const r = ev.currentTarget.getBoundingClientRect();
    const x = ((ev.clientX - r.left) / r.width) * W;
    const ev0 = Math.max(0, Math.min(budget, ((x - M.l) / (W - M.l - M.r)) * budget));
    setHover(ev0);
  };
  const at = (xs: number[], ys: number[], x: number) => {
    let best = 0;
    for (let i = 0; i < xs.length; i++) if (Math.abs(xs[i] - x) < Math.abs(xs[best] - x)) best = i;
    return { x: xs[best], y: ys[best] };
  };
  return (
    <figure className="chart">
      <div className="chart-box">
        <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label={props.title} onPointerMove={onMove} onPointerLeave={() => setHover(null)}>
          {[0, 6, 12, 18, 24].map((t) => (
            <g key={t}>
              <line x1={M.l} x2={W - M.r} y1={sy(t)} y2={sy(t)} className="grid" />
              <text x={M.l - 8} y={sy(t) + 6} textAnchor="end">{t}</text>
            </g>
          ))}
          {xTicks.map((t) => (
            <text key={t} x={sx(t)} y={H - M.b + 26} textAnchor="middle">{t.toLocaleString("en-US")}</text>
          ))}
          <text x={(M.l + W - M.r) / 2} y={H - 4} textAnchor="middle" className="axis-label">evaluations used</text>
          <text x={26} y={(M.t + H - M.b) / 2} textAnchor="middle" className="axis-label" transform={`rotate(-90 26 ${(M.t + H - M.b) / 2})`}>
            {props.yLabel ?? "best-so-far training fitness"}
          </text>
          {series.map((s) => s.q25 && <path key={s.arm + "b"} d={band(s)} className="band" style={{ fill: ARM_STYLE[s.arm]?.color }} />)}
          {series.map((s) => (
            <path key={s.arm} d={path(s.x, s.median)} className="line" style={{ stroke: ARM_STYLE[s.arm]?.color, strokeDasharray: ARM_STYLE[s.arm]?.dash }} />
          ))}
          {extra.map((s) => (
            <path key={"x" + s.arm} d={path(s.x, s.y)} className="line seed" style={{ stroke: ARM_STYLE[s.arm]?.color }} />
          ))}
          {cursor !== undefined && <line x1={sx(cursor)} x2={sx(cursor)} y1={M.t} y2={H - M.b} className="cursor" />}
          {hover !== null && <line x1={sx(hover)} x2={sx(hover)} y1={M.t} y2={H - M.b} className="crosshair" />}
          <rect x={M.l} y={M.t} width={W - M.l - M.r} height={H - M.t - M.b} fill="transparent" />
        </svg>
        {hover !== null && (
          <div className="tooltip" style={{ left: `${(sx(hover) / W) * 100}%` }}>
            <strong>{Math.round(hover).toLocaleString("en-US")} evaluations</strong>
            {series.map((s) => (
              <span key={s.arm}><i className="sw" style={{ background: ARM_STYLE[s.arm]?.color }} />{s.arm}: {at(s.x, s.median, hover).y.toFixed(1)}</span>
            ))}
            {extra.map((s) => (
              <span key={"x" + s.arm}><i className="sw" style={{ background: ARM_STYLE[s.arm]?.color }} />{s.label}: {at(s.x, s.y, hover).y.toFixed(1)}</span>
            ))}
          </div>
        )}
      </div>
      <figcaption>
        <ul className="legend">
          {series.map((s) => (
            <li key={s.arm}>
              <svg width="28" height="10" aria-hidden="true" focusable="false"><line x1="0" x2="28" y1="5" y2="5" className="line" style={{ stroke: ARM_STYLE[s.arm]?.color, strokeDasharray: ARM_STYLE[s.arm]?.dash }} /></svg>
              {ARM_STYLE[s.arm]?.label ?? s.arm}
            </li>
          ))}
          {extra.map((s) => (
            <li key={"x" + s.arm}>
              <svg width="28" height="10" aria-hidden="true" focusable="false"><line x1="0" x2="28" y1="5" y2="5" className="line seed" style={{ stroke: ARM_STYLE[s.arm]?.color }} /></svg>
              {s.label}
            </li>
          ))}
        </ul>
      </figcaption>
    </figure>
  );
}

// ------------------------------------------------------------ ancestry

export function AncestryChart(props: {
  title: string;
  arm: string;
  fitness: ArrayLike<number>;
  parents: ArrayLike<number>; // slot in the previous generation, -1 if none
  population: number;
  generations: number;
  upto: number; // last generation shown (0-based)
}) {
  const { fitness, parents, population: p, generations: g, upto } = props;
  const AW = 640, AH = 260, ml = 8, mr = 8, mt = 8, mb = 30;
  const geo = useMemo(() => {
    const rank = new Int16Array(p * g);
    for (let gen = 0; gen < g; gen++) {
      const ids = Array.from({ length: p }, (_, i) => gen * p + i);
      ids.sort((a, b) => fitness[b] - fitness[a] || a - b);
      ids.forEach((id, r) => { rank[id] = r; });
    }
    return rank;
  }, [fitness, p, g]);
  const x = (gen: number) => ml + (gen + 0.5) * ((AW - ml - mr) / g);
  const y = (r: number) => mt + (r + 0.5) * ((AH - mt - mb) / p);
  const hasParents = parents[p] !== undefined && parents[p] >= 0;
  // Ancestors of every individual in generation `upto`, and the lineage of its best individual.
  const { links, lineage, bestId } = useMemo(() => {
    const links: Array<[number, number]> = [];
    const lineage: number[] = [];
    let best = upto * p;
    for (let i = 0; i < p; i++) { const id = upto * p + i; if (fitness[id] > fitness[best]) best = id; }
    if (!hasParents) return { links, lineage, bestId: best };
    let cur = new Set<number>(Array.from({ length: p }, (_, i) => upto * p + i));
    for (let gen = upto; gen > 0; gen--) {
      const next = new Set<number>();
      for (const id of cur) { const par = (gen - 1) * p + parents[id]; links.push([id, par]); next.add(par); }
      cur = next;
    }
    for (let id = best; id >= 0; ) {
      lineage.push(id);
      const gen = Math.floor(id / p);
      if (gen === 0) break;
      id = (gen - 1) * p + parents[id];
    }
    return { links, lineage, bestId: best };
  }, [fitness, parents, p, upto, hasParents]);
  const pos = (id: number): [number, number] => [x(Math.floor(id / p)), y(geo[id])];
  const dots = [];
  for (let id = 0; id < (upto + 1) * p; id++) {
    const [cx, cy] = pos(id);
    dots.push(<circle key={id} cx={cx} cy={cy} r={1.9} className="dot" style={{ fillOpacity: 0.15 + 0.85 * Math.min(1, fitness[id] / 20) }} />);
  }
  const color = ARM_STYLE[props.arm]?.color;
  return (
    <figure className="chart">
      <svg viewBox={`0 0 ${AW} ${AH}`} className="ancestry" role="img" aria-label={props.title}>
        {links.map(([a, b], i) => {
          const [x1, y1] = pos(b), [x2, y2] = pos(a);
          return <line key={i} x1={x1} y1={y1} x2={x2} y2={y2} className="anc" />;
        })}
        {dots}
        {lineage.length > 1 && (
          <polyline points={lineage.map((id) => pos(id).join(",")).join(" ")} className="lineage" style={{ stroke: color }} />
        )}
        <circle cx={pos(bestId)[0]} cy={pos(bestId)[1]} r={4.5} className="best" style={{ stroke: color }} />
        <text x={ml} y={AH - 8}>generation 0</text>
        <text x={AW - mr} y={AH - 8} textAnchor="end">generation {upto}</text>
      </svg>
    </figure>
  );
}

// ------------------------------------------------------------ organism grid

export function OrganismGrid(props: { food: Uint8Array; path: Int16Array; eatenAt: Map<number, number>; step: number; arm: string; label: string }) {
  const { food, path, eatenAt, step } = props;
  const n = 16, c = 10;
  const cells = [];
  for (let i = 0; i < n * n; i++) {
    if (!food[i]) continue;
    const t = eatenAt.get(i);
    const gone = t !== undefined && t <= step;
    cells.push(<circle key={i} cx={(i % n) * c + c / 2} cy={Math.floor(i / n) * c + c / 2} r={gone ? 1.4 : 3.2} className={gone ? "food eaten" : "food"} />);
  }
  const segs: string[] = [];
  let d = "";
  for (let t = 0; t <= step; t++) {
    const r = path[t * 3], col = path[t * 3 + 1];
    const px = col * c + c / 2, py = r * c + c / 2;
    if (t > 0) {
      const pr = path[(t - 1) * 3], pc = path[(t - 1) * 3 + 1];
      if (Math.abs(pr - r) > 1 || Math.abs(pc - col) > 1) { segs.push(d); d = ""; }
    }
    d += `${d ? "L" : "M"}${px},${py}`;
  }
  segs.push(d);
  const r = path[step * 3], col = path[step * 3 + 1], h = path[step * 3 + 2];
  const cx = col * c + c / 2, cy = r * c + c / 2;
  return (
    <svg viewBox={`0 0 ${n * c} ${n * c}`} className="organism" role="img" aria-label={props.label}>
      <rect x="0" y="0" width={n * c} height={n * c} className="board" />
      {Array.from({ length: n + 1 }, (_, i) => (
        <g key={i}>
          <line x1={i * c} x2={i * c} y1="0" y2={n * c} className="cellline" />
          <line y1={i * c} y2={i * c} x1="0" x2={n * c} className="cellline" />
        </g>
      ))}
      {cells}
      {segs.map((s, i) => s && <path key={i} d={s} className="trail" style={{ stroke: ARM_STYLE[props.arm]?.color }} />)}
      <polygon points="0,-4.6 3.8,3.6 -3.8,3.6" transform={`translate(${cx} ${cy}) rotate(${h * 90})`} className="agent" />
    </svg>
  );
}
