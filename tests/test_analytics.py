"""Cycle 5: per-posting fit, fix ladder, baseline scan, liveness summary."""
import copy, json, shutil, subprocess, sys
from pathlib import Path
import pytest
ROOT = Path(__file__).resolve().parents[1]
S = ROOT / "skills" / "run" / "scripts"
EX = ROOT / "examples" / "fictional-candidate" / "run"
import fit


@pytest.fixture()
def run(tmp_path):
    d = tmp_path / "run"; shutil.copytree(EX, d, ignore=shutil.ignore_patterns("out")); return d


def sh(*a): return subprocess.run([sys.executable, *map(str, a)], capture_output=True, text=True, check=True)


def test_fit_per_posting(run):
    sh(S / "fit.py", "per-posting", "--run", run, "--niche", "n03")
    o = json.loads((run / "niches" / "n03" / "fit_per_posting.json").read_text())
    an = json.loads((run / "niches" / "n03" / "analysis.json").read_text())
    assert o["n"] == an["n_now"] == len(o["postings"])
    assert all(0 <= p["fit"] <= 1 for p in o["postings"])
    assert o["above_line"] == sum(p["fit"] >= o["line"] for p in o["postings"]) and o["line"] == 0.6


def test_fix_ladder_monotone_and_exact(run):
    sh(S / "fit.py", "ladder", "--run", run, "--niche", "n02")
    lad = json.loads((run / "niches" / "n02" / "fix_ladder.json").read_text())
    base = fit.score(run, "n02", write=False)
    assert lad["steps"] and all(s["coverage_gain"] >= 0 and s["fit_gain"] >= 0 for s in lad["steps"])
    s0 = lad["steps"][0]
    ev = json.loads((run / "evidence.json").read_text()); ev[s0["code"]]["grade"] = 3
    (run / "evidence.json").write_text(json.dumps(ev))
    after = fit.score(run, "n02", write=False)
    assert round(after["coverage"] - base["coverage"], 3) == s0["coverage_gain"]
    assert round(after["fit"] - base["fit"], 3) == s0["fit_gain"]
    assert lad["steps"] == sorted(lad["steps"], key=lambda s: (-s["coverage_gain"], -s["fit_gain"]))


def test_baseline_scan(run):
    sh(S / "baseline.py", "--run", run)
    b = json.loads((run / "baseline.json").read_text())
    g = {x["name"]: x for x in b["gates"]}
    assert g["authenticity"]["status"] == "fail" and "results-driven" in g["authenticity"]["detail"]
    assert {"traceability", "keyword_coverage", "six_second_zone", "bullet_score"} <= set(g)


def test_liveness_summary(run):
    sh(S / "analyze.py", "--run", run, "--niche", "n03")
    ls = json.loads((run / "niches" / "n03" / "analysis.json").read_text())["liveness_summary"]
    assert set(ls["age_buckets"]) == {"0-30", "31-60", "61-90", "90+", "unknown"}
    assert 0 <= ls["doubtful_share"] <= 1 and ls["benchmark"]["low"] == 0.18 and ls["benchmark"]["high"] == 0.22
