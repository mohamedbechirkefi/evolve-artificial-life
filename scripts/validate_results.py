# SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0
"""Metric validation on known identities for a result folder (M3): each metric
is recomputed from the raw episode scores and search trace stored in the run file.
Usage: .venv/bin/python scripts/validate_results.py RESULTS_DIR"""
import sys, numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from evolve.report import load_results
from evolve.metrics import adaptation_auc
docs=load_results(sys.argv[1]); bad=0
for d in docs:
    m=d['metrics']; e=d['episodes']; t=d['trace']; tf=np.array(t['train_fitness'])
    checks={
     'f_test=mean(test episodes)': np.isclose(m['f_test'],np.mean(e['test'])),
     'f_shift=mean(shift episodes)': np.isclose(m['f_shift'],np.mean(e['shift'])),
     'gap=fresh-test': np.isclose(m['generalisation_gap'],np.mean(e['train_fresh'])-m['f_test']),
     'n_eval=E=len(trace)': m['n_evaluations']==len(tf)==d['config']['arm'].get('evaluations', d['config']['arm'].get('population_size',0)*d['config']['arm'].get('generations',0)),
     'auc=mean cummax': np.isclose(m['adaptation_auc'],np.maximum.accumulate(tf).mean()) and np.isclose(adaptation_auc(tf),m['adaptation_auc']),
     'best_train=max trace, returned argmax': np.isclose(m['best_train_fitness'],tf.max()) and tf[t['returned_index']]==tf.max(),
     'episodes in [0,n_food]': all(0<=x<=d['config']['env']['n_food'] for x in e['test']) and all(0<=x<=d['config']['shift_env']['n_food'] for x in e['shift']),
     'exploit fractions sum 1': np.isclose(sum(m['exploit'][k] for k in ('forward_fraction','stay_fraction','turn_fraction')),1),
     'replay': m['exploit']['replay_check_passed'],
     'K1 fields null when resampled': (m['f_train_fixed'] is None)==(not d['config']['evaluation']['train_fixed']),
     'behav div in [0,1]': 0<=m['behavioural_diversity']<=1,
    }
    for k,v in checks.items():
        if not v: bad+=1; print('FAIL',d['run_id'],k)
print(len(docs),'runs,',len(checks),'checks each,',bad,'failures')
sys.exit(1 if bad else 0)
