// SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0
// Replay of the committed confirmatory runs: fitness curves (median and
// interquartile range over 30 run seeds) and ancestry per run seed, scrubbed
// generation by generation. Every value comes from results.json.
import { useEffect, useRef, useState } from "react";
import { AncestryChart, ARM_STYLE, CurvesChart } from "./charts";
import { Reveal } from "./motion";
import type { Results } from "./results";

export function Lab({ r }: { r: Results }) {
  const rp = r.replay;
  const [armName, setArmName] = useState("EVO");
  const [seed, setSeed] = useState(0);
  const [gen, setGen] = useState(rp.generations - 1);
  const [playing, setPlaying] = useState(false);
  const timer = useRef<number | null>(null);

  useEffect(() => {
    if (!playing) return;
    timer.current = window.setInterval(() => {
      setGen((g) => {
        if (g >= rp.generations - 1) { setPlaying(false); return g; }
        return g + 1;
      });
    }, 220);
    return () => { if (timer.current !== null) window.clearInterval(timer.current); };
  }, [playing, rp.generations]);

  const arm = rp.arms.find((a) => a.arm === armName) ?? rp.arms[0];
  const run = arm.runs.find((x) => x.seed === seed) ?? arm.runs[0];
  const p = rp.population;
  const cursor = (gen + 1) * p;
  const exp1 = r.curves.items.find((c) => c.experiment_id === "EXP-001" && c.condition === "main")!;
  const exp2 = r.curves.items.find((c) => c.experiment_id === "EXP-002" && c.condition === "main")!;
  const toSeries = (c: typeof exp1) => c.arms.map((a) => ({ arm: a.arm, x: a.evaluation, median: a.median, q25: a.q25, q75: a.q75 }));
  const seedLine = {
    arm: arm.arm,
    x: run.best_per_generation.map((_, i) => (i + 1) * p),
    y: run.best_per_generation,
    label: `${arm.arm}, run seed ${run.seed} (this run)`,
  };
  const inPanel1 = exp1.arms.some((a) => a.arm === arm.arm);
  const best = run.best_per_generation[gen];
  const returnedGen = Math.floor(run.returned_index / p);

  return (
    <section id="lab" aria-labelledby="h-lab">
      <h2 id="h-lab">Replay: how the committed runs searched</h2>
      <p className="label measured">Measured: committed confirmatory runs (EXP-001 and EXP-002, E = 2,000, K = 5)</p>
      <p>
        Each confirmatory run spends 2,000 policy evaluations. Population arms do so in 40 generations of 50 policies; RS draws
        2,000 independent policies, shown here in chunks of 50 for comparison. Choose an arm and a run seed, then move through the
        generations. The curves show the best training fitness found so far; that is the training signal, not the held-out result,
        which is reported in the results section.
      </p>
      <div className="controls" role="group" aria-label="Replay controls">
        <label>
          Arm{" "}
          <select value={armName} onChange={(e) => setArmName(e.target.value)}>
            {rp.arms.map((a) => (
              <option key={a.arm} value={a.arm}>{ARM_STYLE[a.arm]?.label ?? a.arm}</option>
            ))}
          </select>
        </label>
        <label>
          Run seed{" "}
          <select value={seed} onChange={(e) => setSeed(Number(e.target.value))}>
            {arm.runs.map((x) => (
              <option key={x.seed} value={x.seed}>{x.seed}</option>
            ))}
          </select>
        </label>
        <label className="grow">
          Generation <output htmlFor="gen">{gen}</output>
          <input id="gen" type="range" min={0} max={rp.generations - 1} value={gen} onChange={(e) => { setPlaying(false); setGen(Number(e.target.value)); }} />
        </label>
        <button type="button" onClick={() => { setPlaying(false); setGen((g) => Math.max(0, g - 1)); }}>Previous generation</button>
        <button type="button" onClick={() => { if (gen >= rp.generations - 1) setGen(0); setPlaying((x) => !x); }} aria-pressed={playing}>
          {playing ? "Pause replay" : "Play replay"}
        </button>
        <button type="button" onClick={() => { setPlaying(false); setGen((g) => Math.min(rp.generations - 1, g + 1)); }}>Next generation</button>
      </div>
      <p className="readout">
        {arm.arm}, run seed {run.seed}, generation {gen} ({cursor.toLocaleString("en-US")} evaluations used): best training fitness so
        far {best.toFixed(1)} items per episode. The returned policy was found in generation {returnedGen}; its held-out fitness is{" "}
        {run.f_test} items per episode (raw per-run value from <code>{run.run_id}</code>, not a manuscript number).
      </p>

      <div className="lab-grid">
        <div>
          <h3>Fitness curves, EXP-001 arms</h3>
          <Reveal>
          <CurvesChart
            title="Best-so-far training fitness against evaluations for RS, NOSEL and EVO in EXP-001: EVO rises far above RS, NOSEL stays lowest."
            series={toSeries(exp1)}
            budget={exp1.budget}
            cursor={cursor}
            extra={inPanel1 ? [seedLine] : []}
          />
          </Reveal>
        </div>
        <div>
          <h3>Fitness curves, mutation strength (EXP-002)</h3>
          <Reveal>
          <CurvesChart
            title="Best-so-far training fitness for sigma 0, 0.02, 0.1 and 0.5 in EXP-002: sigma 0.5 ends highest, above the frozen sigma 0.1."
            series={toSeries(exp2)}
            budget={exp2.budget}
            cursor={cursor}
            extra={inPanel1 ? [] : [seedLine]}
          />
          </Reveal>
        </div>
      </div>
      <p className="note">
        Lines: median over the 30 run seeds; shaded bands: interquartile range (25th to 75th percentile); thin line: the selected run
        seed. Units: food items per episode (24 available), averaged over the K = 5 training environments of each evaluation. Hover a
        chart for values. Derived by <code>scripts/export_demo_data.py</code> from the committed run traces; these curves are not
        printed in the manuscript (the reports' FIG-2 shows the adaptation curves).
      </p>

      <h3>Ancestry, {ARM_STYLE[arm.arm]?.label ?? arm.arm}, run seed {run.seed}</h3>
      <AncestryChart
        title={`Ancestry of ${arm.arm} run seed ${run.seed} up to generation ${gen}. Each column is a generation, each dot a policy ranked by training fitness; grey lines link the surviving lineages to their parents; the coloured line traces the best policy of generation ${gen} back to generation 0.`}
        arm={arm.arm}
        fitness={run.fitness}
        parents={run.parents}
        population={p}
        generations={rp.generations}
        upto={gen}
      />
      <p className="note">
        {arm.arm === "RS"
          ? "RS has no ancestry: every policy is an independent draw. Dots are shown in chunks of 50 for comparison."
          : arm.arm === "SELONLY"
            ? "SELONLY copies selected parents without mutation (sigma 0), so every lineage stays one of the 50 starting policies."
            : arm.arm === "NOSEL"
              ? "NOSEL chooses parents uniformly at random: lineages drift and fitness does not concentrate."
              : "Under truncation selection the surviving lineages collapse to a few founders within a few generations."}{" "}
        More opaque dots mean higher training fitness. Columns: generations 0 to {gen}; rows: the 50 policies of each generation ranked by
        training fitness, best at the top.
      </p>
    </section>
  );
}
