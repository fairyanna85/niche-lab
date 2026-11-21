"""The generalized scripts must reproduce the reference study's numbers."""
import json, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "reference" / "partnerships-2026"
S = ROOT / "skills" / "run" / "scripts"


def run(*a):
    return subprocess.run([sys.executable, *map(str, a)], capture_output=True, text=True, check=True).stdout


def test_reference_then_now():
    out = run(REF / "then_now.py")
    line = next(l for l in out.splitlines() if l.startswith("zero "))
    f = line.split()
    assert f[3] == "24" and f[4] == "62"          # baseline 24% → 2026 NYC 62%
    assert "codes/posting mean 11.7" in out and "codes/posting mean 14.0" in out


def test_reference_mh():
    run(REF / "mh_adjusted.py")
    mh = json.loads((REF / "mh_adjusted.json").read_text())
    assert round(mh["zero"]["or_mh"], 2) == 4.29
    assert round(mh["aiu"]["or_mh"], 1) == 7.2 and round(mh["csuite"]["or_mh"], 1) == 7.5


def test_generalized_analyze_matches_reference(tmp_path):
    rnd = tmp_path / "run"; rnd.mkdir()
    (rnd / "run_config.json").write_text(json.dumps({"relaxed": False}))
    run(S / "postings.py", "import-reference", "--run", rnd, "--niche-map", json.dumps({"n01": {"city": ["NYC"]}}))
    (rnd / "niches.json").write_text(json.dumps({"niches": [{"id": "n01", "label": "NYC", "role_family": "partnerships", "seniority": "Head-VP",
        "segment": "all", "city": "New York", "module": "partnerships", "origin": "current", "triage": {"score": 9}, "screen": {"n_postings": 0, "n_employers": 0}, "verdict": "keep", "reason": ""}]}))
    run(S / "analyze.py", "--run", rnd, "--niche", "n01")
    a = json.loads((rnd / "niches" / "n01" / "analysis.json").read_text())
    assert a["n_now"] == 32 and a["n_archive"] == 17
    row = next(r for r in a["change"]["rows"] if r["code"] == "zero")
    assert abs(row["then"] - 4 / 17) < 0.001 and row["now"] == 0.625   # 24% → 62.5%
    assert row["or_mh"] == 4.29
    assert a["reliability"]["pooled_kappa"] == 0.79
