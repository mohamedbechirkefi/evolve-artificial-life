// SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0
// Visitor sandbox: runs RS, NOSEL and EVO on the reduced engine port in a Web
// Worker. Its output is labelled as sandbox output and never mixed with the
// published results. Nothing is stored or sent anywhere.
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { AncestryChart, ARM_STYLE, CurvesChart, OrganismGrid } from "./charts";
import { simulate, testLayouts } from "./engine";
import type { SandboxSettings, WorkerReply, WorkerRequest } from "./sandbox.worker";

type Done = Extract<WorkerReply, { type: "done" }>;
const DEFAULTS: SandboxSettings = { seed: 1, budget: 500, sigma: 0.1, k: 5 };

export function Sandbox() {
  const worker = useRef<Worker | null>(null);
  const [settings, setSettings] = useState<SandboxSettings>(DEFAULTS);
  const [running, setRunning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [out, setOut] = useState("");
  const [result, setResult] = useState<Done | null>(null);

  const start = useCallback(() => {
    worker.current?.terminate();
    const w = new Worker(new URL("./sandbox.worker.ts", import.meta.url), { type: "module" });
    w.onmessage = (ev: MessageEvent<WorkerReply>) => {
      const m = ev.data;
      if (m.type === "progress") { setProgress(m.fraction); return; }
      if (m.type === "done") {
        setResult(m);
        setOut(
          `Sandbox output (seed ${m.settings.seed}, illustrative): mean score on ${m.nTest} sandbox test layouts, ` +
            m.arms.map((a) => `${a.arm} ${a.testMean.toFixed(2)}`).join(", ") + " items per episode.",
        );
      }
      if (m.type === "error") setOut(`Sandbox run failed: ${m.message}`);
      if (m.type === "cancelled") setOut("Sandbox run cancelled.");
      setRunning(false);
    };
    w.onerror = () => { setOut("Sandbox run failed: the worker stopped."); setRunning(false); };
    worker.current = w;
    return w;
  }, []);

  useEffect(() => {
    start();
    return () => worker.current?.terminate();
  }, [start]);

  const run = () => {
    setRunning(true);
    setProgress(0);
    setOut("");
    (worker.current ?? start()).postMessage({ type: "run", settings } satisfies WorkerRequest);
  };
  // A synchronous search cannot read a cancel message, so cancelling ends the worker and starts a fresh one.
  const cancel = () => {
    start();
    setRunning(false);
    setOut("Sandbox run cancelled.");
  };
  const reset = () => {
    if (running) start();
    setRunning(false);
    setSettings(DEFAULTS);
    setResult(null);
    setOut("");
    setProgress(0);
  };
  const exportJson = () => {
    if (!result) return;
    const blob = new Blob([JSON.stringify({ label: "EVOLVE sandbox output (illustrative, not the research engine; not a research result)", ...result }, null, 1)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `evolve-sandbox-seed${result.settings.seed}.json`;
    a.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  };

  return (
    <section id="sandbox" aria-labelledby="h-sandbox" className="sandbox">
      <h2 id="h-sandbox">Sandbox: evolve your own organisms</h2>
      <p className="label sandbox-label">Sandbox output: illustrative, not the research engine</p>
      <p className="note">
        This runs a reduced port of the engine in your browser. The grid, the observation window, the policy network and the scoring
        are an exact port, checked against episodes from the Python engine with zero tolerance. The random numbers are not: the port
        uses a different generator, so no sandbox seed reproduces a research run, and its held-out layouts are its own. Nothing it
        produces is a research result or comparable to the published numbers.
      </p>
      <div className="controls" role="group" aria-label="Sandbox settings">
        <label>
          Seed{" "}
          <input type="number" min={1} max={1_000_000} value={settings.seed} disabled={running}
            onChange={(e) => setSettings({ ...settings, seed: Math.min(1_000_000, Math.max(1, Math.trunc(Number(e.target.value)) || 1)) })} />
        </label>
        <label>
          Budget{" "}
          <select value={settings.budget} disabled={running} onChange={(e) => setSettings({ ...settings, budget: Number(e.target.value) as 500 | 2000 })}>
            <option value={500}>500 evaluations (25 x 20)</option>
            <option value={2000}>2,000 evaluations (50 x 40)</option>
          </select>
        </label>
        <label>
          Mutation sigma{" "}
          <select value={settings.sigma} disabled={running} onChange={(e) => setSettings({ ...settings, sigma: Number(e.target.value) })}>
            <option value={0.02}>0.02</option>
            <option value={0.1}>0.1 (frozen primary)</option>
            <option value={0.5}>0.5</option>
          </select>
        </label>
        <label>
          Training design{" "}
          <select value={settings.k} disabled={running} onChange={(e) => setSettings({ ...settings, k: Number(e.target.value) as 1 | 5 })}>
            <option value={5}>K = 5 resampled environments</option>
            <option value={1}>K = 1 fixed environment</option>
          </select>
        </label>
        <button type="button" className="primary" onClick={run} disabled={running}>Run sandbox</button>
        <button type="button" onClick={cancel} disabled={!running}>Cancel</button>
        <button type="button" onClick={reset}>Reset</button>
      </div>
      {running && <progress max={1} value={progress} aria-label="Sandbox progress">{Math.round(progress * 100)}%</progress>}
      <p aria-live="polite" className="sandbox-out">{out}</p>
      {!result && !running && <p className="note">No sandbox run yet. The default settings take a few seconds; 2,000 evaluations take longer.</p>}
      {result && <SandboxResult r={result} onExport={exportJson} />}
    </section>
  );
}

function SandboxResult({ r, onExport }: { r: Done; onExport: () => void }) {
  const [armName, setArmName] = useState<"RS" | "NOSEL" | "EVO">("EVO");
  const [layoutIdx, setLayoutIdx] = useState(0);
  const [step, setStep] = useState(100);
  const [playing, setPlaying] = useState(false);
  const arm = r.arms.find((a) => a.arm === armName)!;
  const layouts = useMemo(() => testLayouts(r.settings.seed, r.nTest), [r]);
  const ep = useMemo(() => simulate(arm.theta, layouts[layoutIdx], 100, true), [arm, layouts, layoutIdx]);
  const budget = r.population * r.generations;

  useEffect(() => {
    if (!playing) return;
    const t = window.setInterval(() => setStep((s) => { if (s >= 100) { setPlaying(false); return s; } return s + 1; }), 90);
    return () => window.clearInterval(t);
  }, [playing]);

  const curves = r.arms.map((a) => {
    const xs: number[] = [], ys: number[] = [];
    let m = 0;
    a.fitness.forEach((f, i) => { m = Math.max(m, f); if ((i + 1) % r.population === 0) { xs.push(i + 1); ys.push(m); } });
    return { arm: a.arm, x: xs, median: ys };
  });
  const evo = r.arms.find((a) => a.arm === "EVO")!;
  const slots = evo.parent.map((par, i) => (par < 0 ? -1 : par - (Math.floor(i / r.population) - 1) * r.population));
  const eatenSoFar = [...ep.eatenAt!.values()].filter((t) => t <= step).length;

  return (
    <div className="sandbox-result">
      <div className="table-scroll" id="sandbox-scores" role="region" aria-label="Sandbox scores" tabIndex={0}>
        <table>
          <caption>Sandbox output, seed {r.settings.seed}: budget {budget.toLocaleString("en-US")}, sigma {r.settings.sigma}, K = {r.settings.k}{r.settings.k === 1 ? " (fixed)" : ""}</caption>
          <thead>
            <tr><th scope="col">Arm</th><th scope="col">Best training fitness</th><th scope="col">Mean over {r.nTest} sandbox test layouts</th></tr>
          </thead>
          <tbody>
            {r.arms.map((a) => (
              <tr key={a.arm}><th scope="row">{a.arm}</th><td>{a.fitness[a.returned].toFixed(2)}</td><td>{a.testMean.toFixed(2)}</td></tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="note">One sandbox seed is one run: it says nothing about the average difference, which the research estimates over 30 paired seeds with intervals.</p>
      <div className="lab-grid">
        <div>
          <h3>Sandbox fitness curves</h3>
          <CurvesChart title="Sandbox output: best-so-far training fitness against evaluations for RS, NOSEL and EVO in this sandbox run." series={curves} budget={budget} />
        </div>
        <div>
          <h3>Sandbox ancestry, EVO</h3>
          <AncestryChart title="Sandbox output: ancestry of the EVO population in this sandbox run, generation 0 to the last generation." arm="EVO"
            fitness={evo.fitness} parents={slots} population={r.population} generations={r.generations} upto={r.generations - 1} />
        </div>
      </div>
      <h3>Watch a returned organism forage</h3>
      <div className="controls" role="group" aria-label="Organism replay controls">
        <label>
          Organism{" "}
          <select value={armName} onChange={(e) => setArmName(e.target.value as "RS" | "NOSEL" | "EVO")}>
            {r.arms.map((a) => <option key={a.arm} value={a.arm}>{ARM_STYLE[a.arm].label}</option>)}
          </select>
        </label>
        <label>
          Sandbox test layout{" "}
          <select value={layoutIdx} onChange={(e) => setLayoutIdx(Number(e.target.value))}>
            {layouts.map((_, i) => <option key={i} value={i}>{i + 1}</option>)}
          </select>
        </label>
        <label className="grow">
          Step <output htmlFor="step">{step}</output>
          <input id="step" type="range" min={0} max={100} value={step} onChange={(e) => { setPlaying(false); setStep(Number(e.target.value)); }} />
        </label>
        <button type="button" onClick={() => { if (step >= 100) setStep(0); setPlaying((x) => !x); }} aria-pressed={playing}>{playing ? "Pause organism" : "Play organism"}</button>
        <button type="button" onClick={onExport}>Export sandbox JSON</button>
      </div>
      <div className="organism-wrap">
        <OrganismGrid food={layouts[layoutIdx].food} path={ep.path!} eatenAt={ep.eatenAt!} step={step} arm={armName}
          label={`Sandbox output: the ${armName} organism on sandbox test layout ${layoutIdx + 1} at step ${step}; it has eaten ${eatenSoFar} of 24 food items.`} />
        <p className="readout">
          Step {step} of 100: the {armName} organism has eaten {eatenSoFar} of 24 items (episode total {ep.eaten}). Dots are food; the
          triangle is the organism and points in its heading; the line is its path on the torus (it wraps at the edges). It sees a
          5 x 5 window around itself and chooses forward, left, right or stay.
        </p>
      </div>
    </div>
  );
}
