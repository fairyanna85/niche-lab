"""Seniority-adjusted then-vs-now tests (rebuilt from the original thread).
Mantel-Haenszel odds ratio, 2026 NYC vs 2020-25 baseline, stratified by level band
(senior = Head/VP/SVP, director = Mgr/Dir/SrDir), +0.5 continuity correction on every cell."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from statsmodels.stats.contingency_tables import StratifiedTable
from data import R, CODES
from hist import H
SEN = {"Head", "VP", "SVP"}
def band(r): return "senior" if r["lvl"] in SEN else "director"
NOW = [r for r in R if r["city"] == "NYC"]; BASE = H
def table(code, b):
    now = [r for r in NOW if band(r) == b]; base = [r for r in BASE if band(r) == b]
    a = sum(1 for r in now if r["c"][code] >= 1); c = sum(1 for r in base if r["c"][code] >= 1)
    return np.array([[a, len(now) - a], [c, len(base) - c]], dtype=float) + 0.5
out = {}
for k in CODES:
    st = StratifiedTable([table(k, "senior"), table(k, "director")])
    out[k] = dict(or_mh=float(st.oddsratio_pooled), p=float(st.test_null_odds(correction=True).pvalue))
if __name__ == "__main__":
    for k, v in sorted(out.items(), key=lambda kv: kv[1]["p"]):
        print(f"{k:6s} OR_MH {v['or_mh']:6.2f}  p {v['p']:.3f}")
    json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "mh_adjusted.json"), "w"), indent=1)
