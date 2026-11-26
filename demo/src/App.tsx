// SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0
import { useEffect, useState } from "react";
import { AxisStrip, domainOf, IntervalStrip, KIND_LABEL } from "./charts";
import { Lab } from "./Lab";
import { fmtEstimate, fmtInterval, loadResults, ResultsError, type Estimate, type Results } from "./results";
import { Sandbox } from "./Sandbox";
import { PlateStack } from "./Hero";
import { SectionNav } from "./motion";

type State = { kind: "loading" } | { kind: "error"; message: string } | { kind: "ready"; results: Results };

export function App() {
  const [state, setState] = useState<State>({ kind: "loading" });

  useEffect(() => {
    loadResults()
      .then((results) => setState({ kind: "ready", results }))
      .catch((e: unknown) =>
        setState({ kind: "error", message: e instanceof ResultsError ? e.message : "results could not be loaded" }),
      );
  }, []);

  const answer = state.kind === "ready" ? headlineOf(state.results, "EXP-001") : null;
  const k1 = state.kind === "ready" ? headlineOf(state.results, "EXP-003") : null;

  return (
    <>
      <a className="skip" href="#main">Skip to content</a>
      <header className="bar">
        <div className="bar-in">
          <a className="brand" href="#top" aria-label="EVOLVE, back to the top">
            <img src="./brand/evolve-mark.svg" alt="" width="30" height="30" />
            <span className="wordmark">Evolve</span>
          </a>
          <SectionNav />
        </div>
      </header>
      <main id="main">
        <div className="hero" id="top">
          <div className="wrap hero-grid">
            <div className="hero-text">
              <p className="hero-status">EVOLVE, a simulation study. Preprint draft, not peer-reviewed.</p>
              <h1>Does selection beat random search at an equal budget, and how robust is it?</h1>
              {answer && k1 ? (
                <p className="answer">
                  In this simulation, yes at the frozen setting: at 2,000 evaluations EVO minus RS was{" "}
                  <span className="fig">{fmtEstimate(answer)}</span> {answer.unit} on held-out layouts (95% CI{" "}
                  <span className="fig">{fmtInterval(answer)}</span>, {answer.n_pairs} paired run seeds). With one fixed training
                  environment the advantage was inconclusive (<span className="fig">{fmtEstimate(k1)}</span>, CI{" "}
                  <span className="fig">{fmtInterval(k1)}</span>).
                </p>
              ) : null}
              <p className="dek">Inherited, mutated policies under selection in a simulated foraging grid. Simulation only: not evidence about biological evolution or general intelligence.</p>
              <p className="byline">Mohamed Bechir Kefi, independent researcher</p>
            </div>
            <PlateStack />
          </div>
        </div>
        <div className="wrap">
          {state.kind === "loading" && <p role="status">Loading the published results.</p>}
          {state.kind === "error" && (
            <div role="alert" className="panel error">
              <h2>Results unavailable</h2>
              <p>The published results file failed validation, so no numbers are shown.</p>
              <p><code>{state.message}</code></p>
            </div>
          )}
          {state.kind === "ready" ? <Published r={state.results} /> : <Sandbox />}
        </div>
      </main>
      <footer className="site">
        <div className="wrap foot-grid">
          <div className="foot-brand">
            <img src="./brand/evolve-lockup.svg" alt="EVOLVE" width="132" height="40" />
            <p>Mohamed Bechir Kefi, independent researcher.</p>
          </div>
          <ul className="foot-links">
            <li><a href="https://github.com/mohamedbechirkefi/evolve-artificial-life">Repository on GitHub</a></li>
            <li><a href="https://github.com/mohamedbechirkefi/evolve-artificial-life/blob/main/research/paper/manuscript.md">Manuscript (preprint draft)</a></li>
            <li><a href="https://labs.kefimohamedbechir.workers.dev">All lab studies</a></li>
            <li><a href="https://evolve-artificial-life.kefimohamedbechir.workers.dev">This demo: evolve-artificial-life.kefimohamedbechir.workers.dev</a></li>
          </ul>
          <div className="foot-notes">
            <p>Runs offline after the first load. No data about visitors is collected, stored or sent anywhere; the page makes no request to any other host.</p>
            <p>Licence: EVOLVE Source-Available Non-Commercial Research License v1.0 (custom, not OSI-approved). An AI system was used as a research and development assistant; it is not an author.</p>
            <p>Type: IM Fell English (Igino Marini) and Alegreya Sans (Huerta Tipogr&aacute;fica), both under the SIL Open Font License 1.1, served from this site.</p>
          </div>
        </div>
      </footer>
    </>
  );
}

function headlineOf(r: Results, id: string): Estimate | null {
  return r.experiments.find((e) => e.id === id)?.estimates.find((x) => x.headline) ?? null;
}

const HEADLINE_TEXT: Record<string, { title: string; plain: string }> = {
  "EXP-001": {
    title: "Primary result: selection beat random search",
    plain: "At 2,000 evaluations, EVO's returned policies collected more food on 200 held-out layouts than RS's, in 29 of 30 paired run seeds.",
  },
  "EXP-002": {
    title: "Against an assumption: the frozen sigma 0.1 was not the best setting tested",
    plain: "Sigma 0.5 exceeded the frozen sigma 0.1 by 1.776 items per episode (shown as sigma 0.1 minus sigma 0.5). The owner classified this as a contradicting result under EXP-002's rule, a finding against EXP-002's assumption about the setting; H1 of EXP-001 stands.",
  },
  "EXP-003": {
    title: "Sensitivity: with one fixed training environment, inconclusive",
    plain: "With K = 1 the held-out advantage was inconclusive, which is not equivalence, and EVO overfit its single training layout more than RS. The primary result holds for resampled training only.",
  },
};

function Headline({ id, e, domain }: { id: string; e: Estimate; domain: [number, number] }) {
  const t = HEADLINE_TEXT[id];
  return (
    <article className={`finding kind-${e.kind}`} aria-labelledby={`hl-${id}`}>
      <div className="finding-text">
        <p className="finding-kind"><span className={`tag kind-${e.kind}`}>{KIND_LABEL[e.kind]}</span> {id}</p>
        <h3 id={`hl-${id}`}>{t.title}</h3>
        <p className="big">
          <span className="num">{fmtEstimate(e)}</span> <span className="ci">95% CI {fmtInterval(e)}</span>
        </p>
        <p className="meta">{e.label}; {e.unit}; n = {e.n_pairs} paired run seeds</p>
        <p className="plain">{t.plain}</p>
      </div>
      <div className="finding-strip">
        <IntervalStrip e={e} domain={domain} />
      </div>
    </article>
  );
}

function Published({ r }: { r: Results }) {
  const all = r.experiments.flatMap((e) => e.estimates);
  const domain = domainOf(all.filter((x) => x.label.includes("F_test")));
  const headlines = r.experiments.flatMap((e) => e.estimates.filter((x) => x.headline).map((x) => ({ id: e.id, x })));
  const confirmatory = r.experiments.filter((e) => e.id.startsWith("EXP-"));
  const exploratory = r.experiments.filter((e) => !e.id.startsWith("EXP-"));
  return (
    <>
      <section id="overview" aria-labelledby="h-overview">
        <h2 id="h-overview">Three findings on one plate</h2>
        <p className="status-label">{r.status_label}</p>
        <p className="question">{r.question}</p>
        <p>
          A 16 x 16 grid holds 24 food items. A small neural network sees a 5 x 5 window and chooses to move, turn or stay. Three
          ways of searching for good networks get the same budget of 2,000 evaluations: independent random search (RS), evolution
          with selection and mutation (EVO), and the same population without selection (NOSEL). The protocol was frozen by the
          owner before any confirmatory run; 420 of 420 planned runs completed. The three findings below carry equal weight.
        </p>
        <div className="findings">
          {headlines.map(({ id, x }) => <Headline key={id} id={id} e={x} domain={domain} />)}
          <div className="findings-axis" aria-hidden="true">
            <span className="axis-note">difference in held-out food items per episode; dashed line: no difference</span>
            <AxisStrip domain={domain} />
          </div>
        </div>
        <p className="note">
          Intervals: 95 percent percentile bootstrap over run seeds (10,000 resamples). Filled point: the interval excludes 0; hollow
          point: it does not. The zero line marks no difference. All numbers are identical to the manuscript (<code>research/paper/manuscript.md</code>).
        </p>
      </section>

      <Lab r={r} />

      <Sandbox />

      <section id="results" aria-labelledby="h-results">
        <h2 id="h-results">Published results</h2>
        <p className="label measured">Measured: committed results at revision <code>{r.code_revision.slice(0, 12)}</code></p>
        <p className="note">
          Every contrast registered in the three experiments, including the contradicting and inconclusive ones, followed by the
          exploratory analyses, labelled as such. These numbers are separate from anything the sandbox produces. F_test is the
          held-out fitness of the returned policy in food items per episode; a positive difference favours the first arm.
        </p>
        {[...confirmatory, ...exploratory].map((e) => (
          <article key={e.id} className={`panel${e.id.startsWith("EXP-") ? "" : " exploratory"}`} aria-labelledby={`h-${e.id}`}>
            <h3 id={`h-${e.id}`}>{e.id}: {e.title}</h3>
            <p>
              <span className="badge">{e.status}</span>
            </p>
            <p><strong>{e.id.startsWith("EXP-") ? "Verdict under the frozen rule:" : "Status:"}</strong> {e.verdict}</p>
            <div className="table-scroll" id={`est-${e.id}`} role="region" aria-label={`${e.id} estimates`} tabIndex={0}>
              <table className="estimates">
                <thead>
                  <tr>
                    <th scope="col">Contrast</th>
                    <th scope="col">Mean difference</th>
                    <th scope="col">95% CI</th>
                    <th scope="col">d_z</th>
                    <th scope="col">Seeds + / -</th>
                    <th scope="col">Reading</th>
                    <th scope="col" className="plotcol">Interval (dashed line: 0)</th>
                  </tr>
                </thead>
                <tbody>
                  {e.estimates.map((x) => (
                    <tr key={x.label} className={`kind-${x.kind}`}>
                      <th scope="row">{x.label}</th>
                      <td className="numcell">{fmtEstimate(x)}</td>
                      <td className="numcell">{fmtInterval(x)}{x.ci_level !== null && x.ci_level !== 0.95 ? ` (${(x.ci_level * 100).toFixed(2)}% level)` : ""}</td>
                      <td className="numcell">{x.dz_display ?? "not printed"}</td>
                      <td className="numcell">{x.seeds_display ?? "not printed"}</td>
                      <td><span className={`tag kind-${x.kind}`}>{KIND_LABEL[x.kind]}</span> {x.reading}</td>
                      <td className="plotcol"><IntervalStrip e={x} domain={x.label.includes("F_test") || x.label.includes("Bonferroni") || x.label.includes("seed 13") ? domain : domainOf(e.estimates)} /></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {e.notes.map((n, i) => <p key={i} className="note">{n}</p>)}
            <p className="meta">
              Report: <code>{e.report_path}</code>
              {e.claim_ids.length > 0 && <> · Claims: {e.claim_ids.join(", ")}</>}
            </p>
          </article>
        ))}
        <p className="note">Shared axis for every F_test contrast: {domain[0]} to {domain[1]} items per episode, zero marked. The F_shift, gap, F_train_fixed and overfit_drop rows use their own experiment's axis.</p>

        <h3>Arm means of held-out fitness</h3>
        <div className="table-scroll" id="arm-means" role="region" aria-label="Arm means" tabIndex={0}>
          <table>
            <thead>
              <tr><th scope="col">Experiment</th><th scope="col">Condition</th><th scope="col">Arm</th><th scope="col">Mean F_test</th><th scope="col">SD over 30 seeds</th></tr>
            </thead>
            <tbody>
              {r.arm_means.map((m) => (
                <tr key={m.experiment_id + m.condition + m.arm}>
                  <td>{m.experiment_id}</td><td>{m.condition}</td><th scope="row">{m.arm}</th>
                  <td className="numcell">{m.display}</td><td className="numcell">{m.sd_display}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="note">Means over n = 30 run seeds, food items per episode (24 available). The SD describes spread between seeds; intervals for differences are in the tables above. SDs as printed in each experiment report's TAB-1. The comparison of ablation means with the RS mean crosses experiments and has no registered paired contrast.</p>
        <p><a href="./data/results.json" download="evolve-results.json">Download the exported results (JSON)</a></p>
      </section>

      <section id="assumptions" aria-labelledby="h-assumptions">
        <h2 id="h-assumptions">Assumptions</h2>
        <p className="label assumption">Assumptions and design values, not results</p>
        <dl className="assumptions">
          {r.assumptions.map((a) => (
            <div key={a.name}>
              <dt>{a.name}</dt>
              <dd>
                {a.value} <span className="meta">({a.source})</span>
              </dd>
            </div>
          ))}
        </dl>
      </section>

      <section id="method" aria-labelledby="h-method">
        <h2 id="h-method">Method and limitations</h2>
        <p>
          The main protocol, three experiment protocols and three configs were frozen with SHA-256 hashes before any confirmatory run
          (<code>research/freeze.json</code>); the run command refuses a config whose hash differs. The analysis script was committed
          before any confirmatory output. The unit of analysis is the run seed; each contrast is a mean paired difference over 30 run
          seeds with a 95 percent percentile bootstrap interval. The frozen rule reads an interval above 0 as supported, at or below 0
          as contradicted, and otherwise as inconclusive, which is never read as equivalence. Secondary contrasts are estimates
          without a significance claim, and no multiplicity adjustment was frozen.
        </p>
        <h3>Limitations (from manuscript section 7)</h3>
        <ul>
          {r.limitations.map((l, i) => <li key={i}>{l}</li>)}
        </ul>
        <details>
          <summary>Source files and hashes ({r.sources.length})</summary>
          <ul className="meta sources">
            {r.sources.map((s) => (
              <li key={s.path}>
                <code>{s.path}</code> <code>{s.sha256.slice(0, 12)}</code>
              </li>
            ))}
          </ul>
        </details>
      </section>
    </>
  );
}
