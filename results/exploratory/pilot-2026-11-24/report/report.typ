#let horizontalrule = line(start: (25%,0%), end: (75%,0%))

#show terms: it => {
  it.children
    .map(child => [
      #strong[#child.term]
      #block(inset: (left: 1.5em, top: -0.4em))[#child.description]
      ])
    .join()
}

#set table(
  inset: 6pt,
  stroke: none
)

#show figure.where(
  kind: table
): set figure.caption(position: top)

#show figure.where(
  kind: image
): set figure.caption(position: bottom)

#let content-to-string(content) = {
  if content.has("text") {
    content.text
  } else if content.has("children") {
    content.children.map(content-to-string).join("")
  } else if content.has("body") {
    content-to-string(content.body)
  } else if content == [ ] {
    " "
  }
}
#let conf(
  title: none,
  subtitle: none,
  authors: (),
  keywords: (),
  date: none,
  abstract: none,
  cols: 1,
  margin: (x: 1.25in, y: 1.25in),
  paper: "us-letter",
  lang: "en",
  region: "US",
  font: (),
  fontsize: 11pt,
  sectionnumbering: none,
  pagenumbering: "1",
  doc,
) = {
  set document(
    title: title,
    author: authors.map(author => content-to-string(author.name)),
    keywords: keywords,
  )
  set page(
    paper: paper,
    margin: margin,
    numbering: pagenumbering,
    columns: cols,
    )
  set par(justify: true)
  set text(lang: lang,
           region: region,
           font: font,
           size: fontsize)
  set heading(numbering: sectionnumbering)

  place(top, float: true, scope: "parent", clearance: 4mm)[
  #if title != none {
    align(center)[#block(inset: 2em)[
      #text(weight: "bold", size: 1.5em)[#title]
      #(if subtitle != none {
        parbreak()
        text(weight: "bold", size: 1.25em)[#subtitle]
      })
    ]]
  }

  #if authors != none and authors != [] {
    let count = authors.len()
    let ncols = calc.min(count, 3)
    grid(
      columns: (1fr,) * ncols,
      row-gutter: 1.5em,
      ..authors.map(author =>
          align(center)[
            #author.name \
            #author.affiliation \
            #author.email
          ]
      )
    )
  }

  #if date != none {
    align(center)[#block(inset: 1em)[
      #date
    ]]
  }

  #if abstract != none {
    block(inset: 2em)[
    #text(weight: "semibold")[Abstract] #h(1em) #abstract
    ]
  }
  ]

  doc
}
#show: doc => conf(
  font: ("Libertinus Serif",),
  pagenumbering: "1",
  cols: 1,
  doc,
)


= EVOLVE exploratory pilot (not a finding)
<evolve-exploratory-pilot-not-a-finding>
Generated 2026-11-24T16:10:29.741927Z by `src/evolve/report.py` from
`results/exploratory/pilot-2026-11-24`. Label(s): exploratory. All
results are simulations of a synthetic grid world.

#strong[EXPLORATORY. NOT A FINDING.] These runs were executed before the
protocol freeze, on the exploratory test pool and exploratory run seeds.
They exist to measure runtime, seed spread and degenerate cases for
planning. They must not be cited as evidence or pooled with confirmatory
runs.

== Runs
<runs>
120 runs (120 ok, 0 failed). Code revision(s): d06c290d8c64.

== TAB-1. Summary by condition and arm
<tab-1.-summary-by-condition-and-arm>
#figure(
  align(center)[#table(
    columns: (7.14%, 7.14%, 7.14%, 7.14%, 7.14%, 7.14%, 7.14%, 7.14%, 7.14%, 7.14%, 7.14%, 7.14%, 7.14%, 7.14%),
    align: (auto,auto,auto,auto,auto,auto,auto,auto,auto,auto,auto,auto,auto,auto,),
    table.header([condition], [arm], [n ok], [n failed], [F\_test mean
      (sd)], [F\_test min to max], [F\_train\_fresh mean], [F\_shift
      mean], [gap mean], [AUC mean], [geno div], [behav div], [stay
      frac], [s/run mean],),
    table.hline(),
    [E500], [EVO], [10], [0], [6.612 (2.930)], [3.060 to
    11.595], [6.703], [4.376], [0.091], [7.754], [4.23], [0.413], [0.067], [1.28],
    [E500], [RS], [10], [0], [2.251 (1.138)], [0.945 to
    3.935], [2.293], [1.969], [0.042], [3.473], [21.65], [0.634], [0.131], [1.54],
    [E8000], [EVO], [10], [0], [14.474 (0.948)], [13.195 to
    15.685], [14.559], [9.465], [0.086], [17.413], [6.56], [0.300], [0.007], [20.92],
    [E8000], [RS], [10], [0], [5.673 (1.617)], [3.555 to
    9.025], [5.756], [4.253], [0.083], [7.060], [21.69], [0.616], [0.104], [19.99],
    [K1], [EVO], [10], [0], [5.401 (2.228)], [2.390 to
    10.310], [5.535], [5.287], [0.134], [16.308], [4.89], [0.407], [0.126], [1.18],
    [K1], [RS], [10], [0], [2.904 (1.450)], [1.465 to
    6.465], [3.007], [2.392], [0.104], [8.926], [21.70], [0.616], [0.196], [1.36],
    [main], [EVO-sigma0.02], [10], [0], [5.052 (2.100)], [2.170 to
    8.350], [5.150], [4.554], [0.099], [8.624], [1.08], [0.218], [0.105], [4.15],
    [main], [EVO-sigma0.5], [10], [0], [12.738 (1.585)], [10.715 to
    15.355], [12.875], [8.899], [0.137], [14.826], [22.55], [0.446], [0.039], [4.43],
    [main], [EVO], [10], [0], [11.482 (1.832)], [7.705 to
    13.410], [11.952], [8.085], [0.469], [13.578], [4.90], [0.308], [0.011], [4.12],
    [main], [NOSEL], [10], [0], [2.438 (0.911)], [0.640 to
    3.530], [2.639], [2.044], [0.201], [4.466], [17.04], [0.520], [0.221], [4.17],
    [main], [RS], [10], [0], [3.559 (1.580)], [1.150 to
    6.115], [3.650], [2.573], [0.091], [5.296], [21.70], [0.616], [0.120], [3.91],
    [main], [SELONLY], [10], [0], [2.543 (1.331)], [0.930 to
    4.480], [2.588], [2.324], [0.045], [6.765], [0.00], [0.000], [0.215], [4.10],
  )]
  , kind: table
  )

Units: fitness in food items per episode; gap = F\_train\_fresh -
F\_test; s/run = wall-clock seconds.

== TAB-2. Paired contrasts on F\_test (unit: run seed)
<tab-2.-paired-contrasts-on-f_test-unit-run-seed>
Mean paired difference with a 95 percent percentile bootstrap interval
over run seeds (10000 resamples, analysis seed 0); d\_z = mean / SD of
the differences; Wilcoxon signed-rank (normal approximation) as a
robustness check. MDE = normal-approximation minimum detectable mean
difference at 80 percent power and two-sided alpha 0.05, using the
observed SD of differences.

#figure(
  align(center)[#table(
    columns: (9.09%, 9.09%, 9.09%, 9.09%, 9.09%, 9.09%, 9.09%, 9.09%, 9.09%, 9.09%, 9.09%),
    align: (auto,auto,auto,auto,auto,auto,auto,auto,auto,auto,auto,),
    table.header([condition], [contrast], [n pairs], [mean diff], [95%
      CI], [SD diff], [d\_z], [Wilcoxon p], [MDE n], [MDE 20], [MDE 30],),
    table.hline(),
    [E500], [EVO - RS], [10], [4.361], [\[2.273,
    6.581\]], [3.683], [1.18], [0.0069], [3.263], [2.307], [1.884],
    [E8000], [EVO - RS], [10], [8.801], [\[7.623,
    9.913\]], [1.951], [4.51], [0.0051], [1.728], [1.222], [0.998],
    [K1], [EVO - RS], [10], [2.497], [\[0.791,
    4.315\]], [2.989], [0.84], [0.0367], [2.648], [1.873], [1.529],
    [main], [EVO - RS], [10], [7.923], [\[6.462,
    9.529\]], [2.591], [3.06], [0.0051], [2.295], [1.623], [1.325],
    [main], [EVO-sigma0.02 - RS], [10], [1.492], [\[0.054,
    2.778\]], [2.323], [0.64], [0.0593], [2.058], [1.455], [1.188],
    [main], [EVO-sigma0.5 - RS], [10], [9.178], [\[7.554,
    10.934\]], [2.861], [3.21], [0.0051], [2.535], [1.792], [1.464],
    [main], [NOSEL - RS], [10], [-1.121], [\[-2.179,
    0.034\]], [1.871], [-0.60], [0.0926], [1.658], [1.172], [0.957],
    [main], [SELONLY - RS], [10], [-1.016], [\[-2.110,
    0.034\]], [1.851], [-0.55], [0.3329], [1.639], [1.159], [0.947],
    [main], [EVO - EVO-sigma0.02], [10], [6.431], [\[5.177,
    7.559\]], [2.041], [3.15], [0.0051], [1.808], [1.279], [1.044],
    [main], [EVO - EVO-sigma0.5], [10], [-1.255], [\[-2.325,
    \-0.128\]], [1.865], [-0.67], [0.0593], [1.652], [1.168], [0.954],
    [main], [EVO - NOSEL], [10], [9.044], [\[7.712,
    10.183\]], [2.114], [4.28], [0.0051], [1.873], [1.325], [1.082],
    [main], [EVO - SELONLY], [10], [8.939], [\[7.643,
    10.097\]], [2.084], [4.29], [0.0051], [1.847], [1.306], [1.066],
  )]
  , kind: table
  )

In exploratory reports these intervals describe planning quantities
(seed spread) only. They are not tests of the registered hypotheses.

== FIG-1
<fig-1>
#figure(image("figures/FIG-1_f_test_by_arm.png"),
  caption: [
    Strip plot of held-out test fitness per run seed for each search
    arm, one panel per condition.
  ]
)

#emph[FIG-1.] Held-out test fitness of the returned policy, one point
per run seed, per arm and condition. Red bar: mean over seeds. Unit:
food items per episode.

== FIG-2
<fig-2>
#figure(image("figures/FIG-2_adaptation.png"),
  caption: [
    Line chart of best-so-far training fitness against evaluations for
    each arm.
  ]
)

#emph[FIG-2.] Best-so-far training fitness (mean of K training episodes)
against the number of evaluations. Thin lines: individual run seeds;
thick lines: mean over seeds. Training fitness of the best of many noisy
evaluations is biased upwards (winner's curse); held-out fitness is in
FIG-1.

== Runtime projection for the planned matrix
<runtime-projection-for-the-planned-matrix>
Assumption: linear in evaluations per arm kind, median rate of the
measured runs with the largest budget; serial, one core. Measured at E =
8000: population 2.633 ms per evaluation, random\_search 2.458 ms per
evaluation.

#figure(
  align(center)[#table(
    columns: 4,
    align: (auto,auto,auto,auto,),
    table.header([config], [experiment], [runs], [serial hours],),
    table.hline(),
    [experiments/configs/EXP-001.json], [EXP-001], [60], [0.09],
    [experiments/configs/EXP-002.json], [EXP-002], [100], [0.15],
    [experiments/configs/EXP-003.json], [EXP-003], [120], [0.30],
  )]
  , kind: table
  )

Total: 280 runs, 0.53 serial hours (0.07 hours on 8 workers if scaling
were perfect).

== Failures
<failures>
None.

== Degenerate-case checks
<degenerate-case-checks>
- Returned policies with F\_test = 0: 0 \[\]
- Returned policies with stay fraction above 0.5 on the test set: 3
  \['PILOT.K1.RS.s1001', 'PILOT.main.NOSEL.s1001',
  'PILOT.main.SELONLY.s1000'\]
- Runs whose best training fitness reached the ceiling (24 items): 0
  \[\]
- Final populations with zero behavioural diversity: 10
  \['PILOT.main.SELONLY.s1000', 'PILOT.main.SELONLY.s1001',
  'PILOT.main.SELONLY.s1002', 'PILOT.main.SELONLY.s1003',
  'PILOT.main.SELONLY.s1004', 'PILOT.main.SELONLY.s1005',
  'PILOT.main.SELONLY.s1006', 'PILOT.main.SELONLY.s1007',
  'PILOT.main.SELONLY.s1008', 'PILOT.main.SELONLY.s1009'\]
- Replay check (consumed items equal the decrease of food on the grid):
  enforced in every simulated episode; a violation aborts the run.
